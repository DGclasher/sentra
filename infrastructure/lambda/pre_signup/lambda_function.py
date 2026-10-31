import os

import boto3


dynamodb = boto3.resource("dynamodb")
USERS_TABLE_NAME = os.environ["USERS_TABLE_NAME"]
users_table = dynamodb.Table(USERS_TABLE_NAME)


def lambda_handler(event, context):
    trigger_source = event.get("triggerSource")
    print("Trigger source:", trigger_source)
    event["response"]["autoConfirmUser"] = True

    user_attributes = event["request"]["userAttributes"]
    if "email" in user_attributes:
        event["response"]["autoVerifyEmail"] = True

    if trigger_source == "PreSignUp_SignUp":
        username = event.get("userName")
        item = {
            "userId": username,
            "email": user_attributes.get("email"),
            "first_name": user_attributes.get("given_name"),
            "last_name": user_attributes.get("family_name"),
            "role": "user",
        }
        users_table.put_item(Item=item)
        print("Created user in Users table:", username)
    elif trigger_source == "PreSignUp_AdminCreateUser":
        print("Admin-created user. Skipping Users table:", event.get("userName"))

    return event
