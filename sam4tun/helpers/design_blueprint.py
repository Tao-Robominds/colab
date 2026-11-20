import json
import os
_REQUIRED = ('inner_diameter_m', 'ring_length_m', 'ring_count', 'orientation_xy')

def load_design_blueprint(subset_id: str | None=None) -> dict:
    meta_path = (os.environ.get('PROXY4TUN_TUNNEL_META') or '').strip()
    if not meta_path:
        raise SystemExit('PROXY4TUN_TUNNEL_META is required for the design blueprint')
    subset = (os.environ.get('PROXY4TUN_SUBSET') or '').strip() or (subset_id or '')
    if not subset:
        raise SystemExit('PROXY4TUN_SUBSET or subset_id is required for the design blueprint')
    with open(meta_path, 'r', encoding='utf-8') as handle:
        meta = json.load(handle)
    entry = meta.get(subset)
    if entry is None:
        raise SystemExit(f'No design blueprint for subset {subset} in {meta_path}')
    missing = [key for key in _REQUIRED if key not in entry]
    if missing:
        raise SystemExit(f'Design blueprint for {subset} missing fields: {missing}')
    diameter = float(entry['inner_diameter_m'])
    ring_length = float(entry['ring_length_m'])
    ring_count = int(entry['ring_count'])
    orientation = entry['orientation_xy']
    if ring_count < 1:
        raise SystemExit('ring_count must be >= 1')
    if diameter <= 0 or ring_length <= 0:
        raise SystemExit('inner_diameter_m and ring_length_m must be positive')
    if not isinstance(orientation, (list, tuple)) or len(orientation) != 2:
        raise SystemExit('orientation_xy must have two components')
    ox = float(orientation[0])
    oy = float(orientation[1])
    norm = (ox * ox + oy * oy) ** 0.5
    if norm == 0.0 or not norm == norm:
        raise SystemExit('orientation_xy must be a finite non-zero vector')
    return {'subset_id': subset, 'inner_diameter_m': diameter, 'ring_length_m': ring_length, 'ring_count': ring_count, 'orientation_xy': (ox / norm, oy / norm)}
