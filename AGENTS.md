# Repository Guidelines

## Project Structure & Module Organization
The repository is data-first: `cost.csv`, `enrollment.csv`, `gradrates.csv`, and `institutions.csv` are the canonical inputs driving the ACT chart outputs. Keep raw datasets in the repository root, and place any derived exports inside `data/` with subfolders such as `data/processed/2024/` when versioning intermediate files. New transformation or visualization code should live under `src/` using clear module names (for example, `src/charts/enrollment_trends.py`), while exploratory notebooks belong in `notebooks/` with dates in the filename to document analysis history.

## Build, Test, and Development Commands
Set up a local environment with `python -m venv .venv && source .venv/bin/activate`, then install dependencies via `pip install -r requirements.txt` (add the file if new libraries are introduced). Run data quality checks and chart generation through targeted scripts, e.g. `python src/charts/build_all.py` to regenerate figures. Use `make refresh-data` when adding a Makefile target that pulls updated IPEDS exports, keeping automation repeatable.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, favor dataclasses for structured records, and annotate functions with type hints. Name chart modules `*_chart.py`, dataset loaders `load_*.py`, and constants in `UPPER_SNAKE_CASE`. Run `ruff check .` before committing to lint formatting, and `black src tests` if formatting drift appears. Notebook cells should remain concise—extract reusable logic into modules and import it back into notebooks.

## Testing Guidelines
Adopt `pytest` for unit and integration coverage. Store tests in `tests/` mirroring the `src/` layout, using function names like `test_enrollment_trend_handles_missing_rows`. Provide fixture CSVs under `tests/fixtures/` representing minimal slices of the canonical files, and prefer parametrized tests to cover multiple academic years. Aim for high coverage on data validation utilities and any calculation that feeds chart annotations.

## Commit & Pull Request Guidelines
Use Conventional Commits (`feat:`, `fix:`, `data:`) so changelogs can be generated automatically. Squash noisy commits before merging, reference the related issue number, and summarize dataset revisions (rows added, filters applied) in the PR description. Include updated chart thumbnails or CLI output snippets when behavior changes, call out manual steps that reviewers must run, and ensure lint/tests pass locally before requesting review.

## Security & Data Handling
Do not commit files that contain PII or API credentials—store secrets in a local `.env` ignored by Git. When sharing derived datasets, aggregate to institutional or cohort levels to avoid exposing individual records. Document any external data pulls in the PR description so reviewers can verify licensing and redistribution terms.
