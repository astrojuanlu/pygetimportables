from pathlib import Path

import pytest
from pygetimportables import get_top_importables_from_wheel

here = Path(__file__).parent


@pytest.mark.parametrize(
    "wheel_path, expected_importables",
    [
        (
            here / "cases" / "single_script-0.1.0-py2.py3-none-any.whl",
            {"single_script"},
        ),
    ],
)
def test_get_packages_from_wheel(wheel_path, expected_importables):
    packages = get_top_importables_from_wheel(wheel_path)
    assert packages == expected_importables
