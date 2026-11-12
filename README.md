---
title: Kerbal Copilot
emoji: 🚀
colorFrom: indigo
colorTo: gray
sdk: gradio
sdk_version: 6.31.0
python_version: "3.12"
app_file: app.py
pinned: false
short_description: AI rocket-build assistant for modded KSP 1.12
---

# Kerbal Copilot (Mission Control)

An AI build assistant for Kerbal Space Program 1.12. It designs rockets from your installed
(modded) parts, computes delta-v and TWR in Python, draws the staging, remembers your builds,
and looks up mod updates. It runs on free OpenRouter models.

The block at the top of this file is the Hugging Face Space configuration. Keep it as the
first thing in the file.

## Commands

All commands run from the repo root after `uv sync --extra dev`.

| Command | Where | What it does |
|---|---|---|
| `uv run kerbal-copilot ingest --ksp "<KSP folder>" --upload` | Gaming PC | Builds `data/parts.db` from your install and uploads it |
| `uv run kerbal-copilot pull-data` | Laptop | Downloads the latest `parts.db` |
| `uv run kerbal-copilot search "vacuum engine" --role engine` | Anywhere | Searches parts |
| `uv run kerbal-copilot ask "Design a Mun flyby rocket"` | Anywhere | One agent turn in the terminal |
| `uv run python app.py` | Anywhere | Runs the web app on http://localhost:7860 |
| `uv run pytest -q` and `uv run ruff check .` | Anywhere | Tests and lint (CI runs these) |

Secrets go in `.env` (copy `.env.example`). Never commit `.env` or anything from GameData.

## Deploy

Pushing to `main` runs the tests, then uploads the app to the Hugging Face Space. The GitHub
repo needs the `HF_TOKEN` secret and the `HF_SPACE` variable.
