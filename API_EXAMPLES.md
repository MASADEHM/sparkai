# SparkAI API Endpoints - Usage Examples

## Base URL
- Local: `http://127.0.0.1:8000`
- Production: `https://your-backend-url.azurecontainerapps.io`

## Authentication

All endpoints except `GET /health` require HTTP Basic auth with the `API_USERNAME` / `API_PASSWORD`
set in the backend's environment. Missing or wrong credentials return `401`; if the backend has no
credentials configured it returns `503`.

Browser clients must send the `Authorization` header explicitly (CORS does not allow ambient credentials).
Set `CORS_ORIGINS=https://a.com,https://b.com` on the backend to restrict which origins may call it (default `*`).

---

## 1. Health Check

**Endpoint:** `GET /health` (no auth)

**Response:**
```json
{"status": "ok"}
```

---

## 2. Chat Endpoint

**Endpoint:** `POST /chat`

**Description:** Main conversational chat endpoint with thread-based history. History is stored in
SQLite (`CHECKPOINT_DB`, default `checkpoints.sqlite`) and survives restarts.

Before the assistant will search company documents, search the web, or send email, the user must verify
their email: the assistant emails a 6-digit code (valid 5 minutes) and the user types it back into the chat.

**Request Body:**
```json
{
  "messages": ["Hello, what can you help me with?"],
  "thread_id": "unique-thread-id-123"
}
```

**Response:**
```json
"Hello! Please provide your email address so I can verify you."
```

---

## 3. Trade Name Validation

**Endpoint:** `POST /tradename`

**Description:** Validates a trade name against UAE regulations. The `has*` flags are informational only;
`valid` and `remarks` reflect the actual rule checks.

**Request Body:**
```json
{
  "name": "Dubai Tech Solutions"
}
```

**Response:**
```json
{
  "hasNumber": false,
  "hasGulf": true,
  "hasRegionName": false,
  "hasArabizedName": false,
  "hasTrademark": false,
  "hasAbbreviation": false,
  "arabicEquivalentName": "دبي للحلول التقنية",
  "valid": true,
  "remarks": ""
}
```

---

## Testing the API

### Using cURL

```bash
curl -X POST "http://127.0.0.1:8000/tradename" \
  -u "$API_USERNAME:$API_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '{"name": "Al Saqer Contracting"}'
```

### Using Python

```python
import os, requests

response = requests.post(
    "http://127.0.0.1:8000/tradename",
    json={"name": "Al Saqer Contracting"},
    auth=(os.environ["API_USERNAME"], os.environ["API_PASSWORD"]),
)
print(response.json())
```

---

## Error Responses

**401 Unauthorized:**
```json
{"detail": "Invalid username or password"}
```

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {"type": "missing", "loc": ["body", "name"], "msg": "Field required", "input": {}}
  ]
}
```

**503 Service Unavailable:**
```json
{"detail": "API authentication is not configured"}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider implementing rate limiting based on your Azure OpenAI quota.
