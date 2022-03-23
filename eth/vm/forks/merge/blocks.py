from abc import ABC
from typing import Type

from eth.abc import TransactionBuilderAPI

from eth_utils import (
    encode_hex,
)

from rlp.sedes import (
    CountableList,
)

from .transactions import (
    MergeTransactionBuilder,
)
from ..arrow_glacier.blocks import ArrowGlacierBlockHeader
from ..gray_glacier import (
    GrayGlacierBlock,
)
from ..gray_glacier.blocks import (
    GrayGlacierMiningHeader,
)
from ..london.blocks import (
    LondonBackwardsHeader,
)


class MergeMiningHeader(GrayGlacierMiningHeader, ABC):
    pass


class MergeBlockHeader(ArrowGlacierBlockHeader, ABC):
    def __str__(self) -> str:
        return f'<MergeBlockHeader #{self.block_number} {encode_hex(self.hash)[2:10]}>'


class MergeBlock(GrayGlacierBlock):
    transaction_builder: Type[TransactionBuilderAPI] = MergeTransactionBuilder
    fields = [
        ('header', MergeBlockHeader),
        ('transactions', CountableList(transaction_builder)),
        ('uncles', CountableList(LondonBackwardsHeader)),
    ]
