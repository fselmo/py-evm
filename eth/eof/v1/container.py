from typing import (
    Any, Dict, List,
    Sequence,
    Union,
)

from pydantic import (
    field_validator, root_validator,
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

                if opcode in [0x5c, 0x5d]:
                    if pos + 2 > len(code):
                        raise ValidationError("truncated relative jump offset")
                    offset = int.from_bytes(
                        code[pos: pos + 2], byteorder="big", signed=True
                    )

                    rjumpdest = pc_post_instruction + offset
                    if rjumpdest < 0 or rjumpdest >= len(code):
                        raise ValidationError("relative jump destination out of bounds")

                    rjumpdests.add(rjumpdest)
                elif opcode == 0x5e:
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

    @classmethod
    @root_validator(skip_on_failure=True)
    def validate_function(
        cls,
        values: Dict[str, Any],
    ) -> None:
        body = values.get("body")
        #
        # validate_code_section(func_id, code, types)
        #
        # stack_heights = {}
        # start_stack_height = types[func_id].inputs
        # max_stack_height = start_stack_height
        #
        # # queue of instructions to analyze, list of (pos, stack_height) pairs
        # worklist = [(0, start_stack_height)]
        #
        # while worklist:
        #     pos, stack_height = worklist.pop(0)
        #     while True:
        #         # Assuming code ends with a terminating instruction due to previous validation in validate_code_section()
        #         assert pos < len(code), "code is invalid"
        #         op = code[pos]
        #         info = TABLE[op]
        #
        #         # Check if stack height (type arity) at given position is the same
        #         # for all control flow paths reaching this position.
        #         if pos in stack_heights:
        #             if stack_height != stack_heights[pos]:
        #                 raise ValidationException(
        #                     "stack height mismatch for different paths"
        #                 )
        #             else:
        #                 break
        #         else:
        #             stack_heights[pos] = stack_height
        #
        #         stack_height_required = info.stack_height_required
        #         stack_height_change = info.stack_height_change
        #
        #         if op == OP_CALLF:
        #             called_func_id = int.from_bytes(
        #                 code[pos + 1:pos + 3], byteorder="big", signed=False
        #             )
        #             # Assuming called_func_id is valid due to previous validation in validate_code_section()
        #             stack_height_required += types[called_func_id].inputs
        #             stack_height_change += types[called_func_id].outputs - types[
        #                 called_func_id].inputs
        #
        #         # Detect stack underflow
        #         if stack_height < stack_height_required:
        #             raise ValidationException("stack underflow")
        #
        #         stack_height += stack_height_change
        #         max_stack_height = max(max_stack_height, stack_height)
        #
        #         # Handle jumps
        #         if op == OP_RJUMP:
        #             offset = int.from_bytes(
        #                 code[pos + 1:pos + 3], byteorder="big", signed=True
        #             )
        #             pos += info.immediate_size + 1 + offset  # pos is valid for validated code.
        #
        #         elif op == OP_RJUMPI:
        #             offset = int.from_bytes(
        #                 code[pos + 1:pos + 3], byteorder="big", signed=True
        #             )
        #             # Save True branch for later and continue to False branch.
        #             worklist.append((pos + 3 + offset, stack_height))
        #             pos += info.immediate_size + 1
        #
        #         elif info.is_terminating:
        #             expected_height = types[func_id].outputs if op == OP_RETF else 0
        #             if stack_height != expected_height:
        #                 raise ValidationException(
        #                     "non-empty stack on terminating instruction"
        #                 )
        #             break
        #
        #         else:
        #             pos += info.immediate_size + 1
        #
        # if max_stack_height >= 1023:
        #     raise ValidationException("max stack above limit")
        #
        # return max_stack_height


class EOFContainerV1(EOFContainer):
    header: EOFHeaderV1
    body: EOFBodyV1

    _valid_opcodes: List[int] = VALID_OPCODES
    _terminating_opcodes: List[int] = TERMINATING_OPCODES
    _immediate_sizes: List[int] = IMMEDIATE_SIZES

    @staticmethod
    def from_bytecode(bytecode: Union[bytes, HexBytes]) -> "EOFContainerV1":
        return EOFContainerV1(**eof_obj_from_bytecode(bytecode))
