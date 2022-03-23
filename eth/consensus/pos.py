from typing import (
    Iterable,
)

from eth_typing import (
    Address,
    Hash32,
)

from eth.abc import (
    AtomicDatabaseAPI,
    BlockHeaderAPI,
    ConsensusAPI,
)
from eth.constants import (
    POST_MERGE_DIFFICULTY,
    POST_MERGE_NONCE,
)
from eth.validation import (
    validate_length,
)


def check_merge_rules_pos(
    mix_hash: Hash32,
    nonce: bytes,
    difficulty: int
) -> None:
    validate_length(mix_hash, 32, title="Mix Hash")
    validate_length(nonce, 8, title="POS Nonce")

    assert (
        nonce == POST_MERGE_NONCE,
        f"Unexpected Post-Merge None {nonce}",
    )
    assert (
        difficulty == POST_MERGE_DIFFICULTY,
        f"Unexpected Post-Merge Difficulty {difficulty}"
    )


class PosConsensus(ConsensusAPI):
    """
    Modify a set of VMs to validate blocks via Proof of Work (POW)
    """

    def __init__(self, base_db: AtomicDatabaseAPI) -> None:
        pass

    def validate_seal(self, header: BlockHeaderAPI) -> None:
        """
        Validate the seal on the given header by checking the proof of work.
        """
        check_merge_rules_pos(
            header.mix_hash,
            header.nonce,
            header.difficulty
        )

    def validate_seal_extension(self,
                                header: BlockHeaderAPI,
                                parents: Iterable[BlockHeaderAPI]) -> None:
        pass

    @classmethod
    def get_fee_recipient(cls, header: BlockHeaderAPI) -> Address:
        """
        Return the ``coinbase`` of the passed ``header`` as the receipient for any
        rewards for the block.
        """
        pass
