## ADDED Requirements

### Requirement: Admin password has no default
`Settings.admin_password` SHALL default to `None` and be populated only from the `ADMIN_PASSWORD` environment variable or `.env`.

#### Scenario: Source audit
- **WHEN** `code/backend/app/config.py` is inspected
- **THEN** no literal password string is assigned to `admin_password`

### Requirement: Admin endpoints are disabled when no password is configured
When `settings.admin_password` is `None` or empty, every admin dependency SHALL raise HTTP 403 with detail `"admin disabled: set ADMIN_PASSWORD"`. When configured, the comparison SHALL use `secrets.compare_digest`.

#### Scenario: Unconfigured
- **WHEN** `ADMIN_PASSWORD` is unset and a request hits an admin route with any credentials
- **THEN** the response is 403 with the specified detail

#### Scenario: Configured and correct
- **WHEN** `ADMIN_PASSWORD=abc` and a request supplies `abc`
- **THEN** the admin route executes

#### Scenario: Configured and wrong
- **WHEN** `ADMIN_PASSWORD=abc` and a request supplies `abd`
- **THEN** the response is the same status and detail as today's wrong-password path

### Requirement: Deployment env carries the password
The server's `code/backend/.env` SHALL contain a non-empty `ADMIN_PASSWORD` after this change is applied, and `tests/test_admin.py` SHALL inject the password via monkeypatch rather than relying on a default.

#### Scenario: Tests pass without default
- **WHEN** `pytest tests/test_admin.py` runs with `ADMIN_PASSWORD` unset in the environment
- **THEN** all tests pass
