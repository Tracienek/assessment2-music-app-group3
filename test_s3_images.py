import os

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SAMPLE_SIZE = 5

s3 = boto3.client("s3", region_name=AWS_REGION)

resp = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="music-images/")
objects = resp.get("Contents", [])

print(f"Total objects under music-images/: {len(objects)}")

for obj in objects[:SAMPLE_SIZE]:
    key = obj["Key"]
    url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
    r = requests.get(url, timeout=10)
    status = "OK" if r.status_code == 200 else f"FAILED ({r.status_code})"
    print(f"  {key}: {status} - {url}")
