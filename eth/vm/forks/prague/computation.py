from eth_utils.toolz import (
    merge,
)

from eth._utils.address import (
    force_bytes_to_address,
)
from eth.precompiles.bls12_381.bls12_381_g1 import (
    bls12_g1_add_precompile,
    bls12_g1_msm_precompile,
    bls12_map_fp_to_g1_precompile,
)
from eth.vm.forks.cancun.computation import (
    CancunComputation,
)
from eth.vm.forks.prague.constants import (
    BLS12_G1ADD_PRECOMPILE_ADDRESS,
    BLS12_G1MSM_PRECOMPILE_ADDRESS,
    BLS12_MAP_FP_TO_G1_PRECOMPILE_ADDRESS,
)
from eth.vm.forks.prague.opcodes import (
    PRAGUE_OPCODES,
)

PRAGUE_PRECOMPILES = merge(
    CancunComputation.get_precompiles(),
    {
        force_bytes_to_address(BLS12_G1ADD_PRECOMPILE_ADDRESS): bls12_g1_add_precompile,
        force_bytes_to_address(BLS12_G1MSM_PRECOMPILE_ADDRESS): bls12_g1_msm_precompile,
        # force_bytes_to_address(BLS12_G2ADD_PRECOMPILE_ADDRESS): bls12_g2_add_precompile,  # noqa: E501
        # force_bytes_to_address(BLS12_G2MSM_PRECOMPILE_ADDRESS): bls12_g2_msm_precompile,  # noqa: E501
        # force_bytes_to_address(BLS12_PAIRING_CHECK_PRECOMPILE_ADDRESS): bls12_pairing_check_precompile,  # noqa: E501
        force_bytes_to_address(
            BLS12_MAP_FP_TO_G1_PRECOMPILE_ADDRESS
        ): bls12_map_fp_to_g1_precompile,  # noqa: E501
        # force_bytes_to_address(BLS12_MAP_FP2_TO_G2_PRECOMPILE_ADDRESS): bls12_map_fp2_to_g2_precompile,  # noqa: E501
    },
)


class PragueComputation(CancunComputation):
    """
    A class for all execution computations in the ``Prague`` hard fork
    """

    opcodes = PRAGUE_OPCODES
    _precompiles = PRAGUE_PRECOMPILES
