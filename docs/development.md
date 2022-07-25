# Build and run locally

```
docker build -t duckiehunt .
docker compose -f docker-compose-mac.yaml up

# Clear image cache
docker rmi -f duckiehunt

# Get Python Django shell
docker exec -it duckiehunt-local python manage.py shell
```

# Perform updates

```
docker exec -it duckiehunt bash
python manage.py migrate
```

# Reference for upgrading PIP packages

  https://stackoverflow.com/questions/2720014/how-to-upgrade-all-python-packages-with-pip/43642193#43642193

```
$ pip freeze > requirements.txt
Open the text file, replace the == with >=, or have sed do it for you:

$ sed -i 's/==/>=/g' requirements.txt
and execute:

$ pip install -r requirements.txt --upgrade
```
