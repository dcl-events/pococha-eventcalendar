#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""organizer-ope.pococha.com /festivals を全カテゴリ横断で取得しJSON化する。"""
import json, re, sys, time, html, urllib.request, os

BASE = "https://organizer-ope.pococha.com"
COOKIE = open(os.path.expanduser("~/Claude/pococha/.session")).read().strip()
HERE = os.path.dirname(os.path.abspath(__file__))

FILTERS = {1: "開催前", 2: "エントリー期間中", 3: "開催中", 4: "開催後"}
ROW_RE = re.compile(
    r'<td><a href="/festivals/(\d+)">(.*?)</a></td>\s*<td>(.*?)</td>', re.S)
DT_RE = re.compile(
    r'(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}).*?〜.*?(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})', re.S)
MAXPAGE_RE = re.compile(r'page=(\d+)')


def fetch(ft, page):
    url = f"{BASE}/festivals?filter_type={ft}&page={page}"
    req = urllib.request.Request(url, headers={"Cookie": COOKIE,
                                               "User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def parse(html_text):
    out = []
    for fid, name, dt in ROW_RE.findall(html_text):
        m = DT_RE.search(dt)
        if not m:
            continue
        sd, st, ed, et = m.groups()
        out.append({
            "id": fid,
            "name": html.unescape(re.sub(r"<[^>]+>", "", name)).strip(),
            "start": f"{sd}T{st}",
            "end": f"{ed}T{et}",
        })
    return out


def max_page(html_text):
    pages = [int(p) for p in MAXPAGE_RE.findall(html_text)]
    return max(pages) if pages else 1


def main():
    # 開催後は膨大なので直近だけ (引数で調整可, 既定2ページ)
    past_pages = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    events = {}
    for ft, label in FILTERS.items():
        first = fetch(ft, 1)
        mp = max_page(first)
        if ft == 4:
            mp = min(mp, past_pages)
        pages_html = [first] + [None] * (mp - 1)
        for p in range(2, mp + 1):
            time.sleep(0.4)
            pages_html[p - 1] = fetch(ft, p)
        cnt = 0
        for h in pages_html:
            for ev in parse(h):
                # 既に別カテゴリで入っていても category は上書きしない(開催前>エントリー>…優先で先勝ち)
                if ev["id"] not in events:
                    ev["category"] = label
                    events[ev["id"]] = ev
                    cnt += 1
        print(f"filter_type={ft} {label}: pages={mp} new={cnt}", file=sys.stderr)
    data = sorted(events.values(), key=lambda e: e["start"])
    json.dump(data, open(os.path.join(HERE, "festivals.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"total unique events: {len(data)}", file=sys.stderr)


if __name__ == "__main__":
    main()
