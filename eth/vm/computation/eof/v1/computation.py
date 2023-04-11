from eth.abc import (
    ComputationAPI, EOFComputationAPI, GasMeterAPI,
    MessageComputationAPI, StateAPI,
)

from .constants import (
    EOFv1_OPCODES,
)
from ... import BaseComputation


class EOFv1Computation(EOFComputationAPI, BaseComputation):
    version = 1
    opcodes = EOFv1_OPCODES

    def _configure_gas_meter(self) -> GasMeterAPI:
        # TODO: refactor this to MessageComputation, no need to be in the base class
        pass

    @classmethod
    def apply_computation(
        cls,
        state: StateAPI,
        parent_message_computation: MessageComputationAPI,
    ) -> ComputationAPI:
        with cls(state, parent_message_computation) as computation:
            pass

        return computation
