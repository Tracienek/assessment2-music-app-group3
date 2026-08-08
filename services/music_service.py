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


def get_user(email):
    return TEMP_USERS.get(email)


def create_user(email, user_name, password):
    if email in TEMP_USERS:
        return False

    TEMP_USERS[email] = {
        "user_name": user_name,
        "password": password,
    }

    return True


def search_music(title="", artist="", year=""):
    title = title.lower().strip()
    artist = artist.lower().strip()
    year = year.lower().strip()

    results = []

    for song in TEMP_MUSIC:
        if title and title not in song["title"].lower():
            continue

        if artist and artist not in song["artist"].lower():
            continue

        if year and year not in song["year"].lower():
            continue

        results.append(song)

    return results


def get_music_by_id(music_id):
    for song in TEMP_MUSIC:
        if song["music_id"] == music_id:
            return song

    return None


def get_subscriptions(email):
    return TEMP_SUBSCRIPTIONS.get(email, [])


def add_subscription(email, music_id):
    song = get_music_by_id(music_id)

    if not song:
        return False

    subscriptions = TEMP_SUBSCRIPTIONS.setdefault(email, [])

    already_exists = any(
        item["music_id"] == music_id
        for item in subscriptions
    )

    if not already_exists:
        subscriptions.append(song)

    return True


def remove_subscription(email, music_id):
    subscriptions = TEMP_SUBSCRIPTIONS.get(email, [])

    TEMP_SUBSCRIPTIONS[email] = [
        song
        for song in subscriptions
        if song["music_id"] != music_id
    ]