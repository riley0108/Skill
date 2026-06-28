# ppt-master — AI-SVG 簡報生成 pipeline

> 路徑 B 的參考。萃自 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)（自身就是一個 Claude Code skill/plugin，719 行 SKILL.md + 大量 scripts/模板，13k+ 檔，故不 vendor，clone 後使用）。

## 是什麼
AI 驅動的多格式 SVG 內容生成系統：把來源文件（PDF/DOCX/URL/Markdown）轉成高品質 SVG 頁面，經多角色協作後匯出成**原生、可編輯**的 .pptx（真的 DrawingML 形狀/文字框/圖表，非貼圖）。講者備註可轉語音旁白。可跑在 Claude Code / Cursor / VS Code Copilot 等 AI IDE。

## 核心 Pipeline（嚴格序列）
```
來源文件 → 建專案 → [模板] → 策略師(Strategist) → [生圖 Image_Generator]
        → 執行者(Executor) 逐頁 SVG 即時預覽 → 品質檢查 → 後製 → 匯出 PPTX
```

## 安裝
- Python 3.10+；選用 pandoc（處理 .doc/.odt/.rtf 等舊格式）；選用生圖 API key（gpt-image/OpenAI/Gemini）與圖片搜尋（Pexels/Pixabay/Openverse/Wikimedia）。
- `pip install -r requirements.txt`，照 repo 的 `docs/getting-started.md`。
- 來源放 `projects/`，產出到 `exports/`。
- 支援的 AI 模型：Claude（推薦）、GPT、Gemini、Kimi 等。

## 主要 scripts（`scripts/`）
| 類 | script | 用途 |
|---|---|---|
| 來源轉 MD | `source_to_md/pdf_to_md.py` / `doc_to_md.py` / `excel_to_md.py` / `ppt_to_md.py` / `web_to_md.py` | PDF/文件/Excel/PPT/網頁 → Markdown |
| 專案 | `project_manager.py` | 專案 init/validate/manage |
| 圖 | `analyze_images.py` / `image_gen.py` / `slice_images.py` / `latex_render.py` | 圖片分析/AI 生圖/切圖/公式渲染 |
| SVG | `svg_quality_checker.py` / `finalize_svg.py` / `svg_to_pptx.py` | 品質檢查/後製/匯出 PPTX |
| 既有 PPTX | `native_enhance_pptx.py` / `native_narration_pptx.py` | 既有檔加備註/旁白/轉場 |
| 規格 | `update_spec.py` | 把 spec_lock 的配色/字型改動傳播到所有 SVG |

## Standalone workflows（`workflows/`）
- `topic-research` — 只給主題沒檔案時，先抓網路來源
- `template-fill-pptx` — 給原生 PPTX 模板 + 素材，選頁填字（不走 SVG）
- `beautify-pptx` — 既有 PPTX 經 SVG pipeline 重排版（保留原文字/配色，只重做版面）
- `create-template` / `create-brand` — 建可重用版型 / 品牌識別預設
- `resume-execute` — 跨對話續跑（Phase A 完成後在新對話跑 Phase B）
- `verify-charts` — 資料圖表座標校準
- `customize-animations` — 物件級 PPTX 動畫自訂
- `native-enhance-pptx` — 既有成品加備註/音訊/自動換頁/轉場
- `live-preview` / `visual-review` — 瀏覽器即時預覽 / 逐頁視覺自檢

## PPTX 路由邊界（重要）
- 給「原生 PPTX 模板 + 新素材，要產 PPTX」→ 預設走 **`template-fill`**（直接 OOXML 填字，不走 SVG）。
- 要把該 PPTX 變成「可重用 SVG 版型包再生成」→ 先跑 **`create-template`** 拿到版型目錄，再進主 pipeline。
- 兩者互斥：`template-fill` = 複製選定原生頁 + 補字；`create-template`→主pipeline = 轉成可重用版型後用 SVG 生成。

## ⚠️ 鐵則（它跨頁一致的關鍵，別違反）
1. **嚴格序列執行**；標 ⛔ BLOCKING 的步驟（如「八項確認」）必須停下等使用者明確回覆，不可代為決定。
2. **SVG 必須主 agent 逐頁手寫** —— 不可委派 sub-agent、不可寫腳本批量產 SVG（即使「省 token / 趕時間」也禁止）。跨頁視覺一致依賴每頁帶完整上游 context 手刻，腳本做不到。
3. **每頁生成前先 `read_file spec_lock.md`** —— 所有配色/字型/圖示/圖片都從這檔來，不可憑記憶或當場亂編；並查該頁的 `page_rhythm`/`page_layouts`/`page_charts`。這是抵抗長 deck context 漂移、打破「每頁都長一樣」的關鍵。
4. **回應語言** match 使用者輸入與來源語言；但 `design_spec.md` 須保留原英文模板結構（欄位名），值可用使用者語言。
5. 不要為它建 `.worktrees/`/`tests/`/branch 等通用工程結構——它是 repo-specific 工作流。

## 特色
- 多畫布格式（PPT 16:9、微信、小紅書等）、自訂 .pptx 模板或自由設計、AI 生圖或網路搜圖、SVG 備份可重新匯出修改、講者備註轉語音。
