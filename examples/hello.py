from turbox import TurboX

app = TurboX()

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    app.run()
