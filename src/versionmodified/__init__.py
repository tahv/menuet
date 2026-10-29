"""A python-markdown extension for describing changes between versions.

- [Python-markdown Extension API](https://python-markdown.github.io/extensions/api/)
- [Blocks Extension API](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/api/)
- [Admonition](https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/admonition/)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import TypeAlias
from typing import TypedDict

from pymdownx.blocks import BlocksExtension
from pymdownx.blocks import BlocksProcessor
from pymdownx.blocks.admonition import Admonition
from typing_extensions import override

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET
    from collections.abc import Mapping

    from markdown import Markdown
    from markdown.extensions import Extension


class VersionConfig(TypedDict):
    """Block configuration."""

    release_url: str
    version_expression: str


VersionKind: TypeAlias = Literal[
    "version-added",
    "version-changed",
    "version-deprecated",
    "version-removed",
]


class VersionModified(Admonition):
    """Describe changes between versions. Inspired by Sphinx version directives.

    The block is structured as follow:

    ```
    /// <version-modified> | <version>
    [content]
    ///
    ```

    - `<version-modified>`: one of the supported version modified types.
    - `<version>`: mandatory version tag, such as `1.2.3`.
    - `[content]`: optional content, a brief explanation.

    Supported modified types are:

    - `version-added`: document the version which **added** the feature.
    - `version-changed`: document the version which **changed** the feature
      in some way (new parameters, changed side effects, etc.).
    - `version-deprecated`: describes when the feature was **deprecated**.
      An explanation can also be gives, for example what to use instead.
    - `version-removed`: describes when the feature was **removed**.
      An explanation can also be gives, for example what to use instead,
      or why the feature was removed.

    Example blocks:

    ```text
    /// version-added | 1.2.0
    ///

    /// version-changed | 1.3.0
    Some content
    ///
    ```

    See: <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#describing-changes-between-versions>
    """

    NAME: VersionKind
    ARGUMENT = True  # type: ignore[assignment]
    config: VersionConfig

    @override
    def on_validate(self, parent: ET.Element) -> bool:
        if super().on_validate(parent) is False:  # type: ignore[no-untyped-call]
            return False

        if self.argument is None:
            return False

        version = self.argument
        assert isinstance(version, str)

        prefixes: dict[VersionKind, str] = {
            "version-added": "Added",
            "version-changed": "Changed",
            "version-deprecated": "Deprecated",
            "version-removed": "Removed",
        }
        modified = prefixes[self.NAME]

        expression = self.config["version_expression"]
        if release_url := self.config["release_url"]:
            release_url = release_url.format(
                version=eval(expression, None, {"version": version})  # noqa: S307
            )
            self.argument = f"{modified} in [{version}]({release_url})"
        else:
            self.argument = f"{modified} in {version}"

        return True


class VersionModifiedExtension(BlocksExtension):
    """Version Modified Extension."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        self.config: Mapping[str, list[Any]] = {
            "release_url": [
                "",
                "Describe changes between versions.",
            ],
            "version_expression": [
                "'{version}'",
                "Apply an expression to the version passed to the release url.",
            ],
        }
        super().__init__(*args, **kwargs)

    @override
    def extendMarkdownBlocks(self, md: Markdown, block_mgr: BlocksProcessor) -> None:
        config: VersionConfig = {
            "release_url": self.config["release_url"][0],
            "version_expression": self.config["version_expression"][0],
        }
        block_mgr.register(
            type(
                "VersionAdded",
                (VersionModified,),
                {"NAME": "version-added", "DEF_CLASS": "version-added"},
            ),
            config,  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        )
        block_mgr.register(
            type(
                "VersionChanged",
                (VersionModified,),
                {"NAME": "version-changed", "DEF_CLASS": "version-changed"},
            ),
            config,  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        )
        block_mgr.register(
            type(
                "VersionDeprecated",
                (VersionModified,),
                {"NAME": "version-deprecated", "DEF_CLASS": "version-deprecated"},
            ),
            config,  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        )
        block_mgr.register(
            type(
                "VersionRemoved",
                (VersionModified,),
                {"NAME": "version-removed", "DEF_CLASS": "version-removed"},
            ),
            config,  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
        )


def makeExtension(*args: Any, **kwargs: Any) -> Extension:  # noqa: ANN401, N802
    """Return extension."""
    return VersionModifiedExtension(*args, **kwargs)
