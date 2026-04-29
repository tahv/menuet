# ruff:  noqa: PLC0415
from __future__ import annotations

import atexit
import importlib
import logging
import warnings
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

collect_ignore: list[str] = []
"""Exclude test directories or modules with Unix shell-style wildcards."""

logger = logging.getLogger("pytest-menuet")


@cache
def is_in_maya() -> bool:
    """Whether current interpreter is Maya."""
    try:
        importlib.import_module("maya.cmds")
    except ImportError:
        return False
    return True


@cache
def is_in_blender() -> bool:
    """Whether current interpreter is Blender."""
    try:
        m = importlib.import_module("bpy")
    except ImportError:
        return False

    # 'fake-bpy-module' is a stub-only package; it's named 'bpy', not 'bpy-stubs'
    # and can be imported. Next release will fix this:
    # https://github.com/nutti/fake-bpy-module/issues/433
    return not (m.__file__ is None or (Path(m.__file__).parent / "py.typed").exists())


@cache
def is_in_unreal() -> bool:
    """Whether current interpreter is Unreal."""
    try:
        importlib.import_module("unreal")
    except ImportError:
        return False
    return True


@cache
def is_in_mayapy() -> bool:
    """Whether current interpreter is mayapy."""
    try:
        cmds = importlib.import_module("maya.cmds")
    except ImportError:
        return False
    return "about" not in cmds.__dict__


class MarkConfig(NamedTuple):
    """Mark configuration."""

    desc: str
    reason: str
    check: Callable[[], bool]
    paths: tuple[str, ...]


MARKS: dict[str, MarkConfig] = {
    "requires_maya": MarkConfig(
        desc="Tests intended for Autodesk Maya",
        reason="Not running a Maya or Mayapy interpreter",
        check=is_in_maya,
        paths=(),
    ),
    "requires_maya_gui": MarkConfig(
        desc="Tests intended for Autodesk Maya that can only run with GUI",
        reason="Not running a Maya interpreter in GUI mode",
        check=lambda: is_in_maya() and not is_in_mayapy(),
        paths=(),
    ),
    "requires_blender": MarkConfig(
        desc="Tests intended for Blender",
        reason="Not running a Blender interpreter",
        check=is_in_blender,
        paths=(
            "src/menuet/builders/blender.py",
            "tests/test_builder_blender.py",
        ),
    ),
    "requires_unreal": MarkConfig(
        desc="Tests intended for Unreal",
        reason="Not running a Unreal interpreter",
        check=is_in_unreal,
        paths=(),
    ),
}


def pytest_collectstart(collector: pytest.Collector) -> None:
    """Collector starts collecting."""
    for mark_config in MARKS.values():
        if mark_config.check():
            continue
        for path in mark_config.paths:
            warnings.warn(
                f"Excluding {path!r}: {mark_config.reason!r}",
                pytest.PytestCollectionWarning,
                stacklevel=1,
            )
            collect_ignore.append(path)


def pytest_configure(config: pytest.Config) -> None:
    """Perform initial configuration."""
    for mark_name, mark_config in MARKS.items():
        config.addinivalue_line("markers", f"{mark_name}: {mark_config.reason}")


def pytest_runtest_call(item: pytest.Item) -> None:
    """Called to run the test item."""
    for mark in item.iter_markers():
        if (mark_config := MARKS.get(mark.name)) and not mark_config.check():
            pytest.skip(mark_config.reason)


@pytest.fixture(scope="session", autouse=True)
def initialize_mayapy() -> None:
    """Initialize Maya standalone."""
    if not is_in_mayapy():
        return

    import maya.standalone

    maya.standalone.initialize()
    atexit.register(maya.standalone.uninitialize)
