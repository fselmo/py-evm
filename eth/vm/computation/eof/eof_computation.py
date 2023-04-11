from eth.abc import GasMeterAPI
from eth.vm.computation import BaseComputation


class EOFComputation(BaseComputation):
    version: int

    def _configure_gas_meter(self) -> GasMeterAPI:
        pass
