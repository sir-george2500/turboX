# TurboX ⚡

A high-performance Python backend framework built on the Codon compiler.

## About

TurboX leverages Codon to compile Python code to machine code, delivering performance comparable to Rust and C++ without the overhead of traditional Python interpreters.

Built on **Nucleus** - a high-performance server core written in Codon with C FFI, TurboX combines Python's developer experience with native code performance.

### Vision & Goals

TurboX aims to be a **high-speed, flexible backend framework** with:

- ⚡ **Native Performance**: Compiled to machine code via Codon - no Python interpreter overhead
- 🤖 **First-class AI Tooling Support**: Built-in support for MCP (Model Context Protocol) servers and AI integrations
- 🔧 **Pythonic API**: Familiar Flask/FastAPI-like syntax that compiles to native code
- 🚀 **Parallel by Default**: Leverage Codon's threading and parallelism without GIL limitations
- 🎯 **Modern Web Standards**: Built for microservices, APIs, and high-performance backends

### Current State

**Advantages:**
- ✅ Compiles to native executables (no Python runtime needed)
- ✅ C-level socket performance via FFI
- ✅ Clean, Pythonic routing API
- ✅ Small binary size (~200KB for minimal server)
- ✅ Fast startup time compared to interpreted Python
- ✅ Full HTTP request parsing (query params, headers, body)
- ✅ JSON and form data parsing
- ✅ Request object with easy access to request data

**Current Limitations:**
- ⚠️ Early development - API may change
- ⚠️ Single-threaded request handling (concurrency coming soon)
- ⚠️ No middleware system yet
- ⚠️ Pure Python code in `turbox/` won't compile with Codon yet (uses Python's socket module)

**Coming Soon:**
- 🔄 Concurrent request handling with Codon's parallelism
- 🔄 MCP server integration for AI tooling
- 🔄 WebSocket support
- 🔄 Middleware system
- 🔄 Full Codon compilation of framework code

## Prerequisites

- [Codon compiler](https://github.com/exaloop/codon) installed and available in your PATH
- Linux/macOS (Windows support coming soon)

To check if Codon is installed:
```bash
codon --version
```

## Quick Start

### 1. Install TurboX

```bash
pip install -e .
```

### 2. Create Your First App

Create a file `app.py`:

```python
from turbox import TurboX

app = TurboX()

# Use modern HTTP method decorators
@app.get("/")
def hello(request):
    return "Hello, World!"

@app.get("/greet")
def greet(request):
    name = request.query_params.get('name', ['Guest'])[0]
    return f"Hello, {name}!"

@app.post("/echo")
def echo(request):
    return "POST request received"

if __name__ == "__main__":
    app.run()
```

### 3. Development Mode (Python)

For rapid development, run with Python:

```bash
python app.py
```

Test it:
```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/greet?name=Alice
```

### 4. Production Mode (Compiled with Codon)

For maximum performance, compile to native binary:

```bash
# Build to native executable
python -m turbox.build app.py

# Run the compiled binary
./app
```

The compiled binary:
- ✅ No Python runtime needed
- ✅ C-level performance
- ✅ Small binary size (~200KB)
- ✅ Fast startup time

### 5. Low-level: Running the Nucleus Server

The nucleus server demonstrates TurboX's core capabilities using Codon's C FFI for direct socket access.

**Compile the server:**
```bash
cd examples
codon build nucleus.codon
```

This creates a native executable (`nucleus`) with no Python runtime overhead.

**Run the server:**
```bash
./nucleus
```

You should see:
```
TurboX server running on http://127.0.0.1:8000
Press Ctrl+C to stop
```

**Test it:**
```bash
curl http://127.0.0.1:8000/
# Output: Hello, World!
```

### 6. Direct Execution (without pre-compilation)

You can also run the server directly:
```bash
codon run examples/nucleus.codon
```

## API Reference

### HTTP Method Decorators

TurboX supports modern, intuitive HTTP method decorators:

```python
from turbox import TurboX

app = TurboX()

# GET request
@app.get("/users")
def list_users(request):
    return "Users list"

# POST request
@app.post("/users")
def create_user(request):
    return "User created"

# PUT request
@app.put("/users/<id>")
def update_user(request):
    return "User updated"

# DELETE request
@app.delete("/users/<id>")
def delete_user(request):
    return "User deleted"

# PATCH request
@app.patch("/users/<id>")
def patch_user(request):
    return "User patched"

# Multiple methods (classic style)
@app.route("/api", methods=["POST", "PUT"])
def api_handler(request):
    return f"Method: {request.method}"
```

### Computed Routes (NEW!)

TurboX can resolve routes with constants:

```python
API_BASE = "/api"
VERSION = "v1"

@app.get(API_BASE + "/users")
def users(request):
    return "Users"

@app.get(f"{API_BASE}/{VERSION}/posts")
def posts(request):
    return "Posts"
```

### Request Object

Every route handler receives a `Request` object with the following attributes:

- `request.method` - HTTP method (GET, POST, etc.)
- `request.path` - Request path (without query string)
- `request.query_params` - Dict of query parameters (values are lists)
- `request.headers` - Dict of headers (lowercase keys)
- `request.body` - Raw request body as bytes
- `request.json()` - Parse JSON body
- `request.form()` - Parse form-encoded body

### Example Usage

```python
@app.get("/user")
def get_user(request):
    # Get query parameter
    user_id = request.query_params.get('id', [''])[0]
    
    # Check header
    auth = request.headers.get('authorization', '')
    
    return f"User ID: {user_id}, Auth: {auth}"

@app.post("/create")
def create_user(request):
    # Parse JSON
    data = request.json()
    name = data.get('name')
    email = data.get('email')
    
    return f"Created user: {name} ({email})"
```

## Project Status

TurboX is in active development. Currently implemented:

- ✅ Minimal HTTP server using C FFI
- ✅ Basic request/response handling
- ✅ Native compilation to machine code
- ✅ Routing system with decorators
- ✅ **HTTP method decorators** (`@app.get()`, `@app.post()`, etc.)
- ✅ **Computed routes** (constants, concatenation, f-strings)
- ✅ HTTP request parsing (methods, paths, headers, query params)
- ✅ JSON and form data parsing
- ✅ Request object API
- ✅ **Comprehensive validation** (catches errors before compilation)
- ✅ **35+ tests** - All passing!

Coming soon:
- 🔄 Concurrent request handling with Codon's parallelism
- 🔄 Middleware system
- 🔄 Path parameters (`/users/<int:id>`)
- 🔄 WebSocket support
- 🔄 Performance benchmarks
- 🔄 Full Codon compilation of framework code

## Documentation

- 📘 **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete tutorial
- 📗 **[Build System Architecture](docs/build-architecture.md)** - How it works
- 📕 **Examples in `examples/`** - Working code samples

## Testing

```bash
# Run all tests
python tests/run_tests.py

# Run specific test suite
python tests/build/test_route_extractor.py
python tests/build/test_computed_routes.py
python tests/test_app_runtime.py
```

**Test Coverage:** 35 tests across 5 test suites, all passing! ✅

## Development

This framework is in active development. Contributions and feedback welcome!
