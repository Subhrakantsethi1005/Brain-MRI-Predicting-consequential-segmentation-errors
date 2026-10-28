# Viva Preparation — Brain-Tumour Segmentation Reliability Project

> A plain-language guide to explain and defend this project in a viva. It covers:
> (1) what the project does in one breath, (2) the problem and why it matters,
> (3) the key terms in simple words, (4) how the system works step by step,
> (5) the methodology in brief, (6) the honest result, and (7) likely questions
> with answers. Read it top to bottom once; the bold lines are the ones to say out loud.

## 1. What this project does (the one-sentence answer)

**We built a system that looks at an AI's brain-tumour outline and predicts whether that outline got the tumour's *size* badly wrong — without ever seeing the correct answer — so that risky cases can be sent to a doctor and the safe ones can be trusted automatically.**

If the examiner only remembers one sentence, that is the one.

## 2. The problem — and why anyone should care

An AI can automatically draw an outline around a brain tumour on an MRI scan. This is called **segmentation**. From that outline you can measure the **tumour volume** (its size in millilitres).

Why volume matters: doctors track whether a tumour is growing or shrinking to decide if a treatment is working. There is an official clinical rule (**RANO**) that says a **25 % increase in tumour burden counts as the disease getting worse**. So the volume number directly changes a patient's treatment.

The danger: the AI is usually good, but it occasionally makes a bad mistake on one scan. If that one scan's volume is badly wrong, a doctor could wrongly conclude the tumour grew (or shrank). We cannot check every case by hand — that defeats the point of automation.

**So the real question is not "is the AI accurate on average?" It is "for THIS one scan, can we trust the result, or should a human look?"** That per-scan trust decision is what this project is about.

The hard part: in the real world we **do not have the correct answer** to compare against (if we did, we wouldn't need the AI). So our system has to judge the AI's reliability using only clues the AI itself produces — this is called **reference-free** (no ground-truth needed at decision time).

## 3. Key terms in plain words

| Term | Plain-English meaning |
|---|---|
| Segmentation | Drawing the outline of the tumour on the scan (which voxels are tumour). |
| Voxel | A 3D pixel — one little cube of the scan. |
| Volume error | How far the AI's tumour size is from the true size. |
| "Consequential" error | An error big enough to matter clinically (our rule: ≥ 25 % off AND ≥ 1 mL off). |
| Reference-free | Deciding reliability **without** the correct answer — like real deployment. |
| Uncertainty | A measure of how unsure the AI is, built from its own wobble (see MC-dropout). |
| MC-dropout | Running the AI several times with parts randomly switched off, so it gives slightly different answers each time. If the answers jump around a lot, the AI is unsure. |
| Test-time augmentation (TTA) | Also flipping the scan left/right on each run, to add more honest variation. |
| Triage | Sorting cases into "trust automatically" vs "send to a human". |
| Dice score | A 0–1 score of how well two outlines overlap (1 = perfect). A quality measure. |
| AUROC | A 0.5–1.0 score for how well our detector separates "wrong" cases from "fine" cases (0.5 = coin flip, 1.0 = perfect). |
| Pre-registered | We wrote down and froze the exact success rule **before** looking at the test data, so we can't cheat by moving the goalposts. |

## 4. How the system works — step by step

Think of it as a pipeline with five stages. Each stage has a numbered script (`00`–`04`).

**Step 0 — Split the patients (`00_make_splits.py`).**
We divide patients into four separate groups so no patient is ever in two groups at once:
- **seg_train (45 %)** — teach the tumour-outlining AI.
- **seg_val (5 %)** — pick the best version of that AI and report its quality.
- **risk_dev (30 %)** — build and tune our *reliability* detector.
- **risk_test (20 %)** — the locked box; touched only once, at the very end.

*Why it matters:* the detector must learn from realistic mistakes. If the segmenter graded its own training cases, its "mistakes" would be unrealistically tiny. Keeping the groups separate is what makes the whole study honest.

**Step 1 — Train the segmenter (`01`).**
We train a standard, well-known 3D network (a **residual 3D U-Net**, from the MONAI library) to outline the tumour. We deliberately did **not** invent a new network — we want an ordinary, fair baseline, not a specially weakened or specially tuned one.

**Step 2 — Run it "wobbly" to get uncertainty (`02`).**
For each new scan we run the segmenter **several times** with MC-dropout on and random flips (TTA). This gives several slightly different outlines. From them we compute, for each voxel, the **average** opinion and how much the opinions **varied**. Lots of variation = the AI is unsure there. **No correct answer is used here — this is the reference-free part.**

**Step 3 — Turn the wobble into case-level clues / features (`03`).**
We squeeze all that voxel-level information into a handful of numbers that describe the *whole case*. We group them into "families":
- **uncertainty** — how unsure the AI is overall (average entropy/variance).
- **disagreement** — how much the measured volume jumps between the repeated runs.
- **boundary / morphology** — how fuzzy the tumour's edge is, how many separate blobs there are, the shape, and how much of the volume is "undecided".
- **combined** — all of the above together.

We also keep two deliberately dumb **baselines** to beat:
- **volume_only** — just the predicted size (small tumours naturally have big percentage errors).
- **best_single** — the single best one of the uncertainty numbers on its own ("just threshold one uncertainty value").

**Step 4 — Train the reliability detector and test it (`04`).**
A simple model (**logistic regression**, with gradient boosting as a backup) takes those feature numbers and outputs a **risk score**: how likely this case has a consequential volume error. We tune it on `risk_dev` using repeated cross-validation, fix an operating threshold at **90 % sensitivity** (catch 90 % of the truly bad cases), then test **once** on the locked `risk_test`.

**The payoff is a triage rule:** cases flagged as risky → human review; the rest → trusted automatically. We report how many we can safely automate and how much the error rate drops in the "trusted" pile.

## 5. The methodology in brief (say this if asked "summarise your method")

> "We frame segmentation reliability as a **case-level prediction problem**: using only the segmenter's own stochastic behaviour — **no reference mask** — predict whether the whole-tumour volume error is clinically consequential, so unreliable cases can be triaged to a human.
>
> We split patients into disjoint groups so the detector learns from realistic errors. We train a standard 3D residual U-Net, then run it with **MC-dropout plus flip test-time augmentation** to get per-voxel mean and variance. From these we build reference-free, case-level **features** — uncertainty, prediction disagreement, and boundary/shape descriptors — and compare them against two baselines (predicted volume alone, and the single best uncertainty score).
>
> The success rule was **pre-registered and frozen** before we touched the test set: the primary endpoint flags a case when whole-tumour volume error is **≥ 25 % AND ≥ 1 mL** (the 25 % ties to the RANO progression threshold). A **logistic-regression** risk model is tuned with repeated cross-validation on the development split, its threshold fixed at 90 % sensitivity, and then evaluated **once** on the held-out split using **AUROC** and triage metrics, with a **paired bootstrap** to compare feature families."

## 6. The honest result (and how to defend it)

Be straight about this — examiners respect honesty and it is a strength of the work.

**On our first (feasibility) dataset, the fancy engineered features did NOT beat the simple baselines on the pre-registered primary endpoint.** All methods scored a similar AUROC (roughly 0.83–0.88). The strongest candidate beat the best single-uncertainty baseline by only +0.001 (basically a tie).

How to frame it positively and truthfully:
- **We did not change the goalposts to manufacture a win** — that is exactly why pre-registration matters, and it is the scientific point.
- **Triage still works:** at 90 % sensitivity we could safely automate about half the cases, and the error rate in the trusted pile dropped sharply.
- **The honest negative result is the motivation for the real research:** it told us a simple checker wasn't a genuine contribution, which led to (a) moving to a much larger dataset (**BraTS 2023, 1,251 cases, now downloaded**) and (b) building a **learned end-to-end detector** — a small 3D network that reads the uncertainty maps directly instead of hand-made features — tested under the *same* frozen rules.

One-liner to say: **"The method is sound and the protocol is honest; on the small dataset the engineered features only tied the baseline, and that negative finding is what drives our next step on the full dataset."**

## 7. Likely viva questions — with short answers

**Q: Why predict *volume* error and not Dice/overlap?**
Because volume is what doctors actually act on (the 25 % RANO rule). A model can have decent overlap yet still mis-measure volume enough to change a treatment decision.

**Q: What does "reference-free" mean and why is it important?**
It means we decide reliability without the correct answer — because in real deployment there is no correct answer. It's the whole point: if we had ground truth we wouldn't need the AI.

**Q: Where does the uncertainty come from?**
From MC-dropout plus flip TTA: we run the segmenter several times with randomness on; disagreement between runs is the uncertainty signal. No extra models needed — runs on one 6 GB GPU.

**Q: Why pre-register the endpoint?**
So we can't tune the definition of "error" until we get a nice result. The commit timestamp proves the rule was fixed before we saw the test data. It is what makes a negative result trustworthy.

**Q: Why keep the patient groups separate?**
So the detector learns from *realistic* errors. A segmenter makes unrealistically small errors on scans it trained on; using those would make the problem artificially easy and the results misleading.

**Q: Why logistic regression instead of a big deep model?**
Positives (bad cases) are rare, so a simple, interpretable model is less likely to overfit and is a fair, transparent baseline. We report gradient boosting as a secondary check.

**Q: Your features didn't beat the baseline — isn't the project a failure?**
No. The contribution is the **problem formulation, the honest pre-registered comparison, and the triage benchmark** — not a claim of beating baselines. The negative result is a valid, reportable finding and it directs the next, genuinely novel step (the learned detector on the large dataset).

**Q: What's the threshold "90 % sensitivity"?**
We fix the detector to catch 90 % of the truly consequential errors, then measure how many cases that lets us safely automate. In triage you care most about not missing the bad ones.

**Q: What's next?**
Run the identical pipeline on the full BraTS 2023 set (1,251 cases, already downloaded), and train the learned end-to-end detector, judged on a fresh once-opened test split under the same frozen rules.
