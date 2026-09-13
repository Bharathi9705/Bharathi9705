import re
import sys
import textwrap
import requests

README_PATH = "README.md"
SVG_PATH = "assets/quote-card.svg"
START_MARKER = "<!-- QUOTE:START -->"
END_MARKER = "<!-- QUOTE:END -->"


def get_quote():
    """Fetch a random quote. Falls back to a static one if the API is down."""
    try:
        resp = requests.get("https://zenquotes.io/api/random", timeout=10)
        resp.raise_for_status()
        data = resp.json()[0]
        return data["q"], data["a"]
    except Exception as e:
        print(f"Quote API failed ({e}), using fallback quote.", file=sys.stderr)
        return "Stay hungry, stay foolish.", "Steve Jobs"


def build_glass_svg(quote, author):
    """Glass-panel SVG card in the cyan/violet command-center theme."""
    lines = textwrap.wrap(quote, width=46)[:4]
    line_height = 30
    total_text_h = len(lines) * line_height
    width, height = 700, 200

    tspans = "".join(
        f'<tspan x="{width/2}" dy="{0 if i == 0 else line_height}">{l}</tspan>'
        for i, l in enumerate(lines)
    )

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0A0E17"/>
      <stop offset="100%" stop-color="#1B0F3C"/>
    </linearGradient>
    <filter id="blur1"><feGaussianBlur stdDeviation="30"/></filter>
  </defs>

  <rect width="{width}" height="{height}" rx="24" fill="url(#bg)"/>

  <circle cx="120" cy="40" r="70" fill="#00E5FF" opacity="0.12" filter="url(#blur1)"/>
  <circle cx="600" cy="170" r="90" fill="#8B5CF6" opacity="0.14" filter="url(#blur1)"/>

  <rect x="18" y="18" width="{width-36}" height="{height-36}" rx="18"
        fill="#ffffff" fill-opacity="0.06" stroke="#00E5FF" stroke-opacity="0.35" stroke-width="1.5"/>

  <text x="{width/2}" y="{height/2 - total_text_h/2 + 26}" text-anchor="middle"
        font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" font-weight="600"
        fill="#E0F7FF">
    {tspans}
  </text>

  <text x="{width/2}" y="{height - 28}" text-anchor="middle"
        font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" font-weight="500"
        fill="#C4B5FD">
    — {author}
  </text>
</svg>'''


def update_svg(quote, author):
    import os
    os.makedirs("assets", exist_ok=True)
    svg = build_glass_svg(quote, author)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg)


def update_readme_marker():
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    block = (
        f'{START_MARKER}\n'
        f'<img src="{SVG_PATH}" alt="Quote of the Day" width="700" />\n'
        f'{END_MARKER}'
    )

    pattern = re.compile(f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL)
    if pattern.search(content):
        content = pattern.sub(block, content)
    else:
        content += f"\n\n### Quote of the Day\n{block}\n"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    q, a = get_quote()
    update_svg(q, a)
    update_readme_marker()
    print(f"Updated quote: {q} — {a}")
