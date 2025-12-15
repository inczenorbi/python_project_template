"""Compatibility shim package.

This top-level package exists so tests and tools that run from the
repository root can import ``python_project_template`` without setting
PYTHONPATH or installing the package. It simply extends the package
search path to include the implementation under ``src/python_project_template``.

This is intentionally minimal and safe: it only mutates ``__path__`` so the
existing source tree under ``src/`` is used.
"""
import os

# Compute the absolute path to the package implementation under src/
_HERE = os.path.dirname(__file__)
_SRC_PKG = os.path.abspath(os.path.join(_HERE, "..", "src", "python_project_template"))

if os.path.isdir(_SRC_PKG):
    # Prepend so the src implementation takes precedence over any other
    # installed packages with the same name.
    __path__.insert(0, _SRC_PKG)
