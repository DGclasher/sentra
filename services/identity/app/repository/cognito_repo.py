import boto3  # type: ignore[import-untyped]
from typing import Any

from app.core.config import settings
from botocore.exceptions import ClientError  # type: ignore[import-untyped]


class CognitoRepository:

    def __init__(self):
        self.cognito = boto3.client(
            "cognito-idp",
            region_name=settings.aws_region
        )

        self.user_pool_id = settings.cognito_user_pool_id

    def create_staff_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
    ) -> dict[str, Any]:

        try:
            response = self.cognito.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {
                        "Name": "email",
                        "Value": email,
                    },
                    {
                        "Name": "given_name",
                        "Value": first_name,
                    },
                    {
                        "Name": "family_name",
                        "Value": last_name,
                    },
                ],
                MessageAction="SUPPRESS",
            )

            user = response["User"]

            # Cognito's unique user ID
            user_sub = next(
                (
                    attribute["Value"]
                    for attribute in user.get("Attributes", [])
                    if attribute["Name"] == "sub"
                ),
                None,
            )

            if user_sub is None:
                raise RuntimeError(
                    "Cognito user was created but sub was not returned"
                )

            return {
                "username": user["Username"],
                "sub": user_sub,
            }

        except ClientError as error:

            error_code = (
                error.response
                .get("Error", {})
                .get("Code")
            )

            if error_code == "UsernameExistsException":
                raise ValueError(
                    "A user with this email already exists"
                ) from error

            raise RuntimeError(
                "Unable to create Cognito user"
            ) from error

    def delete_staff_user(
        self,
        cognito_username: str
    ) -> None:

            try:
                self.cognito.admin_delete_user(
                    UserPoolId=self.user_pool_id,
                    Username=cognito_username,
                )

            except ClientError as error:
                raise RuntimeError(
                    "Unable to delete Cognito user"
                ) from error