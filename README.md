# Riley 的技能庫

## 結構
真實檔案分兩層存放，**外層 symlink 讓 Claude Code 讀得到**
（官方文件：Claude Code 只掃 `~/.claude/skills/<name>/SKILL.md` 一層，但支援 symlink）。

```
~/.claude/skills/
├── official/          # Anthropic 官方 skill
│   ├── documents/     pdf xlsx docx pptx
│   ├── design/        canvas-design algorithmic-art theme-factory brand-guidelines frontend-design slack-gif-creator
│   ├── development/   mcp-builder web-artifacts-builder webapp-testing claude-api-ref
│   ├── writing/       doc-coauthoring internal-comms
│   └── meta/          skill-creator
├── custom/            # 自製 / 第三方
│   ├── presentation/  slidev pptx-generator academic-poster
│   ├── media/         comfyui short-video video-autopilot
│   ├── development/   supabase
│   ├── writing/       danruwu
│   └── meta/          skills-catalog loop-engineering
└── <技能名> -> official|custom/<用途>/<技能名>   ← symlink（27 個）
```

## 新增技能
```bash
./add-skill.sh <技能資料夾> <official|custom> <用途分類>
```
會自動放進正確位置並建好 symlink。**不要直接把資料夾丟在根目錄**，請照分類放。

## 驗證全部技能正常
```bash
for s in $(find . -maxdepth 1 -type l -printf "%f\n"); do
  [ -f "$s/SKILL.md" ] || echo "壞掉: $s"
done
```
