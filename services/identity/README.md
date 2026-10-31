# Identity Service

The Identity Service is a FastAPI service that manages Sentra user profiles and administrator-controlled staff accounts.

## What It Does

- Returns the authenticated user's profile.
- Updates the authenticated user's email, first name, and last name.
- Allows administrators to create, list, view, update, and delete staff accounts.
- Provisions staff accounts in Amazon Cognito and stores staff profiles in DynamoDB.
- Rolls back Cognito staff creation when the corresponding DynamoDB profile cannot be created.
- Uses the `X-User-Id` request header as the caller identity supplied by the API gateway.

## API Endpoints

User profile endpoints:

- `GET /api/v1/identity/me`
- `PATCH /api/v1/identity/me`

Administrator staff endpoints:

- `POST /api/v1/identity/admin/staff`
- `GET /api/v1/identity/admin/staff`
- `GET /api/v1/identity/admin/staff/{staff_id}`
- `PATCH /api/v1/identity/admin/staff/{staff_id}`
- `DELETE /api/v1/identity/admin/staff/{staff_id}`

Health endpoints:

- `GET /health`
- `GET /ready`

All application endpoints require `X-User-Id`. Staff administration additionally requires the caller to have the `admin` role.

## Dependencies

Runtime dependencies are pinned or specified in `requirements.txt`:

- Python 3.12
- FastAPI and Uvicorn
- Pydantic and Pydantic Settings
- Boto3 and Botocore
- Python dotenv
- Email validation support
- Python JOSE with cryptography

Development and testing dependencies include pytest, pytest-asyncio, HTTPX, Black, mypy, and Pylint.

## AWS Dependencies

The service requires access to:

- Amazon DynamoDB `Users` and `Staffs` tables.
- An Amazon Cognito User Pool for staff account administration.
- AWS credentials with permission to read and update the DynamoDB tables, administer Cognito users, and list Cognito users.

## Configuration

Configuration is loaded from environment variables or a local `.env` file:

```text
AWS_REGION
COGNITO_USER_POOL_ID
COGNITO_CLIENT_ID
COGNITO_CLIENT_SECRET
DYNAMODB_USER_TABLE_NAME
DYNAMODB_STAFF_TABLE_NAME
DYNAMODB_ENDPOINT_URL
```

`AWS_REGION` defaults to `us-east-1`. The DynamoDB table names default to `Users` and `Staffs`. `DYNAMODB_ENDPOINT_URL` is optional and can be used for a local DynamoDB-compatible endpoint.

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run the tests from the service directory:

```bash
python -m pytest tests -v
```