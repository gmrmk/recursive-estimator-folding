# D-AC: Algorithmic Contribution report extension (v2)

Date: 2026-08-08. Task D-AC of the reset plan.

## What this is

An EXTENSION of the frozen tangent-lineage prize report, not a competing
paper. `build_phase2_report_v2.py` is the builder extracted from the frozen
source release (`outputs/WHestBench-Phase-II-source-release.tar.gz`, member
`./build_phase2_report.py` — the tar is untouched) plus exactly three
additions:

1. **Section 6b "The non-Gaussianity wall: certified exact Gaussian-closure
   measurements"** — the M178 certified Phi2/Owen-T provider, the M179 exact
   full-covariance recurrence, and the T2 measurement (diagonal 7.175e-4,
   exact full-cov 9.606e-5, sampling ~3.09e-7; MC floor 1-2e-7), closing with
   the unifying design principle: exact Gaussian structure pays when
   subtracted (Section 3's control: -19.8094%) and fails when predicted
   (46x outside the competitive boundary).
2. **A Claude disclosure paragraph in Section 9**, matching the paper's
   existing AI-disclosure standard.
3. **References [11] (D. B. Owen 1956) and [12] (Tallis 1961)** — both DOIs
   resolved and title-verified via doi.org this session (the first Tallis DOI
   guess was wrong — tb00390.x is a road-traffic paper — and was corrected to
   tb00408.x, JRSS-B 23(1) 223-229, before commit).

Everything else in the builder is byte-identical to the frozen original.

## Rendered artifact

`WHestBench-Algorithmic-Prize-Report-DRAFT-v2.pdf` (6 pages; the original is
5). Rendered with reportlab 5.0.0 in a scratch venv; verified visually
page-by-page after render (section placement, table, disclosure, references).

## Filing procedure (unchanged from the original, using v2)

The banner and `--submission-id` mechanics are inherited: at filing time run

    python build_phase2_report_v2.py <out.pdf> --submission-id <GRADED_ID>

with exactly one successfully graded Phase-II submission ID. The report is
written around the tangent estimator, so the natural ID is the tangent
archive's (`D2E58DF6…8CF231`, which PASSED pinned v0.14 validate-package
locally on 2026-08-08). Per the D-PM adjudication: if the tangent archive
fails hosted grading, filing requires reworking the report around a graded
sampler ID — known risk, decided at the user-return runbook step.

## Evidence classes

Section 6b's numbers: numerical certificates (T2, observed 2026-08-08).
Provider/recurrence certificates: M178/M179 frozen artifacts (commits
3b590c66, f352762). DOI verification: observed (doi.org resolution this
session). The tangent-lineage numbers elsewhere in the report are the frozen
original's and were not re-derived here.
