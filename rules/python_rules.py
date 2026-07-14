SIGNATURES = [
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "requirements-dev.txt",  # common in larger projects
    "Pipfile",               # pipenv projects
    "Pipfile.lock",
    "mypy.ini",
    "environment.yml",
    ".python-version",       # pyenv marker
]

DELETABLES = [
    "venv",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    ".egg-info",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",                  # nox task runner cache
    "htmlcov",               # coverage HTML report folder
    ".hypothesis",           # hypothesis testing cache
]

REVIEWABLES = [
    ".log",
    ".tmp",
    ".coverage",
    "pip-log.txt",
]