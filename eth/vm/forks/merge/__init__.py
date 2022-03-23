from typing import (
    Any, Type,
)

import rlp

from eth.abc import BlockAPI, BlockHeaderAPI
from eth.rlp.blocks import BaseBlock
from eth.rlp.headers import BlockHeader
from eth.vm.state import BaseState
from eth_utils import ValidationError, keccak

from .blocks import MergeBlock
from .headers import (
    configure_merge_header,
    create_merge_header_from_parent,
)
from .constants import (
    POST_MERGE_DIFFICULTY,
    POST_MERGE_NONCE,
    POST_MERGE_OMMERS_HASH,
)
from .state import MergeState
from .. import GrayGlacierVM


class MergeVM(GrayGlacierVM):
    # fork name
    fork = 'merge'

    # classes
    block_class: Type[BaseBlock] = MergeBlock
    _state_class: Type[BaseState] = MergeState

    # Methods
    create_header_from_parent = staticmethod(create_merge_header_from_parent)
    compute_difficulty = POST_MERGE_DIFFICULTY
    configure_header = configure_merge_header

    def _assign_block_rewards(self, block: BlockAPI) -> None:
        # No block reward or uncles / uncle rewards post-merge
        pass

    @classmethod
    def validate_header(
        cls,
        header: BlockHeaderAPI,
        parent_header: BlockHeaderAPI
    ) -> None:
        super().validate_header(header, parent_header)

        difficulty, nonce, uncles_hash = (
            header.difficulty, header.nonce, header.uncles_hash
        )

        if difficulty != POST_MERGE_DIFFICULTY:
            raise ValidationError(
                f"Post-merge difficulty must be {POST_MERGE_DIFFICULTY}, "
                f"got {difficulty}"
            )
        if nonce != POST_MERGE_NONCE:
            raise ValidationError(
                f"Post-merge nonce must be {POST_MERGE_NONCE}, got {nonce}"
            )
        if uncles_hash != POST_MERGE_OMMERS_HASH:
            raise ValidationError(
                f"Post-merge uncles hash must be {POST_MERGE_OMMERS_HASH}, "
                f"got {uncles_hash}"
            )

