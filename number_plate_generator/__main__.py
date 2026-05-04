import sys

from number_plate_generator.plate_generator import DEFAULT_STATE_FILE, NumberPlateGenerator


def main() -> None:
    # --reset is a special flag that clears all plate history without generating
    # a new plate. It is handled before the normal argument check.
    if len(sys.argv) == 2 and sys.argv[1] == "--reset":
        NumberPlateGenerator(DEFAULT_STATE_FILE).reset()
        print("Plate history cleared.")
        return

    if len(sys.argv) != 3:
        print("Usage: python -m number_plate_generator <memory_tag> <date>\n"
              "python -m number_plate_generator --reset\n"
              "Example: python -m number_plate_generator MV 03/04/2010"
              )
        sys.exit(1)

    # Convert memory tag to uppercase and read date.
    memory_tag = sys.argv[1].upper()
    date = sys.argv[2]

    # Creates a generator pointing at the default state file.
    generator = NumberPlateGenerator(DEFAULT_STATE_FILE)
    # Generate a plate using user's inputs
    plate = generator.generate(memory_tag, date)
    print(plate)


if __name__ == "__main__":
    main()
