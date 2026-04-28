# AGENTS.md

Guidelines for agentic coding agents working in this repository.

## Project Overview

Django 5.2 + Django REST Framework backend (Python 3.13) using PostgreSQL,
JWT auth (`djangorestframework-simplejwt`), `django-filter`, and
`django-model-utils`. Dependencies are managed with `uv`. Apps live under
`src/`: `caged/` (project config), `authentication/`, `gathering/`.

## Environment & Setup

- Python: `3.13` (see `.python-version`).
- Package manager: `uv` (see `pyproject.toml`, `uv.lock`).
- Install deps: `uv sync --locked`
- Required env vars (loaded via `python-dotenv` from `.env`):
  `SECRET_KEY`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`,
  `DATABASE_HOST`, `DATABASE_PORT`.
- Local Postgres: `docker compose up -d postgres`.

## Build / Run / Lint / Test

All commands run via `uv run` from the repo root.

- Run dev server: `uv run src/manage.py runserver 0.0.0.0:8000`
- Make migrations: `uv run src/manage.py makemigrations`
- Apply migrations: `uv run src/manage.py migrate`
- Create superuser: `uv run src/manage.py createsuperuser`
- Django shell: `uv run src/manage.py shell`
- Run all tests: `uv run src/manage.py test`
- Run tests for one app: `uv run src/manage.py test authentication`
- Run a single test class: `uv run src/manage.py test authentication.tests.UserTests`
- Run a single test method: `uv run src/manage.py test authentication.tests.UserTests.test_create`
- Keep test DB between runs (faster): add `--keepdb`
- Verbose test output: add `-v 2`
- Lint: `uv run ruff check .`
- Auto-fix lint issues: `uv run ruff check --fix .`
- Format: `uv run ruff format .`
- Check formatting only: `uv run ruff format --check .`

Always run lint + format + tests before declaring work complete.

## Project Layout

- `src/manage.py` — Django entrypoint.
- `src/caged/` — project settings, root `urls.py`, WSGI/ASGI.
- `src/<app>/` — Django apps. Each contains `models.py`, `views.py`,
  `serializers.py`, `urls.py`, `admin.py`, `permissions.py` (when needed),
  `managers.py` (custom managers), `migrations/`, `tests.py`.
- New apps: create under `src/`, register in `INSTALLED_APPS` in
  `src/caged/settings.py`, and include their `urls` from `src/caged/urls.py`.

## Code Style

Style is enforced by `ruff` (the only configured tool). No project-level
`[tool.ruff]` section exists, so ruff defaults apply: 4-space indent,
88-char line length, double quotes, trailing-comma friendly.

### Imports

- Order: stdlib → third-party (`django`, `rest_framework`, etc.) → local.
- Separate groups with a blank line. One import per line for `from` imports
  with multiple names: prefer the parenthesised multi-line form when long.
- Use **relative imports inside an app** (`from .models import User`,
  `from .serializers import ...`) and **absolute imports across apps**
  (`from authentication.models import User`).
- Never use wildcard imports.

### Formatting & Types

- Double quotes for strings; f-strings for interpolation.
- Trailing commas in multi-line literals/calls (ruff-format style).
- Type hints are encouraged on new helpers and methods (e.g.
  `def get_user_from_jwt_raw_token(self) -> User:`). Annotate return types
  on non-trivial functions; DRF view methods may omit annotations to match
  existing style.
- Use `pathlib.Path` (not `os.path`) for filesystem work in new code.

### Naming Conventions

- Modules/packages: `lower_snake_case`.
- Classes (models, serializers, views, viewsets): `PascalCase`
  (e.g. `UserViewSet`, `LoginSerializer`, `ResetPasswordView`).
- Functions, methods, variables: `snake_case`.
- Constants and Django settings: `UPPER_SNAKE_CASE`.
- Django `TextChoices` members: `UPPER_SNAKE_CASE` (see
  `User.Roles` in `src/authentication/models.py:12`).
- View classes end in `View`/`ViewSet`; serializers end in `Serializer`;
  managers end in `Manager`.
- URL names use `kebab-case` paths and `snake_case` `name=` identifiers.

### Models & Migrations

- Inherit `TimeStampedModel` from `model_utils.models` for `created`/
  `modified` timestamps when relevant.
- Custom user model lives at `authentication.User`
  (`AUTH_USER_MODEL = "authentication.User"`); reference users via
  `settings.AUTH_USER_MODEL` or `get_user_model()`, never import `User`
  directly from `django.contrib.auth`.
- Always commit generated migration files. Never edit applied migrations;
  create a new migration instead.

### Views, Serializers, Permissions

- Prefer DRF `viewsets.ModelViewSet` / `generics.*` / `APIView` consistent
  with existing patterns in `src/authentication/views.py`.
- Default permission is `IsAuthenticated` (set globally in
  `REST_FRAMEWORK`); override per-view with `permission_classes` or
  `get_permissions()` when needed.
- Use `serializer.is_valid(raise_exception=True)` to surface validation
  errors as 400 responses.
- Return `rest_framework.response.Response` with explicit
  `status=status.HTTP_*` codes.
- Pagination is `PageNumberPagination` with `PAGE_SIZE = 20`; filter
  backend is `DjangoFilterBackend`.

### Error Handling

- Let DRF translate `serializer.is_valid(raise_exception=True)` and
  `get_object_or_404` into proper HTTP responses; do not wrap them in
  broad `try/except`.
- Avoid bare `except:` and `except Exception:`; catch the narrowest
  exception that applies (e.g. `TokenError` in `RefreshTokenView`).
- User-facing `detail` messages are written in **Brazilian Portuguese**
  (`LANGUAGE_CODE = "pt-br"`); keep code, identifiers, and comments in
  English.
- Never log or return secrets, JWTs, or password hashes.

### Tests

- Use Django's `TestCase` (`from django.test import TestCase`) or DRF's
  `APITestCase` for endpoint tests.
- Place tests in each app's `tests.py` (or a `tests/` package with
  `__init__.py`). Test classes: `PascalCase` ending in `Tests`; test
  methods: `test_<behavior>`.
- Tests must be hermetic: do not depend on `.env` or external services
  beyond the configured Postgres test DB.

## Cursor / Copilot Rules

No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md`
files exist in this repo at the time of writing. If any are added later,
fold their guidance into this file.

## Agent Workflow Notes

- Plan multi-step work with the todo tool; keep one task in progress.
- Prefer editing existing files over creating new ones.
- Do not commit `.env` or any file containing secrets.
- Do not run `git commit`, `git push`, or destructive git commands unless
  the user explicitly requests it.
