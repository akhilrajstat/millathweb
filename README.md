# Millath College ERP

A modular, Django 5.x-based Enterprise Resource Planning system for Millath College.

---

## Project Structure

```
project_root/
├── apps/
│   └── accounts/          ← Custom user model, auth views, groups command
│       ├── management/commands/create_groups.py
│       ├── migrations/
│       ├── admin.py
│       ├── apps.py
│       ├── models.py      ← User + UserRole enum
│       ├── urls.py
│       └── views.py
├── config/
│   ├── settings/
│   │   ├── base.py        ← Shared settings (all secrets from env)
│   │   ├── development.py ← Console email, no HTTPS
│   │   └── production.py  ← Full security headers active
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   └── css/main.css
├── templates/
│   ├── base.html
│   └── accounts/          ← Login, lockout, dashboard, password-reset templates
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & create virtualenv

```bash
git clone <repo-url> millath-erp
cd millath-erp
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create default groups

```bash
python manage.py create_groups
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
# After creation, approve the account via the shell or admin:
# python manage.py shell -c "from apps.accounts.models import User; User.objects.filter(username='<name>').update(is_approved=True)"
```

### 7. Start the development server

```bash
python manage.py runserver
```

Visit <http://localhost:8000/accounts/login/> to see the login page.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key (long random string) |
| `DEBUG` | ✅ | `True` for dev, `False` for prod |
| `ALLOWED_HOSTS` | ✅ | Comma-separated hostnames |
| `DJANGO_SETTINGS_MODULE` | ✅ | `config.settings.development` or `config.settings.production` |
| `DATABASE_URL` | ✅ prod | Postgres DSN (SQLite used if absent) |
| `EMAIL_HOST` | ✅ prod | SMTP hostname |
| `EMAIL_PORT` | ✅ prod | SMTP port (default 587) |
| `EMAIL_HOST_USER` | ✅ prod | SMTP username |
| `EMAIL_HOST_PASSWORD` | ✅ prod | SMTP password |
| `DEFAULT_FROM_EMAIL` | ✅ prod | Sender display name + address |

---

## Security Baseline

- **No hardcoded secrets** anywhere — all from `.env`
- **django-axes**: locks out after 5 failed login attempts (per username + IP) for 30 min
- **Password policy**: minimum 10 characters, not common, not numeric-only
- **is_approved gate**: users cannot log in until an admin approves their account
- **Production headers**: HSTS (1 year + subdomains + preload), `SECURE_SSL_REDIRECT`, secure cookies, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`
- **Upload limits**: 5 MB max for both form data and file uploads

---

## Management Commands

```bash
# Create the four default role groups
python manage.py create_groups
```

---

## User Roles

Defined as `UserRole(models.TextChoices)` in `apps/accounts/models.py`:

| Constant | DB value | Display |
|---|---|---|
| `UserRole.SUPER_ADMIN` | `super_admin` | Super Admin |
| `UserRole.OFFICE_STAFF` | `office_staff` | Office Staff |
| `UserRole.FACULTY` | `faculty` | Faculty |
| `UserRole.STUDENT` | `student` | Student |

Always reference roles by their constant, never by raw string.

---

## Deploying to Render

This project is pre-configured for automated deployment on [Render](https://render.com) using `render.yaml` (Infrastructure-as-Code Blueprint) or manual service setup.

### Step 1: Push Code to GitHub
Ensure all your latest changes and the `render.yaml` / `build.sh` files are pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure Render deployment"
git push origin main
```

### Step 2: Create a Render Account & Connect Repository
1. Sign up or log in at [render.com](https://render.com).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository (`millathweb`).
4. Render will automatically detect `render.yaml` and provision:
   - A **Web Service** (Python 3.12, Gunicorn WSGI server)
   - A **PostgreSQL Database** (Free tier) with `DATABASE_URL` linked automatically.

*(Alternatively, if setting up manually: create a PostgreSQL database, then create a Web Service with Build Command `./build.sh` and Start Command `gunicorn config.wsgi:application`, linking `DATABASE_URL` from the database).*

### Step 3: Configure Environment Variables
In the Render Dashboard for your Web Service, ensure the following environment variables are set under **Environment**:

| Variable | Value | Notes |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | Enables production security & WhiteNoise |
| `SECRET_KEY` | *(Generate a secure 50+ char random string)* | Auto-generated by Blueprint |
| `DEBUG` | `False` | Never enable in production |
| `ALLOWED_HOSTS` | `.onrender.com,yourcustomdomain.com` | Automatically includes `.onrender.com` |
| `DATABASE_URL` | *(From Render PostgreSQL)* | Auto-linked by Blueprint |

### Step 4: Build & Deployment Process
During deployment, Render will automatically execute [`build.sh`](file:///d:/Programs%20-%20New/Millath%20Website/build.sh) as the build command:
1. `pip install -r requirements.txt`
2. `python manage.py collectstatic --noinput` (WhiteNoise compresses and hashes static files)
3. `python manage.py migrate` (Applies all database schema migrations)

### Step 5: Post-Deployment Initialisation (One-Time Setup)
After the first deployment completes successfully, open your Web Service in the Render dashboard, navigate to the **Shell** tab, and run:

```bash
# 1. Create default role permission groups
python manage.py create_groups

# 2. Seed initial site settings, banners, and sample notices
python manage.py seed_initial_data

# 3. Create your administrative superuser
python manage.py createsuperuser
```

Your website and management portal are now live at `https://<your-service-name>.onrender.com/`!

---

## Production Deployment (gunicorn + WhiteNoise)

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## Before Packaging / Deploying

Before deploying to staging/production or distributing the codebase as an archive, ensure strict environment hygiene.

### Prohibited Artifacts (Never Deploy)

The following items are strictly excluded in `.gitignore` and must never be included in deployment archives:

| Artifact | Why It Must Be Excluded |
|---|---|
| `db.sqlite3`, `*.sqlite3`, `*.db` | Local SQLite databases contain stale development records, test passwords, and mock state that will corrupt or overwrite production PostgreSQL data. |
| `.env` / `*.env` | Local environment files contain local debug credentials, development keys, and machine-specific secrets. Production uses host environment variables or secure vault injection. |
| `venv/`, `.venv/`, `env/` | Local virtual environments contain operating-system-specific compiled binaries (e.g. Windows `.exe`/`.pyd` vs Linux `.so`) and must be built fresh on the target server. |
| `__pycache__/`, `*.pyc` | Bytecode caches are platform-specific and auto-generated by the runtime. |
| `media/` | User-uploaded files (photos, syllabus PDFs) belong in persistent blob/cloud storage or persistent server mounts, not in code deployment packages. |
| `staticfiles/` | Production static assets must be collected fresh via `python manage.py collectstatic --noinput` on the production server. |

### Automated Packaging Script

To create a clean deployment archive that enforces all exclusions automatically:

```bash
python scripts/package_project.py [optional_archive_name.zip]
```

---

## Adding New Apps

1. Create `apps/<appname>/` with an `AppConfig` whose `name = "apps.<appname>"`.
2. Add `"apps.<appname>"` to `LOCAL_APPS` in `config/settings/base.py`.
3. Run `python manage.py makemigrations <appname>` and `python manage.py migrate`.

---

## Before Going Live

> **Action required by office staff / admin before public launch.**

The following template files contain **temporary placeholder images** sourced from
[Unsplash](https://unsplash.com/) under their free-use licence. These images are
clearly marked in the HTML source with the comment:
```
<!-- TEMP PLACEHOLDER — replace with real campus photography via admin -->
```

They must be replaced with authentic Millath College campus photography before
the site is launched publicly. **Do not claim or imply that any placeholder image
depicts the actual college, its staff, or its students.**

### Placeholder Image Inventory

| Template File | Section | How to Replace |
|---|---|---|
| `templates/home.html` | **Hero background** | Upload a banner image via Django Admin → **Core → Site Banners**. Once a banner is live, the hero auto-uses it. |
| `templates/home.html` | **Programme cards** (6 images, one per B.Ed specialisation) | Upload a programme image via Django Admin → **Programs → Programs** → edit each programme → *Image* field. |
| `templates/home.html` | **Gallery section** (8 placeholder images) | Upload real campus photos via Django Admin → **Gallery → Gallery Images**. Once any images exist, placeholders disappear automatically. |

### Checklist Before Launch

- [ ] Replace all placeholder images (see table above)
- [ ] Set college name, tagline, address, phone, email, social links via Admin → **Core → Site Settings**
- [ ] Upload college logo via Admin → **Core → Site Settings** → *Logo* field
- [ ] Verify faculty profiles contain real qualifications (not fabricated by test scripts)
- [ ] Run `python scripts/package_project.py` to generate the deployment archive
- [ ] Delete `db.sqlite3` from local machine before sharing the archive



