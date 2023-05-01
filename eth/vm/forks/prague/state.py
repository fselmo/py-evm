from typing import Type

from eth.abc import TransactionExecutorAPI
from .computation import PragueComputation
from ..shanghai import ShanghaiState
from ..shanghai.state import ShanghaiTransactionExecutor


class PragueTransactionExecutor(ShanghaiTransactionExecutor):
    pass


class PragueState(ShanghaiState):
    computation_class = PragueComputation
    transaction_executor_class: Type[TransactionExecutorAPI] = PragueTransactionExecutor   # noqa: E501
