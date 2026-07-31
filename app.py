from flask import Flask, redirect, url_for

from config import SECRET_KEY


app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return "Login page is working"


@app.route("/health")
def health():
    return {
        "status": "ok",
        "application": "Assessment 2 Music App",
    }


if __name__ == "__main__":
    app.run(debug=True)