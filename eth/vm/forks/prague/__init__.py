from typing import (
    Type,
)

from eth.rlp.blocks import BaseBlock
from eth.vm.forks.shanghai import ShanghaiVM
from eth.vm.state import BaseState

from .blocks import PragueBlock
from .headers import (
    configure_prague_header,
    create_prague_header_from_parent,
)
from .state import PragueState


class PragueVM(ShanghaiVM):
    # fork name
    fork = 'prague'

    # classes
    block_class: Type[BaseBlock] = PragueBlock
    _state_class: Type[BaseState] = PragueState

    # Methods
    create_header_from_parent = staticmethod(  # type: ignore
        create_prague_header_from_parent()
    )
    configure_header = configure_prague_header
