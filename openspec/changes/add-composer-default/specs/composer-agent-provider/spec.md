## ADDED Requirements

### Requirement: Resident Cursor SDK bridge
The backend SHALL start one `cursor-sdk-bridge` (via `AsyncClient.launch_bridge` or equivalent) during application lifespan when `BAZI_CURSOR_API_KEY` is non-empty, keep that client for the process lifetime, and close it on shutdown. The backend MUST NOT launch a new bridge per interpret or chat request.

#### Scenario: Key present
- **WHEN** the backend starts with a non-empty Cursor API key
- **THEN** `/chat/status` reports `cursorEnabled=true` and a single bridge remains usable for subsequent chat calls

#### Scenario: Key absent
- **WHEN** the backend starts with an empty Cursor API key
- **THEN** no bridge process is started and `/chat/status` reports `cursorEnabled=false`

#### Scenario: Per-request isolation
- **WHEN** two interpret requests run while the key is configured
- **THEN** both reuse the same lifespan client and do not spawn additional `cursor-sdk-bridge` processes

### Requirement: Isolated local workspace
Composer local agents SHALL use a dedicated empty workspace directory under the backend data path, not the ZY repository root. MCP servers MUST NOT be registered. Local setting sources MUST remain empty.

#### Scenario: Workspace path
- **WHEN** a Composer agent is created
- **THEN** its local `cwd` is the isolated composer workspace directory

### Requirement: Standard Composer 2.5 without Fast
When the selected model is `composer-2.5`, the provider SHALL call Cursor with model id `composer-2.5` and MUST NOT enable the Fast parameter.

#### Scenario: Model id
- **WHEN** the orchestrator resolves model `composer-2.5`
- **THEN** the Cursor agent is created or resumed with id `composer-2.5` and without Fast

### Requirement: Text-only stream and session bind
Composer send and interpret paths SHALL stream only assistant text chunks into the existing chat/interpret SSE `delta` events, call `wait()` for a terminal result, bind the Cursor agent id to the chat session, and map SDK failures to the existing agent error path.

#### Scenario: Stream text
- **WHEN** a user sends a Composer chat or interpret stream
- **THEN** SSE `delta` events contain assistant text only and a terminal `done` or `error` follows

#### Scenario: Follow-up
- **WHEN** the same session sends a second Composer message
- **THEN** the provider resumes or reuses the bound agent instead of treating it as an unrelated one-shot prompt
