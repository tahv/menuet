---
icon: lucide/file-cog
---

# Menu Configuration

The [`load`][menuet.load] function takes a dict of
`#!py3 { "action": [], "menu": [] }`.

```python { title="Example" .copy }
import menuet
from menuet.builders.text import Render, TextMenuBuilder

model = menuet.Model()
load(
    {
        "menu": [
            {
                "label": "Sub-Menu",
                "menu": ["My App"],
                "group": "Separator",
            },
        ],
        "action": [
            {
                "id": "open-gui",
                "label": "Open GUI",
                "cb": "import myapp; myapp.open_gui()",
                "menu": ["My App", "Sub-Menu"],
            },
            {
                "id": "print-hello",
                "label":  "Print Hello",
                "cb": 'print("Hello")',
            },
        ],
    },
    model,
)

builder = TextMenuBuilder(model, root_menu="Example", render=Render.UTF8)
print(builder.build())
```

/// html | div.result

```text
Example
├── My App
│   ├── Separator ───
│   └── Sub-Menu
│       └── Open GUI
└── Print Hello
```

///

## Action Options

The `[[action]]` tables accepts the following options:

```toml { .copy }
[[action]]                   # `action` is an array of action tables
id = "my-action"             # unique identifier [required]
label = "My Action"          # display name
menu = ["Menu", "Sub-Menu"]  # parent menus hierarchy
group = "My Group"           # group related menus and actions
cb = "print('Hello !')"      # action callback
desc = "Print Hello"         # tooltip
icon = "icons/my-icon.png"   # path to an icon
```

## Menu Options

The `[[menu]]` tables accepts the following options:

```toml { .copy }
[[menu]]                    # `menu` is an array of menu tables
label = "My Menu"           # display name [required]
desc = "My App Scripts"     # tooltip
menu = ["Parent Menu"]      # parent menus hierarchy
group = "My Group"          # group related menus and actions
icon = "icons/my-icon.png"  # path to an icon
```

Menus defined in `[[action]]` tables are created automatically.
The only reason to configure `[[menu]]` explicitly is to set an `icon`,
a `group`, or a `desc`.

## `icon` Schemes

<!-- TODO(tga): path relative to toml config -->

The `icon` option accepts a value in the format `<path>` or `<scheme>:<value>`.
The following schemes are available:

- `path` *(default)*: takes a path to an icon file.

    ```toml
    icon = "icons/settings.png"

    icon = "path:icons/settings.png"
    ```

- `res`: load a [resource file][importlib.resources.files].
  Value is in the form `res:importable.module:file.ext`.

    ```toml
    icon = "res:myapp.data:logo.svg" 
    ```

## `cb` Schemes

The `cb` option accepts a value in the format `<script>` or `<scheme>:<value>`.
The following schemes are available:

- `exec` *(default)*: takes a Python script.

    ```toml
    cb = "print('Hello !')"

    cb = "exec:import myapp; myapp.open_gui()"

    cb = """\
    from importlib.metadata import version
    print(version("myapp"))
    """

    cb = """exec:\
    import myapp
    myapp.open_gui()
    """
    ```

- `ep`: loads an [entry point][importlib.metadata.EntryPoint].
  Value is in the form `ep:importable.module:callable`.

    ```toml
    cb = "res:myapp.my_module:open_gui"

    cb = "res:myapp:my_function"
    ```

- `copy`: copy its value to the clipboard.

    ```toml
    cb = "copy:Lorem ipsum dolor sit amet"
    ```

    /// warning

    The `copy` scheme requires the
    [copykitten](https://github.com/klavionik/copykitten) package,
    available as an extra:

    ```console { .copy }
    pip install menuet[copy]
    ```

    ///

- `url`: takes a URL and open it in the default browser.

    ```toml
    cb = "url:https://codeberg.org/tahv/menuet"
    ```

## JSON Schema

Menuet provides its own
[JSON Schema](https://json-schema.org/understanding-json-schema/about).
If your editor supports TOML schema validation,
it's recommended to set it up to enable validation diagnostics and auto-complete
when editing a menu file:

Both [tombi](https://tombi-toml.github.io/tombi/docs)
and [taplo](https://taplo.tamasfe.dev/) supports the `#:schema` directive to
specify the schema to use for the document.

Add the comment directive at the beginning of the document,
followed by a blank line.

```toml { title="menu.toml" .copy }
#:schema https://tahv.codeberg.page/menuet/menuet.json

```

### Sub Schema

Tombi can be [configured](https://tombi-toml.github.io/tombi/docs/configuration)
with
[sub schema](https://tombi-toml.github.io/tombi/docs/configuration#sub-schema)
to apply a schema to a specific part of the TOML document.

```toml { title="tombi.toml" .copy }
[[schemas]]
root = "tool.my-menu"
path = "https://tahv.codeberg.page/menuet/menuet.json"
include = ["pyproject.toml"]
```
