import sys

from number_plate_generator.plate_generator import DEFAULT_STATE_FILE, NumberPlateGenerator
import re


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == "--reset":
        NumberPlateGenerator(DEFAULT_STATE_FILE).reset()
        print("Plate history cleared.")
        return
    
    if len(sys.argv) == 3 and sys.argv[2] == "--reset-prefix":
        prefix = sys.argv[1].upper()
        generator = NumberPlateGenerator(DEFAULT_STATE_FILE)
        generator.reset_index(prefix)
        print(f"Plate history for prefix '{prefix}' cleared.")
        return
    
    if len(sys.argv) != 4:
        print("Usage: python -m number_plate_generator <memory_tag> <date> <count>\n"
              "python -m number_plate_generator --reset\n"
              "Example: python -m number_plate_generator MV 03/04/2010 5"
              )
        sys.exit(1)
    
    # Validate memory_tag
    try:
      memory_tag = sys.argv[1].upper()
      if not sys.argv[1].isalpha():
        print("Error: Memory tag must contain only letters.")
        sys.exit(1)
      if len(memory_tag) != 2:
        print("Error: Memory tag must be exactly 2 letters.")
        sys.exit(1)
    except ValueError:
      print("Error: Memory tag must be a valid string.")
      sys.exit(1)
    
    # Validate date format (DD/MM/YYYY)
    try:
        date = sys.argv[2]
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', date):
          print("Error: Date must be in DD/MM/YYYY format.")
          sys.exit(1)
    except ValueError:
       print("Error: Date must be a valid string.")
       sys.exit(1)
    
    # Validate count
    try:
      count = int(sys.argv[3])
      if count <= 0:
        print("Error: Count must be a positive integer.")
        sys.exit(1)
    except ValueError:
      print("Error: Count must be a valid integer.")
      sys.exit(1)

    generator = NumberPlateGenerator(DEFAULT_STATE_FILE)
    
    plates_list = [generator.generate(memory_tag, date) for _ in range(count)]
    
    print(plates_list)
    
    print("\nIssued plate counts by prefix:")

    counts = {f"{prefix}: {count}" for prefix, count in generator.count_issued().items() if count > 1000}

    print(type(counts))

if __name__ == "__main__":
    main()
