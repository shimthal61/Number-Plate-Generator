import pytest

from number_plate_generator.plate_generator import NumberPlateGenerator


@pytest.fixture
def generator(tmp_path) -> NumberPlateGenerator:
    """A fresh generator with an isolated state file in a temp directory."""
    return NumberPlateGenerator(state_file=tmp_path / "test_state.json")
