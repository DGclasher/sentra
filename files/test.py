import os
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

load_dotenv()

app = FastAPI()

COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET")
COGNITO_REDIRECT_URI = os.getenv("COGNITO_REDIRECT_URI")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_REGION = os.getenv("COGNITO_REGION")

if not all([COGNITO_DOMAIN, COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET, COGNITO_REDIRECT_URI, COGNITO_USER_POOL_ID, COGNITO_REGION]):
    raise ValueError(
        "Missing required environment variables for Cognito configuration.")

TOKEN_URL = f"https://{COGNITO_DOMAIN}/oauth2/token"

COGNITO_ISSUER = (
    f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/"
    f"{COGNITO_USER_POOL_ID}"
)

JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

security = HTTPBearer()
jwks_cache: dict[str, Any] | None = None


async def get_jwks() -> dict[str, Any]:
    global jwks_cache
    if jwks_cache is not None:
        return jwks_cache

    async with httpx.AsyncClient() as client:
        response = await client.get(JWKS_URL)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch JWKS")

    print(response.json())  # Debugging line to print the JWKS response
    jwks_cache = response.json()
    return jwks_cache


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security),) -> dict[str, Any]:
    token = credentials.credentials
    print(f"Verifying token: {token[:50]}...")  # Print first 50 chars

    try:
        # First, decode WITHOUT verification to see the payload
        unverified = jwt.decode(
            token,
            "",  # Empty key since we're not verifying
            options={"verify_signature": False},
        )
        print(f"Unverified payload: {unverified}")

        jwks = await get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=COGNITO_ISSUER,
            options={
                "verify_aud": False,
            },
        )
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(
            status_code=401, detail=f"Invalid token: {str(e)}") from e

    # Debugging line to print the decoded payload
    print("Decoded JWT payload:", payload)
    print(f"token_use: {payload.get('token_use')}, expected: access")
    print(
        f"client_id in token: {payload.get('client_id')}, expected: {COGNITO_CLIENT_ID}")

    if payload.get("token_use") != "access":
        raise HTTPException(
            status_code=401, detail=f"Invalid token use: {payload.get('token_use')}")
    if payload.get("client_id") != COGNITO_CLIENT_ID:
        raise HTTPException(
            status_code=401, detail=f"Invalid client ID: {payload.get('client_id')} != {COGNITO_CLIENT_ID}")
    return payload


@app.get("/auth/login")
async def login():
    """Redirect user to Cognito login page."""
    cognito_login_url = (
        f"https://{COGNITO_DOMAIN}/login/continue?"
        f"client_id={COGNITO_CLIENT_ID}&"
        f"response_type=code&"
        f"scope=openid+profile+email&"
        f"redirect_uri={COGNITO_REDIRECT_URI}"
    )

    return RedirectResponse(cognito_login_url)


@app.get("/auth/callback")
async def auth_callback(code: str):
    data = {
        "grant_type": "authorization_code",
        "client_id": COGNITO_CLIENT_ID,
        "client_secret": COGNITO_CLIENT_SECRET,
        "code": code,
        "redirect_uri": COGNITO_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=500, detail="Failed to exchange code for token")

    tokens = response.json()
    print("Tokens received:", tokens)  # Debugging line to print the tokens

    return {
        "access_token": tokens.get("access_token"),
        "id_token": tokens.get("id_token"),
        "refresh_token": tokens.get("refresh_token"),
        "expires_in": tokens.get("expires_in"),
        "token_type": tokens.get("token_type"),
    }


@app.get("/me")
async def me(token: dict[str, Any] = Depends(verify_jwt)):
    return {
        "authenticated": True,
        "user_id": token.get("sub"),
        "username": token.get("username"),
        "email": token.get("email"),
        "client_id": token.get("client_id"),
    }
