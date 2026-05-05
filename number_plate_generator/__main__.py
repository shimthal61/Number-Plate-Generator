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
    
    if len(memory_tag) != 2 or not memory_tag.isalpha() or any(letter in "IQZ" for letter in memory_tag):
        print("Memory tag must be exactly two letters and cannot contain I, Q, or Z.")
        sys.exit(1)

    date = sys.argv[2]

    parts = date.split("/")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        print("Date must be in the format DD/MM/YYYY.")
        sys.exit(1)

    _, month, year = map(int, parts)
    if not (1 <= month <= 12 and year >= 2000):
        print("Date must be in the format DD/MM/YYYY, with month 1-12 and year >= 2000.")
        sys.exit(1)

    generator = NumberPlateGenerator(DEFAULT_STATE_FILE)
    plate = generator.generate(memory_tag, date)
    print(plate)


if __name__ == "__main__":
    main()
