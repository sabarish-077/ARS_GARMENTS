# ARS Garments storefront

A responsive Django storefront based on the supplied Stitch design archive. The pages use Django templates, custom CSS, Bootstrap 5, Django ORM, and MySQL.

## Screens and routes

- `/` — editorial storefront, collections, manufacturing overview and brand story
- `/shop/` — searchable catalog with category, maximum-price and sort filters
- `/product/<slug>/` — product information and add-to-bag form
- `/cart/` and `/checkout/` — session cart, delivery form, cash-on-delivery order placement
- `/track-order/` — status lookup by order number and checkout phone number
- `/b2b/` — manufacturing services, estimate calculator and saved enquiry form
- `/factory/` and `/contact/` — factory story and customer enquiry form
- `/newsletter/subscribe/` — newsletter signup stored in MySQL
- `/account/register/`, `/account/login/` — Django account registration and login
- `/admin/` — Django admin for categories, products, orders, enquiries and subscribers

## Project structure

```text
ars_garments/                 Django settings and root URL configuration
store/                        Catalog, account, contact and order app
  management/commands/        Idempotent starter catalog command
  migrations/                 MySQL schema history
templates/                    Shared layout and individual Django pages
static/store/css/site.css     Brand styling and mobile/tablet breakpoints
stitch_ars_garments_e_commerce_storefront/  Supplied ZIP references
```

The ZIP has eight exported screen references and a design-system document under `stitch_ars_garments_e_commerce_storefront/`. The exported page code uses Tailwind, so the working pages were rebuilt with Bootstrap and the design tokens. The archive includes only full-screen PNG reference images; product photography is linked to the same image host used by the supplied HTML exports.

## Local setup (Windows PowerShell)

Install Python 3.11 or later and MySQL 8.0 or later first. Create a MySQL database:

```sql
CREATE DATABASE ars_garments CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

From this folder, set up the project and install its dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

The MySQL backend needs the `mysqlclient` driver. If `runserver` reports `No module named 'MySQLdb'` or says to install `mysqlclient`, install the project requirements with the same Python launcher used to start Django, then confirm the driver imports:

```powershell
py -m pip install -r requirements.txt
py -c "import MySQLdb; print('MySQL driver is installed')"
py manage.py runserver
```

If MySQL reports `Access denied for user 'root'@'localhost' (using password: NO)`, Django has reached the database but did not receive a password. Check that `.env` exists beside `manage.py` and that `MYSQL_PASSWORD` contains your local MySQL password. Keep that password in `.env`; do not paste it into source files or chat.

Copy `.env.example` to `.env` and edit the MySQL password and Django secret key. Settings load this local file and it is excluded from Git. You can also set the same values in the current PowerShell session; existing environment variables take precedence:

```powershell
Copy-Item .env.example .env
notepad .env
```

Apply the schema, load the starter styles, create an administrator and run Django:

```powershell
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Manage inventory and review orders at `http://127.0.0.1:8000/admin/`.

## Before deployment

Set a private `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and production `DJANGO_ALLOWED_HOSTS`; use a restricted MySQL account and HTTPS. Run `python manage.py collectstatic` as part of deployment. Set product stock, prices, and any operational contact information from the admin before accepting real orders. Checkout records cash-on-delivery orders; no payment gateway is connected. Product image URLs currently point to the supplied design export's external image host, so replace them with owned/managed image URLs if you need self-hosted product photography.
