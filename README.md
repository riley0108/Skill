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
把整個資料夾放到 `~/.claude/skills/`，重開 Claude Code 即可用 `/danruwu`、`/short-video`，或在對應情境自動觸發。
