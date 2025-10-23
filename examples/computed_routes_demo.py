"""
Example demonstrating computed/dynamic routes support

Shows that TurboX can now handle:
- String constants
- String concatenation
- F-strings with constants
- Module-level constants
"""
from turbox import TurboX

app = TurboX()

# Define some constants for paths
API_BASE = "/api"
VERSION = "v1"
ADMIN_PREFIX = "/admin"

# Simple constant path (always worked)
@app.get("/")
def index(request):
    return "Welcome to TurboX"

# String concatenation - NEW!
@app.get(API_BASE + "/users")
def list_users(request):
    return "Users list"

@app.post(API_BASE + "/users")
def create_user(request):
    return "User created"

# F-string with constants - NEW!
@app.get(f"/{API_BASE.strip('/')}/{VERSION}/posts")
def list_posts(request):
    return "Posts list (API v1)"

# Multiple concatenations - NEW!
@app.get(API_BASE + "/" + VERSION + "/comments")
def list_comments(request):
    return "Comments list"

# Complex f-string - NEW!
RESOURCE = "products"
@app.get(f"{API_BASE}/{VERSION}/{RESOURCE}")
def list_products(request):
    return "Products list"

# Admin routes with prefix
@app.get(ADMIN_PREFIX + "/dashboard")
def admin_dashboard(request):
    return "Admin Dashboard"

@app.get(ADMIN_PREFIX + "/users")
def admin_users(request):
    return "Admin Users Management"

# Mixed approaches
HEALTH_PATH = "/health"
@app.get(HEALTH_PATH)
def health_check(request):
    return "OK"

@app.get(API_BASE + HEALTH_PATH)  # Concatenation of two constants
def api_health(request):
    return "API OK"

if __name__ == "__main__":
    print("Routes that will be compiled:")
    print("  GET /")
    print("  GET /api/users")
    print("  POST /api/users")
    print("  GET /api/v1/posts")
    print("  GET /api/v1/comments")
    print("  GET /api/v1/products")
    print("  GET /admin/dashboard")
    print("  GET /admin/users")
    print("  GET /health")
    print("  GET /api/health")
    print("\nAll paths resolved at build time! ✨")
    
    app.run()
