> [!IMPORTANT]
> Development takes place on GitLab:
> [gitlab.com/tahv/menuet](https://gitlab.com/tahv/menuet).

<div align="center">

  <h1>menuet</h1>

  <p>
    <b>Declarative menu builder for DCC applications</b>
  </p>

  <p>
    <a href="https://tahv.gitlab.io/menuet/">Documentation</a>
    • <a href="https://pypi.org/project/menuet">PyPI</a>
    • <a href="https://gitlab.com/tahv/menuet">GitLab</a>
    • <a href="https://github.com/tahv/menuet">GitHub</a>
    • <a href="https://gitlab.com/tahv/menuet/-/blob/main/CHANGELOG.md">Changelog</a>
    • <a href="https://gitlab.com/tahv/menuet/-/blob/main/CONTRIBUTING.md">Contributing</a>
  </p>

  <p align="center">
    <a href="https://pypi.org/project/menuet"><img alt="PyPI" src="https://img.shields.io/pypi/v/menuet?style=for-the-badge&logo=python&logoColor=white"></a>
    <a href="https://www.buymeacoffee.com/tgambier"><img alt="Buy Me a Coffee" style="height: 28px;" height="28" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"></a>
    <a href="https://gitlab.com/tahv/menuet/-/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/menuet?style=for-the-badge" alt="License MIT"></a>
  </p>

</div>

<table width="100%">
  <tr>
    <td width="50%" style="padding: 5px;"><p align="center"><b>Blender</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-blender.png" /></td>
    <td width="50%" style="padding: 5px;"><p align="center"><b>3ds Max</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-max.png" /></td>
  </tr>
  <tr>
    <td style="padding: 5px;"><p align="center"><b>Maya</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-maya.png" /></td>
    <td style="padding: 5px;"><p align="center"><b>Maya Marking Menu</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-maya-marking-menu.png" /></td>
  </tr>
  <tr>
    <td style="padding: 5px;"><p align="center"><b>macOS</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-qtapp-macos.png" /></td>
    <td style="padding: 5px;"><p align="center"><b>macOS Native</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-qtapp-macos-native.png" /></td>
  </tr>
  <tr>
    <td style="padding: 5px;"><p align="center"><b>Windows</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-qtapp-windows.png" /></td>
    <td style="padding: 5px;"><p align="center"><b>MotionBuilder</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-motionbuilder.png" /></td>
  </tr>
  <tr>
    <td style="padding: 5px;"><p align="center"><b>Unreal Engine</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-unreal.png" /></td>
    <td style="padding: 5px;"><p align="center"><b>Houdini</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-houdini.png" /></td>
  </tr>
  <tr>
    <td style="padding: 5px;"><p align="center"><b>Substance Painter</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-painter.png" /></td>
    <td style="padding: 5px;"><p align="center"><b>Substance Designer</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-designer.png" /></td>
  </tr>
  <tr>
    <td style="padding: 5px;"><p align="center"><b>Nuke</b></p><img src="https://gitlab.com/tahv/menuet/-/raw/main/docs/assets/demo-nuke.png" /></td>
  </tr>
</table>

## Features

- Load menu from a TOML, JSON, YAML, from a Python dict, from entry points,
  or build it programmatically
- Supports, Blender, 3ds Max, Maya, MotionBuilder, Unreal, Houdini,
  Substance Designer, Substance Painter, and any PySide6 application
- Declare one or more menus in a dedicated `.toml`, `.json` or `.yaml` file
- Compose menu from multiple files
- Declare menu in a `pyproject.toml`

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
- [Colorbleed/scriptsmenu](https://github.com/Colorbleed/scriptsmenu)

<!--

## Roadmap

- [ ] Tests: menuet.builders.maya.MayaMenuBuilder
- [ ] Tests: menuet.builders.unreal.UnrealMenuBuilder
- [ ] Tests: menuet.builders.max.MaxDynamicMenuBuilder
- [ ] Builder: `menuet.builders.max.MaxMenuSystemBuilder`
      https://help.autodesk.com/view/MAXDEV/2025/ENU/?guid=menu_system
- [ ] Icon path should be relative to file
- [ ] Error: passthrough expected 0 argument, received 1 argument
- [ ] Define __slots__ in Action and Menu
- [ ] extra shoud be frozendict
- [ ] Builder: MayaShelfBuilder (takes a model and a list of actions ids)
      https://nate-maxwell.github.io/maya-custom-shelf/
- [ ] Filter out actions in builders with 'action.if'.
      Action still added to the model, raise an error when called, filtered out of builders
      https://dotter-documentation.vercel.app/docs/config-structure#conditional-files-with-if
      https://docs.gitlab.com/ci/jobs/job_rules/#cicd-variable-expressions
      `if = ["{dcc} =~ maya|max|mobu && {environment} != production"]`
- [ ] Search Bar

-->
