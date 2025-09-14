# FastAPI ERP System - Code Examples

This directory contains practical examples for integrating with and extending the FastAPI ERP System.

## Available Examples

### Authentication Examples

- [`login_example.py`](./login_example.py) - User authentication workflow
- [`session_management.py`](./session_management.py) - Managing user sessions

### API Integration Examples

- [`client_sdk.py`](./client_sdk.py) - Python SDK for API integration
- [`javascript_client.js`](./javascript_client.js) - JavaScript client example
- [`curl_examples.sh`](./curl_examples.sh) - cURL command examples

### Custom Middleware Examples

- [`custom_middleware.py`](./custom_middleware.py) - Creating custom middleware
- [`rate_limiting.py`](./rate_limiting.py) - Rate limiting implementation
- [`request_logging.py`](./request_logging.py) - Request/response logging

### Testing Examples

- [`test_patterns.py`](./test_patterns.py) - Common testing patterns
- [`mock_examples.py`](./mock_examples.py) - Mocking database and external services

### Deployment Examples

- [`docker_examples/`](./docker_examples/) - Docker deployment configurations
- [`kubernetes_examples/`](./kubernetes_examples/) - Kubernetes manifests
- [`nginx_configs/`](./nginx_configs/) - Nginx configuration examples

## Quick Start

Each example includes:

- Complete, runnable code
- Detailed comments explaining the implementation
- Prerequisites and setup instructions
- Common use cases and variations

## Running Examples

1. **Setup environment**:

```bash
cd fastapi-mysql-app
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

2. **Install additional dependencies if needed**:

```bash
pip install -r docs/examples/requirements.txt
```

3. **Run specific example**:

```bash
python docs/examples/login_example.py
```

## Contributing Examples

To add new examples:

1. Create a new file in the appropriate category
2. Include comprehensive documentation
3. Add any new dependencies to `requirements.txt`
4. Update this README with a link to your example
5. Test the example thoroughly

## Support

For questions about these examples:

- Check the main documentation in the `docs/` directory
- Review the API documentation at `/docs` when running the server
- Create an issue in the project repository
