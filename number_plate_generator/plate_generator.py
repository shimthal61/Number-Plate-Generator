import itertools # Used to generate all 3 letter suffixes
import json # saving/loading keys to JSON file.
import random # shuffling plate order and seed
import string # Gives us all uppercase letters in alphabet
from pathlib import Path # Used to define path rather than raw strings.

# Letters banned from number plates. 
# Using sets for fast membership checks (0(1) lookup).

RESTRICTED_LETTERS = frozenset({"I", "Q", "Z"})

# Every uppercase letter except the three restricted ones. Keep as list to preserve order for suffix generation.
VALID_LETTERS = [c for c in string.ascii_uppercase if c not in RESTRICTED_LETTERS]

# Default location for the plate storage file.
DEFAULT_STATE_FILE = Path("plate_state.json")

# Use OOP as we want to store data between function calls in self.prefix_index and self.suffix_pool.
class NumberPlateGenerator:
    """
    Generates unique UK-format number plates of the form: XX00 XXX
      XX  — caller-supplied DVLA memory tag
      00  — age identifier derived from the registration date
      XXX — three randomly-chosen letters (excluding I, Q, or Z)

    State is persisted to a JSON file so that no plate is ever repeated
    across separate runs of the program. Call reset() to clear this history.
    """

    def __init__(self, state_file: Path = DEFAULT_STATE_FILE) -> None:
        # constructor - stores and preserves state file path
        self._state_file = Path(state_file)
        self._initialise()

    def _initialise(self) -> None:
        # Check whether state file exists to determine whether to load existing state or start fresh.
        if self._state_file.exists():
            # Calls method that reads json file and returns dict
            state = self._load_state()
            # takes the seed from the loaded dict
            seed = state["seed"]
            # dict type hint pulls from loaded state
            self._prefix_index: dict[str, int] = state["prefix_index"]
        else:
            # Otherwise generate random seed and empty index
            seed = random.randint(0, 2**32 - 1)
            self._prefix_index = {}

        # Stores seed in class instance
        self._seed = seed

        # random.Random(seed) creates an isolated random instance so this shuffle does not affect any other random calls elsewhere in the program.
        rng = random.Random(self._seed)
        # Nested for loop takes (product()) each combination of 3 letters, then takes each tuple and kjoins it into a single string
        all_suffixes = ["".join(combo) for combo in itertools.product(VALID_LETTERS, repeat=3)]
        # Shuffles list into random order using seeded rng
        rng.shuffle(all_suffixes)
        # Stores shuffled suffix list in class instance.
        self._suffix_pool: list[str] = all_suffixes

        # Persist immediately so the seed is saved even before any plates are generated.
        self._save_state()

    def generate(self, memory_tag: str, date: str) -> str:
        """Return a unique plate for the given memory tag and registration date."""
        # Calculate the age identifier from the date
        age = self._calculate_age_identifier(date)
        # :02d format specs that formats 02 as a pad with leading zeros to a mun width of 2, and d as a decimal integer (i.e. so 2 becomes "02" but 12 stays "12")
        prefix = f"{memory_tag}{age:02d}"
        # Gets the next unused suffix
        suffix = self._next_suffix(prefix)
        # Save the new state to the disk immediately so that if the program is interrupted, we don't lose progress and accidentally reuse plates.
        self._save_state()
        # Combines the two halves and returns the full plate string.
        return f"{prefix} {suffix}"

    def reset(self) -> None:
        """Delete the persisted state and start fresh with a new random pool."""
        # If the state file exists, delete it to clear history. Then reinitialise to start with a new seed and empty index.
        if self._state_file.exists():
            self._state_file.unlink()
        self._initialise()

    def _calculate_age_identifier(self, date: str) -> int:
        # Parse dd/mm/yyyy — splitting on "/" is sufficient; no library needed.
        date = "01/01/2004"
        
        # Generator expression, ignore day part of the date.
        _, month, year = (int(part) for part in date.split("/"))

        #
        if 3 <= month <= 8:
            return year % 100
        elif month >= 9:
            return year % 100 + 50
        else:  # month in (1, 2) — January or February
            return (year - 1) % 100 + 50

    def _next_suffix(self, prefix: str) -> str:
        # Get (or initialise at 0) the current draw position for this prefix.
        idx = self._prefix_index.get(prefix, 0)
        if idx >= len(self._suffix_pool):
            raise ValueError(
                f"All {len(self._suffix_pool)} possible plates for prefix "
                f"'{prefix}' have been exhausted."
            )
        suffix = self._suffix_pool[idx]
        # Advance the index so the next call for this prefix gets a different suffix.
        self._prefix_index[prefix] = idx + 1
        return suffix

    def _save_state(self) -> None:
        state = {"seed": self._seed, "prefix_index": self._prefix_index}
        self._state_file.write_text(json.dumps(state, indent=2))

    def _load_state(self) -> dict:
        return json.loads(self._state_file.read_text())
