import os
import boto3

from boto3.dynamodb.conditions import Key, Attr

from dotenv import load_dotenv

load_dotenv()


dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"), aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
music = dynamodb.Table(os.getenv("MUSIC_TABLE_NAME", "music"))
login = dynamodb.Table(os.getenv("LOGIN_TABLE_NAME", "login"))
Subscriptions = dynamodb.Table(os.getenv("SUBSCRIPTION_TABLE_NAME", "subscriptions"))



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
    return login.get_item(Key={"email": email})


def create_user(email, user_name, password):
    if get_user(email):
        return False

    login.put_item(Item={
        "email": email,
        "user_name": user_name,
        "password": password
    })

    return True


def search_music(title="", artist="", year=""):
    title = title.lower().strip()
    artist = artist.lower().strip()
    year = year.lower().strip()

    results = []

    for song in music.scan()["Items"]:
        if title and title not in song["title"].lower():
            continue

        if artist and artist not in song["artist"].lower():
            continue

        if year and year not in song["year"].lower():
            continue

        results.append(song)

    return results


def get_music_by_id(music_id):
    return music.get_item(Key={"music_id": music_id})


def get_subscriptions(email):
    return Subscriptions.get_item(Key={"email": email})

def add_subscription(email, music_id):
    song = get_music_by_id(music_id)

    if not song:
        return False

    subscriptions = Subscriptions.get_item(Key={"email": email})

    already_exists = any(
        item["music_id"] == music_id
        for item in subscriptions
    )

    if not already_exists:
        subscriptions.append(song)
    
    Subscriptions.put_item(Item={
        "email": email,
        "subscriptions": subscriptions
    })

    return True


def remove_subscription(email, music_id):
    subscriptions = Subscriptions.get_item(Key={"email": email})

    subscriptions = [
        song
        for song in subscriptions
        if song["music_id"] != music_id
    ]

    Subscriptions.put_item(Item={
        "email": email,
        "subscriptions": subscriptions
    })