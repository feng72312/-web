# Zi Wei Dou Shu MVP (Tab 11)

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/ziwei/rules` | Rule enums and defaults |
| POST | `/api/v1/ziwei/chart` | Natal chart + decadal / minor / yearly limits |
| POST | `/api/v1/ziwei/rag/search` | RAG category `11紫微斗数` |
| POST | `/api/v1/ziwei/interpret` | RAG + AI (quota) |
| POST | `/api/v1/ziwei/chat/init` | Chat bootstrap |

## Env

- `BAZI_ZIWEI_RAG_CATEGORY` (default `11紫微斗数`)
- `BAZI_ZIWEI_LEAP_MONTH_RULE` (`next_month` | `midmonth_split`)
- `BAZI_ZIWEI_ZI_HOUR_RULE` (`combined` | `split`)
- `BAZI_ZIWEI_MUTAGEN_TABLE` (`nan_pai` reserved others)

## Engine

- Library: `iztro-py` (South branch san-he default)
- Time: China DST + optional true solar (`longitude` default 120)
- Rules independent from Bazi `PaipanRules`

## Chart JSON

See `app/core/ziwei/normalize.py` for `palaces`, `limits.decadal`, `limits.minor`, `limits.yearly`.
