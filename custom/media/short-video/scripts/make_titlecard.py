#!/usr/bin/env python3
"""用 Pillow 產生整張標題字卡 PNG（取代 ImageMagick）。預設 9:16 直式 1080x1920。
用法: python make_titlecard.py "標題文字" out.png [--w 1080 --h 1920 --fs 90 --bg "#111418" --fg "#FFFFFF" --sub "副標"]
中文用 Noto Sans TC，不會變方框。
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

FONT = "/home/riley/.local/share/fonts/NotoSansTC.ttf"
FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

def load_font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except Exception:
        return ImageFont.truetype(FALLBACK, size)

def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if draw.textlength(cur + ch, font=font) <= max_w:
            cur += ch
        else:
            lines.append(cur); cur = ch
    if cur:
        lines.append(cur)
    return lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text"); ap.add_argument("out")
    ap.add_argument("--w", type=int, default=1080); ap.add_argument("--h", type=int, default=1920)
    ap.add_argument("--fs", type=int, default=90); ap.add_argument("--sub", default="")
    ap.add_argument("--bg", default="#111418"); ap.add_argument("--fg", default="#FFFFFF")
    ap.add_argument("--accent", default="#F5C518")
    a = ap.parse_args()

    img = Image.new("RGB", (a.w, a.h), a.bg)
    d = ImageDraw.Draw(img)
    font = load_font(a.fs)
    margin = int(a.w * 0.1); max_w = a.w - 2 * margin
    lines = wrap(d, a.text, font, max_w)
    lh = int(a.fs * 1.3); block_h = lh * len(lines)
    y = (a.h - block_h) // 2
    # 強調色橫條
    d.rectangle([margin, y - 40, margin + 120, y - 24], fill=a.accent)
    for ln in lines:
        w = d.textlength(ln, font=font)
        d.text(((a.w - w) // 2, y), ln, font=font, fill=a.fg)
        y += lh
    if a.sub:
        sf = load_font(int(a.fs * 0.45))
        sw = d.textlength(a.sub, font=sf)
        d.text(((a.w - sw) // 2, y + 20), a.sub, font=sf, fill=a.accent)
    img.save(a.out)
    print(f"✅ 字卡輸出: {a.out} ({a.w}x{a.h})")

if __name__ == "__main__":
    main()
