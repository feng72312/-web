from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "public" / "images" / "home"
MODULES = BASE / "modules"
SECTIONS = BASE / "sections"
MODULES.mkdir(parents=True, exist_ok=True)
SECTIONS.mkdir(parents=True, exist_ok=True)


def svg(w: int, h: int, body: str, label: str, *, show_label: bool = False) -> str:
    label_markup = ""
    if show_label:
        label_markup = (
            f'<text x="{w // 2}" y="{h - 36}" text-anchor="middle" '
            f'fill="#f8e6b8" font-family="serif" font-size="26" font-weight="700">{label}</text>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1a1420"/>
      <stop offset="100%" stop-color="#0e1118"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="42%" r="58%">
      <stop offset="0%" stop-color="#d9a441" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="#d9a441" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#glow)"/>
  {body}
  {label_markup}
</svg>"""


MODULE_ITEMS = {
    "01-bazi.svg": (
        "八字命理",
        '<circle cx="320" cy="200" r="78" fill="none" stroke="#f8e6b8" stroke-width="3"/>'
        '<path d="M320 122 C365 168 365 232 320 278 C275 232 275 168 320 122Z" fill="#8b2f2f"/>'
        '<path d="M320 122 C275 168 275 232 320 278 C365 232 365 168 320 122Z" fill="#f8e6b8"/>'
        '<circle cx="320" cy="200" r="10" fill="#d9a441"/>',
    ),
    "11-ziwei.svg": (
        "紫微斗数",
        '<circle cx="320" cy="170" r="90" fill="none" stroke="#c9a0ff" stroke-width="2" opacity="0.8"/>'
        + "".join(
            f'<circle cx="{180 + i * 35}" cy="{120 + (i % 3) * 30}" r="{4 + (i % 3)}" fill="#f8e6b8"/>'
            for i in range(12)
        ),
    ),
    "09-xingming.svg": (
        "星命占验",
        '<circle cx="220" cy="180" r="36" fill="#d9a441"/>'
        '<circle cx="320" cy="150" r="24" fill="#f8e6b8"/>'
        '<circle cx="410" cy="190" r="30" fill="#7ab8ff"/>'
        '<ellipse cx="320" cy="250" rx="180" ry="40" fill="none" stroke="#d9a441" stroke-width="2" opacity="0.5"/>',
    ),
    "02-liuyao.svg": (
        "六爻卜筮",
        "".join(
            f'<circle cx="{220 + i * 80}" cy="190" r="34" fill="none" stroke="#d9a441" stroke-width="3"/>'
            f'<text x="{220 + i * 80}" y="198" text-anchor="middle" fill="#f8e6b8" font-size="22">钱</text>'
            for i in range(3)
        ),
    ),
    "03-meihua.svg": (
        "梅花易数",
        "".join(
            f'<circle cx="{260 + i * 60}" cy="{160 + (i % 2) * 40}" r="18" fill="#f8b4c4" opacity="0.9"/>'
            f'<path d="M{260 + i * 60} 178 L{260 + i * 60} 240" stroke="#8b4a5c" stroke-width="4"/>'
            for i in range(5)
        ),
    ),
    "04-qimen.svg": (
        "奇门遁甲",
        "".join(
            f'<rect x="{170 + (i % 3) * 100}" y="{120 + (i // 3) * 70}" width="80" height="55" rx="8" '
            f'fill="none" stroke="#d9a441" stroke-width="2" opacity="0.85"/>'
            for i in range(9)
        ),
    ),
    "05-liuren.svg": (
        "大六壬",
        '<rect x="210" y="110" width="220" height="150" rx="12" fill="none" stroke="#d9a441" stroke-width="3"/>'
        '<line x1="240" y1="150" x2="400" y2="150" stroke="#f8e6b8" stroke-width="2" opacity="0.6"/>'
        '<line x1="240" y1="180" x2="380" y2="180" stroke="#f8e6b8" stroke-width="2" opacity="0.45"/>'
        '<line x1="240" y1="210" x2="360" y2="210" stroke="#f8e6b8" stroke-width="2" opacity="0.35"/>',
    ),
    "06-fengshui.svg": (
        "风水堪舆",
        '<polygon points="320,100 420,200 380,260 260,260 220,200" fill="none" stroke="#7dd87a" stroke-width="3"/>'
        '<rect x="270" y="200" width="100" height="70" fill="none" stroke="#d9a441" stroke-width="2"/>'
        '<circle cx="320" cy="235" r="16" fill="none" stroke="#f8e6b8" stroke-width="2"/>',
    ),
    "util-hepan.svg": (
        "合盘工具",
        '<circle cx="250" cy="190" r="50" fill="none" stroke="#f8e6b8" stroke-width="3"/>'
        '<circle cx="390" cy="190" r="50" fill="none" stroke="#f8e6b8" stroke-width="3"/>'
        '<path d="M300 190 H340" stroke="#d9a441" stroke-width="4"/>',
    ),
    "util-zhuge.svg": (
        "诸葛神数",
        '<rect x="230" y="120" width="24" height="160" rx="4" fill="#c9a66b"/>'
        '<rect x="270" y="120" width="24" height="160" rx="4" fill="#b89560"/>'
        '<rect x="310" y="120" width="24" height="160" rx="4" fill="#c9a66b"/>'
        '<rect x="350" y="120" width="24" height="160" rx="4" fill="#b89560"/>',
    ),
    "util-jiemeng.svg": (
        "周公解梦",
        '<circle cx="320" cy="170" r="55" fill="#f8e6b8" opacity="0.9"/>'
        '<path d="M180 250 Q320 180 460 250" fill="none" stroke="#7ab8ff" stroke-width="3" opacity="0.7"/>',
    ),
    "util-cewen.svg": (
        "测字",
        '<text x="320" y="210" text-anchor="middle" fill="#f8e6b8" font-family="serif" font-size="96" font-weight="700">字</text>',
    ),
    "util-naming.svg": (
        "起名",
        '<rect x="250" y="250" width="140" height="18" rx="4" fill="#c9a66b"/>'
        '<path d="M310 250 L310 130" stroke="#8b5a2b" stroke-width="8" stroke-linecap="round"/>'
        '<path d="M310 130 Q350 110 380 140" fill="none" stroke="#d9a441" stroke-width="3"/>',
    ),
    "util-name-analysis.svg": (
        "姓名分析",
        '<rect x="250" y="140" width="140" height="140" rx="12" fill="none" stroke="#d9a441" stroke-width="3"/>'
        '<text x="320" y="230" text-anchor="middle" fill="#8b2f2f" font-family="serif" font-size="72" font-weight="700">名</text>',
    ),
    "util-phone.svg": (
        "手机号分析",
        '<rect x="285" y="110" width="70" height="130" rx="14" fill="none" stroke="#d9a441" stroke-width="3"/>'
        '<circle cx="320" cy="220" r="8" fill="#f8e6b8"/>',
    ),
}

HERO_ITEMS = {
    "hero.svg": (
        "东方玄学天文馆",
        '<circle cx="320" cy="140" r="70" fill="none" stroke="#d9a441" stroke-width="2" opacity="0.7"/>'
        + "".join(
            f'<circle cx="{180 + i * 45}" cy="{90 + (i % 4) * 25}" r="{2 + (i % 2)}" fill="#f8e6b8" opacity="0.9"/>'
            for i in range(14)
        )
        + '<path d="M120 280 Q320 200 520 280" fill="none" stroke="#7ab8ff" stroke-width="2" opacity="0.5"/>',
    ),
}

MODULE_ITEMS["13-tarot.svg"] = (
    "塔罗牌阵",
    '<rect x="200" y="110" width="90" height="150" rx="8" fill="none" stroke="#d9a441" stroke-width="3"/>'
    '<rect x="275" y="95" width="90" height="150" rx="8" fill="none" stroke="#f8e6b8" stroke-width="3"/>'
    '<rect x="350" y="110" width="90" height="150" rx="8" fill="none" stroke="#d9a441" stroke-width="3"/>'
    '<circle cx="320" cy="175" r="22" fill="none" stroke="#c9a0ff" stroke-width="2"/>',
)

SECTION_ITEMS = {
    "chart.svg": (
        "命盘层",
        '<circle cx="320" cy="150" r="80" fill="none" stroke="#c9a0ff" stroke-width="2"/>'
        + "".join(
            f'<line x1="320" y1="150" x2="{320 + 70 * (1 if i % 2 else 0.7)}" y2="{150 - 60 + i * 12}" '
            f'stroke="#d9a441" stroke-width="2" opacity="0.6"/>'
            for i in range(8)
        ),
    ),
    "divination.svg": (
        "卜筮",
        '<path d="M200 250 L280 150 L360 250 L440 150" fill="none" stroke="#d9a441" stroke-width="4"/>'
        '<circle cx="280" cy="150" r="10" fill="#f8e6b8"/>'
        '<circle cx="440" cy="150" r="10" fill="#f8e6b8"/>',
    ),
    "environment.svg": (
        "环境关系",
        '<path d="M160 260 L320 120 L480 260 Z" fill="none" stroke="#7dd87a" stroke-width="3"/>'
        '<rect x="260" y="210" width="120" height="70" fill="none" stroke="#d9a441" stroke-width="2"/>',
    ),
    "utility.svg": (
        "实用专区",
        '<rect x="210" y="130" width="90" height="120" rx="8" fill="none" stroke="#d9a441" stroke-width="2"/>'
        '<rect x="340" y="130" width="90" height="120" rx="8" fill="none" stroke="#d9a441" stroke-width="2"/>'
        '<path d="M255 190 H385" stroke="#f8e6b8" stroke-width="3"/>',
    ),
}


def main() -> None:
    for filename, (label, body) in MODULE_ITEMS.items():
        (MODULES / filename).write_text(svg(640, 400, body, label, show_label=False), encoding="utf-8")
    for filename, (label, body) in SECTION_ITEMS.items():
        (SECTIONS / filename).write_text(svg(960, 320, body, label, show_label=True), encoding="utf-8")
    for filename, (label, body) in HERO_ITEMS.items():
        (BASE / filename).write_text(svg(1200, 480, body, label, show_label=True), encoding="utf-8")
    print(
        f"generated {len(MODULE_ITEMS)} module + {len(SECTION_ITEMS)} section + {len(HERO_ITEMS)} hero covers"
    )


if __name__ == "__main__":
    main()
