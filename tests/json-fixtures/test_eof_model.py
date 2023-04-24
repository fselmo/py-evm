# TODO: This test will likely not exist as it currently is. This is useful for
#  debugging the EOF model validation while development is in progress.

import os
import pytest

from hexbytes import (
    HexBytes,
)

from eth.tools.fixtures import (
    filter_fixtures,
    generate_fixture_tests,
    load_fixture,
)
from eth.eof import (
    EOFContainerV1,
)

from eth_utils import (
    ValidationError, to_tuple,
)

from eth_typing import (
    ForkName,
)


ROOT_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


BASE_FIXTURE_PATH = os.path.join(
    ROOT_PROJECT_DIR,
    "fixtures",
    "EOFTests",
)

# Fixtures have an `_info` key at their root which we need to skip over.
FIXTURE_FORK_SKIPS = {'_info'}


@to_tuple
def expand_fixtures_forks(all_fixtures):
    """
    The transaction fixtures have different definitions for each fork and must be
    expanded one step further to have one fixture for each defined fork within
    the fixture.
    """
    for fixture_path, fixture_key in all_fixtures:
        if not fixture_key.startswith("ymlExample"):
            fixture = load_fixture(fixture_path, fixture_key)
            results = [
                vector_dict["results"] for vector_dict in list(fixture["vectors"].values())
            ]
            forks = [list(result.keys()) for result in results][0]
            for fixture_fork in forks:
                if fixture_fork not in FIXTURE_FORK_SKIPS:
                    yield fixture_path, fixture_key, fixture_fork


def pytest_generate_tests(metafunc):
    generate_fixture_tests(
        metafunc=metafunc,
        base_fixture_path=BASE_FIXTURE_PATH,
        preprocess_fn=expand_fixtures_forks,
    )


@pytest.fixture
def fixture(fixture_data):
    fixture_path, fixture_key, fixture_fork = fixture_data
    fixture = load_fixture(
        fixture_path,
        fixture_key,
    )

    return fixture


EOF_FORMAT_FORK_MAP = {
    "Cancun": EOFContainerV1,
}


def test_eof_model(fixture):
    vectors = fixture["vectors"]

    likely_execution_fails = []

    for test_name in vectors:
        if not test_name.startswith("ymlExample"):
            vector = vectors[test_name]

            bytecode = HexBytes(vector["code"])

            for fork_name in vector["results"]:
                container_should_be_valid = vector["results"][fork_name]["result"]

                if container_should_be_valid:
                    eof_container_class = EOF_FORMAT_FORK_MAP[fork_name]

                    eof = eof_container_class.from_bytecode(bytecode)

                    eof_as_bytecode = eof.as_bytecode()
                    assert eof_as_bytecode == bytecode

                    reconstructed_eof = eof_container_class.from_bytecode(
                        eof_as_bytecode
                    )
                    assert reconstructed_eof == eof

                else:
                    if fork_name not in EOF_FORMAT_FORK_MAP.keys():
                        # For pre-EOF forks, there is no EOF model to validate and those
                        #  tests are expected to fail every time.
                        continue

                    try:
                        eof_container_class = EOF_FORMAT_FORK_MAP[fork_name]
                        eof_container_class.from_bytecode(bytecode)
                        likely_execution_fails.append(bytecode)
                    except (ValueError, ValidationError, AssertionError):
                        # exception is expected
                        pass

    print(likely_execution_fails)
