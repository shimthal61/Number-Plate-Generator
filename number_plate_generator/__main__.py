import sys

from number_plate_generator.plate_generator import DEFAULT_STATE_FILE, NumberPlateGenerator


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

    memory_tag = sys.argv[1].upper()
    date = sys.argv[2]
    count = int(sys.argv[3])

    generator = NumberPlateGenerator(DEFAULT_STATE_FILE)
    
    plates_list = [generator.generate(memory_tag, date) for _ in range(count)]
    
    print(plates_list)
    
    print("\nIssued plate counts by prefix:")

    counts = {f"{prefix}: {count}" for prefix, count in generator.count_issued().items() if count > 1000}

    print(type(counts))

if __name__ == "__main__":
    main()
