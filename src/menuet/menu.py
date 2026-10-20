from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from attrs import define, field
from attrs.validators import deep_iterable, instance_of, optional
from typing_extensions import Self

from menuet.utils import extra_factory, to_icon_converter, to_tuple_converter

if TYPE_CHECKING:
    import sys

    if sys.version_info < (3, 11):
        from importlib.abc import Traversable
    else:
        from importlib.resources.abc import Traversable


@define(frozen=True, kw_only=True, slots=True)
class Menu:
    """Menu node definition."""

    label: str = field(
        validator=instance_of(str),
    )
    """Display name."""

    menu: tuple[str, ...] = field(
        default=(),
        converter=to_tuple_converter,  # TODO(tga): too permissive
        validator=deep_iterable(member_validator=instance_of(str)),
    )
    """Menu labels hierarchy.

    The root menu is represented by an empty tuple `()`.
    """

    group: str | None = field(
        default=None,
        validator=optional(instance_of(str)),
    )
    """A group under `menu`.

    Items under the same `menu` can be grouped together.
    Groups are represented by menu separators.
    """

    icon: Traversable | None = field(
        default=None,
        converter=to_icon_converter,
    )
    """Path to an icon.

    Icons are displayed alongside the `label`, if supported by the menu builder.
    """

    desc: str | None = field(
        default=None,
        validator=optional(instance_of(str)),
    )
    """Short description.

    Displayed as a menu tooltip.
    """

    extra: Mapping[str, object] = field(
        factory=extra_factory,
        validator=instance_of(Mapping),  # type: ignore[type-abstract]
        eq=False,
        hash=False,
        repr=False,
    )
    """Extra user data."""

    @classmethod
    def deserialize(cls, config: dict[str, Any]) -> Self:
        """Deserialize `config` into a new instance."""
        return cls(
            label=config["label"],
            menu=config.get("menu", ()),
            group=config.get("group"),
            icon=config.get("icon"),
            desc=config.get("desc"),
            extra=config.get("extra", {}),
        )

    def is_configured(self) -> bool:
        """Whether this menu has any configuration beside `menu` and `label`."""
        return (
            self.icon is not None
            or self.group is not None
            or self.desc is not None
            or bool(self.extra)
        )
