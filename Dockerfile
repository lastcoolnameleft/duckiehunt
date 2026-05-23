FROM python:3.12-slim

ARG GIT_SHA=unknown
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=duckiehunt.settings \
    GIT_SHA=${GIT_SHA}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY django/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY django /app/django

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh && \
    DJANGO_SETTINGS_MODULE=duckiehunt.settings \
    DJANGO_SECRET_KEY=build-placeholder \
    python /app/django/manage.py collectstatic --noinput

RUN useradd -r -u 1000 -d /app appuser && \
    chown -R appuser:appuser /app

USER appuser

WORKDIR /app/django

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn"]
