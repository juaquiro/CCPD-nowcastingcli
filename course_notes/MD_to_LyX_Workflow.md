# Converting the Course Notes: Markdown → LaTeX → LyX

How `Course_Notes_Combined.lyx` (and its PDF) is produced from the seven
per-module Markdown files in this directory. Re-run this whenever the
Markdown sources change and the combined LyX/PDF needs to be regenerated.

## Pipeline

```
Module1_Course_Notes.md ─┐
Module2_Course_Notes.md  │
       ...                ├─▶ pandoc (md → LaTeX) ─▶ tex2lyx (LaTeX → LyX) ─▶ LyX / XeLaTeX ─▶ PDF
Module7_Course_Notes.md  │
Course_Notes_Index.md ───┘
```

There is no direct Markdown → LyX converter, and no direct Markdown →
single-PDF path that preserves LyX editability — hence the two-hop
conversion.

## Tools required

| Tool | Used for | Notes |
|---|---|---|
| [Pandoc](https://pandoc.org/) | Markdown → LaTeX | Not preinstalled on this machine — install first (see below) |
| LyX (this machine has 2.5) | `tex2lyx.exe` (LaTeX → LyX) and compiling the final document | `C:\Program Files\LyX 2.5\bin\` |
| A LaTeX distribution (MiKTeX, confirmed installed) | Actually compiling to PDF | Must provide `pdflatex`, **and** `xelatex` or `lualatex` |
| DejaVu Sans / DejaVu Sans Mono fonts | Rendering the Unicode characters used in the notes' code blocks and diagrams | Bundled with most MiKTeX/TeX Live installs; used automatically once non-TeX fonts are enabled (see Gotcha #1) |

Install Pandoc (pick one):

```powershell
winget install --id JohnMacFarlane.Pandoc
# or
choco install pandoc
```

Verify everything is on PATH:

```powershell
pandoc --version
& "C:\Program Files\LyX 2.5\bin\tex2lyx.exe" --version
```

## Step 1 — Concatenate the Markdown sources

Combine the module files in reading order. Do this in a scratch file, not
in the repo — the combined `.md` is a build intermediate, not a source of
truth (the per-module files remain authoritative).

```powershell
$modules = 1..7 | ForEach-Object { "course_notes\Module${_}_Course_Notes.md" }
Get-Content $modules -Raw | Set-Content combined.md -Encoding utf8
```

Prepend a YAML metadata block Pandoc will turn into the title page:

```yaml
---
title: "Claude Code for Python Developers --- Course Notes"
subtitle: "NowcastingCLI (Course Project 1) --- Modules 1-7, combined"
date: "2026-09-11"
---
```

## Step 2 — Markdown → LaTeX (Pandoc)

```powershell
pandoc combined.md -o combined.tex `
  --standalone `
  --toc `
  -V documentclass=book `
  -V colorlinks=true
```

- `--standalone` produces a full document (preamble + `\begin{document}`),
  not just a fragment — required for `tex2lyx` to parse it as a complete
  document.
- `--toc` gives the notes a table of contents; the index file already
  serves as a manual TOC, so this is optional.
- Section numbers were removed from the final document by adding a small
  `\ifPDFTeX ... \fi`-guarded preamble line in LyX afterward
  (`Document > Settings > LaTeX Preamble`) rather than a Pandoc flag —
  simplest to do as a post-edit in Step 3.

## Step 3 — LaTeX → LyX (`tex2lyx`)

```powershell
& "C:\Program Files\LyX 2.5\bin\tex2lyx.exe" combined.tex course_notes\Course_Notes_Combined.lyx
```

Open the result in LyX and spot-check the automatic conversion, in
particular:

- Fenced code blocks (` ```lang `) become `Verbatim` paragraph layouts —
  check the fence markers themselves didn't leak through as literal text
  (see Gotcha #2).
- Nested content under numbered list items (e.g. a code block followed by
  more prose under the same `Enumerate` item) sometimes converts into a
  `\begin_deeper` wrapper that doesn't round-trip cleanly back to LaTeX
  (see Gotcha #3).

## Step 4 — Enable Unicode-safe fonts

The course notes' code blocks and ASCII-art diagrams use characters well
outside Latin-1: box-drawing (`├── └── │ ─`), arrows (`→ ↑ ↓ ► ▼`), block
elements (`▁▂▃▄▅▆▇█`, from the real `SPARKLINE_CHARS` constant in
`nowcastingcli/display.py`), checkmarks (`✓`), em dashes, degree signs.

`tex2lyx` defaults to `\use_non_tex_fonts false`, which compiles with
plain `pdflatex` using the `lmodern` typewriter font — a font with no
glyphs past Latin-1. Every one of those characters will fail to compile,
one at a time, with an error like:

```
Uncodable character '▼' (code point 0x25bc)
```

Fix once, for all characters at once: in
`Document > Settings > Fonts`, check **"Use non-TeX fonts (XeTeX/LuaTeX)"**
— or edit the `.lyx` file directly:

```
\use_non_tex_fonts false     →     \use_non_tex_fonts true
```

This switches the compiler to XeTeX/LuaTeX and activates the document's
existing `\ifPDFTeX ... \else ... \fi` preamble branch, which loads
`fontspec`/`unicode-math` and the already-declared fallback font
`"DejaVu Sans Mono"` — full Unicode coverage, no per-character fixing.

## Step 5 — Compile and verify from the command line

Don't rely on opening the GUI and reading the dialog — compile headless
and grep the real LaTeX log, since LyX can still emit a PDF even after a
LaTeX error (nonstop mode plows through and produces output anyway):

```powershell
& "C:\Program Files\LyX 2.5\bin\LyX.exe" -batch -e pdf4 course_notes\Course_Notes_Combined.lyx
```

`pdf4` = XeTeX output format (`pdf5` = LuaTeX, `pdf2` = plain pdflatex —
don't use `pdf2` here, see Step 4). Then find and check the actual log
LyX wrote to a temp build directory (not next to the `.lyx` file):

```powershell
$log = Get-ChildItem "$env:TEMP\lyx_tmpdir.*\lyx_tmpbuf0\Course_Notes_Combined.log" |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1
Select-String -Path $log -Pattern '^! |Emergency stop|Extra \\end|endgroup' 
```

No matches = clean compile. The log also reports the final page count on
success (`Output written on Course_Notes_Combined.pdf (N pages)`).

## Gotchas hit doing this for real

1. **Any non-ASCII character in a `Verbatim`/code block fails to compile,
   one at a time, until `use_non_tex_fonts` is set** (Step 4). Don't
   chase these individually — fix the font setting first, then re-check.
   A quick way to find every offending character in one pass instead of
   discovering them one compile at a time:

   ```python
   import re
   begin_re = re.compile(r"^\\begin_layout\s+Verbatim")
   end_re = re.compile(r"^\\end_layout")
   in_verbatim = False
   with open("course_notes/Course_Notes_Combined.lyx", encoding="utf-8") as f:
       for i, line in enumerate(f, 1):
           s = line.rstrip("\n")
           if begin_re.match(s): in_verbatim = True; continue
           if end_re.match(s): in_verbatim = False; continue
           if in_verbatim and any(ord(c) > 127 for c in s):
               print(i, s)
   ```

2. **Leftover Markdown fence markers** (```` ```bash ````, ```` ``` ````)
   can survive the `pandoc`/`tex2lyx` round-trip as literal text inside a
   `Verbatim` layout, sometimes carrying an invisible zero-width space
   (U+200B) picked up from the Markdown source. LyX reports this the same
   way as any other uncodable character. Search for and delete the
   redundant fence-marker `Verbatim` paragraphs — the content is already
   correctly wrapped without them.

3. **`\begin_deeper` around mixed `Standard`/`Verbatim` paragraphs breaks
   the LaTeX export.** When a numbered list item has a code block,
   followed by more prose, followed by another code block (still the same
   item), `tex2lyx` may wrap the continuation in `\begin_deeper` /
   `\end_deeper`. On export this can produce an unbalanced
   `\end{verbatim}` (`LaTeX Error: \begin{document} ended by
   \end{verbatim}` / `Extra \endgroup`). Fix: remove the
   `\begin_deeper`/`\end_deeper` pair and leave the paragraphs at the same
   nesting level as the rest of the list item — this is how every other
   multi-block list item in these notes is structured, and it round-trips
   cleanly.

## Regenerating after Markdown changes

Repeat Steps 1–3 to get a fresh `.lyx`, then re-check Gotchas #1–#3 before
compiling — `tex2lyx` doesn't remember the fixes applied to a previous
conversion; they need to be redone (or scripted) each time the Markdown
sources change enough to require a fresh combined document.
