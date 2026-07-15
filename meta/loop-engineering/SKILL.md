---
name: loop-engineering
description: 把「一次一句 prompt 手動盯」升級成「自己會觸發、自檢、報告的迴圈系統」。當使用者要「讓某個自動化更可靠、加驗證/自檢、避免亂發或幻覺直接送出、設 token/次數/時間上限避免燒錢、把任務排程/定時跑、worker+checker 兩段式、重試帶 feedback、budget 上限、L1→L2→L3 自主度、把庫巴/行銷輪播/n8n/看門狗這類自動化做穩」時使用，或問「loop engineering、verification loop、grade before done、budget before start」時使用。附可直接套用的 verified_run.py（驗證迴圈 + budget，零相依）。
---

# 🔁 Loop Engineering — 讓工作自己跑、還跑得可靠

一句話：**別再一句一句想 prompt，去設計那個「沒有你也能跑」的迴圈。** 你從「操作者」變成「設計者」。
三條鐵律：**Grade before done（做完要先驗）· Budget before start（開跑先設上限）· Report always（永遠回報）。**

萃取自 [hardness1020/awesome-agent-architecture §21](https://github.com/hardness1020/awesome-agent-architecture)（MIT）＋ Claude Code 既有原語。完整概念在 [references/patterns.md](references/patterns.md)；可直接套的程式在 [scripts/verified_run.py](scripts/verified_run.py)。

## 🎯 四層迴圈（一層包一層，各答一個問題）
| 迴圈 | 回答 | 你手上對應 |
|---|---|---|
| **Agent loop** | 這一步怎麼做完 | 模型呼叫工具直到完成 |
| **Verification loop** ⭐新關鍵 | 是不是**真的**做完了 | worker 產出 → 獨立 checker 依 rubric 打分 → 沒過帶 feedback 重試 → budget 花完 escalate |
| **Event loop** | 工作**何時**開始 | cron、webhook、channel（你的 Telegram 庫巴） |
| **Improvement loop** | 系統有沒有**變好** | trace/觀測回頭調 harness/skill/model |

## ⭐ 核心缺口：加上 Verification Loop
你現有的自動化（庫巴、行銷輪播、n8n、看門狗）大多已有 event loop（定時觸發），**缺的是中間這層自檢**。內層 loop 是「模型說完成就停」；驗證迴圈讓「完成」變成**被檢查過的宣稱**：

```python
# scripts/verified_run.py — 直接 import 用
from verified_run import verified_run, needs_all, human_escalate

def worker(prompt):   # 你的產出：呼叫 LLM / 跑 stock.py / 組文案
    return generate(prompt)

def checker(task, out):                       # 「另一個」判斷，別讓 worker 自評
    return needs_all(out, must_contain=["資料時間", "約延遲15分"])

r = verified_run("查 2330 股價", worker, checker, budget=2)
r["ok"] and deliver(r["output"]) or human_escalate(r)   # 通過才發；沒過告警給人
```
**三個要點**：① checker 要**乾淨 context 的獨立判斷**（worker 自評幾乎都放行）② rubric **固定在迴圈外**（模型只能滿足、不能改）③ 失敗評語是**資料**，帶進下一次重試。

## 💰 Budget：開跑前先設「模型講不贏」的上限
每個迴圈都要一個模型**無法用話術繞過**的天花板：次數 / token / wall-clock / dry-counter（連 K 輪沒新發現就停）。**由 harness 強制，不是拜託模型停**。
- `verified_run` 的天花板就是 `range(budget)`，第 `budget+1` 次不會發生。
- 在 **Claude Code Workflow** 裡：`budget.remaining()` 是硬上限，超過 `agent()` 直接 throw；另有每 workflow **1000 agent** 終身上限兜底。
> 名言：**沒 grader 的迴圈自動化了工作；沒 budget 的迴圈自動化了帳單。**

## 🪜 自主度階梯（一次只升一級，用權限 gate）
- **L1 · Report**：迴圈只讀取＋回報，人來動手。
- **L2 · Assisted**：迴圈起草改動，人按核准。
- **L3 · Unattended**：迴圈直接動，人事後稽核。
→ **只有在「當前這級無聊到都對」之後，才升下一級。** 對照你的記憶：動設定/花錢/對外的步驟先問過（[[no-changing-settings-without-consent]]、[[verify-before-execute]]）。

## 🧰 用哪個原語（Claude Code）
| 需求 | 用 |
|---|---|
| 定時／週期重複跑一個 prompt/指令 | `/loop <interval> <prompt>`（省略 interval 則自我調速） |
| 自我調速的下一次喚醒、`stop:true` 收工 | `ScheduleWakeup` |
| 多 agent 組合、worker/checker、fan-out、budget | `Workflow`（`agent()`/`pipeline()`/`parallel()`、`budget.remaining()`）— 其 adversarial verify / judge panel / loop-until-dry 就是驗證迴圈 |
| 固定排程、跨 session | cron（你的看門狗、9:00/20:00 輪播） |
| 事件觸發、對外送 | channels（Telegram 庫巴）、webhook、n8n |

## 🚀 落地到你的自動化（建議順序）
1. **庫巴回覆**（股價/翻譯/記帳）：`worker=產草稿`、`checker=needs_all(["資料時間","約延遲15分"])` 或 `llm_checker`，**通過才 reply**，沒過重試一次再不行就發「查詢中／查無」而非亂報 → 直接落實你的「先查證再執行」鐵則。
2. **每日行銷輪播（9:00/20:00）**：發文前加 checker（字數/必含 CTA/無佔位符/圖有生成成功），沒過就重生成，budget=2，花完告警你手動看。
3. **看門狗 / n8n 排程**：event loop 已有，補「每次都回報」（heartbeat + pass rate/cost），避免 silent drift。
4. 想更進階：用 `Workflow` 把「產→驗→重試」寫成腳本，跑不穩的任務並行多個再挑最佳。

## ☠️ 六大失敗模式（照著避）
1. **沒 stop 條件** → 燒 token 到看到帳單。解：harness 強制 次數/token/時間 上限。
2. **自己評自己** → 驗了等於沒驗。解：獨立 checker + 迴圈外固定 rubric。
3. **橡皮圖章 rubric**（總是 PASS）→ 把爛貨標成已驗證。解：對抗式（叫 checker 盡量挑錯、拿不準就 FAIL）+ 定期人工抽查。
4. **太早放無人管**（沒驗過 L1 就給 L3 寫權限）。解：一級一級爬，用權限 gate。
5. **Silent drift**（沒人看它退化）。解：heartbeat、永遠送出的報告、pass rate/cost 指標。
6. **狀態失憶**（每次重跑同樣的活）。解：把發現寫進 memory/工作紀錄，開跑先讀。

> 完整四層迴圈細節、per-system 對照、runnable 測試 → [references/patterns.md](references/patterns.md)。
