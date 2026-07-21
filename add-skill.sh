#!/usr/bin/env bash
# 新增技能到技能庫（自動歸類 + 建 symlink）
# 用法：./add-skill.sh <技能資料夾路徑> <official|custom> <用途分類>
#   例：./add-skill.sh /tmp/my-skill custom media
set -euo pipefail
SK="$HOME/.claude/skills"
SRC="${1:?請給技能資料夾路徑}"; ROOT="${2:?official 或 custom}"; CAT="${3:?用途分類}"
NAME=$(basename "$SRC")
[ -f "$SRC/SKILL.md" ] || { echo "❌ $SRC 裡沒有 SKILL.md"; exit 1; }
case "$ROOT" in official|custom) ;; *) echo "❌ 第2個參數只能是 official 或 custom"; exit 1;; esac
mkdir -p "$SK/$ROOT/$CAT"
cp -r "$SRC" "$SK/$ROOT/$CAT/$NAME"
ln -sfn "$ROOT/$CAT/$NAME" "$SK/$NAME"
[ -f "$SK/$NAME/SKILL.md" ] && echo "✅ $NAME 已安裝到 $ROOT/$CAT/，symlink 正常" || { echo "❌ symlink 失敗"; exit 1; }
