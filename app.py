from flask import Flask, render_template, request, redirect, url_for, session

from services.music_service import (
    get_user,
    create_user,
    search_music,
    get_subscriptions,
    add_subscription,
    remove_subscription,
)


app = Flask(__name__)
app.secret_key = "development-secret-key"


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = get_user(email)

        if not user or user["password"] != password:
            return render_template(
                "login.html",
                error="email or password is invalid",
            )

        session["email"] = email
        session["user_name"] = user["user_name"]

        return redirect(url_for("main"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user_name = request.form.get("user_name", "").strip()
        password = request.form.get("password", "").strip()

        success = create_user(
            email,
            user_name,
            password,
        )

        if not success:
            return render_template(
                "register.html",
                error="The email already exists",
            )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/main")
def main():
    if "email" not in session:
        return redirect(url_for("login"))

    subscriptions = get_subscriptions(
        session["email"]
    )

    return render_template(
        "main.html",
        user_name=session["user_name"],
        subscriptions=subscriptions,
        results=None,
        no_results=False,
    )


@app.route("/query", methods=["POST"])
def query_music():
    if "email" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    year = request.form.get("year", "").strip()
    artist = request.form.get("artist", "").strip()

    results = search_music(
        title=title,
        artist=artist,
        year=year,
    )

    subscriptions = get_subscriptions(
        session["email"]
    )

    return render_template(
        "main.html",
        user_name=session["user_name"],
        subscriptions=subscriptions,
        results=results,
        no_results=len(results) == 0,
        query_title=title,
        query_year=year,
        query_artist=artist,
    )


@app.route("/subscribe", methods=["POST"])
def subscribe():
    if "email" not in session:
        return redirect(url_for("login"))

    music_id = request.form.get("music_id")

    if music_id:
        add_subscription(
            session["email"],
            music_id,
        )

    return redirect(url_for("main"))


@app.route("/remove", methods=["POST"])
def remove_subscription_route():
    if "email" not in session:
        return redirect(url_for("login"))

    music_id = request.form.get("music_id")

    if music_id:
        remove_subscription(
            session["email"],
            music_id,
        )

    return redirect(url_for("main"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)