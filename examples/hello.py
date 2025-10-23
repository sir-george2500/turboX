from turbox import TurboX

app = TurboX()

# Use the new HTTP method decorators!
@app.get("/")
def hello(request):
    return "Hello, World!"

@app.get("/ping")
def ping(request):
    return "pong"

@app.get("/greet")
def greet(request):
    name = request.query_params.get('name', ['Guest'])[0]
    return f"Hello, {name}!"

@app.post("/echo")
def echo(request):
    return "Echo: POST received"

if __name__ == "__main__":
    app.run()
