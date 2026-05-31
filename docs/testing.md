# Testing

## Django unit tests

```bash
source venv/bin/activate
cd django && python manage.py test duck.tests --verbosity=2
```

## Playwright tests (requires local dev server)

All Playwright-based browser tests live in `tests/playwright/`.

Start the dev server first:
```bash
source venv/bin/activate
cd django && python manage.py runserver 0.0.0.0:8042
```

Run all local Playwright tests:
```bash
pytest tests/playwright/ -v
```

Run with visible browser:
```bash
pytest tests/playwright/ -v --headed
```

Run a specific test file:
```bash
pytest tests/playwright/test_basic.py -v
pytest tests/playwright/test_maps.py -v
pytest tests/playwright/test_ui_components.py -v
pytest tests/playwright/test_photo_upload.py -v --headed
```

### UI component tests

After Bootstrap/CSS/JS changes, verify all interactive UI still works:
```bash
pytest tests/playwright/test_ui_components.py -v
```

This covers:
- **Navbar**: desktop visibility, mobile collapse, hamburger expand
- **Accordions**: FAQ and Issue page open/close
- **Mark form JS**: name field disable/enable via fetch, submit button spinner
- **Create form**: page loads with expected fields
- **Footer**: links present and navigable

Run with `--headed` to watch the browser interactions visually:
```bash
pytest tests/playwright/test_ui_components.py -v --headed
```

Tests that require authentication need `auth.json` at the repo root:
- `test_mark_duck.py`
- `test_photo_upload.py`

## Staging/Production tests (CI)

These run in GitHub Actions against deployed environments:
```bash
pytest tests/staging/ -v
pytest tests/production/ -v
```

## Generating auth.json

```bash
npx playwright codegen http://localhost:8042 --save-storage=auth.json
```

Or use the helper script:
```bash
python tests/create_auth.py
```