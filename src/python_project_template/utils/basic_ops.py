from __future__ import annotations


class BasicOperations:
    """A tiny example class providing a few basic numeric operations.

    This is intentionally small and dependency-free so you can copy it into
    other projects as a starting point. Methods accept ints/floats and lists
    of numbers where it makes sense.

    Usage:
        calc = BasicOperations()
        calc.add(1, 2)            # -> 3
        calc.mean([1, 2, 3])      # -> 2.0
    """

    def add(self, a: float, b: float) -> float:
        """Return the sum of two numbers."""
        return float(a) + float(b)

    def subtract(self, a: float, b: float) -> float:
        """Return a - b."""
        return float(a) - float(b)

    def multiply(self, a: float, b: float) -> float:
        """Return the product of two numbers."""
        return float(a) * float(b)

    def divide(self, a: float, b: float) -> float:
        """Return the result of a / b.

        Raises:
            ZeroDivisionError: if b == 0
        """
        b_f = float(b)
        if b_f == 0.0:
            raise ZeroDivisionError("Division by zero")
        return float(a) / b_f

    def mean(self, values: list[float]) -> float:
        """Return the arithmetic mean of a sequence of numbers.

        Raises:
            ValueError: if `values` is empty.
        """
        vals: list[float] = [float(v) for v in values]
        if not vals:
            raise ValueError("mean() requires at least one value")
        return sum(vals) / len(vals)

    def power(self, a: float, exponent: float) -> float:
        """Return a raised to the given exponent."""
        return float(a) ** float(exponent)
