"""Render deterministic editorial SVG cards from the latest real GitHub snapshot."""
from __future__ import annotations

import html
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from calculate_analytics import calculate

OUT = ROOT / "assets" / "github"
P = {"bg":"#F4F4F1", "card":"#FFFFFF", "ink":"#111111", "sub":"#737373", "muted":"#A0A0A0", "blue":"#3155FF", "l1":"#DCE5FF", "l2":"#AFC1FF", "l3":"#6E8CFF", "dark":"#1938D4", "border":"#E5E5E2", "zero":"#E6E6E2"}
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_start(w: int, h: int, title: str) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(title)}">',
            '<style>text{font-synthesis:none} .mono{font-family:'+MONO+'} .serif{font-family:'+SERIF+'}</style>',
            f'<rect width="{w}" height="{h}" rx="18" fill="{P["bg"]}"/>']


def text(x, y, value, size=14, color=None, family="mono", weight=400, anchor="start", extra=""):
    cls = "serif" if family == "serif" else "mono"
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{color or P["ink"]}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{esc(value)}</text>'


def render_overview(a: dict) -> str:
    s = svg_start(1460, 550, "GitHub contribution overview and activity statistics")
    s += [f'<rect x="1" y="1" width="1458" height="548" rx="18" fill="{P["card"]}" stroke="{P["border"]}"/>',
          text(54, 61, "THE LAST 12 MONTHS ON GITHUB", 13, P["sub"], weight=600, extra='letter-spacing="1.8"'),
          text(54, 174, f'{a["total"]:,}', 90, P["ink"], family="serif"),
          text(56, 211, "CONTRIBUTIONS", 12, P["sub"], weight=600, extra='letter-spacing="1.7"'),
          f'<line x1="1055" y1="50" x2="1055" y2="500" stroke="{P["border"]}"/>']
    vals = a["months"]
    chart_x, chart_y, chart_w, chart_h = 58, 265, 930, 190
    maxval = max((m["total"] for m in vals), default=0) or 1
    gap = 18; bw = (chart_w - gap * 11) / 12
    peak = max(range(len(vals)), key=lambda i: vals[i]["total"])
    for i, m in enumerate(vals):
        x = chart_x + i * (bw + gap)
        height = max(3, m["total"] / maxval * chart_h) if m["total"] else 3
        color = P["muted"] if m["incomplete"] else P["blue"] if i == peak else P["ink"]
        s.append(f'<rect x="{x:.1f}" y="{chart_y+chart_h-height:.1f}" width="{bw:.1f}" height="{height:.1f}" rx="3" fill="{color}"/>')
        s.append(text(x+bw/2, 482, m["month"].upper(), 10, P["muted"] if m["incomplete"] else P["sub"], anchor="middle"))
        s.append(text(x+bw/2, chart_y+chart_h-height-10, str(m["total"]), 10, P["sub"], anchor="middle"))
    stats = [("CURRENT STREAK", f'{a["current_streak"]} days', "LONGEST · {0} days".format(a["longest_streak"])),
             ("ACTIVE DAYS", f'{a["active_days"]} / {a["period_days"]}', "days with a contribution"),
             ("BUSIEST DAY", f'{a["busiest_count"]} contributions', a["busiest_date"])]
    for i, (label, value, note) in enumerate(stats):
        y = 98 + i * 142
        if i: s.append(f'<line x1="1090" y1="{y-33}" x2="1405" y2="{y-33}" stroke="{P["border"]}"/>')
        s += [text(1092, y, label, 11, P["sub"], weight=600, extra='letter-spacing="1.5"'),
              text(1092, y+48, value, 32, P["ink"], family="serif"),
              text(1092, y+75, note, 11, P["muted"])]
    s += [text(55, 523, f'PERIOD · {a["start"]} — {a["today"]}', 10, P["muted"]), '</svg>']
    return "\n".join(s)


def level(count: int) -> int:
    return 0 if count == 0 else 1 if count <= 2 else 2 if count <= 5 else 3 if count <= 9 else 4 if count <= 19 else 5


def render_heatmap(a: dict) -> str:
    days = a["heatmap"]
    weeks = len(days) // 7
    s = svg_start(1460, 270, "Daily GitHub contributions heatmap")
    s += [f'<rect x="1" y="1" width="1458" height="268" rx="18" fill="{P["card"]}" stroke="{P["border"]}"/>',
          text(40, 45, "Every day, in blue.", 24, P["blue"], family="serif"),
          text(1418, 44, "REFRESHED DAILY", 10, P["muted"], anchor="end", extra='letter-spacing="1.4"')]
    # A week column is Sunday through Saturday; dates are chronological.
    x0, y0, cell, gap = 72, 78, 17, 6
    colors = [P["zero"], P["l1"], P["l2"], P["l3"], P["blue"], P["dark"]]
    month_markers = []
    for wi in range(weeks):
        col = days[wi*7:(wi+1)*7]
        for ri, day in enumerate(col):
            x, y = x0 + wi*(cell+gap), y0 + ri*(cell+gap)
            dt = date.fromisoformat(day["date"])
            title = f'{day["date"]}: {day["count"]} contributions · level {level(day["count"])}'
            opacity = 1 if day["in_period"] else .25
            s.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{colors[level(day["count"])]}" opacity="{opacity}"><title>{esc(title)}</title></rect>')
            if ri == 0 and dt.day <= 7:
                month_markers.append((x, dt.strftime("%b").upper()))
    for x, label in month_markers:
        s.append(text(x, 246, label, 9, P["sub"]))
    s += [text(72, 265, "LESS", 9, P["muted"])]
    for i, color in enumerate(colors): s.append(f'<rect x="{111+i*20}" y="252" width="13" height="13" rx="3" fill="{color}"/>')
    s += [text(246, 265, "MORE", 9, P["muted"]), text(1418, 265, "CONTRIBUTIONS · LAST 12 MONTHS", 9, P["muted"], anchor="end"), '</svg>']
    return "\n".join(s)


def render_monthly(a: dict) -> str:
    s = svg_start(1460, 360, "Monthly contribution analytics")
    s += [f'<rect x="1" y="1" width="1458" height="358" rx="18" fill="{P["card"]}" stroke="{P["border"]}"/>',
          text(48, 52, "MONTHLY ACTIVITY", 12, P["sub"], weight=600, extra='letter-spacing="1.7"')]
    cols = a["months"]; maxv = max((x["total"] for x in cols), default=0) or 1
    x0, gap, bw, top, bh = 50, 20, 98, 102, 146
    peak = max(range(len(cols)), key=lambda i: cols[i]["total"])
    for i, m in enumerate(cols):
        x = x0+i*(bw+gap); barh = max(3, m["total"]/maxv*bh)
        fill = P["muted"] if m["incomplete"] else P["blue"] if i == peak else P["ink"]
        s.append(f'<rect x="{x}" y="{top+bh-barh:.1f}" width="{bw}" height="{barh:.1f}" rx="4" fill="{fill}"/>')
        s += [text(x+bw/2, top+bh-barh-9, f'{m["total"]}', 11, P["sub"], anchor="middle"),
              text(x+bw/2, 275, f'{m["month"]} {str(m["year"])[2:]}', 11, P["sub"], anchor="middle"),
              text(x+bw/2, 307, f'{m["active_days"]} active days', 9, P["muted"], anchor="middle"),
              text(x+bw/2, 325, f'avg {m["average"]:.1f} · max {m["highest_count"]}', 9, P["muted"], anchor="middle")]
    s.append(text(1410, 52, "TOTAL · ACTIVE DAYS · AVG/DAY · PEAK", 9, P["muted"], anchor="end"))
    s.append('</svg>')
    return "\n".join(s)


def render_streak(a: dict) -> str:
    s = svg_start(720, 230, "Contribution streak statistics")
    s += [f'<rect x="1" y="1" width="718" height="228" rx="18" fill="{P["card"]}" stroke="{P["border"]}"/>',
          text(38, 43, "CONSISTENCY, BY THE CALENDAR", 11, P["sub"], weight=600, extra='letter-spacing="1.4"')]
    for i, (label, value) in enumerate((("CURRENT STREAK", a["current_streak"]), ("LONGEST STREAK", a["longest_streak"]), ("ACTIVE DAYS", f'{a["active_days"]}/{a["period_days"]}'))):
        x = 40 + i*230
        if i: s.append(f'<line x1="{x-24}" y1="70" x2="{x-24}" y2="190" stroke="{P["border"]}"/>')
        s += [text(x, 104, value, 44, P["ink"], family="serif"), text(x, 133, "days" if i < 2 else "this period", 10, P["muted"]), text(x, 176, label, 10, P["sub"], weight=600)]
    return "\n".join(s+["</svg>"])


def render_repositories(repos: list[dict]) -> str:
    # Show true public repository metadata, prioritizing the named flagship if it exists.
    repos = sorted(repos, key=lambda r: ("niramaya" not in r.get("name", "").lower(), -int(r.get("stargazerCount", 0)), r.get("name", "").lower()))[:6]
    h = 142 + max(1, len(repos))*70
    s = svg_start(1000, h, "Featured public repositories")
    s += [f'<rect x="1" y="1" width="998" height="{h-2}" rx="18" fill="{P["card"]}" stroke="{P["border"]}"/>', text(38, 43, "SELECTED PUBLIC REPOSITORIES", 11, P["sub"], weight=600, extra='letter-spacing="1.5"')]
    if not repos:
        s.append(text(38, 100, "Repository data will appear after the first successful GitHub refresh.", 13, P["muted"]))
    for i, repo in enumerate(repos):
        y=91+i*70
        if i: s.append(f'<line x1="38" y1="{y-23}" x2="962" y2="{y-23}" stroke="{P["border"]}"/>')
        name=repo.get("name", "Repository"); desc=repo.get("description") or "Public project"
        lang=(repo.get("primaryLanguage") or {}).get("name") or "—"; stars=repo.get("stargazerCount", 0)
        s += [f'<a href="{esc(repo.get("url", "#"))}">', text(38, y, name, 18, P["ink"], family="serif", weight=600), '</a>',
              text(38, y+23, desc[:110], 11, P["sub"]),
              text(960, y+2, f'{lang}   ·   ★ {stars}', 10, P["sub"], anchor="end")]
    return "\n".join(s+["</svg>"])


def main() -> int:
    data_path=ROOT/"data"/"contributions.json"
    if not data_path.exists():
        print("Contribution snapshot missing. Run scripts/fetch_github_data.py first.", file=sys.stderr); return 1
    source=json.loads(data_path.read_text(encoding="utf-8"))
    today=date.fromisoformat(os.environ["PROFILE_TODAY"]) if os.getenv("PROFILE_TODAY") else datetime.now(timezone.utc).date()
    analytics=calculate(source.get("days", []), today)
    OUT.mkdir(parents=True, exist_ok=True)
    rendered={"contribution-overview.svg":render_overview(analytics), "contribution-heatmap.svg":render_heatmap(analytics),
              "monthly-activity.svg":render_monthly(analytics), "streak-stats.svg":render_streak(analytics),
              "repositories.svg":render_repositories(source.get("repositories", []))}
    static=os.getenv("STATIC") == "1"
    for name, content in rendered.items():
        # Renderer intentionally emits no animation; STATIC mode is byte-for-byte deterministic.
        (OUT/name).write_text(content+"\n", encoding="utf-8")
    print(f"Rendered {len(rendered)} cards{' in static mode' if static else ''} from {len(source.get('days', []))} real dates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
