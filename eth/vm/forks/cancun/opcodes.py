import copy
from typing import Dict

from eth_utils.toolz import merge

from eth.abc import OpcodeAPI
from eth.vm.forks.shanghai.opcodes import SHANGHAI_OPCODES

CANCUN_OPCODES: Dict[int, OpcodeAPI] = merge(
    copy.deepcopy(SHANGHAI_OPCODES),
)
