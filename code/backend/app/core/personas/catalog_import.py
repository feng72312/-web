from __future__ import annotations

import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


AWESOME_COMMIT = "1bc395977d5c04427229d0dc58a4abd74aaa21e7"
AWESOME_URL = "https://github.com/nuwa-skills/awesome-nuwa"

CATEGORY_DEFINITIONS = (
    ("chinese-philosophers", "中国哲学家"),
    ("western-philosophers", "西方哲学家"),
    ("scientists", "科学家"),
    ("business-leaders", "商业领袖"),
    ("chinese-entrepreneurs", "当代中国企业家"),
    ("investors", "投资大师"),
    ("technology-innovation", "科技与创新"),
    ("chinese-writers", "中国文学家"),
    ("western-writers", "西方作家"),
    ("psychologists", "心理学家"),
    ("political-leaders", "政治领袖"),
    ("military-strategy", "军事与战略"),
    ("art-design", "艺术与设计"),
    ("sports", "体育"),
    ("education", "教育"),
    ("economists", "经济学家"),
    ("spiritual-wisdom", "精神与智慧"),
    ("contemporary-thinkers", "当代思想者"),
)
CATEGORY_BY_LABEL = {label: category_id for category_id, label in CATEGORY_DEFINITIONS}

TABLE_ROW_RE = re.compile(
    r"^\|\s*\[([^]]+)]\((https://github\.com/[^)]+)\)\s*\|\s*([^|]+?)\s*\|"
)
COUNT_RE = re.compile(r"^- \[([^]]+)]\([^)]*\)\s*`(\d+)`\s*$")
TOTAL_RE = re.compile(r"共\s*\*\*(\d+)\*\*\s*位人物.*\*\*(\d+)\*\*\s*个领域")

ALLOWED_BLOBS = ("LICENSE", "LICENSE.md", "SKILL.md", "README.md")
REFERENCE_PATH_RE = re.compile(r"^references/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.md$")
MAX_BLOB_BYTES = 160_000
MAX_TOTAL_BYTES = 360_000

# Conservative by design: anything not explicitly listed is routed to public-framework mode.
HISTORICAL_IDS = {
    "kongzi", "laozi", "zhuangzi", "sunzi", "wangyangming", "zengguofan",
    "hanfeizi", "mozi", "xunzi", "zhuxi", "guiguzi", "zhugeliang", "sudongpo",
    "wangfuzhi", "socrates", "plato", "aristotle", "aurelius", "epictetus",
    "seneca", "kant", "nietzsche", "schopenhauer", "montaigne", "wittgenstein",
    "heraclitus", "foucault", "arendt", "beauvoir", "feynman", "einstein", "darwin",
    "newton", "turing", "curie", "tesla", "shannon", "vonneumann", "copernicus",
    "faraday", "davinci", "qianxuesen", "sagan", "drucker", "walton", "grove",
    "matsushita", "ford", "welch", "inamori", "webb", "zongqinghou", "bogle",
    "grahamben", "steve-jobs", "luxun", "hushi", "wangxiaobo", "linyutang",
    "qianzhongshu", "hemingway", "orwell", "tolstoy", "kafka", "borges",
    "freud", "jung", "adler", "frankl", "mao", "lincoln", "churchill", "mandela",
    "gandhi", "napoleon", "caocao", "hannibal", "caesar", "washington", "suntzu",
    "picasso", "vangogh", "miyazaki", "jobs", "montessori", "keynes", "hayek",
    "smith", "mises", "krishnamurti", "osho", "buddha", "jesus", "rumi",
}


class CatalogImportError(ValueError):
    pass


@dataclass(frozen=True)
class Candidate:
    id: str
    name: str
    category_id: str
    category_label: str
    themes: tuple[str, ...]
    repository: str
    owner: str
    repo: str


def _repo_parts(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if parsed.scheme != "https" or parsed.netloc != "github.com" or len(parts) != 2:
        raise CatalogImportError(f"unsupported repository URL: {url}")
    owner, repo = parts
    repo = repo.removesuffix(".git")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner + repo):
        raise CatalogImportError(f"unsafe repository URL: {url}")
    return owner, repo


def parse_awesome_readme(text: str) -> dict[str, object]:
    declared_total = None
    declared_categories = None
    declared_counts: dict[str, int] = {}
    candidates: list[Candidate] = []
    current_label: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        total_match = TOTAL_RE.search(line)
        if total_match:
            declared_total = int(total_match.group(1))
            declared_categories = int(total_match.group(2))
        count_match = COUNT_RE.match(line)
        if count_match and count_match.group(1) in CATEGORY_BY_LABEL:
            declared_counts[count_match.group(1)] = int(count_match.group(2))
        if line.startswith("## "):
            label = line[3:].strip()
            current_label = label if label in CATEGORY_BY_LABEL else None
            continue
        row_match = TABLE_ROW_RE.match(line)
        if not row_match:
            continue
        if current_label is None:
            raise CatalogImportError("persona table row appears outside a known category")
        name, repository, theme_text = row_match.groups()
        owner, repo = _repo_parts(repository)
        persona_id = repo.removesuffix("-skill").lower()
        themes = tuple(item.strip() for item in theme_text.split("/") if item.strip())
        if not themes:
            raise CatalogImportError(f"missing themes for {name}")
        candidates.append(Candidate(
            id=persona_id,
            name=name.strip(),
            category_id=CATEGORY_BY_LABEL[current_label],
            category_label=current_label,
            themes=themes,
            repository=repository,
            owner=owner,
            repo=repo,
        ))

    if len(declared_counts) != len(CATEGORY_DEFINITIONS):
        raise CatalogImportError("README category index is incomplete")
    if not candidates:
        raise CatalogImportError("README contains no persona rows")

    seen_repos: dict[str, list[str]] = {}
    seen_ids: dict[str, list[str]] = {}
    for item in candidates:
        seen_repos.setdefault(item.repository.lower(), []).append(item.name)
        seen_ids.setdefault(item.id, []).append(item.name)
    duplicate_repositories = {key: names for key, names in seen_repos.items() if len(names) > 1}
    duplicate_ids = {key: names for key, names in seen_ids.items() if len(names) > 1}
    if duplicate_ids:
        raise CatalogImportError(f"duplicate persona ids: {sorted(duplicate_ids)}")

    actual_counts = {
        label: sum(item.category_label == label for item in candidates)
        for _, label in CATEGORY_DEFINITIONS
    }
    count_drift = {
        label: {"declared": declared_counts[label], "actual": actual_counts[label]}
        for _, label in CATEGORY_DEFINITIONS
        if declared_counts[label] != actual_counts[label]
    }
    return {
        "declared_total": declared_total,
        "declared_categories": declared_categories,
        "declared_counts": declared_counts,
        "actual_counts": actual_counts,
        "count_drift": count_drift,
        "duplicate_repositories": duplicate_repositories,
        "candidates": candidates,
    }


def _run_git(args: list[str], cwd: Path | None = None) -> str:
    command = [
        "git", "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never",
        *args,
    ]
    result = subprocess.run(
        command, cwd=cwd, check=False, capture_output=True, text=True, timeout=90,
        env={"PATH": "/usr/bin:/bin", "GIT_TERMINAL_PROMPT": "0"},
    )
    if result.returncode:
        raise CatalogImportError(result.stderr.strip() or "git operation failed")
    return result.stdout.strip()


def audit_repository(candidate: Candidate, cache_root: Path) -> dict[str, object]:
    cache_root.mkdir(parents=True, exist_ok=True)
    repository_dir = cache_root / f"{candidate.owner}--{candidate.repo}.git"
    if not repository_dir.exists():
        _run_git(["clone", "--bare", "--filter=blob:none", "--depth=1", candidate.repository, str(repository_dir)])
        revision = "HEAD"
    else:
        _run_git(["fetch", "--depth=1", "origin", "HEAD"], cwd=repository_dir)
        revision = "FETCH_HEAD"
    commit = _run_git(["rev-parse", revision], cwd=repository_dir)
    blobs: dict[str, str] = {}
    total_bytes = 0
    tree_names = _run_git(["ls-tree", "-r", "--name-only", commit], cwd=repository_dir).splitlines()
    reference_names = [name for name in tree_names if REFERENCE_PATH_RE.fullmatch(name)][:40]
    for name in (*ALLOWED_BLOBS, *reference_names):
        try:
            content = _run_git(["show", f"{commit}:{name}"], cwd=repository_dir)
        except CatalogImportError:
            continue
        size = len(content.encode("utf-8"))
        if size > MAX_BLOB_BYTES:
            return {"status": "review_required", "reason": f"{name} exceeds size limit", "commit": commit}
        total_bytes += size
        blobs[name] = content
    if total_bytes > MAX_TOTAL_BYTES:
        return {"status": "review_required", "reason": "review documents exceed total size limit", "commit": commit}
    license_text = blobs.get("LICENSE") or blobs.get("LICENSE.md") or ""
    if "MIT License" not in license_text:
        return {"status": "review_required", "reason": "MIT license not verified", "commit": commit}
    skill = blobs.get("SKILL.md", "")
    if len(skill) < 200:
        return {"status": "review_required", "reason": "SKILL.md missing or too short", "commit": commit}
    return {
        "status": "ready",
        "reason": "MIT license and Skill documentation verified",
        "commit": commit,
        "license": "MIT",
        "reference_count": len(reference_names),
        "skill_excerpt": _safe_excerpt(skill),
    }


def _safe_excerpt(text: str) -> str:
    """Extract prose only; never carry commands, tools, frontmatter or code into runtime prompts."""
    lines: list[str] = []
    in_code = False
    in_frontmatter = text.lstrip().startswith("---")
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "---" and in_frontmatter:
            in_frontmatter = False
            continue
        if in_frontmatter:
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line or line.startswith(("$", "npx ", "npm ", "git ", "curl ")):
            continue
        if re.search(r"\b(tool|command|execute|install|安装|命令|脚本)\b", line, re.I):
            continue
        lines.append(line.lstrip("#>*- "))
        if sum(len(item) for item in lines) >= 4000:
            break
    return "\n".join(lines)[:4000]


def build_catalog(
    parsed: dict[str, object], audits: dict[str, dict[str, object]],
) -> dict[str, object]:
    candidates = parsed["candidates"]
    assert isinstance(candidates, list)
    records: list[dict[str, object]] = []
    for order, item in enumerate(candidates):
        assert isinstance(item, Candidate)
        audit = audits.get(item.repository, {"status": "review_required", "reason": "repository audit unavailable", "commit": ""})
        if item.id == "wangyangming" and audit["status"] != "ready":
            audit = {
                **audit, "status": "ready", "reason": "bundled Wang Yangming pack independently reviewed",
                "license": "MIT", "skill_excerpt": "",
            }
        historical = item.id in HISTORICAL_IDS
        mode = "historical_simulation" if historical else "public_framework"
        records.append({
            "id": "wang-yangming" if item.id == "wangyangming" else item.id,
            "name": item.name,
            "formalName": item.name,
            "categoryId": item.category_id,
            "categoryLabel": item.category_label,
            "categoryOrder": next(i for i, definition in enumerate(CATEGORY_DEFINITIONS) if definition[0] == item.category_id),
            "order": order,
            "themes": list(item.themes)[:12],
            "summary": f"以{item.name}公开作品与思想资料为线索，从{'、'.join(item.themes[:3])}等角度协助分析问题。",
            "lifeStatus": "historical" if historical else "unknown",
            "interactionMode": mode,
            "availability": audit["status"],
            "availabilityReason": audit["reason"],
            "upstream": {
                "name": f"{item.owner}/{item.repo}", "url": item.repository,
                "owner": item.owner, "commit": audit.get("commit", ""),
            },
            "license": {
                "name": audit.get("license", "Unverified"),
                "attribution": f"Derived from {item.owner}/{item.repo}; adapted with platform safety boundaries.",
                "sourceUrl": f"{item.repository}/blob/{audit.get('commit') or 'HEAD'}/LICENSE",
            },
            "skillExcerpt": audit.get("skill_excerpt", ""),
        })
    categories = [
        {
            "id": category_id, "label": label, "order": order,
            "count": sum(record["categoryId"] == category_id for record in records),
            "readyCount": sum(record["categoryId"] == category_id and record["availability"] == "ready" for record in records),
        }
        for order, (category_id, label) in enumerate(CATEGORY_DEFINITIONS)
    ]
    return {
        "schemaVersion": 1,
        "source": {"url": AWESOME_URL, "commit": AWESOME_COMMIT},
        "declaredTotal": parsed["declared_total"],
        "actualUniqueTotal": len({record["id"] for record in records}),
        "categories": categories,
        "personas": records,
    }


def diff_catalog(previous: dict[str, object] | None, current: dict[str, object]) -> dict[str, object]:
    old_records = previous.get("personas", []) if previous else []
    new_records = current.get("personas", [])
    old_by_repo = {item["upstream"]["url"]: item for item in old_records}
    new_by_repo = {item["upstream"]["url"]: item for item in new_records}
    added = sorted(new_by_repo.keys() - old_by_repo.keys())
    removed = sorted(old_by_repo.keys() - new_by_repo.keys())
    renamed = [
        {"repository": repo, "from": old_by_repo[repo]["name"], "to": new_by_repo[repo]["name"]}
        for repo in sorted(old_by_repo.keys() & new_by_repo.keys())
        if old_by_repo[repo]["name"] != new_by_repo[repo]["name"]
    ]
    moved = [
        {"repository": repo, "from": old_by_repo[repo]["categoryId"], "to": new_by_repo[repo]["categoryId"]}
        for repo in sorted(old_by_repo.keys() & new_by_repo.keys())
        if old_by_repo[repo]["categoryId"] != new_by_repo[repo]["categoryId"]
    ]
    return {"added": added, "removed": removed, "renamed": renamed, "moved": moved}


def audit_all(candidates: Iterable[Candidate], cache_root: Path, workers: int = 6) -> dict[str, dict[str, object]]:
    items = list(candidates)
    results: dict[str, dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=max(1, min(workers, 6))) as executor:
        future_map = {executor.submit(audit_repository, item, cache_root): item for item in items}
        for future in as_completed(future_map):
            item = future_map[future]
            try:
                results[item.repository] = future.result()
            except Exception as exc:  # every failure remains visible as a disabled catalog record
                results[item.repository] = {"status": "review_required", "reason": str(exc)[:300], "commit": ""}
    return results


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
