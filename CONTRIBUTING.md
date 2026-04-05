# Contributing

## Project commands

The easiest way to run project commands is to
[install just](https://just.systems/man/en/installation.html).

For example, the `rust-just` Python package can be installed with
[`uv`](https://docs.astral.sh/uv/concepts/tools/):

```console
uv tool install rust-just
just
```

Or executed without installation with
[`uvx`](https://docs.astral.sh/uv/guides/tools/):

```console
uvx --from rust-just just
```

Running `just` without any arguments list available recipes in the
[justfile](./justfile) at the root of the repo.

```console
just
```

## Local development environment

The project virtual environment can be created with `uv`:

```console
uv sync --all-extras
```

Or with this `just` recipe:

```console
just sync
```

If you don't want to use `uv` or `just`, you can use pip 25.1
(that added support for dependency groups)
or newer and install the dependencies manually:

```console
pip install --editable .[copy,qt] --group dev
```

## Changelog

We use [towncrier](https://towncrier.readthedocs.io/) to manage our
[CHANGELOG.md](./CHANGELOG.md).

To create a news fragment,
run the following command and follow the instructions:

```console
towncrier create --no-edit
```

Or use this `just` recipe:

```console
just news
```

Alternatively, you don't need to install towncrier,
you just have to abide by a few simple rules:

For each merge request, add a new file into the `changelog.d` directory with a
filename adhering to the schema: `mr#.(break|feat|fix|doc|other|chore).md`.
For example, `changelog.d/123.feat.md` for a feature
that is proposed in pull request `#123`.

See `tool.towncrier.types` in the [`pyproject.toml`](./pyproject.toml)
for the list of fragment types.
