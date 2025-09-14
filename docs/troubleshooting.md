# Troubleshooting Guide

This guide helps resolve common issues when working with the FastAPI ERP System.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Database Connection Problems](#database-connection-problems)
- [Authentication Issues](#authentication-issues)
- [API Performance Problems](#api-performance-problems)
- [Docker Issues](#docker-issues)
- [Production Problems](#production-problems)
- [Development Environment Issues](#development-environment-issues)

## Installation Issues

### Python Version Compatibility

**Problem**: ImportError or syntax errors during startup

**Solution**:

```bash
# Check Python version
python --version

# Ensure Python 3.7+
python3.9 -m venv venv  # Use specific version
```

**Common Error**:

```
SyntaxError: invalid syntax (fastapi features require Python 3.7+)
```

### Dependency Installation Failures

**Problem**: pip install fails for some packages

**Solution**:

```bash
# Update pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# For Windows compilation issues
pip install --upgrade setuptools wheel

# Alternative: use conda
conda install -c conda-forge fastapi uvicorn mysql-connector-python
```

**Common Error**:

```
error: Microsoft Visual C++ 14.0 is required
```

**Windows Solution**:

- Install Visual Studio Build Tools
- Or use pre-compiled wheels: `pip install --only-binary=all package_name`

### Virtual Environment Issues

**Problem**: Command not found or wrong Python version in venv

**Solution**:

```bash
# Remove and recreate virtual environment
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Verify correct Python
which python
python --version
```

## Database Connection Problems

### Connection Refused

**Problem**: `mysql.connector.errors.InterfaceError: 2003: Can't connect to MySQL server`

**Diagnosis**:

```bash
# Test MySQL service
mysql -h localhost -u root -p

# Check if MySQL is running
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # Mac
services.msc  # Windows (look for MySQL)

# Test network connectivity
telnet localhost 3306
nc -zv localhost 3306
```

**Solutions**:

1. **Start MySQL service**:

```bash
sudo systemctl start mysql  # Linux
brew services start mysql  # Mac
net start MySQL80  # Windows
```

2. **Check MySQL configuration**:

```bash
# Check bind-address in MySQL config
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Ensure: bind-address = 0.0.0.0
```

3. **Verify firewall**:

```bash
sudo ufw allow 3306  # Linux
```

### Authentication Failed

**Problem**: `mysql.connector.errors.ProgrammingError: 1045: Access denied for user`

**Solutions**:

1. **Reset MySQL root password**:

```sql
-- Connect as root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

2. **Create application user**:

```sql
CREATE USER 'fastapi_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON wholesale.* TO 'fastapi_user'@'localhost';
FLUSH PRIVILEGES;
```

3. **Check environment variables**:

```bash
# Verify .env file
cat .env
echo $MYSQL_PASSWORD  # Linux/Mac
echo %MYSQL_PASSWORD%  # Windows
```

### Database Does Not Exist

**Problem**: `mysql.connector.errors.ProgrammingError: 1049: Unknown database 'wholesale'`

**Solution**:

```sql
-- Connect to MySQL and create database
mysql -u root -p
CREATE DATABASE wholesale CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
```

### Connection Pool Exhaustion

**Problem**: Application becomes unresponsive under load

**Symptoms**:

- Slow response times
- Connection timeout errors
- High memory usage

**Solutions**:

1. **Increase pool size**:

```python
# app/database_v2.py
config = {
    'pool_size': 50,  # Increase from default
    'pool_reset_session': True,
    'pool_name': 'fastapi_pool'
}
```

2. **Monitor connections**:

```sql
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Connections';
SHOW STATUS LIKE 'Threads_connected';
```

3. **Implement connection recycling**:

```python
# Add connection timeout
config = {
    'pool_size': 20,
    'connection_timeout': 10,
    'autocommit': False
}
```

## Authentication Issues

### MD5 Password Mismatch

**Problem**: Login fails with correct credentials

**Diagnosis**:

```python
# Test password hashing
import hashlib

password = "your_password"
md5_hash = hashlib.md5(password.encode()).hexdigest()
print(f"MD5 hash: {md5_hash}")

# Check database
SELECT username, password FROM users WHERE username = 'test_user';
```

**Solutions**:

1. **Verify hash format**:

```python
# app/auth.py - ensure correct MD5 implementation
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.md5(plain_password.encode()).hexdigest() == hashed_password
```

2. **Check database schema**:

```sql
DESCRIBE users;
-- Ensure password column exists and is VARCHAR(32) for MD5
```

### Session Management

**Problem**: User authentication doesn't persist

**Solution** (if implementing sessions):

```python
# Add session middleware
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here"
)
```

## API Performance Problems

### Slow Query Performance

**Problem**: API endpoints respond slowly

**Diagnosis**:

1. **Enable slow query log**:

```sql
SET GLOBAL slow_query_log = 1;
SET GLOBAL long_query_time = 2;
SET GLOBAL log_queries_not_using_indexes = 1;
```

2. **Monitor queries**:

```bash
tail -f /var/log/mysql/mysql-slow.log
```

3. **Profile specific queries**:

```sql
EXPLAIN SELECT * FROM sales WHERE date BETWEEN '2024-01-01' AND '2024-12-31';
```

**Solutions**:

1. **Add database indexes**:

```sql
-- Common indexes for reporting
CREATE INDEX idx_sales_date ON sales(date);
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_inventory_category ON inventory(category);
```

2. **Optimize queries**:

```python
# Use LIMIT for large datasets
def get_sales_data(limit: int = 1000):
    query = """
    SELECT * FROM sales
    ORDER BY date DESC
    LIMIT %s
    """
    return execute_query(query, (limit,))
```

3. **Implement caching**:

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_cached_report(report_type: str, date_key: str):
    # Cache reports for 5 minutes
    return generate_report(report_type, date_key)
```

### Memory Usage Issues

**Problem**: Application consumes too much memory

**Diagnosis**:

```bash
# Monitor memory usage
ps aux | grep uvicorn
top -p $(pgrep uvicorn)

# Python memory profiling
pip install memory-profiler
python -m memory_profiler app.py
```

**Solutions**:

1. **Limit query results**:

```python
def get_large_dataset(page: int = 1, page_size: int = 100):
    offset = (page - 1) * page_size
    query = "SELECT * FROM large_table LIMIT %s OFFSET %s"
    return execute_query(query, (page_size, offset))
```

2. **Use generators for large datasets**:

```python
def stream_results(query: str, params=None):
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        while True:
            rows = cursor.fetchmany(1000)
            if not rows:
                break
            yield from rows
```

3. **Reduce worker count**:

```bash
# If running multiple workers
uvicorn app.main:app --workers 2  # Reduce from 4
```

### High CPU Usage

**Problem**: CPU usage consistently high

**Solutions**:

1. **Profile code**:

```python
import cProfile
import pstats

def profile_function(func):
    pr = cProfile.Profile()
    pr.enable()
    result = func()
    pr.disable()

    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    return result
```

2. **Optimize hot paths**:

```python
# Use list comprehensions instead of loops
# Cache expensive calculations
# Avoid N+1 query problems
```

## Docker Issues

### Container Won't Start

**Problem**: Docker container exits immediately

**Diagnosis**:

```bash
# Check container logs
docker logs container_name

# Run interactively to debug
docker run -it --entrypoint /bin/bash your_image

# Check image layers
docker history your_image
```

**Common Issues**:

1. **Missing dependencies**:

```dockerfile
# Ensure all dependencies in Dockerfile
RUN pip install -r requirements.txt
```

2. **Permission issues**:

```dockerfile
# Create non-root user
RUN useradd -m -s /bin/bash appuser
USER appuser
```

3. **Environment variables**:

```bash
# Check if .env is properly loaded
docker run --env-file .env your_image env
```

### Database Connection in Docker

**Problem**: App can't connect to host MySQL from container

**Solutions**:

1. **Use correct host**:

```bash
# .env for Docker
MYSQL_HOST=host.docker.internal  # Windows/Mac
MYSQL_HOST=172.17.0.1           # Linux
```

2. **Use Docker Compose**:

```yaml
version: "3.8"
services:
  app:
    build: .
    depends_on:
      - mysql
    environment:
      - MYSQL_HOST=mysql # Service name

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
```

3. **Check network connectivity**:

```bash
# Test from inside container
docker exec -it container_name ping mysql_host
docker exec -it container_name telnet mysql_host 3306
```

## Production Problems

### High Load Issues

**Problem**: Application becomes unresponsive under load

**Diagnosis**:

```bash
# Monitor system resources
htop
iostat -x 1
netstat -tuln

# Check application metrics
curl http://localhost:8000/health
```

**Solutions**:

1. **Scale horizontally**:

```bash
# Run multiple instances
uvicorn app.main:app --port 8000 --workers 4
uvicorn app.main:app --port 8001 --workers 4
```

2. **Implement load balancing**:

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

3. **Add caching**:

```python
# Redis caching
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key: str):
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return None
```

### SSL/TLS Issues

**Problem**: HTTPS not working or certificate errors

**Solutions**:

1. **Check certificate**:

```bash
openssl x509 -in certificate.crt -text -noout
openssl s_client -connect your-domain.com:443
```

2. **Verify Nginx config**:

```bash
sudo nginx -t
sudo nginx -s reload
```

3. **Renew Let's Encrypt**:

```bash
sudo certbot renew --dry-run
sudo certbot renew
```

### Log Management

**Problem**: Log files growing too large

**Solutions**:

1. **Configure log rotation**:

```bash
# /etc/logrotate.d/fastapi-erp
/var/log/fastapi-erp/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 fastapi fastapi
    postrotate
        systemctl reload fastapi-erp
    endscript
}
```

2. **Structured logging**:

```python
import structlog

logger = structlog.get_logger()
logger.info("User login", user_id=123, ip_address="192.168.1.1")
```

## Development Environment Issues

### Import Errors

**Problem**: ModuleNotFoundError when running application

**Solutions**:

1. **Check PYTHONPATH**:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"
```

2. **Install in development mode**:

```bash
pip install -e .
```

3. **Use relative imports correctly**:

```python
# In app/routers/auth.py
from ..services.auth_service import AuthService  # Correct
from app.services.auth_service import AuthService  # Also correct
```

### Hot Reload Not Working

**Problem**: Changes not reflected when using --reload

**Solutions**:

1. **Check file extensions**:

```bash
uvicorn app.main:app --reload --reload-include="*.py"
```

2. **Verify file watching**:

```bash
# Use watchdog explicitly
pip install watchdog
uvicorn app.main:app --reload
```

3. **Check file permissions**:

```bash
chmod 644 app/*.py
```

### Environment Variable Issues

**Problem**: Environment variables not loading

**Solutions**:

1. **Load .env explicitly**:

```python
from dotenv import load_dotenv
load_dotenv()
```

2. **Check .env location**:

```bash
# .env should be in project root
ls -la .env
```

3. **Verify syntax**:

```bash
# No spaces around =
MYSQL_HOST=localhost  # Correct
MYSQL_HOST = localhost  # Wrong
```

## Getting Help

### Debug Information to Collect

When reporting issues, include:

1. **System information**:

```bash
python --version
pip list
uname -a  # Linux/Mac
systeminfo  # Windows
```

2. **Application logs**:

```bash
tail -n 100 /var/log/fastapi-erp.log
```

3. **Database information**:

```sql
SELECT VERSION();
SHOW VARIABLES LIKE 'version%';
```

4. **Configuration**:

```bash
# Sanitized .env (remove sensitive data)
cat .env | sed 's/PASSWORD=.*/PASSWORD=***/'
```

### Common Log Patterns

**Database Errors**:

```
ERROR - mysql.connector.errors.OperationalError: (2003, "Can't connect to MySQL")
```

**Authentication Errors**:

```
ERROR - Authentication failed for user 'username'
```

**Performance Issues**:

```
WARNING - Request took 5.23 seconds: GET /api/v1/reports/sales
```

### Useful Commands

```bash
# System monitoring
htop
netstat -tuln | grep :8000
lsof -i :8000

# Application debugging
python -c "from app.main import app; print('App loaded')"
curl -v http://localhost:8000/health

# Database debugging
mysql -u root -p -e "SHOW PROCESSLIST;"
mysql -u root -p -e "SHOW STATUS LIKE 'Connections';"
```

This troubleshooting guide covers the most common issues. For specific problems not covered here, check the application logs and consider the diagnostic steps provided for each category.
