import json
import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
TABLE_NAME = "music"
JSON_FILE = "a2.json"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

try:
    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    songs = data["songs"]

    print(f"Found {len(songs)} songs in {JSON_FILE}.")
    print("Uploading songs to DynamoDB...")

    with table.batch_writer() as batch:
        for index, song in enumerate(songs, start=1):
            item = {
                "title": song["title"],
                "artist": song["artist"],
                "year": song["year"],
                "web_url": song["web_url"],
                "image_url": song["img_url"]
            }

            batch.put_item(Item=item)

            print(
                f"[{index}/{len(songs)}] "
                f"{song['title']} - {song['artist']}"
            )

    print()
    print("All songs uploaded successfully.")

except FileNotFoundError:
    print(f"Error: {JSON_FILE} was not found.")

except KeyError as error:
    print(f"Error: missing field in JSON: {error}")

except ClientError as error:
    print("AWS error:")
    print(error)

except Exception as error:
    print("Unexpected error:")
    print(error)
