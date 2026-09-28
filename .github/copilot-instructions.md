# Sentra Copilot Instructions

## Project Overview

- This is a Python 3.12 project (`pyproject.toml`) built around FastAPI services and AWS DynamoDB/Cognito. Keep the existing architecture and boundaries intact.
- Make the smallest change that satisfies the request. Do not restructure, rename, move, replace, or redesign existing components, APIs, models, dependencies, configuration, or infrastructure unless explicitly required. Do not modify unrelated files or add speculative features, abstractions, frameworks, or libraries.
- Search the repository before assuming a file, API, class, function, environment variable, table, endpoint, dependency, or AWS resource exists. Never invent project facts, test results, or implementation details; state uncertainty when the repository and request do not determine an answer.

## Repository Structure

- `services/identity/app`: identity FastAPI app, split into `api`, `core`, `domain`, `service`, and `repository` packages.
- `services/ticket/app`: ticket FastAPI app, split into `api/routes`, `core`, `domain`, `schemas`, `service`, and `repository` packages.
- Each service has its own `tests` directory, and `services/identity` also has a Dockerfile and requirements file.
- Root HTML/Python files and the minimal root README are separate exploratory/sample code; do not assume they are part of either service.

## Architecture and Coding Conventions

- Routes are thin FastAPI functions using `APIRouter`, dependency injection, request/response models, and service calls. Put business rules in `service`, persistence/AWS calls in `repository`, and shared domain values/models in `domain` or `schemas` as appropriate.
- Use the existing naming and data shapes: identity/DynamoDB fields include `userId`, `staffId`, `cognitoUsername`, `first_name`, and `last_name`; ticket/message fields use camelCase such as `ticketId`, `assignedStaffId`, and `createdAt`.
- Existing code uses type hints, Pydantic v2 models, `ConfigDict(extra="forbid")` for request bodies, `Field` constraints, `dict[str, Any]`, and `str | None` unions. Match nearby style rather than introducing a new style.
- Keep route response models and status codes explicit. Preserve the existing `/api/v1` prefixes and route tags.

## API, Authentication, and Authorization

- Both services obtain the caller identity from the gateway-provided `X-User-Id` header. Do not accept caller identity from query parameters or request bodies.
- Identity uses `get_current_user_id`; missing identity returns HTTP 401. Ticket uses `get_current_user`, resolves the role through `IdentityRepository`, and returns 401 for missing/unknown identities.
- Ticket roles are `user`, `staff`, and `admin`; staff and admin share staff-route access. User routes reject staff/admin with 403, and staff routes reject regular users with 403.
- User ticket reads/messages are restricted to tickets owned by the authenticated user. Staff ticket reads/messages are restricted to tickets assigned to that staff member. Missing or unauthorized ticket visibility is intentionally reported as 404.
- Identity admin staff operations require the requesting DynamoDB staff record to have role `admin`; use the existing 403/404 behavior and Cognito/DynamoDB ordering when changing these operations.
- `main.py` at the repository root contains an older Cognito JWT experiment. Do not treat it as the authentication implementation for the service apps without explicit scope.

## Validation and Error Handling

- Use Pydantic validation for input constraints and forbidden extra fields. Profile and ticket/message content fields already define the expected length/email rules; extend those models rather than duplicating validation in routes.
- Services raise `fastapi.HTTPException` for expected API errors: commonly 401/403/404/409/422, with concise `detail` strings. Repositories translate relevant boto3 `ClientError` cases to `ValueError`, `RuntimeError`, `None`, or `False` according to the existing method contract.
- Preserve conditional DynamoDB writes for staff creation/update/delete and ticket acceptance/rejection. Ticket acceptance must remain atomic so concurrent staff claims produce one success and a 409 for the loser.
- Identity staff creation provisions Cognito before DynamoDB and rolls Cognito back if profile creation fails; updates/deletes likewise coordinate Cognito and DynamoDB. Preserve this ordering and its existing failure messages unless the request changes the contract.

## Data Access and AWS

- Repositories create boto3 DynamoDB resources using `AWS_REGION` and optional `DYNAMODB_ENDPOINT_URL`, then access the configured tables directly. Identity uses `Users` and `Staffs`; ticket uses `Users`, `Staffs`, `Tickets`, and `Messages`.
- Ticket and identity repositories currently use DynamoDB `scan` for filtered lists and direct key operations for individual records. Do not introduce an ORM or datastore without an explicit requirement.
- Cognito operations are isolated in `CognitoRepository` and use `COGNITO_USER_POOL_ID`; keep Cognito-specific calls out of routes and unrelated services.
- Configuration is loaded with `python-dotenv` and `pydantic-settings`, with environment-backed defaults in each service's `core/config.py`. Do not hard-code credentials or add secrets to tracked files.

## Testing and Workflow

- Tests use pytest, FastAPI `TestClient`, `pytest.raises`, `unittest.mock.Mock`/`monkeypatch`, and a fake in-memory repository for service behavior. Add focused tests beside the affected service and follow existing fixtures and assertion style.
- Run tests from the relevant service directory so its `app` package resolves, for example `cd services/ticket && pytest` or `cd services/identity && pytest`.
- Use the repository's declared tools and pinned dependencies (`pyproject.toml`, service requirements, Black, Pylint, mypy, pytest). Do not upgrade or replace dependencies as part of an unrelated change.

## Known Repository Inconsistencies

- `pyproject.toml` declares Python `>=3.12`, while `services/identity/Dockerfile` currently starts from Python 3.11; do not silently resolve this mismatch. Confirm scope before changing runtime versions.
- `.env.example` contains legacy/future Cognito, service URL, database, Bedrock, and S3/SQS placeholders that are not all consumed by the current service settings. Prefer the actual `core/config.py` names and observed code paths.
- There is no evident CI workflow or shared logging abstraction. Existing code uses occasional `print` debugging; do not claim structured logging or CI validation unless the repository gains it.
