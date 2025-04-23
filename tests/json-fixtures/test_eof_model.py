# TODO: This test will likely not exist as it currently is. This is useful for
#  debugging the EOF model validation while development is in progress.

import pytest
import os

from eth_typing import (
    ForkName,
)
from eth_utils import (
    ValidationError,
)
from hexbytes import (
    HexBytes,
)

from eth.tools.fixtures import (
    filter_fixtures,
    generate_fixture_tests,
    load_fixture,
)
from eth.vm.forks.cancun.eof import (
    EOFContainerV1,
)

ROOT_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


BASE_FIXTURE_PATH = os.path.join(
    ROOT_PROJECT_DIR,
    "fixtures",
    "EOFTests",
    "efExample",
)


def pytest_generate_tests(metafunc):
    generate_fixture_tests(
        metafunc=metafunc,
        base_fixture_path=BASE_FIXTURE_PATH,
        filter_fn=filter_fixtures(
            fixtures_base_dir=BASE_FIXTURE_PATH,
        ),
    )


@pytest.fixture
def fixture(fixture_data):
    fixture_path, fixture_key = fixture_data
    fixture = load_fixture(
        fixture_path,
        fixture_key,
    )
    return fixture


EOF_FORMAT_FORK_MAP = {
    ForkName.Shanghai: EOFContainerV1,
}


class TestShouldHaveFailed(Exception):
    pass


def test_eof_model(fixture):
    vectors = fixture["vectors"]

    likely_execution_fails = []

    for test_name in vectors:
        # TODO: test "validInvalid_32" has mismatched `header.data_size` and
        #  `len(body.data_section)`. Confirming if this is a bug in the test.
        if test_name.startswith("validInvalid") and not test_name.endswith("_32"):
            vector = vectors[test_name]

            full_bytecode = vector["code"]
            eof_bytecode = HexBytes(full_bytecode[full_bytecode.find("ef") :])

            for fork_name in vector["results"]:
                container_should_be_valid = vector["results"][fork_name]["result"]

                eof_container_class = EOF_FORMAT_FORK_MAP[fork_name]

                if container_should_be_valid:
                    eof = eof_container_class.from_bytecode(eof_bytecode)

                    eof_as_bytecode = eof.as_bytecode()
                    assert eof_as_bytecode == eof_bytecode

                    reconstructed_eof = eof_container_class.from_bytecode(
                        eof_as_bytecode
                    )
                    assert reconstructed_eof == eof

                else:
                    try:
                        eof_container_class.from_bytecode(eof_bytecode)
                        likely_execution_fails.append(eof_bytecode)
                        # raise TestShouldHaveFailed(
                        #     "EOFContainer.from_bytecode() should have failed here."
                        # )
                    except (ValueError, ValidationError, AssertionError):
                        # exception is expected
                        pass

    print(likely_execution_fails)
