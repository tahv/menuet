from functools import partial
from textwrap import dedent

from menuet.builders.maya import MayaMenuBuilder
from menuet.demo import demo_model


def action_script(action: str, /, model: str) -> str:
    return dedent(f"""\
    from importlib.metadata import EntryPoint
    model_loader = EntryPoint(name="", group="", value='{model}').load()
    model = model_loader()
    model.get_action('{action}').cb()
    """)


def secondary_script(action: str, /, model: str, extra: str) -> str:
    return dedent(f"""\
    from importlib.metadata import EntryPoint
    model_loader = EntryPoint(name="", group="", value='{model}').load()
    model = model_loader()
    action = model.get_action('{action}').extra.get('{extra}')
    if action is not None:
        model.get_action(action).cb()
    """)


model = demo_model()
builder = MayaMenuBuilder(
    model,
    root_menu="Demo",
    parent="MayaWindow",
    to_drag_menu_command=partial(
        action_script,
        model="menuet.demo:demo_model",
    ),
    to_drag_double_click_command=partial(
        secondary_script,
        model="menuet.demo:demo_model",
        extra="secondary-action",
    ),
)
builder.build()
