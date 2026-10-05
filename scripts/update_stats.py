"""Generate profile cards from public GitHub data using the authenticated gh CLI."""

import json
import subprocess
from collections import Counter
from html import escape
from pathlib import Path


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True, encoding="utf-8"))


def card(title, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="240" viewBox="0 0 480 240" role="img" aria-label="{escape(title)}">
    <defs><linearGradient id="border"><stop stop-color="#8b5cf6"/><stop offset="1" stop-color="#22d3ee"/></linearGradient></defs>
    <rect x="1" y="1" width="478" height="238" rx="18" fill="#161b2e" stroke="url(#border)" stroke-width="2"/>
    <g font-family="Segoe UI,Arial,sans-serif"><text x="28" y="40" fill="#c4b5fd" font-size="19" font-weight="700">{escape(title)}</text>{body}</g></svg>'''


user = api("users/MattiaValerio")
repos = api("users/MattiaValerio/repos?per_page=100")
owned = [repo for repo in repos if not repo["fork"]]
metrics = [
    ("Public repositories", user["public_repos"], "#a78bfa"),
    ("Stars earned", sum(repo["stargazers_count"] for repo in owned), "#fbbf24"),
    ("Followers", user["followers"], "#22d3ee"),
    ("Repository forks", sum(repo["forks_count"] for repo in owned), "#34d399"),
]
body = ""
for index, (label, value, color) in enumerate(metrics):
    x, y = 28 + (index % 2) * 232, 91 + (index // 2) * 82
    body += f'<text x="{x}" y="{y}" fill="{color}" font-size="30" font-weight="700">{value}</text><text x="{x}" y="{y + 24}" fill="#a9b1d6" font-size="13">{label}</text>'

output = Path(__file__).resolve().parents[1] / "assets"
output.mkdir(exist_ok=True)
(output / "github-stats.svg").write_text(card("GitHub / Public stats", body), encoding="utf-8")

languages = Counter()
for repo in owned:
    languages.update(api(f'repos/MattiaValerio/{repo["name"]}/languages'))
total = sum(languages.values())
colors = ["#3178c6", "#a78bfa", "#fbbf24", "#34d399", "#fb7185"]
body = '<text x="28" y="66" fill="#a9b1d6" font-size="12">Share of code bytes across public, non-fork repositories</text>'
for index, (language, count) in enumerate(languages.most_common(5)):
    y, percent = 92 + index * 29, count / total * 100
    body += f'<text x="28" y="{y}" fill="#e2e8f0" font-size="13">{escape(language)}</text><rect x="145" y="{y - 10}" width="230" height="9" rx="4" fill="#252b43"/><rect x="145" y="{y - 10}" width="{230 * percent / 100:.1f}" height="9" rx="4" fill="{colors[index]}"/><text x="395" y="{y}" fill="#a9b1d6" font-size="12">{percent:.1f}%</text>'
(output / "github-languages.svg").write_text(card("GitHub / Languages", body), encoding="utf-8")
