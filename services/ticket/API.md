# Ticket Service API Reference

The Ticket Service gets the authenticated identity exclusively from the `X-User-Id` header. API Gateway sets this header from the validated Cognito JWT. Clients must not send `userId` or `assignedStaffId` to select an identity; those values are derived by the service.

Ticket data is stored in the `Tickets` table and messages are stored in the `Messages` table.

## Common Authentication

All `/api/v1/user/*` and `/api/v1/staff/*` endpoints require:

```http
X-User-Id: user-123
```

The service looks up the ID in the existing `Users` and `Staffs` tables. Staff and admin identities have the same staff route access for now.

Common authentication errors:

- `401`: `X-User-Id` is missing or does not identify a known user.
- `403`: the identity does not have the role required by the route.

## Health

### `GET /health`

Returns the service health status.

Headers: none.

Example:

```http
GET /health
```

Success `200`:

```json
{
  "status": "healthy"
}
```

### `GET /ready`

Returns the service readiness status.

Headers: none.

Example:

```http
GET /ready
```

Success `200`:

```json
{
  "ready": true
}
```

## User Tickets

User routes operate only on tickets whose `userId` matches the authenticated `X-User-Id`.

### `POST /api/v1/user/tickets`

Creates an open ticket for the authenticated user. The service assigns `ticketId`, `userId`, `status`, `assignedStaffId`, `createdAt`, and `updatedAt`.

Required headers:

```http
X-User-Id: user-123
Content-Type: application/json
```

Request:

```json
{
  "title": "Unable to access reports",
  "description": "The reports page returns an error."
}
```

Success `201`:

```json
{
  "ticketId": "7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a",
  "userId": "user-123",
  "title": "Unable to access reports",
  "description": "The reports page returns an error.",
  "status": "OPEN",
  "assignedStaffId": null,
  "createdAt": "2026-09-21T12:00:00+00:00",
  "updatedAt": "2026-09-21T12:00:00+00:00"
}
```

Relevant errors: `401` for missing/unknown identity, `403` for a staff/admin identity, and `422` for an invalid request or extra fields such as `userId` or `assignedStaffId`.

### `GET /api/v1/user/tickets`

Lists only tickets owned by the authenticated user.

Required headers:

```http
X-User-Id: user-123
```

Example:

```http
GET /api/v1/user/tickets
```

Success `200`:

```json
[
  {
    "ticketId": "7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a",
    "userId": "user-123",
    "title": "Unable to access reports",
    "description": "The reports page returns an error.",
    "status": "OPEN",
    "assignedStaffId": null,
    "createdAt": "2026-09-21T12:00:00+00:00",
    "updatedAt": "2026-09-21T12:00:00+00:00"
  }
]
```

Relevant errors: `401` for missing/unknown identity and `403` for a staff/admin identity.

### `GET /api/v1/user/tickets/{ticket_id}`

Returns one ticket only when it belongs to the authenticated user.

Required headers:

```http
X-User-Id: user-123
```

Example:

```http
GET /api/v1/user/tickets/7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a
```

Success `200`: returns the ticket object shown in the previous response.

Relevant errors: `401` for missing/unknown identity, `403` for a staff/admin identity, and `404` when the ticket does not exist or belongs to another user.

### `POST /api/v1/user/tickets/{ticket_id}/messages`

Adds a message to a ticket owned by the authenticated user.

Required headers:

```http
X-User-Id: user-123
Content-Type: application/json
```

Request:

```json
{
  "content": "I can reproduce this problem every time."
}
```

Success `201`:

```json
{
  "messageId": "3e3f5b23-2f86-4e26-9c0c-8b38a1e7c4b2",
  "ticketId": "7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a",
  "senderId": "user-123",
  "senderRole": "user",
  "content": "I can reproduce this problem every time.",
  "createdAt": "2026-09-21T12:05:00+00:00"
}
```

Relevant errors: `401` for missing/unknown identity, `403` for a staff/admin identity, `404` for a missing or another user's ticket, and `422` for an invalid request.

### `GET /api/v1/user/tickets/{ticket_id}/messages`

Returns messages only for a ticket owned by the authenticated user.

Required headers:

```http
X-User-Id: user-123
```

Example:

```http
GET /api/v1/user/tickets/7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a/messages
```

Success `200`:

```json
[
  {
    "messageId": "3e3f5b23-2f86-4e26-9c0c-8b38a1e7c4b2",
    "ticketId": "7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a",
    "senderId": "user-123",
    "senderRole": "user",
    "content": "I can reproduce this problem every time.",
    "createdAt": "2026-09-21T12:05:00+00:00"
  }
]
```

Relevant errors: `401` for missing/unknown identity, `403` for a staff/admin identity, and `404` for a missing or another user's ticket.

## Staff and Admin Tickets

Staff and admin routes use the authenticated `X-User-Id` as the staff identity. A staff member can access only tickets assigned to that ID.

### `GET /api/v1/staff/tickets`

Lists tickets assigned to the authenticated staff/admin identity.

Required headers:

```http
X-User-Id: staff-123
```

Example:

```http
GET /api/v1/staff/tickets
```

Success `200`: returns an array of ticket objects.

Relevant errors: `401` for missing/unknown identity and `403` for a regular user identity.

### `GET /api/v1/staff/tickets/available`

Lists open, unassigned tickets available for staff/admin acceptance.

Required headers:

```http
X-User-Id: staff-123
```

Example:

```http
GET /api/v1/staff/tickets/available
```

Success `200`: returns an array of tickets with `status` equal to `OPEN` and no assigned staff identity.

Relevant errors: `401` for missing/unknown identity and `403` for a regular user identity.

### `GET /api/v1/staff/tickets/{ticket_id}`

Returns a ticket only when it is assigned to the authenticated staff/admin identity.

Required headers:

```http
X-User-Id: staff-123
```

Example:

```http
GET /api/v1/staff/tickets/7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a
```

Success `200`: returns the ticket object shown above.

Relevant errors: `401` for missing/unknown identity, `403` for a regular user identity, and `404` when the ticket does not exist or is assigned to another staff member.

### `POST /api/v1/staff/tickets/{ticket_id}/accept`

Atomically claims an available open ticket for the authenticated staff/admin identity and changes its status to `IN_PROGRESS`.

Required headers:

```http
X-User-Id: staff-123
```

Example:

```http
POST /api/v1/staff/tickets/7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a/accept
```

Success `200`: returns the updated ticket with `assignedStaffId` set to `staff-123` and `status` set to `IN_PROGRESS`.

Relevant errors: `401` for missing/unknown identity, `403` for a regular user identity, and `409` when the ticket is missing, no longer open, or already assigned.

### `POST /api/v1/staff/tickets/{ticket_id}/reject`

Releases an available ticket or a ticket currently assigned to the authenticated staff/admin identity. The ticket is reset to `OPEN` with no assigned staff identity.

Required headers:

```http
X-User-Id: staff-123
```

Example:

```http
POST /api/v1/staff/tickets/7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a/reject
```

Success `200`: returns the updated ticket with `status` set to `OPEN` and `assignedStaffId` set to `null`.

Relevant errors: `401` for missing/unknown identity, `403` for a regular user identity, and `409` when the ticket is assigned to another staff member or cannot be released.

### `POST /api/v1/staff/tickets/{ticket_id}/messages`

Adds a message to a ticket assigned to the authenticated staff/admin identity.

Required headers:

```http
X-User-Id: staff-123
Content-Type: application/json
```

Request:

```json
{
  "content": "The issue has been assigned for investigation."
}
```

Success `201`:

```json
{
  "messageId": "8f7b4f9a-8e2b-4f2e-b7d5-2ab2e4c0f5a1",
  "ticketId": "7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a",
  "senderId": "staff-123",
  "senderRole": "staff",
  "content": "The issue has been assigned for investigation.",
  "createdAt": "2026-09-21T12:10:00+00:00"
}
```

Relevant errors: `401` for missing/unknown identity, `403` for a regular user identity, `404` for a missing or differently assigned ticket, and `422` for an invalid request.

### `GET /api/v1/staff/tickets/{ticket_id}/messages`

Returns messages only for a ticket assigned to the authenticated staff/admin identity.

Required headers:

```http
X-User-Id: staff-123
```

Example:

```http
GET /api/v1/staff/tickets/7d8a0d31-52c2-4cd8-a2c6-2b9b6a8d0f4a/messages
```

Success `200`: returns an array of message objects.

Relevant errors: `401` for missing/unknown identity, `403` for a regular user identity, and `404` for a missing or differently assigned ticket.
