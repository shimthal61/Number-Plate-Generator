# creates a generator using pytest's tmp_path fixture, so every test gets a fresh state file in a unique temp directory.

import pytest

from number_plate_generator.plate_generator import NumberPlateGenerator

@pytest.fixture
def generator(tmp_path) -> NumberPlateGenerator:
    return NumberPlateGenerator(state_file=tmp_path / "test_state.json")
