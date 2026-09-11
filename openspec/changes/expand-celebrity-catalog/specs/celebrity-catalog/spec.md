## ADDED Requirements

### Requirement: Complete upstream catalog snapshot
The system SHALL maintain a versioned local snapshot of every unique person entry parsed from a pinned awesome-nuwa revision, including its category, themes, upstream repository, owner, and source revision. The import process MUST report declared-count, parsed-count, duplicate, missing-repository, and category-count differences.

#### Scenario: Import current awesome-nuwa revision
- **WHEN** an operator imports a pinned awesome-nuwa revision
- **THEN** every unique person table row is represented in the local snapshot
- **AND** an audit report records the actual person and category counts

#### Scenario: Upstream count drifts
- **WHEN** the README summary count differs from the parsed unique entries
- **THEN** the import reports the difference and does not silently discard or invent people

### Requirement: Safe and licensed offline ingestion
The importer MUST treat every linked repository as untrusted input, MUST read only approved documentation and license paths within configured size limits, and MUST NOT execute upstream code, scripts, commands, hooks, or Skill tool instructions. A person SHALL be dialogue-ready only when its upstream revision and compatible license are recorded.

#### Scenario: Repository passes audit
- **WHEN** a repository contains an accepted license and all required source files within limits
- **THEN** the generated record contains its immutable revision, attribution, license, and review evidence

#### Scenario: Repository has missing or incompatible license
- **WHEN** the importer cannot verify a compatible license
- **THEN** the person remains visible in the catalog with `review_required` or `unavailable` status
- **AND** the system refuses to initialize a dialogue for that person

#### Scenario: Repository contains executable instructions
- **WHEN** an upstream Skill references scripts, commands, hooks, or tools
- **THEN** the importer stores none of those executable behaviors in the runtime person pack

### Requirement: Stable category taxonomy and discovery
The catalog SHALL expose stable category IDs, Chinese category labels, upstream ordering, dynamic counts, person themes, and availability counts. Users SHALL be able to search by Chinese or Latin name and theme, filter by category and availability, and clear all filters.

#### Scenario: Browse a category
- **WHEN** a user selects “科学家”
- **THEN** the catalog shows only people whose primary category is “科学家”
- **AND** the visible count matches the filtered result

#### Scenario: Search across categories
- **WHEN** a user searches for a name or theme such as “第一性原理”
- **THEN** matching people from all categories are returned without loading every person detail

#### Scenario: No results
- **WHEN** no person matches the active search and filters
- **THEN** the interface shows a clear empty state and a control to reset filters

### Requirement: Lifecycle-aware identity modes
Every person record MUST have a server-controlled life status and interaction mode. Deceased people MAY use `historical_simulation`; living or uncertain people MUST use `public_framework` or be unavailable. Client input MUST NOT change or elevate the interaction mode.

#### Scenario: Start a historical dialogue
- **WHEN** a dialogue-ready deceased person is selected
- **THEN** the bootstrap permits a disclosed first-person historical thought simulation
- **AND** it preserves source and quotation boundaries

#### Scenario: Start a living-person dialogue
- **WHEN** a dialogue-ready living person is selected
- **THEN** the bootstrap describes an AI analysis based on that person's public thought framework
- **AND** it forbids claiming to be the person, private knowledge, current endorsement, or unverified real-time views

#### Scenario: Client forges interaction mode
- **WHEN** a client submits a more permissive life status or interaction mode during initialization
- **THEN** the server ignores it and uses the reviewed catalog record

### Requirement: Catalog availability and API compatibility
The public API SHALL return category and availability metadata for catalog queries and SHALL keep the existing person detail and person chat initialization contracts compatible. A disabled catalog record MUST return a structured refusal reason rather than creating a session.

#### Scenario: Existing Wang Yangming client
- **WHEN** an existing client requests `wang-yangming` through the current detail and initialization endpoints
- **THEN** it continues to receive a valid detail and chat session without migration

#### Scenario: Query catalog page
- **WHEN** a client requests people with category, query, availability, offset, or limit parameters
- **THEN** the response includes filtered items, total count, category metadata, and stable ordering

#### Scenario: Initialize unavailable person
- **WHEN** a client requests dialogue initialization for a person that is not `ready`
- **THEN** the server refuses with a structured status and does not create session metadata

### Requirement: Scalable classified person hall
The person hall SHALL present the full catalog with category navigation, search, filters, count feedback, visible identity mode, availability status, and accessible person cards. It MUST remain usable at 390px and wide desktop viewports without whole-page horizontal overflow.

#### Scenario: Browse full catalog on desktop
- **WHEN** a user opens the person hall on a wide viewport
- **THEN** category navigation, search controls, grouped or paged cards, and result counts are visible and keyboard operable

#### Scenario: Browse full catalog on mobile
- **WHEN** a user opens the person hall at 390px
- **THEN** filters remain reachable, category navigation can scroll within its own region, and the page has no horizontal overflow

#### Scenario: Open reviewed and unreviewed people
- **WHEN** a user opens a ready person
- **THEN** the detail offers dialogue and shows sources and identity mode
- **WHEN** a user opens an unreviewed person
- **THEN** the detail explains its status and provides the upstream source without an enabled dialogue button

### Requirement: Attribution and update auditability
Every catalog person SHALL expose upstream repository attribution and review status. Every dialogue-ready person SHALL expose license and source information. Catalog updates MUST produce a human-readable diff of added, removed, moved, renamed, and changed-upstream entries before production snapshot replacement.

#### Scenario: Inspect person attribution
- **WHEN** a user opens a person detail
- **THEN** the interface shows the upstream repository, license when verified, and whether the mode is historical simulation or public framework analysis

#### Scenario: Review an upstream update
- **WHEN** an operator imports a newer awesome-nuwa revision
- **THEN** the audit output lists category moves, additions, removals, repository changes, and review-state changes before deployment
