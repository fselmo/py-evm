from abc import abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Sequence,
    Union,
)

from pydantic import (
    BaseModel,
    field_validator,
    root_validator,
)

from hexbytes import HexBytes
from .constants import (
    MAGIC_EOF_PREFIX,
    TERMINATOR,
    VALID_CODE_SIZE,
    VALID_DATA_SIZE,
    VALID_INPUTS,
    VALID_MAX_STACK_HEIGHT,
    VALID_NUM_CODE_SECTIONS,
    VALID_OUTPUTS,
    VALID_TYPES_SIZE,
)

"""
Note: The methods for the base classes were implemented during EOF v1 with some
assumptions about what may change across EOF versions. Fields such as `version`, and
`kind_*` fields make sense to be validated in at the version implementation level and 
not at the base class level. If any later versions of EOF need to override the below 
methods, they may need to be re-defined across the respective version classes with the 
appropriate validation logic for each version.
"""


class EOFHeader(BaseModel):
    """
    Base class for an EOF container `header`.
    """

    magic: bytes
    version: bytes
    kind_types: bytes
    types_size: bytes
    kind_code: bytes
    num_code_sections: bytes
    code_size: List[bytes]
    kind_data: bytes
    data_size: bytes
    terminator: bytes

    # general field validation

    @field_validator("version", "kind_types", "kind_code", "kind_data", "terminator")
    def validate_single_byte_length(cls, value: bytes) -> bytes:
        assert len(value) == 1, f"field should be 1 byte in length, got {len(value)}"
        return value

    @field_validator("types_size", "num_code_sections", "data_size")
    def validate_two_byte_length(cls, value: bytes) -> bytes:
        assert len(value) == 2, f"field should be 2 bytes in length, got {len(value)}"
        return value

    # field-specific validation

    @field_validator("magic")
    def validate_magic_value(cls, magic: bytes) -> bytes:
        if magic != MAGIC_EOF_PREFIX:
            raise ValueError("invalid `magic` value")
        return magic

    @field_validator("types_size")
    def validate_types_size_value(cls, types_size: bytes) -> bytes:
        int_value = int.from_bytes(types_size, "big")
        if int_value not in VALID_TYPES_SIZE or int_value % 4 != 0:
            raise ValueError("invalid `types_size` value")
        return types_size

    @field_validator("num_code_sections")
    def validate_num_code_sections(cls, num_code_sections: bytes) -> bytes:
        int_value = int.from_bytes(num_code_sections, "big")
        if int_value not in VALID_NUM_CODE_SECTIONS:
            raise ValueError("invalid `num_code_sections` value")
        return num_code_sections

    @field_validator("code_size")
    def validate_code_size_values(cls, code_size: List[bytes]) -> List[bytes]:
        for size in code_size:
            int_value = int.from_bytes(size, "big")
            if int_value not in VALID_CODE_SIZE:
                raise ValueError("invalid `code_size` value")
        return code_size

    @field_validator("data_size")
    def validate_data_size(cls, data_size: bytes) -> bytes:
        int_value = int.from_bytes(data_size, "big")
        if int_value not in VALID_DATA_SIZE:
            raise ValueError("invalid data_size value")
        return data_size

    @field_validator("terminator")
    def validate_terminator(cls, terminator: bytes) -> bytes:
        if terminator != TERMINATOR:
            raise ValueError("invalid terminator value")
        return terminator

    # property methods

    @property
    def size(self) -> int:
        return (
            len(self.magic)
            + len(self.version)
            + len(self.kind_types)
            + len(self.types_size)
            + len(self.kind_code)
            + len(self.num_code_sections)
            + sum(len(i) for i in self.code_size)
            + len(self.kind_data)
            + len(self.data_size)
            + len(self.terminator)
        )


class EOFTypesSection(BaseModel):
    """
    Base class for an EOF container body's `types` section.
    """

    inputs: bytes
    outputs: bytes
    max_stack_height: bytes

    @field_validator("inputs")
    def validate_inputs(cls, inputs: bytes) -> bytes:
        assert len(inputs) == 1, "inputs must be 1 byte in length"

        int_value = int.from_bytes(inputs, "big")
        if int_value not in VALID_INPUTS:
            raise ValueError("invalid inputs value")

        return inputs

    @field_validator("outputs")
    def validate_outputs(cls, outputs: bytes) -> bytes:
        assert len(outputs) == 1, "outputs must be 1 byte in length"

        int_value = int.from_bytes(outputs, "big")
        if int_value not in VALID_OUTPUTS:
            raise ValueError("invalid outputs value")

        return outputs

    @field_validator("max_stack_height")
    def validate_max_stack_height(cls, max_stack_height: bytes) -> bytes:
        assert len(max_stack_height) == 2, "max_stack_height must be 2 bytes in length"

        int_value = int.from_bytes(max_stack_height, "big")
        if int_value not in VALID_MAX_STACK_HEIGHT:
            raise ValueError("invalid max_stack_height value")

        return max_stack_height

    @property
    def size(self) -> int:
        return len(self.inputs) + len(self.outputs) + len(self.max_stack_height)


class EOFBody(BaseModel):
    """
    Base class for an EOF container `body`.
    """

    types_section: Sequence[EOFTypesSection]
    code_section: List[bytes]
    data_section: bytes

    @field_validator("code_section")
    def validate_code_section(cls, code_section: List[bytes]) -> List[bytes]:
        assert len(code_section) <= 1024, "number of code sections must not exceed 1024"
        return code_section

    @property
    def size(self) -> int:
        return (
            sum(ts.size for ts in self.types_section)
            + sum(len(cs) for cs in self.code_section)
            + len(self.data_section)
        )


class EOFContainer(BaseModel):
    """
    Base class for an EOF `container`.
    """

    header: EOFHeader
    body: EOFBody

    @field_validator("header")
    def validate_header(cls, header: EOFHeader) -> EOFHeader:
        assert header.size >= 15, "header size must be at least 15 bytes"
        return header

    @root_validator(skip_on_failure=True)
    def validate_container(
        cls,
        values: Dict[str, Any],
    ) -> Dict[str, Any]:
        header = values.get("header")
        body = values.get("body")

        num_code_sections = int.from_bytes(header.num_code_sections, "big")
        types_size = int.from_bytes(header.types_size, "big")
        data_size = int.from_bytes(header.data_size, "big")
        sum_of_code_sizes = sum(
            int.from_bytes(header.code_size[i], "big")
            for i in range(0, num_code_sections)
        )
        # validate container size
        expected_container_size = (
            13 + 2 * num_code_sections + types_size + sum_of_code_sizes + data_size
        )
        if header.size + body.size != expected_container_size:
            raise ValueError("invalid container size")

        # validate code sections
        assert len(body.code_section) == types_size / 4

        return values

    def as_bytecode(self) -> bytes:
        return (
            self.header.magic
            + self.header.version
            + self.header.kind_types
            + self.header.types_size
            + self.header.kind_code
            + self.header.num_code_sections
            + b"".join(self.header.code_size)
            + self.header.kind_data
            + self.header.data_size
            + self.header.terminator
            + b"".join(
                b"".join([ts.inputs, ts.outputs, ts.max_stack_height])
                for ts in self.body.types_section
            )
            + b"".join(self.body.code_section)
            + self.body.data_section
        )

    @staticmethod
    @abstractmethod
    def from_bytecode(bytecode: Union[bytes, HexBytes]) -> "EOFContainer":
        ...

    @property
    def size(self) -> int:
        return len(self.as_bytecode())
