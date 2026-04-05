from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field, validators
from typing_extensions import Self

from menuet.utils import (
    passthrough,
    to_cb_converter,
    to_icon_converter,
    to_tuple_converter,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from importlib.abc import Traversable


ID_PATTERN = r"[a-z](?:[a-z-]*[a-z])?"


@define(frozen=True, kw_only=True)
class Action:
    """Runtime action definition."""

    id: str = field(validator=validators.matches_re(ID_PATTERN))
    """Action identifier.

    Identifier must abide by these rules:

    - Must be **unique** in its [`Model`][menuet.Model]
    - The **first** and **last** characters must be ascii lowercase `[a-z]`
    - Other characters must be ascii lowercase or dash `[a-z-]`
    """

    cb: Callable[[], Any] = field(
        converter=to_cb_converter,
        eq=False,
        default=passthrough,
    )
    """Callback to execute when action is requested."""

    enabled: bool = field(default=True)  # TODO(tga): unused
    """Whether the action is enabled."""

    visible: bool = field(default=True)  # TODO(tga): unused
    """Whether the action is visible in the menu."""

    menu: tuple[str, ...] = field(default=(), converter=to_tuple_converter)
    """Menu labels hierarchy.

    The root menu is represented by an empty tuple `()`.
    """

    label: str | None = field(default=None)
    """Display name."""

    group: str | None = field(default=None)
    """A group under `menu`.

    Items under the same `menu` can be grouped together.
    Groups are represented by separators.
    """

    icon: Traversable | None = field(default=None, converter=to_icon_converter)
    """Path to an icon.

    Icons are displayed alongside the `label`, if supported by the menu builder.
    """

    desc: str | None = field(default=None)
    """Short description.

    Displayed as a menu tooltip.
    """

    # TODO(tga): extra: Mapping[str, object]

    @classmethod
    def deserialize(cls, config: dict[str, Any]) -> Self:
        """Deserialize `config` into a new instance."""
        return cls(
            id=config["id"],
            cb=config.get("cb", passthrough),
            enabled=config.get("enabled", True),
            visible=config.get("visible", True),
            menu=config.get("menu", ()),
            label=config.get("label"),
            group=config.get("group"),
            icon=config.get("icon"),
            desc=config.get("desc"),
        )
