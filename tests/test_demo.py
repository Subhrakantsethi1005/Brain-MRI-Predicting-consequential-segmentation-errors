"""Verify clinically relevant rule boundaries and trajectory handling."""
import importlib.util
from pathlib import Path
import json

spec = importlib.util.spec_from_file_location('brainrisk_demo', Path(__file__).resolve().parents[1] / 'demo/run_demo.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def test_both_growth_conditions_required():
    assert demo.progression(14, 10)
    assert not demo.progression(13.99, 10)
    assert not demo.progression(0.8, 0.1)
    assert demo.progression(1.05, 0)


def test_nadir_uses_only_prior_postoperative_visits():
    visits = [dict(week=0, label='Pre-Op', vd=0.01, vh=0.01),
              dict(week=1, label='Post-Op', vd=10, vh=10),
              dict(week=2, label='SD', vd=14, vh=11),
              dict(week=3, label='PD', vd=8, vh=8),
              dict(week=4, label='SD', vd=12, vh=12)]
    rows = demo.replay(visits)
    assert rows[0]['label'] == 'Post-Op' and 'flag' not in rows[0]
    assert rows[1]['flag'] == 'REFER'
    assert rows[2]['nadir_d'] == 10
    assert rows[3]['nadir_d'] == 8 and rows[3]['flag'] == 'AGREE'
    # Changing evaluable expert outcome cannot change tool decisions.
    visits[2]['label'] = 'PD'
    assert demo.replay(visits)[1]['call_d'] == rows[1]['call_d']


def test_bundled_default_contains_real_disagreement():
    data = json.loads(demo.DATA.read_text(encoding='utf-8'))
    patient = demo.select_patient(data['patients'])
    assert any(row.get('flag') == 'REFER' for row in demo.replay(data['patients'][patient]))
    assert data['provenance']['doi'] == '10.1038/s41597-022-01881-7'
    rows = [r for visits in data['patients'].values() for r in demo.replay(visits) if 'flag' in r]
    assert len(rows) == 221
    # Compare replay decisions against the original analysis export at source precision.
    assert all(r['call_d'] == bool(r['auto_d']) and r['call_h'] == bool(r['auto_h']) for r in rows)
