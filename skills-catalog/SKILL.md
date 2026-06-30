---
name: skills-catalog
description: 大型外部 skill 集合的目錄索引 —— 查找並「按需安裝」現成的 Claude/Agent skills。當使用者問「有沒有現成的 skill 做 X／有哪些可用的 skill／幫我找一個 ___ 的 skill／安裝某個 knowledge-work plugin／從 anthropics 或 awesome-agent-skills 抓某個 skill」時使用。索引涵蓋 anthropics/knowledge-work-plugins（212 個企業知識工作 skill，18 領域）與 VoltAgent/awesome-agent-skills（~1205 條各廠商 skill：Supabase/Stripe/Terraform/Python/TypeScript/Rust/NVIDIA NeMo 等）。這兩批未 vendor，本 skill 教你怎麼挑、怎麼單獨裝進 ~/.claude/skills/。
---

# 🗂️ Skills Catalog — 外部 skill 目錄索引

查找並按需安裝現成的 skill。這裡索引的是**量太大、不整批 vendor**的兩大集合；要哪個再單獨裝。

> Anthropic 官方 17 個精選 skill（docx/pdf/pptx/xlsx、mcp-builder、skill-creator、canvas-design、brand-guidelines、frontend-design、web-artifacts-builder、webapp-testing、theme-factory、algorithmic-art、internal-comms、doc-coauthoring、slack-gif-creator、claude-api）**已經 vendor 進本 repo**，直接可用，不在此索引內。

## 📇 兩份索引
- **[references/knowledge-work-plugins.md](references/knowledge-work-plugins.md)** — [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) 的 **212 個 skill**，按 18 領域（data / engineering / finance / legal / sales / marketing / design / small-business / partner-built…）列出名稱與用途。企業知識工作流為主。
- **[references/awesome-agent-skills.md](references/awesome-agent-skills.md)** — [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) 的 **~1205 條** skill，按廠商/語言分類（Supabase / Stripe / Terraform / Better Auth / Firecrawl / ClickHouse / Python / TypeScript / Rust / .NET / Java / NVIDIA NeMo 系列…）列出各區段與 skill 數。

## 🔎 怎麼用
1. 使用者問「有沒有做 X 的 skill」→ 在上面兩份索引（用 grep）找對得上的 → 回報名稱、來源、用途。
2. 找到後問要不要裝 → 確認後照下方「按需安裝」拉進 `~/.claude/skills/`。
3. 索引只有名稱+簡述；要看完整內容就去該 repo 對應路徑 Read SKILL.md。

```bash
# 在索引裡搜尋（例：找 reconciliation / dashboard / terraform 相關）
grep -i "dashboard" ~/.claude/skills/skills-catalog/references/*.md
```

## 📥 按需安裝一個 skill
**A. 從 knowledge-work-plugins 裝單一 skill**（212 之一）：
```bash
# 淺 clone（已在 scratchpad 有就略過），複製目標 skill 資料夾進來
TMP=$(mktemp -d); git clone --depth 1 https://github.com/anthropics/knowledge-work-plugins.git "$TMP/kw"
# 例：裝 finance 的 reconciliation
cp -r "$TMP/kw/finance/skills/reconciliation" ~/.claude/skills/
rm -rf "$TMP"
```
（各 skill 實際路徑見索引；多數是 `<領域>/skills/<skill-name>/SKILL.md` 或 `<領域>/<plugin>/skills/<name>/`。複製前先 `find` 確認。）

**B. 從 awesome-agent-skills 裝**：該清單是**指向各廠商自己 repo 的連結**，不是單一 repo。流程：在 [references/awesome-agent-skills.md](references/awesome-agent-skills.md) 或原清單找到該 skill → 點進它的來源 repo → clone 並把 `SKILL.md` 所在資料夾複製進 `~/.claude/skills/`。很多廠商（Supabase/Stripe/Terraform…）的 skill 放在自家 repo 的 `.claude/skills/` 或 `skills/` 下。

**C. 整個 plugin 當 marketplace 載入**（進階）：knowledge-work-plugins 的領域資料夾本身是 Claude Code plugin，可用 `/plugin` marketplace 機制整包載入（會一次帶進該領域所有 skill）。零散需求建議用 A 只挑單一 skill，避免一次塞太多干擾自動觸發。

## ⚠️ 安裝後注意
- 每裝一個就多一個會**自動觸發**的 skill；別亂裝整批，挑真的會用的。
- 裝完重開 Claude Code 才會載入。裝進來的記得到本 repo README 補一行索引。
- 名稱若跟現有 skill 撞名（如又一個 `claude-api`），會衝突——先改 frontmatter 的 `name:` 或別裝。

## 🧩 anthropics/claude-code（CLI 本體，非 skill）
[anthropics/claude-code](https://github.com/anthropics/claude-code) 是 Claude Code CLI 本身，不是 skill。要問 Claude Code 功能/hooks/MCP/設定，用 `claude-code-guide` agent 或 `claude-api` skill；本 repo 不收它的內容。

> 來源：anthropics/knowledge-work-plugins（Apache-2.0）、VoltAgent/awesome-agent-skills、anthropics/skills（17 個已 vendor）。索引產於 2026-06，數量會隨上游變動。
