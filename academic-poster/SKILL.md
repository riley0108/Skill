---
name: academic-poster
description: 專做「學術／科學研究會議海報」（academic/scientific conference research poster，大尺寸列印如 A0、48x36）。涵蓋 LaTeX beamerposter/tikzposter、PowerPoint 大尺寸設定、多欄版面與閱讀動線、字級字數準則、色盲友善配色、高解析「資料圖表」匯出（向量 PDF/SVG、matplotlib dpi）、Mike Morrison 的 #betterposter「大結論」設計、送印前置（嵌字型/出 PDF/出血）。當使用者要「研究/會議海報、CVPR/ECCV poster、把論文變海報、beamerposter/tikzposter 範本、A0/48x36 學術海報」時用。⚠️ 邊界：一般「藝術／行銷／活動海報」或要產 .png/.pdf 視覺設計作品，改用 `canvas-design` skill；本 skill 專攻帶研究內容、資料圖、大尺寸送印的學術海報。附 LaTeX 起始範本。
---

# 🪧 學術研究海報（Academic Poster）

把研究變成「站在攤位前、十呎外就能讀懂」的海報。完整指南在 **[references/reference.md](references/reference.md)**（格式/尺寸/版面/字體/配色/betterposter/LaTeX/工作流 8 區）；LaTeX 起始範本在 **[templates/](templates/)**。

## 🚦 先選格式（30 秒決策）
| 你的情況 | 用 |
|---|---|
| 數學/ML/物理多、要重用論文 LaTeX 與公式 | **LaTeX `beamerposter` / `tikzposter`**（[templates/](templates/)） |
| 大多數人、要跟非設計者協作、快速組裝 | **PowerPoint / Google Slides** |
| 要印刷級精緻、設計感重 | **Illustrator / InDesign / Affinity**（免費替代 **Inkscape**） |

→ 重現性/自動產圖 → LaTeX；速度/協作 → PowerPoint；印刷精緻 → 向量設計軟體。**永遠從「最終尺寸」的範本開始做，不要先做小再放大。**

## 📐 尺寸速查
- **48×36 in**（美式最常見橫式）｜**36×48** 直式｜**36×24**、**42×30** 較小
- **A0 = 841×1189 mm**（歐洲會議標準）｜A1 = 594×841｜A2 = 420×594
- **數位海報**：1920×1080（16:9）或 3840×2160（4K）
- PowerPoint 設尺寸：**Design → Slide Size → Custom**，提示縮放選「Ensure Fit」
- ⚠️ **PowerPoint 上限 56×56 in**。要更大（如 48×96）→ **用一半尺寸（24×48）做、請印刷廠放大 200%**，圖務必用向量否則放大會糊
- 列印：所有點陣圖 **最終尺寸下 ≥300 DPI**；向量（PDF/SVG/EPS）無 DPI 問題，優先用

## ✍️ 字級 & 字數（48×36 / 36×48）
| 元素 | 大小 |
|---|---|
| 標題 | ~72–120 pt（常見 ~85） |
| 作者 | ~60 pt |
| 章節標題 | ~36–72 pt |
| 內文 | **24–32 pt，絕不低於 24** |
| 圖說 | ~24 pt |
- 全張 **< ~800 字**，越少越好；標題/標頭用無襯線（Arial/Helvetica），最多 2–3 種字型；標題內文都別全大寫。

## 🎯 版面 & 設計鐵則
1. **2–4 欄**（48×36 橫式常用 3 欄），欄寬一致對齊。
2. **閱讀動線**：欄內由上到下，再左到右（報紙式）；動線會混淆就標號。
3. **視覺優先**：海報不是貼在牆上的論文——**砍文字、放圖**，段落改條列。圖文比要高。
4. **視覺層級**：標題 > 章節標頭 > 內文 > 圖說，全張風格一致。
5. **留白**：別塞滿，欄間距與邊界要夠（過度擁擠是頭號錯誤）。
6. 標題列含：標題/作者/單位/logo；內文靠左對齊，置中只用於標題與圖說。

## 💡 #betterposter（Mike Morrison 大結論法）
攤位前的人是**快速掃描篩選**，所以把單一關鍵結果放正中央、用大字白話講：
- **中央「主結論 Bar」**：一句大字、白話、講清楚這研究的 takeaway（不是制式學術標題）。
- 中央下方：**QR code** 連到完整論文/聯絡。
- 左欄「無聲簡報」：脈絡，讓海報沒人顧時也能自我說明。
- 右欄「彈藥 Bar」：給想深聊的人看的細節/圖/方法。
- 折衷版（Hybrid 1.5）：保留大結論，但恢復較傳統的細節欄——最安全。

## 🧰 LaTeX 起始範本
- [templates/beamerposter_skeleton.tex](templates/beamerposter_skeleton.tex) — A0 橫式三欄（beamer 系，公式/BibTeX 原生）
- [templates/tikzposter_skeleton.tex](templates/tikzposter_skeleton.tex) — A0 直式雙欄（TikZ 系，版面彈性大）
- 完整會議海報範例（CVPR/ECCV：CAM/UperNet/PS-FCN/SDPS-Net/TOM-Net…）見來源 repo [SuperBruceJia/Poster_Template](https://github.com/SuperBruceJia/Poster_Template)；生科 PPT/AI 範本與 48×36 標註範例見 [MIT-BECL/Poster_Resources](https://github.com/MIT-BECL/Poster_Resources)。

## ☠️ 列印前必做（最常翻車處）
1. **嵌入或外框化字型**（PowerPoint：File→Options→Save→Embed fonts；Illustrator/Inkscape：文字轉外框），否則印刷廠換字型整個跑版。
2. **出 PDF 給印刷**（保留向量與版面），別交 .pptx。
3. **圖用向量**（plot 用 `plt.savefig("fig.pdf")`；點陣最終尺寸 ≥300 DPI）。
4. 確認**出血/邊界**，留安全邊；**100% 縮放校稿**，看有無糊圖、錯字。

> 來源：SuperBruceJia/Poster_Template、MIT-BECL/Poster_Resources + 多所大學海報指南與 #betterposter 運動。核對於 2026-06。
