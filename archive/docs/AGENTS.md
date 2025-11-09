# Repository Guidelines

## Project Structure & Module Organization
This repository is data-first: canonical IPEDS extracts (`cost.csv`, `enrollment.csv`, `gradrates.csv`, `institutions.csv`) stay in the root. Derived outputs move into `data/processed/<year>/`, while source pulls live in `data/raw/`. `app.py` is the Streamlit entry point; place reusable transformations and visualizations under `src/` (create the folder if missing) with descriptive names such as `src/charts/cost_vs_grad_chart.py`. Mirror business logic in `tests/`, and reserve `notebooks/` for dated exploratory notebooks that import shared code.

## Build, Test, and Development Commands
Create a virtual environment with `python -m venv .venv && source .venv/bin/activate`, then install dependencies via `pip install -r requirements.txt` or `pip install -e '.[dev]'` for editable installs. Launch the dashboard locally using `streamlit run app.py`. When chart pipelines exist, trigger regenerations through focused scripts (e.g., `python src/charts/build_all.py`) so outputs remain reproducible.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, type hints, and dataclasses for structured records. Name chart modules `*_chart.py`, dataset loaders `load_*.py`, and constants in `UPPER_SNAKE_CASE`. Run `ruff check .` to lint and `black src tests` when formatting drifts. Keep notebook cells slim—push reusable logic into modules and import it back.

## Testing Guidelines
Use `pytest` (`pytest -q`) and keep test directories aligned with `src/`. Name tests descriptively, e.g., `test_enrollment_trend_handles_missing_rows`. Store minimal fixture CSVs in `tests/fixtures/` and prefer parametrized cases to cover multiple academic years. Target high coverage for validation utilities and any calculations feeding chart annotations or filters.

## Commit & Pull Request Guidelines
Adopt Conventional Commits (`feat:`, `fix:`, `data:`, etc.). Squash noisy work before merging, link related issues, and summarize dataset revisions (rows added, filters applied) in the PR body. Include refreshed chart thumbnails or CLI output when behavior changes, call out manual steps reviewers should run, and confirm `ruff`/`pytest` status prior to requesting review.

## Security & Data Handling
Exclude secrets and PII; store credentials in an ignored `.env`. Share derived datasets only at institutional or cohort granularity. Document external data pulls and licensing notes in PRs so reviewers can verify redistribution rights.
