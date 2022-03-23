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
    TheMergeTransactionBuilder,
)
from ..arrow_glacier import (
    ArrowGlacierBlock,
)
from ..arrow_glacier.blocks import (
    ArrowGlacierBlockHeader,
    ArrowGlacierMiningHeader,
)
from ..london.blocks import (
    LondonBackwardsHeader,
)


class TheMergeMiningHeader(ArrowGlacierMiningHeader, ABC):
    pass


class TheMergeBlockHeader(ArrowGlacierBlockHeader, ABC):
    def __str__(self) -> str:
        return f'<TheMergeBlockHeader #{self.block_number} {encode_hex(self.hash)[2:10]}>'


class TheMergeBlock(ArrowGlacierBlock):
    transaction_builder: Type[TransactionBuilderAPI] = TheMergeTransactionBuilder
    fields = [
        ('header', TheMergeBlockHeader),
        ('transactions', CountableList(transaction_builder)),
        ('uncles', CountableList(LondonBackwardsHeader))
    ]
