# Claude Code for Python Developers — Course Notes Index

> **Course:** Claude Code for Python Developers: Hands-On Agentic Coding
> **Repo:** CCPD-nowcastingcli
> **Last updated:** 2026-09-11

This index replaces the single monolithic `COURSE_NOTES.md`. Notes are
split one file per module — easier to manage, and easier to extend as new
modules are added — but the seven files below tell one continuous story:
building NowcastingCLI from an empty directory (Module 1) through a
self-publishing CI/CD pipeline (Module 7). Read them in order the first
time through; use this index and the cross-references inside each module
to jump around afterward.

**Course Project 1 (NowcastingCLI) is complete** — all seven modules
below are finished and verified end-to-end. Project 2 (fringeDemod) is
next; see "On the Horizon" below.

---

## Reading This Set

Every module file (`ModuleN_Course_Notes.md`) opens with the same
metadata block so you can navigate without going back to this index:

```
> Part of: Claude Code for Python Developers: Hands-On Agentic Coding
> Project: NowcastingCLI (`CCPD-nowcastingcli`)
> Previous: <link to Module N-1, or "—" for Module 1>
> Next: <link to Module N+1, or "—" for Module 7>
> See also: Course Notes Index
```

Each module also closes with a **"Module N complete"** line pointing to
whatever comes next. Within the body text, the first mention of a concept
that properly belongs to another module is a link to it — e.g. Module 2's
tests are only trivial because of a design decision made in Module 1;
Module 5's docs describe the same `physics.py`/`heuristics.py` that
Module 3 refactored. Follow those links rather than treating each file as
self-contained background reading.

Two formatting conventions carried through every module:
- **Exercise Checklist** at the end of each file — `[ ]` for undone,
  `[x]` for verified complete. Modules 6 and 7 also use checklists inline
  to track sub-verifications (e.g. "Standalone Package Checklist" in
  Module 6) since those modules involve more external, hard-to-automate
  verification (PyPI uploads, a second Windows user account, GitHub
  branch protection) than the earlier ones.
- **Numbered `##` sections** (`## 1. ...`, `## 2. ...`) in Modules 6 and 7,
  where the material is naturally a sequence of delivery paths / workflow
  components referenced by number elsewhere in the same file. Modules 1–5
  use plain (unnumbered) `##` sections, since their content is referenced
  by name, not number.

---

## Modules

| # | File | Topic |
|---|------|-------|
| 1 | [Module1_Course_Notes.md](./Module1_Course_Notes.md) | NowcastingCLI: Project Setup |
| 2 | [Module2_Course_Notes.md](./Module2_Course_Notes.md) | pytest: Unit Testing NowcastingCLI |
| 3 | [Module3_Course_Notes.md](./Module3_Course_Notes.md) | Claude Code: Refactoring, Test Generation, Code Explanation |
| 4 | [Module4_Course_Notes.md](./Module4_Course_Notes.md) | Logging: Structured Logs for NowcastingCLI |
| 5 | [Module5_Course_Notes.md](./Module5_Course_Notes.md) | Documentation: MkDocs for NowcastingCLI |
| 6 | [Module6_Course_Notes.md](./Module6_Course_Notes.md) | Build, Packaging, and Manual Delivery |
| 7 | [Module7_Course_Notes.md](./Module7_Course_Notes.md) | CI/CD: GitHub Actions (branch model, 4 workflow triggers, 4 working scenarios) |

---

## Module 1 — NowcastingCLI: Project Setup

**Summary:** Scaffolded the NowcastingCLI package (`models.py`, `physics.py`,
`heuristics.py`, `display.py`, `main.py`), set up the conda environment, and
did an editable install via `pyproject.toml`. Established the barometric
QNH-normalization formula and the improving/stable/worsening heuristic rules
that every later module builds on.

**Sections:**
- Project Overview
- Project Structure
- Environment Setup
- Module Breakdown (`models.py`, `physics.py`, `heuristics.py`, `display.py`, `main.py`, `pyproject.toml`)
- Key Concepts (editable install, pure functions, `rich` console lifecycle, in-memory time series)
- Exercise Checklist
- What Each Module Will Touch

---

## Module 2 — pytest: Unit Testing NowcastingCLI

**Summary:** Introduced pytest over `unittest`, wrote tests for the pure
functions in `physics.py` and `heuristics.py`, covered `pytest.approx` for
float comparisons, parameterized tests, coverage via `pyproject.toml`, and
two VS Code debugging workflows (F5 GUI debugger and `breakpoint()`/`pdb`).

**Sections:**
- Why pytest
- Install
- Where Tests Live
- Testing `physics.py`
- Testing `heuristics.py`
- `pytest.approx`
- Parameterized Tests
- Coverage
- Running Subsets
- Debugging Tests in VS Code (Mode 1: VS Code GUI, Mode 2: `breakpoint()` + Terminal, When to Use Which)
- Exercise Checklist

---

## Module 3 — Claude Code: Refactoring, Test Generation, Code Explanation

**Summary:** Installed Claude Code (npm-based agentic CLI tool) and ran it
through three core workflows against the NowcastingCLI codebase: explaining
`normalize_pressure()`, refactoring `physics.py` (extracting constants,
adding validation), and generating tests for the new guards. Covered slash
commands, `CLAUDE.md` persistent project instructions, and VS Code
integration.

**Sections:**
- What Claude Code Is
- Installation
- First Launch
- Use Case 1 — Code Explanation
- Use Case 2 — Refactoring
- Use Case 3 — Test Generation
- Slash Commands
- `CLAUDE.md` — Persistent Project Instructions
- VS Code Integration
- Exercise Checklist

---

## Module 4 — Logging: Structured Logs for NowcastingCLI

**Summary:** Replaced `print()` with Python's `logging` module. Covered
logger hierarchy, handlers/formatters, `dictConfig` vs `basicConfig`,
structured JSON logging via `python-json-logger`, and where to place log
calls across `main.py`, `physics.py`, and `heuristics.py`. Included a
ready-to-run Claude Code agentic task prompt for wiring it all up.

**Sections:**
- Why Logging Not `print()`
- Logger Hierarchy
- Handlers and Formatters
- `dictConfig` vs `basicConfig`
- Structured JSON Logging
- Where to Log in NowcastingCLI
- Implementation (step-by-step)
- Claude Code Agentic Task
- Verifying Output
- Exercise Checklist

---

## Module 5 — Documentation: MkDocs for NowcastingCLI

**Summary:** Chose MkDocs + Material + `mkdocstrings` over Sphinx (nDoc
analogy for the XML-comment-extraction mental model). Covered docstring
generation via Claude Code, API reference pages, `mkdocs.yml` config, live
preview/build, GitHub Pages deployment, and build-time version injection
from `pyproject.toml`. Includes an addendum on the MkDocs 2.0 ecosystem
break and the recommended stance (pin `mkdocs<2`, watch Zensical).

**Sections:**
- MkDocs vs Sphinx
- Install
- Project Structure
- `mkdocs.yml`
- Docstrings with Claude Code
- API Reference Pages
- Content Pages
- Live Preview and Build
- GitHub Pages Deployment
- Doc Versioning: Version and Date in HTML Output (3 options)
- Addendum 2026-08-26 — MkDocs 2.0 Ecosystem Warning
- Exercise Checklist

---

## Module 6 — Build, Packaging, and Manual Delivery

**Summary:** Covered the standard Python build/packaging chain independent
of any CI system — `pyproject.toml` as the single build-config source,
`python -m build` producing wheel + sdist, and five manual delivery paths
ranging from TestPyPI/PyPI (Trusted Publishing) down to a fully
self-contained standalone `.exe` (PyInstaller) and a Raspberry Pi/`pipx`
install for machines with no prior Python setup. This module is the
prerequisite for [Module 7](./Module7_Course_Notes.md) — CI/CD automates
exactly the manual steps established here. Closes with a repo-state note:
current branch renames to `develop`, and a new `main` branch is created as
the stable/release branch, setting up Module 7's branch model.

**Sections:**
- Build Backends and `pyproject.toml`
- `python -m build`: Wheel vs sdist
- Version Source of Truth
- Manual Delivery Path 1 — TestPyPI / PyPI (Trusted Publishing vs. token upload)
- Manual Delivery Path 2 — conda packaging
- Manual Delivery Path 3 — Local/editable install on another machine
- Manual Delivery Path 4 — Standalone `.exe` (PyInstaller): launcher-script and hidden-import fixes, the `.spec` file, verifying on a Python-free machine
- Manual Delivery Path 5 — Unix / Raspberry Pi (`pipx`): why PyInstaller/conda don't fit, why `pipx` does
- Standalone Package Checklist (what "ready for installation on another machine" means)
- Exercise Checklist

---

## Module 7 — CI/CD: GitHub Actions

**Summary:** Migrated the manual [Module 6](./Module6_Course_Notes.md)
delivery process into two GitHub Actions workflows, using a two-branch
model (`develop` = integration, `main` = release) with GitHub branch
protection as the enforcement mechanism. Covered the distinction between
`pull_request`-triggered checks (gates, block merge) and `push`-triggered
checks (post-merge confirmation), PyPI Trusted Publishing via OIDC,
auto-tagging with idempotency, and the four standard working scenarios
including the hotfix exception path — all four walked end-to-end against
the real repo, not just designed. Explicitly separates what is
GitHub-platform-dependent (portable only via migration effort) from what
is tooling-standard (portable as-is). Closes with final verification
tasks: a real clean-room `pip install` from PyPI, automated docs
deployment to GitHub Pages (with two real CI bugs found and fixed along
the way), and granting third-party collaborator access.

**Sections:**
- GitHub Actions vs. NAnt — Conceptual Mapping
- Branch Model: `develop` (integration) vs `main` (release)
- Workflow 1 — `smoke-tests.yml` (triggers, gate vs. confirmation runs)
- Workflow 2 — `release.yml` (triggers, gate vs. ship runs, `if: github.event_name == 'push'`)
- Branch Protection Rules (required status checks, up-to-date requirement)
- PyPI Trusted Publishing (OIDC, `permissions: id-token: write`)
- **The Four Working Scenarios** (Normal Development, Feature Work, Build/Release, Hotfix) — each verified end-to-end
- **What Is GitHub-Dependent vs. Tool-Standard** (portability audit)
- Final Verification Tasks — clean-room PyPI install, GitHub Pages docs deployment, third-party collaborator access
- Exercise Checklist

---

## Related Repository Documentation

The course notes above are a **narrative record** of how NowcastingCLI was
built, module by module — they capture decisions, dead ends, and the
reasoning behind them, and are not updated after the fact when the repo
moves on. For the **current, living state** of the same subjects, see:

| Topic | Course narrative | Current state |
|---|---|---|
| CI/CD workflows | [Module 7](./Module7_Course_Notes.md) | [`README.md` § CI/CD Pipeline](../README.md#cicd-pipeline) and [`.github/workflows/`](../.github/workflows/) |
| Packaging / distribution | [Module 6](./Module6_Course_Notes.md) | [`README.md` § Building a Distributable Package](../README.md#building-a-distributable-package) |
| Build config, dependencies, version | [Module 1](./Module1_Course_Notes.md), [Module 6 §3](./Module6_Course_Notes.md#3-version-source-of-truth) | [`pyproject.toml`](../pyproject.toml) |
| Logging | [Module 4](./Module4_Course_Notes.md) | [`README.md` § Logging](../README.md#logging) and `nowcastingcli/logging_config.py` |
| API / architecture docs | [Module 5](./Module5_Course_Notes.md) | [`docs/`](../docs/) (built via `mkdocs serve`/`mkdocs build`) |
| Conda environment sync | *(not covered by a module)* | [`README_CONDA_ENV_SYNC.md`](../README_CONDA_ENV_SYNC.md) |

When the two disagree, the repo docs in the right-hand column are correct
— treat a mismatch as the course notes having fallen behind, not the other
way around.

---

## On the Horizon

- fringeDemod (Course Project 2, Module 1) — scientific library design
- fringeDemod-cli (Module 2) — CLI wrapper, dependency management
- fringeDemod-qt (Module 3) — PyQt GUI, threading, SQLite
- fringeDemod-web (Module 4) — FastAPI, HTTP basics, Docker (optional)

*This index and the per-module files will be extended as each new module of Project 2 is completed.*
