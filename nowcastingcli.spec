# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for nowcastingcli.

Lets the build be run as `pyinstaller nowcastingcli.spec` without having to
remember the CLI flags (--onefile --name nowcastingcli --distpath dist-exe
--hidden-import ...) each time.

hiddenimports must list every module that is resolved dynamically by name
rather than imported directly, since PyInstaller builds its dependency list
by statically scanning for import statements. `pythonjsonlogger.json` is
here because nowcastingcli/logging_config.py references
"pythonjsonlogger.json.JsonFormatter" as a string inside a dictConfig()
call, not via a direct `import pythonjsonlogger` statement, so PyInstaller
can't see it and silently omits it from the .exe. If a future dictConfig()
entry (formatter, handler, filter) references another module only by
string, add that submodule to hiddenimports too.
"""


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pythonjsonlogger.json'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='nowcastingcli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
