# College Accountability Dashboard

## Processed Data Notes
- Files: `data/processed/tuition_vs_graduation.parquet` and `data/processed/tuition_vs_graduation_two_year.parquet` are the Snappy-compressed Parquet sources used by the app.
- Compression: Snappy via `DataFrame.to_parquet(..., compression="snappy")` balances size and load speed.
- Column dtypes: `UnitID`/`enrollment`/`year` → `Int32`, `cost`/`graduation_rate` → `float32`, `sector`/`state` → pandas `category`, and `institution` → pandas `string`.
- Cache versioning: `DATA_VERSION = "parquet_v1"` in `src/data/datasets.py` scopes Streamlit's `st.cache_data` to the current Parquet schema.
- Regeneration: run `python -m src.data.datasets` to rebuild Parquet (falls back to CSV, validates counts/stats, and overwrites the Parquet outputs).
