# Slidev Reference (v51+, 2026)

> markdown 投影片工具。Slides 放在單一 `slides.md`，dev server / presenter / 匯出由 Vite + Vue + UnoCSS + Shiki 驅動。核對於 sli.dev 官方文件，2026-06。

## 1. Setup & CLI

**需求**：Node.js **>= 20.12.0**。

**建專案：**
```bash
npm init slidev@latest     # npm
pnpm create slidev          # pnpm
yarn create slidev          # yarn
bun create slidev           # bun
# 免安裝線上試：https://sli.dev/new
```

**典型 `package.json` scripts：**
```json
{
  "scripts": {
    "dev": "slidev --open",
    "build": "slidev build",
    "export": "slidev export"
  }
}
```

**免本地安裝跑**：`npx @slidev/cli`（或 `npx slidev`）。

**CLI 指令：**

| 指令 | 用途 |
|---|---|
| `slidev [entry]` | 啟動 dev server（預設 entry `slides.md`） |
| `slidev build [entry]` | build 靜態 SPA 到 `dist/` |
| `slidev export [...entry]` | 匯出 PDF / PNG / PPTX / MD |
| `slidev format [entry]` | 重新格式化 markdown |
| `slidev theme [eject]` | 主題操作（`slidev theme eject` 把主題複製進專案） |

**dev server flags：**

| Flag | 預設 | 說明 |
|---|---|---|
| `--port`, `-p` | `3030` | dev server 埠 |
| `--open`, `-o` | `false` | 啟動時開瀏覽器 |
| `--remote [password]` | – | 對網路開放（遠端控制/手機）；可選密碼 |
| `--bind` | `0.0.0.0` | 綁定位址 |
| `--base` | `/` | base URL 路徑 |
| `--force`, `-f` | `false` | 強制 Vite 重新優化依賴 |
| `--theme`, `-t` | – | 覆寫主題 |

```bash
slidev                       # dev server http://localhost:3030
slidev --open --port 8080    # 自訂埠、自動開
slidev --remote              # LAN 分享；另一台開 /presenter 控場
slidev --remote mypassword   # 加密碼
```

## 2. slides.md 結構

Slides 用獨立一行的 `---` 分隔，**前後要有空行**（`---` 緊貼文字會被當 YAML 解析，不是分頁）：

```md
# Slide 1

Hello, **Slidev**!

---

# Slide 2

Content
```

**Headmatter vs frontmatter**：檔案最上方的**第一個** YAML 區塊是 **headmatter** — 設定整份 deck。後續每頁開頭的 YAML 是**該頁 frontmatter** — 只設定那一頁。

**Headmatter（deck 設定）範例：**
```md
---
theme: seriph
title: Welcome to Slidev
background: https://cover.sli.dev
class: text-center
highlighter: shiki
lineNumbers: false
transition: slide-left
mdc: true
fonts:
  sans: Robot
  mono: Fira Code
---

# First slide
```

**每頁 frontmatter**（套 layout / 背景 / class 到單頁）：
```md
---
layout: center
background: /background-1.png
class: text-white
transition: fade-out
---

# Second slide
```

Layout 用 frontmatter 的 `layout:`（`center`/`two-cols`…）。`class:` 加 CSS/UnoCSS class 到頁根。

**匯入/重用 slides** — frontmatter 指向外部 md：
```md
---
src: ./pages/intro.md       # 把那檔的所有 slides 匯入此處
---
```
匯入頁的 frontmatter 會跟被匯入檔的 headmatter 合併（匯入頁的 key 優先）。

## 3. 內建 Layouts

| Layout | 說明 |
|---|---|
| `default` | 一般內容 |
| `center` | 內容置中 |
| `cover` | 封面/標題頁 |
| `intro` | 介紹頁：標題/描述/作者 |
| `section` | 新章節起始 |
| `statement` | 大字宣告 |
| `fact` | 醒目呈現一個事實/數字 |
| `quote` | 引言 |
| `two-cols` | 左右兩欄（用 `::right::` slot） |
| `two-cols-header` | 上方橫跨表頭 + 左右兩欄（`::left::`/`::right::`） |
| `image` | 影像為主內容（`image` 屬性） |
| `image-left` / `image-right` | 影像在左/右，內容在另一邊 |
| `iframe` / `iframe-left` / `iframe-right` | 網頁 iframe（`url` 屬性） |
| `full` | 用滿全螢幕 |
| `end` | 結尾頁 |
| `none` | 完全不套樣式 |

**`two-cols` + `::right::` slot：**
```md
---
layout: two-cols
---

# Left
左邊內容

::right::

# Right
右邊內容
```

**`two-cols-header`**（表頭橫跨兩欄）：
```md
---
layout: two-cols-header
---

橫跨兩欄的表頭

::left::

# 左欄

::right::

# 右欄
```

**`image-right` 帶屬性：**
```md
---
layout: image-right
image: /my-image.png
class: my-cool-content-on-the-left
---

# 左邊內容
```
`::name::` 是 Vue 具名 slot 的語法糖（等於 `<template v-slot:right>`）。

## 4. 內容功能

**程式碼逐行高亮** — `{}` 內放行號：
```` ```ts {2,3} ````（高亮第 2、3 行）。範圍與關鍵字：`{2-4}`、`{all}`、`{none}`、`{hide}`。**點擊逐步**用 `|`：
```` ```ts {1|2|3-5} ````（先亮第 1 行，再 2，再 3-5）。可加 `{at:'+5', lines:true, startLine:5}`、`maxHeight:'200px'`。

**Monaco 編輯器**（頁內可編輯）：```` ```ts {monaco} ````。變體：`{monaco-run}`（可執行顯示輸出）、`{monaco-diff}`（差異對比，用 `~~~` 分隔）、高度 `{height:'300px'}`。

**Twoslash**（TS 型別 hover/inline）：
```` ```ts twoslash ````，用 `^?` 標記在該行下方 inline 顯示推斷型別。

**Shiki Magic Move** — 多個程式碼區塊間 token 逐字動畫，用 `` magic-move `` 包住多個 fenced block。

**LaTeX 數學**（KaTeX）。Inline 用單 `$`，block 用 `$$`：
```md
Inline: $\sqrt{3x-1}+(1+x)^2$

$$
\begin{aligned}
\nabla \cdot \vec{E} &= \frac{\rho}{\varepsilon_0}
\end{aligned}
$$
```
Block 數學支援像程式碼的高亮/點擊：`$$ {1|3|all} ... $$`。化學式 mhchem：`vite.config.ts` 加 `import 'katex/contrib/mhchem'`。

**Mermaid 圖：**
```` ```mermaid ````，可加選項 `{theme: 'neutral', scale: 0.8}`。**PlantUML**：```` ```plantuml ````。

**Vue 元件** — `components/` 資料夾自動匯入（免手動 import）：
```md
<MyComponent :count="4" />
<Toc />
<Link to="42">跳到第 42 頁</Link>
```
內建元件：`Toc`、`Link`、`Arrow`、`Transform`、`AutoFitText`、`VClick`/`VClicks`/`VSwitch`、`SlideCurrentNo`、`SlidesTotal`、`Youtube`、`Tweet`、`RenderWhen`、`LightOrDark`。

**點擊動畫：**
```md
<v-click>點一下出現</v-click>
<div v-click class="text-xl">也是點一下</div>

<v-clicks>

- 項目 1
- 項目 2
- 項目 3

</v-clicks>

<div v-click>顯示</div>
<div v-after>跟前一個同一次點擊一起顯示</div>
```
- `v-clicks` 逐個顯示子元素；支援 `depth`（巢狀清單）、`every`（每 N 個一組）。
- `.hide`：點擊後消失 `<div v-click.hide>`。
- `at` 定位：絕對 `v-click="3"`；相對 `v-click="+2"`；範圍 `v-click.hide="[2, 4]"`。
- 表達式取點擊數：`<span v-if="$clicks > 3">`。

**v-motion**（位置/縮放動畫，可綁點擊）：
```md
<div v-motion :initial="{ x: -80 }" :enter="{ x: 0 }"
     :click-1="{ x: 0, y: 30 }" :click-2-4="{ x: 40 }">
  Slidev
</div>
```

**講者備註** — 每頁**結尾**的 HTML 註解變成 presenter note（支援 Markdown/HTML）；頁中間的註解被忽略：
```md
# 標題

內容

<!-- 這是 **講者備註**，只在 presenter 模式顯示 -->
```

**圖示**（Iconify via UnoCSS）— 用 `<collection-name />`，先裝 collection：
```bash
npm i -D @iconify-json/mdi @iconify-json/carbon
```
```md
<mdi-account-circle />
<carbon-logo-github />
<uim-rocket class="text-3xl text-red-400 animate-ping" />
```
瀏覽：icones.js.org / icon-sets.iconify.design。

**MDC（Markdown Components）** — headmatter 開 `mdc: true`：
```md
[紅字]{style="color:red"} 與 [粗體]{.font-bold}

::block-component{.flex.gap-4}
預設 slot 內容
::
```

## 5. 樣式 & 主題

**主題** — headmatter 設 `theme:`。短名對應 npm 套件 `slidev-theme-<name>`（官方用 `@slidev/theme-<name>`）；本地主題用相對路徑：
```md
---
theme: seriph          # → @slidev/theme-seriph
# theme: ./my-theme    # 本地
---
```
未安裝會提示安裝，或手動 `npm i @slidev/theme-seriph`。官方主題：`default`、`seriph`、`apple-basic`、`bricks`、`shibainu`…

**Addons** — headmatter 陣列：
```md
---
addons:
  - excalidraw
---
```

**UnoCSS / utility class** — Slidev 內建 UnoCSS（Wind preset，Tailwind/Windi 風格）+ attributify + icons：
```md
<div class="grid grid-cols-2 gap-4 text-blue-500 mt-8">…</div>
```

**`class:` frontmatter** — 加 class 到頁根：`class: text-center text-white`。

**每頁 scoped `<style>`** — 頁內 `<style>` 自動只作用該頁：
```md
# 紅標題

<style>
h1 { color: red; }
</style>
```

**全域樣式** — `styles/index.css` 自動注入 app root。注意：全域 CSS 也會影響 presenter UI，最好 scope 到單頁或包在 `.slidev-layout` 下：
```css
.slidev-layout .grid { gap: 1rem; }
```

**專案目錄結構：**
```
your-slidev/
├── slides.md          # 主入口（簡報內容）
├── components/        # 自動匯入的 Vue/MD 元件
├── layouts/           # 自訂 layout
├── public/            # 靜態資源（served at /）
├── styles/            # 全域樣式
├── setup/             # setup hooks（shiki/monaco/mermaid/main…）
├── vite.config.ts
└── package.json
```

## 6. 導覽 & Presenter 模式

**快捷鍵（slides 畫面）：**

| 鍵 | 動作 |
|---|---|
| `right` / `space` | 下一個動畫或頁 |
| `left` | 上一個動畫或頁 |
| `up` / `down` | 上/下一頁 |
| `f` | 全螢幕 |
| `o` | 切換總覽 |
| `d` | 切換深色模式 |
| `g` | 「跳到第幾頁」 |

**特殊路由**（`<port>` 預設 3030）：
- **Presenter**：`http://localhost:<port>/presenter` — 當前+下一頁、備註、計時；配 `--remote` 可控所有連線端。
- **Overview**：`/overview` — 所有頁網格（或按 `o`）。
- **Notes editor**：`/notes-edit`。
- **Export view**：`/export`。

其他：導覽列（全螢幕/深色/相機/錄影/presenter/設定）、繪圖標註（drauu，`drawings.persist` 存進 deck）、相機 webcam 疊加、錄影。

## 7. 匯出

PDF/PNG/PPTX 匯出需 **playwright-chromium**：
```bash
npm i -D playwright-chromium
```

```bash
slidev export                       # → slides-export.pdf（預設）
slidev export --format png          # 每頁一張 PNG
slidev export --format pptx         # PPTX（每頁為圖；文字不可選）
slidev export --format md           # 編譯後圖片的 markdown
slidev export --with-clicks         # 每個點擊步驟一頁（-c）
slidev export --range 1,6-8,10      # 只匯出這些頁
slidev export --output talk.pdf     # 自訂檔名
slidev export --dark                # 深色版
slidev export --timeout 60000       # 渲染逾時（ms，預設 30000）
slidev export --with-toc            # PDF 大綱書籤
slidev export --per-slide           # 逐頁渲染（排版問題的解法）
```
也可從瀏覽器匯出：開 `/export` 或 More-options 選單的「Export」（Chromium 系最佳）。

**Build & host 成網站**（保留互動，跟 export 不同）：
```bash
slidev build                                  # → dist/
slidev build --base /talks/my-cool-talk/      # 子路徑（頭尾都要 /）
slidev build --out my-folder                  # 自訂輸出目錄
slidev build --without-notes                  # 移除講者備註
slidev build --download                        # 內含可下載 PDF
```
預覽：`npx vite preview`。

**Hosting：**
- **GitHub Pages**：`--base /<repo-name>/`，served at `https://<user>.github.io/<repo>/`。
- **Netlify**（`netlify.toml`）：`publish='dist'`、`command='npm run build'`。
- **Vercel**：`vercel.json` 把所有路由 rewrite 到 `/index.html`。
- **Docker**：`tangramor/slidev:latest`。

## 8. 踩雷

- **匯出需 Playwright**：沒 `npm i -D playwright-chromium`，export 會失敗。
- **`---` 前後要空行**：否則被當 frontmatter 不是分頁。
- **第一個 YAML 是 headmatter**（整份）；後續頁開頭 YAML 是該頁 frontmatter。theme/fonts 別放個別頁。
- **備註要放每頁最後**：頁中間的 HTML 註解被忽略。
- **全域 CSS 會漏進 presenter UI**：scope 到單頁或包 `.slidev-layout`。
- **`--base` 頭尾都要 `/`**（GitHub Pages 常見錯）。
- **PPTX/PNG/MD 匯出是圖片**：文字不可選、互動失去；要互動就 host `build` 輸出。
- **Node >= 20.12.0**，舊版起不來。

**來源**：sli.dev/guide、syntax、animations、builtin/layouts、builtin/components、builtin/cli、guide/exporting、guide/hosting、features（mermaid/latex/monaco/twoslash/icons/mdc）。
