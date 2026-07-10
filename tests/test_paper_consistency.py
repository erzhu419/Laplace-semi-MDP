from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_paper_consistency import (  # noqa: E402
    duplicate_labels,
    extract_citations,
    extract_graphics,
    missing_references,
    title_from_cff,
    title_from_manuscript,
)


class PaperConsistencyTests(unittest.TestCase):
    def test_extracts_multikey_citations_and_graphics(self) -> None:
        text = r"\citep{alpha,beta}\citet[chap. 2]{gamma}\includegraphics[width=1.0]{fig/a.pdf}"
        self.assertEqual(extract_citations(text), ["alpha", "beta", "gamma"])
        self.assertEqual(extract_graphics(text), ["fig/a.pdf"])

    def test_detects_duplicate_and_missing_labels(self) -> None:
        text = r"\label{a}\label{a}\label{b}\ref{b}\eqref{c}"
        self.assertEqual(duplicate_labels(text), ["a"])
        self.assertEqual(missing_references(text), ["c"])

    def test_extracts_matching_titles(self) -> None:
        title = "Rate-Distortion Boundary Graphs"
        self.assertEqual(title_from_manuscript(rf"\title{{{title}}}"), title)
        self.assertEqual(title_from_cff(f'title: "{title}"\n'), title)


if __name__ == "__main__":
    unittest.main()
