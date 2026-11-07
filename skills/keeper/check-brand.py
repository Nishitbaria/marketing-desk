#!/usr/bin/env python3
"""Check a brand scrape so a bad value is dropped, not repeated. Standard library only.

Brand: python3 skills/keeper/check-brand.py .firecrawl/home.json
Claims: python3 skills/keeper/check-brand.py .firecrawl/home.json .firecrawl/page-1.md \\
        --quotes .firecrawl/quotes.txt --lines .firecrawl/lines.txt
Self-check: python3 skills/keeper/check-brand.py --check

Claims come from files, one per line, so website text never reaches the shell.
"""
import argparse
import json
import re
import sys
from urllib.parse import urlparse

SOLID = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})")
SAFE_URL = re.compile(r"https?://[\w./?=&%#:+~-]+")
USEFUL_LINK = re.compile(r"about|pricing|plans|features|product|story|mission", re.I)
FIRST_LINK = re.compile(r"pricing|plans|about", re.I)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
ROLES = ("primary", "secondary", "accent", "background", "textPrimary", "textSecondary", "link")
GENERIC = {"inherit", "serif", "sans-serif", "monospace", "system-ui", "-apple-system",
           "blinkmacsystemfont", "ui-sans-serif", "ui-serif", "ui-monospace"}
MIN_QUOTE = 12
MIN_PAGE = 200
AA_TEXT, AA_LARGE = 4.5, 3.0
INVISIBLE = 1.1
SPELLING = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                          "\u2013": "-", "\u2014": "-", "\u00a0": " "})


def luminance(colour):
    h = colour[1:] if len(colour) == 7 else "".join(c * 2 for c in colour[1:])
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    r, g, b = ((c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4) for c in (r, g, b))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def contrast(pair, fg, bg, basis):
    r = ratio(fg, bg)
    status = "pass" if r >= AA_TEXT else "large-only" if r >= AA_LARGE else "fail"
    return {"pair": pair, "ratio": round(r, 2), "status": status, "basis": basis}


def solid(value):
    return isinstance(value, str) and SOLID.fullmatch(value.strip()) is not None


def first_font(stack):
    return next((f for f in stack or [] if f.lower() not in GENERIC), None)


def pick_fonts(b, notes):
    typo = b.get("typography") or {}
    stacks, families = typo.get("fontStacks") or {}, typo.get("fontFamilies") or {}
    roles = {f.get("role"): f.get("family") for f in b.get("fonts") or []}
    heading = first_font(stacks.get("heading"))
    reported = families.get("heading")
    if heading and reported and heading.lower() != reported.lower():
        notes.append(f"heading font: stack says {heading}, report says {reported}, kept the stack")
    body = first_font(stacks.get("body")) or first_font(stacks.get("paragraph"))
    return {"heading": heading or reported or roles.get("heading") or roles.get("display"),
            "body": body or families.get("primary") or roles.get("body")}


def pick_name(b, host):
    alt = (b.get("images") or {}).get("logoAlt") or ""
    alt = re.sub(r"\s*logo$", "", alt.strip(), flags=re.I)
    if alt:
        return alt
    name = (b.get("brandName") or "").strip()
    return name if 0 < len(name) <= 30 else host


def pick_links(scrape, host):
    links = []
    for url in scrape.get("links") or []:
        same = isinstance(url, str) and urlparse(url).hostname in (host, "www." + host)
        if same and SAFE_URL.fullmatch(url) and USEFUL_LINK.search(urlparse(url).path) and url not in links:
            links.append(url)
    return sorted(links, key=lambda u: not FIRST_LINK.search(u))[:3]


def check_brand(scrape):
    b = scrape.get("branding") or {}
    meta = scrape.get("metadata") or {}
    host = (urlparse(meta.get("sourceURL") or meta.get("url") or "").hostname or "").removeprefix("www.")
    notes, colours = [], {}
    raw = b.get("colors") or {}
    for role in ROLES:
        value = raw.get(role)
        if value is None:
            continue
        if solid(value):
            colours[role] = value.strip()
        else:
            notes.append(f"dropped {role}: {str(value)[:40]!r} is not a solid colour")
    bg = colours.get("background")
    for role in list(colours):
        if bg and role != "background" and ratio(colours[role], bg) < INVISIBLE:
            notes.append(f"dropped {role}: {colours.pop(role)} cannot be seen on {bg}")

    fonts = pick_fonts(b, notes)
    checks = []
    if bg and "textPrimary" in colours:
        checks.append(contrast("text on background", colours["textPrimary"], bg, "assumed"))
    button = (b.get("components") or {}).get("buttonPrimary") or {}
    if solid(button.get("textColor")) and solid(button.get("background")):
        checks.append(contrast("button text on button", button["textColor"], button["background"], "measured"))

    images = b.get("images") or {}
    logo = b.get("logo") or images.get("logo")
    if logo and not SAFE_URL.fullmatch(logo):
        notes.append("dropped logo: it is inline, not a URL")
        logo = None
    if not colours and not any(fonts.values()):
        raise ValueError("no colours and no fonts in this scrape")
    return {"name": pick_name(b, host), "colours": colours, "fonts": fonts, "contrast": checks,
            "logo": logo, "links": pick_links(scrape, host),
            "thin": len(scrape.get("markdown") or "") < MIN_PAGE, "notes": notes}


def clean(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text.translate(SPELLING))
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`#>]", "", text)
    return " ".join(text.lower().split())


def page_text(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if path.endswith(".json"):
        data = json.loads(raw)
        return data.get("markdown") or data.get("text") or ""
    return raw


def check_claims(page, quotes, lines):
    page = clean(page)
    numbers = set(NUMBER.findall(page))
    q = [{"text": t, "found": len(clean(t)) >= MIN_QUOTE and clean(t) in page} for t in quotes]
    n = [{"text": t, "unsupported": [x for x in NUMBER.findall(clean(t)) if x not in numbers]} for t in lines]
    return {"quotes": q, "lines": n, "thin": len(page) < MIN_PAGE,
            "dropped": sum(not x["found"] for x in q) + sum(bool(x["unsupported"]) for x in n)}


def read_lines(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def check():
    good = {"markdown": "x" * MIN_PAGE, "links": ["https://acme.test/features", "https://acme.test/pricing", "https://evil.test/about"],
            "metadata": {"sourceURL": "https://www.acme.test/"},
            "branding": {"colors": {"primary": "#00A3FF", "secondary": "transparent", "background": "#000000",
                                    "textPrimary": "#050505", "link": "#000"},
                         "typography": {"fontFamilies": {"heading": "Reported", "primary": "Inter"},
                                        "fontStacks": {"heading": ["Real", "serif"], "body": ["system-ui"]}},
                         "components": {"buttonPrimary": {"background": "#00A3FF", "textColor": "#FFFFFF"}},
                         "images": {"logoAlt": "Acme logo"}, "logo": "data:image/svg+xml;utf8,x"}}
    out = check_brand(good)
    assert out["name"] == "Acme", out
    assert out["colours"] == {"primary": "#00A3FF", "background": "#000000"}, out
    assert out["fonts"] == {"heading": "Real", "body": "Inter"}, out
    assert out["contrast"] == [{"pair": "button text on button", "ratio": 2.73, "status": "fail",
                                "basis": "measured"}], out
    assert out["logo"] is None and out["links"] == ["https://acme.test/pricing", "https://acme.test/features"], out
    assert len(out["notes"]) == 5, out
    assert round(ratio("#000000", "#ffffff"), 1) == 21.0
    try:
        check_brand({"branding": {}})
        raise SystemExit("an empty scrape passed")
    except ValueError:
        pass
    page = "Send [email](https://x.y) for developers \u2014 from $20 a month to 3 teams."
    out = check_claims(page, ["email for developers - from", "made up claim here", "short"],
                       ["Only $20 a month", "Trusted by 500 teams"])
    assert [x["found"] for x in out["quotes"]] == [True, False, False], out
    assert out["lines"][0]["unsupported"] == [] and out["lines"][1]["unsupported"] == ["500"], out
    assert out["dropped"] == 3 and out["thin"], out
    print("ok")


def main():
    if sys.argv[1:] == ["--check"]:
        return check()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pages", nargs="+")
    parser.add_argument("--quotes")
    parser.add_argument("--lines")
    args = parser.parse_args()
    if args.quotes or args.lines:
        page = "\n".join(page_text(p) for p in args.pages)
        out = check_claims(page, read_lines(args.quotes), read_lines(args.lines))
    else:
        with open(args.pages[0], encoding="utf-8") as f:
            try:
                out = check_brand(json.load(f))
            except ValueError as error:
                sys.exit(f"Could not use this scrape: {error}")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
