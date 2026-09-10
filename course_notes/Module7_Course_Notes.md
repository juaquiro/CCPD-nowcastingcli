# Module 7 — CI/CD: GitHub Actions

> Part of: Claude Code for Python Developers: Hands-On Agentic Coding
> Project: NowcastingCLI (`CCPD-nowcastingcli`)
> Builds on: Module 6 (the manual process this module automates)

---

## 1. GitHub Actions vs. NAnt — Conceptual Mapping

| NAnt | GitHub Actions |
|---|---|
| `.build` file | `.github/workflows/*.yml` |
| `<target>` | `job` |
| `<task>` inside a target | `step` inside a job |
| `depends="..."` attribute on a target | `needs:` on a job |
| Conditional task execution (`if`/`unless` on a task) | `if:` on a job or step |
| Trigger: whatever invokes NAnt (scheduled job, manual `nant.exe` call, external poll) | `on:` event (`push`, `pull_request`, `release`) — the event itself is the trigger, built into the platform |
| Build machine you provision and maintain | `runs-on: ubuntu-latest` — ephemeral, GitHub-hosted runner, spun up per run and discarded |
| Credentials on the build machine / passed as build properties | GitHub Actions **Secrets**, or OIDC Trusted Publishing (no stored secret at all) |

Key mental shift from NAnt: GitHub Actions workflows are **event-driven and
declarative**, and the runner has no persistent state between runs — there's
no build machine to provision or keep patched; each run starts from a clean
image. `needs:` replaces the `depends` chain you'd build between NAnt
targets, and `if:` conditionals replace what you'd otherwise handle with
NAnt's own conditional task attributes or a wrapping script.

---

## 2. Branch Model: `develop` (integration) vs `main` (release)

- **`develop`** — integration branch. Feature branches PR into this.
  Protected, requires the smoke-test check.
- **`main`** — release branch. `develop` PRs into this. Protected, triggers
  the full pipeline. Represents "what's installable right now" — matches
  GitHub's own default-branch assumption (Dependabot, security alerts,
  template defaults all assume `main` = stable).

This is a deliberate rename from an earlier draft (`main`=dev, `build`=release)
specifically to avoid fighting GitHub's built-in conventions.

**Implementation in this repo:**

- `develop` was branched off the tip of the original single-branch `main`
  (so it started with full history, nothing lost) and pushed to `origin`.
- `develop` was then set as the repository's **default branch**
  (Settings → General → Default branch, or `gh api -X PATCH
  repos/{owner}/{repo} --field default_branch=develop`). New clones,
  new PRs, and the branch shown by default on GitHub now point at
  `develop`, matching its role as the everyday integration branch.
- `main` was locked down with a branch protection rule (`gh api -X PUT
  repos/{owner}/{repo}/branches/main/protection`):
  - Pull request required to merge (`required_pull_request_reviews`,
    `required_approving_review_count: 0` — a PR is mandatory, but a solo
    maintainer doesn't need a second reviewer to approve their own PR).
  - `allow_force_pushes: false` — history on `main` can't be rewritten.
  - `allow_deletions: false` — the branch can't be deleted.
  - `enforce_admins: false` — the repo admin can still bypass protection
    in an emergency (e.g., a hotfix that can't wait), rather than being
    locked out entirely.
- Net effect: `git push origin main` now fails for everyone, including the
  admin, unless they explicitly bypass protection; the only supported path
  onto `main` is a merged pull request from `develop` (or a `hotfix/*`
  branch, see Scenario 4).

---

## 3. Workflow 1 — `smoke-tests.yml`

```yaml
name: Smoke Tests
on:
  pull_request:
    branches: [develop]
  push:
    branches: [develop]

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.x" }
      - run: pip install -e .[dev]
      - run: pytest -m smoke --no-cov
```

Requires marking a test subset:
```python
@pytest.mark.smoke
def test_normalize_pressure_basic(): ...
```
and registering the marker in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = ["smoke: fast subset run on every push/PR to develop"]
```

**Two roles from one job:**
- `pull_request → develop` run = **the gate**. Required status check;
  blocks merge if red.
- `push → develop` run = **post-merge confirmation**. Can't block anything
  (the merge already happened), but confirms what actually landed on
  `develop` is still green — catches drift from squash/merge-commit
  interactions or non-PR pushes the PR check never saw.

---

## 4. Workflow 2 — `release.yml`

**Status: committed to `develop`** (inert there — only triggers on
`pull_request`/`push` to `main`; won't actually run until Step 8's
`develop → main` PR exercises it). Two fixes applied beyond this draft,
both needed for the workflow to run at all on a fresh runner:

- `tag-and-release` needs `env: { GH_TOKEN: ${{ github.token }} }` on the
  tagging step — `gh release create` requires an authenticated `gh` CLI;
  the run-scoped `github.token` covers it with no secret to configure.
- `build-and-publish` runs on its own fresh runner (jobs don't share
  environment within a workflow run) and needs `actions/setup-python@v5`
  + `pip install build` before `python -m build` — neither Python nor
  the `build` package is present by default.

A fourth job, `deploy-docs`, was added later (§9.2) to publish the
MkDocs site to GitHub Pages on every release-triggering push — runs in
parallel with `tag-and-release`/`build-and-publish`, all three gated
only by `full-suite` and the `push`-event guard.

`pyproject.toml`'s `[project].version` is confirmed a static string
(`"0.6.0"` as of Module 7 work), not `setuptools_scm`-managed, so the
`tomllib`-based version extraction below works unmodified.

```yaml
name: Release Pipeline
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  full-suite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e .[dev,docs]
      - run: pytest --cov --cov-report=xml
      - uses: actions/upload-artifact@v4
        with: { name: coverage, path: coverage.xml }
      - run: mkdocs build

  tag-and-release:
    needs: full-suite
    if: github.event_name == 'push'        # never release from a PR preview
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@v4
      - run: |
          VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
          if git rev-parse "v$VERSION" >/dev/null 2>&1; then
            echo "Tag v$VERSION already exists — skipping (no version bump, no release)."
            exit 0
          fi
          git tag "v$VERSION"
          git push origin "v$VERSION"
          gh release create "v$VERSION" --generate-notes
        env:
          GH_TOKEN: ${{ github.token }}    # gh CLI needs auth; run-scoped, no secret

  build-and-publish:
    needs: tag-and-release
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions: { id-token: write }        # PyPI Trusted Publishing (OIDC)
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5      # fresh runner, needs its own Python
        with: { python-version: "3.x" }
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

**Two roles, same split as Workflow 1:**
- `pull_request → main` (i.e., the `develop → main` PR) = **the gate**.
  Runs `full-suite` only (tests, coverage, docs build). Required status
  check on `main`.
- `push → main` (fired automatically when that PR is merged — the merge
  button *is* the push event) = **ships it**. Runs `full-suite` again to
  confirm, then `tag-and-release`, then `build-and-publish`.

The `if: github.event_name == 'push'` guard on the last two jobs is the
load-bearing line — without it, every PR update would cut a release.
PyPI publishes can't be undone, so this check is the one that must never
be wrong.

**Idempotency:** the tag-existence check means a `develop → main` push that
didn't bump the version (e.g., docs-only change merged straight to main)
just runs tests/coverage/docs — no spurious release.

---

## 5. Branch Protection Rules

Configured in GitHub UI (Settings → Branches) or via `gh api`, not in YAML:

- **`develop`:** require the `smoke` check to pass before merge; require
  branches to be up to date before merging (forces re-check against
  current tip, shrinking the gap the `push`-triggered confirmation run
  exists to catch).
- **`main`:** require the `full-suite` check (from the `pull_request`
  trigger) to pass before merge; same up-to-date requirement; require a PR
  (no direct pushes) given `main` triggers publishing.

**Currently applied in this repo:**

| Setting | `main` |
|---|---|
| Pull request required to merge | Yes (`required_approving_review_count: 0`) |
| Required status checks | **`full-suite`**, `strict: true` — added after Scenario 3's PR gave GitHub a `full-suite` run to reference against `main` (a check can only be required once it has reported at least once on that branch) |
| Force pushes | Blocked |
| Branch deletion | Blocked |
| Admin enforcement | Off — admin can bypass in an emergency |

Only `full-suite` is required, not `tag-and-release`/`build-and-publish`
— those two only ever fire on the `push` event (guarded by
`if: github.event_name == 'push'`), so they never run on the
`pull_request` event a required check actually gates against; requiring
them would deadlock every PR.

**Currently applied in this repo — `develop`:**

Branch protection is now live on `develop`:
- Required status check: `smoke`, `strict: true` (branch must be up to
  date before merge)
- Required PR before merge: enabled, 0 required approvals
- `enforce_admins: false` — as owner, direct pushes from you still work;
  non-admin collaborators must go through a PR that only merges once
  `smoke` is green
- Force-pushes and branch deletion: both blocked

Verify anytime with `gh api repos/{owner}/{repo}/branches/develop/protection`,
or GitHub → Settings → Branches in the UI.

---

## 6. PyPI Trusted Publishing (OIDC)

Configured once on pypi.org: register the GitHub repo + workflow filename
as a trusted publisher for the package. No `PYPI_API_TOKEN` secret stored
anywhere. The workflow just needs `permissions: id-token: write` on the
publishing job — GitHub mints a short-lived OIDC token, PyPI verifies it
against the registered repo/workflow, publish proceeds. This is the modern
replacement for token-in-secrets upload from Module 6.

**Registered in this project (pending publisher, since `nowcastingcli`
hasn't been published to real PyPI yet):**

| Field | Value |
|---|---|
| PyPI Project Name | `nowcastingcli` |
| Owner | `juaquiro` |
| Repository | `CCPD-nowcastingcli` |
| Workflow filename | `release.yml` |
| Environment | *(none)* |

A pending publisher pre-authorizes only the *first* successful publish;
once that lands, PyPI converts it into the project's normal trusted
publisher automatically — no further action needed. Nothing to verify
from the CLI side until Step 10's actual publish attempt exercises it.

---

## 7. The Four Working Scenarios

### Scenario 1 — Normal Development
Small, low-risk changes. Work directly on `develop`, commit, `git push`.
No PR overhead for solo trivial changes.
- Fires: `push → develop` (smoke test, confirmation-only — nothing to
  gate since there's no PR).

**Verified end-to-end:** committed the `smoke` marker + `smoke-tests.yml`
itself directly to `develop`; `push → develop` fired as a confirmation-only
run (no PR involved, nothing to gate); confirmed green.

#### Notification methods for a `push → develop` result

Because a direct push has no PR to block, the only thing standing between
you and an unnoticed red run is whichever of these you're actually using.
Ranked most passive → most immediate:

1. **GitHub notifications (passive, default-on for most people).**
   If Actions notifications are enabled under
   `https://github.com/settings/notifications` → "Actions", a failed run
   on a branch you pushed to sends an email/web notification automatically.
   Worth confirming it's actually on — this is the safety net for when you
   forget to watch a run.

2. **A status badge in `README.md` (passive, always visible).**
   ```markdown
   ![Smoke Tests](https://github.com/<owner>/<repo>/actions/workflows/smoke-tests.yml/badge.svg?branch=develop)
   ```
   Reflects the most recently *completed* run on `develop` — good for
   at-a-glance repo health, not useful mid-push since it won't update
   until the run finishes and you refresh.

3. **Watch it live right after pushing (active, immediate).**
   `gh run watch` with no ID picks a run interactively, but called
   immediately after `git push` it can race GitHub's API (run not
   registered yet) and either error or pick up a stale prior run. The
   reliable version pins the run ID explicitly:
   ```bash
   git push origin develop
   sleep 2
   RUN_ID=$(gh run list --branch develop --workflow "Smoke Tests" \
     --limit 1 --json databaseId -q '.[0].databaseId')
   gh run watch "$RUN_ID" --exit-status
   ```
   `--exit-status` makes the command itself exit non-zero on failure, so
   it chains (`&& echo "safe to continue"`) or scripts cleanly. Worth
   wrapping in a shell function (e.g. `pushdev`) if pushing to `develop`
   directly is a regular habit.

4. **Pull the result explicitly, on demand.**
   ```bash
   gh run list --branch develop --workflow "Smoke Tests" --limit 1
   ```
   Same mechanism as watching, just without the wait — useful when
   checking back later rather than blocking on the push.

For a suite this fast (smoke run completes in well under a minute),
**option 3 is the everyday default** — no dependence on notification
settings, definitive pass/fail in-terminal within seconds. Option 1 is
the safety net for pushes made without watching. Option 2 is a nice-to-have
for repo visibility, not a substitute for 1/3. Option 4 is rarely needed
once 3 is habitual, since it answers the same question with no time
advantage.

Unlike a NAnt/Jenkins-style pipeline where a broken build interrupts you
with a red console by default, GitHub Actions has no equivalent
interruption mechanism for a solo dev outside of the above — the
`pushdev`-style wrapper in option 3 is what manufactures that
"don't proceed until green" discipline yourself.

### Scenario 2 — Feature Work
Branch from `develop` (`feature/xyz`), implement, open PR into `develop`.
- Fires: `pull_request → develop` (smoke test, **gate** — required check).
- On merge, fires: `push → develop` (confirmation run).

**Verified end-to-end:** `feature/smoke-humidity-check` branched from
`develop`, added a 4th smoke test (humidity range validation), opened PR
via `gh pr create --base develop`. `pull_request → develop` smoke check
ran as a required gate — confirmed via `gh pr checks --watch`; merge
blocked until green. On `gh pr merge --squash --delete-branch`, the
merge itself fired `push → develop` automatically as the post-merge
confirmation run. This is the first real (not simulated) confirmation
that branch protection's required-check gate actually blocks, not just
that it's configured.

> **`--delete-branch` caution:** it deletes the PR's *head* branch, not
> a fixed "feature branch" concept. Safe here because the head was the
> throwaway `feature/smoke-humidity-check`. In Scenario 3 (`develop → main`)
> the head branch *is* `develop` — never pass `--delete-branch` there, or
> the integration branch itself gets deleted. Check which branch is the
> head before reaching for this flag out of habit.

### Scenario 3 — Build / Release
PR from `develop` into `main`.
- Fires: `pull_request → main` (full suite + coverage + docs — **gate**,
  required check, no release/publish here).
- On merge, fires: `push → main` (full suite again, then tag, release,
  publish).

**In progress — first real run surfaced two stacked bugs, both fixed by
pushing to `develop` (which auto-updates the open PR's head and re-fires
the gate):**

1. **`mkdocs: command not found`** — `full-suite`'s install step
   (`pip install -e .[dev]`) only pulled the `dev` extra; MkDocs and its
   plugins live under a separate `docs` extra in this project's
   `pyproject.toml`, never installed by the workflow. Fix: install both
   extras, `pip install -e .[dev,docs]`.
2. **`Invalid requirement: 'docs]'`** — the first fix attempt had a space
   after the comma (`.[dev, docs]`). In an unquoted YAML `run:` line, the
   shell tokenizes on whitespace *before* pip ever sees the string, so
   `.[dev, docs]` splits into two separate arguments: `.[dev,` and
   `docs]`. Pip then tries to parse the second token, `docs]`, as its own
   requirement and fails on the stray bracket. Fix: no space after the
   comma — `.[dev,docs]`. General lesson: multi-extra pip specs in shell
   `run:` steps need to be written as a single unbroken token, same
   constraint as typing it directly at a shell prompt.

**Merged and verified — first real end-to-end execution of `release.yml`:**

Merge command used was `gh pr merge --squash` — **deliberately without**
`--delete-branch`. Worth flagging explicitly: in Scenario 2,
`--delete-branch` was correct because the PR's head branch was the
throwaway `feature/smoke-humidity-check`. Here, the PR's head branch is
`develop` itself — passing `--delete-branch` out of habit would have
deleted the integration branch. `--delete-branch` always targets the
head branch of the PR being merged, not a fixed "feature branch"
concept; check which branch that actually is before reaching for the
flag.

The merge fired `push → main`, watched live with `gh run watch`:

```
Select a workflow run * Release v0.6.1 (#18), Release Pipeline [main] 17s ago
  ✓ main Release Pipeline · 34413638740
  Triggered via push about 1 minute ago

  JOBS
  ✓ full-suite in 20s
  ✓ tag-and-release in 8s
  ✓ build-and-publish in 34s

  ANNOTATIONS
  ! Node.js 20 is deprecated. The following actions target Node.js 20 but
    are being forced to run on Node.js 24: actions/checkout@v4,
    actions/setup-python@v5, actions/upload-artifact@v4.
```

**Reading this output:**

- All three jobs ran this time (Scenario 3's whole point) because
  merging is itself a `push` event to `main` — unlike the PR's
  `pull_request` event, which only ever runs `full-suite` due to the
  `if: github.event_name == 'push'` guard on the other two jobs.
- **`full-suite` (20s):** checkout → `setup-python` → install
  `.[dev,docs]` → `pytest --cov` → upload coverage artifact →
  `mkdocs build`. Reran independently of the PR's earlier pass, now
  against the actual merged state of `main` — this is the confirmation
  role, same pattern as `smoke-tests.yml`'s `push` run on `develop`.
- **`tag-and-release` (8s):** read `version = "0.6.1"` out of
  `pyproject.toml` via `tomllib`, created and pushed tag `v0.6.1`, and
  called `gh release create` — first real exercise of the `GH_TOKEN`
  fix added earlier this module; it worked without issue.
- **`build-and-publish` (34s):** `python -m build` produced the
  sdist/wheel, then `pypa/gh-action-pypi-publish` authenticated via
  OIDC against the PyPI pending publisher registered earlier — first
  real activation of Trusted Publishing, no stored token anywhere in
  the chain. Succeeded on the first attempt, meaning the
  project/owner/repo/workflow-name match registered on pypi.org was
  exact.
- **Net result:** `v0.6.1` is now tagged, has a GitHub Release, and is
  published on PyPI — for real, irreversibly.

**The Node.js 20 deprecation annotation is informational, not a
failure.** `actions/checkout@v4`, `actions/setup-python@v5`, and
`actions/upload-artifact@v4` are built against the Node 20 runtime,
which GitHub is deprecating; GitHub is currently auto-forcing these
onto Node 24 behind the scenes, so nothing broke this run. Not urgent,
but worth tracking as a future maintenance item — bump to newer major
versions of these actions (e.g. `checkout@v5`) before Node 20 support
is fully withdrawn. Logged as a follow-up, not blocking.

### Scenario 4 — Hotfix
`main` is live at, e.g., v1.2.0. A critical bug surfaces in production, but
`develop` has unfinished/unreleasable work — you can't fix it by routing
through `develop`.
- Branch `hotfix/xyz` **from `main`**, not from `develop`.
- Fix, bump patch version on the hotfix branch, open PR `hotfix/xyz → main`.
- Fires: `pull_request → main` (same gate as Scenario 3).
- On merge, fires: `push → main` → new patch version tags/releases/publishes.
- **Required follow-up (manual discipline, not a workflow trigger):**
  merge or cherry-pick the same fix back into `develop` via a second PR
  (`hotfix/xyz → develop`, gated by the normal Scenario 2 check) — otherwise
  the bug silently reappears in the next regular release out of `develop`.

This is the one path that breaks the "everything flows `develop → main`"
assumption baked into Scenario 3 — `main` gets its own branch, and the
fix must be explicitly back-propagated.

#### Back-merge strategy (verified)

The hotfix branch (`hotfix/xyz`) is deleted immediately after merging into
`main` (`gh pr merge --squash --delete-branch` — head branch here *is*
the throwaway hotfix branch, so `--delete-branch` is correct, unlike the
Scenario 3 caution above). That means the back-merge into `develop`
can't reference the old branch directly; instead, branch fresh from
`develop`, merge `main`'s updated tip into it, and PR that back:

```bash
# 1. Fetch latest refs
git fetch origin main develop

# 2. Create a merge branch from develop
git checkout -b merge-main-into-develop origin/develop

# 3. Merge main into it (resolve conflicts if any show up —
#    expect the pyproject.toml version line to differ:
#    develop=0.6.1, main=0.6.2 after the hotfix; keep 0.6.2)
git merge origin/main

# 4. Push the merge branch
git push -u origin merge-main-into-develop

# 5. Open a PR into develop
gh pr create --base develop --head merge-main-into-develop \
  --title "Back-merge hotfix v0.6.2 from main into develop" \
  --body "Brings the hotfix and version bump back into develop so it isn't lost on the next release cut."

# 6. Wait for the smoke gate, then merge with a REAL MERGE COMMIT — not squash
gh pr merge --merge --delete-branch

# 7. Verify version landed
git show origin/develop:pyproject.toml | grep '^version'
```

**Why a real merge commit (`--merge`), not squash, specifically for this
PR:** step 3 already performs a genuine three-way merge, establishing
real ancestry between `develop` and `main` at this point in history.
Squashing at the PR-merge step (step 6) would discard exactly that
ancestry, collapsing it into a single flat commit with no recorded
merge-base. This matters more for a back-merge than for an ordinary
feature PR: if a future `develop → main` release needs to reconcile
these same lines again, Git's three-way merge relies on shared ancestry
to know the content is already accounted for. A squashed back-merge
falls back to pure content comparison instead — usually still works,
but loses the guarantee. Every other PR in this project (Scenarios 2
and 3, and the original hotfix→`main` PR) is squash-merged deliberately,
since those all have throwaway single-purpose branches with no ancestry
worth preserving; this back-merge is the one exception, precisely
because step 3's merge is the point of the exercise.

Note also `gh pr merge --merge` requires "Allow merge commits" enabled
as a strategy under repo Settings → General → Pull Requests — some
repos default to squash-only, which would surface as an error on the
merge command itself rather than a branch-protection failure.

---

## 8. What Is GitHub-Dependent vs. Tool-Standard

Useful to know explicitly before investing further, in case of a future
migration off GitHub (e.g., to GitLab CI, or back to a self-hosted
NAnt-driven pipeline):

| Component | GitHub-dependent? | Notes |
|---|---|---|
| `pytest -m smoke`, `pytest --cov`, `mkdocs build`, `python -m build` | **No** | Plain CLI tools, run identically anywhere, in any CI system or locally. This is the majority of the actual logic. |
| YAML workflow syntax (`on:`, `jobs:`, `steps:`, `needs:`, `if:`) | **Yes** | GitHub Actions-specific syntax. Porting to GitLab CI, or back to a NAnt `.build` file, means rewriting the orchestration layer, not the underlying commands. |
| `pull_request` / `push` event triggers | **Yes** | GitHub's event model. Conceptually portable (every CI system has equivalent PR/commit triggers) but the exact trigger config is GitHub-specific. |
| Branch protection rules (required status checks) | **Yes** | Configured via GitHub's UI/API, not in the repo at all — invisible to anyone reading just the YAML. Worth documenting here for that reason. |
| `actions/checkout`, `actions/setup-python`, `actions/upload-artifact` | **Yes** | GitHub Marketplace actions. Equivalent steps exist elsewhere (e.g., GitLab CI has built-in checkout, no marketplace-action needed) but these exact action names don't port. |
| `gh release create`, `gh` CLI | **Yes** | GitHub CLI, talks to GitHub's Releases API specifically. |
| `pypa/gh-action-pypi-publish` + OIDC Trusted Publishing config | **Partially** | The *action* is GitHub-specific, but PyPI's Trusted Publisher registration also supports GitLab CI/CD and other OIDC-capable systems — the OIDC *mechanism* is portable, this specific action wrapper is not. |
| GitHub Pages deployment (`mkdocs gh-deploy`, i.e. `deploy-docs` job) | **Yes** (hosting) | GitHub Pages as a hosting target is GitHub-specific; `mkdocs build` output itself is not — could deploy the same built `site/` directory anywhere. **Live in this repo** as of §9.2 — `mkdocs gh-deploy` pushes to `gh-pages` branch on every release push. |
| Secrets management (`permissions: id-token: write`) | **Yes** (syntax) | Concept (short-lived scoped credentials) is portable; the `permissions:` block syntax is GitHub Actions-specific. |

**Takeaway:** the actual engineering (what to test, what to build, what to
publish) lives in tool-standard commands and is fully portable. What's
GitHub-specific is almost entirely the *orchestration and enforcement*
layer (YAML trigger syntax, branch protection, marketplace actions) — this
is normal and expected; it's the same ratio you'd see migrating a NAnt
pipeline to a different build/CI system.

---

## 9. Final Verification Tasks

### 9.1 Clean-room install from real PyPI

Distinct from Module 6's TestPyPI-only walkthrough — this validates that
the actual published `nowcastingcli` package, as a stranger would
encounter it, installs and runs correctly with no dependency on this
machine's dev environment (no editable install, no local `PYTHONPATH`
propping anything up).

```bash
conda create -n pypi-verify python=3.11 -y
conda activate pypi-verify
pip install nowcastingcli
```

Entry point, from `pyproject.toml`:
```toml
[project.scripts]
nowcastingcli = "nowcastingcli.main:cli"
```

Verified:
```bash
which nowcastingcli         # confirms the console script resolved
nowcastingcli --help
pip show nowcastingcli      # Version: 0.6.2 — confirms latest release, not a stale cache
```

**Result: confirmed working.** `pip install nowcastingcli` in a fresh
conda env resolves `Version: 0.6.2` (the current tip after Scenario 4's
hotfix) and the `nowcastingcli` console script runs correctly — proof
the PyPI Trusted Publishing pipeline from §6 produces a genuinely
installable package, not just a successful-looking Action run.

### 9.2 Checking the deployed app's documentation

Two ways to read the docs, depending on whether you're working locally
or want the published, always-current version.

**Manual (local, always works, no deployment dependency):**
```bash
conda activate <your-dev-env>
pip install -e .[docs]
mkdocs serve
```
Serves at `http://127.0.0.1:8000` with live-reload on edits — useful
while actively writing docs, or as a fallback if Pages is ever down.

**Deployed (GitHub Pages, published automatically on release):**

Previously a gap (see §8's original table entry marking GitHub Pages
hosting as configured-but-unused) — closed by adding a `deploy-docs`
job to `release.yml`:

```yaml
  deploy-docs:
    needs: full-suite
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions: { contents: write }        # pushes to the gh-pages branch
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.x" }
      - run: pip install -e .[dev,docs]
      - run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
      - run: mkdocs gh-deploy --force --clean
```

Runs in parallel with `tag-and-release`/`build-and-publish` (all three
depend only on `full-suite`, not on each other) — docs publishing isn't
gated on a successful package release, and vice versa. `mkdocs gh-deploy`
builds the site and pushes it directly to a `gh-pages` branch in one
step (via `ghp-import` under the hood); the `git config` lines are
needed because the runner has no identity configured by default, and
`gh-deploy`'s push needs one to attribute the commit to.

One-time setup: GitHub Pages needs pointing at the `gh-pages` branch
once it exists (created automatically by the first `deploy-docs` run).
Either via UI (Settings → Pages → Source → "Deploy from a branch" →
`gh-pages` / `/(root)`), or via `gh api` after that first run:
```bash
gh api -X POST repos/{owner}/{repo}/pages \
  -f "source[branch]=gh-pages" -f "source[path]=/"
```

Once live, docs are reachable at `https://juaquiro.github.io/CCPD-nowcastingcli/`
— updates automatically on every `push → main` that carries a version
bump (or any release-triggering push), no manual redeploy step needed.

**Bugs surfaced and fixed while wiring this up — all worth knowing,
independent of the docs-deployment feature itself:**

1. **`tag-and-release`'s idempotency check was blind.** `actions/checkout@v4`
   defaults to a shallow clone (`fetch-depth: 1`, current commit only,
   no tag refs). The existing-tag check (`git rev-parse "v$VERSION"`)
   silently always failed to find tags that genuinely existed on the
   remote, so the script fell through to the create-and-push path and
   failed with a non-fast-forward rejection instead of skipping cleanly.
   Fixed with `fetch-depth: 0` on that job's checkout step (full history
   and tags).

2. **`build-and-publish` had no skip logic of its own.** Even after fix
   #1, a no-version-bump push to `main` would still attempt
   `build-and-publish`, which PyPI correctly rejects (duplicate
   version/filename) — a red job for an expected, harmless situation.
   Fixed by having `tag-and-release` emit a job output:
   ```yaml
     tag-and-release:
       outputs:
         released: ${{ steps.tag.outputs.released }}
       steps:
         - id: tag
           run: |
             ...
             echo "released=false" >> "$GITHUB_OUTPUT"   # skip path
             ...
             echo "released=true" >> "$GITHUB_OUTPUT"    # release path
   ```
   and `build-and-publish` reading it:
   ```yaml
     build-and-publish:
       if: github.event_name == 'push' && needs.tag-and-release.outputs.released == 'true'
   ```
   Verified with a real no-bump push (the PR that added this very fix):
   `tag-and-release` correctly skipped, and `build-and-publish` showed
   as **skipped** (0s, no steps), not failed.

3. **Squash-merged PRs into `main` create ancestry gaps.** After two
   consecutive `develop → main` PRs were both merged via
   `gh pr merge --squash`, a third PR from `develop` into `main` failed
   with `mergeStateStatus: DIRTY` / `mergeable: CONFLICTING` — despite
   `develop` and `main` having no real content disagreement. Squash
   merges create a brand-new commit on `main` with no shared ancestry
   to the original commit(s) still living on `develop`; two branches
   end up with equivalent content but divergent history for the same
   lines, which is enough to trip Git's merge algorithm on the next
   round. Resolved via `gh pr checkout <PR#> && git fetch origin main
   && git merge origin/main`, inspecting each conflict (confirmed
   textually equivalent, not a real disagreement) before resolving.
   **General lesson, consistent with the rationale documented in
   Scenario 4:** repeated squash-merging of the *same two long-lived
   branches* against each other, back and forth, erodes shared history
   over time — this is exactly why the Scenario 4 back-merge used a
   real merge commit (`--merge`) instead of squash. Squash is fine for
   throwaway feature/hotfix branches merging in one direction only;
   it's the wrong tool for two branches that repeatedly reconcile with
   each other.

### 9.3 Granting third-party collaborator access (contributor, non-admin)

`CCPD-nowcastingcli` is a **personal repo**, not under an organization —
this means access is a **direct collaborator invite**, not team-based
access. (The mechanism differs under an org: access there is normally
granted via team membership with a role assigned to the team, not to
individuals directly — not applicable here, but worth knowing which
case you're in before following any GitHub docs, since they cover both.)

**GitHub's role model, personal repos:**

| Role | Can do | Can't do |
|---|---|---|
| Read | Clone, view, open issues | Push, open PRs against the repo |
| Triage | Read + manage issues/PRs (labels, assign, close) | Push code |
| **Write** | Triage + push to non-protected branches, open PRs | Change branch protection, repo settings, manage collaborators |
| Maintain | Write + manage some repo settings (webhooks, some config) | Change branch protection, delete repo, billing |
| Admin | Everything | — |

**`Write` is the correct role for a contributor with no admin rights** —
matches "can open PRs and push to non-protected branches, cannot touch
branch protection or repo settings." Given `develop` and `main` both
already require PRs and passing status checks, a `Write` collaborator
is structurally prevented from bypassing CI/CD gates even though they
technically have push access — they simply can't push directly to
either protected branch, the same restriction the repo owner faces
without using the admin-bypass allowance. `Maintain` was considered
and rejected: it grants some settings access beyond what "no admin
rights" implies.

**Invite via `gh api`:**
```bash
gh api -X PUT repos/{owner}/{repo}/collaborators/{username} \
  -f permission=push
```
Note the naming inconsistency: the API's `permission` field uses `push`
as the value for the `Write` role shown in the UI. Full value set:
`pull` (Read), `triage` (Triage), `push` (Write), `maintain` (Maintain),
`admin` (Admin).

**Or via UI:** repo → Settings → Collaborators and teams → Add people →
search username → role: **Write**.

The invited person receives a notification/email and must accept before
access activates — it's pending, not immediate, either way.

**Verify:**
```bash
gh api repos/{owner}/{repo}/collaborators/{username}/permission
```
Expect `"permission": "write"`.

*(Documented as mechanism only this session — not actually exercised
against a real invite.)*

---

## Exercise Checklist

- [x] Branch `develop` off the existing `main`; set `develop` as the
      repository's default branch
- [x] Set branch protection on `main` (PR required, no force pushes, no
      deletions, admin bypass allowed)
- [x] Add `smoke` pytest marker + `smoke-tests.yml`
- [x] Walk Scenario 1 (direct push to `develop`, confirmation-only run)
      end-to-end, confirm green; document notification methods (§7)
- [x] Set branch protection on `develop` requiring the smoke check
- [x] Write `release.yml` with the `pull_request`/`push` split and the
      `if: github.event_name == 'push'` guard (committed to `develop`;
      inert there until a `develop → main` PR exercises it)
- [x] Add the `full-suite` check to `main`'s branch protection as a
      required status check — verified: `required_status_checks.contexts`
      returns `["full-suite"]`
- [x] Register PyPI Trusted Publisher for the repo + `release.yml`
      (pending publisher — activates on first successful publish)
- [x] Walk a real feature branch through Scenario 2 end-to-end
- [x] Walk a `develop → main` PR through Scenario 3 end-to-end, confirm
      auto-tag/release/publish fires correctly — `v0.6.1` tagged,
      released on GitHub, and published to PyPI via Trusted Publishing
- [x] (Optional, for understanding only) simulate Scenario 4 — branch a
      hotfix from `main`, confirm the back-merge-to-`develop` step —
      executed: hotfix merged into `main` (0.6.2), back-merge PR
      (`merge-main-into-develop`) run via real merge commit
      (`gh pr merge --merge --delete-branch`), `develop` now carries
      the hotfix and version 0.6.2

**Final Module 7 tasks (added at end of session, not yet started):**
- [x] Document install/run of the deployed app from real PyPI (`pip install
      nowcastingcli` from a clean env, confirm entry point runs) — distinct
      from Module 6's TestPyPI-only install walkthrough — see §9.1,
      confirmed working, resolved v0.6.2
- [x] Document how to check the deployed app's documentation — manual
      `mkdocs serve` fallback documented, `deploy-docs` job added to
      `release.yml`, verified live end-to-end (§9.2). Surfaced two
      real bugs along the way: `tag-and-release`'s idempotency check
      was blind under the default shallow checkout (fixed with
      `fetch-depth: 0`), and `build-and-publish` had no way to know
      when `tag-and-release` was a no-op (fixed with a `released` job
      output gating `build-and-publish`'s `if:` condition) — confirmed
      by a real no-version-bump push correctly skipping
      `build-and-publish` (0s, no steps) rather than failing on a
      PyPI duplicate-version rejection.
- [x] Document granting repo access to a third-party collaborator with
      contributor-level (non-admin) rights — see §9.3: `Write` role via
      direct collaborator invite (personal repo, not org/team-based);
      mechanism documented, not exercised against a real invite

**Follow-up (non-blocking, logged from Scenario 3's first real run):**
- [ ] Bump `actions/checkout`, `actions/setup-python`, and
      `actions/upload-artifact` to newer major versions ahead of GitHub's
      Node.js 20 runtime deprecation — currently auto-forced onto Node 24,
      not yet broken, but worth addressing before support is withdrawn
