import copy
from typing import Dict

from eth.vm import mnemonics, opcode_values
from eth.vm.opcode import as_opcode
from eth_utils.toolz import merge

from eth.abc import OpcodeAPI
from eth.vm.forks.shanghai.opcodes import SHANGHAI_OPCODES

# -- legacy opcodes -- #

PRAGUE_LEGACY_OPCODES: Dict[int, OpcodeAPI] = merge(
    copy.deepcopy(SHANGHAI_OPCODES),
)

# -- eof opcodes -- #

NEW_EOF_OPCODES: Dict[int, OpcodeAPI] = {
    opcode_values.CALLF: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.CALLF,
        gas_cost=5,
    ),
    opcode_values.RETF: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.RETF,
        gas_cost=0,
    ),
    opcode_values.RJUMP: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.RJUMP,
        gas_cost=0,
    ),
    opcode_values.RJUMPI: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.RJUMPI,
        gas_cost=0,
    ),
    opcode_values.RJUMPV: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.RJUMPV,
        gas_cost=0,
    ),
}

MODIFIED_LEGACY_OPCODES: Dict[int, OpcodeAPI] = merge(
    copy.deepcopy(PRAGUE_LEGACY_OPCODES),
    {
        # EIP-4750: JUMPDEST instruction renamed to NOP ("no operation")
        opcode_values.NOP: as_opcode(
            logic_fn=lambda _: _,
            mnemonic=mnemonics.NOP,
            gas_cost=1,  # costs 1 gas to execute
        ),
        opcode_values.INVALID: as_opcode(
            logic_fn=lambda _: _,
            mnemonic=mnemonics.INVALID,
            gas_cost=0,
        ),
    },
)

# EIP-3670: CALLCODE and SELFDESTRUCT are invalid and their opcodes are undefined
MODIFIED_LEGACY_OPCODES.pop(opcode_values.CALLCODE)
MODIFIED_LEGACY_OPCODES.pop(opcode_values.SELFDESTRUCT)

# EIP-4750: JUMP, JUMPI, and PC instructions are invalid and their opcodes are undefined
MODIFIED_LEGACY_OPCODES.pop(opcode_values.JUMP)
MODIFIED_LEGACY_OPCODES.pop(opcode_values.JUMPI)
MODIFIED_LEGACY_OPCODES.pop(opcode_values.PC)


PRAGUE_EOF_OPCODES: Dict[int, OpcodeAPI] = merge(
    MODIFIED_LEGACY_OPCODES,
    NEW_EOF_OPCODES,
)
