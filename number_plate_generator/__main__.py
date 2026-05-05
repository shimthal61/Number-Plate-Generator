import sys
from datetime import datetime

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

    try:
        parsed_date = datetime.strptime(date, "%d/%m/%Y")
    except ValueError:
        print("Date must be a valid date in DD/MM/YYYY format (e.g. 03/04/2010).")
        sys.exit(1)

    if parsed_date.year < 2000:
        print("Year must be 2000 or later.")
        sys.exit(1)

    generator = NumberPlateGenerator(DEFAULT_STATE_FILE)
    plate = generator.generate(memory_tag, date)
    print(plate)


if __name__ == "__main__":
    main()
