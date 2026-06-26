# Riley 的 Claude Code Skills

我的 Claude Code 技能集合（放在 `~/.claude/skills/`）。每個資料夾是一個 skill，含 `SKILL.md`（帶 frontmatter，可被自動觸發）。

## 技能清單

### 🦖 danruwu — 吳淡如教學人設
用《人生實用商學院》主講人吳淡如的語氣、人設與教學哲學回答理財／人生／職涯議題，並引用 11 集節目蒸餾出的知識庫。
- `references/` — 語感、口頭禪、開場收尾、教學哲學與結構模板
- `knowledge/` — 11 集節目知識庫（ETF、高股息、定期定額、房地產、中年理財、致富習慣、創業、人際界限、股災心理…）
- 來源：[gamezpika/danruwu](https://github.com/gamezpika/danruwu)

### 🎬 short-video — 短影音自動化（一條龍）
把一段口播錄音/影片自動做成直式 9:16 短影音：轉逐字稿、上字幕、自動快剪去停頓、做標題字卡、燒字幕、接片頭尾、配背景音樂。
- `scripts/transcribe_srt.py` — faster-whisper 轉逐字稿 + SRT
- `scripts/make_titlecard.py` — Pillow 產標題字卡（取代 ImageMagick）
- 引擎：ffmpeg + faster-whisper + auto-editor + Pillow + yt-dlp

### 🎬 video-autopilot — 影片自動化方法論 + 工具庫
從「一句題目」到「完整 YouTube／短影音發佈套件」的端到端流程：腳本＋packaging（標題/縮圖/描述）＋發佈計畫＋raw 素材自動 audit＋CapCut/ffmpeg 剪輯路徑＋發佈後學 pattern 優化。上游策略層，跟 `short-video`（執行層）互補。
- `knowledge/` — M1-M102 避坑大全、YouTube 演算法、Shorts/Reels SOP、跨平台心法、CapCut SOP（21 篇）
- `src/` — `silent_vlog_maker`（純 ffmpeg pipeline、audit、場景分群、多平台 encode）＋ `capcut_helpers`（草稿 I/O、花字、交付 QA）
- `templates/` / `SETUP.md` — 填自己的 voice/品牌/演算法 profile（空白模板，資料留本地）
- 來源：[Hao0321/video-autopilot-kit](https://github.com/Hao0321/video-autopilot-kit)（MIT）

### 🟢 supabase — 用 Supabase 蓋 app 的實作指南
Postgres + Auth + Row Level Security + Storage + Edge Functions + Realtime + CLI 本地開發的可複製貼上參考；含 2026 新金鑰制、`@supabase/ssr`、Supavisor pooling 等近期變動與常見雷。
- `references/reference.md` — 9 大區完整程式碼（supabase-js v2 為主、supabase-py 為輔）
- 來源：[supabase/supabase](https://github.com/supabase/supabase) 官方文件萃取

### 🟣 comfyui — 節點式 AI 生成引擎實作指南
用 ComfyUI 跑 SD/SDXL/SD3/Flux 影像與 Wan/Hunyuan/LTX 影片：安裝啟動、節點圖原理、workflow JSON（UI vs API 格式）、HTTP/WebSocket API 程式化跑圖、自訂節點開發、Manager/comfy-cli 生態。對接數位人/對嘴影片技術棧（RunComfy）。
- `references/reference.md` — 7 大區完整程式碼與 API 端點
- `scripts/` — repo 官方 API 範例腳本（basic / websockets，可直接改 prompt+seed 套用）
- 來源：[comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)（Comfy-Org）

## 安裝（換新電腦時的地基）

short-video 需要這些工具。Ubuntu/Linux：
```bash
# 系統層（需 sudo）
sudo apt install ffmpeg imagemagick   # ffmpeg 必裝；imagemagick 選用
# Python venv（免 sudo）
python3 -m venv ~/kuba/video-venv && source ~/kuba/video-venv/bin/activate
pip install faster-whisper auto-editor Pillow requests yt-dlp
# 繁中字型（免 sudo）— 否則字幕字卡變亂碼
mkdir -p ~/.local/share/fonts
curl -fsSL "https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf" -o ~/.local/share/fonts/NotoSansTC.ttf
fc-cache -f
```
> 各 `SKILL.md` 內的絕對路徑（venv、字型）是以本機 `/home/riley` 為準，換機請對應調整。

## 使用
把整個資料夾放到 `~/.claude/skills/`，重開 Claude Code 即可用 `/danruwu`、`/short-video`、`/video-autopilot`、`/supabase`、`/comfyui`，或在對應情境自動觸發。
