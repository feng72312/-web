## ADDED Requirements

### Requirement: Strip agent protocol from complete replies
Complete assistant text SHALL pass through `strip_agent_protocol` before existing footer sanitization. The stripper MUST remove whole lines matching `[MODE: …]` and MUST remove leading meta-research paragraphs that mention combining prior chart material or looking up persona packs / related materials. Body text after the protocol prefix MUST be kept. A lone word such as 研究 inside the body MUST NOT be removed. If stripping leaves no text, the result MUST be empty.

#### Scenario: Dual mode tags and lookup preamble
- **WHEN** the model returns two `[MODE: RESEARCH]` lines plus a paragraph about looking up 老子 in the persona pack, then a body starting with 我是李耳
- **THEN** the sanitized text starts at 我是李耳 and contains no `[MODE:`

#### Scenario: Body mentions research
- **WHEN** a complete reply has no mode tags and includes the word 研究 in the persona answer
- **THEN** that word remains in the sanitized text

### Requirement: Stream only cleaned increments
Cursor chat stream SHALL accumulate raw chunks, apply protocol stripping to the accumulated text, and yield only the increment versus the previously emitted cleaned text. Footer stripping MUST wait until the run completes. The text persisted for the session MUST be the cleaned full text.

#### Scenario: Protocol prefix then body
- **WHEN** early chunks are only `[MODE: RESEARCH]` and a lookup sentence, then later chunks add 我是李耳
- **THEN** SSE deltas do not include the mode tag, and the first visible delta starts at the body

### Requirement: Wrap without default chart homework
Cursor message wrapping SHALL tell the model to answer the user directly, forbid mode tags / research process / system notes, combine prior context when it exists, and avoid repeating ready-made openings. The default wrap MUST NOT say 请结合上文命盘资料.

#### Scenario: Persona who-am-I
- **WHEN** a persona session wraps 我是谁 with a bootstrap and no foreign chart transcript
- **THEN** the wrap instruction does not contain 请结合上文命盘资料
