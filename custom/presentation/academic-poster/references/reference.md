# 學術／科學研究海報 — 完整指南

> 萃自 SuperBruceJia/Poster_Template、MIT-BECL/Poster_Resources + 大學海報指南與 #betterposter 運動。核對於 2026-06。

## 0. 兩個來源 repo 有什麼
**SuperBruceJia/Poster_Template** — ML/CV 會議海報，兩種格式：
- **PowerPoint (.pptx)**：NLNet(MMSP'22)、CAM(CVPR'15)、ADE20k(CVPR'17)、TRN(ECCV'18)、UPerNet(ECCV'18)、NetDissect(CVPR'18)。PPT 範本出自 Prof. Bolei Zhou。（repo 自註 NetDissect「字太小/太密」是反面教材，別照抄。）
- **LaTeX (.tex)**：DeepHDRVideo、PS-FCN、SDPS-Net、TOM-Net，用 `beamerposter`/`tikzposter`，出自 Prof. Guanying Chen。
- 當 CVPR/ECCV 風格橫式 ML 海報的起始骨架。

**MIT-BECL/Poster_Resources** — 生科範本：
- 格式 **PowerPoint (.ppt)** + **Adobe Illustrator (.ai)**；方向 **橫/直/方**。
- 一份 **48×36 直式標註範例 (PDF)** 示範最佳實踐 + **PowerPoint 母片使用指南 (PDF)**。
- 推薦 **Inkscape** 當 Illustrator 免費替代。

## 1. 格式選擇
| 工具 | 適合 | 優 | 缺 |
|---|---|---|---|
| **LaTeX `beamerposter`** | 數學/ML/物理、重用論文 LaTeX | 排版美、公式/BibTeX 原生、可重現 | 版面繁瑣、學習曲線陡、視覺迭代慢 |
| **LaTeX `tikzposter`** | 同上、要更彈性版面/主題 | TikZ 版面彈性大、多主題、block 模型乾淨 | 比 beamer 陡、冗長 |
| **LaTeX `baposter`/`a0poster`** | 舊/legacy 範本 | baposter 盒裝版面；a0poster 極簡基礎 | 維護少；a0poster 很手動 |
| **PowerPoint / Google Slides** | 多數人、非設計者協作、快速組裝 | 易、WYSIWYG、人人有、好共編 | 圖要手動、字體弱、56" 上限 |
| **Illustrator / InDesign** | 印刷精緻、設計重 | 全向量控制、精準排版、專業輸出 | 付費、需設計力；InDesign 適文字多 |
| **Inkscape / Affinity / Scribus** | 免費/便宜的向量力 | 免訂閱、向量控制 | 生態小、範本少 |

**依優先選**：印刷精緻 → InDesign/Affinity/Scribus/Illustrator；重現性/自動產圖 → LaTeX 或 Quarto/R Markdown；速度/協作 → PowerPoint/Google Slides/Canva。

**會議慣例**：多數 CS/ML 場（CVPR、ECCV、NeurIPS、ICML）接受任何工具，只看**指定尺寸的最終 PDF**。會議範本通常是 PowerPoint；CV/ML 圈常用 LaTeX。**開工前務必看 call-for-posters 的尺寸與方向。**

## 2. 標準尺寸 & 設定
**常見列印尺寸**：
- **48×36 in**（121.9×91.4 cm）— 美式最常見橫式。**36×48** — 直式版。
- **42×30 in**、**36×24 in** — 較小替代。
- **ISO A 系列（歐洲/公制）**：A0 = **841×1189 mm**、A1 = 594×841、A2 = 420×594。A0 是歐洲會議標準。

**數位/虛擬海報**：1920×1080（16:9 HD）、3840×2160（4K）、1600×1200（4:3）。

**方向**：直式適合文字多、窄板（上下流）；橫式適合視覺/STEM、寬板。配合會議展板方向。

**解析度/DPI**：
- 列印：所有點陣圖 **最終列印尺寸下 ≥300 DPI**（不是縮圖尺寸）。數位顯示 150 DPI 可接受。
- **向量 > 點陣**：PDF/SVG/EPS 無限縮放不失真，DPI 對它們無意義。plot/圖表/logo 優先向量。

**PowerPoint 設自訂尺寸**：
1. 開空白簡報，刪預設文字框。
2. **Design → Slide Size → Custom Slide Size**。
3. 輸入 Width/Height/Orientation。
4. 縮放提示選 **「Ensure Fit」**。

**56 吋陷阱**：PowerPoint 最大 **56×56 in**。要更大（如 48×96）→ **用一半尺寸（24×48）做、印刷廠放大 200%**，但點陣圖放大會失真，圖務必向量或超大尺寸。

## 3. 版面 & 設計最佳實踐
- **欄結構**：用 **2–4 欄**（48×36 橫式典型 3 欄），欄寬一致對齊。
- **閱讀動線**：眼睛 **欄內由上到下、再左到右橫跨**（報紙式）。動線可能混淆就標號。別讓讀者找。
- **視覺層級**：標題最大 → 章節標頭 → 內文 → 圖說。標頭一種風格、內文一種，全段一致。
- **標題列（頂帶）**：標題、作者、單位、logo（機構/會議/資助）。標題要隔著房間可讀。
- **視覺優先**：海報是視覺、不是貼牆論文。**砍文字、放圖**；圖文比要高；段落改條列/編號清單。
- **留白**：別塞滿。充足邊界與區塊間距提升可讀、避免「太擠」（頭號錯誤）。
- **距離可讀目標**：~4–6 ft → ~30 pt；~10 ft → ~48 pt；~12 ft → ~60 pt。標題十呎可讀，內文幾呎可讀。
- **章節結構兩法**：①經典 Intro/Background → Methods → Results → Discussion/Conclusion → References/Ack；②問題優先/結論優先（見 §6 #betterposter）。
- **對齊**：內文靠左。置中只用標題與圖說，別整段內文置中。

## 4. 字體
| 元素 | 大小（36×48 / 48×36） |
|---|---|
| **標題** | ~72–120 pt（常見 ~85） |
| **作者** | ~60 pt |
| **章節標題** | ~36–72 pt（常見 36–54） |
| **次標題** | ~54 pt |
| **內文** | **24–32 pt；絕不低於 24** |
| **圖說** | ~24 pt |
- **無襯線（Arial/Helvetica）** 用於標題/標頭與遠距可讀；**襯線（Times/Georgia）** 內文可接受——擇一致方案。全張**最多 2–3 種字型**。
- **字數**：全張 **< ~800 字**，越少越好。
- 標題與內文**別全大寫**（傷可讀）。

## 5. 配色 & 圖
- **對比**：深字淺底（或反之）強對比。測試文字在任何底色上都可讀。
- **色盲友善**：別只用紅/綠區分。用色盲友善調色盤——類別資料用 **Bang Wong palette**（Nature Methods 2011）；連續用 **viridis/cividis/plasma**。用**線型/標記/標籤**強化顏色，灰階也能讀。
- **一致**：全張圖表與標頭用同一有限調色盤；plot 內字型/色一致。
- **匯出高解析圖**：
  - plot/圖表/logo 優先 **向量 PDF/SVG/EPS**。
  - 點陣（照片）**最終尺寸 ≥300 DPI**（Nature/Science 線稿要 600–1200 DPI）。
  - matplotlib：
    ```python
    import matplotlib.pyplot as plt
    plt.savefig("figure.pdf", bbox_inches="tight")   # 向量（海報最佳）
    plt.savefig("figure.svg", bbox_inches="tight")
    plt.savefig("figure.png", dpi=300, bbox_inches="tight")  # 點陣備援
    ```
    向量與高 DPI 點陣**都出一份**。`bbox_inches="tight"` 保住所有標籤。
- 每張圖要有資訊性標題與軸標；100% 縮放確認不糊。

## 6. #betterposter（Mike Morrison）
概念（2019 爆紅 YouTube + OSF 範本）：海報攤位的人**狂掃描篩選**，所以把單一關鍵結果放正中央、用大字白話講。

**三區版面（橫式 v1）**：
- **中央「主結論 Bar」（the "___ Bar"）**：一句**大字、白話**講研究 takeaway（不是制式學術標題），大字實底。這是整張海報的頭條。
- 中央下方：**QR code** 連完整論文/聯絡。
- **左欄「無聲簡報」/概覽**：脈絡，讓海報沒人顧時自我說明。
- **右欄「彈藥 Bar」**：給想深聊的人的細節/圖/方法。

**版本演進**：v1.0「硬重置」剝到剩骨架（被批圖太小/缺、浪費空間）；v2.0 應回饋恢復**大圖與更多資料**；Hybrid 1.5 保留大結論但恢復較傳統細節欄（傳統與 v2.0 折衷）。

**證據與批評**：小型 pilot 眼動/偏好支持，但顯著性薄弱。主要反對是**情感捷思**——極簡海報可能「感覺不夠科學」即使溝通更好。要大膽溝通的場合用它；Hybrid 是安全中道。

## 7. LaTeX 最小骨架
**`beamerposter`**（建於 beamer）：見 [../templates/beamerposter_skeleton.tex](../templates/beamerposter_skeleton.tex)。要點：`\documentclass[final]{beamer}` + `\usepackage[orientation=landscape,size=a0,scale=1.4]{beamerposter}`；單一 `\begin{frame}` = 整張；`\begin{columns}[t]` 內 `\begin{block}{標題}...\end{block}`；`scale` 放大全部字級。

**`tikzposter`**（TikZ，block 模型）：見 [../templates/tikzposter_skeleton.tex](../templates/tikzposter_skeleton.tex)。要點：`\documentclass[25pt,a0paper,portrait]{tikzposter}`；`\column{<fraction>}`（加總約 1.0）；`\block{標題}{內文}` 核心單位；`\note{}` 便利貼；主題 Default/Board/Rays/Basic/Simple/Envelope/Wave。

## 8. 工作流 & 踩雷
**Do**：
- **從「最終尺寸」範本開始**（別做小再放大——除非 PowerPoint 半尺寸/200% 那招，且圖保持向量）。
- 開工前確認會議**尺寸+方向**。
- 圖盡量**向量**；點陣只用照片、最終尺寸 ≥300 DPI。
- 送印前**嵌入或外框化字型**（PowerPoint：File→Options→Save→Embed fonts；Illustrator/Inkscape：文字轉路徑），免印刷廠換字型。
- **出 PDF 列印**（保向量與版面）；PowerPoint 也匯 PDF 別交 .pptx。
- 查**出血/邊界**，留安全邊，問印刷廠 bleed 規格。
- **100% 縮放校稿**：確認無糊圖、字可讀、拼字。
- 檔案大小合理（只降超大點陣，向量本來就小）。

**常見錯誤（避免）**：文字過多/整牆段落（>800 字）；低解析圖印出糊；字太小（內文 <24 pt）；版面過擠無留白、動線不明；只用紅/綠、對比差；各區字型/色不一致；用制式學術標題而非清楚 takeaway；忘了嵌字型導致印出亂碼。

---

### 主要來源
- Repo：[SuperBruceJia/Poster_Template](https://github.com/SuperBruceJia/Poster_Template)、[MIT-BECL/Poster_Resources](https://github.com/MIT-BECL/Poster_Resources)
- 尺寸/設定：Fourwaves、UNC PowerPoint poster setup｜版面/字體：UCLA、U Idaho library guides
- LaTeX：Overleaf Posters｜圖：Matplotlib high-res export
- #betterposter：Astrobites、Publication Plan、UC Davis better-scientific-poster、BEACON
