# Django-Q2 Background Task Queue

## Overview

Duckiehunt uses [Django-Q2](https://django-q2.readthedocs.io/) to process heavy I/O tasks asynchronously. When a user submits a duck sighting, the response is returned immediately — photo uploads, social media posts, and email notifications happen in the background.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Request                       │
│                                                     │
│  POST /mark/                                        │
│    1. Validate form                                 │
│    2. Save DuckLocation to DB                       │
│    3. Save image to disk (if provided)              │
│    4. Queue background tasks ← async_task()         │
│    5. Return redirect immediately                   │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              SQLite Task Queue                        │
│         (django_q_ormq table in duckiehunt.db)       │
│                                                     │
│  Tasks are stored as rows in the database.           │
│  The qcluster worker polls for new tasks.            │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              Q Cluster (Worker Process)               │
│         python manage.py qcluster                    │
│                                                     │
│  Picks up tasks, executes them, logs results.        │
│  Runs as a separate container in production.         │
└─────────────────────────────────────────────────────┘
```

## Current Tasks

All task functions live in `django/duck/tasks.py`:

| Task Function | Triggered When | What It Does | Timeout |
|---------------|---------------|--------------|---------|
| `upload_photo` | User submits sighting with image | Uploads saved file to Flickr/active provider, updates existing DuckLocationPhoto record | 120s |
| `share_to_social` | Approved sighting is submitted | Posts to Facebook/Instagram (if configured) | 120s |
| `send_email_notification` | Approved sighting is submitted | Sends email via SendGrid to configured recipients | 120s |

### Task Flow Diagram

```
mark_process() in views.py
│
├── image provided?
│   └── Yes → save_uploaded_file() to disk
│            → create DuckLocationPhoto(local_path=...)
│            → async_task('duck.tasks.upload_photo', ...)
│
├── approved == 'Y'?
│   ├── async_task('duck.tasks.send_email_notification', ...)
│   └── async_task('duck.tasks.share_to_social', ...)
│
└── return HttpResponseRedirect (user sees location page)
```

## Configuration

Settings are in `django/duckiehunt/settings/__init__.py`:

```python
Q_CLUSTER = {
    "name": "duckiehunt",
    "workers": 2,           # Number of worker threads
    "timeout": 120,         # Max seconds a task can run
    "retry": 180,           # Retry failed tasks after this many seconds
    "queue_limit": 50,      # Max tasks queued before blocking
    "bulk": 10,             # How many tasks to process per cycle
    "orm": "default",       # Use the default database as the broker
    "sync": DJANGO_Q_SYNC,  # When True, tasks run inline (for testing)
}
```

### Key Settings Explained

- **`orm: "default"`** — Uses your existing SQLite database as the message broker. No Redis or RabbitMQ needed.
- **`workers: 2`** — Two threads process tasks concurrently. Sufficient for current traffic.
- **`timeout: 120`** — If a task runs longer than 2 minutes, it's killed and marked as failed.
- **`retry: 180`** — If a task fails, it's retried after 3 minutes.
- **`sync`** — Controlled by `DJANGO_Q_SYNC` env var. When `True`, `async_task()` runs the function immediately (synchronous). Used in unit tests.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DJANGO_Q_SYNC` | Run tasks synchronously (for tests) | `False` |

No other env vars are needed — Django-Q2 inherits database config from Django settings.

## Deployment

### Docker Compose (Production & Staging)

```yaml
services:
  duckiehunt:
    image: ghcr.io/lastcoolnameleft/duckiehunt:latest
    command: gunicorn duckiehunt.wsgi  # web server

  worker:
    image: ghcr.io/lastcoolnameleft/duckiehunt:latest
    command: python manage.py qcluster  # task worker
    depends_on:
      - duckiehunt
```

Both containers share the same image, env vars, and database volume. The worker is namespaced by `COMPOSE_PROJECT_NAME`:
- Production: `duckiehunt-worker`
- Staging: `duckiehunt-stg-worker`

### Local Development

`scripts/run-local.sh` starts both the dev server and worker in one terminal:

```bash
./scripts/run-local.sh
# Starts: runserver (foreground) + qcluster (background)
# Ctrl+C stops both
```

## Monitoring

### Django Admin

Django-Q2 adds these to the admin panel (`/admin/`):

- **Successful tasks** — completed tasks with results
- **Failed tasks** — tasks that errored (with tracebacks)
- **Scheduled tasks** — recurring/future tasks (if configured)
- **Queued tasks** — tasks waiting to be processed

### Logs

The worker logs to stdout (visible in `docker logs duckiehunt-worker`):

```
[Q] INFO Process-1 processing [duck.tasks.upload_photo]
[Q] INFO Process-1 success [duck.tasks.upload_photo] (2.34s)
```

Task functions also use Python logging:
```python
logger.info("Photo uploaded for duck #%s (location %s)", duck_id, duck_location_id)
logger.error("Photo upload failed for duck #%s", duck_id)
```

### Health Check

```bash
# Is the worker running?
docker ps | grep worker

# Recent task activity
docker logs duckiehunt-worker --tail 50

# Via Django shell
python manage.py shell -c "from django_q.models import Success, Failure; print(f'OK: {Success.objects.count()}, Failed: {Failure.objects.count()}')"
```

## Error Handling

Each task function wraps its work in try/except:

- **Photo upload fails** → logged as error (Sentry captures it); local `/media/...` fallback remains visible while provider fields stay empty
- **Social share fails** → logged as error, does not affect other providers or the sighting
- **Email fails** → logged as error, sighting unaffected

Tasks that raise unhandled exceptions are:
1. Marked as failed in Django-Q's `Failure` table
2. Retried after `retry` seconds (180s)
3. Visible in Django admin under "Failed tasks"

## Testing

Unit tests set `DJANGO_Q_SYNC=1` so tasks execute inline:

```bash
cd django && DJANGO_Q_SYNC=1 python manage.py test duck.tests --verbosity=2
```

Tests mock `duck.views.async_task` to verify tasks are queued with correct arguments without actually executing them.

## Future Candidates

Tasks that would benefit from being moved to the queue:

| Candidate | Reason |
|-----------|--------|
| Content moderation (Azure API) | External API call, ~0.5-1s per request |
| Image thumbnail generation | CPU-intensive if moving off Flickr |
| Facebook/IG token refresh | Scheduled task (Django-Q2 supports cron) |
| Stale submission cleanup | Scheduled nightly task |
| Sitemap regeneration | Scheduled, avoid on-demand computation |

## Adding a New Task

1. Add function to `django/duck/tasks.py`:
   ```python
   def my_new_task(arg1, arg2):
       """Docstring explaining what this does."""
       from .models import MyModel  # import inside function
       # ... do work ...
   ```

2. Queue it from a view or other code:
   ```python
   from django_q.tasks import async_task
   async_task('duck.tasks.my_new_task', arg1, arg2)
   ```

3. For scheduled/recurring tasks:
   ```python
   from django_q.tasks import schedule
   schedule(
       'duck.tasks.refresh_tokens',
       schedule_type='D',  # Daily
   )
   ```

### Important Patterns

- **Import models inside the function** — avoids circular imports and ensures the Django app registry is ready.
- **Accept IDs, not model instances** — tasks are serialized to the database; pass `duck_location_id`, not the object itself.
- **Fail gracefully** — wrap in try/except, log errors, don't let one task's failure cascade.
- **Keep tasks idempotent** — they may be retried on failure.
