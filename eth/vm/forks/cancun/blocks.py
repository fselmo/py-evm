from abc import (
    ABC,
)
from typing import (
    Type,
)

from eth_utils import (
    encode_hex,
)
from rlp.sedes import (
    CountableList,
)

from eth.abc import (
    ReceiptBuilderAPI,
    TransactionBuilderAPI,
)

from ..london.receipts import (
    LondonReceiptBuilder,
)
from ..shanghai.blocks import (
    ShanghaiBackwardsHeader,
    ShanghaiBlock,
    ShanghaiBlockHeader,
    ShanghaiMiningHeader,
)
from ..shanghai.withdrawals import (
    Withdrawal,
)
from .transactions import (
    CancunTransactionBuilder,
)


class CancunMiningHeader(ShanghaiMiningHeader, ABC):
    pass


class CancunBlockHeader(ShanghaiBlockHeader, ABC):
    def __str__(self) -> str:
        return f"<CancunBlockHeader #{self.block_number} {encode_hex(self.hash)[2:10]}>"


class CancunBlock(ShanghaiBlock):
    transaction_builder: Type[TransactionBuilderAPI] = CancunTransactionBuilder
    receipt_builder: Type[ReceiptBuilderAPI] = LondonReceiptBuilder
    fields = [
        ("header", CancunBlockHeader),
        ("transactions", CountableList(transaction_builder)),
        ("uncles", CountableList(ShanghaiBackwardsHeader, max_length=0)),
        ("withdrawals", CountableList(Withdrawal)),
    ]