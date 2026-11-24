# Commands by purpose

Run commands from the repository root.

| Directory | Purpose |
|---|---|
| `pipeline/` | Numbered segmentation / risk training and evaluation, plus segmentation evaluation |
| `brats/` | Consequential-volume characterization, comparison and retrospective MRI showcase |
| `longitudinal/` | LUMIERE agreement, expert-label validation, robustness and extensions |
| `data/` | Dataset acquisition helper |
| `publication/` | Figures and document exports |

The numbered pipeline still runs in order 00, 01, 02, 03, 04. LUMIERE scripts import shared helpers from their own directory. See [the path migration map](../docs/REORGANIZATION.json) for old commands.
