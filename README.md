# pygetimportables

[![Documentation Status](https://readthedocs.org/projects/pygetimportables/badge/?version=latest)](https://pygetimportables.readthedocs.io/en/latest/?badge=latest)
[![Code style: ruff-format](https://img.shields.io/badge/code%20style-ruff_format-6340ac.svg)](https://github.com/astral-sh/ruff)
[![PyPI](https://img.shields.io/pypi/v/pygetimportables)](https://pypi.org/project/pygetimportables)

Python functions to get top-level importable names from a source tree or an already built wheel.

See https://discuss.python.org/t/script-to-get-top-level-packages-from-source-tree/40232?u=astrojuanlu

## Installation

To install, run

```
(.venv) $ pip install pygetimportables
```

## Usage

To get the top-level importable names directly from a source tree:

```
>>> from pygetimportables import get_top_importables
>>> get_top_importables(".")  # Wait a few seconds, requires working `pip install`
{'pygetimportables'}
```

To get the top-level importable names from an already built wheel:

```
(.venv) $ python -m build
...
(.venv) $ python -q
>>> from pygetimportables import get_top_importables_from_wheel
>>> get_top_importables_from_wheel("dist/pygetimportables-0.1.0+d20231204-py3-none-any.whl")  # Fast
{'pygetimportables'}
```

## Development

To run style checks:

```
(.venv) $ pip install pre-commit
(.venv) $ pre-commit -a
```
