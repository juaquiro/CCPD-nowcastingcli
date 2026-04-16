# Conda Environment Sync via Git

Strategy and scripts for keeping a conda environment in sync across multiple machines using Git.

## Approach

A single `environment.lock.yml` file (full export of the conda environment) is committed to the repository. Two batch scripts handle regenerating and syncing it.

No minimal `environment.yml` is needed when all machines share the same OS and architecture.

## Files

```
project-root/
+-- environment.lock.yml        # full conda export, committed to git
+-- scripts/
    +-- update_lock.bat         # run after installing/updating packages
    +-- sync_env.bat            # run on the other machine after pulling
```

## Usage

Both scripts must be run from the **repository root** in the **Anaconda Prompt**.

**After installing or updating a package:**
```
scripts\update_lock.bat
scripts\update_lock.bat "optional custom commit message"
```

**On the other machine, to pull and sync the environment:**
```
scripts\sync_env.bat
```

## What each script does

### `update_lock.bat`
1. Checks the Git repo and conda environment exist
2. Exports the active environment to `environment.lock.yml`
3. Stages, commits, and pushes the lock file

### `sync_env.bat`
1. Checks for uncommitted local changes and warns if found
2. Runs `git pull`
3. Updates the existing environment (`conda env update --prune`) or creates it from scratch if it does not exist yet

## Lessons learned (Windows / Anaconda Prompt)

### `conda run` kills the parent batch process
`conda run -n ENV cmd` is documented to activate an environment and run a command, but on Windows it frequently terminates the calling `.bat` process after finishing, silently, with no error. The script stops mid-execution with no output.

**Fix:** use `conda env export -n ENV` directly (no `conda run`), wrapped in a `cmd /c` child process:
```bat
cmd /c "conda env export -n %ENV_NAME% > %LOCK_FILE%"
```

### Do not check errorlevel after conda commands
`conda env export` and `conda run` regularly return non-zero exit codes even when they succeed. Checking `if errorlevel 1` after them causes the script to abort silently on a false positive.

**Fix:** check for the existence of the output file instead:
```bat
if not exist "%LOCK_FILE%" ( echo [ERROR] export failed & exit /b 1 )
```

### `git diff --quiet` does not detect new untracked files
`git diff --quiet FILE` compares the working tree vs the staging area. After `git add`, staging and working tree are identical, so it always returns 0 (no changes), even if the file is brand new and was never committed.

**Fix:** use `git diff --cached --quiet FILE`, which compares the staging area vs the last commit. Returns 1 if there are staged changes (new or modified file), 0 if nothing changed.

### Batch files must use CRLF line endings and pure ASCII
`.bat` files generated on Linux/macOS or by tools that default to UTF-8 with LF line endings silently misbehave in Windows CMD and Anaconda Prompt: commands are not recognised, variables are not expanded, and the script exits immediately.

**Fix:** always write `.bat` files with CRLF line endings and ASCII-only content (no accented characters, no box-drawing characters).

### `if errorlevel N` vs `if %ERRORLEVEL%==N`
`if errorlevel N` is true when errorlevel is **greater than or equal to** N, not exactly N. For exact comparisons use:
```bat
if %ERRORLEVEL%==0 ( ... )
```

### ANSI colors work in Anaconda Prompt (Windows 10+)
Standard ANSI escape codes for color output work in the Anaconda Prompt without any extra dependencies, using this pattern to obtain the ESC character:
```bat
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "NC=%ESC%[0m"
```
