# HTTP Method Decorators - Before & After Comparison

## Quick Reference

### Syntax Comparison

| Task | Before (Verbose) | After (Concise) |
|------|------------------|-----------------|
| GET endpoint | `@app.route("/users", methods=['GET'])` | `@app.get("/users")` |
| POST endpoint | `@app.route("/users", methods=['POST'])` | `@app.post("/users")` |
| PUT endpoint | `@app.route("/users", methods=['PUT'])` | `@app.put("/users")` |
| DELETE endpoint | `@app.route("/users", methods=['DELETE'])` | `@app.delete("/users")` |
| PATCH endpoint | `@app.route("/users", methods=['PATCH'])` | `@app.patch("/users")` |

### Real-World Example

#### Before (Old Syntax)
```python
from turbox import TurboX

app = TurboX()

@app.route("/users", methods=['GET'])
def list_users(request):
    return "User list"

@app.route("/users", methods=['POST'])
def create_user(request):
    return "User created"

@app.route("/users/<id>", methods=['GET'])
def get_user(request):
    return "User details"

@app.route("/users/<id>", methods=['PUT'])
def update_user(request):
    return "User updated"

@app.route("/users/<id>", methods=['DELETE'])
def delete_user(request):
    return "User deleted"
```

**Line count:** 24 lines  
**Readability:** 😐 Verbose, methods parameter repeated

#### After (New Syntax)
```python
from turbox import TurboX

app = TurboX()

@app.get("/users")
def list_users(request):
    return "User list"

@app.post("/users")
def create_user(request):
    return "User created"

@app.get("/users/<id>")
def get_user(request):
    return "User details"

@app.put("/users/<id>")
def update_user(request):
    return "User updated"

@app.delete("/users/<id>")
def delete_user(request):
    return "User deleted"
```

**Line count:** 24 lines (same)  
**Readability:** 😊 Clear, self-documenting  
**Characters saved:** ~70 characters less typing

## Feature Matrix

| Feature | Before | After |
|---------|--------|-------|
| `@app.route()` | ✅ | ✅ (still works) |
| `@app.get()` | ❌ | ✅ |
| `@app.post()` | ❌ | ✅ |
| `@app.put()` | ❌ | ✅ |
| `@app.delete()` | ❌ | ✅ |
| `@app.patch()` | ❌ | ✅ |
| `@app.head()` | ❌ | ✅ |
| `@app.options()` | ❌ | ✅ |
| Multiple methods | `methods=['GET','POST']` | `methods=['GET','POST']` |

## Framework Comparison

TurboX now matches the API of popular frameworks:

### FastAPI Style
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
@app.post("/users")
@app.put("/users/{id}")
@app.delete("/users/{id}")
```

### Flask Style
```python
from flask import Flask
app = Flask(__name__)

@app.route("/users", methods=['GET'])
@app.route("/users", methods=['POST'])
```

### TurboX (New)
```python
from turbox import TurboX
app = TurboX()

@app.get("/users")          # FastAPI style ✅
@app.post("/users")         # FastAPI style ✅
@app.route("/users", methods=['GET'])  # Flask style ✅
```

**TurboX supports BOTH patterns!** 🎉

## Use Case Examples

### RESTful API
```python
# GET /api/users - List all users
@app.get("/api/users")
def list_users(request):
    return "Alice, Bob, Charlie"

# POST /api/users - Create new user
@app.post("/api/users")
def create_user(request):
    return "User created"

# GET /api/users/<id> - Get specific user
@app.get("/api/users/<id>")
def get_user(request):
    return f"User {request.query_params.get('id')}"

# PUT /api/users/<id> - Update user
@app.put("/api/users/<id>")
def update_user(request):
    return "User updated"

# DELETE /api/users/<id> - Delete user
@app.delete("/api/users/<id>")
def delete_user(request):
    return "User deleted"
```

### CORS Support
```python
# Handle preflight requests
@app.options("/api/users")
def users_cors(request):
    return "CORS headers"

# HEAD request for metadata
@app.head("/api/health")
def health_check(request):
    return "OK"
```

### Partial Updates
```python
# PUT - full replacement
@app.put("/api/profile")
def update_profile(request):
    return "Profile replaced"

# PATCH - partial update
@app.patch("/api/profile")
def patch_profile(request):
    return "Profile updated partially"
```

## Migration Guide

### Step 1: Identify verbose routes
```python
# Old pattern - look for these
@app.route("/path", methods=['GET'])
@app.route("/path", methods=['POST'])
@app.route("/path", methods=['DELETE'])
```

### Step 2: Replace with HTTP method decorators
```python
# New pattern - replace with these
@app.get("/path")
@app.post("/path")
@app.delete("/path")
```

### Step 3: Keep multi-method routes as-is
```python
# If a route handles multiple methods, keep using @app.route()
@app.route("/api", methods=['POST', 'PUT', 'PATCH'])
def api_handler(request):
    return "Handles POST, PUT, and PATCH"
```

## Benefits Summary

✅ **Less typing** - Shorter decorator syntax  
✅ **Self-documenting** - HTTP method is obvious  
✅ **Familiar** - Matches FastAPI/Flask patterns  
✅ **Backward compatible** - Old code still works  
✅ **Prevents errors** - No forgetting `methods=[]` parameter  
✅ **Better tooling** - IDEs can better autocomplete  

## Testing

Run the comprehensive test suite:
```bash
python tests/build/test_route_extractor.py
```

Output:
```
✅ All 14 tests passed!
Problem #1 (Wrong app verification) is SOLVED! 🎉
Problem #2 (HTTP method decorators) is SOLVED! 🎉
```

## Try It Out

```bash
# Build the demo
python -m turbox.build examples/http_methods_demo.py

# Run the server
./examples/http_methods_demo

# Test with curl
curl http://localhost:8000/users          # GET
curl -X POST http://localhost:8000/users  # POST
curl -X PUT http://localhost:8000/users/1 # PUT
curl -X DELETE http://localhost:8000/users/1  # DELETE
```

---

**Problem #2:** ✅ SOLVED  
**Tests Added:** 6 new tests  
**Breaking Changes:** None  
**Performance Impact:** None
