#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""~/Claude/pococha/.session を GitHub Secret POCO_SESSION へ同期する。

launchd の WatchPaths（.session の変更検知）から呼ばれる想定。
- Cookieが有効(organizer-opeへ200)な時だけ同期する（壊れたCookieでSecretを上書きしない）
- 同期後に update.yml を workflow_dispatch でキック（サイトを即更新）
Cookie値はログに出さない。GitHubトークンはkeychain(git credential)から取得。
"""
import base64, json, os, subprocess, sys, urllib.request, datetime
from nacl import encoding, public

REPO = "dcl-events/pococha-eventcalendar"
API = "https://api.github.com"
SESSION = os.path.expanduser("~/Claude/pococha/.session")


def log(msg):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {msg}", flush=True)


def gh_token():
    p = subprocess.run(["git", "credential", "fill"],
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password="):]
    raise SystemExit("GitHubトークンをkeychainから取得できませんでした")


def gh(method, path, token, data=None):
    r = urllib.request.Request(f"{API}{path}", method=method,
        headers={"Authorization": f"token {token}",
                 "Accept": "application/vnd.github+json"},
        data=json.dumps(data).encode() if data is not None else None)
    return urllib.request.urlopen(r)


def cookie_valid(cookie):
    try:
        r = urllib.request.Request(
            "https://organizer-ope.pococha.com/festivals?filter_type=3",
            headers={"Cookie": cookie, "User-Agent": "Mozilla/5.0"})
        return urllib.request.urlopen(r, timeout=30).status == 200
    except Exception as e:
        log(f"cookie検証でエラー: {type(e).__name__}")
        return False


def main():
    if not os.path.exists(SESSION):
        raise SystemExit(".session が無い")
    cookie = open(SESSION).read().strip()
    if not cookie:
        raise SystemExit(".session が空")
    if not cookie_valid(cookie):
        log("⚠ Cookieが無効(200でない)。Secretは更新しません（既存を維持）")
        return
    token = gh_token()
    pk = json.load(gh("GET", f"/repos/{REPO}/actions/secrets/public-key", token))
    sealed = public.SealedBox(public.PublicKey(pk["key"].encode(),
                                               encoding.Base64Encoder()))
    enc = base64.b64encode(sealed.encrypt(cookie.encode())).decode()
    gh("PUT", f"/repos/{REPO}/actions/secrets/POCO_SESSION", token,
       {"encrypted_value": enc, "key_id": pk["key_id"]})
    log(f"✓ Secret POCO_SESSION を更新（cookie len={len(cookie)}）")
    # クラウドを即キックしてサイトを最新化
    try:
        gh("POST", f"/repos/{REPO}/actions/workflows/update.yml/dispatches",
           token, {"ref": "main"})
        log("✓ update.yml をキック（サイト即更新）")
    except Exception as e:
        log(f"⚠ workflowキックに失敗（Secretは更新済み）: {type(e).__name__}")


if __name__ == "__main__":
    main()
