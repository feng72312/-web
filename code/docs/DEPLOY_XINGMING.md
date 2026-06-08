# Xingming (Tab 09) and Tianxiang deployment

## Dependencies

- Python: `pyswisseph>=2.10.3.2` (in `code/backend/requirements.txt`)
- Optional ephemeris files: set `BAZI_TIANXIANG_EPHEMERIS_PATH` to a directory with Swiss `.se1` files for highest precision. Moshier fallback may apply when files are absent.

## Knowledge assets

1. RAG index category `09星命占验` -> collection `kb_09_xingming`
2. Structured nodes: `code/knowledge/data/graph/xingming_nodes.jsonl`
   - Regenerate: `py code/knowledge/scripts/seed_xingming_nodes.py`
3. Gold cases: `code/knowledge/data/cases/xingming_cases_gold.jsonl`

## API smoke

- `GET /api/v1/xingming/rules`
- `POST /api/v1/xingming/chart` with birth JSON
- `POST /api/v1/xingming/cases/search`
- `POST /api/v1/tianxiang/positions`

## Triple fusion (Bazi tab)

Set `fusion: true` and `fusionMode: "triple"` on `POST /api/v1/paipan/interpret`.

Env:

- `BAZI_FUSION_XINGMING_ENABLED=true`
- `BAZI_FUSION_TRIPLE_DEFAULT_SCOPE=stage_turn`
- `BAZI_XINGMING_RAG_CATEGORY=09星命占验`

## Calibration

- `code/knowledge/data/calibration/xingming_gold_charts.json`
- Tests: `pytest code/backend/tests/test_tianxiang_ephemeris.py code/backend/tests/test_xingming_chart.py`

Rules frozen in V1: school `guolao_v1`, ketu = mean lunar apogee, rahu = opposite ketu on ecliptic.
