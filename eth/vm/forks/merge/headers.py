from typing import Any, Callable, Optional

from toolz import curry

from eth.abc import BlockHeaderAPI
from eth.vm.forks.gray_glacier.headers import (
    compute_gray_glacier_difficulty,
    create_header_from_parent as gray_glacier_create_header_from_parent,
)
from eth.vm.forks.istanbul.headers import (
    configure_header,
)
from eth_utils import ValidationError
from ..merge.constants import (
    POST_MERGE_DIFFICULTY,
    POST_MERGE_MIX_HASH,
    POST_MERGE_NONCE,
)
from ..merge.blocks import MergeBlockHeader


def _validate_and_return_post_merge_header_param(header_param, actual, constant_value):
    if actual and actual != constant_value:
        raise ValidationError(
            f"post-merge header param '{header_param}' must always be "
            f"{constant_value}, got: {actual}"
        )
    return constant_value


@curry
def create_header_from_parent(
    _difficulty_fn: Callable[[BlockHeaderAPI, int], int],
    parent_header: Optional[BlockHeaderAPI],
    **header_params: Any,
) -> BlockHeaderAPI:
    if parent_header is None:
        if "mix_hash" not in header_params:
            header_params["mix_hash"] = POST_MERGE_MIX_HASH
        if "nonce" not in header_params:
            header_params["nonce"] = POST_MERGE_NONCE
        if "difficulty" not in header_params:
            header_params["difficulty"] = POST_MERGE_DIFFICULTY

    header_params["mix_hash"] = (
        header_params["mix_hash"] if "mix_hash" in header_params
        else parent_header.mix_hash
    )

    if parent_header is not None:
        if "difficulty" in header_params:
            header_params["difficulty"] = _validate_and_return_post_merge_header_param(
                "difficulty", header_params["difficulty"], POST_MERGE_DIFFICULTY
            )
        else:
            header_params["difficulty"] = POST_MERGE_DIFFICULTY

        if "nonce" in header_params:
            header_params["nonce"] = _validate_and_return_post_merge_header_param(
                "nonce", header_params["nonce"], POST_MERGE_NONCE
            )
        else:
            header_params["nonce"] = POST_MERGE_NONCE

    gray_glacier_validated_header = gray_glacier_create_header_from_parent(
        compute_gray_glacier_difficulty, parent_header, **header_params
    )

    # extract params validated up to gray glacier and plug into a `MergeBlockHeader`
    all_fields = gray_glacier_validated_header.as_dict()
    return MergeBlockHeader(**all_fields)  # type:ignore


create_merge_header_from_parent = create_header_from_parent(POST_MERGE_DIFFICULTY)
configure_merge_header = configure_header(POST_MERGE_DIFFICULTY)
