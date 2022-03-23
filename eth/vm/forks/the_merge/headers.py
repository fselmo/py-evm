from typing import Any, Callable, Optional

from toolz import curry

from eth.abc import BlockHeaderAPI
from eth.vm.forks.arrow_glacier.headers import (
    create_header_from_parent as arrow_glacier_create_header_from_parent,
)
from eth.vm.forks.istanbul.headers import (
    configure_header,
)
from ..the_merge.constants import (
    POST_MERGE_DIFFICULTY,
    POST_MERGE_MIX_HASH,
    POST_MERGE_NONCE,
)


def _validate_and_return_post_merge_header_param(header_param, actual, constant_value):
    if actual and actual != constant_value:
        raise ValueError(
            f'post-merge header param "{header_param}" must always be {constant_value}, '
            f'got: {actual}'
        )
    return constant_value


@curry
def create_header_from_parent(
    difficulty_fn: Callable[[BlockHeaderAPI, int], int],
    parent_header: Optional[BlockHeaderAPI],
    **header_params: Any
) -> BlockHeaderAPI:
    # validate post-merge fields
    header_params_difficulty = header_params['difficulty']
    header_params_mix_hash = header_params['mix_hash']
    header_params_nonce = header_params['nonce']

    header_params['difficulty'] = _validate_and_return_post_merge_header_param(
        'difficulty',  header_params_difficulty, POST_MERGE_DIFFICULTY
    )
    header_params['mix_hash'] = _validate_and_return_post_merge_header_param(
        'mix_hash', header_params_mix_hash, POST_MERGE_MIX_HASH
    )
    header_params['nonce'] = _validate_and_return_post_merge_header_param(
        'nonce', header_params_nonce, POST_MERGE_NONCE
    )

    # validate arrow glacier fields, passing in merge-validated fields
    arrow_glacier_header = arrow_glacier_create_header_from_parent(
        difficulty_fn, parent_header, **header_params
    )

    all_fields = vars(arrow_glacier_header).items()

    return TheMergeBlockHeader(**all_fields)  # type:ignore


create_the_merge_header_from_parent = create_header_from_parent(POST_MERGE_DIFFICULTY)
configure_the_merge_header = configure_header(POST_MERGE_DIFFICULTY)
