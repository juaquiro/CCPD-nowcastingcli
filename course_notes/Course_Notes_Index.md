# Claude Code for Python Developers — Course Notes Index

> **Course:** Claude Code for Python Developers: Hands-On Agentic Coding
> **Repo:** CCPD-nowcastingcli
> **Last updated:** 2026-08-27

This index replaces the single monolithic `COURSE_NOTES.md`. Notes are now
split one file per module — easier to manage, easier to extend as new
modules (fringeDemod, GitHub Actions, packaging/delivery, etc.) are added.

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
`python -m build` producing wheel + sdist, and the manual delivery paths
(TestPyPI/PyPI via Trusted Publishing, conda packaging as an alternative,
and plain local/editable install for another machine). This module is the
prerequisite for Module 7 — CI/CD automates exactly the manual steps
established here. Closes with a repo-state note: current branch renames
to `develop`, and a new `main` branch is created as the stable/release
branch, setting up Module 7's branch model.

**Sections:**
- Build Backends and `pyproject.toml`
- `python -m build`: Wheel vs sdist
- Version Source of Truth
- Manual Delivery Path 1 — TestPyPI / PyPI (Trusted Publishing vs. token upload)
- Manual Delivery Path 2 — conda packaging
- Manual Delivery Path 3 — Local/editable install on another machine
- Standalone Package Checklist (what "ready for installation on another machine" means)
- Exercise Checklist

---

## Module 7 — CI/CD: GitHub Actions

**Summary:** Migrated the manual Module 6 delivery process into two GitHub
Actions workflows, using a two-branch model (`develop` = integration,
`main` = release) with GitHub branch protection as the enforcement
mechanism. Covered the distinction between `pull_request`-triggered checks
(gates, block merge) and `push`-triggered checks (post-merge confirmation),
PyPI Trusted Publishing via OIDC, auto-tagging with idempotency, and the
four standard working scenarios including the hotfix exception path.
Explicitly separates what is GitHub-platform-dependent (portable only via
migration effort) from what is tooling-standard (portable as-is).

**Sections:**
- GitHub Actions vs. NAnt — Conceptual Mapping
- Branch Model: `develop` (integration) vs `main` (release)
- Workflow 1 — `smoke-tests.yml` (triggers, gate vs. confirmation runs)
- Workflow 2 — `release.yml` (triggers, gate vs. ship runs, `if: github.event_name == 'push'`)
- Branch Protection Rules (required status checks, up-to-date requirement)
- PyPI Trusted Publishing (OIDC, `permissions: id-token: write`)
- Auto-Tag and Release Idempotency
- **The Four Working Scenarios** (Normal Development, Feature Work, Build/Release, Hotfix)
- **What Is GitHub-Dependent vs. Tool-Standard** (portability audit)
- Exercise Checklist

---

## On the Horizon

- fringeDemod (Course Project 2, Module 1) — scientific library design
- fringeDemod-cli (Module 2) — CLI wrapper, dependency management
- fringeDemod-qt (Module 3) — PyQt GUI, threading, SQLite
- fringeDemod-web (Module 4) — FastAPI, HTTP basics, Docker (optional)

*This index and the per-module files will be extended as each new module is completed.*
