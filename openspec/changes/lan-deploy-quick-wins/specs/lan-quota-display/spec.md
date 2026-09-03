## ADDED Requirements

### Requirement: Quota bar shows remaining count only
The `QuotaBar` component SHALL display today's remaining AI count from `/quota/status` and SHALL NOT render a redeem-key button, redeem panel, pricing text, or any persistence warning.

#### Scenario: Default render
- **WHEN** the app loads on a LAN host
- **THEN** the header shows text of the form "今日 AI 剩余 N 次" and the strings "兑换秘钥", "人工付款", "服务端数据尚未持久化" do not appear anywhere in the DOM

#### Scenario: Status endpoint unavailable
- **WHEN** `/quota/status` fails
- **THEN** the quota bar renders nothing (no error text) and the rest of the header is unaffected

### Requirement: Quota bar does not call the persistence probe
The frontend SHALL NOT request `/api/v1/quota/persistence`.

#### Scenario: Network audit
- **WHEN** the app is loaded and left idle for 6 minutes
- **THEN** no request to `/quota/persistence` is observed, and `/quota/status` is requested at most twice (initial + one refresh)

### Requirement: Quota error messages do not reference login or redeem keys
`parseApiErrorMessage` SHALL map HTTP 402 to a message that tells the user the daily limit is reached without mentioning keys or payment, and SHALL NOT map HTTP 401 to a login prompt.

#### Scenario: 402 message
- **WHEN** an AI request returns 402
- **THEN** the shown message is "今日 AI 次数已用完, 明日再试"

#### Scenario: 401 without access-code detail
- **WHEN** a request returns 401 whose body lacks `detail.code === "access_code_required"`
- **THEN** the shown message is the server's `detail` text or "请求未授权", never "请先登录"

### Requirement: Backend quota APIs are retained
The backend `/quota/status`, `/quota/persistence`, `/quota/redeem` endpoints and SQLite storage SHALL remain functional and covered by existing tests.

#### Scenario: Existing tests still pass
- **WHEN** `pytest tests/test_quota.py` runs
- **THEN** all tests pass without modification beyond this change's scope
