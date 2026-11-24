# Recorded-data demonstration

Run `python demo/run_demo.py` from the repository root. Requires only Python's standard library. `--list` shows public pseudonymous IDs, `--patient ID` selects a trajectory, and `--json` emits the replay for inspection.

The demo replays actual derived enhancing-tumour measurements from the public LUMIERE tables, not live inference. It computes each tool's volume-only progression call from its own prior post-operative nadir. It refers disagreements for review and labels agreement without claiming safety. The expert RANO label appears only for retrospective comparison.

The default example is deliberately selected to contain a disagreement, so it illustrates the rule rather than estimating performance. Calls use source-precision measurements. The console display rounds volumes to 0.01 mL. No raw MRI or model weights are bundled here.

Data source: Yannick Suter et al., *The LUMIERE dataset: Longitudinal Glioblastoma MRI with expert RANO evaluation*, Scientific Data 9, 768 (2022), https://doi.org/10.1038/s41597-022-01881-7. Derived under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes: selected available trajectories, converted mm3 to mL, preserved source precision, added computed progression calls. No endorsement by the dataset authors is implied.

For an MRI overlay demonstration, the original `scripts/brats/showcase_demo.py` requires local BraTS data and predicted masks. Existing retrospective examples remain under `docs/paper/figures/showcase/`. Their historic “trust” annotations are illustrative and do not establish a calibrated safety decision.
