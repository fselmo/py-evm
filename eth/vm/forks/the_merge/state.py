from typing import Type

from eth.abc import TransactionExecutorAPI
from .computation import TheMergeComputation
from ..arrow_glacier import ArrowGlacierState
from ..arrow_glacier.state import ArrowGlacierTransactionExecutor


class TheMergeTransactionExecutor(ArrowGlacierTransactionExecutor):
    pass


class TheMergeState(ArrowGlacierState):
    computation_class = TheMergeComputation
    transaction_executor_class: Type[TransactionExecutorAPI] = TheMergeTransactionExecutor
