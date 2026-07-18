from __future__ import annotations

from textwrap import dedent

import pytest

from menuet import Action
from menuet.builders.houdini import (
    HoudiniXmlMainMenuBuilder,
    InsertAfter,
    InsertAtIndex,
    InsertBefore,
    InsertPosition,
)
from menuet.model import Model, loads


def test_houdini_xml_main_menu() -> None:
    model = Model()
    loads(
        dedent("""\
        [[menu]]
        label = "Menu B"
        group = "Group A"

        [[action]]
        id = "action-a"
        label = "Action A"
        group = "Group A"

        [[action]]
        id = "action-b"
        menu = ["Menu B"]
        label = "Action B"

        [[action]]
        id = "action-c"
        menu = ["Menu B"]
        label = "Action C"
        group = "Group B"

        [[action]]
        id = "action-d"
        menu = ["Menu A", "Menu C"]
        label = "Action D"
        """),
        model,
    )

    builder = HoudiniXmlMainMenuBuilder(
        model,
        root_menu="Test Menu",
        to_string_command=lambda a: f"print('{a}')",
    )
    assert builder.build() == dedent("""\
    <?xml version="1.0" encoding="utf-8"?>
    <mainMenu>
      <menuBar>
        <subMenu>
          <label>Test Menu</label>
          <subMenu>
            <label>Menu A</label>
            <subMenu>
              <label>Menu C</label>
              <scriptItem id="action-d">
                <scriptCode><![CDATA[
    print('action-d')]]></scriptCode>
                <label>Action D</label>
              </scriptItem>
            </subMenu>
          </subMenu>
          <titleItem>
            <label>Group A</label>
          </titleItem>
          <subMenu>
            <label>Menu B</label>
            <scriptItem id="action-b">
              <scriptCode><![CDATA[
    print('action-b')]]></scriptCode>
              <label>Action B</label>
            </scriptItem>
            <titleItem>
              <label>Group B</label>
            </titleItem>
            <scriptItem id="action-c">
              <scriptCode><![CDATA[
    print('action-c')]]></scriptCode>
              <label>Action C</label>
            </scriptItem>
          </subMenu>
          <scriptItem id="action-a">
            <scriptCode><![CDATA[
    print('action-a')]]></scriptCode>
            <label>Action A</label>
          </scriptItem>
        </subMenu>
      </menuBar>
    </mainMenu>""")


@pytest.mark.parametrize(
    ("position", "expected_tag"),
    [
        pytest.param(
            InsertAfter(),
            "<insertAfter/>",
            id="insert-after",
        ),
        pytest.param(
            InsertAfter("help_menu"),
            "<insertAfter>help_menu</insertAfter>",
            id="insert-after-id",
        ),
        pytest.param(
            InsertBefore(),
            "<insertBefore/>",
            id="insert-before",
        ),
        pytest.param(
            InsertBefore("help_menu"),
            "<insertBefore>help_menu</insertBefore>",
            id="insert-before-id",
        ),
        pytest.param(
            InsertAtIndex(3),
            "<insertAtIndex>3</insertAtIndex>",
            id="insert-at-index",
        ),
    ],
)
def test_houdini_xml_main_menu_insert_before(
    position: InsertPosition,
    expected_tag: str,
) -> None:
    model = Model()
    model.add_action(Action(id="test-action", label="Test Action"))

    builder = HoudiniXmlMainMenuBuilder(
        model,
        root_menu="Test Menu",
        to_string_command=lambda a: f"print('{a}')",
        position=position,
    )

    assert builder.build() == dedent(f"""\
    <?xml version="1.0" encoding="utf-8"?>
    <mainMenu>
      <menuBar>
        <subMenu>
          <label>Test Menu</label>
          {expected_tag}
          <scriptItem id="test-action">
            <scriptCode><![CDATA[
    print('test-action')]]></scriptCode>
            <label>Test Action</label>
          </scriptItem>
        </subMenu>
      </menuBar>
    </mainMenu>""")
