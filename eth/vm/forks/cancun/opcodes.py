import copy
from typing import Dict

from eth.vm import mnemonics, opcode_values
from eth.vm.logic import stack
from eth.vm.opcode import as_opcode
from eth_utils.toolz import merge

from eth.abc import OpcodeAPI
from eth.vm.forks.shanghai.opcodes import SHANGHAI_OPCODES

from eth import constants

NEW_OPCODES: Dict[int, OpcodeAPI] = {
    opcode_values.CALLF: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.CALLF,
        gas_cost=0,
        is_eof_opcode=True,
    ),
    opcode_values.RETF: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.RETF,
        gas_cost=0,
        is_eof_opcode=True,
    ),
    opcode_values.RJUMP: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.RJUMP,
        gas_cost=0,
        is_eof_opcode=True,
    ),
    opcode_values.RJUMPI: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.RJUMPI,
        gas_cost=0,
        is_eof_opcode=True,
    ),
    opcode_values.RJUMPV: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.RJUMPV,
        gas_cost=0,
        is_eof_opcode=True,
    ),

    # TODO: If this is even necessary, add this OPCODE to the earliest fork that
    #  makes the most sense
    opcode_values.EXPLICIT_INVALID: as_opcode(
        logic_fn=lambda _: _,
        mnemonic=mnemonics.EXPLICIT_INVALID,
        gas_cost=0,
    ),
}

CANCUN_OPCODES: Dict[int, OpcodeAPI] = merge(
    copy.deepcopy(SHANGHAI_OPCODES),
    NEW_OPCODES,
)
