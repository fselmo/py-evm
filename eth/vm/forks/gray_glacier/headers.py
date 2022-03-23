from typing import Any, Callable, Optional

from toolz import curry

from eth.abc import BlockHeaderAPI
from eth.vm.forks.gray_glacier.blocks import GrayGlacierBlockHeader
from eth.vm.forks.london.headers import (
    create_header_from_parent as london_create_header_from_parent,
)
from eth.vm.forks.petersburg.headers import (
    compute_difficulty,
)
from eth.vm.forks.istanbul.headers import (
    configure_header,
)


compute_gray_glacier_difficulty = compute_difficulty(11_400_000)


@curry
def create_header_from_parent(
    difficulty_fn: Callable[[BlockHeaderAPI, int], int],
    parent_header: Optional[BlockHeaderAPI],
    **header_params: Any
) -> BlockHeaderAPI:
    london_validated_header = london_create_header_from_parent(
        difficulty_fn, parent_header, **header_params
    )

    # extract london validated params and plug into a `GrayGlacierBlockHeader`
    all_fields = london_validated_header.as_dict()
    return GrayGlacierBlockHeader(**all_fields)  # type:ignore


create_gray_glacier_header_from_parent = create_header_from_parent(
    compute_gray_glacier_difficulty
)

configure_gray_glacier_header = configure_header(compute_gray_glacier_difficulty)
