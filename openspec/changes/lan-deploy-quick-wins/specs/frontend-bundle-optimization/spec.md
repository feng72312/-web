## ADDED Requirements

### Requirement: Production bundle is minified and split by vendor
The frontend production build SHALL emit minified JavaScript and SHALL split third-party dependencies into separate vendor chunks (react, antd, echarts, framer-motion, assistant-ui) so that no single JavaScript asset exceeds 1.5MB uncompressed.

#### Scenario: Build output size
- **WHEN** `npm run build` completes in `code/frontend`
- **THEN** every file under `dist/assets/*.js` is smaller than 1.5MB and the total of all `dist/assets/*.js` is less than 2.5MB

#### Scenario: Minification enabled
- **WHEN** the built `dist/assets/index-*.js` is inspected
- **THEN** it contains no multi-line indented source formatting (i.e. it is minified) and `vite.config.ts` does not set `build.minify` to `false`

### Requirement: Module tabs load on demand
The `ModulesPage` SHALL load each divination module tab (bazi, liuyao, meihua, qimen, liuren, fengshui, xingming, ziwei, utils, tarot) through `React.lazy` so that module code is fetched only when that module is first opened.

#### Scenario: Initial load excludes module code
- **WHEN** the home page is loaded in a browser with the network panel open
- **THEN** no chunk for `TarotTab`, `ZiweiTab` or `LiuyaoTab` is requested until the corresponding module is opened

#### Scenario: Opening a module shows a fallback then content
- **WHEN** a user opens the bazi module for the first time
- **THEN** a skeleton placeholder is shown while the chunk loads, and the bazi form renders once loaded with no console error

### Requirement: Application still functions after minification
All existing user flows SHALL work identically after minification is enabled.

#### Scenario: Smoke flow after build
- **WHEN** the built app is served via `npm run preview` and a user performs home → bazi → 排盘 → AI 解读 → AI 对话
- **THEN** each step completes without JavaScript runtime errors in the browser console
