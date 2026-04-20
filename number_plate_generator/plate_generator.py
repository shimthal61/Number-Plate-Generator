import itertools
import json
import random
import string
from pathlib import Path

# Letters banned from number plates — they look too similar to digits. A frozenset gives O(1) membership checks.
RESTRICTED_LETTERS = frozenset({"I", "Q", "Z"})

# Every uppercase letter except the three restricted ones.
# This is the only alphabet from which random suffixes are drawn.
VALID_LETTERS = [c for c in string.ascii_uppercase if c not in RESTRICTED_LETTERS]

# Default location for the state file. Using Path keeps file handling
# cross-platform and avoids raw string concatenation.
DEFAULT_STATE_FILE = Path("plate_state.json")


class NumberPlateGenerator:
    """
    Generates unique UK-format number plates of the form: XX00 XXX
      XX  — caller-supplied DVLA memory tag
      00  — age identifier derived from the registration date
      XXX — three randomly-chosen letters (never I, Q, or Z)

    State is persisted to a JSON file so that no plate is ever repeated
    across separate runs of the program. Call reset() to clear this history.
    """

    def __init__(self, state_file: Path = DEFAULT_STATE_FILE) -> None:
        # Accepting state_file as a parameter (rather than hardcoding it) means
        # tests can point each generator at a throwaway temp file, keeping tests
        # isolated from each other and from the real state file.
        self._state_file = Path(state_file)
        self._initialise()

    def _initialise(self) -> None:
        if self._state_file.exists():
            # Restore the shuffle seed and per-prefix draw indices from disk.
            state = self._load_state()
            seed = state["seed"]
            self._prefix_index: dict[str, int] = state["prefix_index"]
        else:
            # First run: generate a truly random seed so the pool order is
            # unpredictable. Subsequent runs will reload this same seed,
            # reconstructing an identical pool in the same order.
            seed = random.randint(0, 2**32 - 1)
            self._prefix_index = {}

        self._seed = seed

        # random.Random(seed) creates an isolated random instance so this shuffle
        # does not affect any other random calls elsewhere in the program.
        rng = random.Random(self._seed)
        all_suffixes = ["".join(combo) for combo in itertools.product(VALID_LETTERS, repeat=3)]
        rng.shuffle(all_suffixes)
        self._suffix_pool: list[str] = all_suffixes

        # Persist immediately so the seed is saved even before any plates are generated.
        self._save_state()

    def generate(self, memory_tag: str, date: str) -> str:
        """Return a unique plate for the given memory tag and registration date."""
        age = self._calculate_age_identifier(date)
        # :02d zero-pads single-digit ages so "2" becomes "02"
        prefix = f"{memory_tag}{age:02d}"
        suffix = self._next_suffix(prefix)
        # Save after every generation so no issued plate is ever forgotten,
        # even if the program exits immediately afterwards.
        self._save_state()
        return f"{prefix} {suffix}"

    def reset(self) -> None:
        """Delete the persisted state and start fresh with a new random pool."""
        # Deleting the file before re-initialising means a new random seed is
        # chosen, producing a different pool order — not just the same sequence
        # restarted from the beginning.
        if self._state_file.exists():
            self._state_file.unlink()
        self._initialise()

    def _calculate_age_identifier(self, date: str) -> int:
        # Parse dd/mm/yyyy — splitting on "/" is sufficient; no library needed.
        _, month, year = (int(part) for part in date.split("/"))

        # The vehicle year runs March → February, divided into two halves:
        #   First half  (Mar–Aug): age = last two digits of the calendar year
        #   Second half (Sep–Feb): age = last two digits + 50
        #
        # January and February belong to the second half of the *previous*
        # calendar year (e.g. Feb 2003 → the Sep 2002–Feb 2003 window → 52).
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
