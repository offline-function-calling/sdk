---
title: Tools
summary: Install and setup tools related to function calling on your machine
---

<style>
  .codehilite { margin-top: 16px; margin-bottom: 16px; }
  html.dark .typography details summary::after { filter: invert(100%); }
  #mkdocs-search-results article > h3 { color: var(--foreground); }
</style>

## Python

[`python`](https://github.com/python/cpython) is a programming language, and [`uv`](https://github.com/astral-sh/uv) is a package and version manager.

### Setup

Download and install `uv` following the [official instructions](https://docs.astral.sh/uv/getting-started/installation/).

Make sure it is installed by executing the following command:

```bash
uv --version
```

### Usage

The following is a list of commands you might need to use often:

```bash
# install the latest python version
uv python install

# run a python script
uv run script.py

# run a jupyter notebook
uv run --with jupyter jupyter lab my-notebook.ipynb

# create a project
uv init my-new-project

# add a dependency
uv add my-dependency
```

To run a Python script, execute the following command:

Refer to the [official documentation](https://docs.astral.sh/uv/guides/) for more commands and info.

## Microsandbox

[`microsandbox`](https://github.com/microsandbox/microsandbox) allows you to spin up secure sandboxes to execute arbitrary user code.

### Setup

Install it on your machine by following the official [installation instructions](https://docs.microsandbox.dev/guides/getting-started/#installation).

Next, run the server in development mode by executing the following command:

```bash
msb server start --dev
```

This starts a server with a JSON-RPC API on port `5555`, which allows us to programmatically manage sandboxes and execute code.

### Usage

Refer to the official [documentation](https://docs.microsandbox.dev) for more information about it.
