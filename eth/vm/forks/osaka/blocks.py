from abc import (
    ABC,
)
from typing import (
    Type,
)

from rlp.sedes import (
    CountableList,
)

from eth.abc import (
    ReceiptBuilderAPI,
    TransactionBuilderAPI,
)
from eth.vm.forks.prague.blocks import (
    PragueBlock,
    PragueBlockHeader,
)

from ..shanghai.withdrawals import (
    Withdrawal,
)
from .transactions import (
    OsakaTransactionBuilder,
)


class OsakaBlockHeader(PragueBlockHeader, ABC):
    ...


class OsakaBlock(PragueBlock):
    transaction_builder: Type[TransactionBuilderAPI] = OsakaTransactionBuilder
    fields = [
        ("header", OsakaBlockHeader),
        ("transactions", CountableList(transaction_builder)),
        ("uncles", CountableList(None, max_length=0)),
        ("withdrawals", CountableList(Withdrawal)),
    ]
