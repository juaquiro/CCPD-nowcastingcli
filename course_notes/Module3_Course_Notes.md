# Module 3 — Claude Code: Refactoring, Test Generation, Code Explanation

> Part of: Claude Code for Python Developers: Hands-On Agentic Coding
> Repo: CCPD-nowcastingcli
> See also: [Course_Notes_Index.md](./Course_Notes_Index.md)

---

## Part 3 — Claude Code: Refactoring, Test Generation, Code Explanation

### What Claude Code Is

Claude Code is Anthropic's agentic CLI coding tool — a coding agent that lives
in your terminal, has full read/write access to your repo, can run commands,
and reasons about your codebase as a whole, not just a pasted snippet.

| This chat (Claude.ai) | Claude Code |
|---|---|
| You copy-paste code in | Reads your files directly |
| Stateless per message | Persistent session with repo awareness |
| You apply suggestions manually | Edits files and runs commands itself |
| Good for explaining concepts | Good for doing work inside your project |

The three core workflows covered in this module:

1. **Explaining** — "What does this formula actually do?"
2. **Refactoring** — "Restructure this without changing behavior"
3. **Generating tests** — "Write pytest tests for `physics.py`"

---

### Installation

Claude Code is a Node.js CLI tool — installed globally, not into your conda env:

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

If Node.js is not available or is too old (need ≥ 18):

```bash
conda install -c conda-forge nodejs
```

**Authentication:** on first run, `claude` opens a browser to authenticate via
your Anthropic account. API usage is billed separately from Claude.ai subscriptions.

---

### First Launch

Always launch from the project root — Claude Code reads the directory structure immediately:

```bash
cd ~/path/to/CCPD-nowcastingcli
claude
```

This drops into an interactive REPL. The interaction model is:
**conversation + file access + command execution**, all in one session.

---

### Use Case 1 — Code Explanation

Claude Code reads the actual file — you don't paste code. Example prompt:

```
Explain normalize_pressure() in physics.py. Walk through the math step by step,
relate each constant to its physical meaning, and state what approximations are
being made and when they break down.
```

It will break down the hypsometric equation: `0.0065` is the standard
tropospheric lapse rate (K/m); `-5.257` is the barometric exponent derived
from the ideal gas law + hydrostatic equation; validity domain is ~5000m
under standard atmosphere assumptions.

It can also cross-reference `models.py` to understand units flowing in — the
whole repo is its context, not just the file you mention.

---

### Use Case 2 — Refactoring

A concrete refactoring task for `physics.py`:

```
Refactor physics.py:
1. Extract the magic numbers (0.0065, 5.257, 273.15) as named module-level
   constants with comments explaining their physical meaning
2. Add a guard that raises ValueError if altitude_m > 5000 or pressure_hpa <= 0
3. Keep the function signature identical — no behavioral changes
4. Update the docstring to document the raised exception
Run the existing pytest suite after to confirm no regressions.
```

Claude Code will edit the file and run `pytest` itself. If tests fail, it
attempts to fix the issue before reporting back.

**The agentic loop:** edit → test → observe → fix. You watch; you don't drive.

The resulting `physics.py` after refactoring:

```python
# Physical constants
LAPSE_RATE = 0.0065          # Standard tropospheric lapse rate, K/m
BAROMETRIC_EXPONENT = 5.257  # Derived from ideal gas law + hydrostatic equation
KELVIN_OFFSET = 273.15       # °C to Kelvin conversion

def normalize_pressure(pressure_hpa: float, altitude_m: float, temperature_c: float) -> float:
    """
    Barometric formula: correct station pressure to QNH (sea-level equivalent).
    Uses the hypsometric approximation valid below ~5000m.

    Raises:
        ValueError: if pressure_hpa <= 0 or altitude_m > 5000.
    """
    if pressure_hpa <= 0:
        raise ValueError(f"pressure_hpa must be positive, got {pressure_hpa}")
    if altitude_m > 5000:
        raise ValueError(f"altitude_m exceeds valid range (>5000m): got {altitude_m}")

    return pressure_hpa * (
        1 - (LAPSE_RATE * altitude_m) / (temperature_c + LAPSE_RATE * altitude_m + KELVIN_OFFSET)
    ) ** -BAROMETRIC_EXPONENT
```

---

### Use Case 3 — Test Generation

After refactoring, prompt Claude Code to generate tests for the new validation:

```
Add tests to tests/test_physics.py for the new ValueError guards added in
physics.py. Follow the existing test style. Run pytest when done and confirm all pass.
```

Claude Code reads your existing `test_physics.py` to match the style
(naming conventions, `pytest.approx` usage, fixture patterns), appends the
new tests, and runs them.

**Critical caveat:** generated tests need review. Claude Code produces
syntactically correct, passing tests — but can write tautological ones
(testing that the function returns what it's hardcoded to return, not that
it constrains behavior). Ask yourself: *does this test fail if I break the
implementation in a plausible way?* If not, strengthen it.

---

### Slash Commands

In the Claude Code REPL, slash commands control the session:

| Command | Purpose |
|---|---|
| `/help` | List all commands |
| `/clear` | Clear conversation history (start fresh) |
| `/compact` | Summarize history to save context window |
| `/cost` | Show token usage for this session |
| `/review` | Request a code review of recent changes |
| `/undo` | Revert last file edit (uses git under the hood) |
| `/diff` | Show what's changed since session start |

`/undo` is the safety net — Claude Code edits real files. Your git history
is always there as a second line of defense.

---

### CLAUDE.md — Persistent Project Instructions

Drop `CLAUDE.md` at the repo root. Claude Code reads it at session start as
a persistent project-level system prompt — equivalent to a `Jenkinsfile`
that describes how the project works, but for the AI agent.

```markdown
# NowcastingCLI — Claude Code Instructions

## Environment
- conda env: `nowcastingcli` (Python 3.11)
- activate before running: `conda activate nowcastingcli`
- run tests: `pytest`
- run app: `nowcastingcli`

## Code Conventions
- Type hints on all public functions
- Docstrings on all public functions
- Named constants for magic numbers in physics.py
- No print() — use rich console for all output

## Architecture
- models.py: only dataclasses, no logic
- physics.py: pure functions only, no I/O
- heuristics.py: pure functions only, depends only on models.py
- display.py: all rich rendering, single Console() instance
- main.py: orchestration only, thin layer over the others

## Test Conventions
- pytest.approx for all float comparisons
- parametrize for table-driven tests
- test file mirrors source: test_physics.py tests physics.py
```

With `CLAUDE.md` in place, every session starts with your conventions loaded.
It won't suggest `print()` when you've told it to use `rich`; it won't create
flat test files when you've specified a mirrored structure.

---

### VS Code Integration

Install the "Claude Code" extension from the VS Code marketplace.

- `Ctrl+Shift+P` → "Claude Code: Open" — launches the REPL panel inside VS Code
- Highlight code and send it to Claude Code with surrounding file context
- File edits appear live in your editor as Claude Code makes them

The terminal workflow and the VS Code panel are the same underlying session.
Use whichever keeps you in flow.

---

### Exercise Checklist

- [ ] Install Claude Code: `npm install -g @anthropic-ai/claude-code`, verify launch from repo root
- [ ] Create `CLAUDE.md` with project conventions (adapt the template above)
- [ ] Run the **explanation** task: ask Claude Code to explain `normalize_pressure()` step by step
- [ ] Run the **refactoring** task: extract named constants + add validation, let it run pytest
- [ ] Run the **test generation** task: generate tests for the new validators
- [ ] Review generated tests critically — strengthen at least one that is too weak
- [ ] Commit: `git commit -m "refactor: extract constants and add validation to physics.py"`

---

---

---

