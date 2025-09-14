# Exposing FastAPI with zrok - Setup Guide

This guide shows how to expose your FastAPI ERP System using zrok and avoid CORS errors.

## What is zrok?

zrok is a secure tunneling service that allows you to share your locally running application with the internet securely. It's similar to ngrok but with enhanced security features.

## Prerequisites

1. **Install zrok**:

   ```bash
   # Download from https://github.com/openziti/zrok/releases
   # Or use package manager (if available)

   # Windows (using PowerShell)
   Invoke-WebRequest -Uri "https://github.com/openziti/zrok/releases/latest/download/zrok_windows_amd64.zip" -OutFile "zrok.zip"
   Expand-Archive zrok.zip

   # Linux/Mac
   curl -sSLo zrok.tar.gz https://github.com/openziti/zrok/releases/latest/download/zrok_linux_amd64.tar.gz
   tar -xzf zrok.tar.gz
   ```

2. **Create zrok account**:

   ```bash
   zrok invite
   # Follow the instructions to create an account
   ```

3. **Enable zrok**:
   ```bash
   zrok enable <your-token>
   ```

## FastAPI CORS Configuration for zrok

Your current CORS configuration is already compatible with zrok:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows zrok domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

However, for production, you might want to be more specific:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Your frontend
        "https://*.zrok.io",      # zrok domains
        "https://*.share.zrok.io" # zrok share domains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Exposing Your FastAPI Application

### Method 1: Basic HTTP Share

1. **Start your FastAPI application**:

   ```bash
   cd fastapi-mysql-app
   python app.py
   # Your app runs on http://localhost:5000
   ```

2. **In another terminal, expose with zrok**:

   ```bash
   zrok share public http://localhost:5000
   ```

3. **zrok will provide a URL like**:
   ```
   https://abc123.share.zrok.io
   ```

### Method 2: Reserved Share (Consistent URL)

1. **Reserve a share**:

   ```bash
   zrok reserve public --backend-mode proxy fastapi-erp-api
   ```

2. **Start the reserved share**:
   ```bash
   zrok share reserved fastapi-erp-api --backend-mode proxy --target http://localhost:5000
   ```

### Method 3: Private Share (More Secure)

1. **Create private share**:

   ```bash
   zrok share private --backend-mode proxy http://localhost:5000
   ```

2. **Access from another machine**:
   ```bash
   zrok access private <share-token>
   # This creates a local proxy to access the private share
   ```

## Testing with zrok

### Using cURL

```bash
# Replace with your actual zrok URL
ZROK_URL="https://abc123.share.zrok.io"

# Test health endpoint
curl -X GET "${ZROK_URL}/health"

# Test authentication
curl -X POST "${ZROK_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Test sales report
curl -X POST "${ZROK_URL}/api/reports/sales" \
  -H "Content-Type: application/json" \
  -d '{"category": "today_hourly"}'
```

### Using Browser

1. **Access Swagger UI**:

   ```
   https://your-zrok-url.share.zrok.io/docs
   ```

2. **Access ReDoc**:
   ```
   https://your-zrok-url.share.zrok.io/redoc
   ```

## Common CORS Issues and Solutions

### Issue 1: CORS Error Despite Wildcard Origins

**Problem**: Browser blocks requests even with `allow_origins=["*"]`

**Solution**: Update CORS configuration:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Add this line
)
```

### Issue 2: Preflight Requests Failing

**Problem**: OPTIONS requests failing

**Solution**: Ensure OPTIONS method is explicitly allowed:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add explicit OPTIONS handler if needed
@app.options("/{full_path:path}")
async def options_handler():
    return {}
```

### Issue 3: Credentials with Wildcard Origins

**Problem**: Cannot use credentials with wildcard origins in modern browsers

**Solution**: Specify explicit origins:

```python
import os

# Get zrok URL from environment or config
ZROK_DOMAIN = os.environ.get("ZROK_DOMAIN", "")

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

if ZROK_DOMAIN:
    allowed_origins.append(f"https://{ZROK_DOMAIN}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Production Considerations

### 1. Environment-Specific CORS

Create different CORS configurations for different environments:

```python
import os

def get_cors_origins():
    env = os.environ.get("ENVIRONMENT", "development")

    if env == "development":
        return ["*"]
    elif env == "staging":
        return [
            "https://staging-frontend.yourdomain.com",
            "https://*.share.zrok.io"
        ]
    else:  # production
        return [
            "https://yourdomain.com",
            "https://api.yourdomain.com"
        ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2. Security Headers

Add security headers when using zrok:

```python
from fastapi import FastAPI, Request, Response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # For zrok, you might want to allow iframe embedding
    if request.headers.get("host", "").endswith(".zrok.io"):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

    return response
```

## Automation Scripts

### PowerShell Script (Windows)

```powershell
# start-zrok.ps1
param(
    [string]$Port = "5000",
    [string]$ShareName = "fastapi-erp"
)

Write-Host "Starting FastAPI application..." -ForegroundColor Green
Start-Process python -ArgumentList "app.py" -WindowStyle Hidden

Start-Sleep -Seconds 3

Write-Host "Starting zrok share..." -ForegroundColor Green
zrok share public http://localhost:$Port --name $ShareName
```

### Bash Script (Linux/Mac)

```bash
#!/bin/bash
# start-zrok.sh

PORT=${1:-5000}
SHARE_NAME=${2:-fastapi-erp}

echo "Starting FastAPI application..."
python app.py &
FASTAPI_PID=$!

sleep 3

echo "Starting zrok share..."
zrok share public http://localhost:$PORT --name $SHARE_NAME

# Cleanup on exit
trap "kill $FASTAPI_PID" EXIT
```

## Monitoring and Logging

### Monitor zrok Status

```bash
# Check zrok status
zrok status

# List active shares
zrok ls

# Monitor share metrics (if available)
zrok metrics
```

### Application Logging

Add middleware to log zrok requests:

```python
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log zrok requests
    host = request.headers.get("host", "")
    if ".zrok.io" in host:
        logger.info(f"zrok request: {request.method} {request.url}")

    response = await call_next(request)
    return response
```

## Best Practices

1. **Use Reserved Shares**: For consistent URLs across sessions
2. **Monitor Usage**: Keep track of zrok usage and limits
3. **Secure Endpoints**: Don't expose sensitive endpoints unnecessarily
4. **Environment Variables**: Store zrok tokens and URLs in environment variables
5. **Health Checks**: Ensure your application has health check endpoints
6. **Logging**: Log all requests coming through zrok for monitoring

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure your FastAPI app is running on the correct port
2. **CORS Errors**: Check browser developer tools for specific CORS issues
3. **zrok Not Found**: Ensure zrok is installed and in your PATH
4. **Token Issues**: Re-enable zrok if you get authentication errors

### Debug Commands

```bash
# Test local application
curl http://localhost:5000/health

# Test zrok connectivity
curl https://your-zrok-url/health

# Check zrok logs
zrok logs

# Verbose zrok output
zrok share public http://localhost:5000 --verbose
```

This setup will allow you to expose your FastAPI application through zrok without CORS issues!
