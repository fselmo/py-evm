from abc import ABC
from typing import (
    Type,
)

from eth.abc import (
    TransactionBuilderAPI,
)

from eth_utils import (
    encode_hex,
)

from rlp.sedes import (
    CountableList,
)

from .transactions import (
    PragueTransactionBuilder,
)
from ..shanghai.blocks import (
    ShanghaiBackwardsHeader,
    ShanghaiBlock,
    ShanghaiBlockHeader,
    ShanghaiMiningHeader,
)
from ..shanghai.withdrawals import Withdrawal


class ParisMiningHeader(ShanghaiMiningHeader, ABC):
    pass


class PragueBlockHeader(ShanghaiBlockHeader, ABC):
    def __str__(self) -> str:
        return f'<PragueBlockHeader #{self.block_number} {encode_hex(self.hash)[2:10]}>'


class PragueBlock(ShanghaiBlock):
    transaction_builder: Type[TransactionBuilderAPI] = PragueTransactionBuilder
    fields = [
        ('header', PragueBlockHeader),
        ('transactions', CountableList(transaction_builder)),
        ('uncles', CountableList(ShanghaiBackwardsHeader, max_length=0)),
        ('withdrawals', CountableList(Withdrawal)),
    ]
