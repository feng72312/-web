## ADDED Requirements

### Requirement: Composer listed as 大师B
The chat model catalog SHALL include `composer-2.5` with display tier `大师B` and provider `cursor`. DeepSeek models `deepseek-chat` (小师傅), `deepseek-reasoner` (大师), and `deepseek-v4-pro` (资深道长) SHALL remain listed when DeepSeek is enabled.

#### Scenario: Both providers enabled
- **WHEN** `/chat/status` is requested and both Cursor and DeepSeek keys are configured
- **THEN** `models` includes `composer-2.5` labeled `大师B` plus the three DeepSeek tiers

#### Scenario: Cursor disabled
- **WHEN** only DeepSeek is configured
- **THEN** `models` does not include `composer-2.5`

### Requirement: Default model prefers Composer
`default_model` and `/chat/status`.model SHALL be `composer-2.5` when Cursor is enabled, and `deepseek-chat` when only DeepSeek is enabled.

#### Scenario: Cursor available
- **WHEN** Cursor is enabled
- **THEN** `/chat/status` returns `model=composer-2.5`

#### Scenario: Cursor unavailable
- **WHEN** Cursor is disabled and DeepSeek is enabled
- **THEN** `/chat/status` returns `model=deepseek-chat` and interpret/chat still function

### Requirement: Quota recognizes 大师B
The quota service SHALL treat tier name `大师B` as a first-class daily bucket with the same numeric limit as other LAN free tiers (9999). Consuming a `composer-2.5` request SHALL debit `大师B`, not `大师` or `小师傅`.

#### Scenario: Consume Composer
- **WHEN** a device consumes one request with model `composer-2.5`
- **THEN** the `大师B` remaining count decreases by one

### Requirement: Frontend follows status default
Pages that load `/chat/status` SHALL set the selected model to `status.model` when that field is present, so a Composer default appears without requiring a manual switch.

#### Scenario: Fresh page
- **WHEN** a module page loads chat status while Cursor is enabled
- **THEN** the model selector value is `composer-2.5` / 大师B
