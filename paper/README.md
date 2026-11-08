# Phase 2 paper (IEEE two-column)

`main.tex` + `refs.bib`. Tables and figures are **generated**, never typed by hand:

```bash
python experiments/reproduce.py report    # writes results/paper/* and copies them to paper/generated/
```

Build on Overleaf (upload this folder, including `generated/`) or locally with
`latexmk -pdf main.tex`. The output must be 8-10 pages.

Before submission:
1. `grep -n pending main.tex` must return nothing: every `\pending{...}` marks a sentence that still
   needs a number from `results/paper/README.md` or a failure-analysis file.
2. `grep -n CHECK refs.bib`: verify each marked DOI / arXiv id on the publisher page.
3. Run the Turnitin check (Deliverable C) on the final PDF.
