#!/usr/bin/env python3
"""Print what a website shows about its brand as JSON. Standard library only.

Usage: python3 skills/keeper/extract-site.py https://example.com
Self-check: python3 skills/keeper/extract-site.py --check
"""
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen

MAX_BYTES = 2_000_000
MAX_STYLESHEETS = 8
MAX_TEXT = 6000
HEX = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})")
FONT = re.compile(r"(?:font-family|--font-(?:family|sans|serif|display|heading|body|regular)[\w-]*)\s*:\s*([^;}]+)", re.I)
GENERIC = {"inherit", "initial", "unset", "serif", "sans-serif", "monospace", "cursive", "system-ui",
           "-apple-system", "blinkmacsystemfont", "ui-sans-serif", "ui-serif", "ui-monospace"}
USEFUL_LINK = re.compile(r"about|pricing|plans|features|product|story|mission", re.I)
SKIP = {"script", "style", "noscript", "svg", "template"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.css, self.skip, self.heading = "", "", 0, 0
        self.in_title, self.in_style = False, False
        self.meta, self.sheets, self.icons, self.links = {}, [], [], []
        self.headings, self.text = [], []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): v or "" for k, v in attrs}
        self.css += " " + a.get("style", "")
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            key = (a.get("property") or a.get("name") or "").lower()
            self.meta.setdefault(key, a.get("content", ""))
        elif tag == "link":
            rel = a.get("rel", "").lower()
            if "stylesheet" in rel:
                self.sheets.append(a.get("href", ""))
            elif "icon" in rel:
                self.icons.append(a.get("href", ""))
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag in ("h1", "h2", "h3"):
            self.heading += 1
            self.headings.append("")
        if tag == "style":
            self.in_style = True
        if tag in SKIP:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag in ("h1", "h2", "h3"):
            self.heading = max(0, self.heading - 1)
        if tag == "style":
            self.in_style = False
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if self.in_style:
            self.css += " " + data
        if self.in_title:
            self.title += data
        elif not self.skip and data.strip():
            self.text.append(" ".join(data.split()))
            if self.heading:
                self.headings[-1] = (self.headings[-1] + " " + self.text[-1]).strip()


def fetch(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; studio-brand-extract)"})
    with urlopen(request, timeout=20) as response:
        return response.read(MAX_BYTES).decode("utf-8", "replace")


def colours(css):
    found = Counter()
    for value in HEX.findall(css):
        value = value[1:].lower()
        found["#" + (value if len(value) == 6 else "".join(c * 2 for c in value))] += 1
    for r, g, b in RGB.findall(css):
        if max(int(r), int(g), int(b)) < 256:
            found["#%02x%02x%02x" % (int(r), int(g), int(b))] += 1
    return found.most_common(12)


def fonts(css, sheets):
    found = Counter()
    for stack in FONT.findall(css):
        name = stack.split(",")[0].strip(" '\"")
        name = re.sub(r"^__|_[0-9a-f]{6}$", "", name).replace("_Fallback", "")
        if name and "var(" not in name and name.lower() not in GENERIC:
            found[name] += 1
    for sheet in sheets:
        if "fonts.googleapis.com" in sheet:
            for family in parse_qs(urlparse(sheet).query).get("family", []):
                found[family.split(":")[0]] += 1
    return [name for name, _ in found.most_common(6)]


def summarise(url, html, fetch_css):
    page = Page()
    page.feed(html)
    sheets = [urljoin(url, href) for href in page.sheets if href]
    css = page.css
    for sheet in sheets[:MAX_STYLESHEETS]:
        if "fonts.googleapis.com" not in sheet:
            css += " " + fetch_css(sheet)
    host = urlparse(url).netloc
    links = {urljoin(url, href).split("#")[0] for href in page.links}
    text = " ".join(page.text)[:MAX_TEXT]
    return {
        "url": url,
        "title": page.title.strip(),
        "description": page.meta.get("description") or page.meta.get("og:description", ""),
        "site_name": page.meta.get("og:site_name", ""),
        "image": page.meta.get("og:image", ""),
        "theme_color": page.meta.get("theme-color", ""),
        "icons": [urljoin(url, href) for href in page.icons[:4]],
        "colours": colours(css),
        "fonts": fonts(css, sheets),
        "headings": [h for h in page.headings if h][:30],
        "links": sorted(l for l in links if urlparse(l).netloc == host and USEFUL_LINK.search(urlparse(l).path))[:12],
        "text": text,
        "thin": len(text) < 200,
    }


def check():
    html = """<title>Acme</title><meta name="description" content="Ledgers">
    <style>body{color:#ABC;font-family:'Space Grotesk',sans-serif}</style>
    <h1>Plain <b>books</b></h1><p>Hello</p><script>var hidden=1</script><a href="/pricing">Pricing</a>"""
    out = summarise("https://acme.test/", html, lambda _: "")
    assert out["title"] == "Acme", out
    assert out["description"] == "Ledgers", out
    assert out["colours"] == [("#aabbcc", 1)], out
    assert out["fonts"] == ["Space Grotesk"], out
    assert out["headings"] == ["Plain books"], out
    assert "hidden" not in out["text"], out
    assert out["links"] == ["https://acme.test/pricing"], out
    print("ok")


def fetch_quietly(url):
    try:
        return fetch(url)
    except OSError:
        return ""


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        check()
    elif len(sys.argv) == 2 and urlparse(sys.argv[1]).scheme in ("http", "https"):
        try:
            print(json.dumps(summarise(sys.argv[1], fetch(sys.argv[1]), fetch_quietly), indent=1))
        except OSError as error:
            sys.exit(f"Could not read {sys.argv[1]}: {error}")
    else:
        sys.exit(__doc__)
