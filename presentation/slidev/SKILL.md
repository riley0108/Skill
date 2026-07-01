---
name: slidev
description: 用 Slidev（slidevjs，開發者取向的 markdown 投影片工具，基於 Vite+Vue+UnoCSS）做簡報。當使用者要「用 markdown / 寫程式碼的方式做投影片、技術分享 slides、把 slides.md 變成簡報、程式碼高亮逐行點開、Mermaid 圖、LaTeX 數學式、Monaco 可編輯程式碼、用 layout 排版、套 theme、匯出 PDF/PNG/PPTX、build 成網站部署 GitHub Pages/Netlify、presenter 簡報者模式」時使用。涵蓋 CLI、slides.md 語法、內建 layouts、點擊動畫、主題樣式、匯出與部署、踩雷。
---

# 🖥️ Slidev — 開發者的 markdown 投影片

Slidev = 把單一 `slides.md` 變成簡報，dev server / presenter 模式 / 匯出都由 Vite + Vue 3 + UnoCSS + Shiki 驅動。適合工程簡報：程式碼高亮、逐行點開、Mermaid/LaTeX、用編輯器跟 git 管版本。

完整語法與 CLI 在 **[references/reference.md](references/reference.md)**（8 大區）。本檔是導覽 + 最容易踩的雷。

## 🚀 30 秒起步
```bash
npm init slidev@latest      # 建專案（需 Node >= 20.12.0）
# 進專案後：
npm run dev                 # = slidev --open，dev server 在 http://localhost:3030
```
編輯 `slides.md` → 存檔即時熱更新。手機/另一台控場：`slidev --remote` 再開 `/presenter`。

## ✍️ slides.md 最小範例
```md
---
theme: seriph
title: 我的簡報
transition: slide-left
---

# 第一頁

Hello **Slidev**

---
layout: two-cols
---

# 左欄

::right::

# 右欄

<!-- 這是 presenter 講者備註（放在每頁「最後」才會生效） -->
```

## 🗺️ reference.md 8 大區
1. **Setup & CLI** — `dev`/`build`/`export`/`format`、`--open`/`--remote`/`--port`
2. **slides.md 結構** — headmatter（整份設定）vs 每頁 frontmatter；`src:` 匯入外部 slides
3. **內建 layouts** — default/center/cover/section/two-cols/image-left/image-right/quote/fact/statement…（含 `::right::` slot）
4. **內容功能** — 程式碼逐行高亮 `{2,3}` 與點擊 `{1|2|3}`、Monaco `{monaco}`、Twoslash、LaTeX `$$`、Mermaid、Vue 元件、`v-click`/`v-clicks`/`v-motion`、講者備註、Iconify 圖示
5. **樣式 & 主題** — `theme:` 拉 npm 套件、UnoCSS utility class、每頁 scoped `<style>`、addons
6. **導覽 & presenter 模式** — 快捷鍵、`/presenter`、`/overview`、繪圖標註、錄影
7. **匯出** — PDF/PNG/PPTX（要 `playwright-chromium`）、`--with-clicks`/`--range`
8. **踩雷**

## ☠️ 最容易踩的 5 個雷
1. **匯出要先裝 Playwright** —— `slidev export`（PDF/PNG/PPTX）沒裝 `npm i -D playwright-chromium` 會失敗。
2. **`---` 分頁符前後要有空行** —— 否則 `---` 會被當成 YAML frontmatter 而不是分頁。
3. **第一個 YAML 區塊是 headmatter（整份設定）**，後面每頁開頭的 YAML 是「該頁」frontmatter。theme/fonts 這種整份設定別寫到個別頁。
4. **講者備註要放在每頁「最後」** —— HTML 註解 `<!-- ... -->` 只有在頁尾才會變成 presenter note，頁中間的會被忽略。
5. **PPTX/PNG 匯出是「圖片」** —— 文字不可選、Monaco/iframe/即時互動會失去。要保留互動就 `slidev build` 成網站部署，別用 export。

## 📤 匯出 & 部署速查
```bash
npm i -D playwright-chromium          # 匯出前置（一次）
slidev export                          # → PDF
slidev export --format pptx            # → PPTX（每頁一張圖）
slidev export --format png --with-clicks   # 每個點擊步驟一張 PNG
slidev build --base /repo-name/        # 出 dist/ 靜態站（GitHub Pages 要 --base 頭尾都帶 /）
```
GitHub Pages / Netlify(`publish=dist`) / Vercel(rewrite 到 index.html) 皆可 host `dist/`。

> 來源：[slidevjs/slidev](https://github.com/slidevjs/slidev) + [sli.dev](https://sli.dev) 官方文件，核對於 2026-06（v51+）。
