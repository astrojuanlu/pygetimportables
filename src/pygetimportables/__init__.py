"""Get the top-level importable names of a Python project."""
# The good parts come from https://gist.github.com/pradyunsg/22ca089b48ca55d75ca843a5946b2691
# Licensed under the MIT license.
#
# Copyright (c) 2022 Pradyun Gedam <mail@pradyunsg.me>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import tempfile
import typing as t
import zipfile
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore
from build import ConfigSettingsType, ProjectBuilder
from build.env import DefaultIsolatedEnv
from installer.sources import WheelFile, WheelSource
from installer.utils import parse_metadata_file
from pyproject_hooks import quiet_subprocess_runner
from validate_pyproject import api, errors


def _simple_build_wheel(
    source_dir: str | Path,
    out_dir: str | Path,
    *,
    build_config_settings: ConfigSettingsType | None = None,
) -> Path:
    """Silently build wheel using build package."""
    with DefaultIsolatedEnv() as env:
        builder = ProjectBuilder.from_isolated_env(
            env, source_dir, runner=quiet_subprocess_runner
        )
        env.install(builder.build_system_requires)
        env.install(builder.get_requires_for_build("wheel", build_config_settings))
        path_built_wheel = builder.build("wheel", out_dir, build_config_settings)
    return Path(path_built_wheel)


def _find_importable_components_from_wheel_content_listing(
    filepaths: t.Iterable[str], *, dist_info_dir: str, data_dir: str
) -> t.Iterable[tuple[str, ...]]:
    purelib_str = f"{data_dir}/purelib/"
    platlib_str = f"{data_dir}/platlib/"
    for path in filepaths:
        if path.startswith(dist_info_dir):
            # Nothing in dist-info is importable.
            continue

        if path.startswith((platlib_str, purelib_str)):
            # Remove the prefix from purelib and platlib files.
            name = path[len(platlib_str) :]
        elif path.startswith(data_dir):
            # Nothing else in data is importable.
            continue
        else:
            # Top level files end up in an importable location.
            name = path

        if name.endswith(".py"):
            yield tuple(name[: -len(".py")].split("/"))


def _determine_major_import_names(
    importable_components: t.Iterable[tuple[str, ...]]
) -> set[str]:
    return {components[0] for components in importable_components}


def _get_importable_components_from_wheel(
    wheel: WheelSource
) -> t.Iterable[tuple[str, ...]]:
    metadata = parse_metadata_file(wheel.read_dist_info("WHEEL"))
    if not (metadata["Wheel-Version"] and metadata["Wheel-Version"].startswith("1.")):
        raise NotImplementedError("Only supports wheel 1.x")

    filepaths: t.Iterable[str] = (
        record_elements[0] for record_elements, _, _ in wheel.get_contents()
    )
    importable_components = _find_importable_components_from_wheel_content_listing(
        filepaths, dist_info_dir=wheel.dist_info_dir, data_dir=wheel.data_dir
    )

    return importable_components


def get_top_importables_from_wheel(wheel_path: str | Path) -> set[str]:
    """Get the top-level importable names of a Python project from a wheel file."""
    with zipfile.ZipFile(wheel_path, "r") as zf:
        wheel_file = WheelFile(zf)
        importable_components = _get_importable_components_from_wheel(wheel_file)
        top_importables = _determine_major_import_names(importable_components)

    return top_importables


def get_top_importables(
    source_dir: str | Path, *, build_config_settings: ConfigSettingsType | None = None
) -> set[str]:
    """Get the top-level importable names of a Python source tree."""
    pyproject_toml_path = Path(source_dir) / "pyproject.toml"
    if not pyproject_toml_path.is_file():
        raise ValueError(
            "pyproject.toml is missing from source directory, "
            "either this directory is not a Python package "
            "or it uses setup.py (which is not supported)"
        )

    with open(pyproject_toml_path, "rb") as fh:
        pyproject_toml = tomllib.load(fh)

    if "project" not in pyproject_toml:
        raise ValueError("pyproject.toml is missing PEP 621 [project] section")

    validator = api.Validator()
    try:
        validator(pyproject_toml)
    except errors.ValidationError as exc:
        raise ValueError("pyproject.toml is invalid") from exc

    with tempfile.TemporaryDirectory() as outdir:
        wheel_path = _simple_build_wheel(
            source_dir, outdir, build_config_settings=build_config_settings
        )
        top_importables = get_top_importables_from_wheel(wheel_path)

    return top_importables
