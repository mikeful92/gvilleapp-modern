FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

COPY data/csv ./data/csv
COPY scripts ./scripts
RUN python scripts/build_db.py --csv-dir data/csv --out data/utility.sqlite3


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=false

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /app/data/utility.sqlite3 ./data/utility.sqlite3

COPY manage.py ./
COPY WebApp ./WebApp
COPY Utility ./Utility
COPY templates ./templates
COPY static ./static
COPY scripts ./scripts

RUN python manage.py collectstatic --noinput

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["sh", "-c", "gunicorn WebApp.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --access-logfile -"]
