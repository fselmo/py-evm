from abc import (
    ABC,
)

from eth_keys.datatypes import (
    PrivateKey,
)

from eth._utils.transactions import (
    create_transaction_signature,
)
from eth.vm.forks.prague.transactions import (
    PragueLegacyTransaction,
    PragueTransactionBuilder,
    PragueUnsignedLegacyTransaction,
)


class OsakaLegacyTransaction(PragueLegacyTransaction, ABC):
    ...


class OsakaUnsignedLegacyTransaction(PragueUnsignedLegacyTransaction):
    def as_signed_transaction(
        self, private_key: PrivateKey, chain_id: int = None
    ) -> OsakaLegacyTransaction:
        v, r, s = create_transaction_signature(self, private_key, chain_id=chain_id)
        return OsakaLegacyTransaction(
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


class OsakaTransactionBuilder(PragueTransactionBuilder):
    legacy_signed = OsakaLegacyTransaction
    legacy_unsigned = OsakaUnsignedLegacyTransaction
