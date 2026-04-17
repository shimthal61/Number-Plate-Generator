import re

from number_plate_generator.plate_generator import NumberPlateGenerator


# Tests are grouped into classes by concern. This keeps related assertions
# together and makes failures easy to locate at a glance.


class TestPlateFormat:
    """The output string must match the documented XX00 XXX structure."""

    def test_output_matches_expected_format(self, generator: NumberPlateGenerator) -> None:
        # A regex is the most direct way to assert structural format.
        # ^[A-Z]{2}  — two uppercase letters (memory tag)
        # \d{2}      — two digits (age identifier)
        # space
        # [A-Z]{3}$  — three uppercase letters (random suffix)
        plate = generator.generate("MV", "03/04/2010")
        assert re.match(r"^[A-Z]{2}\d{2} [A-Z]{3}$", plate)

    def test_memory_tag_is_preserved_in_output(self, generator: NumberPlateGenerator) -> None:
        # The memory tag is caller-supplied and must appear verbatim at the start.
        plate = generator.generate("AB", "01/06/2020")
        assert plate.startswith("AB")


class TestAgeIdentifier:
    """
    The age identifier occupies characters 3-4 of the plate (index 2:4).

    Rules:
      March–August   → last two digits of the year (e.g. 2010 → "10")
      September–Dec  → last two digits + 50         (e.g. 2001 → "51")
      January–Feb    → last two digits of the *previous* year + 50
                       (these months belong to the Sep–Feb window that
                        started in the preceding calendar year)
    """

    def test_march_to_august_uses_last_two_digits_of_year(self, generator: NumberPlateGenerator) -> None:
        # Happy-path first half: April 2010 → age "10"
        plate = generator.generate("MV", "03/04/2010")
        assert plate[2:4] == "10"

    def test_september_to_december_adds_50(self, generator: NumberPlateGenerator) -> None:
        # Happy-path second half: September 2001 → 01 + 50 = "51"
        plate = generator.generate("YA", "25/09/2001")
        assert plate[2:4] == "51"

    def test_january_uses_previous_year_plus_50(self, generator: NumberPlateGenerator) -> None:
        # January 2003 belongs to the Sept 2002 – Feb 2003 window.
        # Year used is 2002 → 02 + 50 = 52.
        # This is the most common mistake in implementing the age rule.
        plate = generator.generate("AB", "01/01/2003")
        assert plate[2:4] == "52"

    def test_february_uses_previous_year_plus_50(self, generator: NumberPlateGenerator) -> None:
        # February 2003 is in the same window as January 2003 above → "52".
        plate = generator.generate("AB", "28/02/2003")
        assert plate[2:4] == "52"

    def test_boundary_march_first_is_first_half(self, generator: NumberPlateGenerator) -> None:
        # March 1st is the very first day of the first-half window.
        plate = generator.generate("AB", "01/03/2015")
        assert plate[2:4] == "15"

    def test_boundary_august_last_is_first_half(self, generator: NumberPlateGenerator) -> None:
        # August 31st is the very last day of the first-half window.
        plate = generator.generate("AB", "31/08/2015")
        assert plate[2:4] == "15"

    def test_boundary_september_first_is_second_half(self, generator: NumberPlateGenerator) -> None:
        # September 1st is the very first day of the second-half window → 15 + 50 = "65".
        plate = generator.generate("AB", "01/09/2015")
        assert plate[2:4] == "65"

    def test_known_example_one_from_spec(self, generator: NumberPlateGenerator) -> None:
        # Spec example 1: MV + 03/04/2010 → "MV10 ..."
        plate = generator.generate("MV", "03/04/2010")
        assert plate.startswith("MV10")

    def test_known_example_two_from_spec(self, generator: NumberPlateGenerator) -> None:
        # Spec example 2: YA + 25/09/2001 → "YA51 ..."
        plate = generator.generate("YA", "25/09/2001")
        assert plate.startswith("YA51")


class TestRandomLetters:
    """The three random suffix letters must obey the restricted-character rule."""

    def test_suffix_is_exactly_three_characters(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("AB", "01/06/2020")
        suffix = plate.split(" ")[1]
        assert len(suffix) == 3

    def test_restricted_letters_never_appear_in_suffix(self, generator: NumberPlateGenerator) -> None:
        # Generate 50 plates from the same prefix so we sample a wide range of
        # suffixes without changing the memory tag or age identifier.
        # Probabilistically, if I/Q/Z could appear, they would surface here.
        plates = [generator.generate("AB", "01/06/2020") for _ in range(50)]
        for plate in plates:
            suffix = plate.split(" ")[1]
            for restricted in ("I", "Q", "Z"):
                assert restricted not in suffix, f"Restricted letter '{restricted}' found in '{plate}'"


class TestUniqueness:
    """No two generated plates should ever be identical."""

    def test_no_duplicate_plates_within_same_prefix(self, generator: NumberPlateGenerator) -> None:
        # 100 plates from the same memory tag + date → all must be distinct.
        # Comparing len(list) vs len(set) is the simplest duplicate check.
        plates = [generator.generate("AB", "01/06/2020") for _ in range(100)]
        assert len(plates) == len(set(plates))
