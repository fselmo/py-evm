from typing import (
    Type,
)

from eth.abc import (
    TransactionExecutorAPI,
)
from eth.vm.forks.prague import (
    PragueState,
)
from eth.vm.forks.prague.state import (
    PragueTransactionExecutor,
)

from .computation import (
    OsakaComputation,
)


class OsakaTransactionExecutor(PragueTransactionExecutor):
    ...


class OsakaState(PragueState):
    computation_class = OsakaComputation
    transaction_executor_class: Type[TransactionExecutorAPI] = OsakaTransactionExecutor
