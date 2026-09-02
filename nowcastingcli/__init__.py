"""NowcastingCLI package root.

Exposes ``__version__``, read from installed package metadata rather than
hardcoded, so it always matches what was installed.
"""

from importlib.metadata import version

# Must match [project] name in pyproject.toml exactly ("nowcastingcli", not
# the module path: "nowcastingcli.main:cli"); only resolves once the package is installed.
__version__ = version("nowcastingcli")

