---
icon: lucide/cooking-pot
---

# Recipes

## Execute actions programmatically

Access any [Action][menuet.Action] in a [Model][menuet.Model] with
[`Model.get_action`][menuet.Model.get_action].

```python { .copy }
import menuet

model = menuet.Model()
menuet.deserialize(
    {
        "action": [{
            "id": "hello-world",
            "cb": "print('Hello World !')",
        }],
    },
    model
)

model.get_action("hello-world").cb()
```

/// html | div.result

```text
Hello World
```

///

## Root keys

The [`load`][menuet.load]
and [`loads`][menuet.loads] functions accepts a `root_keys` argument
which can be used to parse a menu configuration from a sub-table.

```python { .copy }
from textwrap import dedent

import menuet

model = menuet.Model()
menuet.loads(
    dedent("""\
    [[path.to.my-menu.action]]
    id = "print-version"
    label = "Print Version"
    cb = "from importlib.metadata import version; print(version('myapp'))"
    """),
    model,
    root_keys=("path", "to", "my-menu"),
)
```

### Menu in `pyproject.toml`

Loading menu from a sub-table can be used to define a menu in a
`pyproject.toml`.

```toml  { title="pyproject.toml", .copy }
[project]
name = "myapp"
verion = "1.0.0"

[[tool.myapp.my-menu.action]]
id = "hello-world"
label = "Print Hello"
cb = "print('Hello World !')"
```

```python { .copy }
from pathlib import Path

import menuet

model = menuet.Model()
menuet.loads(
    Path("pyproject.toml").read_text(),
    model,
    root_keys=("tool", "myapp", "my-menu"),
)

model.get_action("hello-world").cb()
```

/// html | div.result

```text
Hello World
```

///

### Multiple menus in the same file

Sub-table may be used to define multiple menus in the same file.

```toml { title="menu.toml", .copy }
[[foo.action]]
id = "print-foo"
label = "Print Hello Foo"
menu = ["Foo Menu"]
cb = "print('Hello from foo')"

[[bar.action]]
id = "print-bar"
label = "Print Hello Bar"
menu = ["Bar Menu"]
cb = "print('Hello from bar')"
```

//// tab | Loading **foo** menu

```python { .copy }
from pathlib import Path

import menuet
from menuet.builders.text import TextMenuBuilder

model = menuet.Model()
menuet.loads(Path("menu.toml").read_text(), model, root_keys=("foo",))

print(TextMenuBuilder(model, root_menu="Example").build())
```

/// html | div.result

```text
Example
└── Foo Menu
    └── Print Hello Foo
```

///

////

//// tab | Loading **bar** menu

```python { .copy }
from pathlib import Path

import menuet
from menuet.builders.text import TextMenuBuilder

model = menuet.Model()
menuet.loads(Path("menu.toml").read_text(), model, root_keys=("bar",))

print(TextMenuBuilder(model, root_menu="Example").build())
```

/// html | div.result

```text
Example
└── Bar Menu
    └── Print Hello Bar
```

///

////

## Load multiple files in a Model

```python { .copy }
from pathlib import Path

import menuet
from menuet.builders.text import TextMenuBuilder

model = menuet.Model()
loads(Path("menu.toml").read_text(), model)
loads(Path("other-menu.toml").read_text(), model)
```

## Build model from code

```python { .copy }
from functools import partial
from importlib.metadata import version
from pathlib import Path

import menuet

model = menuet.Model()
model.add_action(
    menuet.Action(
        id="hello-world",
        label="Hello World",
        cb="print('Hello World !')",
    ),
)
model.add_action(
    menuet.Action(
        id="myapp-version",
        label=f"myapp, v{version('myapp')}",
        cb=partial(version, "myapp"),
        menu=("Version",)
    ),
)
model.add_menu(
    menuet.Menu(
        label="Version",
        icon=Path(__file__).parent / "icon.svg",
    ),
)
```

## Build model from Entry Points

In this example, the `myapp` packages build a menu that's populated by plugins,
discovered through
[entry points](https://packaging.python.org/en/latest/specifications/entry-points/).

The `main` function initialize the [Model][menuet.Model]
and lookup the `myapp.menu` entry point group to discover its
[Actions][menuet.Action].

```python { title="myapp/__main__.py" hl_lines="16 28" .copy }
from __future__ import annotations

import logging
from importlib.metadata import entry_points

from PySide6 import QtWidgets

import menuet
from menuet.builders.qt import QMenuBuilder

logger = logging.getLogger("myapp")


def main() -> None:
    model = menuet.Model()
    _load_entry_points(model, "myapp.menu")

    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()
    builder = QMenuBuilder(model, root_menu="My App")
    window.menuBar().addMenu(builder.build())
    window.show()

    app.exec()


def _load_entry_points(model: menuet.Model, group: str) -> None:
    for ep in entry_points(group=group):
        try:
            func = ep.load()
        except Exception:
            logger.exception("Failed to load entry point: %s", ep)
            continue

        try:
            actions = func()
        except Exception:
            logger.exception("Failed to call entry point: %s", ep)
            continue

        if not isinstance(actions, list):
            logger.error("Expected 'list', found %s: %s", type(actions), ep)
            continue

        for item in actions:
            if isinstance(item, menuet.Menu):
                model.add_menu(item)
            elif isinstance(item, menuet.Action):
                model.add_action(item)
            else:
                logger.error(
                    "Expected 'Action' or 'Menu' type, found %s: %s",
                    type(item),
                    ep,
                )


if __name__ == "__main__":
    main()
```

The plugin `myplugin` make its actions available to `myapp` by defining it an
`myapp.menu` entry point in its`pyproject.toml` file.

```toml { title="pyproject.toml" hl_lines="5-6" .copy }
[project]
name = "myplugin"
verion = "1.0.0"

[project.entry-points."myapp.menu"]
myplugin = "myplugin.actions:actions"
```

The `actions` hook function returns a list of [Actions][menuet.Action]
and [Menus][menuet.Menu] to add to `myapp` menu.

```python { title="myplugin/actions.py" hl_lines="3" .copy }
import menuet

def actions() -> list[menuet.Menu | menuet.Action]:
    return [
        menuet.Action(
            id="hello-world",
            label="Hello World",
            cb="print('Hello World !')",
        ),
        menuet.Action(
            id="open-gui",
            label="Open GUI",
            menu=("Sub Menu",),
            cb=open_dialog,
        ),
    ]

def open_dialog() -> None:
    from PySide6 import QtWidgets

    QtWidgets.QMessageBox.information(None, "Demo", "Example Dialog")
```
