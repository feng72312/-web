## ADDED Requirements

### Requirement: Streaming endpoint emits a defined SSE event protocol
`POST /api/v1/interpret/stream` SHALL respond with `text/event-stream` where every frame is `data: <json>\n\n` and `<json>.type` is one of `stage`, `delta`, `done`, `error`. `stage` and `delta` MUST carry `text`; `done` MUST carry `chart`, `sections` and `interpretation`; `error` MUST carry `message`.

#### Scenario: Successful stream
- **WHEN** a client posts a valid non-fusion `InterpretRequest` and DeepSeek is configured
- **THEN** the client receives at least one `stage` event, one or more `delta` events, and exactly one terminal `done` event, in that order

#### Scenario: Upstream failure mid-stream
- **WHEN** the LLM provider raises after some `delta` events were sent
- **THEN** the stream ends with a single `error` event whose `message` is non-empty and no `done` event is sent

### Requirement: Streamed final payload matches the non-streaming payload
The `interpretation` object in the `done` event SHALL be produced by the same finalization code as `POST /api/v1/interpret`, so that for the same request the two responses have identical keys and identical values for every key except `summary`, `summaryPlain`, `summaryProfessional`, `agentId` and `segments`.

#### Scenario: Key parity
- **WHEN** the same chart request is sent to `/interpret` and `/interpret/stream` (with the LLM stubbed to return fixed text)
- **THEN** `done.interpretation` contains `judgement`, `ruleIdRefs`, `tieredEvidence`, `tieredEvidenceSummary`, `knowledgeEvidence`, `confidenceBand`, `segmentStats` and the values of `judgement`, `tieredEvidence`, `ruleIdRefs` equal those from `/interpret`

### Requirement: Streaming shares the quota and session semantics of non-streaming
The streaming endpoint SHALL consume one interpret quota unit per call through the same dependency as `/interpret`, and SHALL create a fresh chat session bootstrapped with the interpret prompt (not reuse a session bound to the chart) so follow-up chat context matches the non-streaming behaviour.

#### Scenario: Quota consumed once
- **WHEN** a client calls `/interpret/stream` once
- **THEN** the caller's remaining quota decreases by exactly one regardless of how many `delta` events were emitted

#### Scenario: Fusion rejected
- **WHEN** the request has `fusion: true`
- **THEN** the endpoint responds 400 before consuming any tokens from the LLM

### Requirement: Bazi frontend renders the interpretation incrementally with fallback
The bazi tab SHALL call the streaming endpoint for AI interpretation, display `stage` text as progress, append `delta` text to the visible summary as it arrives, and on `done` apply the final interpretation exactly as it does today for the non-streaming response. If the stream request fails before the first `delta` (or the request is a fusion request), the tab SHALL fall back to the non-streaming `fetchInterpret`.

#### Scenario: Text appears before completion
- **WHEN** a user clicks 解读 and the backend streams
- **THEN** partial interpretation text is visible in the summary area within 3 seconds of the first `delta`, before the request completes

#### Scenario: Fallback when streaming unavailable
- **WHEN** `/interpret/stream` returns 404 (chat not configured)
- **THEN** the tab transparently issues `/interpret` and shows the complete result with no user-visible error

#### Scenario: Error after partial output
- **WHEN** an `error` event arrives after some text was shown
- **THEN** the partial text remains, an error message is shown, and no automatic second request is made

### Requirement: SSE client logic is shared
The frontend SHALL implement one SSE reader utility used by both the chat stream and the interpret stream.

#### Scenario: Single implementation
- **WHEN** the codebase is searched for `getReader()` under `src/services`
- **THEN** exactly one SSE frame-parsing implementation exists and both `chatApi.ts` and `api.ts` import it
