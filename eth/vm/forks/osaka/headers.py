from typing import (
    Any,
    Dict,
    Optional,
)

from eth_utils.toolz import (
    curry,
)

from eth.abc import (
    BlockHeaderAPI,
)
from eth.vm.forks.osaka.blocks import (
    OsakaBlockHeader,
)
from eth.vm.forks.prague import (
    create_prague_header_from_parent,
)


@curry
def create_osaka_header_from_parent(
    parent_header: Optional[BlockHeaderAPI],
    **header_params: Any,
) -> BlockHeaderAPI:
    prague_validated_header = create_prague_header_from_parent(
        parent_header, **header_params
    )

    all_fields: Dict[Any, Any] = prague_validated_header.as_dict()

    return OsakaBlockHeader(**all_fields)
