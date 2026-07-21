# Loop Engineering — 完整 patterns 參考

> 萃取自 [hardness1020/awesome-agent-architecture §21](https://github.com/hardness1020/awesome-agent-architecture)（MIT）＋ Claude Code 原語。核對 2026-07。

## 心法：工程重心的轉移
每一次模型呼叫外面加一個機制；Loop Engineering 是把它們**組合**起來。與其一個 turn 一個 turn 下 prompt，不如打造外層系統：**找出要做的工作 → 把 agent 跑起來 → 檢查輸出 → 決定下一步**。人從操作者變設計者。

外層迴圈必須：
1. 由 **trigger 啟動**，不是只靠 user。
2. 輸出**先通過檢查**才算完成。
3. 靠 **budget** 停下，不是靠運氣。
4. **存下狀態**，下次接著做而非重來。
5. **回報**發生了什麼，就算沒人在看。

少了這層，外層迴圈就是「人」：下 prompt、讀、判斷、重試全手動；人一停，agent 就停。

## 四層迴圈
1. **Agent loop**：呼叫工具直到任務看起來完成。答：這一步怎麼做完。
2. **Verification loop**：拿 rubric 為輸出打分，沒過帶 feedback 重試到 budget 用完。答：是不是真的完成。
3. **Event loop**：cron / webhook / channel 啟動執行。答：工作何時開始。
4. **Improvement loop**：trace 與 eval 回頭改 harness 配置、skill、model。答：系統有沒有變好。成熟時它改的是 harness 本身——從 trace 挖弱點、提出範圍受限的修改、用 regression 驗證；迴圈結構本身變成可搜尋的空間，而非手工模板。

```
trigger(cron/webhook/channel) → agent loop → candidate → grader
   grader --fail(budget left)--> agent loop（帶 feedback 重試）
   grader --budget spent------> escalate to human
   grader --pass-------------> deliver → traces ⤾ tune harness
```
資料由內往外流：trigger fire → 把 prompt 入 queue → agent loop 產候選 → grader 打分 → 沒過且有 budget 帶 feedback 重試、過了就經該 task 的 channel 投遞 → 這次執行記成 trace → improvement loop 讀它決定 harness 哪裡改。

## Verification loop 參考實作
（完整可跑版在 [../scripts/verified_run.py](../scripts/verified_run.py)）

```python
def verified_run(task, worker, checker, budget=2):
    feedback = ""
    attempts = []
    for n in range(1, budget + 1):                 # range() 就是天花板，harness 強制
        out = worker(task + feedback)              # 內層 agent loop
        verdict = checker(task, out)               # 獨立 checker（乾淨 context）
        attempts.append({"attempt": n, "passed": verdict["passed"], "reason": verdict["reason"]})
        if verdict["passed"]:
            return {"ok": True, "output": out, "attempts": attempts}
        feedback = f"\n\n上一次被退：{out}\n原因：{verdict['reason']}\n修正後再答。"
    return {"ok": False, "output": None, "attempts": attempts}   # budget 花完：escalate
```
- **grader 是獨立、乾淨 context 的 agent**：worker 自評幾乎都放行。
- **rubric 固定在迴圈外**：模型只能滿足、不能改寫。
- **feedback 是資料**：失敗評語帶進重試，讓第二次知道第一次錯在哪。
- **`ok:False` 是 escalation 訊號**：把嘗試紀錄交給人，不無限重試。

## Budget 與 stop 條件
每個迴圈都要一個模型無法用話術繞過的天花板：**iteration 次數 / token budget / wall-clock / dry-counter（連 K 輪沒新發現就停）**。**harness 強制天花板，拜託模型停只是 hint 不是 stop 條件。**

## 自主度階梯（Maturity）
- **L1 · Report**：迴圈讀取＋回報，人動手。
- **L2 · Assisted**：迴圈起草改動，人核准。
- **L3 · Unattended**：迴圈直接動，人事後稽核。

是**權限決策**。只有在「當前這級無聊到都對」之後，才升一級。

## Per-system 對照
| 系統 | Verification | Event loop | Improvement loop |
|---|---|---|---|
| **Claude Code** | 腳本化 verify stage + 對抗式 pattern | cron、自我調速 wakeup、remote trigger | 可續跑的 workflow；原始碼中無封閉迴圈 |
| **Hermes Agent** | 委派 maker/checker；無內建 grader | gateway cron + 受限工具集 | curator agent 從使用中整併 skill |

### Claude Code 原語（你手上就有）
- `/loop <interval> <prompt>` 週期重跑；省略 interval 則模型用 `ScheduleWakeup` 自我調速，`stop:true` 結束。
- Sentinel prompt（`<<autonomous-loop>>`、`<<autonomous-loop-dynamic>>`）在 fire 時才解析迴圈指令，而非 create 時凍結。
- `Workflow` 直接把組合寫成腳本：`agent()`/`pipeline()`/`parallel()` fan-out。其記載的 quality pattern 本身就是驗證迴圈：**adversarial verify、judge panel、loop-until-dry**。
- `budget.remaining()` 讓 token 目標變硬上限，超過 `agent()` throw；每 workflow **1000 agent** 終身上限兜底 runaway。
- `resumeFromRunId` 從快取重播已完成的 `agent()`，固定腳本可續跑不重來。
- cron 與 remote trigger 供給 event loop。

## 六大失敗模式與解法
| 失敗 | 症狀 | 解法 |
|---|---|---|
| **無 stop 條件** | 重試燒 token 到有人看到帳單 | harness 強制 次數/token/時間 budget |
| **自己評自己** | worker 放行自家輸出，驗了等於沒驗 | 獨立 checker agent + 迴圈外固定 rubric |
| **橡皮圖章 rubric** | grader 總 PASS，把爛貨標成已驗證 | 對抗式 verify（叫它挑錯/拿不準就 FAIL）+ 定期人工抽查 |
| **太早 unattended** | 沒驗過 L1 就給 L3 寫權限 | 一級一級爬，權限 gate |
| **Silent drift** | 無人管的迴圈退化沒人發現 | heartbeat、永遠送出的報告、pass rate/cost 指標 |
| **狀態失憶** | 每次重跑同樣的活 | 把發現寫進 memory/工作紀錄，開跑先讀 |
| **自我編輯 harness 逃脫 gate** | improvement loop 能改到 gate 自己的碼 | 權限與 budget 放在迴圈改不到的地方 |

> **權衡**：無人管的迴圈同時放大產出與放大錯誤。**Verification 與 budget 才是讓 L3 敢放著跑的關鍵。**

## 來源
- [cobusgreyling/loop-engineering](https://github.com/cobusgreyling/loop-engineering)、[LangChain · art of loop engineering](https://www.langchain.com/blog/the-art-of-loop-engineering)、[Addy Osmani · Loop engineering](https://addyosmani.com/blog/loop-engineering/)、[Lilian Weng · Harness engineering](https://lilianweng.github.io/posts/2026-07-04-harness/)
- Claude Code `/loop`、`ScheduleWakeup`、`Workflow` schema
