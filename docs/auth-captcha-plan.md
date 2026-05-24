# Auth & Captcha Redesign Plan

## Current State
- **Social login** (Google, Facebook): `@login_required` on `/mark/` → no captcha
- **Anonymous/captcha path**: `/mark_captcha/` → captcha required, no user associated
- **Login page** shows: Google, Facebook, or "Captcha" link
- **No username/password login or registration** in the UI
- `ModelBackend` is in `AUTHENTICATION_BACKENDS`

## Goals
1. **Login page** shows: Google, Facebook, AND username/password form
2. **Registration page** (`/register/`) lets users create accounts (with captcha to prevent bots)
3. **Marking a duck**: authenticated users (any method) → no captcha; unauthenticated → captcha required
4. **Remove the separate `/mark_captcha/` login link** — the captcha happens inline on the mark form when not logged in

## Proposed Flow

### Login (`/login`)
- Google button
- Facebook button
- Username/password form (existing accounts)
- "Don't have an account? Register" link
- No captcha on login (rate limiting is better here)

### Registration (`/register/`)
- Username, email (optional), password, confirm password
- reCAPTCHA to prevent bot signups
- On success → auto-login → redirect to where they were going

### Mark a Duck (`/mark/<id>`)
- **If logged in** (social OR username/password): show form WITHOUT captcha
- **If NOT logged in**: show form WITH captcha (anonymous submission)
- Remove `@login_required` from `mark()` — anyone can access it
- Remove `/mark_captcha/` as a separate endpoint (no longer needed)

### Updated URL Structure
| URL | Purpose |
|-----|---------|
| `/login` | Login page (social + username/password) |
| `/register/` | New account creation (with captcha) |
| `/mark/<id>` | Mark a duck (captcha if anonymous, no captcha if logged in) |
| `/mark_captcha/<id>` | **REMOVED** (redirect to `/mark/<id>` for backwards compat) |

## Implementation Plan

### 1. Forms (`django/duck/forms.py`)
- Add `RegistrationForm`: username, email, password1, password2, captcha
- Add `LoginForm`: username, password (simple AuthenticationForm wrapper)
- `DuckForm` already has `require_captcha` kwarg ✅

### 2. Views (`django/duck/views.py`)
- **`register()`**: new view — show/process `RegistrationForm`, auto-login on success
- **`login()`**: update to render `LoginForm` + process username/password auth (keep social links).  Redesign to use more modern logos/buttons.
- **`mark()`**: remove `@login_required`, pass `require_captcha=not request.user.is_authenticated`
- **`mark_captcha()`**: convert to redirect to `/mark/<id>` (backwards compat)

### 3. URLs (`django/duck/urls.py`)
- Add `path('register/', views.register, name='register')`
- Keep `/mark_captcha/<id>` as redirect

### 4. Templates
- **`login.html`**: redesign — social buttons + username/password form + register link
- **`register.html`**: new — registration form with captcha
- **`mark.html`** (if exists): may need minor update for inline captcha display

### 5. Tests
- `test_forms.py`: RegistrationForm validation (passwords match, captcha required, etc.)
- `test_views.py`: register view (success, duplicate user, weak password), mark view (captcha shown/hidden based on auth)

## What Gets Removed
- `@login_required` decorator on `mark()`
- The "Captcha" link on login page (captcha moves to inline on mark form)
- `/mark_captcha/` as a primary flow (becomes a redirect)

## Security
- Registration: captcha prevents bot account spam
- Anonymous mark: captcha prevents bot submissions
- Login: no captcha (add rate-limiting/lockout later if needed)
- Passwords: Django's built-in validators (min length, common password check, etc.)
