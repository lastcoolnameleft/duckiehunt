# Duckiehunt Technical Constitution

> Generated: 2026-04-08
> Source Repository: lastcoolnameleft/duckiehunt
> Purpose: Enable external development of migration-compatible features
> **Scope:** Full

---

## Table of Contents

1. [Project Identity](#1-project-identity)
2. [Technology Stack](#2-technology-stack)
3. [Dependencies](#3-dependencies)
4. [Database & Data Layer](#4-database--data-layer)
5. [API & Integration Patterns](#5-api--integration-patterns)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [Infrastructure](#7-infrastructure)
8. [Coding Patterns & Conventions](#8-coding-patterns--conventions)
9. [Testing Strategy](#9-testing-strategy)
10. [CI/CD & DevOps](#10-cicd--devops)
11. [Configuration Management](#11-configuration-management)
12. [Sample Code Patterns](#12-sample-code-patterns)
13. [Migration Contract](#13-migration-contract)
14. [Interface Definitions](#14-interface-definitions)
15. [Enum Definitions](#15-enum-definitions)
16. [Model & DTO Definitions](#16-model--dto-definitions)
17. [Base Class Contracts](#17-base-class-contracts)
18. [Quick Reference](#18-quick-reference)

---

## 1. Project Identity

### Project Name
**Duckiehunt** — [duckiehunt.com](https://duckiehunt.com)

### Purpose
A web application for tracking rubber ducks as they travel around the world. Users find physical rubber ducks, log their location (with GPS coordinates, photos, and comments), and track the total distance each duck has traveled.

### Business Domain
Social / community-driven geolocation tracking — similar to geocaching or "Where's George?" for rubber ducks.

### Target Users
- **Public visitors:** Browse duck locations on a map, view duck travel histories
- **Authenticated users:** Log ("mark") duck sightings with GPS, photos, and comments
- **Admins:** Manage ducks, locations, and photos via Django admin

### Key Features
- Interactive world map showing all duck locations
- Per-duck detail pages with travel history and photos
- "Mark a duck" form with GPS (via Google Maps), photo upload (Flickr), and reCAPTCHA
- Social login (Google OAuth2, Facebook OAuth2)
- Distance calculation between duck sightings (haversine)
- Email notifications on duck sightings (SendGrid)
- REST-style JSON APIs for map data

### Repository Structure
```
duckiehunt/
├── django/                  # Main application code
│   ├── duck/                # Primary Django app
│   │   ├── models.py        # Data models (Duck, DuckLocation, etc.)
│   │   ├── views.py         # View functions (pages)
│   │   ├── apis.py          # JSON API endpoints
│   │   ├── forms.py         # Django forms (DuckForm)
│   │   ├── marker.py        # Business logic (create duck, add location, Flickr upload)
│   │   ├── admin.py         # Django admin registrations
│   │   ├── urls.py          # URL routing
│   │   ├── templates/       # HTML templates (Django template language)
│   │   ├── static/          # CSS, JS, icons (Bootstrap-based)
│   │   ├── migrations/      # Django DB migrations
│   │   └── tests/           # Unit tests
│   ├── duckiehunt/          # Django project config
│   │   ├── settings/        # Per-environment settings modules
│   │   ├── urls.py          # Root URL config
│   │   └── wsgi.py          # WSGI entry point
│   ├── manage.py            # Django management CLI
│   ├── requirements.in      # Direct dependencies (pip-compile input)
│   └── requirements.txt     # Pinned dependencies (pip-compile output)
├── charts/                  # Helm charts (Kubernetes)
├── config/                  # Kubernetes / cluster config
├── db/                      # Database files
├── docker-compose/          # Docker Compose files per environment
├── docs/                    # Development, deployment, testing docs
├── playwright/              # Playwright E2E config
├── startup/                 # Systemd service & startup scripts
├── tests/                   # Playwright E2E tests
├── uploads/                 # File upload staging area
├── Dockerfile               # Container image definition
├── .editorconfig            # Editor formatting rules
└── .github/workflows/       # GitHub Actions CI/CD
```

---

## 2. Technology Stack

### 2.1 Languages
| Language | Version | Usage |
|----------|---------|-------|
| **Python** | 3.x (slim Docker image) | Backend application code |
| **HTML/CSS/JavaScript** | N/A | Frontend templates, Bootstrap UI |

### 2.2 Frameworks & Runtimes
| Framework | Version | Purpose |
|-----------|---------|---------|
| **Django** | 5.0.9 | Web framework (views, ORM, admin, forms) |
| **Bootstrap** | 4.x | Frontend CSS/JS framework |
| **jQuery** | Bundled | Frontend DOM manipulation |

### 2.3 Build Tools
| Tool | Purpose |
|------|---------|
| **pip-compile** (pip-tools) | Dependency pinning (`requirements.in` → `requirements.txt`) |
| **Docker** | Container builds (`python:3-slim` base image) |
| **Docker Compose** | Local/staging/production orchestration |

### Build Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python manage.py runserver 0.0.0.0:8000

# Run via Docker
docker compose -f docker-compose/mac.yaml up --build

# Generate pinned requirements
pip install pip-tools && pip-compile
```

---

## 3. Dependencies

### 3.1 Third-Party Libraries

**Core:**
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| django | 5.0.9 | Web framework | BSD-3 |
| whitenoise | 6.6.0 | Static file serving | MIT |

**Authentication:**
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| social-auth-core | 4.5.3 | OAuth2 social login backends | BSD-3 |
| social-auth-app-django | 5.4.1 | Django integration for social auth | BSD-3 |
| oauthlib | 3.2.2 | OAuth request signing | BSD-3 |
| requests-oauthlib | 2.0.0 | OAuth session support | ISC |
| pyjwt | 2.8.0 | JWT token handling | MIT |
| cryptography | 43.0.1 | Crypto primitives for auth | Apache-2.0/BSD-3 |
| python3-openid | 3.2.0 | OpenID support | Apache-2.0 |

**Media & External APIs:**
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| flickr-api | 0.7.7 | Flickr photo upload/management | BSD |
| requests | 2.32.0 | HTTP client | Apache-2.0 |

**Forms:**
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| django-recaptcha | 4.0.0 | Google reCAPTCHA form field | BSD-3 |

**Geolocation:**
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| haversine | 2.8.1 | Distance calculation between GPS coordinates | MIT |

**Utilities:**
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| defusedxml | 0.8.0rc2 | Safe XML parsing | PSF |
| six | 1.16.0 | Python 2/3 compat (flickr-api dep) | MIT |

### 3.2 Internal/Shared Libraries
None. The project is self-contained with a single Django app (`duck`).

---

## 4. Database & Data Layer

### 4.1 Database Technology
- **Database:** MySQL (production/development via Azure Database for MySQL)
- **Connection:** Standard Django `DATABASES` dict with `django.db.backends.mysql`
- **Driver:** `mysqlclient` (installed via `default-libmysqlclient-dev` in Dockerfile)

**Local development:** Connect to a remote MySQL instance or run a local MySQL container. The `DJANGO_SETTINGS_MODULE` environment variable selects the settings file (and thus the DB connection).

### 4.2 ORM / Data Access
- **ORM:** Django ORM (built-in)
- **Migrations:** Django migrations (`python manage.py migrate`)
- **Query style:** Django QuerySet API — `Model.objects.filter()`, `get()`, `all()`, `values()`, `aggregate()`

### 4.3 Schema Documentation

#### Entity: Duck
```
Table: duck
Description: A physical rubber duck being tracked
Fields:
  - duck_id: IntegerField (PRIMARY KEY, user-assigned) — The duck's tag number
  - create_time: DateTimeField (blank) — When the duck was first registered
  - name: CharField(128) (blank, default=None) — Name given to the duck
  - comments: TextField (blank, default=None) — Notes about the duck
  - total_distance: FloatField (blank, default=0) — Cumulative miles traveled
  - approved: CharField(1) (default='Y') — Approval flag
Relationships:
  - One-to-Many → DuckLocation (duck_id FK)
```

#### Entity: DuckLocation
```
Table: duck_location
Description: A single sighting/location report for a duck
Fields:
  - duck_location_id: AutoField (PRIMARY KEY)
  - duck: ForeignKey(Duck, CASCADE, null) — The duck this location belongs to
  - user: ForeignKey(User, CASCADE, null) — The user who reported this sighting
  - link: TextField (blank, null) — External link
  - latitude: FloatField (blank, null) — GPS latitude
  - longitude: FloatField (blank, null) — GPS longitude
  - comments: TextField (blank, null) — User comments about the sighting
  - flickr_photo_id: BigIntegerField (blank, null) — Legacy Flickr photo ID
  - duck_history_id: IntegerField (blank, null) — Legacy history reference
  - date_time: DateTimeField (blank, null) — When the sighting occurred
  - location: TextField (blank, null) — Human-readable location name
  - approved: CharField(1) (blank, null) — Approval flag
  - distance_to: FloatField (blank, null) — Miles from previous sighting
Relationships:
  - Many-to-One → Duck (duck_id FK)
  - Many-to-One → User (user_id FK, Django auth User)
  - One-to-Many → DuckLocationLink
  - One-to-Many → DuckLocationPhoto
```

#### Entity: DuckLocationLink
```
Table: duck_location_link
Description: External links associated with a duck sighting
Fields:
  - duck_location_link_id: AutoField (PRIMARY KEY)
  - duck_location: ForeignKey(DuckLocation, DO_NOTHING, null)
  - link: CharField(100) (blank, null)
Relationships:
  - Many-to-One → DuckLocation
```

#### Entity: DuckLocationPhoto
```
Table: duck_location_photo
Description: Photos associated with a duck sighting (stored on Flickr)
Fields:
  - duck_location_photo_id: AutoField (PRIMARY KEY)
  - duck_location: ForeignKey(DuckLocation, DO_NOTHING, null)
  - flickr_photo_id: BigIntegerField (blank, null) — Flickr photo ID
  - flickr_thumbnail_url: TextField (blank, null) — Flickr thumbnail URL
Relationships:
  - Many-to-One → DuckLocation
```

### 4.4 Data Patterns
- **No repository pattern.** Models are queried directly via Django ORM in views, APIs, and `marker.py`.
- **No Unit of Work pattern.** Django's default auto-commit transaction mode is used.
- **Aggregation:** `DuckLocation.objects.filter(...).aggregate(Sum('distance_to'))` for total distance.
- **Ordering:** `.order_by('-date_time')` for most recent location.
- **Values projection:** `.values('duck_id', 'duck__name', 'latitude', 'longitude', 'comments')` for API responses.
- **Natural keys:** `Duck.natural_key()` returns `{'duck_id', 'name', 'total_distance'}` for serialization.

---

## 5. API & Integration Patterns

### 5.1 API Style
- **REST-style JSON endpoints** (read-only, no framework like DRF)
- **No API versioning** — all endpoints live at `/api/...`
- **No authentication on API endpoints** — they are public read-only

### 5.2 URL Patterns

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/ducks` | List all ducks (id, name, distance) |
| GET | `/api/duck/<int:duck_id>` | Single duck detail |
| GET | `/api/locations` | All duck locations (for map) |
| GET | `/api/duck/<int:duck_id>/locations` | Locations for a specific duck |
| GET | `/api/location/<int:duck_location_id>` | Single location detail |

### 5.3 Response Patterns

**Single object response:**
```json
{
    "duck_id": 1,
    "name": "Tommy's Duckie",
    "total_distance": 12345.67,
    "create_time": "2018-09-01T22:35:00Z",
    "approved": "Y"
}
```

**List response (no envelope):**
```json
[
    {"duck_id": 1, "name": "Tommy's Duckie", "total_distance": 12345.67},
    {"duck_id": 2, "name": "Quackers", "total_distance": 567.89}
]
```

**Location list response:**
```json
[
    {
        "duck_id": 1,
        "duck__name": "Tommy's Duckie",
        "latitude": 32.95,
        "longitude": -96.90,
        "comments": "Found at the park"
    }
]
```

**No error envelope.** Errors use Django's default 404 (via `get_object_or_404`).

### 5.4 External Integrations

| Service | Purpose | Library |
|---------|---------|---------|
| **Flickr API** | Photo upload and thumbnail retrieval | `flickr-api` |
| **Google Maps JS API** | Map rendering, geocoding in templates | Client-side JS |
| **Google reCAPTCHA** | Bot protection on mark form | `django-recaptcha` |
| **SendGrid SMTP** | Email notifications on duck sightings | Django `EmailMessage` |
| **Microsoft Clarity** | Frontend analytics | Client-side JS snippet |

---

## 6. Authentication & Authorization

### Mechanism
- **Social OAuth2** via `social-auth-app-django` (Python Social Auth)
- **Backends:** Google OAuth2, Facebook OAuth2

### Configuration
```python
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
)
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'mark'
```

### URL Routes
| URL | Purpose |
|-----|---------|
| `/login` | Login page (shows Google/Facebook buttons) |
| `/logout` | Logs out user, redirects to `/` |
| `/oauth/` | Social auth callback URLs (`social_django.urls`) |
| `/profile` | User profile page |

### Authorization Pattern
- **`@login_required` decorator** on protected views (e.g., `mark`)
- Unauthenticated users are redirected to `/login?next=<original_url>`
- **No RBAC/permission system** beyond Django's built-in user model
- API endpoints are **public** (no auth required for read-only JSON)
- Admin interface uses Django's built-in admin auth

### How to Mock Auth for Isolated Development
- Use Django's `Client.force_login(user)` in tests
- Create a test user: `User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')`
- For Playwright E2E tests, use `storage_state="auth.json"` to persist login sessions
- The `mark_captcha` view variant bypasses `@login_required` (uses reCAPTCHA instead)

---

## 7. Infrastructure

### 7.1 Cloud / Hosting
| Service | Purpose |
|---------|---------|
| **Azure VM** (DS2, East US) | Application hosting |
| **Azure Database for MySQL** | Production database |
| **GitHub Container Registry (ghcr.io)** | Docker image registry |
| **Flickr** | Photo storage |
| **SendGrid** | Email delivery |
| **Let's Encrypt** | TLS certificates (via Traefik) |

### 7.2 Infrastructure as Code
- **Helm Charts** (`charts/duckiehunt/`) — Kubernetes deployment (legacy/alternative)
- **Docker Compose** — Primary deployment method per environment
- **Traefik** — Reverse proxy with auto-TLS (configured via Docker labels)
- **Systemd service** (`startup/duckiehunt.service`) — Auto-start on VM boot

### 7.3 Environment Strategy

| Environment | Settings Module | Docker Compose File | Domain |
|-------------|----------------|---------------------|--------|
| Development | `duckiehunt.settings.development` | `docker-compose/development.yaml` | `dev.duckiehunt.com` |
| Staging | `duckiehunt.settings.staging` | `docker-compose/staging.yaml` | staging subdomain |
| Production | `duckiehunt.settings.production` | `docker-compose/production.yaml` | `duckiehunt.com` / `www.duckiehunt.com` |
| Local/Mac | `duckiehunt.settings.local` | `docker-compose/mac.yaml` | `localhost` |

**Environment selection:** Set `DJANGO_SETTINGS_MODULE` env var in Docker Compose.

**Secret management:** Settings files with credentials are stored on the VM at `/data/duckiehunt-<env>/settings/` and volume-mounted into containers. Settings files are in `.gitignore`. A `template.py` provides the structure with empty values.

---

## 8. Coding Patterns & Conventions

### 8.1 Architecture Pattern
- **Django MVT (Model-View-Template)** — standard Django architecture
- Views are **function-based** (not class-based views)
- Business logic lives in **`marker.py`** (service layer), not in views
- API endpoints live in **`apis.py`**, separated from template-rendering views
- **No dependency injection** — modules import directly

### 8.2 Code Organization
```
django/duck/           # Single Django app
├── models.py          # All models in one file
├── views.py           # All page views (function-based)
├── apis.py            # All JSON API endpoints (function-based)
├── forms.py           # Django form classes
├── marker.py          # Business logic / service functions
├── admin.py           # Admin registrations
├── urls.py            # URL routing for the app
├── apps.py            # App configuration
├── templates/duck/    # HTML templates
├── static/            # CSS, JS, vendor libs
├── migrations/        # DB migrations
└── tests/             # Unit tests
```

### 8.3 Coding Style

**Formatting:**
- Tab indentation (`.editorconfig`: `indent_style = tab`)
- UTF-8 charset
- Unix-style line endings (LF)
- Insert final newline

**Naming Conventions:**
| Element | Convention | Example |
|---------|------------|---------|
| Python files | lowercase, underscores | `marker.py`, `duck_location.py` |
| Django models | PascalCase | `DuckLocation`, `DuckLocationPhoto` |
| DB tables | snake_case (via `Meta.db_table`) | `duck_location`, `duck_location_photo` |
| View functions | snake_case | `duck_list`, `mark_process` |
| API functions | snake_case | `duck_detail`, `locations_all` |
| URL paths | lowercase, no trailing slash on most | `/api/duck/<int:duck_id>` |
| Templates | lowercase, hyphens | `detail-not-found.html` |

**Import style:**
```python
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
from .models import Duck, DuckLocation, DuckLocationPhoto
```

**Docstrings:** Brief single-line docstrings on view/function definitions.

### 8.4 Error Handling
- **404s:** `get_object_or_404(Model, pk=id)` — returns Django's default 404
- **Model not found in views:** Try/except with custom "not found" template:
  ```python
  try:
      duck = Duck.objects.get(pk=duck_id)
  except Duck.DoesNotExist:
      return render(request, 'duck/detail-not-found.html', {'duck_id': duck_id})
  ```
- **No custom exception classes** — uses Django built-ins
- **No global error handler** — Django's default middleware handles 500s

### 8.5 Logging
- **Minimal logging** — uses `print()` in a few places (e.g., `print(request.user.username)`)
- **No structured logging framework** configured
- **Email notifications** serve as the primary alert mechanism (via `email_duck_location`)
- **Microsoft Clarity** for frontend analytics (JS snippet in base template)

---

## 9. Testing Strategy

### 9.1 Test Frameworks

| Tool | Version | Purpose |
|------|---------|---------|
| **Django TestCase** | Built-in (Django 5.0.9) | Unit tests, integration tests |
| **Playwright** (Python) | Latest | End-to-end browser tests |
| **pytest** | Latest | Test runner for Playwright E2E tests |
| **pytest-playwright** | Latest | Playwright pytest plugin |

### 9.2 Test Organization

```
django/duck/tests/              # Django unit/integration tests
├── __init__.py                  # Imports: from .client_tests import *
├── client_tests.py              # HTTP client tests (views, forms, APIs)
└── media_tests.py               # Flickr upload tests

tests/                           # Playwright E2E tests (root level)
├── test_basic.py                # Homepage, navigation, login flow
├── test_mark_duck.py            # Full "mark a duck" workflow
├── test_media.py                # File upload tests
└── create_auth.py               # Helper to generate auth.json for E2E
```

### 9.3 Test Patterns

**Django Unit Tests (client_tests.py):**
- Inherit from `django.test.TestCase`
- Use `django.test.Client` for HTTP requests
- Use `django.test.RequestFactory` for view-level tests
- Create test users: `User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')`
- Force login for protected views: `self.client.force_login(self.user)`
- Assert on HTTP status codes and redirects
- Test model creation via POST requests

**Playwright E2E Tests (tests/):**
- Use `playwright.sync_api` with `Page` parameter
- Target `http://localhost:8001` (local running instance)
- Use `expect(page).to_have_title()` for page assertions
- Use `page.locator()` for element interaction
- Use `storage_state="auth.json"` for authenticated sessions
- Browser tests can run headless or `--headed`

**Mocking pattern:** No formal mocking framework. Tests use Django's test database (SQLite in-memory by default for tests) and `force_login()` to bypass OAuth.

### 9.4 Running Tests

```bash
# Django unit tests
export DJANGO_SETTINGS_MODULE=duckiehunt.settings.local
python django/manage.py test django/duck/tests

# Playwright E2E tests (requires running app at localhost:8001)
pip install playwright pytest-playwright setuptools
playwright install
pytest tests/test_basic.py
pytest --headed tests/test_basic.py  # with browser visible

# Authenticated E2E tests
pytest -s tests/create_auth.py       # generates auth.json
pytest tests/test_mark_duck.py
```

### 9.5 Test Requirements
- No formal coverage requirements
- No CI test gate (tests are run manually)
- E2E tests require a running application instance

---

## 10. CI/CD & DevOps

### 10.1 Pipeline Configuration

**Platform:** GitHub Actions

**Workflows:**

| Workflow File | Trigger | Purpose |
|---------------|---------|---------|
| `docker-image-build-push-deploy.yml` | Push to `master` | Build Docker image, push to GHCR, deploy to staging |
| `production-push.yaml` | Manual (workflow_dispatch) | Deploy to production |
| `update-stg.yml` | Manual (workflow_dispatch) | Update staging DB migrations |
| `update-prod.yml` | Manual (workflow_dispatch) | Update production DB migrations |

### 10.2 Main Pipeline Stages (docker-image-build-push-deploy.yml)

```
Push to master
  └─► Job: build-push-deploy
      ├── Checkout code
      ├── Login to GitHub Container Registry (ghcr.io)
      ├── Extract Docker metadata (tags, labels)
      ├── Build & push Docker image → ghcr.io/lastcoolnameleft/duckiehunt:<branch>
      └── Generate artifact attestation (supply chain security)
  └─► Job: update-stg (depends on build-push-deploy)
      ├── SCP docker-compose files to VM
      ├── SSH into VM
      ├── Docker system prune
      ├── Pull new image
      └── Docker rollout (zero-downtime) for staging
```

### 10.3 Deployment Strategy
- **Image registry:** `ghcr.io/lastcoolnameleft/duckiehunt`
- **Image tag:** Branch name (e.g., `master`)
- **Deployment:** SSH into Azure VM, pull image, `docker rollout` (zero-downtime)
- **DB migrations:** Run manually via separate workflow (`docker exec <container> python manage.py migrate`)

### 10.4 Quality Gates
- **No automated linting** in CI
- **No automated test execution** in CI
- **No branch protection rules** documented
- Artifact attestation for supply chain security (SLSA provenance)

---

## 11. Configuration Management

### 11.1 Environment Variable Pattern

The primary configuration mechanism is **Django settings modules**, selected via:

```bash
DJANGO_SETTINGS_MODULE=duckiehunt.settings.<environment>
```

| Environment | Module |
|-------------|--------|
| Development | `duckiehunt.settings.development` |
| Staging | `duckiehunt.settings.staging` |
| Production | `duckiehunt.settings.production` |
| Local (Mac) | `duckiehunt.settings.local` |
| Local Tests | `duckiehunt.settings.local-test` |

### 11.2 Settings Structure

Each settings module is a standalone Python file containing ALL configuration:

```python
# Key settings categories:
DEBUG = True/False
INSTALLED_APPS = [...]
MIDDLEWARE = [...]
DATABASES = {'default': {...}}
ALLOWED_HOSTS = [...]
CSRF_TRUSTED_ORIGINS = [...]
SECRET_KEY = '...'

# External services
FLICKR_API_KEY = '...'
FLICKR_API_SECRET = '...'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '...'
SOCIAL_AUTH_FACEBOOK_KEY = '...'
SENDGRID_API_KEY = '...'
RECAPTCHA_PUBLIC_KEY = '...'
RECAPTCHA_PRIVATE_KEY = '...'

# App-specific
BASE_URL = 'http://...'
UPLOAD_PATH = '/code/uploads/'
EMAIL_FROM = '...'
EMAIL_TO = [...]
```

### 11.3 Secret Management
- Settings files with credentials are stored **on the VM** at `/data/duckiehunt-<env>/settings/`
- Volume-mounted into Docker containers at `/code/duckiehunt/settings/`
- The `django/duckiehunt/settings/` directory is in `.gitignore`
- A `template.py` provides the structure with empty placeholder values
- **No vault or secret manager** — credentials are in Python settings files on disk

### 11.4 Feature Flags
- No formal feature flag system
- The `approved` field on `Duck` and `DuckLocation` models serves as a basic content moderation flag (values: `'Y'` or null)

---

## 12. Sample Code Patterns

> ⚠️ These are COMPLETE, representative code samples for building migration-compatible features.

### 12.1 Service / Business Logic Pattern — `marker.py`

```python
""" Helper functions for duck location management """
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from haversine import haversine, Unit
from .models import Duck, DuckLocation, DuckLocationPhoto


def create_new_duck(duck_id, name):
    """ Create a new Duck """
    duck = Duck(duck_id=duck_id,
                name=name,
                approved='Y',
                total_distance=0,
                create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                comments='')
    duck.save()
    add_initial_duck_location(duck)
    return duck


def add_initial_duck_location(duck):
    """ Create new DuckLocation from its origin """
    tommy = User.objects.get(id=1)
    duck_location_start = DuckLocation(duck=duck,
                    latitude='32.95159763382337',
                    longitude='-96.90789423886032',
                    location='Carrollton Plaza Arts Center, Carrollton, TX',
                    date_time='2008-08-16 20:00:00',
                    comments='Just got married!',
                    distance_to=0,
                    user=tommy,
                    approved='Y')
    duck_location_start.save()


def add_duck_location(duck_id, latitude, longitude, location, date_time, comments, user):
    """ Add a new sighting location for a duck """
    last_duck_location = DuckLocation.objects.filter(duck_id=duck_id).order_by('-date_time')[0]
    distance_travelled = haversine(
        (last_duck_location.latitude, last_duck_location.longitude),
        (latitude, longitude), unit=Unit.MILES)
    duck_location = DuckLocation(duck_id=duck_id,
                                 latitude=latitude,
                                 longitude=longitude,
                                 location=location,
                                 date_time=date_time,
                                 comments=comments,
                                 distance_to=round(distance_travelled, 2),
                                 user=user,
                                 approved='Y')
    duck_location.save()
    return duck_location


def email_duck_location(duck_id, duck_location_url):
    """ Send an email notification about a duck sighting """
    msg = EmailMessage(
        'Duckiehunt Update: Duck #' + str(duck_id),
        'Duck #' + str(duck_id) + ' has moved!<br/>' + settings.BASE_URL + duck_location_url,
        settings.EMAIL_FROM, settings.EMAIL_TO
    )
    msg.content_subtype = "html"
    msg.send()
```

### 12.2 API Handler Pattern — `apis.py`

```python
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Duck, DuckLocation, DuckLocationPhoto


def duck_detail(request, duck_id):
    """ Return single duck as JSON """
    duck = get_object_or_404(Duck, pk=duck_id)
    duck_data = {
        'duck_id': duck.duck_id,
        'name': duck.name,
        'total_distance': duck.total_distance,
        'create_time': duck.create_time,
        'approved': duck.approved
    }
    return JsonResponse(duck_data)


def ducks_all(request):
    """ Return all ducks as JSON array """
    duck_locations = Duck.objects.all().values('duck_id', 'name', 'total_distance')
    summary = list(duck_locations)
    return JsonResponse(summary, safe=False, content_type='application/json')


def duck_locations(request, duck_id):
    """ Return locations for a specific duck """
    duck_locations = DuckLocation.objects.filter(duck_id=duck_id).values(
        'duck_id', 'duck__name', 'latitude', 'longitude', 'comments')
    summary = list(duck_locations)
    return JsonResponse(summary, safe=False, content_type='application/json')


def location(request, duck_location_id):
    """ Return single location as JSON """
    duck_location = get_object_or_404(DuckLocation, pk=duck_location_id)
    duck_location_data = {
        'duck_id': duck_location.duck_id,
        'latitude': duck_location.latitude,
        'longitude': duck_location.longitude,
        'date_time': duck_location.date_time,
        'comments': duck_location.comments,
    }
    return JsonResponse(duck_location_data)
```

### 12.3 View Pattern (Template-rendering) — `views.py`

```python
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Duck, DuckLocation, DuckLocationPhoto
from .forms import DuckForm
from duck import marker


def detail(request, duck_id):
    """ /duck/# path — Show duck detail with map and travel history """
    try:
        duck = Duck.objects.get(pk=duck_id)
    except Duck.DoesNotExist:
        return render(request, 'duck/detail-not-found.html', {'duck_id': duck_id})

    photos = DuckLocationPhoto.objects.filter(duck_location__duck_id=duck_id)
    duck_location_list = DuckLocation.objects.filter(duck_id=duck_id)
    map_data = {
        'width': '100%',
        'height': '400px',
        'focus_lat': 0,
        'focus_long': 0,
        'focus_zoom': 2,
        'location_list_api': '/api/duck/' + str(duck_id) + '/locations',
        'duck_location_id': 0,
    }
    duck_dropdown_list = Duck.objects.all()

    return render(request, 'duck/detail.html',
                  {'duck': duck, 'photos': photos, 'map': map_data,
                   'duck_location_list': duck_location_list, 'duck_list': duck_dropdown_list})


@login_required
def mark(request, duck_id=None):
    """ Protected view — log a duck sighting """
    user = request.user
    url = '/mark/' + str(duck_id) if duck_id else '/mark/'
    return mark_process(request, duck_id, user, url)
```

### 12.4 Test Pattern — `client_tests.py`

```python
""" Client Tests """
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model

from duck.models import Duck, DuckLocation
from duck.views import index


class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_details(self):
        request = self.factory.get('/')
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_secure_page(self):
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login?next=/mark/')
        self.client.force_login(self.user)
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)

    def test_mark_full(self):
        self.client.force_login(self.user)
        duck_id = '2'
        data = {'duck_id': duck_id, 'name': 'test duck ' + duck_id, 'location': 'northkapp',
                'lat': '71.169493', 'lng': '25.7831639', 'date_time': '09/01/2018 23:04:08',
                'comments': 'this is a comment'}
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/duck/' + duck_id)
        duck = Duck.objects.get(pk=duck_id)
        self.assertEqual(duck.name, 'test duck ' + duck_id)
        duck_location = DuckLocation.objects.filter(duck_id=duck_id)
        self.assertEqual(len(duck_location), 1)
        self.assertEqual(duck_location[0].location, 'northkapp')
        self.assertEqual(duck_location[0].latitude, 71.169493)
        self.assertEqual(duck_location[0].longitude, 25.7831639)
        self.assertEqual(duck_location[0].comments, 'this is a comment')
```

### 12.5 Form Pattern — `forms.py`

```python
""" Form for Duckiehunt """
from django import forms
from django_recaptcha.fields import ReCaptchaField
import datetime


class DuckForm(forms.Form):
    """ Form for duckiehunt. """
    captcha = ReCaptchaField()
    duck_id = forms.IntegerField(label='Duck #', min_value=2, max_value=3000)
    name = forms.CharField(label='Duck name', max_length=100, disabled=False, required=False)
    location = forms.CharField(label='Location', max_length=100)
    date_time = forms.DateTimeField(label='Date/Time',
                                    initial=datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    lat = forms.FloatField(label='Latitude')
    lng = forms.FloatField(label='Longitude')
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': '50', 'rows': '5'}))
    image = forms.ImageField(required=False)
```

### 12.6 URL Routing Pattern — `urls.py`

```python
""" Duck URL router """
from django.conf.urls import include
from django.urls import path
from . import views, apis

urlpatterns = [
    # Page views
    path('', views.index, name='index'),
    path('duck/', views.duck_list, name='duck_list'),
    path('duck/<int:duck_id>', views.detail, name='detail'),
    path('found/<int:duck_id>', views.found, name='found'),
    path('location/<int:duck_location_id>', views.location, name='location'),
    path('mark/', views.mark, name='mark'),
    path('mark/<int:duck_id>', views.mark, name='mark'),

    # JSON API endpoints
    path('api/duck/<int:duck_id>', apis.duck_detail, name='detail'),
    path('api/ducks', apis.ducks_all),
    path('api/locations', apis.locations_all),
    path('api/duck/<int:duck_id>/locations', apis.duck_locations),
    path('api/location/<int:duck_location_id>', apis.location),

    # Auth
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),
]
```

---

## 13. Migration Contract

> ⚠️ This section defines what MUST match, what WILL change, and what CAN differ when integrating PoC code.

### 13.1 What Must Match Exactly

**API Routes:**
- All API endpoints must follow `/api/<resource>` pattern
- URL parameter types must use `<int:param_id>` Django syntax
- Response JSON keys must match exactly (e.g., `duck_id`, `duck__name`, `total_distance`)

**Model/DTO Property Names:**
- All Django model field names must match the existing schema exactly (snake_case)
- Database table names must use `Meta.db_table` with the exact name
- Foreign key field names must match (e.g., `duck`, `user`, `duck_location`)

**File Naming & Folder Structure:**
- Single Django app under `django/<app_name>/`
- `models.py`, `views.py`, `apis.py`, `forms.py`, `marker.py` (or equivalent service module)
- Templates in `templates/<app_name>/`
- Tests in `tests/` subdirectory with `__init__.py` importing test classes

**Error Response Format:**
- 404: Use `get_object_or_404()` (Django default response)
- Model not found in views: Render a `*-not-found.html` template
- Form validation: Django's built-in form error handling

### 13.2 What Will Be Replaced During Migration

| PoC Component | Replaced With |
|---------------|---------------|
| SQLite/test database | MySQL (Azure Database for MySQL) |
| Mock Flickr upload | Real `flickr-api` integration |
| Stub email sending | Real SendGrid SMTP via `django.core.mail.EmailMessage` |
| Test OAuth credentials | Real Google/Facebook OAuth2 keys |
| Stub reCAPTCHA | Real Google reCAPTCHA keys |
| Local file storage | Volume-mounted `/code/uploads/` |
| `settings.local` | Environment-specific settings module |

### 13.3 What Can Differ

- Test data and fixtures (duck IDs, locations, names)
- Local development tooling (docker-compose variants)
- Documentation format
- Static asset versions (Bootstrap, jQuery)
- Development convenience scripts

### 13.4 Required Base Classes to Extend

This project uses **no custom abstract base classes**. All models inherit directly from `django.db.models.Model`. All views are function-based (no class-based view inheritance). See Section 17 for the Django framework contracts to follow.

### 13.5 Required Interfaces to Implement

Python does not use formal interfaces. The project follows **implicit contracts** through consistent function signatures and Django conventions. See Section 14 for the callable contracts that must be matched.

---

## 14. Interface Definitions

> ⚠️ Python/Django does not use formal interfaces. This section documents the **implicit callable contracts** that PoC code must implement to be migration-compatible.

### 14.1 View Function Contract

All page-rendering views must follow this signature:

```python
def view_name(request: HttpRequest, **url_params) -> HttpResponse:
    """
    Args:
        request: Django HttpRequest object
        **url_params: URL parameters (e.g., duck_id: int, duck_location_id: int)
    Returns:
        HttpResponse via render() or HttpResponseRedirect
    """
    pass
```

### 14.2 API Function Contract

All JSON API endpoints must follow:

```python
def api_endpoint(request: HttpRequest, **url_params) -> JsonResponse:
    """
    Args:
        request: Django HttpRequest object
        **url_params: URL parameters
    Returns:
        JsonResponse with dict (single object) or list (collection)
        Use safe=False for list responses
    """
    pass
```

### 14.3 Service Function Contracts (marker.py pattern)

New feature service modules must expose functions matching these signatures:

```python
def create_new_entity(entity_id: int, name: str) -> Model:
    """Create and save a new entity. Returns the saved model instance."""
    pass

def add_entity_child(entity_id: int, **fields) -> Model:
    """Create a child record linked to a parent entity. Returns saved instance."""
    pass

def email_notification(entity_id: int, url: str) -> None:
    """Send email notification about an entity event."""
    pass
```

### 14.4 Form Class Contract

All Django forms must follow:

```python
class EntityForm(forms.Form):
    """
    Must include:
    - captcha = ReCaptchaField() for public forms
    - All fields with appropriate validators
    - Widget customization via attrs dict
    """
    captcha = ReCaptchaField()
    # ... fields
```

### 14.5 Admin Registration Contract

All new models must be registered with Django admin:

```python
from django.contrib import admin
from .models import NewModel

admin.site.register(NewModel)
```

### 14.6 App Configuration Contract

Each Django app must have:

```python
from django.apps import AppConfig

class NewFeatureConfig(AppConfig):
    name = 'new_feature'
```

### 14.7 Natural Key Contract

Models returned in serialized responses should implement `natural_key()`:

```python
class MyModel(models.Model):
    def natural_key(self):
        return {'field1': self.field1, 'field2': self.field2}
```

---

## 15. Enum Definitions

> ⚠️ Python/Django does not use formal enum classes in this project. Instead, the codebase uses **string/character constants** and **implicit value sets**. This section documents all value-constrained fields that act as enums.

### 15.1 Approved Status (Duck, DuckLocation)

Used on: `Duck.approved`, `DuckLocation.approved`

```python
# Implicit enum — CharField(max_length=1)
APPROVED_VALUES = {
    'Y': 'Approved / Active',
    None: 'Not yet approved / Pending',
}
```

**Usage in code:**
```python
duck = Duck(approved='Y', ...)
duck_location = DuckLocation(approved='Y', ...)
```

### 15.2 Authentication Backends

Used in: `settings.AUTHENTICATION_BACKENDS`

```python
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',      # Google OAuth2
    'social_core.backends.facebook.FacebookOAuth2',   # Facebook OAuth2
)
```

### 15.3 Flickr Photo Visibility

Used in: `settings.FLICKR_PHOTO_IS_PUBLIC`

```python
FLICKR_PHOTO_VISIBILITY = {
    '0': 'Private',
    '1': 'Public',
}
```

### 15.4 Django Settings Module Values

Used in: `DJANGO_SETTINGS_MODULE` environment variable

```python
SETTINGS_MODULES = {
    'duckiehunt.settings.development': 'Development environment',
    'duckiehunt.settings.staging': 'Staging environment',
    'duckiehunt.settings.production': 'Production environment',
    'duckiehunt.settings.local': 'Local Mac development',
    'duckiehunt.settings.local-test': 'Local test configuration',
}
```

### 15.5 Social Auth API Versions

Used in: Settings files

```python
SOCIAL_AUTH_FACEBOOK_API_VERSION = '2.11'
```

### 15.6 Email Configuration Constants

```python
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'  # Literal string 'apikey' for SendGrid
```

### 15.7 Form Field Constraints

Used in: `DuckForm`

```python
DUCK_FORM_CONSTRAINTS = {
    'duck_id_min': 2,
    'duck_id_max': 3000,
    'name_max_length': 100,
    'location_max_length': 100,
    'comments_cols': 50,
    'comments_rows': 5,
    'date_format': '%m/%d/%Y %H:%M:%S',
}
```

---

## 16. Model & DTO Definitions

> ⚠️ COMPLETE Django model definitions with ALL fields, types, and constraints. These are the authoritative definitions for migration compatibility.

### 16.1 Duck (Django Model)

```python
from django.db import models

class Duck(models.Model):
    duck_id = models.IntegerField(primary_key=True)
    create_time = models.DateTimeField(blank=True)
    name = models.CharField(max_length=128, blank=True, default=None)
    comments = models.TextField(blank=True, default=None)
    total_distance = models.FloatField(blank=True, default=0)
    approved = models.CharField(max_length=1, default='Y')

    def natural_key(self):
        return {'duck_id': self.duck_id, 'name': self.name, 'total_distance': self.total_distance}

    class Meta:
        db_table = 'duck'
```

### 16.2 DuckLocation (Django Model)

```python
from django.db import models
from django.contrib.auth.models import User

class DuckLocation(models.Model):
    duck_location_id = models.AutoField(primary_key=True)
    duck = models.ForeignKey(Duck, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    link = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    flickr_photo_id = models.BigIntegerField(blank=True, null=True)
    duck_history_id = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    approved = models.CharField(max_length=1, blank=True, null=True)
    distance_to = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'duck_location'
```

### 16.3 DuckLocationLink (Django Model)

```python
from django.db import models

class DuckLocationLink(models.Model):
    duck_location_link_id = models.AutoField(primary_key=True)
    duck_location = models.ForeignKey(DuckLocation, models.DO_NOTHING, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'duck_location_link'
```

### 16.4 DuckLocationPhoto (Django Model)

```python
from django.db import models

class DuckLocationPhoto(models.Model):
    duck_location_photo_id = models.AutoField(primary_key=True)
    duck_location = models.ForeignKey(DuckLocation, models.DO_NOTHING, null=True)
    flickr_photo_id = models.BigIntegerField(blank=True, null=True)
    flickr_thumbnail_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'duck_location_photo'
```

### 16.5 DuckForm (Django Form — acts as DTO for duck marking)

```python
from django import forms
from django_recaptcha.fields import ReCaptchaField
import datetime

class DuckForm(forms.Form):
    captcha = ReCaptchaField()
    duck_id = forms.IntegerField(label='Duck #', min_value=2, max_value=3000)
    name = forms.CharField(label='Duck name', max_length=100, disabled=False, required=False)
    location = forms.CharField(label='Location', max_length=100)
    date_time = forms.DateTimeField(label='Date/Time',
                                    initial=datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    lat = forms.FloatField(label='Latitude')
    lng = forms.FloatField(label='Longitude')
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': '50', 'rows': '5'}))
    image = forms.ImageField(required=False)
```

### 16.6 Duck Detail API Response DTO

```python
# Returned by apis.duck_detail()
duck_detail_response = {
    'duck_id': int,          # Primary key
    'name': str,             # Duck name
    'total_distance': float, # Cumulative miles traveled
    'create_time': str,      # ISO datetime string
    'approved': str,         # 'Y' or None
}
```

### 16.7 Duck List API Response DTO

```python
# Returned by apis.ducks_all() — list of dicts
duck_list_item = {
    'duck_id': int,
    'name': str,
    'total_distance': float,
}
```

### 16.8 Location List API Response DTO

```python
# Returned by apis.locations_all() and apis.duck_locations()
location_list_item = {
    'duck_id': int,
    'duck__name': str,       # Note: double underscore (Django ORM join notation)
    'latitude': float,
    'longitude': float,
    'comments': str,
}
```

### 16.9 Single Location API Response DTO

```python
# Returned by apis.location()
location_detail_response = {
    'duck_id': int,
    'latitude': float,
    'longitude': float,
    'date_time': str,        # ISO datetime string
    'comments': str,
}
```

### 16.10 Map Data Context DTO (Template Context)

```python
# Passed to templates as 'map' context variable
map_data = {
    'width': str,              # CSS width, e.g. '100%'
    'height': str,             # CSS height, e.g. '400px'
    'focus_lat': float,        # Map center latitude
    'focus_long': float,       # Map center longitude
    'focus_zoom': int,         # Map zoom level
    'location_list_api': str,  # API URL for fetching locations, e.g. '/api/duck/1/locations'
    'duck_location_id': int,   # Highlighted location ID (0 = none)
}
```

### 16.11 Flickr Photo Info DTO

```python
# Returned by marker.handle_uploaded_file() / marker.upload_to_flickr()
photo_info = {
    'id': str,               # Flickr photo ID
    'title': str,            # Photo title
    'description': str,      # Photo description
    'tags': str,             # Space-separated tags
    'sizes': {
        'Small 320': {
            'source': str,   # Thumbnail URL
        },
        # ... other size keys
    },
}
```

### 16.12 Django User (Built-in — referenced by DuckLocation)

```python
# django.contrib.auth.models.User — used as-is, not extended
# Key fields referenced in this project:
user_fields = {
    'id': int,               # Auto PK
    'username': str,
    'email': str,
    'password': str,         # Hashed
}
```

---

## 17. Base Class Contracts

> ⚠️ This project does NOT use custom abstract base classes. All models extend `django.db.models.Model` directly, and all views are function-based. This section documents the **Django framework base classes** that PoC code must extend correctly.

### 17.1 django.db.models.Model

All data models MUST extend `django.db.models.Model`:

```python
from django.db import models

class Model(models.Model):
    """
    Django's base model class. All Duckiehunt models extend this directly.

    Required patterns for new models:
    - Define fields as class attributes using models.* field types
    - Set explicit primary key (AutoField or IntegerField with primary_key=True)
    - Define Meta.db_table with snake_case table name
    - Implement natural_key() if model will be serialized to JSON

    Available field types used in this project:
    - models.IntegerField(primary_key=True)
    - models.AutoField(primary_key=True)
    - models.CharField(max_length=N, blank=True, default=None)
    - models.TextField(blank=True, null=True)
    - models.FloatField(blank=True, null=True)
    - models.BigIntegerField(blank=True, null=True)
    - models.DateTimeField(blank=True, null=True)
    - models.ForeignKey(OtherModel, on_delete=models.CASCADE, null=True)
    - models.ForeignKey(OtherModel, models.DO_NOTHING, null=True)
    """

    class Meta:
        abstract = True  # This is the base; concrete models set db_table

    def natural_key(self):
        """Override to return dict of key fields for JSON serialization."""
        raise NotImplementedError
```

**Example — creating a new model following project conventions:**
```python
class Achievement(models.Model):
    achievement_id = models.AutoField(primary_key=True)
    duck = models.ForeignKey(Duck, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    earned_date = models.DateTimeField(blank=True, null=True)
    approved = models.CharField(max_length=1, default='Y')

    def natural_key(self):
        return {'achievement_id': self.achievement_id, 'name': self.name}

    class Meta:
        db_table = 'achievement'
```

### 17.2 django.test.TestCase

All unit tests MUST extend `django.test.TestCase`:

```python
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model

class TestCase(TestCase):
    """
    Django's test base class with database transaction rollback.

    Required patterns:
    - setUp(): Create Client, RequestFactory, and test User
    - Test methods prefixed with test_
    - Use self.assertEqual, self.assertTrue for assertions
    - Use self.client.get/post for HTTP tests
    - Use self.client.force_login(user) for auth-required views
    - Use self.factory.get/post for RequestFactory tests
    """

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
```

**Example — new test class following project conventions:**
```python
class AchievementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass')

    def test_achievement_api(self):
        response = self.client.get('/api/achievements')
        self.assertEqual(response.status_code, 200)

    def test_achievement_requires_login(self):
        response = self.client.get('/achievement/create/')
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get('/achievement/create/')
        self.assertEqual(response.status_code, 200)
```

### 17.3 django.forms.Form

All user-facing forms MUST extend `django.forms.Form`:

```python
from django import forms
from django_recaptcha.fields import ReCaptchaField

class Form(forms.Form):
    """
    Django's base form class.

    Required patterns for new forms:
    - Include captcha = ReCaptchaField() for any public-facing form
    - Define all fields as class attributes
    - Use appropriate field types with labels and validators
    - Set widget attrs for textarea customization
    - Set required=False for optional fields
    - Use initial= for default values
    """
    pass
```

**Example — new form following project conventions:**
```python
class AchievementForm(forms.Form):
    captcha = ReCaptchaField()
    duck_id = forms.IntegerField(label='Duck #', min_value=2, max_value=3000)
    name = forms.CharField(label='Achievement Name', max_length=128)
    description = forms.CharField(
        widget=forms.Textarea(attrs={'cols': '50', 'rows': '3'}),
        required=False
    )
```

### 17.4 django.apps.AppConfig

Each new Django app MUST have an AppConfig:

```python
from django.apps import AppConfig

class AppConfig(AppConfig):
    """
    Required pattern:
    - name = '<app_name>' matching the directory name
    - One AppConfig per app
    - Referenced in INSTALLED_APPS as '<app_name>.apps.<AppName>Config'
    """
    name = 'app_name'
```

---

## 18. Quick Reference

### Technology Versions

| Component | Version |
|-----------|---------|
| Python | 3.x (slim) |
| Django | 5.0.9 |
| Bootstrap | 4.x |
| jQuery | Bundled |
| haversine | 2.8.1 |
| social-auth-core | 4.5.3 |
| social-auth-app-django | 5.4.1 |
| django-recaptcha | 4.0.0 |
| flickr-api | 0.7.7 |
| whitenoise | 6.6.0 |

### Critical Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Django models | PascalCase | `DuckLocation` |
| DB table names | snake_case via `Meta.db_table` | `duck_location` |
| Model fields | snake_case | `duck_location_id`, `total_distance` |
| View functions | snake_case | `duck_list`, `mark_process` |
| API functions | snake_case | `duck_detail`, `locations_all` |
| URL paths | lowercase, no trailing slash | `/api/duck/<int:duck_id>` |
| Template files | lowercase, hyphens | `detail-not-found.html` |
| Python files | lowercase, underscores | `marker.py`, `client_tests.py` |
| Primary keys | `<entity>_id` | `duck_id`, `duck_location_id` |
| Foreign keys | entity name (no `_id` suffix) | `duck`, `user` |

### Must-Follow Rules

1. **All models** must set `class Meta: db_table = '<snake_case_name>'`
2. **All models** must have an explicit primary key field
3. **All public forms** must include `captcha = ReCaptchaField()`
4. **All protected views** must use `@login_required` decorator
5. **All API responses** use `JsonResponse` — single objects as dict, collections as list with `safe=False`
6. **Business logic** goes in a service module (like `marker.py`), not in views
7. **Views are function-based** — do not use class-based views
8. **Templates** go in `templates/<app_name>/` within the app directory
9. **No API envelope** — return raw dicts/lists, not wrapped responses
10. **Distance calculations** use `haversine` library with `Unit.MILES`
11. **Settings** are per-environment Python modules selected via `DJANGO_SETTINGS_MODULE`
12. **Tab indentation** everywhere (per `.editorconfig`)

### File Locations

| Purpose | Path |
|---------|------|
| Main Django app | `django/duck/` |
| Models | `django/duck/models.py` |
| Page views | `django/duck/views.py` |
| JSON APIs | `django/duck/apis.py` |
| Business logic | `django/duck/marker.py` |
| Forms | `django/duck/forms.py` |
| URL routing (app) | `django/duck/urls.py` |
| URL routing (project) | `django/duckiehunt/urls.py` |
| Admin registrations | `django/duck/admin.py` |
| App config | `django/duck/apps.py` |
| Templates | `django/duck/templates/duck/` |
| Static assets | `django/duck/static/` |
| DB migrations | `django/duck/migrations/` |
| Unit tests | `django/duck/tests/` |
| E2E tests | `tests/` |
| Settings template | `django/duckiehunt/settings/template.py` |
| Docker Compose files | `docker-compose/` |
| Dockerfile | `Dockerfile` |
| CI/CD workflows | `.github/workflows/` |
| Docs | `docs/` |
| Helm charts | `charts/duckiehunt/` |
