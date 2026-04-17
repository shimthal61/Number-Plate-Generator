# Decision Justifications

This document explains the key decisions made when building the Number Plate Generator — written to be understandable without a software development background.

---

## Project Structure

### Why a `src/` folder?

The source code lives inside a `src/` folder rather than directly in the project root. This prevents Python from accidentally picking up the code in an unintended way when running tests. Think of it as keeping the finished product in a clearly labelled box, separate from the workbench.

- **Source:** Python Packaging Authority (PyPA) — [src layout recommendation](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) (2024)
- **Source:** Hynek Schlawack — [Testing & Packaging](https://hynek.me/articles/testing-packaging/) (2022, still canonical)

### Why `pyproject.toml` instead of `requirements.txt` or `setup.py`?

`pyproject.toml` is a single configuration file that replaces several older files (`setup.py`, `setup.cfg`, `requirements.txt`). It is the current official standard for Python projects, adopted through PEPs 517 and 621. Having one file means less clutter and a single place to look for project settings.

- **Source:** [PEP 621](https://peps.python.org/pep-0621/) — standardises `pyproject.toml`
- **Source:** [packaging.python.org — Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) (2024)

### Why a separate `tests/` folder?

Tests live outside the source code in their own folder. This keeps production code and test code cleanly separated — the tests are there to verify the program works, not to be part of the program itself.

- **Source:** [pytest — Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) (2024)

### Why `conftest.py`?

`conftest.py` is a special file that pytest (the testing tool) looks for automatically. It is used to hold shared test setup — for example, creating a fresh generator object that multiple tests can use. Think of it as a preparation room that gets the test environment ready before each test runs.

---

## Class Interface Design

### Why a class rather than a simple function?

The specification requires that **no two plates are ever repeated**. This means the program needs to remember which plates it has already created. A class is the natural way to hold that memory — the list of used plates belongs to the object and lives for as long as that object exists. A standalone function has no memory between calls; a class does.

### Why one public method (`generate`) rather than many?

The only thing a caller ever needs to do is say: *"give me a plate for this tag and date."* Everything else — working out the age number, picking random letters, checking for duplicates — happens invisibly inside the class. Keeping the public interface as small as possible makes the program simpler to use and harder to misuse.

### Why accept `date` as a string (`dd/mm/yyyy`) rather than a date object?

The specification defines the input as a string in the format `dd/mm/yyyy`. Accepting it in that same format keeps the interface honest to the spec, and the class handles the conversion internally. This means the caller does not need to know anything about Python's date types — they just pass in what the spec describes.

---

## Test Design

### Why write tests before the implementation (TDD)?

Test-Driven Development means writing a failing test first, then writing just enough code to make it pass. This forces clarity on what the program should do before worrying about how to do it. It also ensures every piece of logic exists because a test demanded it — not as a guess about what might be needed later.

### Why are tests grouped into classes by concern?

Each test class answers a single question: "does this behaviour work?" The four groups are *format*, *age identifier*, *random letters*, and *uniqueness*. Grouping this way means that when a test fails, the class name alone tells you which part of the program to look at — without reading the test itself.

### Why does the `conftest.py` fixture create a fresh object for every test?

The generator remembers which plates it has already produced. If tests shared the same object, a plate generated in one test could affect the results of another. By giving each test its own fresh generator, the tests are completely independent of each other — a failure in one cannot be caused by a side-effect from another.

### Why is there a specific test for January and February?

This is the most likely mistake in the implementation. January and February feel like they belong to the new calendar year, but the spec says they belong to the *previous* year's second-half window (e.g. February 2003 → age identifier 52, not 53). Without a dedicated test, this bug could easily go undetected.

### Why do the boundary tests check March 1st, August 31st, and September 1st specifically?

These are the exact days where the rule changes. Testing the first and last day of a window (rather than just a day in the middle) catches off-by-one errors — a common source of bugs when code uses `>` instead of `>=`, for example.

### Why does the restricted-letters test generate 50 plates?

A single plate is a weak check — there's a good chance a random plate simply doesn't contain I, Q, or Z by luck. Generating 50 plates from the same prefix samples a wide range of suffixes, making it very unlikely that a bug would go undetected. 50 is chosen as a balance: enough to be meaningful, few enough to run instantly.

### Why does the uniqueness test use `len(list) == len(set)`?

A `set` in Python cannot contain duplicates. If the list of 100 plates contains any repeated plate, the set will be shorter than the list. This is the simplest possible way to detect duplicates — one line, no loops.

---

## Implementation

### Why use `itertools.product` to build the suffix pool?

`itertools.product(VALID_LETTERS, repeat=3)` generates every possible 3-letter combination from the valid alphabet (23 letters → 12,167 combinations). Building this list once at construction time, then shuffling it, means the generator has a ready-made random order to draw from. This is more efficient than picking a random letter on every call and hoping it hasn't been used before.

### Why shuffle the pool once at startup rather than picking randomly each time?

If we picked a random suffix on every call and checked whether it had been used, we would slow down significantly as the pool filled up (imagine trying to find the last unused plate out of 12,167). Shuffling once at the start means we always just take the next item in the list — no searching required.

### Why track a separate draw index per prefix rather than one global used-plates set?

Each prefix (e.g. "MV10") is independent — its suffix pool is never shared with another prefix. Storing one integer index per prefix (e.g. `"MV10" → 42`) is both simpler and faster than maintaining a growing set of full plate strings to check against.

### Why use `frozenset` for `RESTRICTED_LETTERS`?

A `frozenset` is an immutable set — it cannot be accidentally changed after it is created. Since the restricted letters never change, making the collection immutable signals that clearly, and still provides O(1) membership checks when filtering the alphabet.

### Why split the date string on `"/"` rather than using a date library?

The input format is fixed (`dd/mm/yyyy`) and only the month and year are needed. Splitting on `"/"` and reading the second and third values is three lines of code and has no dependencies. Importing a date library for this would be adding complexity where none is needed.
