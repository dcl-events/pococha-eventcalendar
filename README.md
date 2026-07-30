# pococha-events

Pococha 事務所主催イベントカレンダー。organizer-ope.pococha.com の `/festivals`
（開催前 / エントリー期間中 / 開催中 / 開催後）を取得し、月グリッド形式で公開する。

- 公開URL: https://dcl-events.github.io/pococha-events/
- カテゴリ色分け（開催前=青 / エントリー中=琥珀 / 開催中=緑 / 開催後=グレー）
- 複数日イベントはバーで横断表示、密集日は「+N」で集約、当日を強調
- カテゴリフィルタ・イベント名検索・詳細ポップオーバー・ライト/ダーク対応

## 構成

| ファイル | 役割 |
|---|---|
| `scrape_festivals.py` | `/festivals` を全カテゴリ横断取得 → `festivals.json`（引数=開催後の取得ページ数, 既定2） |
| `build.py` | `festivals.json` → `docs/index.html`（自己完結HTML） |
| `run.sh` | 取得→生成→commit&push（Pages自動デプロイ）。launchd 日次実行想定 |
| `.github/workflows/deploy.yml` | `docs/` を GitHub Pages(Actions)へデプロイ |

## 更新

```bash
./run.sh        # 開催後2ページ
./run.sh 10     # 開催後を10ページ遡る
```

## 認証

取得には organizer-ope のログインCookieが必要。`~/Claude/pococha/.session`
（1行のCookie文字列）を参照する。**このリポジトリには秘密情報を含めない。**
Cookie失効時（HTTP 401/403）は貼り直しが必要。
