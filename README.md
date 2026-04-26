# menuet

[![Source](https://img.shields.io/badge/codeberg-%232185D0?logo=codeberg&logoColor=white)](https://codeberg.org/tahv/menuet)
[![Documentation](https://img.shields.io/badge/documentation-teal)](https://tahv.codeberg.page/menuet/)
[![PyPI](https://img.shields.io/pypi/v/menuet?logo=python&logoColor=white&label=)](https://pypi.org/project/menuet/)
[![Pipeline Status](https://ci.codeberg.org/api/badges/16747/status.svg)](https://ci.codeberg.org/repos/16747)

Menuet (`/mə.nɥɛ/`) is a declarative menu builder for DCC applications.

## Features

- Load menu from a TOML or JSON configuration, from a dict, from entry points,
  or build it programmatically.
- Supports, Blender, 3ds Max, Maya, MotionBuilder and any PySide6 application.
- Declare one or more menus in a dedicated `.toml` file.
- Compose menu from multiple `.toml` files.
- Declare a menu in a `pyproject.toml`.

## Project Information

> [!IMPORTANT]
> Development takes place on Codeberg:
> [codeberg.org/tahv/menuet](https://codeberg.org/tahv/menuet).

- [**Documentation**](https://tahv.codeberg.page/menuet)
- [**PyPI**](https://pypi.org/project/menuet/)
- [**Source Code**](https://codeberg.org/tahv/menuet)
- [**Changelog**](https://codeberg.org/tahv/menuet/src/branch/main/CHANGELOG.md)
- [**Contributing**](https://codeberg.org/tahv/menuet/src/branch/main/CONTRIBUTING.md)
- [**GitHub Mirror**](https://github.com/tahv/menuet)

## Installation

```console
pip install menuet
```

## Usage

Create a menu configuration in [TOML](https://toml.io/) format.

```toml
# menu.toml
[[action]]
id = "print-hello"
label = "Print Hello"
cb = "print('Hello')"
group = "Separator"

[[action]]
id = "open-gui"
label = "Open GUI"
cb = "ep:myapp.gui:open_gui"
menu = ["Foo", "Bar"]
```

Load the above configuration into a `Model` and pass
that model to a Menu Builder to create a menu.

```python
from pathlib import Path
from menuet import Model, loads
from menuet.builders.text import Render, TextMenuBuilder

model = Model()
loads(Path("menu.toml").read_text(), model)

builder = TextMenuBuilder(model, root_menu="Demo", render=Render.UTF8)
print(builder.build())
```

```text
Demo
├── Foo
│   └── Bar
│       └── Open GUI
├── Separator ───
└── Print Hello
```

For more information and examples,
visit the documentation at
[tahv.codeberg.page/menuet](https://tahv.codeberg.page/menuet).

## Contributing

You'd like to use menuet with another application ?
Feel free to [open an issue](https://codeberg.org/tahv/menuet/issues),
or read the
[contribution guidelines](https://codeberg.org/tahv/menuet/src/branch/main/CONTRIBUTING.md)
and open a [pull request](https://codeberg.org/tahv/menuet/pulls).

## Alternatives

- [hannesdelbeke/unimenu](https://github.com/hannesdelbeke/unimenu)

<!--

## Roadmap

- [ ] Tests: menuet.builders.maya.MayaMenuBuilder
- [ ] Builder: maya.cmds.popupMenu (marking menu) MayaMarkingMenuBuilder
- [ ] Builder: 3ds Max Menu System
- [ ] Builder: 3ds Max Dynamic Menu
- [ ] Builder: Unreal
- [ ] Helper function to get QMainWindow or QMenuBar
- [ ] Icon path should be relative to file

-->
