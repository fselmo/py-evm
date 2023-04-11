from eth.abc import ComputationAPI

from .eof import EOFContainerV1
from .opcodes import (
    CANCUN_OPCODES,
)
from eth.vm.forks.shanghai.computation import ShanghaiMessageComputation
from ...computation.eof.v1.computation import EOFv1Computation


class CancunMessageComputation(ShanghaiMessageComputation):
    """
    A class for all execution computations in the ``Cancun`` hard fork
    """
    opcodes = CANCUN_OPCODES

    @classmethod
    def apply_eof_computation(cls, computation: ComputationAPI) -> ComputationAPI:
        """
        Triggered by `magic`, builds an EOF container, validating each field, and
        handles EOF logic for the computation.
        """
        remaining_code = computation.code.read(len(computation.code))

        # build the EOF container and validate container fields
        eof_container = EOFContainerV1.from_bytecode(remaining_code)
        cls.eof_container = eof_container

        for code in eof_container.body.code_section:
            pass
            # - build child message
            # - cls.apply_child_computation(child_msg)
            # - cls.apply_eof_computation(child_computation)
            #   ... in `apply_computation()`, flag for EOF computation? or factor out
            #   the bulk of the logic into a separate function, and call that here as
            #   well.

        return computation


class CancunEOFComputation(EOFv1Computation):
    pass
