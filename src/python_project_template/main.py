"""A tiny manual test script for the package interfaces.
Run this module to perform simple, human-readable checks of the project's
public interfaces (keeps things minimal and dependency-free).

Usage:
    python -m python_project_template.main
or:
    python src/python_project_template/main.py
"""


from python_project_template.utils.basic_ops import BasicOperations


def run_manual_tests() -> None:
    """Run a few simple sanity checks and print results."""
    calc = BasicOperations()
    print("Running manual checks for BasicOperations...")
    print("add(1, 2) ->", calc.add(1, 2))
    print("subtract(5, 3) ->", calc.subtract(5, 3))
    print("multiply(2, 3) ->", calc.multiply(2, 3))
    print("divide(7, 2) ->", calc.divide(7, 2))

    # Show handled error conditions
    try:
        calc.divide(1, 0)
    except Exception as exc:  # intentional: show the raised error
        print("divide(1, 0) raised:", repr(exc))

    try:
        calc.mean([])
    except Exception as exc:
        print("mean([]) raised:", repr(exc))

    print("power(2, 3) ->", calc.power(2, 3))


def main() -> None:
    """Entry point for the manual tests."""
    run_manual_tests()


if __name__ == "__main__":
    main()
