---
icon: lucide/mouse-pointer-click
---

# Examples

This section build the [`demo_model`][menuet.demo.demo_model] in different
applications.

## QApplication

```python { .copy }
--8<-- "docs/assets/demo_qtapp.py"
```

/// html | div.result

**Windows:**

![QApplication on Windows](./assets/demo-qtapp-windows.png)

**macOS:**

![QApplication on macOs](./assets/demo-qtapp-macos.png)

**macOS native:**

![QApplication on macOS in native menubar](./assets/demo-qtapp-macos-native.png)

///

## Blender

```python { .copy }
--8<-- "docs/assets/demo_blender.py"
```

/// html | div.result

![Blender](./assets/demo-blender.png)

///

## Text

```python { .copy }
from menuet.builders.text import Render, TextMenuBuilder
from menuet.demo import demo_model

model = demo_model()
builder = TextMenuBuilder(model, root_menu="Demo", render=Render.UTF8)
menu = builder.build()

print(menu)
```

/// html | div.result

```text
Demo
├── Animation
│   ├── FBX
│   │   ├── FBX Animation Exporter
│   │   └── FBX Animation Importer
│   ├── Bake Animation
│   ├── Edit ───
│   ├── Adjustment Blending
│   └── Tween Machine
├── Development
│   └── Start Debugger
├── Modeling
│   ├── Mesh Cleaner
│   ├── Mesh Randomizer
│   └── Mirror Geometry
├── Rigging
│   ├── Joint Tools
│   ├── Skinning Tools
│   ├── Controller ───
│   ├── Controller Creator
│   └── Controller Editor
└── Open Documentation
```

///
