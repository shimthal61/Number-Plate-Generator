import json
import re

from number_plate_generator.plate_generator import NumberPlateGenerator


class TestPlateFormat:
    """The output string must match the documented XX00 XXX structure."""

    def test_output_matches_expected_format(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("MV", "03/04/2010")
        # 2 uppercase letters, 2 digits, space, 3 uppercase letters
        assert re.match(r"^[A-Z]{2}\d{2} [A-Z]{3}$", plate)

    def test_memory_tag_is_preserved_in_output(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("AB", "01/06/2020")
        assert plate.startswith("AB")


class TestAgeIdentifier:
    """
    The age identifier occupies characters 3-4 of the plate (index 2:4).

    Rules:
      March–August   → last two digits of the year (e.g. 2010 → "10")
      September–Dec  → last two digits + 50         (e.g. 2001 → "51")
      January–Feb    → last two digits of the *previous* year + 50
    """

    def test_march_to_august_uses_last_two_digits_of_year(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("MV", "03/04/2010")
        assert plate[2:4] == "10"

    def test_september_to_december_adds_50(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("YA", "25/09/2001")
        assert plate[2:4] == "51"

    def test_january_uses_previous_year_plus_50(self, generator: NumberPlateGenerator) -> None:
        # Jan 2003 → Sept 2002 – Feb 2003 window → 02 + 50 = 52.
        plate = generator.generate("AB", "01/01/2003")
        assert plate[2:4] == "52"

    def test_february_uses_previous_year_plus_50(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("AB", "28/02/2003")
        assert plate[2:4] == "52"

    def test_boundary_march_first_is_first_half(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("AB", "01/03/2015")
        assert plate[2:4] == "15"

    def test_boundary_august_last_is_first_half(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("AB", "31/08/2015")
        assert plate[2:4] == "15"

    def test_boundary_september_first_is_second_half(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("AB", "01/09/2015")
        assert plate[2:4] == "65"

    def test_known_example_one_from_spec(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("MV", "03/04/2010")
        assert plate.startswith("MV10")

    def test_known_example_two_from_spec(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("YA", "25/09/2001")
        assert plate.startswith("YA51")


class TestRandomLetters:
    """The three random suffix letters must obey the restricted-character rule."""

    def test_suffix_is_exactly_three_characters(self, generator: NumberPlateGenerator) -> None:
        plate = generator.generate("AB", "01/06/2020")
        suffix = plate.split(" ")[1]
        assert len(suffix) == 3

    def test_restricted_letters_never_appear_in_suffix(self, generator: NumberPlateGenerator) -> None:
        # Generate 50 plates so we sample a wide range of suffixes.
        plates = [generator.generate("AB", "01/06/2020") for _ in range(50)]
        for plate in plates:
            suffix = plate.split(" ")[1]
            for restricted in ("I", "Q", "Z"):
                assert restricted not in suffix, f"Restricted letter '{restricted}' found in '{plate}'"


class TestUniqueness:
    """No two generated plates should ever be identical."""

    def test_no_duplicate_plates_within_same_prefix(self, generator: NumberPlateGenerator) -> None:
        # len(list) vs len(set) — a set cannot contain duplicates.
        plates = [generator.generate("AB", "01/06/2020") for _ in range(100)]
        assert len(plates) == len(set(plates))


class TestPersistence:
    """Plates must be unique across separate instances (i.e. separate program runs)."""

    def test_state_file_is_created_on_initialisation(self, tmp_path) -> None:
        state_file = tmp_path / "state.json"
        NumberPlateGenerator(state_file=state_file)
        assert state_file.exists()

    def test_plates_unique_across_separate_instances(self, tmp_path) -> None:
        # Two separate instances pointing at the same state file simulates two program runs.
        state_file = tmp_path / "state.json"
        plate1 = NumberPlateGenerator(state_file=state_file).generate("AB", "01/06/2020")
        plate2 = NumberPlateGenerator(state_file=state_file).generate("AB", "01/06/2020")
        assert plate1 != plate2

    def test_plates_unique_across_different_prefixes_and_back(self, tmp_path) -> None:
        # The DVLA scenario: prefix A → prefix B → prefix A again.
        state_file = tmp_path / "state.json"
        plate_a1 = NumberPlateGenerator(state_file=state_file).generate("MV", "03/04/2010")
        NumberPlateGenerator(state_file=state_file).generate("MV", "03/06/2025")
        plate_a2 = NumberPlateGenerator(state_file=state_file).generate("MV", "03/04/2010")
        assert plate_a1 != plate_a2

    def test_reset_clears_issued_plate_history(self, tmp_path) -> None:
        state_file = tmp_path / "state.json"
        gen = NumberPlateGenerator(state_file=state_file)
        gen.generate("AB", "01/06/2020")
        gen.reset()
        state = json.loads(state_file.read_text())
        assert state["prefix_index"] == {}
