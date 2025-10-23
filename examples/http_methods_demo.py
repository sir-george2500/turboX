"""
Example demonstrating HTTP method decorators

Shows the new @app.get(), @app.post(), etc. decorators (Problem #2 fix)
"""
from turbox import TurboX

app = TurboX()

# GET request - list all users
@app.get("/users")
def list_users(request):
    return "User list: Alice, Bob, Charlie"

# POST request - create a new user
@app.post("/users")
def create_user(request):
    return "User created successfully"

# GET request - get specific user
@app.get("/users/<id>")
def get_user(request):
    user_id = request.query_params.get('id', 'unknown')
    return f"User details for ID: {user_id}"

# PUT request - update user
@app.put("/users/<id>")
def update_user(request):
    return "User updated"

# DELETE request - delete user
@app.delete("/users/<id>")
def delete_user(request):
    return "User deleted"

# PATCH request - partial update
@app.patch("/users/<id>")
def patch_user(request):
    return "User partially updated"

# Still supports @app.route() with methods parameter
@app.route("/api/bulk", methods=['POST', 'PUT'])
def bulk_operation(request):
    return "Bulk operation completed"

# HEAD and OPTIONS for CORS/preflight
@app.options("/users")
def users_options(request):
    return "OPTIONS response"

@app.head("/health")
def health_check(request):
    return "OK"

if __name__ == "__main__":
    app.run()
