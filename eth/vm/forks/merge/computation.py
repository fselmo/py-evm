from .opcodes import MERGE_OPCODES
from ..gray_glacier.computation import GrayGlacierComputation


class MergeComputation(GrayGlacierComputation):
    """
    A class for all execution computations in the ``Merge`` soft fork.
    Inherits from :class:`~eth.vm.forks.gray_glacier.GrayGlacierComputation`
    """
    opcodes = MERGE_OPCODES
