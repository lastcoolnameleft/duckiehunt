# Testing

Uses [Playwright](https://playwright.dev/python/docs/running-tests).

Basic run test:
```
cd tests
pytest test_basic.py
pytest test_mark_duck.py

# Run with browser
pytest --headed test_basic.py
```

Regenerate auth.json
```
npx playwright codegen http://localhost:81 --save-storage=auth.json
```