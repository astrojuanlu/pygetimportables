"""Get the top-level packages of a Python project."""

import csv
import pathlib
import tempfile
import tomllib
import zipfile

from build import ProjectBuilder
from build.env import DefaultIsolatedEnv
from pyproject_hooks import quiet_subprocess_runner
from validate_pyproject import api, errors


def _simple_build_wheel(source_dir, out_dir, *, build_config_settings=None):
    """Silently build wheel using build package."""
    with DefaultIsolatedEnv() as env:
        builder = ProjectBuilder.from_isolated_env(
            env, source_dir, runner=quiet_subprocess_runner
        )
        env.install(builder.build_system_requires)
        env.install(builder.get_requires_for_build("wheel", build_config_settings))
        path_built_wheel = builder.build("wheel", out_dir, build_config_settings)
    return path_built_wheel


def get_packages_from_wheel(wheel_path: str | pathlib.Path):
    """Get the top-level packages of a Python project from a wheel file."""
    with zipfile.ZipFile(wheel_path, "r") as zf:
        record_fnames = [
            fname for fname in zf.namelist() if fname.endswith(".dist-info/RECORD")
        ]
        record_fname = min(record_fnames, key=len)
        with zf.open(record_fname) as fh:
            record_content = fh.read().decode()

    record_files = [
        pathlib.Path(row[0]) for row in csv.reader(record_content.splitlines())
    ]

    # A directory is a top-level package if it contains a top-level __init__.py file
    top_packages = {
        record_file.parts[0]
        for record_file in record_files
        if len(record_file.parts) > 1 and record_file.parts[1] == "__init__.py"
    }

    return list(top_packages)


def get_packages(source_dir, *, build_config_settings=None):
    """Get the top-level packages of a Python project."""
    pyproject_toml_path = pathlib.Path(source_dir) / "pyproject.toml"
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
        top_packages = get_packages_from_wheel(wheel_path)

    return list(top_packages)
