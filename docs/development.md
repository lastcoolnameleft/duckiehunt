# Development

Tools for running locally

## Build and run locally

```shell
docker compose -f docker-compose/mac.yaml up --build

# Clear image cache
docker rmi -f duckiehunt

# Get Python Django shell
docker exec -it duckiehunt-local python manage.py shell

# Clear ALL cache
docker system prune

# Rebuild images
docker compose --file docker-compose-local.yaml build
```

## Perform updates

```shell
# Re-create requirements
docker exec -it duckiehunt-local sh
pip install pip-tools
pip-compile

# Update database
docker exec -it duckiehunt-local bash
python manage.py migrate
```

## Reference for upgrading PIP packages

https://stackoverflow.com/questions/2720014/how-to-upgrade-all-python-packages-with-pip/43642193#43642193

```shell
$ pip freeze > requirements.txt
Open the text file, replace the == with >=, or have sed do it for you:

$ sed -i 's/==/>=/g' requirements.txt
and execute:

$ pip install -r requirements.txt --upgrade
```

## Testing

```shell
pip install playwright pytest-playwright setuptools flickr-api
playwright install
pytest tests/test_basic.py

pytest -s tests/create_auth.py
# Provide password and use "say yes on phone/tablet"
pytest tests/test_mark_duck.py

# Haven't gotten working
export DJANGO_SETTINGS_MODULE=duckiehunt.settings.local
python django/manage.py test django/duck/tests
```
