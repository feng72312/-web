# Cursor PDF Skill — 分享包

可独立分发的 Cursor Agent PDF 处理 skill，与任何具体项目无关。

## 包内容

```
cursor-pdf-skill-share/
├── README.md           ← 本文件
├── INTEGRATION.md      ← 接收方 / 新 Agent 完整集成指南
├── requirements.txt    ← Python 依赖
├── install.ps1         ← Windows 一键安装
├── install.sh            ← macOS / Linux 一键安装
└── skill/              ← skill 本体（安装时复制到 ~/.cursor/skills/pdf/）
    ├── SKILL.md
    ├── forms.md
    ├── reference.md
    ├── LICENSE.txt
    └── scripts/        ← 8 个表单/OCR 工具脚本
```

## 分享方式

将整个 `cursor-pdf-skill-share` 文件夹打包发送即可：

```powershell
Compress-Archive -Path "d:\Code\cursor-pdf-skill-share\*" -DestinationPath "d:\Code\cursor-pdf-skill-share.zip"
```

## 接收方安装（3 步）

```powershell
# 1. 解压到任意目录
# 2. 进入目录，运行安装脚本
.\install.ps1

# 3. 重启 Cursor（或新开 Agent 对话）
```

安装完成后 skill 位于：`~/.cursor/skills/pdf/`（Windows: `%USERPROFILE%\.cursor\skills\pdf\`）

## 能力概览

| 能力 | 工具 |
|------|------|
| 合并 / 拆分 / 旋转 | pypdf、qpdf |
| 提取文本 / 表格 | pdfplumber |
| 创建 PDF | reportlab |
| 扫描件 OCR | pdf2image + pytesseract |
| 填写 PDF 表单 | skill/scripts/ + forms.md |

## 许可

skill 本体许可见 [skill/LICENSE.txt](skill/LICENSE.txt)（Anthropic 专有许可）。分享前请确认符合你方与 Anthropic 的协议约定。
