# Changelog

Versions follow [Semantic Versioning](https://semver.org)
(`<major>.<minor>.<patch>`).

This file is managed by [towncrier](https://towncrier.readthedocs.io),
and its format is based on [keep a changelog](https://keepachangelog.com).

Changes for the upcoming release can be found in the
[changelog.d](https://gitlab.com/tahv/menuet/-/tree/main/changelog.d) directory
in the repo.

<!-- towncrier release notes start -->

## [1.5.0](https://gitlab.com/tahv/menuet/-/releases/1.5.0) - 2026-07-18

### Breaking changes

- [!9](https://gitlab.com/tahv/menuet/-/merge_requests/9):
  Remove helper function
  `menuet.builders.unreal.model_reference_to_string_command`.

### Enhancements

- [!8](https://gitlab.com/tahv/menuet/-/merge_requests/8):
  Add `menuet.builders.houdini.HoudiniXmlMainMenuBuilder`.

## [1.4.0](https://gitlab.com/tahv/menuet/-/releases/1.4.0) - 2026-05-06

### Enhancements

- [!5](https://gitlab.com/tahv/menuet/-/merge_requests/5):
  Add `MaxDynamicMenuBuilder`.

## [1.3.0](https://gitlab.com/tahv/menuet/-/releases/1.3.0) - 2026-04-27

### Enhancements

- Add `menuet.builders.unreal.UnrealMenuBuilder`.

### Bug fixes

- Fix `MayaMenuBuilder`: creating menu in main menu bar would fail
  because menu long name was incorrect.

## [1.2.0](https://gitlab.com/tahv/menuet/-/releases/1.2.0) - 2026-04-24

### Enhancements

- Add `MayaMenuBuilder`; build a menu with `maya.cmds`.

## [1.1.0](https://gitlab.com/tahv/menuet/-/releases/1.1.0) - 2026-04-15

### Enhancements

- Add `BlenderMenuBuilder`.

### Documentation

- Add JSON schema `https://tahv.gitlab.io/menuet/menuet.json`.
- Add `menuet.demo` module and **Examples** page.
- Add recipes for building model with code and entry points.

## [1.0.0](https://gitlab.com/tahv/menuet/-/releases/1.0.0) - 2026-04-06

### Enhancements

- Initial release.
