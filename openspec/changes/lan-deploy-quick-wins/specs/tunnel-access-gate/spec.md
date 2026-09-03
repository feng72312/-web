## ADDED Requirements

### Requirement: Tunnel-originated AI requests require an access code
When a request carries the `CF-Connecting-IP` header AND the access-code file configured by `settings.tunnel_access_code_file` exists with non-empty content, the backend SHALL reject requests to protected paths unless the `X-Access-Code` header equals the file content (compared in constant time). Protected paths are any path matching `/api/v1/(.*/)?interpret(/stream)?$`, any path under `/api/v1/chat/`, and `/api/v1/rag/search`. Rejection SHALL be HTTP 401 with body `{"detail":{"code":"access_code_required","message":"请输入访问口令"}}` and SHALL happen before any quota is consumed.

#### Scenario: Tunnel request without code
- **WHEN** a request to `/api/v1/interpret` has `CF-Connecting-IP: 1.2.3.4`, no `X-Access-Code`, and the code file contains `a1b2c3`
- **THEN** the response is 401 with `detail.code == "access_code_required"` and the caller's quota is unchanged

#### Scenario: Tunnel request with correct code
- **WHEN** the same request includes `X-Access-Code: a1b2c3`
- **THEN** the request proceeds to the normal handler

#### Scenario: Tunnel request with wrong code
- **WHEN** the same request includes `X-Access-Code: zzzzzz`
- **THEN** the response is 401 with `detail.code == "access_code_required"`

#### Scenario: LAN request is untouched
- **WHEN** a request to `/api/v1/interpret` has no `CF-Connecting-IP` header, regardless of the code file
- **THEN** the gate does not intervene and the normal handler runs

#### Scenario: No code file means gate is off
- **WHEN** the code file does not exist and a request carries `CF-Connecting-IP`
- **THEN** the gate does not intervene

#### Scenario: Unprotected paths pass
- **WHEN** a tunnel request without code targets `/api/v1/paipan` or `/api/v1/quota/status`
- **THEN** the response is not 401 from the gate

### Requirement: Code file changes take effect without restart
The gate SHALL re-read the code file when its mtime changes, so creating, editing or deleting the file changes behaviour for subsequent requests without restarting the backend.

#### Scenario: File removed while running
- **WHEN** the code file is deleted after the backend has served a gated request
- **THEN** the next tunnel request without a code is not rejected by the gate

### Requirement: Tunnel scripts manage the code lifecycle
`start-tunnel.sh` SHALL determine the code from `ZY_TUNNEL_ACCESS_CODE`, else from `logs/tunnel.code`, else generate a 6-hex-character code; SHALL write it to the backend code file and to `logs/tunnel.code`; and SHALL print both the public URL and the code. `stop-tunnel.sh` SHALL delete the backend code file. `start-all.sh` SHALL delete a stale backend code file when no tunnel process is running.

#### Scenario: Start prints URL and code
- **WHEN** `start-tunnel.sh` succeeds
- **THEN** stdout contains a line with the `https://*.trycloudflare.com` URL and a line `[tunnel] access code: <code>`, and the backend code file contains `<code>`

#### Scenario: Stop removes the code
- **WHEN** `stop-tunnel.sh` runs
- **THEN** the backend code file no longer exists and `logs/tunnel.code` still exists

#### Scenario: Code reuse
- **WHEN** `start-tunnel.sh` runs a second time without `ZY_TUNNEL_ACCESS_CODE`
- **THEN** the printed code equals the previous run's code

### Requirement: Frontend prompts for the code and retries once
Every AI request path in the frontend (module interpret JSON calls, bazi interpret stream, chat stream and chat JSON calls) SHALL send `X-Access-Code` from `localStorage["zy_access_code"]` when present. On a 401 whose body has `detail.code === "access_code_required"`, the frontend SHALL open a modal asking for the code, persist the entered code to localStorage, and retry the original request exactly once. If the user cancels, the original error is surfaced to the caller.

#### Scenario: First tunnel use
- **WHEN** a tunnel visitor without a stored code clicks 解读
- **THEN** a modal titled "输入访问口令" appears; after entering the correct code the interpretation proceeds without a second click

#### Scenario: Wrong code entered
- **WHEN** the visitor enters a wrong code
- **THEN** the retry returns 401 again and the modal reopens with an inline message "口令不正确"

#### Scenario: Cancel
- **WHEN** the visitor dismisses the modal
- **THEN** the interpret button returns to idle with error text "需要访问口令" and no further request is sent

#### Scenario: LAN user never sees the modal
- **WHEN** a LAN user (no `CF-Connecting-IP`) uses any AI feature while the tunnel is active
- **THEN** no modal appears

### Requirement: Access-code file is ignored by git
`code/backend/data/tunnel_access_code.txt` and `code/logs/tunnel.code` SHALL be matched by `.gitignore`.

#### Scenario: Git status clean
- **WHEN** the tunnel is started and `git status --short` is run
- **THEN** neither file appears as untracked
