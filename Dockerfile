FROM python:3.10-slim-buster

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

# Prometheus client if it's not in your requirements.txt (recommended to put it in there)
RUN pip install prometheus_client

# Copy project code
COPY . .
RUN python manage.py collectstatic --noinput

# Run as non-root user
RUN chown -R django:django /app
USER django


# Expose both ports. Important!
EXPOSE 8000 8001

# Run the Django application with gunicorn and bind it correctly to both interfaces.
CMD exec gunicorn --bind 0.0.0.0:8000 --workers $WEB_CONCURRENCY fe.wsgi:application & python manage.py runserver 0.0.0.0:8001