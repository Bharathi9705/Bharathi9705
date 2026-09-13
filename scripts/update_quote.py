import re
import sys
import requests

README_PATH = "README.md"
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


def update_readme(quote, author):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    block = f'{START_MARKER}\n> 💬 *"{quote}"*\n> — **{author}**\n{END_MARKER}'

    pattern = re.compile(f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL)
    if pattern.search(content):
        content = pattern.sub(block, content)
    else:
        content += f"\n\n### 💬 Quote of the Day\n{block}\n"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    q, a = get_quote()
    update_readme(q, a)
    print(f"Updated quote: {q} — {a}")
