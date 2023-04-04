from .opcodes import CANCUN_OPCODES
from eth.vm.forks.shanghai.computation import ShanghaiComputation


class CancunComputation(ShanghaiComputation):
    """
    A class for all execution computations in the ``Cancun`` hard fork
    """
    opcodes = CANCUN_OPCODES  # TODO: if no new opcodes, remove this line and opcodes.py
