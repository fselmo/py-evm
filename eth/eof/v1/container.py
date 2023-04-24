from typing import (
    List,
    Sequence,
    Union,
)

from pydantic import (
    field_validator,
)

from eth_utils import ValidationError
from hexbytes import HexBytes

from ..container import (
    EOFBody,
    EOFContainer,
    EOFHeader,
    EOFTypesSection,
)
from .constants import (
    EOF_VERSION_V1,
    KIND_TYPES_V1,
    KIND_CODE_V1,
    KIND_DATA_V1,
)
from .._utils import eof_obj_from_bytecode


# directly from EIP-4200 reference implementation
VALID_OPCODES = [
    *range(0x00, 0x0b + 1),
    *range(0x10, 0x1d + 1),
    0x20,
    *range(0x30, 0x3f + 1),
    *range(0x40, 0x48 + 1),
    *range(0x50, 0x5e + 1),
    *range(0x60, 0x6f + 1),
    *range(0x70, 0x7f + 1),
    *range(0x80, 0x8f + 1),
    *range(0x90, 0x9f + 1),
    *range(0xa0, 0xa4 + 1),
    # Note: 0xfe is considered assigned.
    *range(0xf0, 0xf5 + 1), 0xfa, 0xfd, 0xfe, 0xff
]

# revised after EIP-5450:
# STOP, RETURN, REVERT, INVALID, RETF
TERMINATING_OPCODES = [0x00, 0xf3, 0xfd, 0xfe, 0xb1]

IMMEDIATE_SIZES = 256 * [0]
IMMEDIATE_SIZES[0x5c] = 2  # RJUMP
IMMEDIATE_SIZES[0x5d] = 2  # RJUMPI
IMMEDIATE_SIZES[0xb0] = 2  # CALLF
IMMEDIATE_SIZES[0xb2] = 2  # JUMPF
for push_opcode in range(0x60, 0x7f + 1):  # PUSH1..PUSH32
    IMMEDIATE_SIZES[push_opcode] = push_opcode - 0x60 + 1

# EIP-4750: EOF - Functions
VALID_OPCODES += [0xb0, 0xb1]
VALID_OPCODES.pop(VALID_OPCODES.index(0x56))  # POP
VALID_OPCODES.pop(VALID_OPCODES.index(0x57))  # MLOAD


class EOFHeaderV1(EOFHeader):
    @field_validator("version")
    def validate_version(cls, version: bytes) -> bytes:
        if version != EOF_VERSION_V1:
            raise ValueError("invalid version value")
        return version

    @classmethod
    @field_validator("kind_types")
    def validate_kind_types(cls, kind_types: bytes) -> bytes:
        if kind_types != KIND_TYPES_V1:
            raise ValueError("invalid kind_types value")
        return kind_types

    @classmethod
    @field_validator("kind_code")
    def validate_kind_code(cls, kind_code: bytes) -> bytes:
        if kind_code != KIND_CODE_V1:
            raise ValueError("invalid kind_code value")
        return kind_code

    @classmethod
    @field_validator("kind_data")
    def validate_kind_data(cls, kind_data: bytes) -> bytes:
        if kind_data != KIND_DATA_V1:
            raise ValueError("invalid kind_data value")
        return kind_data


class EOFTypesSectionV1(EOFTypesSection):
    pass


class EOFBodyV1(EOFBody):
    types_section: Sequence[EOFTypesSectionV1]

    @field_validator("code_section")
    def validate_code_section_items(cls, code_section: List[bytes]) -> List[bytes]:
        for code in code_section:
            # EIP-4200 reference implementation

            pos: int = 0
            rjumpdests = set()
            immediates = set()  # type: ignore

            while pos < len(code):
                opcode = code[pos]
                pos += 1

                if opcode not in VALID_OPCODES:
                    raise ValueError(f"undefined instruction: {opcode}")

                pc_post_instruction = pos + IMMEDIATE_SIZES[opcode]

                if opcode in [0x5C, 0x5D]:
                    if pos + 2 > len(code):
                        raise ValidationError("truncated relative jump offset")
                    offset = int.from_bytes(
                        code[pos: pos + 2], byteorder="big", signed=True
                    )

                    rjumpdest = pc_post_instruction + offset
                    if rjumpdest < 0 or rjumpdest >= len(code):
                        raise ValidationError("relative jump destination out of bounds")

                    rjumpdests.add(rjumpdest)
                elif opcode == 0x5E:
                    if pos + 1 > len(code):
                        raise ValidationError("truncated jump table")
                    jump_table_size = code[pos]
                    if jump_table_size == 0:
                        raise ValidationError("empty jump table")

                    pc_post_instruction = pos + 1 + 2 * jump_table_size
                    if pc_post_instruction > len(code):
                        raise ValidationError("truncated jump table")

                    for offset_pos in range(pos + 1, pc_post_instruction, 2):
                        offset = int.from_bytes(
                            code[offset_pos: offset_pos + 2],
                            byteorder="big",
                            signed=True,
                        )

                        rjumpdest = pc_post_instruction + offset
                        if rjumpdest < 0 or rjumpdest >= len(code):
                            raise ValidationError(
                                "relative jump destination out of bounds"
                            )
                        rjumpdests.add(rjumpdest)

                # Save immediate value positions
                immediates.update(range(pos, pc_post_instruction))

                # Skip immediates
                pos = pc_post_instruction

            # Ensure last opcode's immediate doesn't go over code end
            if pos != len(code):
                raise ValidationError("truncated immediate")

            # NOTE: Terminating Opcode is not a requirement but is still in EIP-4200
            # as of the time of this writing. It is commented out here so as not to
            # confuse the reader if using the EIP as a reference.
            # if opcode not in TERMINATING_OPCODES:
            #     raise ValidationError("no terminating instruction")

            # Ensure relative jump destinations don't target immediates
            if not rjumpdests.isdisjoint(immediates):
                raise ValidationError("relative jump destination targets immediate")

        return code_section


class EOFContainerV1(EOFContainer):
    header: EOFHeaderV1
    body: EOFBodyV1

    valid_opcodes: List[int] = VALID_OPCODES
    terminating_opcodes: List[int] = TERMINATING_OPCODES
    immediate_sizes: List[int] = IMMEDIATE_SIZES

    @staticmethod
    def from_bytecode(bytecode: Union[bytes, HexBytes]) -> "EOFContainerV1":
        return EOFContainerV1(**eof_obj_from_bytecode(bytecode))
