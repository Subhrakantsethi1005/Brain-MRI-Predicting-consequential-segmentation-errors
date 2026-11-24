"""Offline replay of recorded public LUMIERE volumes. No MRI inference."""
import argparse
import json
from pathlib import Path

DATA = Path(__file__).parent / 'data' / 'lumiere.json'
POSTOP = {'Post-Op', 'PD', 'SD', 'PR', 'CR'}
MEASURABLE = {'PD', 'SD', 'PR', 'CR'}


def progression(volume_ml, nadir_ml):
    """Study proxy: >=40% AND >=1 mL over prior nadir, floored at 0.05 mL."""
    nadir_ml = max(nadir_ml, 0.05)
    return volume_ml >= 1.4 * nadir_ml and volume_ml - nadir_ml >= 1.0


def replay(timepoints):
    """Expert labels mark eligible visits but never determine either tool's call."""
    prior_d, prior_h, out = [], [], []
    for visit in sorted(timepoints, key=lambda r: (r['week'], r.get('timepoint', ''))):
        row = dict(visit)
        if visit['label'] not in POSTOP:
            continue
        if prior_d and visit['label'] in MEASURABLE:
            nd, nh = max(min(prior_d), 0.05), max(min(prior_h), 0.05)
            d, h = progression(visit['vd'], nd), progression(visit['vh'], nh)
            row.update(nadir_d=nd, nadir_h=nh, call_d=d, call_h=h,
                       flag='AGREE' if d == h else 'REFER')
        prior_d.append(visit['vd'])
        prior_h.append(visit['vh'])
        out.append(row)
    return out


def select_patient(patients):
    """Deterministically choose an illustrative real case, not a cohort estimate."""
    for patient in sorted(patients):
        if any(r.get('flag') == 'REFER' for r in replay(patients[patient])):
            return patient
    return sorted(patients)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--patient', help='Public pseudonymous ID from --list')
    parser.add_argument('--list', action='store_true', help='Show available patient IDs')
    parser.add_argument('--json', action='store_true', help='Machine-readable replay')
    args = parser.parse_args()
    patients = json.loads(DATA.read_text(encoding='utf-8'))['patients']
    if args.list:
        print('\n'.join(sorted(patients)))
        return
    patient = args.patient or select_patient(patients)
    if patient not in patients:
        parser.error(f'Unknown patient {patient!r}. Run --list for available IDs.')
    rows = replay(patients[patient])
    if args.json:
        print(json.dumps({'patient': patient, 'timepoints': rows}, indent=2))
        return
    print(f'BRAINRISK | recorded LUMIERE replay | {patient}')
    print('Research demonstration. AGREE is not a clinical safety certificate.')
    print('PD proxy: >=40% AND >=1 mL above prior nadir (floor 0.05 mL).')
    print('Volumes in mL; display rounds to 0.01 mL. No model runs here.\n')
    print(f'{"Week":>5} {"DBT":>9} {"HG":>9} {"Nadir D/H":>16} {"DBT call":>10} {"HG call":>10} {"Flag":>8} {"Expert":>8}')
    for r in rows:
        eligible = 'flag' in r
        nd = f'{r["nadir_d"]:.2f}/{r["nadir_h"]:.2f}' if eligible else 'baseline'
        d = ('PD' if r['call_d'] else 'non-PD') if eligible else '--'
        h = ('PD' if r['call_h'] else 'non-PD') if eligible else '--'
        print(f'{r["week"]:5} {r["vd"]:9.2f} {r["vh"]:9.2f} {nd:>16} {d:>10} {h:>10} {r.get("flag","--"):>8} {r["label"]:>8}')
    print('\nREFER: the volume-based tools disagree; human review is appropriate.')
    print('Expert RANO is shown only as retrospective context. Full RANO uses more information.')
    print('Source: Suter et al., Scientific Data (2022), doi:10.1038/s41597-022-01881-7, CC BY 4.0.')


if __name__ == '__main__':
    main()
