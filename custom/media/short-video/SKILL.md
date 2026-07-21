---
name: short-video
description: 把一段口播錄音/影片自動做成直式 9:16 短影音——轉逐字稿、上字幕、自動快剪去停頓、做標題字卡、燒字幕疊字卡、接片頭尾、配背景音樂。當使用者丟來音檔或影片並說「做成短影音 / 上字幕 / 自動剪掉停頓 / 做字卡 / 配樂 / 轉逐字稿 / 抓 B-roll」時使用。基於 ffmpeg + faster-whisper + auto-editor + Pillow + yt-dlp。
---

# 短影音自動化 Skill（一條龍）

把錄音 → 可發的 9:16 直式短影音。AI（你）負責下指令，真正幹活的是這些已裝好的免費工具。

## 環境（已就緒）
- **venv**：`/home/riley/kuba/video-venv`。跑 Python 工具前先 `source /home/riley/kuba/video-venv/bin/activate`
- **ffmpeg / ffprobe**：系統內建,含 subtitles(libass)/drawtext/amix/overlay/scale/crop
- **faster-whisper**：轉逐字稿+SRT(`scripts/transcribe_srt.py`)
- **auto-editor**：自動偵測停頓快剪
- **Pillow**：做字卡(`scripts/make_titlecard.py`,取代 ImageMagick)
- **yt-dlp**：抓素材(系統內建,僅限合法授權/自有素材)
- **中文字型**：Noto Sans TC `/home/riley/.local/share/fonts/NotoSansTC.ttf`(備援 WenQuanYi)
- ⏭️ **配音**：使用者習慣自己錄,不用 ElevenLabs
- ⚠️ **Pexels B-roll**：需使用者提供 API key(requests 已裝)

## 一條龍流程（使用者說「照流程做成短影音」時）

> 工作目錄建議用使用者給的檔案所在資料夾。每一步做完先讓使用者看,**自動剪輯只是輔助,最後人眼看一遍再發**。

### 1. 轉逐字稿 + 字幕
```bash
source /home/riley/kuba/video-venv/bin/activate
python ~/.claude/skills/short-video/scripts/transcribe_srt.py 輸入.mp4 --model small --lang zh
# 產出 輸入.srt + 輸入.txt（繁中）
```

### 2. 自動快剪去停頓
```bash
auto-editor 輸入.mp4 --margin 0.2sec -o 剪好.mp4
# 偵測空白/停頓自動剪掉；--silent-threshold 可調靈敏度
```

### 3. 裁成 9:16 直式（1080x1920）
```bash
# 置中裁切 + 縮放；橫式來源用 crop 取中間直幅
ffmpeg -i 剪好.mp4 -vf "crop='min(iw,ih*9/16)':ih,scale=1080:1920" -c:a copy 直式.mp4
```

### 4. 燒字幕（中文不變方框,指定 Noto Sans TC）
```bash
ffmpeg -i 直式.mp4 -vf "subtitles=輸入.srt:fontsdir=/home/riley/.local/share/fonts:force_style='FontName=Noto Sans TC,FontSize=18,OutlineColour=&H80000000,BorderStyle=3'" -c:a copy 含字幕.mp4
```

### 5. 做標題字卡並接到片頭
```bash
python ~/.claude/skills/short-video/scripts/make_titlecard.py "影片標題" 字卡.png --sub "副標題"
# 字卡圖轉 3 秒影片片段
ffmpeg -loop 1 -t 3 -i 字卡.png -f lavfi -t 3 -i anullsrc=r=44100:cl=stereo -vf scale=1080:1920 -c:v libx264 -pix_fmt yuv420p -c:a aac 片頭.mp4
# 接到主片前面（先統一參數再 concat）
printf "file '片頭.mp4'\nfile '含字幕.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy 接好.mp4   # 失敗就改用 filter_complex concat 重編碼
```

### 6. 配背景音樂、混音
```bash
ffmpeg -i 接好.mp4 -i bgm.mp3 -filter_complex "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" -c:v copy 成品.mp4
```

### 7.（選用）抓 B-roll
yt-dlp 抓自有/授權影片;或用 Pexels API(需使用者的 key)。**下載素材務必注意授權,自己拍或有授權的才用。**

## 踩雷提醒
- 中文字型一定要指定(上面已帶 Noto Sans TC),否則字幕/字卡變亂碼——最常見的雷
- concat 兩段參數(解析度/fps/編碼)不一致時 `-c copy` 會壞,改重新編碼
- 先別追求全自動;最常用的是「轉文字 + 燒字幕」,先把這兩步顧好
