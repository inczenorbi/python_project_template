from python_project_template.utils.basic_ops import BasicOperations
import pytest


def test_add_subtract_multiply():
    c = BasicOperations()
    assert c.add(1, 2) == 3.0
    assert c.subtract(5, 3) == 2.0
    assert c.multiply(2, 3) == 6.0


def test_divide_and_zero():
    c = BasicOperations()
    assert c.divide(7, 2) == 3.5
    with pytest.raises(ZeroDivisionError):
        c.divide(1, 0)


def test_mean_and_power():
    c = BasicOperations()
    assert c.mean([1, 2, 3, 4]) == 2.5
    with pytest.raises(ValueError):
        c.mean([])
    assert c.power(2, 3) == 8.0
