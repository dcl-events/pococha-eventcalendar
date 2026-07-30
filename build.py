#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""festivals.json から自己完結HTMLカレンダーを生成する。"""
import json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "festivals.json")))
today = datetime.date.today().isoformat()
generated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

html = """<meta charset="utf-8">
<title>Pococha イベントカレンダー</title>
<style>
:root{
  --bg:#f5f5f7; --surface:#ffffff; --ink:#1b1b20; --muted:#71717f;
  --line:#e7e7ec; --line2:#f0f0f4; --today:#ff5077;
  --up:#3b74d8; --up-bg:#e8f0fd; --entry:#c47800; --entry-bg:#fdf1dd;
  --live:#0f9d63; --live-bg:#e2f6ec; --done:#8b909c; --done-bg:#eef0f3;
  --shadow:0 1px 2px rgba(20,20,30,.06),0 4px 16px rgba(20,20,30,.05);
}
@media (prefers-color-scheme:dark){:root{
  --bg:#121216; --surface:#1c1c22; --ink:#ececf1; --muted:#9a9aa8;
  --line:#2c2c34; --line2:#242429; --today:#ff5077;
  --up:#6ea0f5; --up-bg:#1d2740; --entry:#e6a637; --entry-bg:#33280f;
  --live:#3ecb8b; --live-bg:#123024; --done:#8b909c; --done-bg:#26262c;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 4px 18px rgba(0,0,0,.35);
}}
:root[data-theme="light"]{
  --bg:#f5f5f7; --surface:#ffffff; --ink:#1b1b20; --muted:#71717f;
  --line:#e7e7ec; --line2:#f0f0f4; --up:#3b74d8; --up-bg:#e8f0fd;
  --entry:#c47800; --entry-bg:#fdf1dd; --live:#0f9d63; --live-bg:#e2f6ec;
  --done:#8b909c; --done-bg:#eef0f3; --shadow:0 1px 2px rgba(20,20,30,.06),0 4px 16px rgba(20,20,30,.05);
}
:root[data-theme="dark"]{
  --bg:#121216; --surface:#1c1c22; --ink:#ececf1; --muted:#9a9aa8;
  --line:#2c2c34; --line2:#242429; --up:#6ea0f5; --up-bg:#1d2740;
  --entry:#e6a637; --entry-bg:#33280f; --live:#3ecb8b; --live-bg:#123024;
  --done:#8b909c; --done-bg:#26262c; --shadow:0 1px 2px rgba(0,0,0,.3),0 4px 18px rgba(0,0,0,.35);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;font-feature-settings:"palt";}
.wrap{max-width:1120px;margin:0 auto;padding:28px 20px 80px}
header.top{display:flex;flex-wrap:wrap;align-items:baseline;gap:12px 16px;margin-bottom:6px}
h1{font-size:22px;font-weight:800;letter-spacing:.01em;margin:0}
.sub{color:var(--muted);font-size:12.5px}
.sub b{color:var(--ink);font-weight:700}
.toolbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:18px 0 22px}
.filters{display:flex;flex-wrap:wrap;gap:7px}
.chip{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);
  background:var(--surface);color:var(--ink);border-radius:999px;padding:6px 13px 6px 11px;
  font-size:12.5px;font-weight:600;cursor:pointer;user-select:none;transition:.12s}
.chip .dot{width:10px;height:10px;border-radius:3px;flex:none}
.chip[aria-pressed="false"]{opacity:.4;filter:saturate(.4)}
.chip:hover{border-color:var(--muted)}
.chip .ct{color:var(--muted);font-weight:700;font-variant-numeric:tabular-nums}
.spacer{flex:1}
.search{border:1px solid var(--line);background:var(--surface);color:var(--ink);
  border-radius:9px;padding:7px 11px;font-size:13px;min-width:190px;outline:none}
.search:focus{border-color:var(--today)}
.month{background:var(--surface);border:1px solid var(--line);border-radius:16px;
  box-shadow:var(--shadow);overflow:hidden;margin-bottom:22px}
.mhead{display:flex;align-items:baseline;gap:10px;padding:15px 18px 12px}
.mhead h2{margin:0;font-size:16px;font-weight:800}
.mhead .yr{color:var(--muted);font-weight:600;font-size:12.5px}
.mhead .mct{margin-left:auto;color:var(--muted);font-size:12px}
.dow{display:grid;grid-template-columns:repeat(7,1fr);border-top:1px solid var(--line)}
.dow div{padding:6px 8px;font-size:11px;font-weight:700;color:var(--muted);text-align:left;border-right:1px solid var(--line2)}
.dow div:last-child{border-right:none}
.dow .sun{color:#e0556e}.dow .sat{color:#4b83e0}
.week{display:grid;grid-template-columns:repeat(7,1fr);position:relative;border-top:1px solid var(--line2)}
.cell{min-height:104px;border-right:1px solid var(--line2);padding:4px 5px}
.cell:last-child{border-right:none}
.cell.out{background:linear-gradient(var(--line2),var(--line2));opacity:.35}
.dnum{font-size:12px;font-weight:700;color:var(--ink);width:23px;height:23px;line-height:23px;text-align:center;border-radius:50%}
.cell.out .dnum{color:var(--muted);font-weight:500}
.cell.today .dnum{background:var(--today);color:#fff}
.lanes{position:absolute;left:0;right:0;pointer-events:none}
.bar{position:absolute;height:19px;border-radius:5px;font-size:11px;font-weight:600;
  line-height:19px;padding:0 7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  pointer-events:auto;cursor:pointer;border-left:3px solid}
.bar.up{background:var(--up-bg);color:var(--up);border-color:var(--up)}
.bar.entry{background:var(--entry-bg);color:var(--entry);border-color:var(--entry)}
.bar.live{background:var(--live-bg);color:var(--live);border-color:var(--live)}
.bar.done{background:var(--done-bg);color:var(--done);border-color:var(--done)}
.bar.cont-l{border-left:none;border-top-left-radius:0;border-bottom-left-radius:0}
.bar.cont-r{border-top-right-radius:0;border-bottom-right-radius:0}
.more{position:absolute;font-size:10.5px;font-weight:700;color:var(--muted);pointer-events:auto;cursor:pointer;padding:0 6px}
/* popover */
.pop{position:fixed;inset:0;background:rgba(10,10,15,.4);display:none;align-items:center;justify-content:center;z-index:50;padding:20px}
.pop.on{display:flex}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);
  max-width:420px;width:100%;padding:20px 20px 18px}
.card .tag{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;margin-bottom:10px}
.card h3{margin:0 0 12px;font-size:16px;font-weight:800;line-height:1.4}
.card .row{display:flex;gap:10px;font-size:13px;margin:5px 0;color:var(--ink)}
.card .row .k{color:var(--muted);width:60px;flex:none}
.card .close{margin-top:16px;width:100%;border:1px solid var(--line);background:transparent;color:var(--ink);
  border-radius:9px;padding:9px;font-size:13px;font-weight:600;cursor:pointer}
.card .close:hover{background:var(--line2)}
footer{color:var(--muted);font-size:11.5px;text-align:center;margin-top:26px;line-height:1.7}
</style>

<div class="wrap">
  <header class="top">
    <h1>Pococha イベントカレンダー</h1>
    <span class="sub">全 <b id="total">0</b> 件 ・ organizer-ope 事務所主催イベント</span>
  </header>
  <div class="toolbar">
    <div class="filters" id="filters"></div>
    <div class="spacer"></div>
    <input class="search" id="search" placeholder="イベント名で絞り込み…">
  </div>
  <div id="cal"></div>
  <footer>
    データ取得: <b id="gen"></b> ／ 出典: organizer-ope.pococha.com ・ 全時刻 JST<br>
    バーをクリックで詳細。カテゴリは色で区別（開催前＝青・エントリー中＝琥珀・開催中＝緑・開催後＝グレー）。
  </footer>
</div>

<div class="pop" id="pop"><div class="card">
  <span class="tag" id="p-tag"></span>
  <h3 id="p-name"></h3>
  <div class="row"><span class="k">開始</span><span id="p-start"></span></div>
  <div class="row"><span class="k">終了</span><span id="p-end"></span></div>
  <div class="row"><span class="k">期間</span><span id="p-dur"></span></div>
  <button class="close" id="p-close">閉じる</button>
</div></div>

<script>
const DATA = __DATA__;
const TODAY = "__TODAY__";
document.getElementById('gen').textContent = "__GEN__";
document.getElementById('total').textContent = DATA.length;

const CATS = {
  "開催前":{cls:"up",v:"--up"}, "エントリー期間中":{cls:"entry",v:"--entry"},
  "開催中":{cls:"live",v:"--live"}, "開催後":{cls:"done",v:"--done"}
};
const LABEL = {"開催前":"開催前","エントリー期間中":"エントリー中","開催中":"開催中","開催後":"開催後"};
const active = new Set(Object.keys(CATS));
let query = "";

function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v);}
const DAY = 86400000;
function d0(iso){const p=iso.slice(0,10).split('-');return new Date(+p[0],+p[1]-1,+p[2]);}
function key(dt){return dt.getFullYear()+'-'+String(dt.getMonth()+1).padStart(2,'0')+'-'+String(dt.getDate()).padStart(2,'0');}
function fmt(iso){const [d,t]=iso.split('T');const [y,m,dd]=d.split('-');
  const w=['日','月','火','水','木','金','土'][d0(iso).getDay()];
  return `${y}/${+m}/${+dd}(${w}) ${t.slice(0,5)}`;}

// build filter chips
const counts={};DATA.forEach(e=>counts[e.category]=(counts[e.category]||0)+1);
const fdiv=document.getElementById('filters');
Object.keys(CATS).forEach(cat=>{
  const c=document.createElement('button');c.className='chip';c.setAttribute('aria-pressed','true');
  c.innerHTML=`<span class="dot" style="background:var(${CATS[cat].v})"></span>${LABEL[cat]}<span class="ct">${counts[cat]||0}</span>`;
  c.onclick=()=>{active.has(cat)?active.delete(cat):active.add(cat);
    c.setAttribute('aria-pressed',active.has(cat));render();};
  fdiv.appendChild(c);
});
document.getElementById('search').oninput=e=>{query=e.target.value.trim().toLowerCase();render();};

// popover
const pop=document.getElementById('pop');
document.getElementById('p-close').onclick=()=>pop.classList.remove('on');
pop.onclick=e=>{if(e.target===pop)pop.classList.remove('on');};
function openPop(ev){
  const c=CATS[ev.category];
  const tag=document.getElementById('p-tag');
  tag.textContent=LABEL[ev.category];
  tag.style.background=`var(${c.v}-bg)`;tag.style.color=`var(${c.v})`;
  document.getElementById('p-name').textContent=ev.name;
  document.getElementById('p-start').textContent=fmt(ev.start);
  document.getElementById('p-end').textContent=fmt(ev.end);
  const days=Math.round((d0(ev.end)-d0(ev.start))/DAY)+1;
  document.getElementById('p-dur').textContent=days+'日間';
  pop.classList.add('on');
}

function render(){
  const cal=document.getElementById('cal');cal.innerHTML='';
  const evs=DATA.filter(e=>active.has(e.category) && (!query||e.name.toLowerCase().includes(query)));
  if(!evs.length){cal.innerHTML='<p style="color:var(--muted);padding:30px;text-align:center">該当するイベントがありません</p>';return;}
  // month range
  let min=d0(evs[0].start),max=d0(evs[0].end);
  evs.forEach(e=>{const s=d0(e.start),en=d0(e.end);if(s<min)min=s;if(en>max)max=en;});
  const months=[];let cur=new Date(min.getFullYear(),min.getMonth(),1);
  const last=new Date(max.getFullYear(),max.getMonth(),1);
  while(cur<=last){months.push(new Date(cur));cur.setMonth(cur.getMonth()+1);}

  months.forEach(m=>{
    const y=m.getFullYear(),mo=m.getMonth();
    const mDiv=document.createElement('div');mDiv.className='month';
    // count events touching this month
    const mStart=new Date(y,mo,1),mEnd=new Date(y,mo+1,0);
    const mc=evs.filter(e=>d0(e.start)<=mEnd&&d0(e.end)>=mStart).length;
    mDiv.innerHTML=`<div class="mhead"><h2>${mo+1}月</h2><span class="yr">${y}</span><span class="mct">${mc}件</span></div>`;
    const dow=document.createElement('div');dow.className='dow';
    ['日','月','火','水','木','金','土'].forEach((d,i)=>{
      const c=document.createElement('div');c.textContent=d;if(i===0)c.className='sun';if(i===6)c.className='sat';dow.appendChild(c);});
    mDiv.appendChild(dow);

    // weeks (Sun start)
    const first=new Date(y,mo,1);
    let ws=new Date(first);ws.setDate(1-first.getDay());
    const monthEnd=new Date(y,mo+1,0);
    while(ws<=monthEnd){
      const week=document.createElement('div');week.className='week';
      const days=[];
      for(let i=0;i<7;i++){const d=new Date(ws);d.setDate(ws.getDate()+i);days.push(d);
        const cell=document.createElement('div');cell.className='cell';
        if(d.getMonth()!==mo)cell.className+=' out';
        if(key(d)===TODAY)cell.className+=' today';
        cell.innerHTML=`<span class="dnum">${d.getDate()}</span>`;
        week.appendChild(cell);
      }
      // events overlapping this week
      const wStart=days[0],wEnd=days[6];
      const inWk=evs.filter(e=>d0(e.start)<=wEnd&&d0(e.end)>=wStart)
        .sort((a,b)=>d0(a.start)-d0(b.start)||(d0(b.end)-d0(a.end)));
      // lane packing
      const lanes=[];const placed=[];
      inWk.forEach(e=>{
        let sCol=Math.max(0,Math.round((d0(e.start)-wStart)/DAY));
        let eCol=Math.min(6,Math.round((d0(e.end)-wStart)/DAY));
        let lane=0;while(lanes[lane]&&lanes[lane]>sCol)lane++;
        lanes[lane]=eCol+1;
        placed.push({e,sCol,eCol,lane,
          contL:d0(e.start)<wStart,contR:d0(e.end)>wEnd});
      });
      const MAXLANE=3;
      const lanesBox=document.createElement('div');lanesBox.className='lanes';
      lanesBox.style.top='26px';
      const overflow={};
      placed.forEach(p=>{
        if(p.lane>=MAXLANE){for(let c=p.sCol;c<=p.eCol;c++)overflow[c]=(overflow[c]||0)+1;return;}
        const bar=document.createElement('div');
        bar.className='bar '+CATS[p.e.category].cls+(p.contL?' cont-l':'')+(p.contR?' cont-r':'');
        bar.style.left=`calc(${p.sCol}/7*100% + 3px)`;
        bar.style.width=`calc(${(p.eCol-p.sCol+1)}/7*100% - 6px)`;
        bar.style.top=(p.lane*22)+'px';
        bar.textContent=(p.contL?'◀ ':'')+p.e.name;
        bar.title=p.e.name;
        bar.onclick=()=>openPop(p.e);
        lanesBox.appendChild(bar);
      });
      Object.keys(overflow).forEach(c=>{
        const m=document.createElement('div');m.className='more';
        m.style.left=`calc(${c}/7*100% + 5px)`;m.style.top=(MAXLANE*22)+'px';
        m.textContent='+'+overflow[c];
        lanesBox.appendChild(m);
      });
      // set week min-height based on lanes
      const need=Math.min(lanes.length,MAXLANE)*22 + (Object.keys(overflow).length?16:0) + 30;
      week.querySelectorAll('.cell').forEach(c=>c.style.minHeight=Math.max(104,need)+'px');
      week.appendChild(lanesBox);
      mDiv.appendChild(week);
      ws.setDate(ws.getDate()+7);
    }
    cal.appendChild(mDiv);
  });
}
render();
</script>
"""

html = (html.replace("__DATA__", json.dumps(data, ensure_ascii=False))
            .replace("__TODAY__", today)
            .replace("__GEN__", generated))
out = os.path.join(HERE, "docs", "index.html")
open(out, "w").write(html)
print("wrote", out, len(html), "bytes")
