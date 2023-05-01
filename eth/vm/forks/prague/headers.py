from typing import Any, Optional

from toolz import curry

from eth.abc import BlockHeaderAPI
from eth.vm.forks.shanghai.headers import (
    create_shanghai_header_from_parent,
)
from eth.vm.forks.byzantium.headers import (
    configure_header,
)
from .blocks import PragueBlockHeader


@curry
def create_prague_header_from_parent(
    parent_header: Optional[BlockHeaderAPI],
    **header_params: Any,
) -> BlockHeaderAPI:

    shanghai_validated_header = create_shanghai_header_from_parent(
        parent_header, **header_params
    )

    # extract params validated up to shanghai (previous VM)
    # and plug into a `PragueBlockHeader` class
    all_fields = shanghai_validated_header.as_dict()
    return PragueBlockHeader(**all_fields)


configure_prague_header = configure_header()
