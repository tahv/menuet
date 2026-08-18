from __future__ import annotations

from unittest.mock import Mock

import pytest

from menuet.utils import complete


@pytest.mark.parametrize(
    ("args", "kwargs"),
    [
        pytest.param(("foo", "bar"), {}, id="args"),
        pytest.param((), {"foo": "bar", "baz": 1}, id="kwargs"),
        pytest.param(("foo", "bar"), {"foo": "bar", "baz": 1}, id="args-kwargs"),
    ],
)
def test_complete_suppress_arguments(
    args: tuple[object, ...],
    kwargs: dict[str, object],
) -> None:
    mocked = Mock()
    complete(mocked)(*args, **kwargs)
    mocked.assert_called_once_with()
