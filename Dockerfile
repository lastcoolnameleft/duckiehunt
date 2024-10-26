FROM python:3-slim
ENV PYTHONUNBUFFERED 1
RUN apt-get update -y
RUN apt install python3-dev default-libmysqlclient-dev pkg-config build-essential libffi-dev -y
RUN mkdir /code
WORKDIR /code
ADD django/requirements.txt /code/
RUN pip install setuptools
RUN pip install -r requirements.txt
ADD django /code/
#  https://stackoverflow.com/a/41061703
#CMD ["python3", "manage.py", "runserver", "--insecure", "0.0.0.0:8000"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
