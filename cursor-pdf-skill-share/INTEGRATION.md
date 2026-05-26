# PDF Skill 集成指南

> 面向：收到本分享包的开发者，或为其配置的 Cursor Agent。
> 阅读时间：5 分钟。

---

## 1. 这是什么

这是一个 **Cursor Agent Skill**，教 Agent 如何处理 PDF：

- 读取 / 提取文本和表格
- 合并、拆分、旋转页面
- 创建新 PDF、加水印、加密
- 扫描件 OCR
- 填写 PDF 表单（可填写字段 + 不可填写字段两种流程）

Skill 安装后，Agent 在用户提到 `.pdf` 或 PDF 相关操作时自动读取 `SKILL.md` 并按指引执行。

---

## 2. 安装步骤

### Windows

```powershell
cd <解压目录>\cursor-pdf-skill-share
.\install.ps1
```

### macOS / Linux

```bash
cd <解压目录>/cursor-pdf-skill-share
chmod +x install.sh
./install.sh
```

### 手动安装（任意平台）

```bash
# 1. 复制 skill 文件
mkdir -p ~/.cursor/skills/pdf
cp -r skill/* ~/.cursor/skills/pdf/

# 2. 安装 Python 依赖
pip install -r requirements.txt
```

### 验证安装

```powershell
# skill 文件存在
Test-Path "$env:USERPROFILE\.cursor\skills\pdf\SKILL.md"   # 应返回 True

# Python 依赖可用
python -c "from pypdf import PdfReader; print('OK')"
```

---

## 3. Agent 如何使用

安装后**无需额外配置**。当用户说：

- 「合并这两个 PDF」
- 「从这个 PDF 提取表格」
- 「帮我把扫描件 OCR 成文字」
- 「填写这个 PDF 表单」

Agent 应：

1. Read `~/.cursor/skills/pdf/SKILL.md`
2. 按任务类型选择工具（见 SKILL.md 内 Quick Reference 表）
3. 表单填写任务额外 Read `forms.md`
4. 高级用法 Read `reference.md`

### 表单填写流程（Agent 必读 forms.md）

```
check_fillable_fields.py  →  有可填写字段？
  ├─ 是 → extract_form_field_info.py → fill_fillable_fields.py
  └─ 否 → convert_pdf_to_images.py → 视觉定位 → fill_pdf_form_with_annotations.py
```

脚本路径：`~/.cursor/skills/pdf/scripts/`，运行时使用绝对路径或先 `cd` 到该目录。

---

## 4. 可选系统依赖

以下仅在特定场景需要，基础读写合并不依赖它们：

| 工具 | 场景 | Windows 安装 |
|------|------|-------------|
| **Poppler** | pdf→图片、OCR | [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) → `bin/` 加入 PATH |
| **Tesseract** | OCR（含中文） | [UB Mannheim 构建](https://github.com/UB-Mannheim/tesseract/wiki) + 安装 `chi_sim` 语言包 |
| **qpdf** | 命令行合并/拆分 | `winget install qpdf` |
| **pdftotext** | 命令行提取文本 | 随 Poppler 提供 |

---

## 5. Python 依赖

见 [requirements.txt](requirements.txt)：

```
pypdf
pdfplumber
reportlab
pdf2image    # OCR 场景
pytesseract  # OCR 场景
```

---

## 6. 文件说明

| 文件 | 用途 | Agent 何时读取 |
|------|------|---------------|
| `skill/SKILL.md` | 主入口：常用操作、代码示例 | 任何 PDF 任务 |
| `skill/forms.md` | 表单填写完整流程 | 填写 PDF 表单 |
| `skill/reference.md` | 高级 API、JS 库、排错 | 复杂 / 非常规任务 |
| `skill/scripts/*.py` | 表单分析、填写、OCR 辅助 | 表单 / 验证场景 |
| `skill/LICENSE.txt` | 许可条款 | 无需读取 |

---

## 7. 常见问题

**Q: Agent 没有使用这个 skill？**
- 确认 `~/.cursor/skills/pdf/SKILL.md` 存在
- 重启 Cursor 或新开对话
- 用户请求中明确提到「PDF」

**Q: 脚本报 ModuleNotFoundError？**
- 重新运行 `install.ps1` 或 `pip install -r requirements.txt`

**Q: OCR 中文乱码或无输出？**
- 确认 Tesseract 已安装且 `chi_sim` 语言包存在
- 确认 Poppler 在 PATH 中

**Q: 能否放到项目 `.cursor/skills/` 下？**
- 可以，复制 `skill/` 内容到 `<项目>/.cursor/skills/pdf/` 即可团队共享
- 本分享包默认安装到用户全局目录，对所有项目生效

**Q: 与 Cursor 内置 pdf skill 冲突？**
- 本包即 Cursor 内置 pdf skill 的完整副本，安装到同一路径会覆盖/对齐，不冲突

---

## 8. 集成检查清单

```
- [ ] 运行 install.ps1 / install.sh 成功
- [ ] ~/.cursor/skills/pdf/SKILL.md 存在
- [ ] python -c "from pypdf import PdfReader" 无报错
- [ ] （可选）Poppler + Tesseract 已装（OCR 场景）
- [ ] 新开 Agent 对话，测试「读取某 PDF 页数」
```
