<div align="center">
  <h1>menuet</h1>
  <p>
    <a href="https://pypi.org/project/menuet">
      <img alt="PyPI" src="https://img.shields.io/pypi/v/menuet?style=for-the-badge&logo=python&logoColor=white">
    </a>
    <a href="https://www.buymeacoffee.com/tgambier">
      <img alt="Buy Me a Coffee" style="height: 28px;" height="28" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png">
    </a>
  </p>
  <p><b>Declarative menu builder for DCC applications</b></p>
  <p>
    <a href="https://tahv.gitlab.io/menuet/">Documentation</a>
    • <a href="https://pypi.org/project/menuet">PyPI</a>
    • <a href="https://gitlab.com/tahv/menuet">GitLab</a>
    • <a href="https://github.com/tahv/menuet">GitHub</a>
    • <a href="https://gitlab.com/tahv/menuet/-/blob/main/CHANGELOG.md">Changelog</a>
    • <a href="https://gitlab.com/tahv/menuet/-/blob/main/CONTRIBUTING.md">Contributing</a>
  </p>
</div>

---

<table width="100%">
  <tr>
    <th>Blender</th>
    <th>3ds Max</th>
  </tr>
  <tr>
    <td width="50%" style="padding: 5px;">
      <img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-blender.png" />
    </td>
    <td width="50%" style="padding: 5px;">
      <img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-max.png" />
    </td>
  </tr>
  <tr>
    <th>Maya</th>
    <th>macOS Native</th>
  </tr>
  <tr>
    <td width="50%" style="padding: 5px;">
      <img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-maya.png" />
    </td>
    <td width="50%" style="padding: 5px;">
      <img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-qtapp-macos-native.png" />
    </td>
  </tr>
  <tr>
    <th>macOS</th>
    <th>Windows</th>
  </tr>
  <tr>
    <td width="50%" style="padding: 5px;">
      <img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-qtapp-macos.png" />
    </td>
    <td width="50%" style="padding: 5px;">
      <img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-qtapp-windows.png" />
    </td>
  </tr>
  <tr>
    <th>Unreal</th>
    <th>Houdini</th>
  </tr>
  <tr>
    <td width="50%" style="padding: 5px;">
      <img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-unreal.png" />
    </td>
    <td width="50%" style="padding: 5px;">
      <img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-houdini.png" />
    </td>
  </tr>
</table>

## Features

- Load menu from a TOML or JSON configuration, from a dict, from entry points,
  or build it programmatically.
- Supports, Blender, 3ds Max, Maya, MotionBuilder,
  Unreal, Houdini and any PySide6 application.
- Declare one or more menus in a dedicated `.toml` file.
- Compose menu from multiple `.toml` files.
- Declare a menu in a `pyproject.toml`.

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
[tahv.gitlab.io/menuet](https://tahv.gitlab.io/menuet).

## Contributing

Contributions of any kind are welcome.
Please [open an issue](https://gitlab.com/tahv/menuet/-/issues), or read the
[contribution guidelines](https://gitlab.com/tahv/menuet/-/blob/main/CONTRIBUTING.md)
and open a [merge request](https://gitlab.com/tahv/menuet/-/merge_requests).

## Alternatives

- [hannesdelbeke/unimenu](https://github.com/hannesdelbeke/unimenu)

<!--

## Roadmap

- [ ] Tests: menuet.builders.maya.MayaMenuBuilder
- [ ] Tests: menuet.builders.unreal.UnrealMenuBuilder
- [ ] Tests: menuet.builders.max.MaxDynamicMenuBuilder
- [ ] Builder: maya.cmds.popupMenu (marking menu)
- [ ] Builder: 3ds Max MenuMan System
- [ ] Helper function to get QMainWindow or QMenuBar
- [ ] Icon path should be relative to file

-->
