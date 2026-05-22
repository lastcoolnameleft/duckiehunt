FROM python:3.12-slim

ARG GIT_SHA=unknown
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=duckiehunt.settings \
    GIT_SHA=${GIT_SHA} \
    HOME=/home/appuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    gosu \
    && rm -rf /var/lib/apt/lists/*

COPY django/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY django /app/django
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh && \
    mkdir -p /app/data /app/uploads && \
    ln -s /app/django /code && \
    ln -s /app/data /db && \
    ln -s /app/uploads /uploads && \
    DJANGO_SETTINGS_MODULE=duckiehunt.settings \
    DJANGO_SECRET_KEY=build-placeholder \
    python /app/django/manage.py collectstatic --noinput && \
    adduser --system --group --home /home/appuser appuser && \
    chown -R appuser:appuser /app /home/appuser /docker-entrypoint.sh

WORKDIR /app/django

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn"]
