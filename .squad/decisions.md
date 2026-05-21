# Squad Decisions

## Active Decisions

### 2026-05-21T15:31:09.000-05:00: Docker deployment migration architecture
**By:** Scrooge (Lead)

Standardize duckiehunt on a single env-driven Django settings module, a single deployment-oriented `docker-compose.yml`, and a build-once/promote-later image pipeline modeled on tracker-platform, while preserving local developer conveniences through local env/profile overlays rather than separate environment-specific deploy files.

**Details:** The current deployment path has configuration drift across four compose files, host-mounted settings directories, and per-environment Django modules. Moving configuration into env files and secret mounts makes the container image portable, restores the repository as the source of truth, reduces production-only surprises, and creates a safer promotion path where production runs the exact image already validated in staging.

### 2026-05-21T16:09:33.231-05:00: Unified settings package entrypoint
**By:** Huey (Backend)

Use `django/duckiehunt/settings/__init__.py` as the new env-driven `duckiehunt.settings` entrypoint while keeping the existing per-environment modules in the `settings/` package for validation and rollback.

**Why:** A standalone `django/duckiehunt/settings.py` file would conflict with the existing `django/duckiehunt/settings/` directory on disk. Using the package entrypoint preserves the public import path (`duckiehunt.settings`) and keeps the legacy modules available until the team removes them in a later step.

### 2026-05-21T16:09:33.231-05:00: Preserve legacy runtime paths during Docker migration
**By:** Dewey (DevOps)

The new root Docker image/layout uses `/app/django`, `/app/data`, and `/app/uploads`, but creates compatibility symlinks for `/code`, `/db`, and `/uploads` inside the container.

**Why:** Step 4 and Step 5 can land now without simultaneously rewriting Django settings modules that still point at the legacy paths. This keeps the migration incremental: Compose and Docker can move to the new tracker-style shape first, while Huey can consolidate settings later without breaking staging or production mounts.

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
