
## 🔧 Local Development Setup

### Option 1: Docker Development (Recommended)

```bash
# Clone and navigate
git clone <repository-url>
cd crud-proj

# Start development environment
docker compose -f docker-compose.local.yml up -d

# View logs
docker compose -f docker-compose.local.yml logs -f web

# Stop services
docker compose -f docker-compose.local.yml down
```

### Option 2: Native Python Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DJANGO_SECRET_KEY='your-secret-key'
export POSTGRES_ENGINE='django.db.backends.sqlite3'
export POSTGRES_DB='db.sqlite3'

# Run migrations
python manage.py migrate

# Create admin user
python manage.py create_admin --email admin@test.com --password admin123

# Start development server
python manage.py runserver 8011
```

### Development Commands

```bash
# Create new migrations
docker exec crud-proj-web-1 python manage.py makemigrations

# Apply migrations
docker exec crud-proj-web-1 python manage.py migrate

# Create superuser
docker exec crud-proj-web-1 python manage.py createsuperuser

# Access Django shell
docker exec -it crud-proj-web-1 python manage.py shell

# Run tests
docker exec crud-proj-web-1 python manage.py test

# Collect static files
docker exec crud-proj-web-1 python manage.py collectstatic --no-input
```

## 🏭 Production Deployment

### Environment Configuration

Create a `.env.production` file:

```env
# Django Settings
DJANGO_SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
POSTGRES_ENGINE=django.db.backends.postgresql
POSTGRES_DB=taskmanagement_prod
POSTGRES_USER=taskman_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Security Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SSL/HTTPS Settings (for production)
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Production Deployment with Docker

```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Start production services
docker compose -f docker-compose.prod.yml up -d

# Initialize database
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py create_admin --email admin@yourdomain.com --password <secure-password>
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# Check service status
docker compose -f docker-compose.prod.yml ps
```

### Production with Nginx Reverse Proxy

The production setup includes Nginx for:
- Static file serving
- SSL termination
- Load balancing
- Security headers

```bash
# Start full production stack
docker compose -f docker-compose.prod.yml up -d

# Nginx will be available on port 80/443
# Django app accessible via Nginx proxy
```

### SSL Certificate Setup

For production HTTPS, add SSL certificates:

```bash
# Create certificates directory
mkdir -p compose/production/nginx/certs

# Add your SSL certificates
cp your-domain.crt compose/production/nginx/certs/
cp your-domain.key compose/production/nginx/certs/

# Update nginx.conf to use SSL
# (See compose/production/nginx/nginx.conf)
```

## 🔌 API Usage

### Authentication Flow

1. **Register a new user**:
```bash
curl -X POST http://localhost:8011/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

2. **Login to get access token**:
```bash
curl -X POST http://localhost:8011/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

3. **Use the access token**:
```bash
curl -X GET http://localhost:8011/api/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Task Operations

```bash
# Create a task
curl -X POST http://localhost:8011/api/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation"
  }'

# List user tasks
curl -X GET http://localhost:8011/api/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Update task status
curl -X PATCH http://localhost:8011/api/tasks/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Get task statistics
curl -X GET http://localhost:8011/api/tasks/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛡️ API Throttling

The API includes comprehensive rate limiting:

### Default Rates
- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Admin users**: 5x higher limits

### Endpoint-Specific Limits
- **Login**: 10 attempts/hour per IP
- **Registration**: 5 registrations/hour per IP
- **Task creation**: 100 tasks/hour per user
- **Task updates**: 200 updates/hour per user
- **Burst protection**: 60 requests/minute

### Throttle Response
When throttled, the API returns HTTP 429:
```json
{
    "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

## 📊 Admin Analytics

Access comprehensive analytics at `/analytics-admin/`:

### Features
- **User Analytics**: User productivity and task completion rates
- **Task Analytics**: System-wide task statistics and recent activity
- **Dashboard**: Overview with key metrics and charts
- **Read-only Access**: Safe data viewing without modification rights

### Access Requirements
- Admin role user account
- Login at `/admin/` first, then navigate to `/analytics-admin/`

## 🧪 Testing

### Running Tests
```bash
# Run all tests
docker exec crud-proj-web-1 python manage.py test

# Run specific app tests
docker exec crud-proj-web-1 python manage.py test users
docker exec crud-proj-web-1 python manage.py test tasks

# Run with coverage
docker exec crud-proj-web-1 coverage run --source='.' manage.py test
docker exec crud-proj-web-1 coverage report
```

### Create Test Data
```bash
# Create sample users and tasks
docker exec crud-proj-web-1 python manage.py create_analytics_data --users 15 --tasks 75

# Create admin user
docker exec crud-proj-web-1 python manage.py create_admin --email admin@test.com --password admin123
```

## 📁 Project Structure

```
crud-proj/
├── application/           # Main Django project
│   ├── settings/         # Environment-specific settings
│   ├── throttles.py      # Custom throttling classes
│   └── urls.py          # Main URL configuration
├── users/               # User authentication app
│   ├── models.py        # User model with roles
│   ├── views.py         # Auth views with throttling
│   └── serializers.py   # User serializers
├── tasks/               # Task management app
│   ├── models.py        # Task model
│   ├── views.py         # Task CRUD views
│   └── serializers.py   # Task serializers
├── analytics/           # Admin analytics app
│   ├── admin.py         # Custom admin site
│   ├── views.py         # Analytics views
│   └── management/      # Management commands
├── templates/           # Django templates
│   └── admin/          # Admin interface templates
├── compose/            # Docker configuration
│   ├── local/          # Local development
│   └── production/     # Production deployment
├── docker-compose.local.yml   # Local development
├── docker-compose.prod.yml    # Production deployment
├── requirements.txt    # Python dependencies
└── THROTTLING.md      # Detailed throttling documentation
```

## 🐛 Troubleshooting

### Common Issues

**Database connection issues**:
```bash
# Check if PostgreSQL is running
docker compose -f docker-compose.local.yml ps

# Restart services
docker compose -f docker-compose.local.yml restart
```

**Migration issues**:
```bash
# Reset migrations (development only)
docker exec crud-proj-web-1 python manage.py migrate --fake-initial

# Create new migration
docker exec crud-proj-web-1 python manage.py makemigrations
```

**Permission issues**:
```bash
# Check user permissions
docker exec -it crud-proj-web-1 python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='your-email')
>>> print(user.role, user.is_staff, user.is_superuser)
```

**Container issues**:
```bash
# View container logs
docker logs crud-proj-web-1

# Access container shell
docker exec -it crud-proj-web-1 /bin/bash

# Rebuild containers
docker compose -f docker-compose.local.yml build --no-cache
```

## 📚 Additional Documentation

- **API Throttling**: See `THROTTLING.md` for detailed rate limiting information
- **OpenAPI Schema**: Available at `/api/schema/`
- **Swagger UI**: Interactive docs at `/swagger/`
- **ReDoc**: Alternative docs at `/redoc/`

## 🔒 Security Considerations

### Production Security Checklist
- [ ] Use strong `DJANGO_SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use HTTPS with SSL certificates
- [ ] Set secure cookie flags
- [ ] Configure proper CORS origins
- [ ] Use strong database passwords
- [ ] Regular security updates
- [ ] Monitor API throttling logs
- [ ] Backup database regularly

### Environment Variables
Store sensitive data in environment variables:
- Database credentials
- Secret keys
- API keys
- Domain configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Submit issues on the project repository
- Contact the development team
