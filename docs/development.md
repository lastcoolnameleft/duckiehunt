# Build and run locally

```
docker build -t duckiehunt .
docker run -p 8000:8000 --name duckiehunt --rm -it -v $PWD/django:/code duckiehunt
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
