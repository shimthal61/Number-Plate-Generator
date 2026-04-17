import pytest

from number_plate_generator.plate_generator import NumberPlateGenerator


# A pytest fixture provides a reusable object to tests that request it.
# Scoping it to the default ("function") means a brand-new generator is created
# for every single test — ensuring no used-plate state leaks between tests.
@pytest.fixture
def generator() -> NumberPlateGenerator:
    return NumberPlateGenerator()
