import hashlib
import json
import os
import sys
import time

import boto3
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = "music-images"

INPUT_FILE = "a2.json"
OUTPUT_FILE = "a2_with_s3_images.json"

REQUEST_TIMEOUT = 10
MAX_RETRIES = 3


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)

# Turns an image URL into a stable filename so duplicate URLs -> same file
def hash_url(url: str) -> str:
    """Stable filename for a given image URL. Same URL -> same filename,
    which is how we dedupe songs that reuse the same album art."""
    return hashlib.md5(url.encode("utf-8")).hexdigest() + ".jpg"

# Checks S3 for an existing object without downloading it, to avoid re-uploads
def object_exists(s3_client, bucket: str, key: str) -> bool:
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
            return False
        raise

# Fetches the raw image bytes from a URL, retrying up to MAX_RETRIES times
def download_image(url: str) -> bytes:
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.content
        except requests.RequestException as e:
            last_error = e
            print(f"    retry {attempt}/{MAX_RETRIES} for {url}: {e}")
            time.sleep(1)
    raise RuntimeError(f"Failed to download {url}: {last_error}")

# Writes the image bytes to S3 under the given key
def upload_to_s3(s3_client, bucket: str, key: str, data: bytes):
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
        ContentType="image/jpeg",
    )

# Builds the final public HTTPS URL for an uploaded object
def public_s3_url(bucket: str, region: str, key: str) -> str:
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

# Orchestrates the whole run: load JSON, process each song, write output + summary
def main():
    if not S3_BUCKET_NAME:
        print("ERROR: set S3_BUCKET_NAME (env var or .env file) before running.")
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    songs = data["songs"]
    print(f"Loaded {len(songs)} songs from {INPUT_FILE}")

    s3_client = get_s3_client()

    # Maps each img_url to its S3 key, avoiding duplicate head_object calls this run
    url_to_key = {}
    uploaded_count = 0
    skipped_existing = 0
    skipped_duplicate = 0
    failed = []

    for i, song in enumerate(songs, start=1):
        img_url = song.get("img_url")
        if not img_url:
            print(f"[{i}/{len(songs)}] {song.get('title')} - no img_url, skipping")
            continue

        if img_url in url_to_key:
            key = url_to_key[img_url]
            skipped_duplicate += 1
        else:
            filename = hash_url(img_url)
            key = f"{S3_PREFIX}/{filename}"
            url_to_key[img_url] = key

            if object_exists(s3_client, S3_BUCKET_NAME, key):
                skipped_existing += 1
                print(f"[{i}/{len(songs)}] {song['title']} - already in S3, skipping upload")
            else:
                try:
                    print(f"[{i}/{len(songs)}] {song['title']} - downloading + uploading")
                    image_bytes = download_image(img_url)
                    upload_to_s3(s3_client, S3_BUCKET_NAME, key, image_bytes)
                    uploaded_count += 1
                except Exception as e:
                    print(f"    FAILED: {e}")
                    failed.append({"title": song["title"], "img_url": img_url, "error": str(e)})
                    continue

        song["image_url"] = public_s3_url(S3_BUCKET_NAME, AWS_REGION, key)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n--- Summary ---")
    print(f"Total songs:        {len(songs)}")
    print(f"Uploaded (new):     {uploaded_count}")
    print(f"Skipped (in S3):    {skipped_existing}")
    print(f"Skipped (dup URL):  {skipped_duplicate}")
    print(f"Failed:             {len(failed)}")
    print(f"Unique images:      {len(url_to_key)}")
    print(f"Output written to:  {OUTPUT_FILE}")

    if failed:
        print("\nFailed downloads:")
        for f_ in failed:
            print(f"  - {f_['title']}: {f_['error']}")


if __name__ == "__main__":
    main()