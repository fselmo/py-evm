from typing import (
    Type,
)

from eth_abi.utils.numeric import (
    ceil32,
)

from eth.abc import (
    ComputationAPI,
    MessageAPI,
    SignedTransactionAPI,
    TransactionContextAPI,
    TransactionExecutorAPI,
)
from eth.exceptions import (
    VMError,
)
from eth.vm.forks.cancun import (
    CancunState,
)
from eth.vm.forks.cancun.state import (
    CancunTransactionExecutor,
)
from eth.vm.forks.prague.constants import (
    STANDARD_TOKEN_COST,
    TOTAL_COST_FLOOR_PER_TOKEN,
)
from eth.vm.forks.shanghai.constants import (
    INITCODE_WORD_COST,
)

from ..cancun.transaction_context import (
    CancunTransactionContext,
)
from .computation import (
    PragueComputation,
)


class PragueTransactionExecutor(CancunTransactionExecutor):
    def build_evm_message(self, transaction: SignedTransactionAPI) -> MessageAPI:
        if hasattr(transaction, "authorization_list"):
            message = super().build_evm_message(transaction)
            # TODO: 7702
            # message.authorizations = transaction.authorization_list
            return message
        else:
            return super().build_evm_message(transaction)

    @staticmethod
    def validate_eip7623_calldata_cost(
        message: MessageAPI, computation: ComputationAPI
    ) -> None:
        calldata = message.data
        tokens_in_calldata = len(calldata) // 32
        words_in_calldata = ceil32(len(calldata)) // 32

        eip_7623_gas_validation = 21000 + max(
            STANDARD_TOKEN_COST * tokens_in_calldata
            + computation.get_gas_used()
            + message.is_create * (32000 + INITCODE_WORD_COST * words_in_calldata),
            TOTAL_COST_FLOOR_PER_TOKEN * tokens_in_calldata,
        )

        if message.gas < eip_7623_gas_validation:
            raise VMError(
                "Transaction gas is insufficient. Expected at least "
                f"{eip_7623_gas_validation}, got {message.gas}."
            )

    def build_computation(
        self,
        message: MessageAPI,
        transaction: SignedTransactionAPI,
    ) -> ComputationAPI:
        transaction_context = self.vm_state.get_transaction_context(transaction)
        computation = self.vm_state.get_computation(message, transaction_context)

        self.validate_eip7623_calldata_cost(message, computation)

        return super().build_computation(message, transaction)


class PragueState(CancunState):
    computation_class = PragueComputation
    transaction_context_class: Type[TransactionContextAPI] = CancunTransactionContext
    transaction_executor_class: Type[TransactionExecutorAPI] = PragueTransactionExecutor
