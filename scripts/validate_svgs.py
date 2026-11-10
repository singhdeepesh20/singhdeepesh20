"""Validate card SVG structure and, when Playwright is installed, capture browser QA."""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "assets" / "github"
EXPECTED = {"contribution-overview.svg": (1460, 550), "contribution-heatmap.svg": (1460, 270),
            "monthly-activity.svg": (1460, 360), "streak-stats.svg": (720, 230)}


def validate() -> list[str]:
    errors=[]
    for filename, (width, height) in EXPECTED.items():
        path=CARDS/filename
        if not path.exists():
            errors.append(f"Missing {path.relative_to(ROOT)}")
            continue
        try: root=ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"Invalid XML in {filename}: {exc}"); continue
        if root.attrib.get("viewBox") != f"0 0 {width} {height}": errors.append(f"Unexpected viewBox in {filename}")
        if root.attrib.get("width") != str(width) or root.attrib.get("height") != str(height): errors.append(f"Unexpected dimensions in {filename}")
        if root.findall(".//{http://www.w3.org/2000/svg}text") == []: errors.append(f"No text in {filename}")
        if root.findall(".//{http://www.w3.org/2000/svg}animate") or root.findall(".//{http://www.w3.org/2000/svg}animateTransform"):
            errors.append(f"Unexpected animation in deterministic card {filename}")
    repo=CARDS/"repositories.svg"
    if repo.exists():
        try: ET.parse(repo)
        except ET.ParseError as exc: errors.append(f"Invalid XML in repositories.svg: {exc}")
    return errors


def browser_qa() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install requirements-dev.txt and run `python -m playwright install chromium` for browser screenshots.", file=sys.stderr)
        return 2
    preview=ROOT/"preview"/"index.html"
    out=ROOT/"preview"/"screenshots"; out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":1500,"height":1000}, device_scale_factor=1)
        page.goto(preview.as_uri(), wait_until="load")
        page.screenshot(path=str(out/"profile-cards.png"), full_page=True)
        issues=page.evaluate("""() => ({broken:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src), overflow:[...document.querySelectorAll('img')].filter(i=>i.getBoundingClientRect().width>document.documentElement.clientWidth+1).map(i=>i.src), dimensions:[...document.querySelectorAll('img')].map(i=>({src:i.src,width:i.naturalWidth,height:i.naturalHeight}))})""")
        clipping=[]
        for filename in [*EXPECTED, "repositories.svg"]:
            asset=CARDS/filename
            if not asset.exists(): continue
            page.goto(asset.as_uri(), wait_until="load")
            bad=page.evaluate("""() => { const svg=document.documentElement, vb=svg.viewBox.baseVal; return [...svg.querySelectorAll('text')].flatMap(el=>{const b=el.getBBox(); return b.x < -1 || b.y < -1 || b.x+b.width > vb.width+1 || b.y+b.height > vb.height+1 ? [el.textContent] : []}) }""")
            clipping.extend(f"{filename}: {text}" for text in bad)
        browser.close()
    if issues["broken"] or issues["overflow"] or clipping:
        print({**issues,"clipped_text":clipping}, file=sys.stderr); return 1
    print(f"Chromium screenshot saved; loaded {len(issues['dimensions'])} cards and checked SVG text bounds.")
    return 0


if __name__ == "__main__":
    problems=validate()
    if problems:
        print("\n".join(problems), file=sys.stderr); raise SystemExit(1)
    print("SVG structure and dimensions validated.")
    if "--browser" in sys.argv: raise SystemExit(browser_qa())
