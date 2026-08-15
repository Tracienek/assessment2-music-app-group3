import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
TABLE_NAME = "music"

dynamodb = boto3.client("dynamodb", region_name=REGION)

try:
    print(f"Creating DynamoDB table: {TABLE_NAME}...")

    dynamodb.create_table(
        TableName=TABLE_NAME,

        KeySchema=[
            {
                "AttributeName": "title",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "artist",
                "KeyType": "RANGE"
            }
        ],

        AttributeDefinitions=[
            {
                "AttributeName": "title",
                "AttributeType": "S"
            },
            {
                "AttributeName": "artist",
                "AttributeType": "S"
            }
        ],

        BillingMode="PAY_PER_REQUEST"
    )

    waiter = dynamodb.get_waiter("table_exists")
    waiter.wait(TableName=TABLE_NAME)

    print("Music table created successfully.")

except ClientError as error:
    if error.response["Error"]["Code"] == "ResourceInUseException":
        print("Music table already exists.")
    else:
        print("Error creating music table:")
        print(error)
