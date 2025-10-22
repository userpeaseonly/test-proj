# Task Management System

A comprehensive Django-based task management system with user authentication, admin analytics, and API throttling.

## Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- PostgreSQL (handled by Docker)

## Setup Instructions

### 1. Environment Configuration

First, create the `env` folder in the project root:

```bash
mkdir env
```

Then create the appropriate environment file based on your deployment:

**For Local Development:**
Create `env/.local` file with your local environment variables.

**For Production:**
Create `env/.production` file with your production environment variables.

### 2. Running the Application

**For Local Development:**
```bash
docker-compose -f docker-compose.local.yml up --build
```

**For Production:**
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

## Environment Variables

Make sure to configure the following variables in your environment files:

### Example `env/.local` file:
```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-for-development
DJANGO_ENV=local

# Database Configuration
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=crud_db_local
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=db
POSTGRES_PORT=5432

# CORS and CSRF Settings
CORS_ALLOWED_ORIGINS=http://0.0.0.0:8011,http://localhost:3001,http://localhost:3000,http://localhost:8011
CSRF_TRUSTED_ORIGINS=http://0.0.0.0:8011,http://localhost:3001,http://localhost:3000,http://localhost:8011

# Other Settings
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### Example `env/.production` file:
```bash
# Django Settings
DJANGO_SECRET_KEY=your-very-secure-production-secret-key
DJANGO_ENV=production

# Database Configuration
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=crud_db_prod
POSTGRES_USER=crud_user
POSTGRES_PASSWORD=your-secure-database-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# CORS and CSRF Settings
CORS_ALLOWED_ORIGINS=https://test-proj-backend.trust-building.uz,https://test-proj-client.trust-building.uz
CSRF_TRUSTED_ORIGINS=https://test-proj-backend.trust-building.uz,https://test-proj-client.trust-building.uz

# Other Settings
DEBUG=0
ALLOWED_HOSTS=test-proj-backend.trust-building.uz,your-domain.com
```

## Features

- User authentication with JWT tokens
- Task management with CRUD operations
- Admin analytics dashboard
- API rate limiting and throttling
- Multi-language support (Uzbek, English, Russian)
- Responsive admin interface with light theme

## API Documentation

Once running, access the API documentation at:
- Local: `http://localhost:8011/api/schema/swagger/`
- Production: `https://your-domain/api/schema/swagger/`

## Admin Access

- Local: `http://localhost:8011/admin/`
- Analytics Dashboard: `http://localhost:8011/analytics-admin/`
- Production: `https://your-domain/admin/`