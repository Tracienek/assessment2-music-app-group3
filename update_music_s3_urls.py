import json
import boto3

REGION = "us-east-1"
TABLE_NAME = "music"
JSON_FILE = "a2_with_s3_images.json"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

songs = data["songs"]

print(f"Updating {len(songs)} songs with S3 image URLs...")

with table.batch_writer() as batch:
    for index, song in enumerate(songs, start=1):
        batch.put_item(
            Item={
                "title": song["title"],
                "artist": song["artist"],
                "year": song["year"],
                "web_url": song["web_url"],
                "image_url": song["image_url"],
            }
        )

        print(
            f"[{index}/{len(songs)}] "
            f"{song['title']} - {song['artist']}"
        )

print("DynamoDB music table updated with S3 image URLs.")
