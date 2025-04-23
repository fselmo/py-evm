from typing import (
    Type,
)

from eth.constants import (
    SYSTEM_ADDRESS,
    SYSTEM_MESSAGE_GAS,
)
from eth.rlp.blocks import (
    BaseBlock,
)
from eth.vm.forks.prague import (
    PragueVM,
)
from eth.vm.state import (
    BaseState,
)

from .blocks import (
    OsakaBlock,
)
from .headers import (
    create_osaka_header_from_parent,
)
from .state import (
    OsakaState,
)


class OsakaVM(PragueVM):
    # fork name
    fork = "osaka"

    # classes
    block_class: Type[BaseBlock] = OsakaBlock
    _state_class: Type[BaseState] = OsakaState

    # methods
    create_header_from_parent = staticmethod(  # type: ignore
        create_osaka_header_from_parent()
    )
