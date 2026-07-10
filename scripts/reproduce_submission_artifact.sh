#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

python3 experiments/run_fair_budget_frontier.py
python3 experiments/run_theorem_experiment_bridge.py
python3 experiments/run_submission_main_table.py
python3 experiments/plot_p0_submission_figures.py
python3 experiments/plot_operator_pipeline_figure.py
python3 scripts/check_paper_consistency.py

if command -v pdflatex >/dev/null 2>&1 && command -v bibtex >/dev/null 2>&1; then
  (
    cd paper
    pdflatex -interaction=nonstopmode manuscript.tex >/dev/null
    bibtex manuscript >/dev/null
    pdflatex -interaction=nonstopmode manuscript.tex >/dev/null
    pdflatex -interaction=nonstopmode manuscript.tex >/dev/null
  )
else
  printf '%s\n' "pdflatex/bibtex unavailable; regenerated tables and figures only."
fi

printf '%s\n' "Submission artifact regenerated."
