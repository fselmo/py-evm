from typing import (
    Dict,
    cast,
)

from eth.abc import (
    ComputationAPI,
    MessageAPI,
    OpcodeAPI,
    StackAPI,
    StateAPI,
    TransactionContextAPI,
)
from eth.eof import EOFContainerV1
from eth.exceptions import Halt

from .opcodes import (
    PRAGUE_EOF_OPCODES,
    PRAGUE_LEGACY_OPCODES,
)
from eth.eof.v1.constants import (
    MAGIC_EOF_PREFIX,
)
from eth.vm.computation import (
    BaseComputation, NO_RESULT,
)
from eth.vm.forks.shanghai.computation import (
    ShanghaiComputation,
)
from ...logic.invalid import InvalidOpcode


class PragueComputation(ShanghaiComputation):
    """
    A class for all execution computations in the ``Prague`` hard fork
    """
    _legacy_opcodes: Dict[int, OpcodeAPI] = PRAGUE_LEGACY_OPCODES
    _eof_opcodes: Dict[int, OpcodeAPI] = PRAGUE_EOF_OPCODES

    # -- eof config -- #
    @property
    def is_eof_computation(self) -> bool:
        return self.msg.code.startswith(MAGIC_EOF_PREFIX)

    # TODO: Find out when we implement EOF if it's useful to build it this way
    # @property
    # def return_stack(self) -> StackAPI:
    #     if not self.is_eof_computation:
    #         raise NotImplementedError("return_stack only applies to EOF computations")
    #     return self._return_stack
    #
    # @return_stack.setter
    # def return_stack(self, value: StackAPI) -> None:
    #     self._return_stack = value

    # -- properties -- #
    @classmethod
    def opcodes(cls) -> Dict[int, OpcodeAPI]:
        return cls._eof_opcodes if cls.is_eof_computation else cls._legacy_opcodes

    # -- applying the computation -- #
    @classmethod
    def apply_computation(
        cls,
        state: StateAPI,
        message: MessageAPI,
        transaction_context: TransactionContextAPI,
    ) -> ComputationAPI:
        with cls(state, message, transaction_context) as computation:

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

            if computation.is_eof_computation:
                cls._apply_eof_computation(computation)
            else:
                cls._apply_legacy_computation(computation)

        return computation

    @classmethod
    def _apply_eof_computation(cls, computation: ComputationAPI) -> ComputationAPI:
        show_debug2 = computation.logger.show_debug2
        if show_debug2:
            computation.logger.debug2("EOF Computation")

        # validates and builds container
        container = EOFContainerV1.from_bytecode(computation.msg.code)

        opcode_lookup = computation.opcodes
        for code in container.body.code_section:
            for opcode in code:
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

        return computation

    @classmethod
    def _apply_legacy_computation(cls, computation: ComputationAPI) -> ComputationAPI:
        show_debug2 = computation.logger.show_debug2
        if show_debug2:
            computation.logger.debug2("EOF Computation")

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

        return computation
