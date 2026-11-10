"""Calendar based contribution analytics shared by the SVG renderer and tests."""
from __future__ import annotations

import calendar
import json
from datetime import date, timedelta
from pathlib import Path


def month_starts(today: date, count: int = 12) -> list[date]:
    y, m = today.year, today.month
    result = []
    for _ in range(count):
        result.append(date(y, m, 1))
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return list(reversed(result))


def calculate(days: list[dict], today: date) -> dict:
    counts = {date.fromisoformat(d["date"]): int(d.get("contributionCount", d.get("count", 0))) for d in days}
    start = month_starts(today)[0]
    visible = {day: counts.get(day, 0) for day in (start + timedelta(i) for i in range((today-start).days+1))}
    active = sorted(day for day, count in counts.items() if count > 0)
    months = []
    for first in month_starts(today):
        last = min(date(first.year, first.month, calendar.monthrange(first.year, first.month)[1]), today)
        month_days = {d: visible.get(d, 0) for d in (first + timedelta(i) for i in range(max(0, (last-first).days+1)))}
        active_month = [(d, c) for d, c in month_days.items() if c > 0]
        max_day = max(month_days.items(), key=lambda item: (item[1], -item[0].toordinal()), default=(first, 0))
        months.append({
            "month": first.strftime("%b"), "year": first.year,
            "total": sum(month_days.values()), "active_days": len(active_month),
            "average": sum(c for _, c in active_month) / len(active_month) if active_month else 0,
            "highest_day": max_day[0].isoformat(), "highest_count": max_day[1],
            "incomplete": first.year == today.year and first.month == today.month,
        })
    period_active = sum(1 for value in visible.values() if value > 0)
    # Compute the current run using calendar dates; a zero today may still have a run through yesterday.
    cursor = today if counts.get(today, 0) else today - timedelta(days=1)
    current = 0
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    longest = best = run = 0
    previous = None
    for day in active:
        run = run + 1 if previous == day - timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    busiest_date, busiest_count = max(visible.items(), key=lambda item: (item[1], -item[0].toordinal()), default=(today, 0))
    heat_start = start - timedelta(days=(start.weekday() + 1) % 7)  # Sunday aligned
    heat_end = today + timedelta(days=(5-today.weekday()) % 7)
    heat_days = []
    day = heat_start
    while day <= heat_end:
        heat_days.append({"date": day.isoformat(), "count": counts.get(day, 0), "in_period": start <= day <= today})
        day += timedelta(days=1)
    return {
        "start": start.isoformat(), "today": today.isoformat(), "total": sum(visible.values()),
        "period_days": len(visible), "active_days": period_active, "current_streak": current,
        "longest_streak": longest, "busiest_date": busiest_date.isoformat(),
        "busiest_count": busiest_count, "months": months, "heatmap": heat_days,
    }


def load(path: Path, today: date) -> tuple[dict, dict]:
    source = json.loads(path.read_text(encoding="utf-8"))
    return source, calculate(source.get("days", []), today)
