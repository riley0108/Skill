---
name: pptx-generator
description: 用「特定兩套工具鏈」產生 PowerPoint (.pptx)：(A) 本 skill 內附的 Office-PowerPoint MCP server（32 工具、python-pptx 驅動）——要用 MCP 工具、python-pptx 腳本化、批量自動化產/改 .pptx、加圖表表格、套模板時用；(B) ppt-master AI-SVG pipeline——要把 PDF/DOCX/網址/markdown 生成「設計精美」的原生 .pptx、或要設計感簡報時用。也附簡報工具總覽。⚠️ 邊界：一般單純「建立/讀取/編輯/抽取文字/合併分割 .pptx」而**不指定用這兩套工具**時，改用 Anthropic 官方 `pptx` skill（那才是通用 .pptx 能力）；本 skill 專門用於「MCP server / python-pptx 批量腳本 / ppt-master 精美生成」這三種情境。
---

# 📊 PowerPoint (.pptx) 生成與編輯

兩條互補路徑，先選對路：

| | **A. python-pptx / MCP server** | **B. ppt-master AI-SVG pipeline** |
|---|---|---|
| 做什麼 | 程式化建/改 .pptx、加表格圖表、套設計 | 從文件/主題生**精美設計**的原生 .pptx |
| 適合 | 批量、自動化、改既有檔、資料驅動、報表 | 一份漂亮的簡報、文件轉簡報、要設計感 |
| 怎麼動 | python-pptx（OOXML），可腳本可 MCP 工具 | AI 多角色 + 逐頁手刻 SVG → 轉 PPTX |
| 美感 | 看你怎麼排（內附 25+ 模板與 4 配色） | 高（SVG 全控版面/插圖/圖表） |
| 安裝 | `pip install python-pptx`，MCP 已內附 | 需另裝 ppt-master plugin（見下） |

→ **要可控/可腳本/改檔 → A**；**要一份美觀成品 → B**。兩者可混：B 出成品、A 做後續批量微調。

## 🅰️ python-pptx + 內附 MCP server
- **最快**：`pip install python-pptx`，直接寫 Python 操作 .pptx（見 [references/python-pptx-mcp.md](references/python-pptx-mcp.md) 的 quickstart）。
- **MCP 工具**：本 skill 內附完整 [Office-PowerPoint MCP server](mcp-server/)（32 工具，python-pptx 驅動，**原 repo 已封存故凍結穩定**）。接上後可用自然語言叫工具建簡報。設定：
```bash
pip install -r ~/.claude/skills/pptx-generator/mcp-server/requirements.txt
```
```json
{
  "mcpServers": {
    "ppt": {
      "command": "python",
      "args": ["/home/riley/.claude/skills/pptx-generator/mcp-server/ppt_mcp_server.py"],
      "env": {}
    }
  }
}
```
32 工具分 6 類（簡報管理 / 內容 / 模板 / 結構元素 / 專業設計 / 特殊功能），完整清單與用法見 [references/python-pptx-mcp.md](references/python-pptx-mcp.md)。

## 🅱️ ppt-master AI-SVG pipeline
從 PDF/DOCX/URL/Markdown 生原生可編輯 .pptx。**Pipeline**：`來源文件 → 建專案 → [模板] → 策略師 → [生圖] → 執行者逐頁 SVG 即時預覽 → 品質檢查 → 後製 → 匯出`。
- 它是獨立的 Claude Code **plugin/skill**（719 行 SKILL.md + 大量 scripts/模板，13k+ 檔），太大不 vendor。安裝與用法摘要見 [references/ppt-master.md](references/ppt-master.md)。
- 安裝：clone [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，照其 `docs/getting-started.md`（Python 3.10+，選用 pandoc/生圖 API key）；或當 Claude Code plugin 載入。
- ⚠️ 它的鐵則：SVG 必須**主 agent 逐頁手寫**（不可 sub-agent、不可腳本批量產），每頁先重讀 `spec_lock.md` 確保配色/字型/圖一致——這是它跨頁視覺一致的關鍵。

## 🧰 python-pptx 最小範例（路 A，直接可跑）
```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()                          # 或 Presentation("template.pptx")
slide = prs.slides.add_slide(prs.slide_layouts[0])   # 0=標題頁
slide.shapes.title.text = "我的簡報"
slide.placeholders[1].text = "副標題"

# 內容頁 + 項目符號
s2 = prs.slides.add_slide(prs.slide_layouts[1])
s2.shapes.title.text = "重點"
tf = s2.placeholders[1].text_frame
tf.text = "第一點"
p = tf.add_paragraph(); p.text = "第二點"; p.level = 1

prs.save("output.pptx")
```

## 📚 references
- [references/python-pptx-mcp.md](references/python-pptx-mcp.md) — python-pptx 速查 + MCP server 32 工具清單與設定
- [references/ppt-master.md](references/ppt-master.md) — ppt-master pipeline、工作流、安裝、鐵則
- [references/tools-landscape.md](references/tools-landscape.md) — 簡報工具總覽（AI 生成器/markdown 工具/設計/協作/資料視覺化，萃自 Awesome-presentation-tools）

> 來源：[GongRzhe/Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server)（已 vendor，封存唯讀）、[hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)、[runablehq/Awesome-presentation-tools](https://github.com/runablehq/Awesome-presentation-tools)。核對於 2026-06。
