FROM python:3.11-slim-buster

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=fe.settings \
    PORT=8000 \
    WEB_CONCURRENCY=4 \
    PRODUCTION=true

# Install system packages required by Django (if needed).
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django \
    && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy project code
COPY . .
RUN python manage.py collectstatic --noinput

# Run as non-root user
RUN chown -R django:django /app
USER django

# Run application
CMD ["gunicorn", "fe.wsgi:application", "--log-config-json", "./logger_conf.json"]
