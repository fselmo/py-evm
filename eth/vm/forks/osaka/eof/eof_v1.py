from typing import (
    List,
    Sequence,
    Union,
)

from eth_utils import (
    ValidationError,
)
from hexbytes import (
    HexBytes,
)
from pydantic import (
    field_validator,
)

from .constants import (
    EOF_VERSION_V1,
    KIND_CODE_V1,
    KIND_DATA_V1,
    KIND_TYPES_V1,
)
from .main import (
    EOFBody,
    EOFContainer,
    EOFHeader,
    EOFTypesSection,
)
from .utils import (
    eof_obj_from_bytecode,
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


# STOP, RETURN, REVERT, INVALID, RETF
terminating_opcodes = [0x00, 0xF3, 0xFD, 0xFE, 0xB1]

immediate_sizes = 256 * [0]
immediate_sizes[0x5C] = 2  # RJUMP
immediate_sizes[0x5D] = 2  # RJUMPI
for opcode in range(0x60, 0x7F + 1):  # PUSH1..PUSH32
    immediate_sizes[opcode] = opcode - 0x60 + 1


class EOFHeaderV1(EOFHeader):
    @field_validator("version")
    @classmethod
    def validate_version(cls, version: bytes) -> bytes:
        if version != EOF_VERSION_V1:
            raise ValueError("invalid version value")
        return version

    @field_validator("kind_types")
    @classmethod
    def validate_kind_types(cls, kind_types: bytes) -> bytes:
        if kind_types != KIND_TYPES_V1:
            raise ValueError("invalid kind_types value")
        return kind_types

    @field_validator("kind_code")
    @classmethod
    def validate_kind_code(cls, kind_code: bytes) -> bytes:
        if kind_code != KIND_CODE_V1:
            raise ValueError("invalid kind_code value")
        return kind_code

    @field_validator("kind_data")
    @classmethod
    def validate_kind_data(cls, kind_data: bytes) -> bytes:
        if kind_data != KIND_DATA_V1:
            raise ValueError("invalid kind_data value")
        return kind_data


class EOFTypesSectionV1(EOFTypesSection):
    pass


class EOFBodyV1(EOFBody):
    types_section: Sequence[EOFTypesSectionV1]

    @field_validator("code_section")
    @classmethod
    def validate_code_section_items(cls, code_section: List[bytes]) -> List[bytes]:
        for code in code_section:
            opcode = 0
            pos = 0
            rjumpdests = set()
            immediates = set()  # type: ignore

            while pos < len(code):
                opcode = code[pos]
                pos += 1

                # TODO: use OSAKA_OPCODES.keys() once those are implemented
                if opcode not in VALID_OPCODES:
                    raise ValueError(f"undefined instruction: {opcode}")

                pc_post_instruction = pos + immediate_sizes[opcode]

                if opcode in [0x5C, 0x5D]:
                    if pos + 2 > len(code):
                        raise ValidationError("truncated relative jump offset")
                    offset = int.from_bytes(
                        code[pos : pos + 2], byteorder="big", signed=True
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
                            code[offset_pos : offset_pos + 2],
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

            # opcode is the *last opcode*
            if opcode not in terminating_opcodes:
                raise ValidationError("no terminating instruction")

            # Ensure relative jump destinations don't target immediates
            if not rjumpdests.isdisjoint(immediates):
                raise ValidationError("relative jump destination targets immediate")

        return code_section


class EOFContainerV1(EOFContainer):
    header: EOFHeaderV1
    body: EOFBodyV1

    @staticmethod
    def from_bytecode(bytecode: Union[bytes, HexBytes]) -> "EOFContainerV1":
        return EOFContainerV1(**eof_obj_from_bytecode(bytecode))
