# Identity Service

User and organization management service for the Sentra platform.

## Responsibilities

- User account management
- Organization creation and management
- Organization member management
- User roles and permissions
- User profile management

## Directory Structure

```
identity/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── routes.py        # API endpoint definitions
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py        # Configuration and settings
│   │   ├── auth.py          # Cognito JWT validation (placeholder)
│   │   └── __init__.py
│   │   └── __init__.py
│   ├── services/            # Business logic layer
│   │   └── __init__.py
│   ├── repositories/        # Data access layer (placeholder)
│   │   └── __init__.py
│   └── __init__.py
├── tests/                   # Test suite (placeholder)
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

### Health
- `GET /health` - Health check
- `GET /ready` - Readiness check

### Users
- `GET /api/v1/me` - Get current user

### Organizations
- `POST /api/v1/organizations` - Create organization
- `GET /api/v1/organizations` - List organizations
- `GET /api/v1/organizations/{organization_id}` - Get organization
- `PATCH /api/v1/organizations/{organization_id}` - Update organization

### Organization Members
- `GET /api/v1/organizations/{organization_id}/members` - List members
- `POST /api/v1/organizations/{organization_id}/members` - Add member
- `PATCH /api/v1/organizations/{organization_id}/members/{user_id}` - Update member role
- `DELETE /api/v1/organizations/{organization_id}/members/{user_id}` - Remove member

### User
- `email` - Email address
- `first_name` - User first name
- `last_name` - User last name
- `created_at` - Creation timestamp
- `owner_id` - ID of organization owner
- `created_at` - Creation timestamp

### OrganizationMember
- `user_id` - Member user ID
- `role` - Role (owner, admin, member, viewer)
- `joined_at` - Membership start timestamp

### UserProfile
- `profile_id` - Unique identifier
- `user_id` - Associated user
- `avatar_url` - Profile picture URL
- `bio` - User biography
- `phone` - Phone number

## Enums

### Role
- `owner` - Organization owner
- `admin` - Administrator
- `member` - Regular member
- `viewer` - Read-only member

## Authentication

Authentication is handled by API Gateway. It passes the authenticated identity in the `X-User-Id` header. The identity service uses that header as the `Users.userId` value for `/api/v1/me`; it does not extract a username from a request token or accept a user ID from query parameters or request bodies.

## Local Development

### Setup
```bash
cd services/identity
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
python -m uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`

### Run Tests

### Lint and Type Check
```

```bash
docker build -t identity-service .
```bash
docker run -p 8000:8000 identity-service
```
- [ ] Implement database access with actual ORM (SQLAlchemy/Tortoise)
- [ ] Connect to DynamoDB or preferred datastore
- [ ] Implement connection pooling

### Validation
- [ ] Add request/response validation
- [ ] Add business logic validations
- [ ] Add error handling middleware

### Observability
- [ ] Add logging
- [ ] Add structured tracing
- [ ] Add metrics

### Testing
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add test database setup

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **pytest** - Testing framework

See `requirements.txt` for full dependency list.

## Notes

This is a scaffold implementation. All endpoints return `NotImplementedError`. Data layer operations are placeholders.
