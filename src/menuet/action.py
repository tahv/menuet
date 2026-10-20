from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any

from attr.validators import optional
from attrs import define
from attrs import field
from attrs.validators import deep_iterable
from attrs.validators import instance_of
from attrs.validators import matches_re
from typing_extensions import Self

from menuet.utils import extra_factory
from menuet.utils import passthrough
from menuet.utils import to_cb_converter
from menuet.utils import to_icon_converter
from menuet.utils import to_tuple_converter

if TYPE_CHECKING:
    import sys

    if sys.version_info < (3, 11):
        from importlib.abc import Traversable
    else:
        from importlib.resources.abc import Traversable


@define(frozen=True, kw_only=True, slots=True)
class Action:
    """Runtime action definition."""

    id: str = field(
        validator=matches_re(r"^[a-z](?:[a-z-]*[a-z])?$"),
    )
    """Action identifier.

    Identifier must abide by these rules:

    - Must be **unique** in its [`Model`][menuet.Model]
    - The **first** and **last** characters must be ascii lowercase `[a-z]`
    - Other characters must be ascii lowercase or dash `[a-z-]`
    """

    cb: Callable[[], Any] = field(
        converter=to_cb_converter,
        default=passthrough,
        eq=False,
    )
    """Callback to execute when action is requested."""

    menu: tuple[str, ...] = field(
        default=(),
        converter=to_tuple_converter,  # TODO(tga): too permissive
        validator=deep_iterable(
            iterable_validator=instance_of(tuple),
            member_validator=instance_of(str),
        ),
    )
    """Menu labels hierarchy.

    The root menu is represented by an empty tuple `()`.
    """

    label: str | None = field(
        default=None,
        validator=optional(instance_of(str)),
    )
    """Display name."""

    group: str | None = field(
        default=None,
        validator=optional(instance_of(str)),
    )
    """A group under `menu`.

    Items under the same `menu` can be grouped together.
    Groups are represented by separators.
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
            id=config["id"],
            cb=config.get("cb", passthrough),
            menu=config.get("menu", ()),
            label=config.get("label"),
            group=config.get("group"),
            icon=config.get("icon"),
            desc=config.get("desc"),
            extra=config.get("extra", {}),
        )
