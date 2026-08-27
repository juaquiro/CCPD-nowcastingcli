# Module 5 — Documentation: MkDocs for NowcastingCLI

> Part of: Claude Code for Python Developers: Hands-On Agentic Coding
> Repo: CCPD-nowcastingcli
> See also: [Course_Notes_Index.md](./Course_Notes_Index.md)

---

## Part 5 — Documentation: MkDocs for NowcastingCLI

### MkDocs vs Sphinx

**MkDocs** is Markdown-native, has a single `mkdocs.yml` config file, and with
the Material theme produces professional output immediately. The `mkdocstrings`
plugin handles auto-generated API reference from docstrings.

**Sphinx** is the traditional Python doc tool — reStructuredText by default,
steeper config curve, better for multi-package cross-references and ReadTheDocs
publishing at scale.

**Decision for NowcastingCLI:** MkDocs. You already write Markdown, the project
is a single package, and the setup overhead is minimal.

**nDoc analogy:** `mkdocstrings` is the equivalent of nDoc's XML comment
extraction. The `:::` directive points at a Python dotted path the same way
nDoc points at an assembly. `mkdocs.yml` is your nDoc project file.
`mkdocs serve` = local preview. `mkdocs build` = doc generation step in pipeline.

---

### Install

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
```

`mkdocstrings[python]` pulls in `griffe` — an AST-based docstring parser that
reads source without importing it, so no side effects during doc builds.

Add to `pyproject.toml`:

```toml
[project.optional-dependencies]
docs = [
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings[python]",
]
```

Install the group with:

```bash
pip install -e ".[docs]"
```

---

### Project Structure

Scaffold with:

```bash
mkdocs new .   # creates docs/index.md and mkdocs.yml
```

Target layout:

```
nowcastingcli/
├── docs/
│   ├── index.md          # Landing page / overview
│   ├── usage.md          # CLI usage guide
│   ├── architecture.md   # Module map, data flow
│   └── api/
│       ├── models.md
│       ├── physics.md
│       └── heuristics.md
├── mkdocs.yml
├── site/                 # Build output — gitignored
```

Add `site/` to `.gitignore`:

```bash
echo "site/" >> .gitignore
```

---

### mkdocs.yml

```yaml
site_name: NowcastingCLI
site_description: Terminal-based weather nowcasting dashboard
repo_url: https://github.com/<your-username>/CCPD-nowcastingcli
repo_name: CCPD-nowcastingcli

theme:
  name: material
  features:
    - navigation.sections
    - toc.integrate
  palette:
    scheme: slate          # dark mode — fits a CLI tool
    primary: teal

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true
            show_root_heading: true

nav:
  - Home: index.md
  - Usage: usage.md
  - Architecture: architecture.md
  - API Reference:
    - models: api/models.md
    - physics: api/physics.md
    - heuristics: api/heuristics.md
```

`docstring_style: google` — Google-style docstrings (Args / Returns / Raises
sections). Clearest style for scientific code. NumPy style is also supported.

---

### Docstrings with Claude Code

Before `mkdocstrings` can render anything useful, the source needs real
docstrings. Delegate this to Claude Code:

```
Add Google-style docstrings to all public functions and classes in
physics.py, heuristics.py, and models.py.

Rules:
- Include Args, Returns, and Raises sections where applicable
- For physics.py: document the barometric formula in the docstring body,
  mention units for every parameter
- For models.py: document the Observation dataclass fields
- Do not change any logic, only add docstrings
```

**Review checklist for Claude Code's output:**

- Units documented for every parameter in `physics.py`
- `Raises: ValueError` documented where guards exist
- Dataclass fields described in `models.py`
- No logic changes — diff should be docstrings only

**Example — `normalize_pressure` target output:**

```python
def normalize_pressure(raw_pressure: float, altitude: float, temperature: float) -> float:
    """Normalize raw station pressure to QNH (sea-level equivalent).

    Applies the international barometric formula to correct for altitude,
    allowing pressure readings from different elevations to be compared
    on a common baseline.

    Args:
        raw_pressure: Station pressure in hPa (millibars). Must be > 0.
        altitude: Station altitude above mean sea level in metres. Must be >= 0.
        temperature: Ambient temperature in degrees Celsius.

    Returns:
        QNH pressure in hPa, normalized to sea level.

    Raises:
        ValueError: If raw_pressure <= 0 or altitude < 0.
    """
```

Commit after review:

```bash
git add nowcastingcli/
git commit -m "docs: add Google-style docstrings to physics, heuristics, models"
```

---

### API Reference Pages

These pages are intentionally thin — they just invoke the `mkdocstrings`
directive. The plugin resolves the Python dotted path via `griffe` and renders
all public members with their docstrings automatically.

**`docs/api/models.md`**

```markdown
# Models

::: nowcastingcli.models
```

**`docs/api/physics.md`**

```markdown
# Physics

::: nowcastingcli.physics
```

**`docs/api/heuristics.md`**

```markdown
# Heuristics

::: nowcastingcli.heuristics
```

---

### Content Pages

**`docs/index.md`** — landing page, analogous to README:

```markdown
# NowcastingCLI

Terminal-based weather nowcasting dashboard.

Accepts periodic pressure, temperature, humidity, and altitude readings,
normalises pressure to QNH, classifies conditions as **IMPROVING / STABLE / WORSENING**,
and displays a live `rich` dashboard.

## Quick start

​```bash
conda activate nowcastingcli
python -m nowcastingcli
​```
```

**`docs/usage.md`** — document the input loop, valid input ranges, what the
dashboard displays, and how to exit cleanly.

**`docs/architecture.md`** — module map and data flow:

```markdown
# Architecture

## Module map

| Module | Responsibility |
|--------|----------------|
| `models.py` | `Observation` dataclass — pure data, no logic |
| `physics.py` | Barometric normalisation (`normalize_pressure`) |
| `heuristics.py` | Condition classification (`assess_conditions`) |
| `display.py` | `rich` dashboard rendering |
| `main.py` | Input loop, orchestration, logging init |
| `logging_config.py` | `dictConfig` setup, `RotatingFileHandler` |

## Data flow

​```
User input
    │
    ▼
Observation (models.py)
    │
    ├──► normalize_pressure() → QNH       (physics.py)
    │
    └──► assess_conditions()  → verdict   (heuristics.py)
                │
                ▼
           display.py (rich Panel)
                │
                ▼
           logging_config.py → logs/
​```
```

---

### Live Preview and Build

**Live preview** — hot-reloads on every file save:

```bash
mkdocs serve
# opens at http://127.0.0.1:8000
```

Edit any `.md` file or source docstring and the browser updates immediately.
Check the terminal for `WARNING` lines — these indicate missing cross-references
or malformed `:::` directives.

**Static build** — outputs to `site/`:

```bash
mkdocs build
```

`site/` is a self-contained static HTML tree. Open `site/index.html` directly,
copy to any web server, or attach as a CI artifact. No runtime server required.

---

### GitHub Pages Deployment

One-command publish to `gh-pages` branch:

```bash
mkdocs gh-deploy
```

Builds the site and force-pushes to `gh-pages`. GitHub serves it at:
`https://<username>.github.io/CCPD-nowcastingcli/`

**One-time repo setup:** Settings → Pages → Source → `gh-pages` branch, `/ (root)`.

In Module 6 (GitHub Actions CI/CD), this command will be automated: a workflow
will run `mkdocs gh-deploy` on every push to `main`.

---

### Doc Versioning: Version and Date in HTML Output

Three options in increasing complexity. **Option 2 is recommended** for this project.

#### Option 1 — Static footer in `mkdocs.yml` (manual, simplest)

Material renders `copyright` in the page footer automatically:

```yaml
copyright: "NowcastingCLI v0.1.0 — 2026-08-26"
```

Downside: you update it by hand. Fine if you rarely change version or date.

---

#### Option 2 — Dynamic hook: read version from `pyproject.toml` (recommended)

Create `mkdocs_hooks.py` at the repo root:

```python
# mkdocs_hooks.py
import tomllib
from datetime import date

def on_config(config):
    with open("pyproject.toml", "rb") as f:
        meta = tomllib.load(f)
    version = meta["project"]["version"]
    config["extra"]["project_version"] = version
    config["extra"]["build_date"] = date.today().isoformat()
    return config
```

Wire into `mkdocs.yml`:

```yaml
hooks:
  - mkdocs_hooks.py

extra:
  project_version: ""   # populated at build time by the hook
  build_date: ""

copyright: "NowcastingCLI v{{ project_version }} — {{ build_date }}"
```

`tomllib` is stdlib in Python 3.11+ — no extra dependency.
`hooks:` is a native MkDocs 1.x feature — no plugin needed.

**Why this is the right pattern:** version is declared once in `pyproject.toml`
and flows automatically into both the installable package and the HTML docs.
No manual sync, no risk of docs showing a stale version string.

You can also reference `{{ project_version }}` inline in any `.md` page:

```markdown
**Version:** {{ project_version }} — **Built:** {{ build_date }}
```

Commit the hook alongside the docs:

```bash
git add mkdocs_hooks.py mkdocs.yml
git commit -m "docs: add build-time version injection from pyproject.toml"
```

---

#### Option 3 — Full versioned docs with `mike` (for library projects)

`mike` publishes multiple doc versions to `gh-pages` simultaneously (e.g.
`v0.1`, `v0.2`, `latest`) with a version-switcher dropdown in the nav bar.

```bash
pip install mike
mike deploy --push --update-aliases 0.1 latest
mike set-default --push latest
```

Adds a `[project.optional-dependencies]` entry:

```toml
docs = [
    "mkdocs>=1.5,<2",
    "mkdocs-material>=9.7.5",
    "mkdocstrings[python]",
    "mike",
]
```

**When to use:** `mike` is overkill for NowcastingCLI — there is only one
deployed version at a time. It becomes relevant for the `fringeDemod` library
(Project 2), where API stability matters and users may need to pin to an older
version of the docs.

---

### Addendum 2026-08-26 — MkDocs 2.0 Ecosystem Warning

> **Status as of August 2026.** The situation is still evolving.
> Pin versions as described below until there is a clear migration path.

#### What happened

MkDocs 2.0 is a ground-up rewrite of the MkDocs framework by a new maintainer,
published as a pre-release under a separate GitHub org (`encode/mkdocs`).
It is **incompatible with Material for MkDocs and the entire plugin ecosystem**,
including `mkdocstrings`. There is no migration path from MkDocs 1.x.

Key breaking changes in MkDocs 2.0:

| Change | Impact |
|--------|--------|
| Plugin system removed | `mkdocstrings`, `search`, and all third-party plugins stop working |
| Theming system rewritten | Material for MkDocs breaks entirely |
| YAML config replaced with TOML | Existing `mkdocs.yml` files are invalid |
| Closed contribution model | Community cannot report bugs or submit PRs |
| Currently unlicensed | Unsuitable for production or commercial use |

MkDocs 1.x is simultaneously unmaintained — no releases in 18+ months, issues
and PRs piling up, and security fix status unclear.

#### The Material for MkDocs team's response

The Material for MkDocs team (squidfunk) has built **Zensical** — a new static
site generator designed as a drop-in replacement for MkDocs 1.x, compatible
with existing `mkdocs.yml` files and the plugin ecosystem. It is not a fork
(forking is impractical because all 300+ plugins have a hard `mkdocs` package
dependency); it is a clean rewrite with a proper build graph, parallel builds,
and differential builds.

Zensical is in active development. Full plugin compatibility is not yet complete,
but it is the intended long-term home for Material for MkDocs and `mkdocstrings`.

#### What the warning means in practice

The warning you see during `mkdocs serve` / `mkdocs build` is emitted by
**Material for MkDocs ≥ 9.7.2** to alert you that MkDocs 2.0 will break your
build if installed. It does **not** mean your current build is broken — it is
a forward-looking advisory.

To suppress it while the situation resolves:

```bash
export NO_MKDOCS_2_WARNING=1
```

#### How to protect your build today

**Pin `mkdocs` to `<2` in your deps.** Material for MkDocs 9.7.5+ already
does this automatically, but be explicit in your own config:

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.5,<2",
    "mkdocs-material>=9.7.5",
    "mkdocstrings[python]",
]
```

This ensures `pip install -e ".[docs]"` will never accidentally pull in
MkDocs 2.0 if/when it is released to PyPI.

#### Recommended stance for this course

- **Continue using MkDocs 1.x + Material + mkdocstrings** — the stack works,
  is stable, and will receive security attention from the Material team.
- **Watch Zensical** (`zensical.org`) — when it reaches stable plugin
  compatibility, migration from MkDocs 1.x will be straightforward (same
  YAML config, same `:::` directives).
- **Do not install MkDocs 2.0** — it is unlicensed, has no plugin support,
  and no migration path exists for this project's setup.
- **Do not suppress the warning permanently** in CI — keep it visible so you
  notice when the situation changes.

#### Reference

Full analysis by the Material for MkDocs team:
`https://squidfunk.github.io/mkdocs-material/blog/2026/02/18/mkdocs-2.0/`

---

### Exercise Checklist

- [ ] `pip install mkdocs mkdocs-material mkdocstrings[python]`, add to `pyproject.toml` optional deps
- [ ] `mkdocs new .` to scaffold `docs/` and `mkdocs.yml`
- [ ] Add `site/` to `.gitignore`
- [ ] Replace generated `mkdocs.yml` with the config above (update repo URL)
- [ ] Use Claude Code to add Google-style docstrings to `physics.py`, `heuristics.py`, `models.py`
- [ ] Review Claude Code's diff — verify units, Raises sections, no logic changes
- [ ] Commit: `git commit -m "docs: add Google-style docstrings to physics, heuristics, models"`
- [ ] Create `docs/api/models.md`, `docs/api/physics.md`, `docs/api/heuristics.md` with `:::` directives
- [ ] Write `docs/index.md`, `docs/usage.md`, `docs/architecture.md`
- [ ] Run `mkdocs serve` — verify API pages render, no WARNING lines in terminal
- [ ] Run `mkdocs build` — verify `site/` is generated
- [ ] (Optional) Run `mkdocs gh-deploy` — verify GitHub Pages URL is live
- [ ] Create `mkdocs_hooks.py` with `on_config` hook reading version from `pyproject.toml`
- [ ] Add `hooks:` and `extra:` blocks to `mkdocs.yml`; set `copyright` to use `{{ project_version }}` and `{{ build_date }}`
- [ ] Run `mkdocs serve` — verify footer shows correct version and today's date
- [ ] Pin `mkdocs` to `<2` in `pyproject.toml` optional deps (see addendum)
- [ ] Commit: `git commit -m "docs: add MkDocs with Material theme, mkdocstrings API reference"`

---

*Notes will be extended as each module is completed.*
