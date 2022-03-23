from abc import ABC

from eth_keys.datatypes import PrivateKey

from eth._utils.transactions import (
    create_transaction_signature,
)
from eth.vm.forks.gray_glacier.transactions import (
    GrayGlacierLegacyTransaction,
    GrayGlacierTransactionBuilder,
    GrayGlacierUnsignedLegacyTransaction,
)


class MergeLegacyTransaction(GrayGlacierLegacyTransaction, ABC):
    pass


class MergeUnsignedLegacyTransaction(GrayGlacierUnsignedLegacyTransaction):
    def as_signed_transaction(
        self,
        private_key: PrivateKey,
        chain_id: int = None
    ) -> MergeLegacyTransaction:
        v, r, s = create_transaction_signature(self, private_key, chain_id=chain_id)
        return MergeLegacyTransaction(
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


class MergeTransactionBuilder(GrayGlacierTransactionBuilder):
    legacy_signed = MergeLegacyTransaction
    legacy_unsigned = MergeUnsignedLegacyTransaction
