# experiment-flask

Python/Flask component of the bachelor's thesis **"CI/CD Pipeline Resilience Research,"** exploring simple ML classifiers for preventive failure detection on CI/CD pipeline signals.

Companion repo: [`experiment-java`](https://github.com/k6gnn/experiment-java) — the Spring Boot fault-injection target application and multi-CI pipeline configs this component analyzes.

## Structure

- `app/` — Flask application
- `models/` — trained classifier model(s) used for failure prediction
- `experiment_results/` — output data and metrics from experiment runs
- `scripts/` — data collection, training, and evaluation scripts
- `tests/` — pytest test suite
- `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` — CI pipelines exercising this component's own test suite
- `requirements.txt`, `pyproject.toml`, `pytest.ini` — Python project configuration

## What this demonstrates

- Applying an ML classifier to pipeline signals (from `experiment-java`'s fault-injection runs) to flag likely failures before they happen, rather than only reacting after a build breaks
- A tested, CI-integrated Python service — not just a notebook: pytest coverage plus its own GitHub Actions/GitLab CI/Jenkins pipelines
- 85 commits of iterative experimentation

## Results

*[Insert real evaluation numbers: classifier accuracy/precision/recall on your test set, or whatever metric you evaluated against, plus a sentence on what "preventive" detection meant in practice — e.g. how far in advance the classifier flagged a failure.]*

## Related

- Fault-injection target and multi-CI pipelines: [`experiment-java`](https://github.com/k6gnn/experiment-java)
- Full thesis: *[link if available]*
