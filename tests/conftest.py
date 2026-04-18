import pytest

from number_plate_generator.plate_generator import NumberPlateGenerator


# tmp_path is a pytest built-in fixture that provides a unique temporary
# directory for each test. Passing a temp state file means every test gets
# a clean generator with no history, and no test ever writes to the real
# plate_state.json on disk.
@pytest.fixture
def generator(tmp_path) -> NumberPlateGenerator:
    return NumberPlateGenerator(state_file=tmp_path / "test_state.json")
