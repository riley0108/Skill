---
name: video-autopilot
description: 從「一句題目」到「完整 YouTube／短影音發佈套件」的端到端自動化方法論 + 工具庫。當使用者要「規劃下一支影片／全部你來／autopilot 一支X」「拍前 packaging（標題+封面+腳本+描述）」「raw 素材自動 audit 與場景分群」「CapCut 草稿自動化／JSON 直接改字幕」「純 ffmpeg 做無口播 vlog」「發佈後記錄數據、學 pattern 優化默認值」，或詢問 YouTube 演算法（CTR/AVP/留存/縮圖/標題）、Shorts/Reels SOP、影片製作避坑（M1-M102）時使用。萃取自 video-autopilot-kit（MIT）。
---

# 🎬 Video Autopilot — 影片自動化方法論 + 工具庫

一句題目 → 可直接執行的全套：腳本（可念）＋ packaging（標題/縮圖/描述）＋ 發佈計畫＋監控時程＋剪輯 pipeline。
本 skill 是「方法論 + Python helpers + 知識庫」，**AI（你）負責下指令與判讀，真正幹活的是 ffmpeg / CapCut / 知識庫裡的 SOP**。

> 萃取自開源 `video-autopilot-kit`（MIT，作者 Hao0321 Studio）。**不含任何人的私人數據** —— voice／策略／頻道數字全是空白模板，使用者填自己的。

## 🔌 跟其他工具的關係（Riley 的環境）
- **`short-video` skill**：負責「已有錄音/影片 → 上字幕、自動快剪去停頓、做字卡、配樂」的**執行層**（faster-whisper venv 在 `~/kuba/video-venv`、Pillow 字卡、auto-editor）。
- **本 skill `video-autopilot`**：負責**上游策略層 + raw 素材 audit + CapCut 路徑 + 發佈後學習迴圈**。
- 典型搭配：本 skill 出「題目→腳本→packaging→畫面規劃」→ 使用者錄製 → `short-video` 或本 skill 的 `silent_vlog_maker` 出片 → 本 skill Mode B 記錄數據 → Mode C 優化。
- Python helpers 跑前先 `source ~/kuba/video-venv/bin/activate`（ffmpeg/ffprobe 系統內建即可）。

## ⚡ 5 條核心鐵則（接到「剪一支影片」先想這 5 件）
1. ☠️ **不要編造數字** — 每個數字/事實必有 source（WebSearch／使用者／畫面）。沒 source → 寫 generic。**「不講話 > 編造」**
2. ⛔ **先看畫面再寫文案** — `ffmpeg` 抽 4 frames（start/early/mid/late）640×360 → grid → Read → 才寫對應 overlay
3. 📋 **介紹式不是記錄式** — 含定位/數字/賣點/CTA ≥3 項，不要「我們來到 X」廢話
4. 🎯 **字幕統一中央偏下** — y≈1280-1400（Shorts）/ y≈820-930（長片），不跳位
5. 🎓 **跑完先 self-critique 17 關** 才算「剪完」，任一未過 → 還沒完
→ 完整 **M1-M102 + 17 條 antipatterns + Self-critique checklist + SOP** 見 [knowledge/meta-lessons.md](knowledge/meta-lessons.md)（**動工前必讀**）。

## 🚦 3 個 Mode（autopilot 主流程）
詳細步驟與呼叫約定見 [knowledge/autopilot-workflow.md](knowledge/autopilot-workflow.md)。

- **Mode A — Plan**：「規劃我下一支X／全部你來／autopilot」→ 9 步：Pre-flight 評分(≤3⭐ 就 fail loud 建議改題)→ 跨平台規劃 → 生腳本 → 砍贅詞 → 留存預檢 → packaging（TOP1 標題+2 變體、TOP1 縮圖+2 變體）→ 描述/標籤/**畫面規劃(script-anchored)** → 寫 `video_log.md` → 排監控時程。**給一句題目立刻跑，不要先問 5 個問題**；資訊不足只反問 1-2 個最關鍵的。
- **Mode B — Log Outcome**：「我發了 #N，CTR X% / AVD X」→ 補 `video_log.md` outcome，tag ✅有效/❌無效，自動排 48-72h + 1 週的數據複盤。
- **Mode C — Optimize**：「review 我的表現／optimize 默認值」→ 讀 log 找 pattern（≥5 outcome 才有意義）→ 寫 `optimization_log.md` → 主動提議更新預設值。

> `video_log.md` / `optimization_log.md` 第一次用時在本 skill 目錄建立即可（accumulate 不覆蓋）。

## 🛠️ 剪輯 Pipeline（選路徑，別反射多模板 agent）
| Path | 用途 | ETA | Token |
|---|---|---|---|
| **A 純 Export** | JSON 已 patch，只匯出 | 5-8m | 低 |
| **B 單一模板+Export** | 整支同一花字 | 25-40m | 中 |
| **C 多模板+貼圖** | marker/main/sub 分配 ⚠ 易撞 daily limit | 60-90m | 高 |
| **D JSON 直接編輯** ⭐ | 改字幕文字/字型/大小/位置 | <1m | 極低 |
| **E 純 ffmpeg** | 無口播 silent vlog | ~90s | 極低 |

- **預設**：一般 vlog → **Path D + A**；silent vlog → **Path E**。不要反射 Path C。
- **Agent spawn 上限 = 2 / task**，連 2 個失敗就停手改 Path D 或人工。
- CapCut 沒有公開 API，自動化＝**AI 透過 Computer Use 操作 CapCut 視窗**；要走 CapCut 路徑得開 Computer Use。SOP 見 [knowledge/capcut-automation-sop.md](knowledge/capcut-automation-sop.md)、JSON 直改見 [knowledge/capcut-json-direct-edit.md](knowledge/capcut-json-direct-edit.md)、agent brief 模板見 [knowledge/capcut-agent-brief-template.md](knowledge/capcut-agent-brief-template.md)、token 效率見 [knowledge/agent-token-efficiency.md](knowledge/agent-token-efficiency.md)。

## 🐍 Python 工具（`src/`）
```bash
source ~/kuba/video-venv/bin/activate
# 接到 raw 第一件事：一鍵 audit（11 維度 + 場景分群 + hi-res frame grid）
python -c "
import sys; sys.path.insert(0,'$HOME/.claude/skills/video-autopilot/src')
from silent_vlog_maker import run_full_audit, route_content, print_routing_decision
from pathlib import Path
r = run_full_audit(raw_dir=Path('videos/raw/'), output_dir=Path('videos/audit/'), project_name='題目')
d = route_content(Path('videos/raw/')); print_routing_decision(d)  # 自動判 layout/type/path/BGM
"
```
- `src/silent_vlog_maker/` — 純 ffmpeg pipeline（audit/場景/字幕/Ken Burns/多平台 encode preset：yt_shorts / yt_longform / ig_reels / tiktok / threads）。
- `src/capcut_helpers/` — CapCut 草稿 I/O、4-level 靜音、花字、post-export ffmpeg、b-roll 占比 audit、交付前 QA（頻閃/死空檔/排版自檢）。
- 跑 demo（不用真素材/CapCut，60 秒看 pipeline 會動）：`python examples/01_vertical_short.py`、`python examples/02_caption_broll_match.py`。

## 📚 知識庫導覽（`knowledge/`，索引見 [knowledge/README.md](knowledge/README.md)）
- 避坑大全 ⭐ [meta-lessons.md](knowledge/meta-lessons.md) — M1-M102 + antipatterns + checklist + SOP
- 演算法 [youtube-algorithm-mastery.md](knowledge/youtube-algorithm-mastery.md) · [youtube-algorithm-2026.md](knowledge/youtube-algorithm-2026.md) · [youtube-algorithm-overview.md](knowledge/youtube-algorithm-overview.md)
- 跨平台心法 [video-craft-playbook.md](knowledge/video-craft-playbook.md) · [viral-short-playbook.md](knowledge/viral-short-playbook.md) · [ig-caption-patterns.md](knowledge/ig-caption-patterns.md) · [shorts-reels-best-practices.md](knowledge/shorts-reels-best-practices.md)
- 經營 [teaching-niche-playbook.md](knowledge/teaching-niche-playbook.md) · [launch-hype-sop.md](knowledge/launch-hype-sop.md)
- 腳本 [script-style-framework.md](knowledge/script-style-framework.md)（學**你自己**的風格，不套別人聲音）
- CapCut [capcut-text-templates.md](knowledge/capcut-text-templates.md) · [capcut-pro-paywall-map.md](knowledge/capcut-pro-paywall-map.md) · 純 ffmpeg [programmatic-video-build.md](knowledge/programmatic-video-build.md)

## 🎛️ 個人化（讓它變成「你的」系統）
照 [SETUP.md](SETUP.md) 的問卷把 `templates/*.template.md` 填成自己的 voice / 品牌 / 演算法 / 社群 profile（資料留本地，不上傳）。卡關時查 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)。
