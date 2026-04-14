---
icon: lucide/file-cog
---

# Menu Configuration

The [`deserialize`][menuet.deserialize] function accepts a dict of `action`
and `menu` lists.

```python
{
    "action": [],
    "menu": [],
}
```

/// example

```python { .copy }
import menuet
from menuet.builders.text import Render, TextMenuBuilder

model = menuet.Model()
menuet.deserialize({
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
    model,
})

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
visible = true               # display action in menu
enables = true               # allow action to be run
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
