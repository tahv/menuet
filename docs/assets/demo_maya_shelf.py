from collections.abc import Callable

from menuet.builders.maya import MayaMenuBuilder
from menuet.demo import demo_model


def to_drag_menu_command_factory(model: str) -> Callable[[str], str]:
    """Generate `to_drag_menu_command` argument from a `Model` reference."""

    def inner(action: str) -> str:
        from textwrap import dedent

        return dedent(f"""\
        from importlib.metadata import EntryPoint
        model_loader = EntryPoint(name="", group="", value='{model}').load()
        model = model_loader()
        model.get_action('{action}').cb()
        """)

    return inner


model = demo_model()
builder = MayaMenuBuilder(
    model,
    root_menu="Demo",
    parent="MayaWindow",
    to_drag_menu_command=to_drag_menu_command_factory("menuet.demo:demo_model"),
)
builder.build()
