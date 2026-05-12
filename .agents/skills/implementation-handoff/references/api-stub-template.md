# API and Data Stub Template

Use API stubs only as alignment drafts unless the repository has inspected API conventions.

```http
POST /api/[resources]

Request
{
  "field": "value"
}

Response 201
{
  "id": "res_123",
  "status": "pending"
}
```

```http
PATCH /api/[resources]/{id}

Request
{
  "field": "updated value"
}

Response 200
{
  "id": "res_123",
  "status": "pending"
}
```

```http
POST /api/[resources]/{id}/[action]

Request
{
  "action": "approve",
  "reason": ""
}

Response 200
{
  "id": "res_123",
  "status": "approved"
}
```

Include:

- Idempotency requirement for create/payment/order flows.
- Backend permission validation for sensitive actions.
- Error codes for validation failure, permission failure, state conflict, duplicate submission, and external dependency failure.
- Audit logs for admin, finance, moderation, or destructive actions.
