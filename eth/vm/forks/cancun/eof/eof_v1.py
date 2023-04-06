from typing import (
    List,
    Union,
)

from pydantic import (
    field_validator,
)

from hexbytes import HexBytes

from .main import (
    EOFBody,
    EOFContainer,
    EOFHeader,
    EOFTypesSection,
)
from .constants import (
    MAGIC_EOF_PREFIX,
    EOF_VERSION_V1,
    KIND_TYPES_V1,
    VALID_TYPES_SIZE,
    KIND_CODE_V1,
    VALID_NUM_CODE_SECTIONS,
    VALID_CODE_SIZE,
    KIND_DATA_V1,
    VALID_DATA_SIZE,
    TERMINATOR,
    VALID_INPUTS,
    VALID_OUTPUTS,
    VALID_MAX_STACK_HEIGHT,
)
from .utils import eof_obj_from_bytecode


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


class EOFHeaderV1(EOFHeader):

    @field_validator("version")
    def validate_version(cls, version):
        if version != EOF_VERSION_V1:
            raise ValueError("invalid version value")
        return version

    @field_validator("kind_types")
    def validate_kind_types(cls, kind_types):
        if kind_types != KIND_TYPES_V1:
            raise ValueError("invalid kind_types value")
        return kind_types

    @field_validator("kind_code")
    def validate_kind_code(cls, kind_code):
        if kind_code != KIND_CODE_V1:
            raise ValueError("invalid kind_code value")
        return kind_code

    @field_validator("kind_data")
    def validate_kind_data(cls, kind_data):
        assert (
            len(kind_data) == 1
        ), f"kind_data must be 1 byte in length, got {len(kind_data)}"
        if kind_data != KIND_DATA_V1:
            raise ValueError("invalid kind_data value")
        return kind_data


class EOFTypesSectionV1(EOFTypesSection):
    pass


class EOFBodyV1(EOFBody):
    types_section: List[EOFTypesSectionV1]

    @field_validator("code_section")
    def validate_code_section_items(cls, code_section: List[bytes]) -> List[bytes]:
        # TODO: use CANCUN_OPCODES once those are implemented
        for code in code_section:
            for opcode in code:
                if opcode not in VALID_OPCODES:
                    raise ValueError(f"invalid opcode")

        return code_section


class EOFContainerV1(EOFContainer):
    header: EOFHeaderV1
    body: EOFBodyV1

    @staticmethod
    def from_bytecode(bytecode: Union[bytes, HexBytes]) -> "EOFContainerV1":
        return EOFContainerV1(**eof_obj_from_bytecode(bytecode))
