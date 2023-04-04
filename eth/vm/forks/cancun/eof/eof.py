from typing import List, Union

from pydantic import (
    BaseModel,
    root_validator,
    validator,
)

from hexbytes import HexBytes
from .constants import (
    MAGIC_EOF_PREFIX,
    EOF_VERSION,
    KIND_TYPES_VALUE,
    VALID_TYPES_SIZE,
    KIND_CODE,
    VALID_NUM_CODE_SECTIONS,
    VALID_CODE_SIZE,
    KIND_DATA,
    VALID_DATA_SIZE,
    TERMINATOR,
    VALID_INPUTS,
    VALID_OUTPUTS,
    VALID_MAX_STACK_HEIGHT,
)

# EIP-3670: EOF - Code Validation
VALID_OPCODES = [
    *range(0x00, 0x0B + 1),
    *range(0x10, 0x1D + 1),
    0x20,
    *range(0x30, 0x3F + 1),
    *range(0x40, 0x48 + 1),
    *range(0x50, 0x5E + 1),
    *range(0x60, 0x6F + 1),
    *range(0x70, 0x7F + 1),
    *range(0x80, 0x8F + 1),
    *range(0x90, 0x9F + 1),
    *range(0xA0, 0xA4 + 1),
    # Note: 0xfe is considered assigned.
    *range(0xF0, 0xF5 + 1),
    0xFA,
    0xFD,
    0xFE,
    0xFF,
]


# EIP-4750: EOF - Functions
VALID_OPCODES.pop(VALID_OPCODES.index(0x56))  # POP
VALID_OPCODES.pop(VALID_OPCODES.index(0x57))  # MLOAD
VALID_OPCODES.append(0xB0)  # CALLF
VALID_OPCODES.append(0xB1)  # RETF


class EOFHeaderV1(BaseModel):
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

    @validator("magic")
    def validate_magic(cls, magic):
        assert len(magic) == 2, f"magic must be 2 bytes in length, got {len(magic)}"
        if magic != MAGIC_EOF_PREFIX:
            raise ValueError("invalid magic value")
        return magic

    @validator("version")
    def validate_version(cls, version):
        assert (
            len(version) == 1
        ), f"version must be 1 byte in length, got {len(version)}"
        if version != EOF_VERSION:
            raise ValueError("invalid version value")
        return version

    @validator("kind_types")
    def validate_kind_types(cls, kind_types):
        assert (
            len(kind_types) == 1
        ), f"kind_types must be 1 byte in length, got {len(kind_types)}"
        if kind_types != KIND_TYPES_VALUE:
            raise ValueError("invalid kind_types value")
        return kind_types

    @validator("types_size")
    def validate_types_size(cls, types_size: bytes):
        assert (
            len(types_size) == 2
        ), f"types_size must be 2 bytes in length, got {len(types_size)}"

        int_value = int.from_bytes(types_size, "big")
        if int_value not in VALID_TYPES_SIZE or int_value % 4 != 0:
            raise ValueError("invalid types_size value")
        return types_size

    @validator("kind_code")
    def validate_kind_code(cls, kind_code):
        assert (
            len(kind_code) == 1
        ), f"kind_code must be 1 byte in length, got {len(kind_code)}"
        if kind_code != KIND_CODE:
            raise ValueError("invalid kind_code value")
        return kind_code

    @validator("num_code_sections")
    def validate_num_code_sections(cls, num_code_sections):
        assert (
            len(num_code_sections) == 2
        ), f"num_code_sections must be 2 bytes in length, got {len(num_code_sections)}"

        int_value = int.from_bytes(num_code_sections, "big")
        if int_value not in VALID_NUM_CODE_SECTIONS:
            raise ValueError("invalid num_code_sections value")
        return num_code_sections

    @validator("code_size", each_item=True)
    def validate_code_size(cls, code_size):
        assert (
            len(code_size) == 2
        ), f"code_size must be 2 bytes in length, got {len(code_size)}"

        int_value = int.from_bytes(code_size, "big")
        if int_value not in VALID_CODE_SIZE:
            raise ValueError("invalid code_size value")
        return code_size

    @validator("kind_data")
    def validate_kind_data(cls, kind_data):
        assert (
            len(kind_data) == 1
        ), f"kind_data must be 1 byte in length, got {len(kind_data)}"
        if kind_data != KIND_DATA:
            raise ValueError("invalid kind_data value")
        return kind_data

    @validator("data_size")
    def validate_data_size(cls, data_size):
        assert (
            len(data_size) == 2
        ), f"data_size must be 2 bytes in length, got {len(data_size)}"

        int_value = int.from_bytes(data_size, "big")
        if int_value not in VALID_DATA_SIZE:
            raise ValueError("invalid data_size value")
        return data_size

    @validator("terminator")
    def validate_terminator(cls, terminator):
        assert (
            len(terminator) == 1
        ), f"terminator must be 1 byte in length, got {len(terminator)}"
        if terminator != TERMINATOR:
            raise ValueError("invalid terminator value")
        return terminator

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


class EOFTypesSectionV1(BaseModel):
    inputs: bytes
    outputs: bytes
    max_stack_height: bytes

    @validator("inputs")
    def validate_inputs(cls, inputs):
        assert len(inputs) == 1, "inputs must be 1 byte in length"

        int_value = int.from_bytes(inputs, "big")
        if int_value not in VALID_INPUTS:
            raise ValueError("invalid inputs value")

        return inputs

    @validator("outputs")
    def validate_outputs(cls, outputs):
        assert len(outputs) == 1, "outputs must be 1 byte in length"

        int_value = int.from_bytes(outputs, "big")
        if int_value not in VALID_OUTPUTS:
            raise ValueError("invalid outputs value")

        return outputs

    @validator("max_stack_height")
    def validate_max_stack_height(cls, max_stack_height):
        assert len(max_stack_height) == 2, "max_stack_height must be 2 bytes in length"

        int_value = int.from_bytes(max_stack_height, "big")
        if int_value not in VALID_MAX_STACK_HEIGHT:
            raise ValueError("invalid max_stack_height value")

        return max_stack_height

    @property
    def size(self) -> int:
        return len(self.inputs) + len(self.outputs) + len(self.max_stack_height)


class EOFBodyV1(BaseModel):
    types_section: List[EOFTypesSectionV1]
    code_section: List[bytes]
    data_section: bytes

    @validator("code_section")
    def validate_code_section(cls, code_section):
        assert len(code_section) <= 1024, "number of code sections must not exceed 1024"
        return code_section

    @validator("code_section", each_item=True)
    def validate_code_section(cls, code):
        for opcode in code:
            if opcode not in VALID_OPCODES:
                raise ValueError(f"invalid opcode {opcode}")
        return code

    @property
    def size(self) -> int:
        return (
            sum(ts.size for ts in self.types_section)
            + sum(len(cs) for cs in self.code_section)
            + len(self.data_section)
        )


class EOFContainerV1(BaseModel):
    header: EOFHeaderV1
    body: EOFBodyV1

    @validator("header")
    def validate_header(cls, header):
        assert header.size >= 15, "header size must be at least 15 bytes"
        return header

    @root_validator
    def validate_container(cls, values):
        header = values.get("header")
        body = values.get("body")

        # validate container size
        expected_container_size = (
            13
            + 2 * int.from_bytes(header.num_code_sections, "big")
            + int.from_bytes(header.types_size, "big")
            + sum(
                int.from_bytes(header.code_size[i], "big")
                for i in range(0, int.from_bytes(header.num_code_sections, "big"))
            )
            + int.from_bytes(header.data_size, "big")
        )
        if header.size + body.size != expected_container_size:
            raise ValueError("invalid container size")

        # validate code sections
        assert len(body.code_section) == int.from_bytes(header.types_size, "big") / 4

        return values

    @staticmethod
    def from_bytecode(bytecode: Union[bytes, HexBytes]) -> "EOFContainerV1":
        if isinstance(bytecode, HexBytes):
            bytecode = bytes(bytecode)

        num_code_sections = bytecode[7:9]  # reused, so define early
        num_code_sections_int = int.from_bytes(num_code_sections, "big")

        header = EOFHeaderV1(
            magic=bytecode[0:2],
            version=bytecode[2:3],
            kind_types=bytecode[3:4],
            types_size=bytecode[4:6],
            kind_code=bytecode[6:7],
            num_code_sections=num_code_sections,
            code_size=[
                bytecode[9 + 2 * i : 11 + 2 * i]
                for i in range(0, num_code_sections_int)
            ],
            kind_data=bytecode[
                9 + 2 * num_code_sections_int : 10 + 2 * num_code_sections_int
            ],
            data_size=bytecode[
                10 + 2 * num_code_sections_int : 12 + 2 * num_code_sections_int
            ],
            terminator=bytecode[
                12 + 2 * num_code_sections_int : 13 + 2 * num_code_sections_int
            ],
        )

        # starting index for types section
        tsi = 13 + 2 * num_code_sections_int
        types_section = [
            EOFTypesSectionV1(
                inputs=bytecode[tsi + 4 * i : tsi + 4 * i + 1],
                outputs=bytecode[tsi + 4 * i + 1 : tsi + 4 * i + 2],
                max_stack_height=bytecode[tsi + 4 * i + 2 : tsi + 4 * i + 4],
            )
            for i in range(num_code_sections_int)
        ]

        # starting index for code section
        # note, this value changes for each section
        csi = tsi + (4 * num_code_sections_int)
        code_section = []
        for i in range(num_code_sections_int):
            code_section.append(
                bytecode[csi : csi + int.from_bytes(header.code_size[i], "big")]
            )
            csi = csi + int.from_bytes(header.code_size[i], "big")

        data_section = bytecode[csi:]

        body = EOFBodyV1(
            types_section=types_section,
            code_section=code_section,
            data_section=data_section,
        )

        return EOFContainerV1(header=header, body=body)

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
