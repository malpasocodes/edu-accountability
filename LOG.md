# Change Log

| Date | Change | Details | Files |
| --- | --- | --- | --- |
| 2025-09-25 | Added federal loan scatter charts | Introduced four- and two-year federal loan vs graduation rate scatter visuals to mirror Pell comparisons. | `app.py`, `src/charts/loan_vs_grad_scatter_chart.py` |
| 2025-09-25 | Added Federal Loans section | Introduced a Federal Loans section with top-dollar charts for four- and two-year institutions sourced from the federal loan dataset. | `app.py`, `src/charts/loan_top_dollars_chart.py` |
| 2025-09-25 | Streamlined value grid UI | Removed enrollment legend from the value grid charts and increased quadrant tab font size for readability. | `src/charts/cost_vs_grad_chart.py` |
| 2025-09-25 | Added landing overview | Introduced a project overview landing page so Streamlit opens with context before navigating to charts. | `app.py` |
| 2024-11-24 | Updated enrollment filter | Enrollment control now uses fixed setpoints (0, 1k, 2.5k, 5k, 10k, 25k, 50k, 100k cap). | `src/dashboard/cost_vs_grad.py` |
| 2024-11-24 | Added two-year dashboard view | Introduced dual cost vs graduation charts for 4-year and 2-year institutions with shared filters. | `app.py`, `src/dashboard/cost_vs_grad.py`, `src/charts/cost_vs_grad_chart.py` |
| 2024-11-24 | Extended dataset builder | Builder now materializes four-year and two-year tuition vs graduation exports. | `src/data/build_tuition_vs_graduation.py`, `src/data/datasets.py`, `data/processed/tuition_vs_graduation.csv`, `data/processed/tuition_vs_graduation_two_year.csv` |
| 2024-11-24 | Added dataset builder | Added script to regenerate tuition vs graduation export for sectors 1-3 and refreshed processed CSV. | `src/data/build_tuition_vs_graduation.py`, `data/processed/tuition_vs_graduation.csv` |
| 2024-11-24 | Refactor committed | Finalized Streamlit refactor, modularizing dashboard logic for long-term maintenance. | `app.py`, `src/` |
| 2024-11-24 | Refactored Streamlit entry point | Moved business logic into `src/` modules and slimmed down `app.py`. | `app.py`, `src/` |
| 2024-11-24 | Added contributor guide | Replaced prior content with concise repository guidelines for agents. | `AGENTS.md` |
| 2024-11-24 | Initialized logbook | Created ongoing markdown log for tracking repository updates. | `LOG.md` |

## Update Instructions
- Append new rows with the current date (ISO format) and a short title.
- Summarize the change in one sentence; link to issues or PRs when relevant.
- Reference touched paths using backticks to keep entries scannable.
- Keep the table sorted with newest entries on top to surface recent work.
