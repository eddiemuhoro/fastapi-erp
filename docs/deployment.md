# Deployment Guide

This guide covers deploying the FastAPI ERP System to various environments, from development to production.

## Table of Contents

- [Environment Overview](#environment-overview)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Database Setup](#database-setup)
- [Monitoring & Logging](#monitoring--logging)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Environment Overview

### Deployment Environments

1. **Development**: Local development with hot reload
2. **Staging**: Production-like environment for testing
3. **Production**: Live production environment

### Infrastructure Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ recommended
- **Storage**: 20GB+ for application and logs
- **Database**: MySQL 5.5+ or MySQL 8.0+
- **Network**: HTTP/HTTPS access, database connectivity

## Local Development

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd fastapi-mysql-app

# Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Run application
python app.py
```

### Development Server Options

#### Option 1: Direct Python execution

```bash
python app.py
```

#### Option 2: Uvicorn with reload

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 3: With specific environment

```bash
uvicorn app.main:app --reload --env-file .env.development
```

## Docker Deployment

### Single Container Deployment

#### Build and Run

```bash
# Build image
docker build -t fastapi-erp:latest .

# Run container
docker run -d \
  --name fastapi-erp \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  fastapi-erp:latest
```

#### Environment Variables for Docker

```bash
# .env file for Docker
MYSQL_HOST=host.docker.internal  # Windows/Mac
# MYSQL_HOST=172.17.0.1          # Linux
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=wholesale
DEBUG=False
```

### Docker Compose Deployment

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  fastapi-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MYSQL_HOST=mysql
      - MYSQL_USER=root
      - MYSQL_PASSWORD=rootpassword
      - MYSQL_DATABASE=wholesale
      - DEBUG=False
    depends_on:
      - mysql
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=wholesale
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

volumes:
  mysql_data:
```

Deploy with Docker Compose:

```bash
docker-compose up -d
```

### Multi-Stage Docker Build

For optimized production images:

```dockerfile
# Dockerfile.prod
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.9-slim

RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

COPY --from=builder /root/.local /home/app/.local
COPY --chown=app:app . .

ENV PATH=/home/app/.local/bin:$PATH

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Production Deployment

### Server Setup (Ubuntu/Debian)

#### System Requirements

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx supervisor mysql-client

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### Application Deployment

```bash
# Create application user
sudo useradd -m -s /bin/bash fastapi
sudo su - fastapi

# Clone and setup application
git clone <repository-url> fastapi-erp
cd fastapi-erp

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Test application
python app.py
```

### Process Management with Supervisor

Create `/etc/supervisor/conf.d/fastapi-erp.conf`:

```ini
[program:fastapi-erp]
directory=/home/fastapi/fastapi-erp
command=/home/fastapi/fastapi-erp/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
user=fastapi
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/fastapi-erp.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
environment=PATH="/home/fastapi/fastapi-erp/venv/bin"
```

Manage service:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start fastapi-erp
sudo supervisorctl status
```

### Systemd Service (Alternative)

Create `/etc/systemd/system/fastapi-erp.service`:

```ini
[Unit]
Description=FastAPI ERP System
After=network.target

[Service]
Type=exec
User=fastapi
Group=fastapi
WorkingDirectory=/home/fastapi/fastapi-erp
Environment=PATH=/home/fastapi/fastapi-erp/venv/bin
EnvironmentFile=/home/fastapi/fastapi-erp/.env
ExecStart=/home/fastapi/fastapi-erp/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Manage service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi-erp
sudo systemctl start fastapi-erp
sudo systemctl status fastapi-erp
```

### Reverse Proxy with Nginx

Create `/etc/nginx/sites-available/fastapi-erp`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static/ {
        alias /home/fastapi/fastapi-erp/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

Enable and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/fastapi-erp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Load Balancing (Multiple Instances)

For high availability, run multiple application instances:

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    location / {
        proxy_pass http://fastapi_backend;
        # ... other proxy settings
    }
}
```

## Database Setup

### MySQL Configuration

#### Production MySQL Setup

```sql
-- Create database and user
CREATE DATABASE wholesale CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fastapi_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON wholesale.* TO 'fastapi_user'@'localhost';
FLUSH PRIVILEGES;

-- Optimize MySQL for FastAPI
SET GLOBAL max_connections = 1000;
SET GLOBAL innodb_buffer_pool_size = 2G;  -- Adjust based on available RAM
SET GLOBAL query_cache_size = 256M;
```

#### Connection Pool Configuration

Update `app/database_v2.py` for production:

```python
import mysql.connector.pooling

config = {
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
    'host': os.environ.get('MYSQL_HOST'),
    'database': os.environ.get('MYSQL_DATABASE'),
    'charset': 'utf8mb4',
    'pool_name': 'fastapi_pool',
    'pool_size': 20,  # Adjust based on expected load
    'pool_reset_session': True,
    'autocommit': False
}

cnx_pool = mysql.connector.pooling.MySQLConnectionPool(**config)
```

### Database Migrations

Create migration system:

```python
# scripts/migrate.py
import os
import glob
from app.database import get_db_connection

def run_migrations():
    """Run all pending migrations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create migrations table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Get executed migrations
    cursor.execute("SELECT filename FROM migrations")
    executed = {row[0] for row in cursor.fetchall()}

    # Run pending migrations
    migration_files = sorted(glob.glob("scripts/migrations/*.sql"))
    for file_path in migration_files:
        filename = os.path.basename(file_path)
        if filename not in executed:
            print(f"Running migration: {filename}")
            with open(file_path, 'r') as f:
                cursor.execute(f.read())
            cursor.execute(
                "INSERT INTO migrations (filename) VALUES (%s)",
                (filename,)
            )

    conn.commit()
    cursor.close()
    conn.close()
```

## Monitoring & Logging

### Application Logging

Configure structured logging:

```python
# app/config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/log/fastapi-erp/app.log'),
        logging.StreamHandler()
    ]
)

for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

### Health Check Endpoint

Add health check to `app/main.py`:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    try:
        # Test database connection
        from app.database import execute_query
        execute_query("SELECT 1")

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

### Monitoring with Prometheus (Optional)

Add metrics endpoint:

```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Security

### Environment Variables

Never commit sensitive data. Use environment variables:

```bash
# Production .env
MYSQL_HOST=production-db-host
MYSQL_USER=secure_user
MYSQL_PASSWORD=very_secure_password_here
MYSQL_DATABASE=wholesale
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
```

### Firewall Configuration

```bash
# UFW firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL/TLS Certificate

Using Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Database Security

```sql
-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Remove remote root login
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Remove test database
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';

-- Reload privileges
FLUSH PRIVILEGES;
```

## Troubleshooting

### Common Issues

#### Application Won't Start

1. **Check logs**:

```bash
sudo journalctl -u fastapi-erp -f
tail -f /var/log/fastapi-erp.log
```

2. **Verify environment**:

```bash
source venv/bin/activate
python -c "from app.main import app; print('App imported successfully')"
```

3. **Test database connection**:

```bash
python -c "from app.database import get_db_connection; get_db_connection().close(); print('DB connected')"
```

#### High Memory Usage

1. **Monitor processes**:

```bash
htop
ps aux | grep uvicorn
```

2. **Reduce worker count**:

```bash
# In supervisor config
command=uvicorn app.main:app --workers 2  # Reduce from 4
```

3. **Add memory limits**:

```bash
# In systemd service
[Service]
MemoryHigh=1G
MemoryMax=1.5G
```

#### Database Connection Issues

1. **Check connection pool**:

```python
# Add to health check
from app.database_v2 import cnx_pool
pool_info = {
    'pool_size': cnx_pool.pool_size,
    'connections_in_use': len(cnx_pool._cnx_queue._queue)
}
```

2. **Increase connection limits**:

```sql
-- MySQL
SET GLOBAL max_connections = 2000;
SHOW VARIABLES LIKE 'max_connections';
```

#### Performance Issues

1. **Enable query logging**:

```sql
-- MySQL slow query log
SET GLOBAL slow_query_log = 1;
SET GLOBAL long_query_time = 2;
```

2. **Monitor endpoint performance**:

```python
# Add timing middleware
import time

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Process-Time"] = str(duration)
    return response
```

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Process manager configured
- [ ] Reverse proxy configured
- [ ] Monitoring setup
- [ ] Log rotation configured
- [ ] Backup strategy implemented
- [ ] Health check endpoint working
- [ ] Load testing completed

This deployment guide covers the essential steps for getting your FastAPI ERP System running in production. Always test deployments in a staging environment first!
