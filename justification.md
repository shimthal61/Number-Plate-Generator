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
