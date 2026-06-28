# python-pptx + Office-PowerPoint MCP Server 速查

> 路徑 A 的完整參考。底層都是 **python-pptx**（操作 OOXML，產出原生 .pptx）。MCP server 已 vendor 在本 skill 的 [`../mcp-server/`](../mcp-server/)（原 repo GongRzhe/Office-PowerPoint-MCP-Server 已於 2026-03 封存，故凍結穩定）。

## A. 直接用 python-pptx（最輕，可腳本）

```bash
pip install python-pptx        # 也裝 Pillow(圖片)、FontTools(字型)
```

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()                      # 空白；或 Presentation("brand.pptx") 套既有模板
# prs.slide_width / prs.slide_height 可設尺寸（16:9 預設 13.333x7.5 in）

# 標題頁（layout 0）
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "標題"
slide.placeholders[1].text = "副標題"

# 內容頁（layout 1）+ 多層項目符號
s = prs.slides.add_slide(prs.slide_layouts[1])
s.shapes.title.text = "重點"
tf = s.placeholders[1].text_frame
tf.text = "第一點"
for txt, lvl in [("子點", 1), ("第二點", 0)]:
    p = tf.add_paragraph(); p.text = txt; p.level = lvl

# 文字框 + 格式
box = s.shapes.add_textbox(Inches(1), Inches(5), Inches(8), Inches(1))
r = box.text_frame.paragraphs[0].add_run(); r.text = "粗體紅字"
r.font.bold = True; r.font.size = Pt(28); r.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)

# 圖片 / 形狀
s.shapes.add_picture("logo.png", Inches(0.5), Inches(0.5), height=Inches(1))

# 表格
rows, cols = 3, 2
tbl = s.shapes.add_table(rows, cols, Inches(1), Inches(2), Inches(6), Inches(2)).table
tbl.cell(0, 0).text = "項目"; tbl.cell(0, 1).text = "數值"

# 圖表（長條）
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
cd = CategoryChartData(); cd.categories = ["Q1", "Q2", "Q3"]
cd.add_series("營收", (10, 18, 25))
s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1), Inches(2), Inches(6), Inches(4), cd)

prs.save("output.pptx")
```

**常用物件**：`prs.slides`、`slide.shapes`、`slide.placeholders[idx]`、`shape.text_frame.paragraphs[].runs[]`、`run.font`（`.bold/.italic/.size/.name/.color.rgb`）。單位用 `Inches/Pt/Emu`。讀取既有檔做批量改寫：開啟 → 迭代 `slide.shapes` 改 `.text` → `save()`。

## B. Office-PowerPoint MCP Server（32 工具）

### 安裝 / 設定
```bash
pip install -r ~/.claude/skills/pptx-generator/mcp-server/requirements.txt
# 或自動：python ~/.claude/skills/pptx-generator/mcp-server/setup_mcp.py
```

MCP 設定（本地 Python）：
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
或免本地安裝用 uvx：`{"command":"uvx","args":["--from","office-powerpoint-mcp-server","ppt_mcp_server"]}`。

### 32 工具（v2.0，分 6 類）

**簡報管理（7）**
- `create_presentation` — 新建簡報
- `create_presentation_from_template` — 從模板建（保留主題）
- `open_presentation` — 開既有 .pptx
- `save_presentation` — 存檔
- `get_presentation_info` — 取簡報 metadata
- `get_template_file_info` — 分析模板結構/版面
- `set_core_properties` — 設文件屬性（標題/作者/關鍵字）

**內容管理（8）**
- `add_slide` — 加投影片（可帶背景樣式）
- `get_slide_info` — 取投影片資訊
- `extract_slide_text` — 抽某頁文字
- `extract_presentation_text` — 抽全部文字 + 統計
- `populate_placeholder` — 填 placeholder
- `add_bullet_points` — 加格式化項目符號
- `manage_text` — 統一工具：新增/格式化/驗證/run 格式
- `manage_image` — 統一工具：加圖/增強

**模板操作（7）**
- `list_slide_templates` — 瀏覽 25+ 內建專業版型
- `apply_slide_template` — 套版型到既有頁
- `create_slide_from_template` — 用版型建頁
- `create_presentation_from_templates` — 用版型序列建整份簡報
- `get_template_info` — 查特定版型屬性
- `auto_generate_presentation` — 依主題描述自動生成
- `optimize_slide_text` — 改善文字可讀性/適配

**結構元素（4）**
- `add_table` — 加表格（增強格式）
- `format_table_cell` — 自訂單一儲存格
- `add_shape` — 加形狀（帶文字/格式）
- `add_chart` — 加圖表（長條/橫條/折線/圓餅）

**專業設計（3）**
- `apply_professional_design` — 統一設計工具（主題/投影片/增強）
- `apply_picture_effects` — 9+ 圖片效果（陰影/光暈/反射…可疊加）
- `manage_fonts` — 字型分析/優化/建議

**特殊功能（5）**
- `manage_hyperlinks` — 超連結增刪查改
- `manage_slide_masters` — 投影片母片屬性
- `add_connector` — 元素間連接線/箭頭
- `update_chart_data` — 替換圖表資料
- `manage_slide_transitions` — 設定轉場效果

**內建資源**：4 配色（Modern Blue / Corporate Gray / Elegant Green / Warm Red）、25+ 版型（自動字級 + 視覺效果）。

### 用法範例
```python
# 建 + 存
r = use_mcp_tool("ppt", "create_presentation", {})
pid = r["presentation_id"]
use_mcp_tool("ppt", "add_slide", {"layout_index": 0, "title": "我的簡報", "presentation_id": pid})
use_mcp_tool("ppt", "save_presentation", {"file_path": "output.pptx", "presentation_id": pid})

# 專業設計頁
use_mcp_tool("ppt", "apply_professional_design", {
    "operation": "slide", "slide_type": "title_content",
    "color_scheme": "modern_blue", "title": "季度回顧",
    "content": ["營收 +15%", "客戶滿意度 94%"]})

# 用版型序列建整份
use_mcp_tool("ppt", "create_presentation_from_templates", {
    "template_sequence": [
        {"template_id": "title_slide", "content": {"title": "年度報告", "subtitle": "2024"}},
        {"template_id": "key_metrics_dashboard", "content": {"metric_1_value": "94%", "metric_2_value": "$2.4M"}}
    ],
    "color_scheme": "modern_blue"})
```

依賴：python-pptx（核心）、Pillow（圖片增強）、FontTools（字型）。Python 3.6+。支援 round-trip 保留既有檔的所有 Open XML 元素。
