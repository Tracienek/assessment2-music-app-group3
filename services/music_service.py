import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from urllib.parse import urlparse

from config import (
    AWS_REGION,
    LOGIN_TABLE_NAME,
    MUSIC_TABLE_NAME,
    SUBSCRIPTION_TABLE_NAME,
    S3_BUCKET_NAME,
)


dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
)

login_table = dynamodb.Table(LOGIN_TABLE_NAME)
music_table = dynamodb.Table(MUSIC_TABLE_NAME)
subscription_table = dynamodb.Table(SUBSCRIPTION_TABLE_NAME)


def make_music_id(title, artist):
    return f"{title}|||{artist}"


def prepare_song_for_display(song):
    song = dict(song)

    song["music_id"] = make_music_id(
        song["title"],
        song["artist"],
    )

    image_url = song.get("image_url", "")

    # S3 bucket is private, so create a temporary readable URL
    if (
        S3_BUCKET_NAME
        and image_url
        and "amazonaws.com" in image_url
    ):
        try:
            key = urlparse(image_url).path.lstrip("/")

            song["image_url"] = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": S3_BUCKET_NAME,
                    "Key": key,
                },
                ExpiresIn=3600,
            )
        except Exception as error:
            print("Could not generate S3 image URL:", error)

    return song


# -------------------------
# USER
# -------------------------

def get_user(email):
    response = login_table.get_item(
        Key={
            "email": email,
        }
    )

    return response.get("Item")


def create_user(email, user_name, password):
    try:
        login_table.put_item(
            Item={
                "email": email,
                "user_name": user_name,
                "password": password,
            },
            ConditionExpression="attribute_not_exists(email)",
        )

        return True

    except ClientError as error:
        if (
            error.response["Error"]["Code"]
            == "ConditionalCheckFailedException"
        ):
            return False

        raise


# -------------------------
# MUSIC
# -------------------------

def get_all_music():
    songs = []

    response = music_table.scan()
    songs.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = music_table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )

        songs.extend(response.get("Items", []))

    return songs


def search_music(title="", artist="", year=""):
    title = title.strip().lower()
    artist = artist.strip().lower()
    year = year.strip().lower()

    results = []

    for song in get_all_music():
        song_title = str(song.get("title", "")).lower()
        song_artist = str(song.get("artist", "")).lower()
        song_year = str(song.get("year", "")).lower()

        # Multiple conditions work as AND
        if title and title not in song_title:
            continue

        if artist and artist not in song_artist:
            continue

        if year and year not in song_year:
            continue

        results.append(
            prepare_song_for_display(song)
        )

    return results


def get_music_by_id(music_id):
    try:
        title, artist = music_id.split("|||", 1)

    except ValueError:
        return None

    response = music_table.get_item(
        Key={
            "title": title,
            "artist": artist,
        }
    )

    return response.get("Item")


# -------------------------
# SUBSCRIPTIONS
# -------------------------

def get_subscriptions(email):
    response = subscription_table.query(
        KeyConditionExpression=Key("user_email").eq(email)
    )

    items = response.get("Items", [])

    return [
        prepare_song_for_display(song)
        for song in items
    ]


def add_subscription(email, music_id):
    song = get_music_by_id(music_id)

    if not song:
        return False

    subscription_table.put_item(
        Item={
            "user_email": email,
            "music_id": music_id,
            "title": song["title"],
            "artist": song["artist"],
            "year": song["year"],
            "image_url": song.get("image_url", ""),
        }
    )

    return True


def remove_subscription(email, music_id):
    subscription_table.delete_item(
        Key={
            "user_email": email,
            "music_id": music_id,
        }
    )

    return True
