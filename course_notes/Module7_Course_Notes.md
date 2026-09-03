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
      - run: pip install -e .[dev]
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

  build-and-publish:
    needs: tag-and-release
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions: { id-token: write }        # PyPI Trusted Publishing (OIDC)
    steps:
      - uses: actions/checkout@v4
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

**Currently applied in this repo** (status-check requirements above are the
target once `smoke-tests.yml`/`release.yml` exist and report check runs —
not yet added; see Exercise Checklist):

| Setting | `main` |
|---|---|
| Pull request required to merge | Yes (`required_approving_review_count: 0`) |
| Required status checks | Not yet configured (no workflow files yet) |
| Force pushes | Blocked |
| Branch deletion | Blocked |
| Admin enforcement | Off — admin can bypass in an emergency |

---

## 6. PyPI Trusted Publishing (OIDC)

Configured once on pypi.org: register the GitHub repo + workflow filename
as a trusted publisher for the package. No `PYPI_API_TOKEN` secret stored
anywhere. The workflow just needs `permissions: id-token: write` on the
publishing job — GitHub mints a short-lived OIDC token, PyPI verifies it
against the registered repo/workflow, publish proceeds. This is the modern
replacement for token-in-secrets upload from Module 6.

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

### Scenario 3 — Build / Release
PR from `develop` into `main`.
- Fires: `pull_request → main` (full suite + coverage + docs — **gate**,
  required check, no release/publish here).
- On merge, fires: `push → main` (full suite again, then tag, release,
  publish).

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
| GitHub Pages deployment (`peaceiris/actions-gh-pages` or `mkdocs gh-deploy`) | **Yes** (hosting) | GitHub Pages as a hosting target is GitHub-specific; `mkdocs build` output itself is not — could deploy the same built `site/` directory anywhere. |
| Secrets management (`permissions: id-token: write`) | **Yes** (syntax) | Concept (short-lived scoped credentials) is portable; the `permissions:` block syntax is GitHub Actions-specific. |

**Takeaway:** the actual engineering (what to test, what to build, what to
publish) lives in tool-standard commands and is fully portable. What's
GitHub-specific is almost entirely the *orchestration and enforcement*
layer (YAML trigger syntax, branch protection, marketplace actions) — this
is normal and expected; it's the same ratio you'd see migrating a NAnt
pipeline to a different build/CI system.

---

## Exercise Checklist

- [x] Branch `develop` off the existing `main`; set `develop` as the
      repository's default branch
- [x] Set branch protection on `main` (PR required, no force pushes, no
      deletions, admin bypass allowed)
- [x] Add `smoke` pytest marker + `smoke-tests.yml`
- [x] Walk Scenario 1 (direct push to `develop`, confirmation-only run)
      end-to-end, confirm green; document notification methods (§7)
- [ ] Set branch protection on `develop` requiring the smoke check
- [ ] Write `release.yml` with the `pull_request`/`push` split and the
      `if: github.event_name == 'push'` guard
- [ ] Add the `full-suite` check to `main`'s branch protection as a
      required status check (protection rule itself already exists)
- [ ] Register PyPI Trusted Publisher for the repo + `release.yml`
- [ ] Walk a real feature branch through Scenario 2 end-to-end
- [ ] Walk a `develop → main` PR through Scenario 3 end-to-end, confirm
      auto-tag/release/publish fires correctly
- [ ] (Optional, for understanding only) simulate Scenario 4 — branch a
      hotfix from `main`, confirm the back-merge-to-`develop` step
