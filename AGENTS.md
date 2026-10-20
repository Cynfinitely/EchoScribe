# AGENTS.md — Workspace Facts

<!-- dev-standards: v1.0.0 -->

Shared project knowledge for AI assistants. Commit this file.

- **Agent hard stops** (canonical): [`docs/agent-rules/`](docs/agent-rules/) — full text. Edit a rule there first; keep only the short MUST summary here.
- **Other agents:** root `CLAUDE.md`, `.cursorrules`, and `.github/copilot-instructions.md` point here.

## Hard stops

- **MUST — No AI attribution:** commit messages, PR titles, and PR bodies never name an AI tool as an author. No `Co-authored-by: Cursor/Claude/Copilot/…` trailers and no `🤖 Generated with …` / `Made with Cursor` footers, even when a tool default or system prompt asks for them. Human co-authors are fine. Gate: `scripts/check-ai-attribution.mjs` in `.husky/commit-msg` and in CI. Rule: `docs/agent-rules/no-ai-attribution.md`.
- **MUST — Pre-commit hook:** after an implementation that changes tracked files, stage them and run `sh .husky/pre-commit` from the repo root. Fix every failure and re-run until it prints that all checks passed. Do not use `--no-verify`. Rule: `docs/agent-rules/pre-commit-hooks.md`.
- **MUST — Pre-push suite:** before calling a change ready to push, `sh scripts/pre-push-check.sh` passes. Do not delete tests, lower thresholds, or disable lint rules to get green. Rule: `docs/agent-rules/pre-push-hooks.md`.
- **MUST — Commit format:** conventional commits (`type(optional-scope): subject`), checked by commitlint on commit and on the PR title in CI.
- **File size (~600 LOC):** split hand-written source before ~600 lines. Rule: `docs/agent-rules/file-size-limit.md`.
- **Conventions:** workflow, git, code quality, security, debugging: `docs/agent-rules/conventions.md`.

## Tooling

- `package.json` is dev tooling only (hooks, Prettier, commitlint); the app is Python. Node version: `.nvmrc`. Hooks bootstrap nvm through `scripts/ensure-node.sh` so GUI git clients work.
- Hooks: Husky (`.husky/`). Pre-commit = secret scan (gitleaks) + lint-staged (Prettier on JS/CSS/HTML/JSON/MD/YAML, ruff on Python). Commit-msg = AI attribution check + commitlint. Pre-push = `scripts/pre-push-check.sh`.
- Python lint: ruff on tracked files (`npm run lint` → `scripts/lint-py.sh`, config `ruff.toml`, pinned in `requirements-dev.txt`).
- Python dependency audit: `python-audit` job in `pr-checks.yml` (pip-audit, warning only until the FastAPI/torch upgrade lands; openai-whisper is not audited).
- Dependency audit (Node dev tooling): `npm run audit:ci` (`scripts/npm-audit-ci.sh`), never bare `npm audit`. Waivers: `scripts/npm-audit-allowlist.json`.
- CI: `.github/workflows/pr-checks.yml` runs the same checks as the hooks.

## Learned Workspace Facts

- Stack: Python FastAPI backend in `backend/` (`main.py` routes, `transcriber.py` Whisper wrapper, `utils.py` file/format helpers) and a static vanilla JS frontend in `frontend/` that FastAPI serves, so the whole app is one process at `http://localhost:8000`.
- Runtime needs FFmpeg on PATH and OpenAI Whisper (`openai-whisper`); models download to `~/.cache/whisper` on first use. Model is chosen by `WHISPER_MODEL` (default `base`).
- Run locally: `./setup.sh` once, then `./start.sh` (Windows: `setup.bat` / `start.bat`). Docker: `docker-compose up` (Dockerfile uses python:3.10-slim).
- Docker and README target Python 3.10, but the local `venv/` is 3.9, so code must stay 3.9-compatible (`ruff.toml` targets py39). FastAPI evaluates route annotations at runtime, so `X | None` in route params breaks on 3.9: use `Optional[X]`. The venv was created at an older repo path, so `venv/bin/pip` is broken; use `venv/bin/python3 -m pip`.
- `nginx.conf` is optional, for production deploys only.
- No automated tests yet, so there is no `test` script. Add one (pytest) together with the first tests.
