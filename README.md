Onion - distributed tasks runner
================================


This repo provides simple framework for running distributed tasks on Python.

## Getting Started

The project is ready to run as is. You will need Python 3.6 or later.

### Create a Virtual Environment

After cloning or downloading the repo, create a Python virtual environment with:

```
python -m venv .venv
```

### Activate the Virtual Environment

Now activate the virtual environment. on macOS, Linux and Unix systems, use:

```
. .venv/bin/activate
```

On Windows:

```
.venv\Scripts\activate.bat
```

### Install the Development Environment

Now run:

```
pip install -e .[dev]
```

This will install the packages the project depends on in production as well as packages needed during development.

At this point, you are ready to start modifying to template for your own needs.

## Testing

You can run unit tests through setup.py with:

```
python setup.py test
```

or just run pytest directly:

```
pytest
```

## Documentation

To generate Sphinx documentation, run:

```
python setup.py doc
```

The generated documentation will be available in `docs/_build`

