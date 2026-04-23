@echo off
rem Run: scripts\test_logging.bat

rem Smoke-test logging: run nowcastingcli with a CSV input file, then pretty-print
rem the JSON log to verify events were written in the correct order.

rem Step 1 - switch console to UTF-8 (code page 65001) so Rich box-drawing
rem          characters and emoji render correctly instead of showing garbled bytes.
chcp 65001 > nul
set PYTHONUTF8=1

rem Step 2 - move to project root so logs\ is created there, not inside scripts\
cd /d "%~dp0\.."

rem Step 3 - activate the conda environment so nowcastingcli is on PATH, then call
rem          it directly. 'call' is required so the batch file resumes after
rem          activate.bat returns (without 'call', CMD exits after the first script).
call conda activate nowcastingcli

rem Step 4 - run the CLI with --input so it reads from the observations file instead
rem          of interactive prompts. No mocking or driver needed.
echo === Running nowcastingcli with 3 scripted observations ===
nowcastingcli --input scripts/test_observations.csv

rem Step 5 - pretty-print the JSON log. type is CMD's equivalent of cat.
rem          --json-lines is required because the log has one JSON object per line
rem          (the default mode expects a single document and fails silently).
echo.
echo === Log output (JSON formatted) ===
type logs\nowcastingcli.log | python -m json.tool --json-lines
