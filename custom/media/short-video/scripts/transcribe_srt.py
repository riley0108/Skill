#!/usr/bin/env python3
"""用 faster-whisper 把音/影片轉成逐字稿 + SRT 字幕。
用法: python transcribe_srt.py <音檔或影片> [--model small] [--lang zh]
輸出: 同檔名的 .srt 與 .txt(繁體中文）。第一次跑會自動下載模型。
"""
import sys, argparse, pathlib

def fmt_ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("--model", default="small", help="tiny/base/small/medium/large-v3")
    ap.add_argument("--lang", default="zh")
    args = ap.parse_args()

    from faster_whisper import WhisperModel
    try:
        import opencc  # 簡轉繁（若有裝）
        cc = opencc.OpenCC("s2twp")
        conv = lambda x: cc.convert(x)
    except Exception:
        conv = lambda x: x  # 沒裝 opencc 就原樣輸出

    src = pathlib.Path(args.media)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(src), language=args.lang, vad_filter=True)
    print(f"偵測語言: {info.language} (p={info.language_probability:.2f})", file=sys.stderr)

    srt_path = src.with_suffix(".srt"); txt_path = src.with_suffix(".txt")
    with open(srt_path, "w", encoding="utf-8") as srt, open(txt_path, "w", encoding="utf-8") as txt:
        for i, seg in enumerate(segments, 1):
            text = conv(seg.text.strip())
            srt.write(f"{i}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{text}\n\n")
            txt.write(text + "\n")
            print(f"[{fmt_ts(seg.start)}] {text}", file=sys.stderr)
    print(f"\n✅ SRT: {srt_path}\n✅ 逐字稿: {txt_path}")

if __name__ == "__main__":
    main()
