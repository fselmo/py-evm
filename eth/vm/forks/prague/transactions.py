from abc import ABC

from eth_keys.datatypes import PrivateKey

from eth._utils.transactions import (
    create_transaction_signature,
)
from eth.vm.forks.shanghai.transactions import (
    ShanghaiLegacyTransaction,
    ShanghaiTransactionBuilder,
    ShanghaiUnsignedLegacyTransaction,
)


class PragueLegacyTransaction(ShanghaiLegacyTransaction, ABC):
    pass


class PragueUnsignedLegacyTransaction(ShanghaiUnsignedLegacyTransaction):
    def as_signed_transaction(
        self,
        private_key: PrivateKey,
        chain_id: int = None
    ) -> PragueLegacyTransaction:
        v, r, s = create_transaction_signature(self, private_key, chain_id=chain_id)
        return PragueLegacyTransaction(
            nonce=self.nonce,
            gas_price=self.gas_price,
            gas=self.gas,
            to=self.to,
            value=self.value,
            data=self.data,
            v=v,
            r=r,
            s=s,
        )


class PragueTransactionBuilder(ShanghaiTransactionBuilder):
    legacy_signed = PragueLegacyTransaction
    legacy_unsigned = PragueUnsignedLegacyTransaction
