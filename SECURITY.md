# Security Model

Naeyla is a local-only personal assistant. It is not designed to be exposed to the internet. This document describes the security decisions made, the protections in place, and the known limitations.

## Threat Model

The primary threats considered are:

1. **A web page the user visits** attempting to call the local API (CSRF/CORS attack)
2. **The AI model** being tricked into executing harmful browser actions via prompt injection
3. **Secrets leaking** into git history, logs, or URLs
4. **A tampered local database** being used to execute arbitrary code on load

Threats that are explicitly out of scope (network-level attacks, physical access, OS-level privilege escalation) are outside what an application-layer defence can address.

---

## Authentication

All API endpoints require a `Authorization: Bearer <token>` header. Query-parameter auth (`?token=...`) is intentionally not supported, which prevents the token from appearing in server access logs, browser history, or referrer headers.

The token is a random 32-byte base64 string generated at setup time:

```bash
TOKEN=$(openssl rand -base64 32)
echo "NAEYLA_TOKEN=$TOKEN" > .env
echo "VITE_NAEYLA_TOKEN=$TOKEN" > tauri-app/naeyla-native/.env.local
```

Both `.env` and `.env.local` are git-ignored. The frontend will refuse to start if `VITE_NAEYLA_TOKEN` is not set (no silent fallback to a weak default).

### Token rotation

To rotate the token, regenerate it with the same command above and restart both the backend and frontend. No database migration is needed.

---

## CORS

The backend restricts cross-origin requests to the two origins the Tauri app uses:

```python
allow_origins=["http://localhost:1420", "tauri://localhost"]
allow_credentials=False
allow_methods=["GET", "POST"]
allow_headers=["Authorization", "Content-Type"]
```

This prevents any arbitrary web page a user visits from making authenticated requests to the local API. `allow_credentials` is `False` because authentication uses `Authorization` headers, not cookies.

---

## SSRF Protection

Browser navigation actions are validated before execution. The `validate_url()` function blocks:

- All loopback addresses (`127.0.0.0/8`, `::1`)
- All RFC-1918 private ranges (`10.x`, `172.16–31.x`, `192.168.x`)
- Link-local addresses (`169.254.0.0/16`), including the AWS/GCP/Azure metadata endpoint (`169.254.169.254`)
- Any IP address marked as reserved by Python's `ipaddress` module
- Non-HTTP(S) schemes

The check uses Python's `ipaddress` module to evaluate bare IP addresses, which covers decimal, hex, and octal representations as well as IPv6.

---

## Input Validation

`ChatRequest` enforces:

- **Message length**: maximum 8,000 characters; empty messages are rejected
- **Mode**: must be one of `companion`, `advisor`, or `guardian` — free-form strings are rejected

These checks happen at the Pydantic model layer before any handler code runs.

---

## Embedding Storage

Conversation embeddings are stored in SQLite as raw `float32` byte arrays using `numpy.tobytes()` / `numpy.frombuffer()`. Pickle serialisation is not used, removing the risk of arbitrary code execution from a tampered database file.

---

## Content Security Policy

The Tauri webview has a CSP that restricts resource loading to:

```
default-src 'self';
connect-src http://localhost:7861;
style-src 'self' 'unsafe-inline';
```

This prevents the frontend from loading scripts or making network requests to any destination other than the local backend.

---

## Action Allowlist

Browser actions executed by the model or the user are validated against an explicit allowlist:

```python
ALLOWED_ACTIONS = {"navigate", "click", "type", "scroll", "screenshot", "get_text", "search", "get_links"}
```

Any action type not in this set is blocked and logged. Navigate actions are additionally checked against the URL blocklist above.

---

## Error Handling

The `/chat` endpoint returns a generic `"Internal server error"` message on unexpected failures. Full exception details are written to `naeyla_audit.log` server-side but are never sent to the client.

---

## Audit Logging

All auth failures, blocked actions, and blocked URLs are written to `naeyla_audit.log` in the repo root. The log path is resolved to an absolute path at startup so it is always written to the same location regardless of the working directory.

---

## Known Limitations

### Prompt injection

The model's text output is parsed for `<|action|>` tokens, and matching actions are executed. A crafted input message could potentially trick the model into emitting a `navigate` or `type` action targeting content the user did not intend. Mitigations in place:

- Only whitelisted action types can execute
- Navigation is blocked to private/localhost addresses
- The model runs locally and is not connected to external services

Full elimination of prompt injection would require separating the action channel from the model's prose output, which is a planned architectural change.

### Local file trust

The SQLite memory database (`data/memory.db`) and model weights (`models/`) are loaded from the local filesystem without cryptographic verification. An attacker with write access to these paths and physical access to the machine could replace them. This is considered out of scope for a single-user local application.

### `macOSPrivateApi`

The Tauri window uses `transparent: true` and macOS vibrancy effects, which require `macOSPrivateApi: true`. This gives the webview access to additional macOS system APIs. It is required for the UI design and is documented here for transparency.
