# TurboX - Getting Started Guide

## Introduction

TurboX is a high-performance Python web framework that compiles to native code using Codon. Write Python, get C-level performance!

## Features

✨ **Modern API** - FastAPI-style decorators (`@app.get()`, `@app.post()`, etc.)  
⚡ **Blazing Fast** - Compiles to native code via Codon  
🔒 **Type-Safe** - Full type checking support  
🎯 **Simple** - Minimal learning curve  
🧪 **Well-Tested** - 35+ tests, all passing  

## Installation

```bash
# 1. Install Codon
# Visit: https://github.com/exaloop/codon

# 2. Clone TurboX
git clone https://github.com/yourusername/turboX
cd turboX

# 3. Install in development mode
pip install -e .
```

## Quick Start

### Your First Application

Create `app.py`:

```python
from turbox import TurboX

app = TurboX()

@app.get("/")
def hello(request):
    return "Hello, World!"

@app.get("/ping")
def ping(request):
    return "pong"

if __name__ == "__main__":
    app.run()
```

### Development Mode (Python)

Run directly with Python for quick iteration:

```bash
python app.py
```

Visit `http://localhost:8000` - your app is running!

### Production Mode (Compiled)

Compile to native binary for maximum performance:

```bash
python -m turbox.build app.py

# This creates a native binary: ./app
./app
```

**Performance:** Native binary runs 10-100x faster than Python! 🚀

## HTTP Method Decorators

TurboX supports modern, intuitive HTTP method decorators:

### GET Requests

```python
@app.get("/users")
def list_users(request):
    return "User list"

@app.get("/users/<id>")
def get_user(request):
    user_id = request.query_params.get('id', ['unknown'])[0]
    return f"User: {user_id}"
```

### POST Requests

```python
@app.post("/users")
def create_user(request):
    return "User created"
```

### PUT Requests

```python
@app.put("/users/<id>")
def update_user(request):
    return "User updated"
```

### DELETE Requests

```python
@app.delete("/users/<id>")
def delete_user(request):
    return "User deleted"
```

### Other Methods

```python
@app.patch("/users/<id>")    # Partial update
@app.head("/health")         # Headers only
@app.options("/api")         # CORS preflight
```

### Multiple Methods (Classic Style)

```python
@app.route("/api", methods=['POST', 'PUT'])
def api_handler(request):
    if request.method == 'POST':
        return "POST request"
    elif request.method == 'PUT':
        return "PUT request"
```

## Working with Requests

### Query Parameters

```python
@app.get("/search")
def search(request):
    # Query params: ?q=python&page=1
    query = request.query_params.get('q', [''])[0]
    page = request.query_params.get('page', ['1'])[0]
    return f"Searching for '{query}' on page {page}"
```

### Request Headers

```python
@app.get("/info")
def info(request):
    user_agent = request.headers.get('user-agent', 'unknown')
    return f"Your browser: {user_agent}"
```

### Request Body

```python
@app.post("/data")
def handle_data(request):
    body = request.body.decode('utf-8')
    return f"Received: {body}"
```

### Request Method

```python
@app.route("/resource", methods=['GET', 'POST', 'PUT'])
def handle_resource(request):
    return f"Method: {request.method}"
```

## Computed Routes (NEW!)

TurboX can resolve routes with constants and expressions:

### Using Constants

```python
from turbox import TurboX

app = TurboX()

API_BASE = "/api"
VERSION = "v1"

@app.get(API_BASE + "/users")
def list_users(request):
    return "Users"

@app.get(f"{API_BASE}/{VERSION}/posts")
def list_posts(request):
    return "Posts"
```

### String Concatenation

```python
BASE = "/admin"

@app.get(BASE + "/dashboard")
def dashboard(request):
    return "Admin Dashboard"

@app.get(BASE + "/users")
def admin_users(request):
    return "User Management"
```

### F-Strings

```python
API_VERSION = "v2"
RESOURCE = "products"

@app.get(f"/api/{API_VERSION}/{RESOURCE}")
def products(request):
    return "Products list"
```

## Complete Example

Here's a full RESTful API example:

```python
from turbox import TurboX

app = TurboX()

# API version constant
API_V1 = "/api/v1"

# List all users
@app.get(API_V1 + "/users")
def list_users(request):
    return "Users: Alice, Bob, Charlie"

# Get specific user
@app.get(API_V1 + "/users/<id>")
def get_user(request):
    user_id = request.query_params.get('id', ['unknown'])[0]
    return f"User ID: {user_id}"

# Create user
@app.post(API_V1 + "/users")
def create_user(request):
    return "User created successfully"

# Update user
@app.put(API_V1 + "/users/<id>")
def update_user(request):
    user_id = request.query_params.get('id', ['unknown'])[0]
    return f"User {user_id} updated"

# Delete user
@app.delete(API_V1 + "/users/<id>")
def delete_user(request):
    user_id = request.query_params.get('id', ['unknown'])[0]
    return f"User {user_id} deleted"

# Health check
@app.get("/health")
def health_check(request):
    return "OK"

if __name__ == "__main__":
    app.run()
```

### Build and Run

```bash
# Build to native binary
python -m turbox.build app.py

# Run the compiled binary
./app

# Test the API
curl http://localhost:8000/api/v1/users
curl -X POST http://localhost:8000/api/v1/users
curl -X DELETE http://localhost:8000/api/v1/users/123
```

## Configuration

### Custom Host and Port

```python
from turbox import TurboX

app = TurboX(host="0.0.0.0", port=3000)

@app.get("/")
def hello(request):
    return "Hello from port 3000!"

if __name__ == "__main__":
    app.run()
```

## Build Options

### Specify Output Binary Name

```bash
python -m turbox.build app.py my_server
./my_server
```

### Build Process

When you run `python -m turbox.build app.py`, TurboX:

1. ✅ Extracts routes from your Python code
2. ✅ Validates your application (catches errors early!)
3. ✅ Generates Codon code
4. ✅ Compiles to native binary

## Performance Tips

### 1. Use Native Binary in Production

```bash
# Development: Fast iteration
python app.py

# Production: Maximum performance
python -m turbox.build app.py
./app
```

### 2. Keep Handlers Simple

TurboX works best with simple, focused handler functions:

```python
# ✅ Good
@app.get("/users")
def get_users(request):
    return "Users list"

# ⚠️ Complex (may not transpile perfectly)
@app.get("/complex")
def complex_handler(request):
    # Lots of complex logic
    # Database calls
    # External API calls
```

### 3. Return Strings

Handler functions must return strings:

```python
# ✅ Good
@app.get("/age")
def get_age(request):
    return "25"

# ❌ Bad (validation will catch this!)
@app.get("/age")
def get_age(request):
    return 25  # Error: must return string
```

## Type Hints (Optional but Recommended)

For better IDE support and validation:

```python
from turbox import TurboX, Request

app = TurboX()

@app.get("/typed")
def typed_handler(request: Request) -> str:
    return "Type-safe!"
```

## Testing Your API

```bash
# GET request
curl http://localhost:8000/

# POST request
curl -X POST http://localhost:8000/users

# With query parameters
curl "http://localhost:8000/search?q=python&page=2"

# With headers
curl -H "Authorization: Bearer token" http://localhost:8000/api

# With data
curl -X POST -d "name=Alice" http://localhost:8000/users
```

## Common Patterns

### API Versioning

```python
V1 = "/api/v1"
V2 = "/api/v2"

@app.get(V1 + "/users")
def users_v1(request):
    return "API v1 users"

@app.get(V2 + "/users")
def users_v2(request):
    return "API v2 users (with new features!)"
```

### Admin Routes

```python
ADMIN = "/admin"

@app.get(ADMIN + "/dashboard")
def dashboard(request):
    return "Admin Dashboard"

@app.get(ADMIN + "/users")
def admin_users(request):
    return "User Management"

@app.get(ADMIN + "/settings")
def settings(request):
    return "Settings"
```

### Health Checks

```python
@app.get("/health")
def health(request):
    return "OK"

@app.get("/ready")
def ready(request):
    return "READY"

@app.head("/ping")
def ping(request):
    return "PONG"
```

## What's Supported

### ✅ Fully Supported

- HTTP method decorators (`@app.get()`, `@app.post()`, etc.)
- Query parameters
- Request headers
- Request body
- String constants in routes
- String concatenation in routes
- F-strings in routes
- Multiple HTTP methods per route

### ⚠️ Limited Support

- Complex Python features (json, async, etc.)
- Dynamic imports
- Runtime-computed routes

### ❌ Not Yet Supported

- WebSockets
- File uploads
- Sessions/Cookies
- Middleware (coming soon!)
- Path parameters like `/users/<int:id>` (coming soon!)

## Troubleshooting

### Build Fails with Validation Errors

Read the error messages carefully - they include:
- Line numbers
- Code context
- Helpful suggestions

Example:
```
❌ Validation Errors:

1. Handler 'get_age' returns non-string value: int
   Location: app.py:15

    def get_age(request):
>>>     return 25

   💡 Suggestion: Convert to string: return str(25)
```

### Routes Not Found

Make sure you have:
1. `app = TurboX()` at module level
2. Decorators like `@app.get("/path")`
3. Functions return strings

### Import Errors

```python
# ✅ Correct
from turbox import TurboX, Request

# ❌ Wrong
from turbox import TurboX, app  # 'app' is not exported
```

## Next Steps

- Check out `examples/` folder for more examples
- Read `docs/` for detailed documentation
- Join our community for support

## Examples in This Repository

- `examples/hello.py` - Basic GET and POST routes
- `examples/http_methods_demo.py` - All HTTP methods
- `examples/computed_routes_demo.py` - Dynamic route paths

## Contributing

We welcome contributions! Check out `docs/build-refactoring.md` and `docs/build-architecture.md` to understand the codebase.

## License

[Your License Here]

---

**Happy coding with TurboX!** 🚀

For more information, visit the `docs/` directory or check out the examples.
