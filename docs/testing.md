# Testing

## Django unit tests

```bash
source venv/bin/activate
cd django && python manage.py test duck.tests --verbosity=2
```

## Playwright tests (requires local dev server)

Start the dev server first:
```bash
source venv/bin/activate
cd django && python manage.py runserver 0.0.0.0:8042
```

Basic smoke tests (no auth required):
```bash
pytest tests/test_basic.py
```

Mark duck test (requires auth.json):
```bash
pytest tests/test_mark_duck.py --headed
```

Photo upload test (requires auth.json):
```bash
pytest tests/test_photo_upload.py -v --headed
```

Run with browser hidden:
```bash
pytest tests/test_photo_upload.py -v
```

## Generating auth.json

```bash
npx playwright codegen http://localhost:8042 --save-storage=tests/auth.json
```

Or use the helper script:
```bash
python tests/create_auth.py
```