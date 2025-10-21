from turbox import TurboX

app = TurboX()

@app.route("/")
def hello(request):
    return "Hello, World!"

@app.route("/ping")
def ping(request):
    return "pong"

if __name__ == "__main__":
    app.run()
