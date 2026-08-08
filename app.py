from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "development-secret-key"


# Temporary users for frontend testing.
# Later, person 1 will replace this with DynamoDB.
TEMP_USERS = {
    "test@student.rmit.edu.au": {
        "password": "123456",
        "user_name": "Test User",
    }
}

TEMP_MUSIC = [
    {
        "music_id": "1904#The Tallest Man On Earth",
        "title": "1904",
        "artist": "The Tallest Man On Earth",
        "year": "2012",
        "image_url": "https://via.placeholder.com/180",
    },
    {
        "music_id": "Creep#Radiohead",
        "title": "Creep",
        "artist": "Radiohead",
        "year": "1993",
        "image_url": "https://via.placeholder.com/180",
    },
    {
        "music_id": "Love Story#Taylor Swift",
        "title": "Love Story",
        "artist": "Taylor Swift",
        "year": "2021",
        "image_url": "https://via.placeholder.com/180",
    },
]

TEMP_SUBSCRIPTIONS = {}


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = TEMP_USERS.get(email)

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

        if email in TEMP_USERS:
            return render_template(
                "register.html",
                error="The email already exists",
            )

        TEMP_USERS[email] = {
            "password": password,
            "user_name": user_name,
        }

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/main")
def main():
    if "email" not in session:
        return redirect(url_for("login"))

    subscriptions = TEMP_SUBSCRIPTIONS.get(
        session["email"],
        [],
    )

    return render_template(
        "main.html",
        user_name=session["user_name"],
        subscriptions=subscriptions,
        results=None,
        no_results=False,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/query", methods=["POST"])
def query_music():
    if "email" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip().lower()
    year = request.form.get("year", "").strip().lower()
    artist = request.form.get("artist", "").strip().lower()

    results = []

    for song in TEMP_MUSIC:
        title_match = (
            not title
            or title in song["title"].lower()
        )

        year_match = (
            not year
            or year in song["year"].lower()
        )

        artist_match = (
            not artist
            or artist in song["artist"].lower()
        )

        if title_match and year_match and artist_match:
            results.append(song)

    subscriptions = TEMP_SUBSCRIPTIONS.get(
        session["email"],
        [],
    )

    return render_template(
        "main.html",
        user_name=session["user_name"],
        subscriptions=subscriptions,
        results=results,
        no_results=len(results) == 0,
        query_title=request.form.get("title", ""),
        query_year=request.form.get("year", ""),
        query_artist=request.form.get("artist", ""),
    )


@app.route("/subscribe", methods=["POST"])
def subscribe():
    if "email" not in session:
        return redirect(url_for("login"))

    music_id = request.form.get("music_id")

    song = next(
        (
            song
            for song in TEMP_MUSIC
            if song["music_id"] == music_id
        ),
        None,
    )

    if song:
        subscriptions = TEMP_SUBSCRIPTIONS.setdefault(
            session["email"],
            [],
        )

        if not any(
            item["music_id"] == music_id
            for item in subscriptions
        ):
            subscriptions.append(song)

    return redirect(url_for("main"))


@app.route("/remove", methods=["POST"])
def remove_subscription():
    if "email" not in session:
        return redirect(url_for("login"))

    music_id = request.form.get("music_id")

    subscriptions = TEMP_SUBSCRIPTIONS.get(
        session["email"],
        [],
    )

    TEMP_SUBSCRIPTIONS[session["email"]] = [
        song
        for song in subscriptions
        if song["music_id"] != music_id
    ]

    return redirect(url_for("main"))

if __name__ == "__main__":
    app.run(debug=True)