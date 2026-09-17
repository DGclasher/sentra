from app.repository.cognito_repo import CognitoRepository


class AuthService:
    def __init__(self):
        self.repo = CognitoRepository()

    async def verify_access_token(self, access_token: str):
        try:
            return await self.repo.verify_access_token(access_token)
        except ValueError as e:
            raise ValueError(str(e)) from e
