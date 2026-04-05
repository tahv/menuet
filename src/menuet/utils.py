from __future__ import annotations

import importlib.resources
import logging
import webbrowser
from collections.abc import Iterable
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable
    from importlib.abc import Traversable

_T = TypeVar("_T")

logger: Final[logging.Logger] = logging.getLogger("menuet")


def load_entry_point(value: str, /) -> Any:  # noqa: ANN401
    """Create, load, and execute `value` entry point."""
    from importlib.metadata import EntryPoint  # noqa: PLC0415

    func = EntryPoint(name="", group="", value=value).load()
    func()


def load_resource(value: str, /) -> Traversable:
    """Load `value` resource."""
    package, _, file = value.partition(":")
    return importlib.resources.files(package).joinpath(file)


def copy_to_clipboard(value: str, /) -> None:
    """Copy `value` into the clipboard."""
    try:
        import copykitten  # noqa: PLC0415
    except ImportError as exc:
        msg = "Unable to import 'copykitten', install extra 'menuet[copy]'"
        raise RuntimeError(msg) from exc

    copykitten.copy(value)


CB_SCHEMES: dict[str, Callable[[str], Any]] = {
    "exec": exec,
    "ep": load_entry_point,
    "url": webbrowser.open,
    "copy": copy_to_clipboard,
}

ICON_SCHEMES: dict[str, Callable[[str], Traversable]] = {
    "path": Path,
    "res": load_resource,
}


def to_tuple_converter(value: Any) -> tuple[Any, ...]:  # noqa: ANN401
    """Convert `value` into a tuple."""
    if is_iterable(value):
        return tuple(value)
    return (value,)


def is_iterable(obj: Any) -> bool:  # noqa: ANN401
    """Returns `True` if `obj` is Iterable."""
    if isinstance(obj, list | tuple | set | dict):
        return True
    return not isinstance(obj, str) and isinstance(obj, Iterable)


def passthrough() -> None:
    """Callable that does nothing."""


def to_cb_converter(value: Any) -> Callable[[], Any]:  # noqa: ANN401
    """Convert `value` to a Callable that takes no argument."""
    if callable(value):
        return value  # type: ignore[no-any-return]

    if isinstance(value, str):
        scheme, sep, rest = value.partition(":")
        if not sep:
            return partial(exec, scheme)
        return partial(CB_SCHEMES.get(scheme, exec), rest)

    raise TypeError(type(value))


def to_icon_converter(value: Any) -> Traversable | None:  # noqa: ANN401
    """Convert `value` to icon path."""
    if value is None:
        return value

    if isinstance(value, Path):
        return value

    if isinstance(value, str):
        scheme, sep, rest = value.partition(":")
        if not sep:
            return Path(scheme)

        converter = ICON_SCHEMES[scheme]

        try:
            return converter(rest)
        except Exception:
            logger.exception("Failed to parse icon '%s'", value)
            return None

    raise TypeError(type(value))


def skip_n(iterable: Iterable[_T], *, n: int = 1) -> Iterable[_T]:
    """Drops `n` elements from the `iterable`."""
    it = iterable.__iter__()
    for _ in range(n):
        next(it)
    yield from it
