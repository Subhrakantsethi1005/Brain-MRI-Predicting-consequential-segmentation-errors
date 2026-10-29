"""Render the Option B report as an IEEE-style two-column conference PDF
(matching the look of the AyShCXR paper: full-width title/author/abstract
block, two-column justified body, numbered sections, result tables, figures).

Pure reportlab — no LaTeX toolchain required.

    python scripts/optionB_ieee_pdf.py            # -> docs/paper/optionB_report_ieee.pdf
"""

from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, Frame, FrameBreak, Image, NextPageTemplate,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether)
from reportlab.lib.styles import ParagraphStyle

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "paper" / "figures"
OUT = ROOT / "docs" / "paper" / "optionB_report_ieee.pdf"

# ---------------------------------------------------------------- geometry
PW, PH = letter
M = 0.6 * inch
GAP = 18
usable_w = PW - 2 * M
colW = (usable_w - GAP) / 2
top_y = PH - M
H1 = 3.6 * inch                       # full-width header block height
col_top = top_y - H1                  # where page-1 columns start

f_head = Frame(M, col_top, usable_w, H1, id="head", leftPadding=0, rightPadding=0,
               topPadding=0, bottomPadding=0)
f_l1 = Frame(M, M, colW, col_top - M, id="l1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
f_r1 = Frame(M + colW + GAP, M, colW, col_top - M, id="r1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
f_l = Frame(M, M, colW, top_y - M, id="l", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
f_r = Frame(M + colW + GAP, M, colW, top_y - M, id="r", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

# ---------------------------------------------------------------- styles
title = ParagraphStyle("title", fontName="Times-Bold", fontSize=17, leading=20,
                       alignment=TA_CENTER, spaceAfter=10)
authors = ParagraphStyle("authors", fontName="Times-Roman", fontSize=11, leading=14, alignment=TA_CENTER)
affil = ParagraphStyle("affil", fontName="Times-Italic", fontSize=9.5, leading=12, alignment=TA_CENTER, spaceAfter=2)
abstract = ParagraphStyle("abstract", fontName="Times-Bold", fontSize=9, leading=11, alignment=TA_JUSTIFY,
                          spaceBefore=8, leftIndent=18, rightIndent=18)
idxterms = ParagraphStyle("idx", fontName="Times-Bold", fontSize=9, leading=11, alignment=TA_JUSTIFY,
                          spaceBefore=4, leftIndent=18, rightIndent=18)
h1 = ParagraphStyle("h1", fontName="Times-Bold", fontSize=10, leading=12, alignment=TA_CENTER,
                    spaceBefore=10, spaceAfter=4)
h2 = ParagraphStyle("h2", fontName="Times-Italic", fontSize=10, leading=12, alignment=TA_LEFT,
                    spaceBefore=6, spaceAfter=3)
body = ParagraphStyle("body", fontName="Times-Roman", fontSize=9.5, leading=11.5, alignment=TA_JUSTIFY,
                      firstLineIndent=10, spaceAfter=2)
bullet = ParagraphStyle("bullet", parent=body, firstLineIndent=0, leftIndent=10, bulletIndent=0)
cap = ParagraphStyle("cap", fontName="Times-Roman", fontSize=8, leading=9.5, alignment=TA_LEFT, spaceBefore=3, spaceAfter=8)
cell = ParagraphStyle("cell", fontName="Times-Roman", fontSize=7, leading=8.2, alignment=TA_CENTER)
cellL = ParagraphStyle("cellL", parent=cell, alignment=TA_LEFT)
cellH = ParagraphStyle("cellH", parent=cell, fontName="Times-Bold")
ref = ParagraphStyle("ref", fontName="Times-Roman", fontSize=8, leading=9.5, alignment=TA_JUSTIFY,
                     leftIndent=10, firstLineIndent=-10, spaceAfter=2)

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
_sec = [0]


def P(t, s=body):
    return Paragraph(t, s)


def section(t):
    _sec[0] += 1
    return P(f"{ROMAN[_sec[0]]}.&nbsp;&nbsp;{t.upper()}", h1)


def fig(name, caption, w=None):
    path = FIG / name
    img = Image(str(path))
    w = w or colW
    img._restrictSize(w, 10 * inch)
    img.hAlign = "CENTER"
    return KeepTogether([img, P(caption, cap)])


def datatable(header, rows, colw):
    data = [[Paragraph(h, cellH) for h in header]]
    for r in rows:
        data.append([Paragraph(r[0], cellL)] + [Paragraph(x, cell) for x in r[1:]])
    t = Table(data, colWidths=colw, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


# ---------------------------------------------------------------- content
story = []
story.append(P("Reference-Free Prediction of Clinically Consequential Volume Errors in Glioma "
                "Segmentation: A Characterisation and Triage Study on BraTS&nbsp;2023", title))
story.append(P("Subhrakant Sethi&nbsp;&nbsp;&nbsp; Ayush Singh&nbsp;&nbsp;&nbsp; "
               "Abhayaditya Sogi&nbsp;&nbsp;&nbsp; Pratyaksh Singh", authors))
story.append(P("Department of Biotechnology, Thapar Institute of Engineering and Technology, Patiala, India", affil))
story.append(P("{ssethi_btech24, asingh3_btech24}@thapar.edu", affil))

story.append(P("<b><i>Abstract</i></b>&mdash; Automated glioma segmentation is increasingly used to measure "
    "tumour volume, which drives treatment decisions via the RANO response criteria. Existing reference-free "
    "quality-control (QC) methods predict overlap quality (Dice), but overlap quality is not the same as clinical "
    "consequence: a segmentation can overlap well yet mis-measure volume enough to change a decision. We ask, on "
    "BraTS&nbsp;2023 adult glioma (1,251 cases, one strong 3D U-Net, val WT Dice 0.89): (i)&nbsp;which segmentation "
    "errors are clinically consequential (frozen endpoint: whole-tumour volume error &ge;25% and &ge;1&nbsp;mL), and "
    "where they concentrate; and (ii)&nbsp;whether a reference-free flag trained to target consequence catches these "
    "errors better than a generic overlap-QC baseline. We pre-registered the endpoints and protocol before opening the "
    "held-out split. We find, confirmed on a frozen held-out split (risk_test, n=245, 23 positives) and consistent with "
    "development (risk_dev, n=379): (1)&nbsp;consequential volume errors are almost never silent &mdash; only 4 of 570 "
    "high-Dice (&ge;0.85) cases carried a consequential volume error (0.5&ndash;1.2%); (2)&nbsp;a consequence-targeted "
    "flag does not outperform a generic overlap-QC baseline or a single uncertainty feature (held-out AUROC 0.74 vs 0.79 "
    "vs 0.84; paired-bootstrap difference vs overlap-QC &minus;0.043, 95% CI [&minus;0.12,&nbsp;+0.02], p=0.25), a "
    "pre-registered null; and (3)&nbsp;simple reference-free triage is nonetheless useful &mdash; a single uncertainty "
    "check safely automates ~56% of volume measurements at 90% sensitivity with ~1.5% residual error.", abstract))
story.append(P("<b><i>Index Terms</i></b>&mdash; <i>brain tumour MRI, segmentation reliability, volumetric error, "
               "uncertainty, quality control, deep learning.</i>", idxterms))

story.append(NextPageTemplate("later"))
story.append(FrameBreak())

# I. Introduction
story.append(section("Introduction"))
story.append(P("A segmentation model can score a high Dice overlap and still be clinically misleading, because "
    "clinicians act on tumour volume (RANO 2.0 uses volumetric change thresholds), not on voxel overlap. "
    "Reference-free QC &mdash; predicting a segmentation's reliability without ground truth, as needed at deployment "
    "&mdash; is an established and recently strong field (e.g. QCResUNet). However, these methods target overlap "
    "quality. The open question, flagged in recent clinical reviews, is whether overlap quality is the right target: "
    "systematic volume errors can push a patient across a RANO threshold with no true biological change, and no "
    "automated QC tool has been validated against clinical (RANO) consequence."))
story.append(P("This project asks a sharp, honest question rather than proposing yet another model: does targeting "
    "clinical consequence, rather than overlap, actually matter for reference-free triage of glioma segmentation? "
    "We characterise consequential errors and test the targeting hypothesis under a frozen protocol. The value "
    "&mdash; and the defence against &lsquo;this just uses an existing model&rsquo; &mdash; is that this is an "
    "original, pre-registered investigation with a real finding, positive or null."))

# II. Related work
story.append(section("Related Work (cited, not claimed)"))
for t in [
    "<b>Reference-free QC / failure detection:</b> QCResUNet (Med. Image Anal. 2025) predicts subject- and voxel-level "
    "quality and error maps on 1,251 BraTS cases, but targets Dice/NSD (overlap). We differ by targeting consequence.",
    "<b>Uncertainty for segmentation:</b> MC-dropout / TTA uncertainty ranks errors well on average but is "
    "miscalibrated on critical sub-regions (&lsquo;Confidence is Not Reliability&rsquo;, 2026). We use these as "
    "features/baselines, not as the contribution.",
    "<b>Metrics vs clinical utility:</b> <i>Metrics Reloaded</i> (Nat. Methods 2024) shows overlap metrics mismatch "
    "clinical goals; relative volume error isolates volumetric bias, which we adopt as the clinically-grounded error.",
    "<b>RANO &amp; volume:</b> RANO 2.0 volumetric thresholds; reviews note systematic segmentation errors can flip "
    "RANO categories without biological change, and that no tool is validated against RANO 2.0.",
]:
    story.append(Paragraph("&bull;&nbsp;" + t, bullet))

# III. Methods
story.append(section("Methods"))
story.append(P("<b>Data.</b> BraTS&nbsp;2023 adult glioma, 1,251 cases, four co-registered modalities (T1, T1c, T2, "
    "FLAIR) with expert segmentation. Patient-disjoint, pre-frozen splits: seg_train 565 / seg_val 62 / risk_dev 379 "
    "/ risk_test 245."))
story.append(P("<b>Segmenter.</b> One standard 3D residual U-Net (MONAI SegResNet-style), trained to selection "
    "(val WT 0.89 / TC 0.88 / ET 0.85). Frozen; not retrained for this study."))
story.append(P("<b>Reference-free features</b> (no ground truth; from MC-dropout + flip-TTA passes): per-sub-region "
    "uncertainty (entropy, variance), disagreement across passes (volume CV, range, sample-Dice), boundary/morphology "
    "(undecided-shell fraction, soft&ndash;hard volume gap, components, surface-to-volume), nested-region consistency, "
    "and a deterministic probability-threshold-sweep volume instability signal."))
story.append(P("<b>Frozen endpoints</b> (pre-registration): primary &mdash; whole-tumour volume error rel &ge;25% and "
    "abs &ge;1&nbsp;mL; secondary &mdash; the same thresholds on TC and ET; a RANO-2.0 magnitude proxy reported "
    "explicitly as a single-timepoint simulation (BraTS is cross-sectional)."))
story.append(P("<b>Analyses.</b> A1 characterisation (signed error; over/under-segmentation; consequential rate by "
    "sub-region and size); A2 metric-blindness (do good-Dice cases still carry consequential volume error?); A3 "
    "consequence-targeted flag (logistic on reference-free features, tuned on risk_dev, evaluated once on risk_test, "
    "operating point at 90% sensitivity); A4 differentiation vs a generic overlap-QC baseline (paired bootstrap). "
    "Baselines: predicted volume alone; best single uncertainty."))

# IV. Results
story.append(section("Results"))
story.append(P("Primary evaluation is the frozen held-out risk_test (n=245; TC/ET defined for 244/238), opened once. "
    "The flag is fit on risk_dev (n=379) and evaluated on risk_test. Development-split (out-of-fold CV) numbers agreed "
    "throughout, as did a 35-case seg_val preview."))

story.append(P("A.&nbsp;&nbsp;Characterisation (A1) and metric-blindness (A2)", h2))
story.append(datatable(
    ["Region", "Conseq. rate", "Over/Under", "Good-Dice but conseq.", "r(Dice, |VE|)"],
    [["WT (primary)", "9.4%", "61 / 39%", "1 / 205 (0.5%)", "&minus;0.81"],
     ["TC", "10.7%", "44 / 56%", "1 / 196 (0.5%)", "&minus;0.78"],
     ["ET", "13.0%", "51 / 49%", "2 / 169 (1.2%)", "&minus;0.63"]],
    [colW * x for x in (0.21, 0.19, 0.17, 0.26, 0.17)]))
story.append(P("TABLE I. Consequential-error characterisation on the held-out split.", cap))
story.append(fig("fig1_dice_vs_volerr.png", "Fig. 1. Consequential errors coincide with low Dice (whole tumour)."))
story.append(fig("fig2_rate_by_region.png", "Fig. 2. Consequential-error rate by sub-region."))
story.append(P("Two findings: (i)&nbsp;consequential volume errors are almost never silent &mdash; only 4 of 570 "
    "high-Dice (&ge;0.85) cases across the three regions carried a consequential volume error; and (ii)&nbsp;Dice "
    "correlates negatively and consistently with relative volume error (&minus;0.63 to &minus;0.81), i.e. for glioma, "
    "good overlap tracks good volume. Part of this coupling is mechanical: a &ge;25% volume error tends to force low "
    "overlap &mdash; we state this plainly."))

story.append(P("B.&nbsp;&nbsp;Consequence-flag vs overlap-QC (A3/A4), WT primary endpoint", h2))
story.append(datatable(
    ["Method (reference-free)", "AUROC [95% CI]", "Retain @90", "Residual"],
    [["best single uncertainty", "0.838 [0.744, 0.916]", "56%", "1.5%"],
     ["overlap-QC baseline", "0.786 [0.681, 0.880]", "27%", "3.0%"],
     ["predicted volume only", "0.766 [0.666, 0.855]", "49%", "1.7%"],
     ["consequence flag (ours)", "0.743 [0.620, 0.854]", "22%", "3.8%"]],
    [colW * x for x in (0.33, 0.37, 0.16, 0.14)]))
story.append(P("TABLE II. Frozen held-out risk_test (n=245, 23 positives).", cap))
story.append(P("On the frozen held-out split the consequence-targeted flag (0.743) does not beat the generic overlap-QC "
    "baseline (0.786) or a single uncertainty feature (0.838). A4 verdict: pre-registered null &mdash; paired-bootstrap "
    "difference (consequence-flag &minus; overlap-QC) = &minus;0.043, 95% CI [&minus;0.121, +0.019], p=0.25. "
    "Practically, a simple uncertainty check still enables useful triage: ~56% of cases automated at 90% sensitivity "
    "with ~1.5% residual consequential error on the retained pile."))

# V. Discussion
story.append(section("Discussion"))
for t in [
    "<b>Characterisation:</b> consequential volume errors occur at ~9&ndash;13% across sub-regions and are almost "
    "never silent &mdash; they coincide with low overlap, and Dice is consistently and negatively coupled to relative "
    "volume error (&minus;0.63 to &minus;0.81).",
    "<b>Targeting hypothesis &mdash; refuted:</b> the consequence-targeted flag does not beat generic overlap-QC or a "
    "single uncertainty feature (A4 difference &minus;0.043, p=0.25). For glioma, overlap quality already tracks "
    "clinical volume consequence closely, so a generic reference-free QC suffices and a dedicated consequence model is "
    "unnecessary &mdash; a useful, mildly counter-intuitive negative result.",
    "<b>Practical value:</b> despite the null, a lightweight single-uncertainty check safely automates ~56% of cases "
    "at 90% sensitivity with ~1.5% residual consequential error &mdash; useful for deployment.",
]:
    story.append(Paragraph("&bull;&nbsp;" + t, bullet))
story.append(P("Each of these is an original, pre-registered finding, not a reused model."))

# VI. Limitations
story.append(section("Limitations"))
story.append(P("BraTS has one timepoint per patient, so the RANO-threshold analysis is a single-timepoint simulation, "
    "not a real serial-scan decision. We use a single segmentation architecture and one dataset family (BraTS), with "
    "no external-site validation. Consequential cases are rare (23 WT positives on risk_test; 45 on risk_dev), so "
    "held-out AUROC CIs are wide (~&plusmn;0.1); development and held-out results agree, which supports the null, but "
    "larger multi-centre cohorts would tighten the estimates. Part of the overlap&ndash;volume coupling is mechanical "
    "(a large volume error forces low Dice), so the &lsquo;no silent errors&rsquo; result is partly expected; we report "
    "it as empirical confirmation, not a surprise."))

# VII. Conclusion
story.append(section("Conclusion"))
story.append(P("We pre-registered and ran a reference-free study of clinically consequential glioma segmentation errors, "
    "with the headline evaluated once on a frozen held-out split. Consequential volume errors in glioma are almost "
    "never silent (they coincide with low overlap); targeting consequence therefore adds no measurable value over "
    "generic reference-free QC (held-out A4 difference &minus;0.043, p=0.25) &mdash; a pre-registered null that refutes "
    "the overlap-vs-volume-divergence assumption for this task; and simple reference-free triage nonetheless safely "
    "automates ~56% of volume measurements at 90% sensitivity with ~1.5% residual consequential error. The practical "
    "takeaway: a lightweight overlap/uncertainty check is sufficient to triage consequential glioma volume errors; a "
    "dedicated consequence model is not needed."))

# References
story.append(section("References"))
refs = [
    "P. Qiu, S. Chakrabarty, P. Nguyen, S. S. Ghosh, and A. Sotiras, &lsquo;QCResUNet: Joint subject-level and "
    "voxel-level segmentation quality prediction,&rsquo; <i>Medical Image Analysis</i>, 2025. arXiv:2412.07156.",
    "X. C. Wong, D. Sarikaya, K. Zucker, M. De Kamps, and N. Ravikumar, &lsquo;Confidence is not reliability: "
    "Rethinking MC dropout in brain tumour segmentation,&rsquo; arXiv:2606.19300, 2026.",
    "L. Maier-Hein, A. Reinke, <i>et al.</i>, &lsquo;Metrics Reloaded: Recommendations for image analysis "
    "validation,&rsquo; <i>Nature Methods</i>, vol. 21, 2024.",
    "B. M. Ellingson <i>et al.</i>, &lsquo;A neuroradiologist's guide to operationalizing the RANO criteria version "
    "2.0 for gliomas in adults,&rsquo; <i>AJNR Am. J. Neuroradiol.</i>, vol. 45, no. 12, pp. 1846&ndash;1856, 2024.",
    "&lsquo;Response Assessment in Neuro-Oncology (RANO) review,&rsquo; <i>Frontiers in Neurology</i>, 2026.",
]
for i, r in enumerate(refs, 1):
    story.append(Paragraph(f"[{i}]&nbsp;&nbsp;{r}", ref))

# ---------------------------------------------------------------- build
doc = BaseDocTemplate(str(OUT), pagesize=letter, title="Reference-Free Prediction of Consequential Volume Errors",
                      author="Sethi, Singh, Sogi, Singh")
doc.addPageTemplates([
    PageTemplate(id="first", frames=[f_head, f_l1, f_r1]),
    PageTemplate(id="later", frames=[f_l, f_r]),
])
doc.build(story)
print(f"wrote {OUT}  ({OUT.stat().st_size} bytes)")
