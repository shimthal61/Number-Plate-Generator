import sys

from number_plate_generator.plate_generator import DEFAULT_STATE_FILE, NumberPlateGenerator


def main() -> None:
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

    memory_tag = sys.argv[1].upper()
    date = sys.argv[2]

    generator = NumberPlateGenerator(DEFAULT_STATE_FILE)
    plate = generator.generate(memory_tag, date)
    print(plate)


if __name__ == "__main__":
    main()
