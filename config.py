import os

from dotenv import load_dotenv


load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")

LOGIN_TABLE_NAME = os.getenv("LOGIN_TABLE_NAME", "login")
MUSIC_TABLE_NAME = os.getenv("MUSIC_TABLE_NAME", "music")
SUBSCRIPTION_TABLE_NAME = os.getenv(
    "SUBSCRIPTION_TABLE_NAME",
    "subscriptions",
)

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key")