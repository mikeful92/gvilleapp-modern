# Gainesville Utility App — Modernized

A modernized version of the 2015 [gvilleapp](https://github.com/mikeful92/gvilleapp). Lets you look up monthly electricity (kWh) and water (1,000 gal) consumption — plus the estimated bill — for any GRU-serviced address in Gainesville, FL. The dataset is historical: GRU's published 2014 consumption export.

## Stack

- Python 3.12, Django 5
- Read-only SQLite, built from the original CSVs at image build time
- WhiteNoise for static files, gunicorn as the WSGI server
- Bootstrap 3.4.1 — same look and feel as the 2015 site
- GitHub Actions for CI, Docker for deploy

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# build the SQLite database from CSVs (~1 minute)
python scripts/build_db.py

# run dev server
DJANGO_DEBUG=true DJANGO_SECRET_KEY=dev python manage.py runserver
```

Visit http://127.0.0.1:8000.

Run tests:

```bash
DJANGO_DEBUG=true DJANGO_SECRET_KEY=dev python manage.py test
```

## Deploy to Render (free tier)

1. Push this repo to GitHub.
2. In the Render dashboard: **New → Blueprint → connect this repo**. Render reads `render.yaml` and provisions the service.
3. First deploy takes ~5 minutes (Docker build includes generating the SQLite DB).

Free-tier note: the service sleeps after 15 minutes idle, so the first request after sleep takes ~30s to wake. Subsequent requests are fast.

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key | (required in production) |
| `DJANGO_DEBUG` | Set `true` for dev | `false` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames | `*` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated origins for CSRF | `""` |
| `DJANGO_DB_PATH` | Override SQLite path | `data/utility.sqlite3` |
| `PORT` | gunicorn bind port | `8000` |

## Data

`data/csv/` holds the two source CSVs. They feed `scripts/build_db.py` which produces `data/utility.sqlite3` with `Utility_electric` and `Utility_water` tables, indexed on `ServiceAddress`.

## Project layout

```
.
├── WebApp/              Django project (settings, urls, wsgi, asgi)
├── Utility/             Django app (models, views, forms)
├── templates/           Bootstrap 3 templates
├── static/static_dirs/  CSS/JS (BS 3.4.1 + jQuery 3.7.1)
├── data/csv/            2014 GRU consumption CSVs
├── scripts/build_db.py  CSV → SQLite builder
├── Dockerfile           Multi-stage: build DB → run gunicorn
├── render.yaml          Render Blueprint
└── .github/workflows/   CI: ruff + tests + smoke test
```

## Original

The original 2015 Django 1.8 / MySQL project lives at `~/code/gvilleapp` and is preserved untouched.
