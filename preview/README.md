# Preview and refresh

The cards are generated from a real GitHub contribution snapshot. To refresh locally, provide a GitHub token with GraphQL access:

```sh
export GH_TOKEN=…
python scripts/fetch_github_data.py
STATIC=1 python scripts/render_readme_cards.py
python scripts/validate_svgs.py --browser
```

Install browser QA once with `python -m pip install -r requirements-dev.txt && python -m playwright install chromium`.

Open the local profile preview with `python scripts/preview.py` and visit `http://127.0.0.1:8000/preview/`. The workflow uses the repository's `GITHUB_TOKEN`, refreshes at 06:00 UTC, validates the cards, and commits only changed snapshots and SVGs.
