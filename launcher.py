"""Entry point PyInstaller builds against (see nowcastingcli.spec).

Necessary because pointing PyInstaller directly at nowcastingcli/main.py
would run it as a top-level script, stripping its package context — any
relative import inside main.py then fails with "attempted relative import
with no known parent package". Living at the repo root, outside the
nowcastingcli/ package, this script instead does a normal absolute import,
which only requires nowcastingcli to be importable (it is, since it's
installed in the active env). PyInstaller discovers the full package by
statically walking that import.

Consumed by PyInstaller as:

    pyinstaller --onefile --name nowcastingcli --distpath dist-exe \
        --hidden-import pythonjsonlogger.json launcher.py

(Once nowcastingcli.spec exists, rebuild with `pyinstaller
nowcastingcli.spec` instead, to avoid retyping these flags — the spec file
still points at this script as its Analysis entry point, so launcher.py
remains required either way.)
"""

from nowcastingcli.main import cli

if __name__ == "__main__":
    cli()