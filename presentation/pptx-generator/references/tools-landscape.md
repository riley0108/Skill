# 簡報工具總覽（Presentation Tools Landscape）

> 萃自 [runablehq/Awesome-presentation-tools](https://github.com/runablehq/Awesome-presentation-tools)（2025-11 版）。挑工具時的地圖：先看「要什麼」再選類別。本 skill 自身聚焦 .pptx 生成（python-pptx/ppt-master）；markdown 路線見 `slidev` skill；學術海報見 `academic-poster` skill。

## AI 簡報生成器（prompt/文字 → 整份簡報）
- **Gamma**、**Tome**、**Beautiful.ai**、**Decktopus**、**Runable** — 從提示/內容/文字描述生成簡報。
- **Slides AI** — 整合 Google Slides。**GenPPT** — 文字提示即時生成完整 deck。
- 適合：快速出初稿、非設計者、行銷簡報。缺點：客製/品牌一致性有限、輸出常是平台鎖定。

## 企業級 AI 方案
- **Prezent**、**Storydoc**、**Prezi AI**、**Curipod** — 著重合規、安全、客製，給組織用。

## 網頁 / 協作平台
- **Pitch**、**Canva**、**Google Slides**、**Visme** — 即時協作、雲端。
- **Microsoft PowerPoint Online** — 內建 Designer AI 與 Copilot。

## 開發者 / Markdown 工具（寫程式碼、進 git）
- **Slidev**（→ 本 repo 有專屬 skill）、**Reveal.js**、**Marp**、**Remark.js** — markdown/HTML 寫投影片，可版控、CI、自架。
- 適合：工程簡報、要可重現、程式碼高亮。

## 視覺 / 互動
- **Prezi** — 非線性、縮放式視覺敘事。
- **Mentimeter**、**Kahoot!**、**AhaSlides** — 即時觀眾互動/投票。

## 資料視覺化專門
- **think-cell**（PowerPoint 外掛，做複雜商業圖表）、**Infogram**、**Datawrapper**、**Flourish** — 圖表/資訊圖/BI。

## 開源 / 免費
- **Impress.js**、**Shower**、**WebSlides**、**Patat**（終端機簡報）。

## 選型速記
| 要什麼 | 選 |
|---|---|
| 一鍵 AI 出初稿 | Gamma / Tome / Beautiful.ai / Runable |
| 程式化、可版控、程式碼 | Slidev / Marp / Reveal.js（或本 repo `slidev` skill） |
| 程式產 .pptx / 改既有檔 | python-pptx / Office-PPT MCP（本 skill 路 A） |
| 文件 → 精美原生 .pptx | ppt-master（本 skill 路 B） |
| 即時協作 | Pitch / Canva / Google Slides |
| 觀眾互動 | Mentimeter / Kahoot / AhaSlides |
| 複雜商業圖表 | think-cell / Datawrapper / Flourish |
| 學術海報 | 本 repo `academic-poster` skill |
