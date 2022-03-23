from eth.vm.forks.london.headers import (
    create_header_from_parent,
)
from eth.vm.forks.byzantium.headers import (
    compute_difficulty,
)
from eth.vm.forks.byzantium.headers import (
    configure_header,
)


compute_arrow_glacier_difficulty = compute_difficulty(10_700_000)

create_arrow_glacier_header_from_parent = create_header_from_parent(
    compute_arrow_glacier_difficulty
)

configure_arrow_glacier_header = configure_header(compute_arrow_glacier_difficulty)
