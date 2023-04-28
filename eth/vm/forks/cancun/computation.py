from typing import cast

from eth.abc import (
    ComputationAPI,
    MessageAPI,
    StateAPI,
    TransactionContextAPI,
)
from eth.exceptions import Halt

from .opcodes import (
    CANCUN_LEGACY_OPCODES,
)
from eth.eof.v1.constants import (
    MAGIC_EOF_PREFIX,
)
from eth.vm.computation import (
    BaseComputation,
    NO_RESULT,
)
from eth.vm.forks.shanghai.computation import (
    ShanghaiComputation,
)
from ...logic.invalid import InvalidOpcode
from ...stack import Stack


class CancunComputation(ShanghaiComputation):
    """
    A class for all execution computations in the ``Cancun`` hard fork
    """

    # A return stack is introduced for EOF computations in EIP-4750
    _return_stack = Stack()

    opcodes = CANCUN_LEGACY_OPCODES

    @staticmethod
    def _execute_legacy_bytecode(computation: ComputationAPI):
        show_debug2 = computation.logger.show_debug2

        if show_debug2:
            computation.logger.debug2("-- legacy bytecode execution rules --")

        opcode_lookup = computation.opcodes
        for opcode in computation.code:
            try:
                opcode_fn = opcode_lookup[opcode]
            except KeyError:
                opcode_fn = InvalidOpcode(opcode)

            if show_debug2:
                # We dig into some internals for debug logs
                base_comp = cast(BaseComputation, computation)
                computation.logger.debug2(
                    "OPCODE: 0x%x (%s) | pc: %s | stack: %s",
                    opcode,
                    opcode_fn.mnemonic,
                    max(0, computation.code.program_counter - 1),
                    base_comp._stack,
                )
            try:
                opcode_fn(computation=computation)
            except Halt:
                break

    @staticmethod
    def _execute_eof_bytecode(computation: ComputationAPI):
        computation.logger.debug2("-- EOF bytecode execution rules --")
        # import pdb; pdb.set_trace()

    @classmethod
    def apply_computation(
        cls,
        state: StateAPI,
        message: MessageAPI,
        transaction_context: TransactionContextAPI,
    ) -> ComputationAPI:
        computation = cls(state, message, transaction_context)

        if message.is_create and computation.is_origin_computation:
            # If computation is from a create transaction, consume initcode gas if
            # >= Shanghai. CREATE and CREATE2 are handled in the opcode
            # implementations.
            cls.consume_initcode_gas_cost(computation)

        # Early exit on pre-compiles
        precompile = computation.precompiles.get(
            message.code_address, NO_RESULT
        )
        if precompile is not NO_RESULT:
            precompile(computation)
            return computation

        if computation.code[0:2] == MAGIC_EOF_PREFIX:
            cls._execute_eof_bytecode(computation)
        else:
            cls._execute_legacy_bytecode(computation)

        return computation
