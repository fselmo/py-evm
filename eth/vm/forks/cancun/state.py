from typing import Type

from eth.abc import TransactionExecutorAPI
from .computation import CancunMessageComputation
from ..shanghai import ShanghaiState
from ..shanghai.state import ShanghaiTransactionExecutor


class CancunTransactionExecutor(ShanghaiTransactionExecutor):
    pass


class CancunState(ShanghaiState):
    computation_class = CancunMessageComputation
    transaction_executor_class: Type[TransactionExecutorAPI] = CancunTransactionExecutor   # noqa: E501
