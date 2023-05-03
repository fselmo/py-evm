from eth.abc import ComputationAPI
from eth.exceptions import Halt


def callf_logic(computation: ComputationAPI):
    if not computation.is_eof_computation:  # consider something more elegant here
        raise Halt("CALLF is only valid in EOF computations")

    if computation._return_stack.__sizeof__() == 1024:
        raise Halt("Return stack overflow")
