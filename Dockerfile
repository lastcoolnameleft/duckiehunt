FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD django/requirements.txt /code/
RUN pip install -r requirements.txt
ADD django /code/
#  https://stackoverflow.com/a/41061703
CMD ["python3", "manage.py", "runserver", "--insecure", "0.0.0.0:8000"]
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
