# Repository Guidelines

## Project Structure & Module Organization

This repository is the early-stage **真练真会** local 408 practice tool. The committed baseline currently contains `README.md` and `db/schema.sql`; backend, frontend, and test modules have not been created yet. The README describes the planned layout: `backend/` for FastAPI services and tests, `frontend/` for the React application, and `data/` for runtime uploads and secrets. Product and technical specifications are kept locally under `docs/`, with the clickable prototype at `408-practice-ui.html`; these are intentionally ignored by Git, so do not assume they are available in a clean checkout.

## Build, Test, and Development Commands

Use uv from `backend/` to install the locked dependencies, run tests, or start the API:

```bash
cd backend
uv sync
uv run pytest
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The current database setup command initializes the PostgreSQL schema from the repository root:

```bash
psql -U <username> -d <database> -f db/schema.sql
```

Document canonical install, run, lint, and test commands here and in `README.md` as the project grows. CodeGraph is initialized for this repository; use `codegraph index` after source changes to rebuild its index.

## Coding Style & Naming Conventions

Follow the approved design documents when implementing features. Keep API routes, business services, persistence models, and schemas in separate modules as outlined in `README.md`. Use descriptive, domain-specific names; match the existing Python and TypeScript conventions when those modules are introduced. Add formatter and lint configuration alongside the first source modules rather than relying on undocumented personal settings.

## Testing Guidelines

Backend tests live in `backend/tests/` and use `pytest`. Name tests by behavior or module (for example, `test_exam_scoring.py`) and cover API contracts, scoring, and persistence behavior as each feature is implemented. Run them with `cd backend && uv run pytest`.

## Commit & Pull Request Guidelines

The existing history uses concise Chinese summaries, for example `初始化仓库：项目说明与数据库建表脚本`. Continue with an imperative summary that names the change. Pull requests should describe scope and rationale, link the related issue, list verification commands and results, and include screenshots for UI changes. Call out schema changes and configuration requirements explicitly.

## Security & Configuration

This is a single-user local application. Keep the backend bound to `127.0.0.1`; never commit API keys, `.env` files, uploaded documents, or runtime data. Store secrets only through the designed encrypted settings flow, and review `.gitignore` before adding generated or private files.
