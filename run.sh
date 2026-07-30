#!/bin/bash
# 取得 → 生成 → GitHub へ push（Pages自動デプロイ）。launchd から日次実行想定。
# 認証Cookieは ~/Claude/pococha/.session を参照（このリポには秘密情報を置かない）。
set -euo pipefail
cd "$(dirname "$0")"

export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 取得開始 ====="
python3 scrape_festivals.py "${1:-2}"   # 引数=開催後を遡る月数(当月含む・既定2ヶ月・ローリング)
python3 build.py

if [[ -n "$(git status --porcelain)" ]]; then
  git add -A
  git commit -m "chore: update events $(date '+%Y-%m-%d')"
  git push origin main
  echo "push 完了"
else
  echo "変更なし（push スキップ）"
fi
echo "===== 完了 ====="
