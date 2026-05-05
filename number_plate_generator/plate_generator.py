import itertools
import json
import random
import string
from pathlib import Path

RESTRICTED_LETTERS = frozenset({"I", "Q", "Z"})
VALID_LETTERS = [c for c in string.ascii_uppercase if c not in RESTRICTED_LETTERS]
DEFAULT_STATE_FILE = Path("plate_state.json")


class NumberPlateGenerator:
    """
    Generates unique UK-format number plates of the form: XX00 XXX
      XX  — caller-supplied DVLA memory tag
      00  — age identifier derived from the registration date
      XXX — three randomly-chosen letters (excluding I, Q, or Z)

    State is persisted to a JSON file so no plate is ever repeated
    across separate runs of the program. Call reset() to clear this history.
    """

    def __init__(self, state_file: Path = DEFAULT_STATE_FILE) -> None:
        self._state_file = Path(state_file)
        self._setup_state()

    def _setup_state(self) -> None:
        if self._state_file.exists():
            state = self._load_state()
            seed = state["seed"]
            self._prefix_index: dict[str, int] = state["prefix_index"]
        else:
            seed = random.randint(0, 2**32 - 1)
            self._prefix_index = {}

        self._seed = seed
        rng = random.Random(self._seed)
        all_suffixes = ["".join(combo) for combo in itertools.product(VALID_LETTERS, repeat=3)]
        rng.shuffle(all_suffixes)
        self._suffix_pool: list[str] = all_suffixes

        self._save_state()

    def generate(self, memory_tag: str, date: str) -> str:
        """Return a unique plate for the given memory tag and registration date."""
        age = self._calculate_age_identifier(date)
        prefix = f"{memory_tag}{age:02d}"
        suffix = self._next_suffix(prefix)
        self._save_state()
        return f"{prefix} {suffix}"

    def reset(self) -> None:
        """Delete the persisted state and start fresh with a new random pool."""
        if self._state_file.exists():
            self._state_file.unlink()
        self._setup_state()

    def _calculate_age_identifier(self, date: str) -> int:
        _, month, year = (int(part) for part in date.split("/"))

        if 3 <= month <= 8:
            return year % 100
        elif month >= 9:
            return year % 100 + 50
        else:
            return (year - 1) % 100 + 50

    def _next_suffix(self, prefix: str) -> str:
        idx = self._prefix_index.get(prefix, 0)
        if idx >= len(self._suffix_pool):
            raise ValueError(
                f"All {len(self._suffix_pool)} possible plates for prefix "
                f"'{prefix}' have been exhausted."
            )
        suffix = self._suffix_pool[idx]
        self._prefix_index[prefix] = idx + 1
        return suffix

    def _save_state(self) -> None:
        state = {"seed": self._seed, "prefix_index": self._prefix_index}
        self._state_file.write_text(json.dumps(state, indent=2))

    def _load_state(self) -> dict:
        return json.loads(self._state_file.read_text())

    def count_issued(self) -> dict[str, int]:
        return {prefix: idx for prefix, idx in self._prefix_index.items()}
    
    def reset_index(self, prefix: str) -> None:
        if prefix in self._prefix_index:
            del self._prefix_index[prefix]
            self._save_state()