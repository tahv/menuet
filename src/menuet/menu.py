from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field
from typing_extensions import Self

from menuet.utils import to_icon_converter, to_tuple_converter

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable


@define(frozen=True, kw_only=True)
class Menu:
    """Menu node definition."""

    label: str = field()
    """Display name."""

    menu: tuple[str, ...] = field(default=(), converter=to_tuple_converter)
    """Menu labels hierarchy.

    The root menu is represented by an empty tuple `()`.
    """

    group: str | None = field(default=None)
    """A group under `menu`.

    Items under the same `menu` can be grouped together.
    Groups are represented by menu separators.
    """

    icon: Traversable | None = field(default=None, converter=to_icon_converter)
    """Path to an icon.

    Icons are displayed alongside the `label`, if supported by the menu builder.
    """

    desc: str | None = field(default=None)
    """Short description.

    Displayed as a menu tooltip.
    """

    @classmethod
    def deserialize(cls, config: dict[str, Any]) -> Self:
        """Deserialize `config` into a new instance."""
        return cls(
            label=config["label"],
            menu=config.get("menu", ()),
            group=config.get("group"),
            icon=config.get("icon"),
            desc=config.get("desc"),
        )

    def is_configured(self) -> bool:
        """Whether this menu has any configuration beside `menu` and `label`."""
        return self.icon is not None or self.group is not None or self.desc is not None
