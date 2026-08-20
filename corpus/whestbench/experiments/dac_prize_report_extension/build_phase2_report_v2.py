"""Build the WHestBench Algorithmic Prize technical report draft."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#14213D")
BLUE = colors.HexColor("#1D5D9B")
TEAL = colors.HexColor("#188977")
PALE = colors.HexColor("#EAF2F8")
GREEN = colors.HexColor("#E8F5EE")
AMBER = colors.HexColor("#FFF3D6")
RED = colors.HexColor("#B42318")
MUTED = colors.HexColor("#536273")
GRID = colors.HexColor("#C9D3DF")


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubtitleCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=MUTED,
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1Custom",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=NAVY,
            spaceBefore=12,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=BLUE,
            spaceBefore=9,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.2,
            textColor=colors.HexColor("#1F2933"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=10.5,
            textColor=MUTED,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCellCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=6.8,
            leading=8.6,
            textColor=colors.HexColor("#1F2933"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeCustom",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=7.7,
            leading=10.2,
            leftIndent=10,
            rightIndent=10,
            borderColor=GRID,
            borderWidth=0.5,
            borderPadding=6,
            backColor=colors.HexColor("#F7F9FB"),
            spaceBefore=4,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BannerCustom",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9.2,
            leading=12,
            textColor=RED,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CalloutCustom",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=NAVY,
            alignment=TA_CENTER,
        )
    )
    return styles


def header_footer(canvas, document, is_draft: bool):
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.4)
    canvas.line(0.62 * inch, height - 0.47 * inch, width - 0.62 * inch, height - 0.47 * inch)
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(MUTED)
    label = "WHestBench Phase II - Algorithmic Prize report draft" if is_draft else "WHestBench Phase II - Algorithmic Prize report"
    canvas.drawString(0.62 * inch, height - 0.36 * inch, label)
    canvas.drawRightString(width - 0.62 * inch, 0.36 * inch, f"Page {document.page}")
    canvas.restoreState()


def para(styles, text, style="BodyCustom"):
    return Paragraph(text, styles[style])


def bullet(styles, text):
    return Paragraph(f"- {text}", styles["BodyCustom"])


def styled_table(data, widths, header=True, font_size=7.5, alignments=None):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.45, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), font_size + 2.2),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    if alignments:
        for column, alignment in enumerate(alignments):
            commands.append(("ALIGN", (column, 1 if header else 0), (column, -1), alignment))
    table.setStyle(TableStyle(commands))
    return table


def build(output: Path, submission_id: str | None = None) -> None:
    if submission_id is not None:
        submission_id = submission_id.strip()
        if not submission_id or any(character in submission_id for character in "\r\n<>"):
            raise ValueError("submission ID must be one non-empty plain-text line")
    is_draft = submission_id is None
    styles = make_styles()
    document = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        leftMargin=0.62 * inch,
        rightMargin=0.62 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.58 * inch,
        title="Moment-Tangent Control for Sparse Randomized-QMC Mean Estimation",
        author="gmrmk with OpenAI Codex assistance",
        subject=f"ARC WHestBench 2026 Algorithmic Prize technical report{' draft' if is_draft else ''}",
    )
    story = []

    banner_text = (
        "DRAFT - INSERT EXACTLY ONE SUCCESSFULLY GRADED PHASE-II SUBMISSION ID BEFORE PRIZE FILING"
        if is_draft
        else f"SUCCESSFULLY GRADED PHASE-II SUBMISSION ID: {html.escape(submission_id)}"
    )
    banner = Table(
        [[para(styles, banner_text, "BannerCustom")]],
        colWidths=[7.12 * inch],
    )
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), AMBER),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D97706")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend(
        [
            banner,
            Spacer(1, 0.20 * inch),
            para(styles, "Moment-Tangent Control for Sparse Randomized-QMC Mean Estimation of Deep ReLU Networks", "TitleCustom"),
            para(
                styles,
            f"Frozen Phase-II candidate and Algorithmic Contribution Prize report{' draft' if is_draft else ''}<br/>"
                "Team: gmrmk | Frozen: 2026-08-03 | Evaluator: WHestBench 0.14.0 / FlopScope 0.10.0",
                "SubtitleCustom",
            ),
            HRFlowable(width="100%", thickness=1.3, color=TEAL, spaceAfter=12),
        ]
    )

    outcome = Table(
        [
            [para(styles, "Primary development result", "SmallCustom"), para(styles, "Frozen lockbox result", "SmallCustom"), para(styles, "Artifact result", "SmallCustom")],
            [para(styles, "17.1599% nested OOF raw-MSE reduction", "CalloutCustom"), para(styles, "9.91146e-7 raw MSE on untouched n=200", "CalloutCustom"), para(styles, "10/10 cold starts; 0 isolated failures", "CalloutCustom")],
        ],
        colWidths=[2.37 * inch] * 3,
    )
    outcome.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, GRID),
                ("BACKGROUND", (0, 0), (-1, 0), PALE),
                ("BACKGROUND", (0, 1), (-1, 1), GREEN),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend([outcome, Spacer(1, 10)])

    story.append(para(styles, "Executive conclusion", "H1Custom"))
    story.append(
        para(
            styles,
            "The promoted estimator is a rules-compliant, fully offline randomized-QMC algorithm for the width-256, depth-32 bias-free ReLU networks used by WHestBench Phase II. Its material innovation is a fixed moment-tangent control: first-layer empirical mean and variance residuals are propagated through a deterministic mean-field response map and subtracted from the final randomized-QMC estimate with development-frozen coefficient <b>lambda = 0.9807112198896164</b>.",
        )
    )
    story.append(
        para(
            styles,
            "The control reduced nested whole-network out-of-fold raw MSE by 17.1599% on 800 public development networks. The effect repeated across three independent setup seeds and improved the official 20-network adjusted score by 19.8094% with zero failures. After source and archive freeze, one untouched 200-network lockbox produced 9.91146e-7 raw MSE and passed every predeclared mean, tail, and finiteness gate. No lockbox-driven retuning followed.",
        )
    )
    story.append(
        para(
            styles,
            "This report does not claim a guaranteed prize or private-rerun score. The complete estimator is deliberately described as biased because its pilot-rescued sparsification can omit active upstream paths. The moment-tangent control is centered under an ideal continuous-Gaussian law, with finite-grid and floating-point qualifications.",
        )
    )

    story.append(para(styles, "1. Challenge objective and accounting", "H1Custom"))
    story.append(
        para(
            styles,
            "For M networks, WHestBench ranks the mean final-layer error after a compute multiplier. With budget B = 272e9 FLOPs and effective compute C_m including charged residual wall time:",
        )
    )
    story.append(
        para(
            styles,
            "score = (1/M) sum_m MSE_m * max(0.1, C_m / B)",
            "CodeCustom",
        )
    )
    story.append(
        para(
            styles,
            "All MLP-dependent numerical work in the submitted source uses FlopScope arrays or flops.stats. The estimator does not call an API, network service, subprocess, raw NumPy prediction path, grader state, or an accounting bypass. Setup reads one packaged asset from SetupContext.submission_dir and randomizes it only with the official setup seed.",
        )
    )

    story.append(para(styles, "2. Frozen estimator", "H1Custom"))
    pipeline = Table(
        [[
            para(styles, "14,000-point<br/>Sobol prefix", "SmallCustom"),
            para(styles, "digital shift +<br/>Box-Muller", "SmallCustom"),
            para(styles, "antipodes +<br/>radial weights", "SmallCustom"),
            para(styles, "cold-screen +<br/>pilot rescue", "SmallCustom"),
            para(styles, "moment tangent<br/>lambda=0.980711", "SmallCustom"),
        ]],
        colWidths=[1.42 * inch] * 5,
    )
    pipeline.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.7, BLUE),
                ("INNERGRID", (0, 0), (-1, -1), 0.7, colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.extend([pipeline, Spacer(1, 6)])
    story.append(para(styles, "Randomized low-discrepancy paths", "H2Custom"))
    story.append(
        para(
            styles,
            "The packaged asset contains 32,768 points in 256 dimensions from a fixed LMS+shift-scrambled Sobol construction. Prediction uses its first 14,000 rows. Setup applies an independent uint32 XOR shift from the official seed, maps midpoints to approximate standard normals with Box-Muller, and propagates each path with its antipode. The final submission therefore evaluates 28,000 paths before pruning.",
        )
    )
    story.append(para(styles, "Exact spectral radial control", "H2Custom"))
    story.append(
        para(
            styles,
            "A bias-free ReLU network is positively one-homogeneous: f(r u) = r f(u). For X = R U with R chi-distributed in dimension 256, the following final-layer weight preserves the ideal Gaussian target while changing variance:",
        )
    )
    story.append(
        para(
            styles,
            "w(R) = 1 - (2600/537689)(R^2 - 257) + (3/537689)(R^4 - 66563)",
            "CodeCustom",
        )
    )
    story.append(
        para(
            styles,
            "The identities E[R(R^2-257)] = 0 and E[R(R^4-66563)] = 0 make this an exact ideal-law radial control for every final neuron. A separate spherical-radial conditioning mutation was tested at full scale and rejected because its 0.1859% mean raw gain was not statistically stable.",
        )
    )
    story.append(para(styles, "Pilot-rescued sparsification", "H2Custom"))
    story.append(
        para(
            styles,
            "A diagonal-Gaussian analytic pass computes layer means, variances, standardized preactivation alpha, and firing probabilities. Neurons with alpha below -2 are provisionally cold. A 256-antipodal-pair pilot rescues any such neuron observed firing. Dense propagation continues only through the active set; analytically cold final outputs are filled by mean propagation.",
        )
    )
    story.append(
        para(
            styles,
            "This is an empirical rescue heuristic, not a proof of zero contribution. A neuron can evade the pilot while carrying an omitted upstream path. That bias is retained explicitly in every claim and artifact.",
        )
    )

    story.append(para(styles, "3. Moment-tangent control", "H1Custom"))
    story.append(
        para(
            styles,
            "For first-layer neuron j with weight norm sigma_j and analytic mean mu_j = sigma_j / sqrt(2 pi), antithetic paths provide empirical first and second moments. Define centered residuals:",
        )
    )
    story.append(
        para(
            styles,
            "r_mu = mean(h_1) - mu<br/>r_v = [mean(h_1^2) - sigma^2/2] - 2 mu r_mu",
            "CodeCustom",
        )
    )
    story.append(
        para(
            styles,
            "The ideal Gaussian expectations of these residuals are zero. A deterministic response approximation propagates them through each later layer. For preactivation perturbations delta_m and delta_v at standardized mean alpha with analytic ReLU mean mu_plus:",
        )
    )
    story.append(
        para(
            styles,
            "delta_mu_plus = Phi(alpha) delta_m + phi(alpha) delta_v / (2 sigma)<br/>"
            "delta_v_plus = 2 mu_plus delta_m + Phi(alpha) delta_v - 2 mu_plus delta_mu_plus",
            "CodeCustom",
        )
    )
    story.append(
        para(
            styles,
            "The final correction is Q_corrected = Q_base - lambda * delta_mu_final. Because the propagation map and coefficient depend only on network weights and frozen development constants, response-approximation error changes variance under the ideal law but does not create ideal-law mean shift. The fitted coefficient is close to the mechanistic value one and remained stable across whole-network folds.",
        )
    )
    story.append(
        para(
            styles,
            "Qualification: randomized uint32 midpoint Box-Muller is a finite floating-point law, not literal continuous Gaussian measure. The complete pilot-pruned estimator is biased independently of this microscopic control-centering issue.",
        )
    )

    story.append(para(styles, "4. Experimental firewall", "H1Custom"))
    firewall_data = [
        ["Stage", "Networks", "Permitted use", "Status"],
        ["Legacy mini", "100", "Early premise work only; known reused data", "Not a holdout"],
        ["Development", "0..799", "Nested CV, coefficients, ablations, seed tests", "Used for generation"],
        ["Public lockbox", "800..999", "One frozen estimator, once, no fitting", "Opened after hash freeze"],
        ["Private Phase II", "Fresh hidden", "Organizer rerun of one designated submission", "Remaining decisive test"],
    ]
    story.append(styled_table(firewall_data, [1.15 * inch, 0.72 * inch, 3.65 * inch, 1.60 * inch], alignments=["LEFT", "CENTER", "LEFT", "LEFT"]))
    story.append(Spacer(1, 6))
    story.append(
        para(
            styles,
            "The 1,000-network public dataset was partitioned and timestamp-frozen before any full-dataset score. Analysis sliced indices 0..799 before residual or score formation. Candidate source, constants, official tarball, and SHA-256 hashes were frozen before the one-shot lockbox capture. Lockbox acceptance limits were also written before access. No model mutation followed the result.",
        )
    )

    story.append(para(styles, "5. Evidence", "H1Custom"))
    evidence_data = [
        ["Gate", "n", "Metric", "Result", "Uncertainty / failures"],
        ["Nested whole-network OOF", "800", "Raw MSE", "1.19984e-6 -> 9.93947e-7 (-17.1599%)", "paired 95% CI [-2.6591e-7, -1.5156e-7]"],
        ["Frozen seed 0", "200", "Raw MSE change", "-14.54%", "CI wholly favorable"],
        ["Frozen seed 1", "200", "Raw MSE change", "-19.44%", "CI wholly favorable"],
        ["Frozen seed 2", "200", "Raw MSE change", "-16.31%", "CI wholly favorable"],
        ["Official subprocess dev20", "20", "Adjusted score", "3.46033e-7 -> 2.77486e-7 (-19.8094%)", "0 failures"],
        ["Frozen public lockbox", "200", "Raw MSE", "9.91146e-7", "finite; q95 2.81997e-6; max 9.48400e-6"],
    ]
    story.append(styled_table(evidence_data, [1.30 * inch, 0.37 * inch, 1.05 * inch, 2.38 * inch, 2.02 * inch], font_size=7.0, alignments=["LEFT", "CENTER", "LEFT", "LEFT", "LEFT"]))

    factorial_data = [
        ["Candidate", "Raw MSE", "Adjusted score", "Mean effective compute", "Decision"],
        ["Pilot-rescued base", "1.06892e-6", "3.46033e-7", "89.651B", "Reference"],
        ["Moment tangent", "8.47386e-7", "2.77486e-7", "90.199B", "Promote"],
        ["Trace-free rank-4 H2", "1.06502e-6", "3.48607e-7", "90.623B", "Kill"],
        ["Tangent + H2", "8.50230e-7", "2.81341e-7", "91.492B", "Kill"],
    ]
    story.append(
        KeepTogether(
            [
                para(styles, "Matched factorial under WHestBench 0.14", "H2Custom"),
                styled_table(factorial_data, [2.15 * inch, 1.05 * inch, 1.12 * inch, 1.45 * inch, 0.80 * inch], font_size=7.3, alignments=["LEFT", "RIGHT", "RIGHT", "RIGHT", "CENTER"]),
                para(
                    styles,
                    "The tangent cell improved raw MSE by 20.7249% and adjusted score by 19.8094% for only 0.6114% more effective compute on the matched dev20 panel. H2 did not pay for its compute and interacted adversely with tangent.",
                ),
            ]
        )
    )

    story.append(para(styles, "6. Negative results kept in the ledger", "H1Custom"))
    negative_rows = [
        ["Tau folding", "Base-two b-adic tent transform", "+71% raw MSE on matched premise gate", "Killed"],
        ["Fractal prefix", "Dyadic/Haar prefix detail", "Only about 0.4 point exploratory gain; weaker bias proof", "Killed"],
        ["Rank-4 H2", "Price/Hermite angular response control", "+0.74% adjusted alone; +1.39% after tangent", "Killed"],
        ["Homeostatic mosaic", "Weight-only network-dependent tangent gain", "+0.403% nested OOF; CI crossed parity", "Killed"],
        ["Spherical-radial", "Exact ideal-law radius integration", "-0.186% raw but CI [-6.32e-9, 2.66e-9]", "Killed"],
        ["Memristive state", "Hysteretic/adaptive continuation", "Order dependence without an exact telescoping identity", "Rejected"],
    ]
    negatives = [["Mutation", "Classical translation", "Measured falsifier", "Decision"]] + [
        [para(styles, value, "TableCellCustom") for value in row] for row in negative_rows
    ]
    story.append(styled_table(negatives, [1.25 * inch, 1.85 * inch, 3.23 * inch, 0.72 * inch], font_size=6.9, alignments=["LEFT", "LEFT", "LEFT", "CENTER"]))
    story.append(
        para(
            styles,
            "The retinal, biological-patterning, quantum-pigment, memristive, fractal, and physics prompts were translated into testable classical operators. Metaphor alone was never counted as mechanism. The experiment ledger retains these failures to prevent retrospective cherry-picking.",
        )
    )

    story.append(para(styles, "6b. The non-Gaussianity wall: certified exact Gaussian-closure measurements", "H1Custom"))
    story.append(
        para(
            styles,
            "The estimator's central design choice is that Gaussian structure enters only as a control subtracted from a randomized estimate (Section 3), never as the predictor itself. A companion measurement campaign (2026-08-08) quantifies why, by making the competing design - the propagated Gaussian moment closure - exact, certifying it, and scoring it as a standalone estimator.",
        )
    )
    story.append(para(styles, "Certified machinery", "H2Custom"))
    story.append(
        para(
            styles,
            "Two audited components make the closure exact rather than approximate. First, a bounded-cost bivariate provider evaluates the rectified-Gaussian pair moment E[ReLU(X_i) ReLU(X_j)] and its derivatives via Owen-T/Phi2 with per-call enclosure certificates, a fixed 4,048-FLOP budget per pair, charged sign comparisons, exact strata at the rank-one and zero-variance limits, and a 12,890-case adversarial census (all contained). Second, an exact zero-order full-covariance recurrence (mu_0 = 0, V_0 = I; a_l = mu W_l; C_l = W_l^T V_l-1 W_l; post-ReLU (mu_l, V_l) from exact Tallis truncated moments [12]) propagates the complete 256 x 256 covariance through all 32 layers, FlopScope-metered inclusively at 8.30e9 FLOPs = 3.05% of budget. Assembly agrees with 30-digit mpmath references to worst error 2.144e-9 and with an independent closure implementation to about 2e-16.",
        )
    )
    story.append(para(styles, "Measured wall", "H2Custom"))
    closure_data = [
        ["Predictor of the depth-32 final-layer mean", "Bias MSE (noise-floor subtracted)", "Basis"],
        ["Diagonal Gaussian closure", "7.175e-4", "3 He-init nets, 400k-sample MC truth"],
        ["Exact full-covariance Gaussian closure", "9.606e-5 (range 3.70e-5 - 1.79e-4)", "same 3 nets, same MC truth"],
        ["Randomized sampling lineage (reference)", "about 3.09e-7 raw", "public-100 official runs, matched budget"],
    ]
    story.append(styled_table(closure_data, [2.55 * inch, 2.30 * inch, 2.25 * inch], font_size=7.3, alignments=["LEFT", "LEFT", "LEFT"]))
    story.append(Spacer(1, 6))
    story.append(
        para(
            styles,
            "The Monte-Carlo noise floor of the measurement is 1-2e-7 per network - 200 to 1,000 times below the measured closure bias - so the numbers above are resolved signal, not sampling noise. Reading: making the covariance exact buys a factor of about 7.5 over the diagonal closure, and the remaining factor of about 300 to the sampling family is third-and-higher-cumulant structure that no Gaussian-moment closure can represent, at any compute multiplier. Even priced at a zero-cost floor multiplier the exact closure would trail the sampling lineage by more than an order of magnitude. This measurement also corrected an internal planning estimate: an 8.76e-7 closure-oracle ceiling carried in earlier strategy documents is refuted 46-fold by direct measurement, and every downstream projection built on it was withdrawn.",
        )
    )
    story.append(
        para(
            styles,
            "Together with Section 3, the campaign's evidence supports one quantified design principle for mean-field methods in deep-network estimation: exact Gaussian structure pays when subtracted (the moment-tangent control: -19.8094% adjusted score) and fails when predicted (closure-as-estimator: 46x outside the competitive boundary). The certified provider, recurrence, metering ledgers, and the kill-gated measurement protocol are released in the recursive-estimator-folding corpus (experiments m178_certified_phi2_owent, m179_background_archive_producer, t2_closure_score_measurement; fold-ledger records 177-180).",
        )
    )

    story.append(PageBreak())
    story.append(para(styles, "7. Compute, package, and legality", "H1Custom"))
    legality_data = [
        ["Gate", "Result"],
        ["Official validate", "Pass; finite (2,4) contract output"],
        ["Cold subprocess starts", "10/10 pass; identical final MSE and counted FLOPs"],
        ["Worst cold effective compute", "0.340253 of 272B budget"],
        ["Isolated extracted dev3", "0 failures; maximum C/B = 0.343537"],
        ["Package validation", "Pass; no issues"],
        ["Archive contents", "estimator.py; sobol_owen_u32.npz; manifest.json"],
        ["Archive size", "33,332,322 bytes; below 50 MiB"],
    ]
    story.append(styled_table(legality_data, [2.35 * inch, 4.75 * inch], font_size=7.7))
    story.append(Spacer(1, 6))
    story.append(
        para(
            styles,
            "One local setup timeout occurred only while two full800 research jobs saturated the workstation. After contention ended, all ten cold subprocess starts passed. Direct setup was about one second, well below the default five-second limit.",
        )
    )
    story.append(
        para(
            styles,
            "The active source contains no sys.path mutation, sibling import, raw NumPy/SciPy/Torch prediction route, network access, subprocess, ctypes, pickle, grader-state read, telemetry carrier, or hidden file dependency. The only file read is submission_dir/sobol_owen_u32.npz. SciPy appears only in the offline asset generator included with the source release.",
        )
    )

    story.append(para(styles, "8. Reproducibility and frozen hashes", "H1Custom"))
    hash_data = [
        ["Artifact", "SHA-256"],
        ["estimator.py", "8428026E01224F9E48F2FD72C303100909E529370183E67F376E4623113425D8"],
        ["sobol_owen_u32.npz", "050339EC9966BD046B4FCF53C85240F89D2CD1F7D60C30421922203045EED0CA"],
        ["official tar.gz", "D2E58DF64A85121770F9D51977667882DD10CDC9496B6219F5E7D8258D8CF231"],
        ["lockbox capture", "F02B75D253CF865D6B5C9179F69102345974DE57F1098F3C8FF9D5E046CCD2BD"],
    ]
    hash_table = Table(hash_data, colWidths=[1.55 * inch, 5.55 * inch], repeatRows=1)
    hash_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.45, GRID),
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (1, 1), (1, -1), "Courier"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.0),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    story.append(hash_table)
    story.append(Spacer(1, 6))
    story.append(
        para(
            styles,
            "The asset generator is pinned to Python 3.12.13, NumPy 2.4.6, and SciPy 1.18.0. It regenerated the exact 33,317,968-byte NPZ and verified the frozen asset hash. The source release is MIT-licensed and includes the estimator, asset generator, asset, experiment ledger, freeze record, lockbox result, and offline Headroom patch.",
        )
    )

    story.append(para(styles, "9. Headroom-Recursion and AI disclosure", "H1Custom"))
    story.append(
        para(
            styles,
            "The gmrmk/headroom-recursion repository was adapted with an OfflineTranscriptClient. The adapter accepts strict queued JSON responses for latent, answer, and judge calls, can log prompts to JSONL, raises explicit exhaustion errors, and performs no API, SDK, login, model, or network call. Its targeted tests pass (11 tests). Generation 2 prescribed setup-seed stability, a tangent/H2 factorial, self-contained packaging, and one post-freeze lockbox opening; those gates were executed as written.",
        )
    )
    story.append(
        para(
            styles,
            "OpenAI Codex substantially assisted web and literature research, mathematics, code implementation, adversarial audits, experiment design, testing, analysis, and report writing. Multiple Codex subagents independently audited the biology translation, Hermite algebra, competition legality, and final artifact. Offline Headroom replay does not mean the overall project had no model assistance. All AI-generated claims were treated as hypotheses until checked against source, derivation, or measured evidence.",
        )
    )
    story.append(
        para(
            styles,
            "Section 6b's certified provider, recurrence, measurements, and text were produced with Anthropic Claude (Fable 5) assistance under the same standard: every closure number above was generated by predeclared, kill-gated, response-free protocols with the falsifier written before the code, adversarially red-teamed by independent subagents, and checked against high-precision references before being reported.",
        )
    )

    story.append(para(styles, "10. Limitations and remaining private test", "H1Custom"))
    for item in [
        "The public lockbox is not the private Phase-II distribution; fresh organizer rerun remains decisive.",
        "Pilot-rescued sparsification is biased and can miss rare upstream paths.",
        "Ideal-Gaussian centering arguments are approximate under the finite uint32 and float32 implementation.",
        "Adjusted score depends on grader hardware through charged residual time, although measured compute has substantial headroom.",
        "If organizers publish a different final WhestBench or FlopScope version, all package and accounting gates must be repeated unchanged.",
    ]:
        story.append(bullet(styles, item))
    story.append(
        para(
            styles,
            "Final prize filing procedure: submit the frozen archive unchanged, obtain one successfully graded Phase-II submission ID, insert exactly that ID in this report, rerender and visually verify the PDF, and file it by the Algorithmic Prize deadline. Do not tune the estimator from the private or lockbox score.",
        )
    )

    story.append(para(styles, "References", "H1Custom"))
    refs = [
        "[1] ARC White-Box Estimation Challenge 2026. https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026",
        "[2] Algorithmic Contribution Prize guidelines. https://discourse.aicrowd.com/t/algorithmic-contribution-prize-guidelines-how-arc-judges-these-prizes-discretion-technical-writeups-llm-usage/18041",
        "[3] ARC townhall and private-rerun clarification. https://discourse.aicrowd.com/t/townhall-summary-recording/18078",
        "[4] WhestBench releases. https://github.com/AIcrowd/whestbench/releases",
        "[5] A. B. Owen. Scrambled net variance for integrals of smooth functions. SIAM Journal on Numerical Analysis. https://doi.org/10.1137/S0036142994277468",
        "[6] T. Goda. The b-adic symmetrization of digital nets for quasi-Monte Carlo integration. https://arxiv.org/abs/1509.08570",
        "[7] B. Poole et al. Exponential expressivity in deep neural networks through transient chaos. https://arxiv.org/abs/1606.05340",
        "[8] S. Schoenholz et al. Deep Information Propagation. https://arxiv.org/abs/1611.01232",
        "[9] R. Price. A useful theorem for nonlinear devices having Gaussian inputs. https://doi.org/10.1109/TIT.1958.1057444",
        "[10] S. Kondo and R. Asai. A reaction-diffusion wave on the skin of the marine angelfish. https://doi.org/10.1038/376765a0",
        "[11] D. B. Owen. Tables for computing bivariate normal probabilities. Annals of Mathematical Statistics 27(4), 1956. https://doi.org/10.1214/aoms/1177728074",
        "[12] G. M. Tallis. The moment generating function of the truncated multi-normal distribution. Journal of the Royal Statistical Society, Series B 23(1), 223-229, 1961. https://doi.org/10.1111/j.2517-6161.1961.tb00408.x",
    ]
    for reference in refs:
        story.append(para(styles, reference, "SmallCustom"))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.8, color=TEAL, spaceAfter=6))
    story.append(
        para(
            styles,
            (
                "Report status: development and public-lockbox evidence complete. Prize-filing ID intentionally absent until one frozen Phase-II submission is successfully graded."
                if is_draft
                else "Report status: development, public-lockbox, and successful Phase-II grading evidence complete. The single prize-filing submission ID is recorded above."
            ),
            "SmallCustom",
        )
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    page_callback = lambda canvas, doc: header_footer(canvas, doc, is_draft)
    document.build(story, onFirstPage=page_callback, onLaterPages=page_callback)
    print(output.resolve())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--submission-id", help="exactly one successfully graded Phase-II submission ID")
    args = parser.parse_args()
    build(args.output, args.submission_id)


if __name__ == "__main__":
    main()
