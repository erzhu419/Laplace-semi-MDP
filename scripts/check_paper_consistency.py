#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence


CITATION_PATTERN = re.compile(
    r"\\cite(?:p|t|alp|alt|author|year|yearpar)?(?:\[[^\]]*\]){0,2}\{([^}]+)\}"
)
GRAPHIC_PATTERN = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
LABEL_PATTERN = re.compile(r"\\label\{([^}]+)\}")
REF_PATTERN = re.compile(r"\\(?:ref|eqref|autoref)\{([^}]+)\}")
BIB_KEY_PATTERN = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)


@dataclass(frozen=True)
class ClaimSpec:
    label: str
    csv_path: Path
    match: Mapping[str, str]
    field: str
    expected: float
    tolerance: float
    manuscript_token: str


def extract_citations(text: str) -> List[str]:
    keys: List[str] = []
    for group in CITATION_PATTERN.findall(text):
        keys.extend(key.strip() for key in group.split(",") if key.strip())
    return keys


def extract_graphics(text: str) -> List[str]:
    return [match.strip() for match in GRAPHIC_PATTERN.findall(text)]


def duplicate_labels(text: str) -> List[str]:
    counts = Counter(LABEL_PATTERN.findall(text))
    return sorted(label for label, count in counts.items() if count > 1)


def missing_references(text: str) -> List[str]:
    labels = set(LABEL_PATTERN.findall(text))
    return sorted(set(REF_PATTERN.findall(text)) - labels)


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def matched_row(path: Path, match: Mapping[str, str]) -> Mapping[str, str]:
    rows = [
        row
        for row in read_rows(path)
        if all(str(row.get(key, "")) == str(value) for key, value in match.items())
    ]
    if len(rows) != 1:
        raise ValueError(f"Expected one row in {path} matching {dict(match)}, found {len(rows)}.")
    return rows[0]


def resolve_graphic(manuscript_path: Path, graphic: str) -> Path | None:
    base = manuscript_path.parent / graphic
    if base.suffix:
        return base.resolve() if base.exists() else None
    for suffix in (".pdf", ".png", ".svg", ".jpg", ".jpeg"):
        candidate = base.with_suffix(suffix)
        if candidate.exists():
            return candidate.resolve()
    return None


def title_from_manuscript(text: str) -> str:
    match = re.search(r"\\title\{([^}]+)\}", text)
    return match.group(1).strip() if match else ""


def title_from_cff(text: str) -> str:
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def default_claims(root: Path) -> List[ClaimSpec]:
    one_shot = root / "experiments/output/submission_main_table/one_shot_operator_summary.csv"
    runtime = root / "experiments/output/submission_main_table/runtime_by_boundary_selector.csv"
    pairing = root / "experiments/output/boundary_constraint_pairing/paired_summary.csv"
    return [
        ClaimSpec(
            "classic selection speedup vs iterative surrogate",
            one_shot,
            {"source": "one_shot_rd_operator", "method": "one_shot_rd_t0p15"},
            "median_selection_speedup_vs_iterative",
            40.06223179680868,
            1e-9,
            r"$40.1\times$",
        ),
        ClaimSpec(
            "classic full graph speedup vs iterative surrogate",
            one_shot,
            {"source": "one_shot_rd_operator", "method": "one_shot_rd_t0p15"},
            "median_total_speedup_vs_iterative",
            7.771528039228121,
            1e-9,
            r"$7.77\times$",
        ),
        ClaimSpec(
            "classic selection speedup vs exact search",
            one_shot,
            {"source": "one_shot_rd_operator", "method": "one_shot_rd_t0p15"},
            "median_selection_speedup_vs_exact_search",
            157.24872488876508,
            1e-9,
            r"$157\times$",
        ),
        ClaimSpec(
            "classic full graph speedup vs exact search",
            one_shot,
            {"source": "one_shot_rd_operator", "method": "one_shot_rd_t0p15"},
            "median_total_speedup_vs_exact_search",
            22.86472609140089,
            1e-9,
            r"$22.9\times$",
        ),
        ClaimSpec(
            "held-out random extraction speedup",
            one_shot,
            {"source": "one_shot_rd_operator_random_reference", "method": "one_shot_rd_t0p15"},
            "median_selection_speedup_vs_iterative",
            369.51494874470774,
            1e-9,
            r"$369.5\times$",
        ),
        ClaimSpec(
            "held-out random full graph speedup",
            one_shot,
            {"source": "one_shot_rd_operator_random_reference", "method": "one_shot_rd_t0p15"},
            "median_total_speedup_vs_iterative",
            12.941598709270796,
            1e-9,
            r"$12.94\times$",
        ),
        ClaimSpec(
            "XL state compression",
            one_shot,
            {"source": "one_shot_rd_operator_xl_end_to_end", "method": "one_shot_rd_t0p15"},
            "median_state_compression",
            192.0,
            1e-12,
            r"$192\times$",
        ),
        ClaimSpec(
            "XL total speedup vs sparse VI",
            one_shot,
            {"source": "one_shot_rd_operator_xl_end_to_end", "method": "one_shot_rd_t0p15"},
            "median_total_speedup_vs_sparse_vi",
            0.0038629720190769294,
            1e-12,
            r"$0.00386\times$",
        ),
        ClaimSpec(
            "iterative RD graph planning speedup",
            runtime,
            {"boundary_selector": "graph_rd_surrogate_joint"},
            "strong_planner_median_planning_speedup",
            29.58248878740116,
            1e-9,
            r"$29.6\times$",
        ),
        ClaimSpec(
            "iterative RD single-task total speedup",
            runtime,
            {"boundary_selector": "graph_rd_surrogate_joint"},
            "strong_planner_median_total_speedup",
            0.0011552957727785707,
            1e-12,
            r"$0.00116\times$",
        ),
        ClaimSpec(
            "reranker/reference exact McNemar p-value",
            pairing,
            {},
            "exact_mcnemar_pvalue",
            0.06391465663909912,
            1e-12,
            r"$p=0.0639$",
        ),
    ]


def check_claims(
    root: Path,
    manuscript_text: str,
    claims: Iterable[ClaimSpec],
) -> tuple[List[Dict[str, object]], List[str]]:
    report: List[Dict[str, object]] = []
    errors: List[str] = []
    for spec in claims:
        try:
            row = matched_row(spec.csv_path, spec.match)
            actual = float(row[spec.field])
        except (FileNotFoundError, KeyError, ValueError) as exc:
            errors.append(f"{spec.label}: {exc}")
            continue
        source_matches = math.isclose(
            actual,
            spec.expected,
            rel_tol=0.0,
            abs_tol=spec.tolerance,
        )
        token_present = spec.manuscript_token in manuscript_text
        if not source_matches:
            errors.append(
                f"{spec.label}: source value {actual} drifted from registered {spec.expected}."
            )
        if not token_present:
            errors.append(
                f"{spec.label}: manuscript token {spec.manuscript_token!r} is missing."
            )
        report.append(
            {
                "claim": spec.label,
                "source": str(spec.csv_path.relative_to(root)),
                "field": spec.field,
                "actual": actual,
                "source_match": source_matches,
                "manuscript_token": spec.manuscript_token,
                "token_present": token_present,
            }
        )
    return report, errors


def markdown_table(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check paper citations, assets, labels, and numeric claims.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manuscript", type=Path, default=Path("paper/manuscript.tex"))
    parser.add_argument("--bib", type=Path, default=Path("paper/references.bib"))
    parser.add_argument("--citation-cff", type=Path, default=Path("CITATION.cff"))
    parser.add_argument("--out", type=Path, default=Path("paper/consistency_report.md"))
    args = parser.parse_args()
    root = args.root.resolve()
    manuscript_path = (root / args.manuscript).resolve()
    bib_path = (root / args.bib).resolve()
    cff_path = (root / args.citation_cff).resolve()
    out_path = (root / args.out).resolve()

    manuscript_text = manuscript_path.read_text(encoding="utf-8")
    bib_text = bib_path.read_text(encoding="utf-8")
    cff_text = cff_path.read_text(encoding="utf-8")
    errors: List[str] = []
    warnings: List[str] = []

    citations = extract_citations(manuscript_text)
    bib_keys = BIB_KEY_PATTERN.findall(bib_text)
    duplicate_bib = sorted(key for key, count in Counter(bib_keys).items() if count > 1)
    missing_citations = sorted(set(citations) - set(bib_keys))
    unused_bib = sorted(set(bib_keys) - set(citations))
    if duplicate_bib:
        errors.append(f"Duplicate BibTeX keys: {', '.join(duplicate_bib)}")
    if missing_citations:
        errors.append(f"Undefined citation keys: {', '.join(missing_citations)}")
    if unused_bib:
        warnings.append(f"Uncited BibTeX keys: {', '.join(unused_bib)}")

    graphics = extract_graphics(manuscript_text)
    missing_graphics = [graphic for graphic in graphics if resolve_graphic(manuscript_path, graphic) is None]
    if missing_graphics:
        errors.append(f"Missing figure assets: {', '.join(missing_graphics)}")

    duplicates = duplicate_labels(manuscript_text)
    missing_refs = missing_references(manuscript_text)
    if duplicates:
        errors.append(f"Duplicate LaTeX labels: {', '.join(duplicates)}")
    if missing_refs:
        errors.append(f"Undefined LaTeX references: {', '.join(missing_refs)}")

    manuscript_title = title_from_manuscript(manuscript_text)
    cff_title = title_from_cff(cff_text)
    if manuscript_title != cff_title:
        errors.append(
            f"CITATION title mismatch: manuscript={manuscript_title!r}, CITATION.cff={cff_title!r}."
        )
    for forbidden in ("preregistered", "student beats teacher", "[Evidence needed"):
        if forbidden.lower() in manuscript_text.lower():
            errors.append(f"Forbidden or unresolved manuscript phrase: {forbidden!r}")

    claim_rows, claim_errors = check_claims(root, manuscript_text, default_claims(root))
    errors.extend(claim_errors)
    status = "PASS" if not errors else "FAIL"
    report_lines = [
        "# Paper Consistency Report",
        "",
        f"Status: **{status}**",
        "",
        f"- citations used / BibTeX entries: `{len(set(citations))}/{len(bib_keys)}`",
        f"- figure assets resolved: `{len(graphics) - len(missing_graphics)}/{len(graphics)}`",
        f"- LaTeX labels / references: `{len(LABEL_PATTERN.findall(manuscript_text))}/{len(REF_PATTERN.findall(manuscript_text))}`",
        f"- registered numeric claims checked: `{len(claim_rows)}`",
        "",
        "## Numeric Claims",
        "",
        markdown_table(
            claim_rows,
            ["claim", "source", "field", "actual", "source_match", "manuscript_token", "token_present"],
        ),
        "",
        "## Errors",
        "",
        *(f"- {error}" for error in errors),
        *( ["- none"] if not errors else [] ),
        "",
        "## Warnings",
        "",
        *(f"- {warning}" for warning in warnings),
        *( ["- none"] if not warnings else [] ),
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(report_lines), encoding="utf-8")
    if errors:
        raise SystemExit("\n".join(errors))


if __name__ == "__main__":
    main()
