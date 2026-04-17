import itertools
import random
import string

# Letters banned from number plates — they look too similar to digits
# (I → 1, Q → 0, Z → 2). A frozenset gives O(1) membership checks.
RESTRICTED_LETTERS = frozenset({"I", "Q", "Z"})

# Every uppercase letter except the three restricted ones.
# This is the only alphabet from which random suffixes are drawn.
VALID_LETTERS = [c for c in string.ascii_uppercase if c not in RESTRICTED_LETTERS]


class NumberPlateGenerator:
    """
    Generates unique UK-format number plates of the form: XX00 XXX
      XX  — caller-supplied DVLA memory tag
      00  — age identifier derived from the registration date
      XXX — three randomly-chosen letters (never I, Q, or Z)

    One instance tracks every plate it has issued, so no plate is
    ever repeated for the lifetime of that instance.
    """

    def __init__(self) -> None:
        # itertools.product yields every combination of VALID_LETTERS of length 3.
        # With 23 letters this produces 23³ = 12,167 possible suffixes.
        # Building the full list once and shuffling it means plates are issued
        # in a random order without re-randomising on every single call.
        all_suffixes = ["".join(combo) for combo in itertools.product(VALID_LETTERS, repeat=3)]
        random.shuffle(all_suffixes)
        self._suffix_pool: list[str] = all_suffixes

        # Each unique prefix (e.g. "MV10") gets its own draw index into the pool.
        # Advancing the index on each draw is O(1) and guarantees no suffix
        # is reused for the same prefix.
        self._prefix_index: dict[str, int] = {}

    def generate(self, memory_tag: str, date: str) -> str:
        """Return a unique plate for the given memory tag and registration date."""
        age = self._calculate_age_identifier(date)
        # :02d zero-pads single-digit ages so "2" becomes "02"
        prefix = f"{memory_tag}{age:02d}"
        suffix = self._next_suffix(prefix)
        return f"{prefix} {suffix}"

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
