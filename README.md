# pygetpackages

[![Documentation Status](https://readthedocs.org/projects/pygetpackages/badge/?version=latest)](https://pygetpackages.readthedocs.io/en/latest/?badge=latest)
[![Code style: ruff-format](https://img.shields.io/badge/code%20style-ruff_format-6340ac.svg)](https://github.com/astral-sh/ruff)
[![PyPI](https://img.shields.io/pypi/v/pygetpackages)](https://pypi.org/project/pygetpackages)

Python functions to get packages from a source tree and an already built wheel.

See https://discuss.python.org/t/script-to-get-top-level-packages-from-source-tree/40232?u=astrojuanlu

## Installation

To install, run

```
(.venv) $ pip install pygetpackages
```

## Usage

To get the packages directly from a source tree:

```
>>> from pygetpackages import get_packages
>>> get_packages(".")  # Wait a few seconds, requires working `pip install`
{'pygetpackages'}
```

To get packages from an already built wheel:

```
(.venv) $ python -m build
...
(.venv) $ python -q
>>> from pygetpackages import get_packages_from_wheel
>>> get_packages_from_wheel("dist/pygetpackages-0.1.0+d20231204-py3-none-any.whl")  # Fast
{'pygetpackages'}
```

## Development

To run style checks:

```
(.venv) $ pip install pre-commit
(.venv) $ pre-commit -a
```
