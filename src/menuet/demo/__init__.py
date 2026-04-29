"""
/// version-added | Added in 1.1.0
///
"""  # noqa: D205, D212, D415

from __future__ import annotations

from menuet import Model, loads
from menuet.utils import load_resource

__all__ = ("demo_model",)


def demo_model() -> Model:
    """An example model to demonstrate what menuet can do.

    Example:
        ```python
        >>> from menuet.demo import demo_model
        >>> from menuet.builders.text import Render, TextMenuBuilder
        >>> model = demo_model()
        >>> builder = TextMenuBuilder(model, root_menu="Demo", render=Render.UTF8)
        >>> print(builder.build())
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
    """
    model = Model()
    loads(
        load_resource("menuet.demo:menu.toml").read_text(),
        model=model,
    )
    return model
