"""Render the guide's engineering diagrams as portable PNG and editable SVG.

Run: python3 code/docs/assets/project-guide/render_diagrams.py
Requires Pillow and a Chinese font; no application services are changed.
"""
from pathlib import Path
from html import escape
from math import atan2, cos, sin

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
INK, MUTED, RED, GREEN = "#292D32", "#626873", "#973F35", "#316B66"
BG, LINE = "#F7F4ED", "#B8B8B1"


class Diagram:
    def __init__(self, title, subtitle):
        self.im = Image.new("RGB", (1600, 940), BG)
        self.draw = ImageDraw.Draw(self.im)
        self.svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="940" viewBox="0 0 1600 940">', f'<rect width="1600" height="940" fill="{BG}"/>']
        self.text(60, 40, title, 38, INK)
        self.text(60, 102, subtitle, 21, MUTED)

    def text(self, x, y, text, size=23, color=INK):
        font = ImageFont.truetype(FONT, size)
        self.draw.text((x, y), text, font=font, fill=color)
        self.svg.append(f'<text x="{x}" y="{y + size}" font-family="Noto Sans CJK SC, sans-serif" font-size="{size}" fill="{color}">{escape(text)}</text>')

    def box(self, x, y, w, h, title, lines, accent=GREEN):
        self.draw.rounded_rectangle((x, y, x+w, y+h), 14, fill="white", outline=LINE, width=2)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="white" stroke="{LINE}" stroke-width="2"/>')
        self.text(x+24, y+17, title, 26, accent)
        for i, line in enumerate(lines):
            self.text(x+24, y+62+i*34, line, 21)

    def arrow(self, points, label=None, label_at=None, color=MUTED):
        self.draw.line(points, fill=color, width=3)
        pts = " ".join(f"{x},{y}" for x,y in points)
        self.svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>')
        x,y = points[-1]
        px,py = points[-2]
        a = atan2(y-py, x-px)
        head = [(x,y),(x-13*cos(a-.45),y-13*sin(a-.45)),(x-13*cos(a+.45),y-13*sin(a+.45))]
        self.draw.polygon(head, fill=color)
        self.svg.append(f'<polygon points="{" ".join(f"{px},{py}" for px,py in head)}" fill="{color}"/>')
        if label:
            self.text(*label_at, label, 19, color)

    def save(self, name, note):
        self.text(60, 874, note, 19, MUTED)
        self.im.save(OUT / f"{name}.png")
        (OUT / f"{name}.svg").write_text("\n".join(self.svg+["</svg>"]), encoding="utf-8")


def architecture():
    d = Diagram("紫云平台 · 整体架构", "浏览器呈现与交互 / 本机业务计算与检索 / 外部 AI 推理服务")
    d.box(60,190,420,180,"01  浏览器 · React + TypeScript",["首页 / 术数工作台 / 人物 / AI 顾问","表单 → API → 图表、证据、流式文本","档案与报告：浏览器本地存储"])
    d.box(590,190,420,180,"02  Nginx · 8080",["dist 静态资源 + SPA 回退","/api/ 反向代理到 8002","关闭代理缓冲，透传 SSE"])
    d.box(1120,190,420,180,"03  外网访问入口",["Cloudflare Quick Tunnel","外网 HTTPS → 本机 8080","局域网可直接访问 8080"],RED)
    d.box(590,465,420,195,"04  FastAPI · 8002",["排盘引擎 → 规则判定 → 解读编排","人物包 / 会话 / 配额 / 统计","SQLite 持久数据 + 内存聊天状态"])
    d.box(60,465,420,195,"05  独立 RAG · 8100",["中文向量召回 + CrossEncoder 重排","Chroma 文本片段与来源元数据","本机 GPU 加速 embedding / rerank"])
    d.box(1120,465,420,195,"06  外部 AI 服务",["Cursor SDK bridge → Composer","httpx → DeepSeek API","本机运行 bridge ≠ 本机训练大模型"],RED)
    d.box(590,727,420,105,"数据资产",["典籍原文 / JSONL 知识节点 / 人物目录"])
    d.arrow([(480,280),(590,280)])
    d.arrow([(1120,280),(1010,280)])
    d.arrow([(800,370),(800,465)],"同源 API",(817,401))
    d.arrow([(590,560),(480,560)])
    d.arrow([(1010,560),(1120,560)])
    d.arrow([(800,727),(800,660)])
    d.save("01-architecture","箭头表示主要调用或数据供给方向；API 响应和流式文本沿调用链返回。")


def bazi():
    d = Diagram("一次八字解读 · 数据如何逐步形成", "基础盘面、规则结论、检索证据和 AI 文字属于不同层次")
    rows = [
        (60,190,"1  出生信息",["公历 / 农历、年月日时、性别","Pydantic 校验请求字段"]),
        (590,190,"2  PaipanEngine",["历法转换 → 四柱 / 藏干 / 十神","五行计数 / 大运 / 盘面细节"]),
        (1120,190,"3  AnalysisRegistry",["summary / wuxing / shishen / dayun","输出统一 sections 展示数据"]),
        (1120,465,"4  BaziJudgementChain",["月令、调候、格局等 Judge","规则仲裁 + 分层证据"]),
        (590,465,"5  Prompt + AI",["命盘 + 判定 + 典籍 + 解读风格","模型生成说明，SSE 持续返回"]),
        (60,465,"6  解读结果",["文字段落 / 规则锚点 / 来源","置信度分档 / 图表 / 多轮追问"]),
    ]
    for x,y,t,lines in rows:
        d.box(x,y,420,175,t,lines)
    d.arrow([(480,278),(590,278)])
    d.arrow([(1010,278),(1120,278)])
    d.arrow([(1330,365),(1330,465)])
    d.arrow([(1120,552),(1010,552)])
    d.arrow([(590,552),(480,552)])
    d.box(335,725,930,110,"知识供给：结构化查表 + 典籍语义检索",["证据缺失、规则冲突和段落锚点不足，会影响结果的置信度标记。"],RED)
    d.arrow([(1265,780),(1450,780),(1450,640)])
    d.save("02-interpretation","本图说明单八字解读链；融合解读会进入多通道分支，详见正文。")


def rag():
    d = Diagram("RAG · 离线建库与在线检索", "向量模型负责相关性，元数据与规则负责来源约束")
    d.text(60,165,"离线：资料变成可检索资产",24,RED)
    d.box(60,220,420,185,"典籍原文",["TXT / DOCX / DOC","规范文本、识别章节与来源","旧 DOC 的读取依赖 Windows COM"])
    d.box(590,220,420,185,"分块与向量编码",["目标 400 字符；长段重叠 80 字符","bge-small-zh-v1.5","保存原文、章节、来源分级等字段"])
    d.box(1120,220,420,185,"Chroma 持久索引",["按术数类别组织 collection","向量用于召回，原文用于引用","索引报告记录建库结果"])
    d.text(60,460,"在线：问题变成可追溯证据",24,RED)
    d.box(60,515,420,205,"查询与候选召回",["用户问题 / 命盘检索键 → query","选择类别，查询向量近邻","按主题、来源等级等过滤候选"])
    d.box(590,515,420,205,"重排与来源加权",["CrossEncoder 比较 query + 原文","相关性 × 来源权重 × 文本角色","案例片段额外降权"])
    d.box(1120,515,420,205,"证据 → 解读上下文",["primary / secondary / case / low trust","返回 excerpt + source + metadata","规则链与 Prompt 使用筛选后的证据"])
    d.arrow([(480,310),(590,310)])
    d.arrow([(1010,310),(1120,310)])
    d.arrow([(1330,405),(1330,435),(520,435),(520,500),(270,500),(270,515)])
    d.arrow([(480,615),(590,615)])
    d.arrow([(1010,615),(1120,615)])
    d.save("03-rag","当前本机启用了 CUDA 和重排；检索得分表示相关性，不代表结论正确的概率。")


def personas():
    d = Diagram("名人对话 · 从人物资料到会话", "人物目录与人物提示词包独立管理，对话复用统一 AI 编排层")
    d.box(60,190,420,190,"上游仓库快照",["awesome-nuwa 分类与人物列表","固定聚合仓库提交，记录人物提交","读取许可、SKILL 和指定参考文档"])
    d.box(590,190,420,190,"导入与标准化",["检查重复、体积、许可与文档","提取方法论摘要 + 标记可用状态","生成 catalog.json / 审计记录"])
    d.box(1120,190,420,190,"人物目录 UI",["165 人 / 18 类：搜索、筛选、分页","详情、话题、来源与身份披露","目录请求不再依赖聊天状态成功"])
    d.box(60,505,420,190,"PersonaPack",["内置王阳明包优先","其他人物由目录记录生成运行时包","方法论 + 来源目录 + 开场问题"])
    d.box(590,505,420,190,"创建 persona 会话",["bootstrap = 模式约束 + 人物资料","metadata 绑定 personaId 与模式","81 个历史模拟 / 84 个公开框架"])
    d.box(1120,505,420,190,"共享 ChatOrchestrator",["已有会话上下文 + 新用户问题","Composer 或 DeepSeek","流式文字 → 聊天界面"])
    d.arrow([(480,285),(590,285)])
    d.arrow([(1010,285),(1120,285)])
    d.arrow([(800,380),(800,420),(270,420),(270,505)])
    d.arrow([(1330,380),(1330,465),(800,465),(800,505)])
    d.arrow([(480,600),(590,600)])
    d.arrow([(1010,600),(1120,600)])
    d.save("04-personas","ready 是导入与可用性状态，不等于人物资料已逐条史学校勘，也不代表模型经过人物专属训练。")


if __name__ == "__main__":
    for render in (architecture, bazi, rag, personas):
        render()
    print("Rendered 4 PNG diagrams and 4 editable SVG diagrams.")
