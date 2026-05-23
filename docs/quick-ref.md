# Quick Ref

```
source venv/bin/activate
cd django
python manage.py runserver 0.0.0.0:8042

# Copy stg db locally for testing
scp dh:/data/duckiehunt/stg/db/duckiehunt.db ./django/data/duckiehunt.db

# Run tests locally 
source venv/bin/activate
pytest tests/staging/test_mark_integration.py -v --headed
```