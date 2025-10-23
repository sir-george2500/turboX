# Problem #2 Fix: HTTP Method Decorators Support

## Problem Statement
The original `RouteExtractor` only recognized `@app.route()` decorator, forcing developers to use verbose syntax:

```python
@app.route("/users", methods=['GET'])
def get_users(request):
    return "Users"

@app.route("/users", methods=['POST'])
def create_user(request):
    return "Created"
```

This was **less intuitive** compared to popular frameworks like FastAPI and Flask.

## Solution Implemented

Added support for HTTP method-specific decorators: `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`, `@app.patch()`, `@app.head()`, `@app.options()`

### Before (Still Works)
```python
@app.route("/users", methods=['GET'])
def get_users(request):
    return "Users"

@app.route("/users", methods=['POST'])
def create_user(request):
    return "Created"
```

### After (New & Better!)
```python
@app.get("/users")
def get_users(request):
    return "Users"

@app.post("/users")
def create_user(request):
    return "Created"
```

## Implementation Details

### 1. Added Supported Decorators List

**File:** `turbox/build/extractor.py`

```python
# Supported HTTP method decorators
SUPPORTED_DECORATORS = ['route', 'get', 'post', 'put', 'delete', 'patch', 'head', 'options']
```

### 2. Extended Decorator Check

**Before:**
```python
if decorator.func.attr == 'route':
    # Only matches @app.route()
```

**After:**
```python
if decorator.func.attr in SUPPORTED_DECORATORS:
    # Matches all HTTP method decorators
```

### 3. Method Inference Logic

```python
decorator_name = decorator.func.attr

if decorator_name == 'route':
    # For @app.route(), check methods keyword argument
    methods = ['GET']  # default
    for keyword in decorator.keywords:
        if keyword.arg == 'methods':
            methods = extract_methods(keyword)
else:
    # For @app.get(), @app.post(), etc.
    # Infer HTTP method from decorator name
    methods = [decorator_name.upper()]  # 'get' -> 'GET'
```

### 4. Same Validation Rules Apply

All HTTP method decorators follow the same validation:
- Must be from the TurboX instance (not other frameworks)
- Cannot be nested (e.g., `@app.router.get()` is rejected)
- Must match the tracked app variable name

## Supported HTTP Methods

| Decorator | HTTP Method | Use Case |
|-----------|-------------|----------|
| `@app.get()` | GET | Retrieve resources |
| `@app.post()` | POST | Create resources |
| `@app.put()` | PUT | Update/replace resources |
| `@app.delete()` | DELETE | Delete resources |
| `@app.patch()` | PATCH | Partial update |
| `@app.head()` | HEAD | Get headers only |
| `@app.options()` | OPTIONS | CORS preflight |
| `@app.route()` | Multiple | Multiple methods via `methods=[]` |

## Example Usage

See `examples/http_methods_demo.py`:

```python
from turbox import TurboX

app = TurboX()

@app.get("/users")
def list_users(request):
    return "User list"

@app.post("/users")
def create_user(request):
    return "User created"

@app.put("/users/<id>")
def update_user(request):
    return "User updated"

@app.delete("/users/<id>")
def delete_user(request):
    return "User deleted"

@app.patch("/users/<id>")
def patch_user(request):
    return "User patched"

# Still supports @app.route() for multiple methods
@app.route("/api", methods=['POST', 'PUT'])
def api_handler(request):
    return "API response"
```

## Test Coverage

Added 6 comprehensive tests in `tests/build/test_route_extractor.py`:

✅ **test_get_decorator** - Basic GET decorator  
✅ **test_post_decorator** - Basic POST decorator  
✅ **test_put_delete_patch_decorators** - PUT, DELETE, PATCH  
✅ **test_mixed_decorators** - Mix of all decorator types  
✅ **test_all_http_methods** - All 7 HTTP method decorators  
✅ **test_wrong_app_with_http_methods** - Validation still works

**Total tests:** 14 (was 8) - All passing! ✅

## Backward Compatibility

✅ **Fully backward compatible**
- `@app.route()` still works exactly as before
- `@app.route("/path", methods=['GET', 'POST'])` still works
- No breaking changes to existing code

## Benefits

### 1. **Better Developer Experience**
```python
# Old way (verbose)
@app.route("/users", methods=['GET'])

# New way (concise)
@app.get("/users")
```

### 2. **Familiar Pattern**
Matches FastAPI, Flask, and other popular frameworks:
```python
# FastAPI style
@app.get("/users")

# Flask style  
@app.route("/users", methods=['GET'])

# TurboX now supports BOTH!
```

### 3. **Self-Documenting Code**
```python
@app.get("/users")      # Clear: this is a GET endpoint
@app.post("/users")     # Clear: this creates resources
@app.delete("/users")   # Clear: this deletes resources
```

### 4. **Prevents Mistakes**
```python
# Before: easy to forget methods parameter
@app.route("/users")  # Defaults to GET, might not be what you want

# After: explicit and clear
@app.post("/users")   # Obviously a POST endpoint
```

## Edge Cases Handled

### Multiple Decorators on Same Path
```python
@app.get("/users")
def list_users(request):
    return "List"

@app.post("/users")  # Different handler, same path
def create_user(request):
    return "Create"
```
✅ Both routes are correctly extracted

### Mixed with @app.route()
```python
@app.get("/simple")
def simple(request):
    return "GET"

@app.route("/complex", methods=['POST', 'PUT'])
def complex(request):
    return "POST or PUT"
```
✅ Both work together seamlessly

### Wrong App Instance
```python
other_app = OtherFramework()

@other_app.get("/users")  # Not TurboX
def handler(request):
    return "Not extracted"
```
✅ Correctly ignored (not extracted)

## Files Modified

1. **turbox/build/extractor.py**
   - Added `SUPPORTED_DECORATORS` constant
   - Extended decorator check logic
   - Added method inference from decorator name

2. **tests/build/test_route_extractor.py**
   - Added 6 new test cases
   - Increased test count from 8 to 14
   - All tests passing

3. **examples/http_methods_demo.py** (new)
   - Demonstrates all HTTP method decorators
   - Practical usage examples

4. **BRIDGE_CRITIQUE.md**
   - Marked "Support @app.get(), @app.post(), etc." as complete

## Performance Impact

**None** - The change is purely syntactic. The generated Codon code is identical whether you use:
```python
@app.route("/users", methods=['GET'])
# or
@app.get("/users")
```

Both produce the same route registration in the compiled binary.

## What's Next

From BRIDGE_CRITIQUE.md Problem #4, remaining work:
- [ ] Validate decorator arguments properly
- [ ] Error on unsupported patterns (computed routes, etc.)

---

**Status:** COMPLETE ✅  
**Tests:** 14/14 passing (6 new tests added)  
**Backward Compatible:** Yes ✅  
**Date:** 2025-10-23
