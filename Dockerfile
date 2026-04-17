FROM python:3.12-slim
ENV PYTHONUNBUFFERED 1
ARG GIT_SHA=unknown
ENV GIT_SHA=${GIT_SHA}
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
      python3-dev default-libmysqlclient-dev pkg-config build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY django/requirements.txt /code/
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt
COPY django /code/
#  https://stackoverflow.com/a/41061703
#CMD ["python3", "manage.py", "runserver", "--insecure", "0.0.0.0:8000"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
