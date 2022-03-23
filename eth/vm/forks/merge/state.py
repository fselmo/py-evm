from typing import Type

from eth.abc import StateAPI, TransactionExecutorAPI
from eth_typing import Hash32
from .computation import MergeComputation
from ..gray_glacier import GrayGlacierState
from ..gray_glacier.state import GrayGlacierTransactionExecutor


class MergeTransactionExecutor(GrayGlacierTransactionExecutor):
    pass


class MergeState(GrayGlacierState):
    computation_class = MergeComputation
    transaction_executor_class: Type[TransactionExecutorAPI] = MergeTransactionExecutor

    @property
    def mix_hash(self: StateAPI) -> Hash32:
        return self.execution_context.mix_hash
