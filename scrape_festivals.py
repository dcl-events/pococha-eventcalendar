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


def month_cutoff(past_months):
    """直近 past_months ヶ月（当月含む）の開始日をISO文字列で返す。
    past_months=2, 当月7月 → 前月6月の1日 '2026-06-01'。毎日ローリング。"""
    import datetime
    t = datetime.date.today()
    m = t.month - (past_months - 1)
    y = t.year
    while m < 1:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}-01"


def add_events(events, htmls, label, cutoff=None):
    cnt = 0
    for h in htmls:
        for ev in parse(h):
            if cutoff and ev["start"][:10] < cutoff:
                continue  # カットオフより前の開催後イベントは除外
            if ev["id"] not in events:
                ev["category"] = label
                events[ev["id"]] = ev
                cnt += 1
    return cnt


def main():
    # 開催後を何ヶ月分遡るか (当月含む・既定2ヶ月, ローリング)
    past_months = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    cutoff = month_cutoff(past_months)
    events = {}
    # 開催前/エントリー/開催中: 全ページ
    for ft in (1, 2, 3):
        label = FILTERS[ft]
        first = fetch(ft, 1)
        mp = max_page(first)
        htmls = [first]
        for p in range(2, mp + 1):
            time.sleep(0.4)
            htmls.append(fetch(ft, p))
        cnt = add_events(events, htmls, label)
        print(f"filter_type={ft} {label}: pages={mp} new={cnt}", file=sys.stderr)
    # 開催後: cutoff まで遡って取得 (2ページ連続で全て cutoff 前なら停止, 安全上限30p)
    label4 = FILTERS[4]
    p, old_streak, htmls4 = 1, 0, []
    while p <= 30:
        h = fetch(4, p)
        htmls4.append(h)
        starts = [m.group(1) for m in
                  (DT_RE.search(row) for row in re.findall(r'<td>.*?</td>', h, re.S))
                  if m]
        page_all_old = bool(starts) and all(s < cutoff for s in starts)
        old_streak = old_streak + 1 if page_all_old else 0
        if old_streak >= 2:
            break
        p += 1
        time.sleep(0.4)
    cnt4 = add_events(events, htmls4, label4, cutoff=cutoff)
    print(f"filter_type=4 {label4}: pages~{p} cutoff>={cutoff} new={cnt4}", file=sys.stderr)

    data = sorted(events.values(), key=lambda e: e["start"])
    json.dump(data, open(os.path.join(HERE, "festivals.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"total unique events: {len(data)} (past cutoff {cutoff})", file=sys.stderr)


if __name__ == "__main__":
    main()
