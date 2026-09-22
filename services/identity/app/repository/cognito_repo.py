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
                        "Name": "email_verified",
                        "Value": "true"
                    },
                    {
                        "Name": "family_name",
                        "Value": last_name,
                    },
                ],
                MessageAction="SUPPRESS",
            )

            user = response["User"]

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

    def get_staff_user(
        self,
        cognito_username: str,
    ) -> dict[str, Any]:

        try:
            response = self.cognito.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=cognito_username,
            )

            return response

        except ClientError as error:

            error_code = (
                error.response
                .get("Error", {})
                .get("Code")
            )

            if error_code == "UserNotFoundException":
                raise ValueError(
                    "Cognito user not found"
                ) from error

            raise RuntimeError(
                "Unable to retrieve Cognito user"
            ) from error

    def update_staff_user(
        self,
        cognito_username: str,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> None:

        attributes = []

        if email is not None:
            attributes.append(
                {
                    "Name": "email",
                    "Value": email,
                }
            )

            attributes.append(
                {
                    "Name": "email_verified",
                    "Value": "true",
                }
            )

        if first_name is not None:
            attributes.append(
                {
                    "Name": "given_name",
                    "Value": first_name,
                }
            )

        if last_name is not None:
            attributes.append(
                {
                    "Name": "family_name",
                    "Value": last_name,
                }
            )

        if not attributes:
            return

        try:
            self.cognito.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=cognito_username,
                UserAttributes=attributes,
            )

        except ClientError as error:

            error_code = (
                error.response
                .get("Error", {})
                .get("Code")
            )

            if error_code == "UserNotFoundException":
                raise ValueError(
                    "Cognito user not found"
                ) from error

            if error_code == "AliasExistsException":
                raise ValueError(
                    "A user with this email already exists"
                ) from error

            raise RuntimeError(
                "Unable to update Cognito user"
            ) from error

    def delete_staff_user(
        self,
        cognito_username: str,
    ) -> None:

        try:
            self.cognito.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=cognito_username,
            )

        except ClientError as error:

            error_code = (
                error.response
                .get("Error", {})
                .get("Code")
            )

            if error_code == "UserNotFoundException":
                raise ValueError(
                    "Cognito user not found"
                ) from error

            raise RuntimeError(
                "Unable to delete Cognito user"
            ) from error

    def list_staff_users(self) -> list[dict[str, Any]]:

        users = []
        pagination_token = None

        try:
            while True:

                params = {
                    "UserPoolId": self.user_pool_id,
                }

                if pagination_token:
                    params["PaginationToken"] = pagination_token

                response = self.cognito.list_users(**params)

                users.extend(response.get("Users", []))

                pagination_token = response.get("PaginationToken")

                if not pagination_token:
                    break

            return users

        except ClientError as error:
            raise RuntimeError(
                "Unable to retrieve Cognito users"
            ) from error

