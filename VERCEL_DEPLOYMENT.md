# Vercel deployment checklist

Vercel supports Django by detecting `manage.py`, loading the configured WSGI entrypoint, and serving collected static files through its CDN. This project already has `manage.py`, `WSGI_APPLICATION`, `STATIC_ROOT`, and `requirements.txt`, so a custom `vercel.json` is not required. See [Vercel's Django guide](https://vercel.com/docs/frameworks/full-stack/django).

## Required before production

- **Plan:** ARS Garments is a commercial storefront. Vercel Hobby is limited to non-commercial personal use; use a plan permitted for business deployment.
- **Git:** The `main` branch of `sabarish-077/ARS_GARMENTS` is pushed to GitHub. Vercel has detected it as an import candidate; import that repository with the project root set to the folder containing `manage.py`.
- **Database:** Vercel cannot reach the MySQL server on your Windows computer. Provision managed MySQL that accepts a secure remote connection from the Vercel deployment. Create a least-privilege app account with `SELECT`, `INSERT`, `UPDATE`, and `DELETE` on `ars_garments`; use a separate migration account for schema changes.
- **Secrets:** Add the following environment variables in Vercel Project Settings. Never commit `.env` or paste credential values into chat.

| Variable | Value |
| --- | --- |
| `DJANGO_SECRET_KEY` | Unique random secret, at least 50 characters |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | Exact `your-project.vercel.app` hostname and any custom hostname, comma-separated |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | HTTPS origins for the production and custom domains, comma-separated |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` |
| `DJANGO_TRUST_PROXY_SSL_HEADER` | `True` |
| `DJANGO_TRUST_PROXY_CLIENT_IP` | `True` (Vercel overwrites `X-Forwarded-For`) |
| `DJANGO_SECURE_HSTS_SECONDS` | Start at `0`; increase after HTTPS and the production domain are verified |
| `MYSQL_DATABASE` | `ars_garments` |
| `MYSQL_USER` / `MYSQL_PASSWORD` | MySQL runtime app account |
| `MYSQL_HOST` / `MYSQL_PORT` | Managed MySQL hostname and port |

Vercel supplies `VERCEL_URL`; settings add that deployment host and its HTTPS origin automatically. Keep the stable production domain in the allowlists too. Production requests use Vercel's forwarded HTTPS header; do not enable forwarded headers behind an untrusted proxy.

## Deployment steps

1. Create/choose the Vercel project and connect the Git repository at the project root (the folder containing `manage.py`).
2. Add the production environment variables above. Do not set `DJANGO_DB_MIGRATION=True` for web requests.
3. Run Django migrations once against the managed MySQL database using the separate migration account and `DJANGO_DB_MIGRATION=True`; then unset it.
4. Trigger a production deployment from the connected repository. Vercel detects Django and automatically runs `collectstatic` because `STATIC_ROOT` is configured.
5. Create a Django superuser against the production database, open `/account/login/`, then verify `/dashboard/`, catalog, checkout, contact forms, and static images on the deployed domain.

Vercel runs the Django app as a Function; production behavior and database access must be checked on the deployed environment. Do not treat a successful build as proof that the external database credentials or migrations work.

## Vercel build dependency

The project uses PyMySQL as Django's MySQLdb-compatible driver. Do not restore `mysqlclient`: Vercel's Python builder does not include the MySQL/MariaDB development libraries required to compile it. After changing dependencies, commit and push the changes, then redeploy from the connected GitHub branch.
