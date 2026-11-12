# Notes for AI assistants

Follow [docs/anti_slop_guidelines.md](docs/anti_slop_guidelines.md) for all writing and code in this repo.

- Every number you write must come from a notebook cell, a pipeline output, or a cited source.
- Shared constants (paths, panel breaks, lattice rule, holidays file) live in `src/config.py`. Import them; don't redefine them.
- The project has two outputs (PLAN.md section 0): Output 1 = JogjaPulse vs Google (notebooks 01-02), Output 2 = applied analytics (notebooks 03-06, `dashboard/app.py`). Output 2 rules live in `src/applied.py`; the notebooks and the dashboard both import them.
- Pipeline order: `src/download_data.py`, `src/fetch_google_mobility.py`, `src/clean.py`, `src/build_features.py`. Notebooks read `data/processed/`.
- Join kapanewon on `kapanewon_code`, never on the name ("JETIS" exists twice).
- Never compare raw JogjaPulse counts across time. See the normalisation rules in PLAN.md.
