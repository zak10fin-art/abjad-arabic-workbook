import json
from pathlib import Path

with open("data/alphabet.json", "r", encoding="utf-8") as f:
    data = json.load(f)

letter = data["letter"]

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="1000">
  <rect width="100%" height="100%" fill="white"/>
  <text x="400" y="250" font-size="180" text-anchor="middle">{letter}</text>
</svg>
"""

Path("output").mkdir(exist_ok=True)
Path("output/alif.svg").write_text(svg, encoding="utf-8")

print("Generated page:", letter)
