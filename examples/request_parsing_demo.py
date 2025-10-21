from turbox import TurboX

app = TurboX()

@app.route("/")
def index(request):
    return "TurboX Request Parsing Demo"

@app.route("/query")
def query_params(request):
    # Access query parameters - returns dict with lists as values
    name = request.query_params.get('name', ['anonymous'])[0]
    age = request.query_params.get('age', ['unknown'])[0]
    return f"Name: {name}, Age: {age}"

@app.route("/headers")
def show_headers(request):
    # Access headers (all lowercase keys)
    user_agent = request.headers.get('user-agent', 'Unknown')
    content_type = request.headers.get('content-type', 'Not specified')
    return f"User-Agent: {user_agent}\nContent-Type: {content_type}"

@app.route("/echo", methods=["POST"])
def echo_json(request):
    # Parse JSON body
    try:
        data = request.json()
        return f"Received JSON: {data}"
    except Exception as e:
        return f"Error parsing JSON: {e}"

@app.route("/form", methods=["POST"])
def handle_form(request):
    # Parse form data
    form_data = request.form()
    username = form_data.get('username', [''])[0]
    password = form_data.get('password', [''])[0]
    return f"Username: {username}, Password: {'*' * len(password)}"

@app.route("/info", methods=["GET", "POST"])
def request_info(request):
    # Show all request details
    info = []
    info.append(f"Method: {request.method}")
    info.append(f"Path: {request.path}")
    info.append(f"Query Params: {request.query_params}")
    info.append(f"Headers: {request.headers}")
    info.append(f"Body Length: {len(request.body)} bytes")
    return "\n".join(info)

if __name__ == "__main__":
    print("Starting TurboX Request Parsing Demo...")
    print("\nTry these commands:")
    print("  curl http://127.0.0.1:8000/")
    print("  curl http://127.0.0.1:8000/query?name=John&age=30")
    print("  curl http://127.0.0.1:8000/headers")
    print("  curl -X POST -H 'Content-Type: application/json' -d '{\"message\":\"hello\"}' http://127.0.0.1:8000/echo")
    print("  curl -X POST -d 'username=john&password=secret' http://127.0.0.1:8000/form")
    print("  curl http://127.0.0.1:8000/info")
    print()
    app.run()
