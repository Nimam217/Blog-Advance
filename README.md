# Blog-Advance

[![Django Test](https://github.com/Nimam217/Blog-Advance/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Nimam217/Blog-Advance/actions/workflows/docker-image.yml)

A blog platform built with **Django 5.2** and **Django REST Framework**. It provides a server-rendered web interface and a versioned REST API, with **Redis caching**, **Celery** background tasks, a **Docker**-based development and production setup, automated tests, load testing, and CI.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Web Routes](#web-routes)
- [REST API](#rest-api)
- [Caching](#caching)
- [Background Tasks](#background-tasks)
- [Environment Variables](#environment-variables)
- [Getting Started (Development)](#getting-started-development)
- [Production Deployment](#production-deployment)
- [Running Tests](#running-tests)
- [Load Testing](#load-testing)
- [Continuous Integration](#continuous-integration)
- [Code Style](#code-style)
- [License](#license)

---

## Features

### Accounts

- Custom `User` model with **email as the login field**
- A `Profile` and an auth `Token` are created automatically for every new user (via `post_save` signals)
- Email activation (`is_verified`) and resend-activation endpoint
- Password change and password reset (both web and API)
- Authentication with Token, JWT (simplejwt), Session, and Basic auth
- Profile endpoint restricted to the owner, and only if the account is verified

### Blog

- Posts with title, content, image, category, publish status, and author
- Categories (managed by staff only)
- Comments with **nested replies** (`parent`) and moderation status
- Web views for listing, viewing, creating, updating, and deleting posts
- Only published posts (`status=True`) and approved comments are exposed through the API
- Only the author of a post or comment can modify it

### REST API

- Full CRUD for posts, categories, and comments
- Filtering, searching, and ordering (`django-filter`, DRF `SearchFilter`, `OrderingFilter`)
- Custom paginated responses with totals and links
- Swagger UI and ReDoc documentation (`drf-yasg`)

### Engineering

- Redis cache for list endpoints with automatic invalidation through signals
- Celery workers for emails and a Celery Beat periodic cleanup job
- Split settings: `development` and `production`
- Multi-stage `Dockerfile`, separate dev and prod Docker Compose files
- Nginx reverse proxy and Gunicorn in production
- pytest + pytest-django test suite, Faker-based fake data command
- Locust load testing in distributed mode (master and worker)
- GitHub Actions workflow running `manage.py check`, `flake8`, and `pytest`

---

## Tech Stack

| Area | Technology |
|------|------------|
| Language | Python 3.11 |
| Framework | Django 5.2, Django REST Framework |
| Auth | Token, JWT (`djangorestframework-simplejwt`), Session |
| Database | SQLite (development), PostgreSQL 15 (production) |
| Cache and broker | Redis (`django-redis`) |
| Task queue | Celery, `django-celery-beat` |
| API docs | `drf-yasg` (Swagger / ReDoc) |
| Emails | `django-mail-templated`, smtp4dev (development) |
| Web server | Gunicorn behind Nginx |
| Testing | pytest, pytest-django, Faker |
| Load testing | Locust |
| Code quality | black, flake8 |
| Containers | Docker, Docker Compose |
| Configuration | `python-decouple` |

---

## Architecture

### Development stack (`docker-compose.yml`)

```text
                 +-------------+
   browser ----> |   backend   |  runserver :8000
                 +------+------+
                        |
        +---------------+----------------+
        |                                |
   +----v----+     +-----------+     +---v-------+
   |  redis  | <-- |  celery   |     | smtp4dev  |
   | cache + |     |  worker   |     | (emails)  |
   | broker  | <-- |  + beat   |     +-----------+
   +---------+     +-----------+

   locust master + worker  ->  load tests against backend
```

### Production stack (`docker-compose.prod.yml`)

```text
 client --> nginx :8080 --> gunicorn (backend :8000) --> PostgreSQL
                |                     |
                |                     +--> Redis <-- Celery worker / beat
                +--> /static/ and /media/ served directly
```

---

## Project Structure

```text
.
├── accounts                      # Users, profiles, authentication
│   ├── api/v1
│   │   ├── urls/                 # user.py and profile.py routes
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   ├── views.py
│   │   └── utils.py
│   ├── models/                   # user.py, profile.py
│   ├── signals.py                # Auto-create Profile and Token
│   ├── tasks.py                  # Celery tasks (emails, cleanup)
│   ├── tests/                    # test_accounts_api, test_accounts_render
│   ├── urls.py
│   └── views.py
├── blog                          # Posts, categories, comments
│   ├── api/v1
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   ├── paginations.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── management/commands/
│   │   └── fake_data.py          # Generate demo data
│   ├── models.py
│   ├── signals.py                # Cache invalidation
│   ├── forms.py
│   ├── tests/                    # test_blog_api, test_blog_render
│   ├── urls.py
│   └── views.py
├── core                          # Project configuration
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── celery.py
│   ├── locust/locustfile.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates                     # base, blog, email, registration
├── nginx/nginx.conf
├── .github/workflows/docker-image.yml
├── Dockerfile
├── docker-compose.yml            # Development
├── docker-compose.prod.yml       # Production
├── wait-for-it.sh
├── pytest.ini
├── requirements.txt
├── manage.py
└── LICENSE
```

---

## Data Models

### User

| Field | Type | Notes |
|-------|------|-------|
| `email` | EmailField | Unique, `USERNAME_FIELD` |
| `is_active` | Boolean | Default `True` |
| `is_verified` | Boolean | Default `False`, set by email activation |
| `is_staff`, `is_superuser` | Boolean | Standard flags |
| `create_date`, `update_date` | DateTime | Automatic |

### Profile

One-to-one with `User` (`related_name="profile"`), created automatically by a signal.

| Field | Type |
|-------|------|
| `first_name`, `last_name` | CharField |
| `image` | ImageField (optional) |
| `description` | TextField (optional) |
| `create_date`, `update_date` | DateTime |

### Post

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField (max 100) | |
| `content` | TextField | |
| `status` | Boolean | `True` means published and visible in the API |
| `author` | FK to `Profile` | |
| `category` | FK to `Category` | `SET_NULL` |
| `image` | ImageField | Optional, `upload_to="images/"` |
| `created_at`, `published_at`, `updated_at` | DateTime | |

### Category

| Field | Type |
|-------|------|
| `name` | CharField |

### Comment

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField | |
| `content` | TextField | |
| `author` | FK to `Profile` | |
| `post` | FK to `Post` | `related_name="comments"` |
| `parent` | FK to self | Optional, for replies (`related_name="replies"`) |
| `status` | Boolean | Only approved comments appear in the API |
| `created_at`, `updated_at` | DateTime | |

---

## Web Routes

| URL | Description |
|-----|-------------|
| `/blog/post/` | Post list |
| `/blog/post/<id>/` | Post detail with comments (login required) |
| `/blog/post/create/` | Create a post (login required) |
| `/blog/post/<id>/update/` | Update a post (login required) |
| `/blog/post/<id>/delete/` | Delete a post (login required) |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |
| `/accounts/password_change/` | Change password |
| `/accounts/password_reset/` | Reset password by email |
| `/admin/` | Django admin |

---

## REST API

### Accounts: `/accounts/api/v1/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `registration/` | Register (sends activation email) |
| GET | `activation/confirm/<token>/` | Activate account |
| POST | `activation/resend/` | Resend activation email |
| POST | `token-login/` | Obtain an auth token |
| POST | `token-destroy/` | Discard the auth token |
| POST | `jwt/token/` | Obtain JWT access and refresh tokens |
| POST | `jwt/refresh/` | Refresh the access token |
| POST | `jwt/verify/` | Verify a token |
| PUT | `change_password/` | Change password |
| POST | `reset_password/` | Request a password reset email |
| POST | `reset_password/confirm/<token>/` | Set a new password |
| GET, PUT, PATCH | `profile/` | Current user's profile (owner and verified only) |

### Blog: `/blog/api/v1/`

| Resource | Endpoint | Permissions |
|----------|----------|-------------|
| Posts | `post/` and `post/<id>/` | Authenticated; only the author can modify |
| Categories | `category/` and `category/<id>/` | Read for everyone; write for staff only |
| Comments | `comment/` and `comment/<id>/` | Authenticated; only the author can modify |

Each resource supports the standard `ModelViewSet` actions (`list`, `create`, `retrieve`, `update`, `partial_update`, `destroy`).

**Query parameters**

| Resource | Filters | Search | Ordering | Page size |
|----------|---------|--------|----------|-----------|
| Posts | `category` (exact, in), `author` | `title`, `content` | `created_at` | 2 |
| Comments | `post`, `author`, `parent` | `content`, `name` | `created_at`, `updated_at` | 3 |
| Categories | none | none | none | 2 |

Examples:

```text
GET /blog/api/v1/post/?category__in=1,2&search=django&ordering=-created_at
GET /blog/api/v1/comment/?post=5&parent=3
```

### Authentication example

```bash
# Get a JWT
curl -X POST http://127.0.0.1:8000/accounts/api/v1/jwt/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your-password"}'

# Use it
curl http://127.0.0.1:8000/blog/api/v1/post/ \
  -H "Authorization: Bearer <access_token>"
```

### API documentation

| URL | Description |
|-----|-------------|
| `/swagger/` | Swagger UI |
| `/redoc/` | ReDoc |
| `/swagger/dock.json/` | Raw OpenAPI schema |

---

## Caching

Redis is used as the Django cache backend (`django-redis`).

- `GET /blog/api/v1/post/` caches each distinct query string for **20 minutes** (key: `post_list:<query>`)
- `GET /blog/api/v1/category/` caches each page for **20 minutes** (key: `category_list:<page>`)
- `blog/signals.py` clears the relevant keys whenever a `Post` or `Category` is saved or deleted, so clients never see stale lists

---

## Background Tasks

Celery uses Redis as the broker (`redis://redis:6379/1`). The Celery Beat scheduler uses the database (`django_celery_beat.schedulers:DatabaseScheduler`), so periodic schedules are managed from the Django admin.

| Task | Description |
|------|-------------|
| `send_email_register_activation` | Sends the activation email after registration |
| `send_email_resend_activation_email` | Resends the activation email |
| `send_email_reset_password` | Sends the password reset email |
| `delete_old_posts` | Deletes posts that have not been updated for more than 365 days |

The email tasks retry automatically on `ConnectionError` with exponential backoff (up to 5 retries).

To run `delete_old_posts` periodically, create a periodic task for it in the admin under **Periodic Tasks**.

---

## Environment Variables

### Development

The development Compose file sets `SECRET_KEY` and `DEBUG` directly for every service, so no `.env` file is required to get started.

### Production (`.env.prod`)

Create a `.env.prod` file in the project root:

```env
SECRET_KEY=change-me-to-a-long-random-value
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=blog
POSTGRES_USER=blog_user
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=database
POSTGRES_PORT=5432
```

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key (required) |
| `ALLOWED_HOSTS` | Comma-separated host list (default `*`) |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database credentials (also used by the PostgreSQL container) |
| `POSTGRES_HOST` | Database host, `database` in Docker Compose |
| `POSTGRES_PORT` | Database port |

> `.env` and `.env.prod` are listed in `.gitignore`. Never commit them.

---

## Getting Started (Development)

### Prerequisites

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Nimam217/Blog-Advance.git
cd Blog-Advance
```

### 2. Start the stack

```bash
docker compose up --build
```

The `migration` service applies migrations first. The `backend`, `celery_worker`, and `celery_beat` services start after it, once Redis is healthy.

### 3. Create a superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

### 4. (Optional) Generate demo data

```bash
docker compose exec backend python manage.py fake_data
```

This creates a user, a profile, categories, 10 posts, and comments with replies. Each run adds a new user and new posts.

### 5. Open the services

| Service | URL |
|---------|-----|
| Web application | http://127.0.0.1:8000/blog/post/ |
| Swagger UI | http://127.0.0.1:8000/swagger/ |
| ReDoc | http://127.0.0.1:8000/redoc/ |
| Admin | http://127.0.0.1:8000/admin/ |
| smtp4dev (read outgoing emails) | http://127.0.0.1:5000 |
| Locust UI | http://127.0.0.1:8089 |

In development, emails are not sent to real inboxes. Open smtp4dev to read the activation and password reset messages.

---

## Production Deployment

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Services:

| Service | Role |
|---------|------|
| `database` | PostgreSQL 15 with the `postgres_data` volume and a health check |
| `migration` | Waits for the database (`wait-for-it.sh`), then runs `migrate` |
| `backend` | Runs `collectstatic`, then Gunicorn on port 8000 (internal) |
| `redis` | Cache and Celery broker |
| `celery_worker` | Processes background tasks |
| `celery_beat` | Runs scheduled tasks |
| `nginx` | Public entry point on port **8080**; serves `/static/` and `/media/` directly |

The application is then available at http://127.0.0.1:8080.

Production settings (`core.settings.production`) use PostgreSQL and `DEBUG = False`. Update `CSRF_TRUSTED_ORIGINS` in that file when you serve the site from a real domain.

---

## Running Tests

The suite uses **pytest** with **pytest-django** (`pytest.ini` points to `core.settings.development`).

```bash
docker compose exec backend pytest . -vv
```

Test layout:

| Path | Covers |
|------|--------|
| `accounts/tests/test_accounts_api/` | API views, permissions, serializers |
| `accounts/tests/test_accounts_render/` | Models, signals, URLs |
| `blog/tests/test_blog_api/` | Post, category, comment APIs, serializers, URLs |
| `blog/tests/test_blog_render/` | Forms, models, URLs, web views |

Run a subset:

```bash
docker compose exec backend pytest blog/tests/test_blog_api -v
docker compose exec backend pytest -k "comment" -v
```

---

## Load Testing

The development stack includes a distributed Locust setup (one master and one worker). The scenario logs in with JWT and repeatedly requests the post list (`core/locust/locustfile.py`).

1. Create a user whose credentials match the ones in `locustfile.py` (or edit them to match your user)
2. Open http://127.0.0.1:8089
3. Set the number of users and spawn rate, then start the test

The host is already configured as `http://backend:8000`.

---

## Continuous Integration

The GitHub Actions workflow (`.github/workflows/docker-image.yml`) runs on every push and pull request to `master`:

1. Start the Docker Compose stack
2. `python manage.py check`
3. `flake8 .`
4. `pytest . -vv`
5. Print container logs on failure, then clean up

---

## Code Style

```bash
docker compose exec backend black .
docker compose exec backend flake8 .
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Nima** — [GitHub: Nimam217](https://github.com/Nimam217)