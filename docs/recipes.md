---
icon: lucide/cooking-pot
---

# Recipes

## Execute actions programmatically

Access any [`Action`][menuet.Action] in a `Model` with
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

<div class="result" markdown>

```text
Hello World
```

</div>

## Root keys

The `root_keys` argument of [`load`][menuet.load]
and [`loads`][menuet.loads] can be used to parse a menu configuration from a
sub-table.

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

<div class="result" markdown>

```text
Hello World
```

</div>

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

/// tab | Loading **foo** menu

```python { .copy }
from pathlib import Path

import menuet
from menuet.builders.text import TextMenuBuilder

model = menuet.Model()
menuet.loads(Path("menu.toml").read_text(), model, root_keys=("foo",))

print(TextMenuBuilder(model, root_menu="Example").build())
```

<div class="result" markdown>

```text
Example
└── Foo Menu
    └── Print Hello Foo
```

</div>
///

/// tab | Loading **bar** menu

```python { .copy }
from pathlib import Path

import menuet
from menuet.builders.text import TextMenuBuilder

model = menuet.Model()
menuet.loads(Path("menu.toml").read_text(), model, root_keys=("bar",))

print(TextMenuBuilder(model, root_menu="Example").build())
```

<div class="result" markdown>

```text
Example
└── Bar Menu
    └── Print Hello Bar
```

</div>
///

## Load multiple files in a Model

```python { .copy }
from pathlib import Path

import menuet
from menuet.builders.text import TextMenuBuilder

model = menuet.Model()
loads(Path("menu.toml").read_text(), model)
loads(Path("other-menu.toml").read_text(), model)
```

<!-- TODO(tga): menu from entrypoints -->
<!-- TODO(tga): menu from code -->
