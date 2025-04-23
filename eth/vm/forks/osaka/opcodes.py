import copy
from typing import (
    Dict,
)

from eth_utils.toolz import (
    merge,
)

from eth.abc import (
    OpcodeAPI,
)
from eth.vm.forks.prague.opcodes import (
    PRAGUE_OPCODES,
)

PRAGUE_OPCODES: Dict[int, OpcodeAPI] = merge(copy.deepcopy(PRAGUE_OPCODES), {})
