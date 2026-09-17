import boto3  # type: ignore[import-untyped]
import httpx
from jose import jwt, JWTError  # type: ignore[import-untyped]
from app.core.config import settings


class CognitoRepository:
    def __init__(self):
        self.client = boto3.client(
            "cognito-idp", region_name=settings.aws_region)
        self.client_id = settings.cognito_client_id

        self.issuer = (
            f"https://cognito-idp.{settings.aws_region}.amazonaws.com/"
            f"{settings.cognito_user_pool_id}"
        )

        self.jwks_url = f"{self.issuer}/.well-known/jwks.json"
        self._jwks = None

    async def verify_access_token(self, access_token: str):
        if self._jwks is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()
                self._jwks = response.json()

        try:
            payload = jwt.decode(
                access_token,
                self._jwks,
                algorithms=["RS256"],
                issuer=self.issuer,
                options={"verify_aud": False},
            )
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}") from e

        if payload.get("token_use") != "access":
            raise ValueError("Token is not an access token")

        if payload.get("client_id") != self.client_id:
            raise ValueError("Token was not issued for this client")

        return payload
