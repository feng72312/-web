## ADDED Requirements

### Requirement: Wuxing distribution bars are filled with element colors
In the bazi report header, each `.bazi-report-wuxing-fill` bar SHALL have a non-transparent background color mapped to its element (`wx-wood` → `--wood`, `wx-fire` → `--fire`, `wx-earth` → `--earth`, `wx-metal` → `--metal`, `wx-water` → `--water`) in both light and dark themes.

#### Scenario: Bars visible for non-zero counts
- **WHEN** a chart with 金 count 3 and 木 count 0 is rendered
- **THEN** the 金 bar has computed `background-color` different from `rgba(0, 0, 0, 0)` and width > 0, and the 木 bar has width 0

#### Scenario: Colors follow theme variables
- **WHEN** the theme is switched to dark
- **THEN** each bar's computed background equals the corresponding `--wood/--fire/--earth/--metal/--water` variable value of the dark theme

### Requirement: Detail tables respect the active theme
`.detail-table` rows, row labels, head cells and alternating rows SHALL take their background and text colors from CSS variables that are defined for both `:root` and `:root[data-theme="dark"]`; no hardcoded hex background MAY remain in `chart-detail.css` for these selectors.

#### Scenario: Dark theme pillar table
- **WHEN** the bazi 四柱详盘 table is viewed in dark theme
- **THEN** the 天干 / 地支 / 藏干 cells have a dark background and the 藏干 十神 labels have a contrast ratio of at least 4.5:1 against that background

#### Scenario: Light theme unchanged
- **WHEN** the same table is viewed in light theme
- **THEN** the alternating row background is visually equivalent to the current `#f7f3ec` and the row label background to `#f0ebe3`

#### Scenario: Other modules inherit the fix
- **WHEN** the ziwei or liuyao detail table is viewed in dark theme
- **THEN** no cell renders with a light hardcoded background
