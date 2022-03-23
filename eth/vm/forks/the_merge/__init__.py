from typing import (
    Type,
)

from eth.rlp.blocks import BaseBlock
from eth.vm.state import BaseState

from .blocks import TheMergeBlock
from .headers import (
    configure_the_merge_header,
    create_the_merge_header_from_parent,
)
from .constants import POST_MERGE_DIFFICULTY
from .state import TheMergeState
from .. import ArrowGlacierVM


class TheMergeVM(ArrowGlacierVM):
    # fork name
    fork = 'the-merge'

    # classes
    block_class: Type[BaseBlock] = TheMergeBlock
    _state_class: Type[BaseState] = TheMergeState

    # Methods
    create_header_from_parent = staticmethod(create_the_merge_header_from_parent)
    compute_difficulty = POST_MERGE_DIFFICULTY
    configure_header = configure_the_merge_header
