import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "project-registry.json"
SVG = ROOT / "assets" / "realm.svg"
README = ROOT / "README.md"
COLORS = {
    "Security": "#55f2d0",
    "AI": "#b6a0ff",
    "Developer Tools": "#69c8ff",
    "Web": "#ffcb76",
    "Research": "#ff8fbd"
}

def load_registry():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(data.get("projects"), list):
        raise ValueError("'projects' must be a list")
    seen = set()
    for i, p in enumerate(data["projects"], 1):
        for key in ("name", "repository", "district", "level", "status", "description"):
            if not p.get(key):
                raise ValueError(f"Project {i} is missing {key}")
        if not isinstance(p["level"], int) or not 1 <= p["level"] <= 5:
            raise ValueError(f"Project {i}: level must be 1 to 5")
        if p["status"] not in {"planned", "in-progress", "completed"}:
            raise ValueError(f"Project {i}: invalid status")
        if p["repository"] in seen:
            raise ValueError(f"Duplicate repository: {p['repository']}")
        seen.add(p["repository"])
    return data

def upgrade_from_release(data):
    if os.environ.get("GITHUB_EVENT_NAME") != "repository_dispatch":
        return
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return
    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if event.get("action") != "project_released":
        return
    payload = event.get("client_payload") or {}
    repo_url = (payload.get("repository") or "").rstrip("/")
    for project in data["projects"]:
        if project["repository"].rstrip("/") == repo_url:
            project["level"] = min(5, project["level"] + 1)
            REGISTRY.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print("Building upgraded for release:", repo_url)
            return
    print("No registry entry matched release:", repo_url)

def render_svg(data):
    projects = data["projects"]
    ground = 300
    slot = 920 / max(1, len(projects))
    buildings = []
    for i, p in enumerate(projects):
        cx = 40 + slot * (i + 0.5)
        bw = min(54, slot * 0.48)
        height = 35 + p["level"] * 24
        x, y = cx - bw / 2, ground - height
        color = COLORS.get(p["district"], "#55f2d0")
        opacity = {"planned": 0.4, "in-progress": 0.76, "completed": 1}[p["status"]]
        roof = f"{cx},{y-10} {x+bw},{y} {cx},{y+10} {x},{y}"
        bits = [
            f'<polygon points="{roof}" fill="{color}" opacity="{opacity}"/>',
            f'<polygon points="{x},{y} {cx},{y+10} {cx},{ground} {x},{ground}" fill="#102b35" stroke="{color}"/>',
            f'<polygon points="{cx},{y+10} {x+bw},{y} {x+bw},{ground} {cx},{ground}" fill="#173d48" stroke="{color}"/>',
            f'<text x="{cx}" y="{ground+22}" text-anchor="middle" class="label">{html.escape(p["name"][:18])}</text>',
            f'<text x="{cx}" y="{ground+36}" text-anchor="middle" class="small">LVL {p["level"]} · {html.escape(p["district"].upper()[:12])}</text>'
        ]
        for row in range(min(5, p["level"] + 1)):
            wy = y + 17 + row * 13
            if wy < ground - 5:
                bits.append(f'<path d="M{x+8} {wy} l6 -2 M{cx+7} {wy-2} l6 -3" stroke="{color}" stroke-width="2"/>')
        buildings.extend(bits)
    completed = sum(p["status"] == "completed" for p in projects)
    levels = sum(p["level"] for p in projects)
    districts = len({p["district"] for p in projects})
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="450" viewBox="0 0 1000 450" role="img">
<title>RUDRA NOIR — The Living Realm</title>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#07151e"/><stop offset="1" stop-color="#102b35"/></linearGradient><pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#4adfc8" stroke-opacity=".08"/></pattern></defs>
<style>.title{{font:700 24px sans-serif;letter-spacing:3px;fill:#e4fff8}}.head{{font:12px sans-serif;letter-spacing:2px;fill:#8ebdbb}}.label{{font:600 10px sans-serif;fill:#e4fff8}}.small{{font:9px sans-serif;fill:#8ebdbb}}.stat{{font:700 22px sans-serif;fill:#55f2d0}}</style>
<rect width="1000" height="450" rx="18" fill="url(#bg)"/><rect width="1000" height="450" rx="18" fill="url(#grid)"/>
<circle cx="850" cy="82" r="36" fill="none" stroke="#b6a0ff" stroke-width="1.5"/><circle cx="850" cy="82" r="25" fill="none" stroke="#b6a0ff" opacity=".5"/>
<text x="40" y="45" class="title">THE LIVING REALM</text><text x="40" y="68" class="head">A KINGDOM BUILT ONE QUEST AT A TIME</text><path d="M40 92H960" stroke="#55f2d0" stroke-opacity=".4"/>
<path d="M0 190 Q250 145 500 190 T1000 175 V300 H0Z" fill="#55f2d0" fill-opacity=".06"/>
<path d="M25 320 L180 292 L330 320 L500 288 L670 320 L820 292 L975 320 L975 350 L820 322 L670 350 L500 318 L330 350 L180 322 L25 350Z" fill="#153b43" stroke="#55f2d0" stroke-opacity=".25"/>
{''.join(buildings)}
<path d="M30 380H970" stroke="#55f2d0" stroke-opacity=".25"/>
<text x="45" y="410" class="stat">{len(projects)}</text><text x="45" y="428" class="small">STRUCTURES</text>
<text x="270" y="410" class="stat">{completed}</text><text x="270" y="428" class="small">COMPLETED QUESTS</text>
<text x="520" y="410" class="stat">{levels}</text><text x="520" y="428" class="small">TOTAL LEVELS</text>
<text x="760" y="410" class="stat">{districts}</text><text x="760" y="428" class="small">DISTRICTS</text></svg>"""

def update_readme(projects):
    text = README.read_text(encoding="utf-8")
    start, end = "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"
    if start not in text or end not in text:
        return
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    rows = ["| Project | District | Level | Status |", "|---|---|---:|---|"]
    for p in projects:
        status = {"planned": "Planned", "in-progress": "In progress", "completed": "Completed"}[p["status"]]
        rows.append(f"| [{p['name']}]({p['repository']}) | {p['district']} | {p['level']} | {status} |")
    README.write_text(before + start + "\n" + "\n".join(rows) + "\n" + end + after, encoding="utf-8")

def main():
    data = load_registry()
    upgrade_from_release(data)
    data = load_registry()
    SVG.parent.mkdir(parents=True, exist_ok=True)
    SVG.write_text(render_svg(data), encoding="utf-8")
    update_readme(data["projects"])
    print(f"Generated realm for {len(data['projects'])} projects.")

if __name__ == "__main__":
    main()
