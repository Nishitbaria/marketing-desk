#!/usr/bin/env python3
"""make_hook.py — render a UGC hook headline as a transparent PNG plate (Pillow) and
print an ffmpeg overlay command. DISTINCT from the bottom subtitles (media/subtitles):
boxed / outlined / script looks, its own fonts, colour, optional COLOUR emoji, and an
optional smaller subline. Top-anchored over the opening beat.

Presets (--style):
  box       white rounded plate, dark bold text              (boxed UGC label)
  outline   bold white text + thick black outline, no plate   (sparkle-emoji hook)
  script    flowing cursive (Caveat), white + soft outline     (handwritten hook)

Options:
  --sub "SUBLINE"   a smaller second line under the headline (e.g. ORGANIC CONTENT)
  --font PATH       override the preset typeface
  --fill / --box-color / --outline-color   colours (hex)
  --size, --outline-width, --pad, --radius, --start/--end, --top-frac

Emoji (colour): the headline may contain emoji; they render in colour via a colour-emoji
font resolved in this order — --emoji-font, fonts/NotoColorEmoji.ttf (bundled),
/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf (apt: fonts-noto-color-emoji),
Apple Color Emoji (local mac). None found -> emoji are dropped (words still render) with a
note; never a crash.
"""
import argparse, pathlib, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = pathlib.Path(__file__).parent / "fonts"

EMOJI_RE = re.compile(
    "([\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF"
    "\U0001F1E6-\U0001F1FF\U00002190-\U000021FF\U0000FE00-\U0000FE0F\U0000200D\U000020E3]+)"
)

# preset -> (font file, default text fill, plate?, default outline as fraction of size)
PRESETS = {
    "box":         ("Montserrat-ExtraBold.ttf",   "#111111", True,  0.0,  False),
    "outline":     ("Montserrat-ExtraBold.ttf",   "#FFFFFF", False, 0.06, False),
    "script":      ("Caveat-Regular.ttf",         "#FFFFFF", False, 0.035, False),
    "calligraphy": ("GreatVibes-Regular.ttf",     "#FFFFFF", False, 0.0,  True),
    "serif":       ("PlayfairDisplay-Italic.ttf", "#111111", True,  0.0,  False),
}

EMOJI_FALLBACKS = [
    FONTS / "NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
]


def resolve_emoji_font(arg):
    for c in ([arg] if arg else []) + EMOJI_FALLBACKS:
        if c and pathlib.Path(str(c)).exists():
            return str(c)
    return None


def resolve_font_path(arg, default):
    """A --font/--sub-font value may be a full path or a bare filename in ./fonts."""
    if not arg:
        return default
    if pathlib.Path(arg).exists():
        return arg
    cand = FONTS / arg
    return str(cand) if cand.exists() else arg


def segment(text):
    parts = [p for p in EMOJI_RE.split(text) if p]
    return [("emoji" if EMOJI_RE.fullmatch(p) else "text", p) for p in parts]


def emoji_image(cluster, target_h, emoji_font_path):
    if not emoji_font_path:
        return None
    for strike in (137, 136, 109, 128, 96, 160):
        try:
            f = ImageFont.truetype(str(emoji_font_path), strike)
            canvas = strike * 3
            img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
            ImageDraw.Draw(img).text((strike, strike), cluster, font=f, embedded_color=True)
            bbox = img.getbbox()
            if not bbox:
                continue
            img = img.crop(bbox)
            h = img.height or 1
            return img.resize((max(1, round(img.width * target_h / h)), target_h), Image.LANCZOS)
        except Exception:
            continue
    return None


def render_line(text, font, fill, ow, outline_color, emoji_font, plate=False,
                box_color="#FFFFFF", radius=0, pad=0, shadow=False):
    """One line (text + inline colour emoji) as an RGBA image; optional plate behind it."""
    asc, desc = font.getmetrics()
    line_h = asc + desc + 2 * max(ow, 1)
    cap_h = int((asc + desc) * 0.92)
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    runs, dropped = [], False
    for kind, s in segment(text):
        if kind == "text":
            w = int(probe.textlength(s, font=font)) + (2 * ow if ow else 0)
            runs.append(("text", s, w))
        else:
            img = emoji_image(s, cap_h, emoji_font)
            if img is None:
                dropped = True
                continue
            runs.append(("emoji", img, img.width + int(font.size * 0.08)))
    content_w = sum(w for *_, w in runs) or 1
    m = max(ow + 2, round(font.size * 0.10)) if shadow else ow + 2
    W = content_w + (2 * pad if plate else 2 * m)
    H = line_h + (2 * pad if plate else 2 * m)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if plate:
        d.rounded_rectangle([0, 0, W - 1, H - 1], radius=radius, fill=box_color)
    x = pad if plate else m
    y = pad if plate else m
    for run in runs:
        if run[0] == "text":
            d.text((x + (ow if ow else 0), y), run[1], font=font, fill=fill,
                   stroke_width=ow, stroke_fill=outline_color, anchor="la")
            x += run[2]
        else:
            im.alpha_composite(run[1], (x, y + (cap_h - run[1].height) // 2 + int(cap_h * 0.02)))
            x += run[2]
    if shadow and not plate:
        off = max(2, round(font.size * 0.04))
        alpha = im.split()[3]
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", im.size, (0, 0, 0, 150)), (0, 0), alpha)
        sh = sh.filter(ImageFilter.GaussianBlur(max(2, round(font.size * 0.03))))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(sh, (off, off))
        out.alpha_composite(im, (0, 0))
        im = out
    return im, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("--style", choices=list(PRESETS), default="box")
    ap.add_argument("--sub", default=None, help="smaller second line under the headline (no plate)")
    ap.add_argument("--sub-font", dest="sub_font", default=None,
                    help="font for the subline (default: main font; use a serif/sans to contrast a calligraphy/script headline)")
    ap.add_argument("--font", default=None)
    ap.add_argument("--emoji-font", dest="emoji_font", default=None)
    ap.add_argument("--size", type=int, default=76)
    ap.add_argument("--fill", default=None)
    ap.add_argument("--box-color", dest="box_color", default="#FFFFFF")
    ap.add_argument("--outline-color", dest="outline_color", default="#000000")
    ap.add_argument("--outline-width", dest="outline_width", type=int, default=None,
                    help="stroke px (default: from preset)")
    ap.add_argument("--pad", type=int, default=None)
    ap.add_argument("--radius", type=int, default=None)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=2.0)
    ap.add_argument("--top-frac", dest="top_frac", type=float, default=0.10)
    ap.add_argument("-o", "--out", default="hook.png")
    a = ap.parse_args()

    fontfile, def_fill, plate, def_ow_frac, def_shadow = PRESETS[a.style]
    fill = a.fill or def_fill
    ow = a.outline_width if a.outline_width is not None else round(a.size * def_ow_frac)
    pad = a.pad if a.pad is not None else int(a.size * 0.42)
    radius = a.radius if a.radius is not None else int(a.size * 0.45)
    font_path = resolve_font_path(a.font, str(FONTS / fontfile))
    eff_size = round(a.size * 1.45) if a.style == "calligraphy" else a.size  # Great Vibes reads small; scale up
    font = ImageFont.truetype(font_path, eff_size)
    emoji_font = resolve_emoji_font(a.emoji_font)

    head, dropped = render_line(a.text, font, fill, ow, a.outline_color, emoji_font,
                                plate=plate, box_color=a.box_color, radius=radius, pad=pad,
                                shadow=def_shadow)

    # Optional subline: smaller, no plate, same treatment, sits under the headline.
    if a.sub:
        sfont = ImageFont.truetype(resolve_font_path(a.sub_font, font_path), max(18, int(a.size * 0.5)))
        sow = max(0, round(ow * 0.5)) if not plate else 0
        sub, sdrop = render_line(a.sub, sfont, fill if plate else "#FFFFFF", sow,
                                 a.outline_color, emoji_font, plate=False, pad=0)
        dropped = dropped or sdrop
        gap = int(a.size * 0.22)
        W = max(head.width, sub.width)
        H = head.height + gap + sub.height
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        im.alpha_composite(head, ((W - head.width) // 2, 0))
        im.alpha_composite(sub, ((W - sub.width) // 2, head.height + gap))
    else:
        im = head

    out = pathlib.Path(a.out)
    im.save(out)
    print(f"wrote {out}  ({im.width}x{im.height})  style={a.style}"
          f"{' +sub' if a.sub else ''}  emoji_font={'yes' if emoji_font else 'NONE'}")
    if dropped:
        print("note: emoji dropped (no colour-emoji font found); words still render. "
              "Bundle fonts/NotoColorEmoji.ttf or apt-get install fonts-noto-color-emoji.")
    print("overlay (add the PNG as a 2nd input, burn for the hook window):")
    print(f'  ffmpeg -i VIDEO.mp4 -i "{out.name}" -filter_complex '
          f'"[0][1]overlay=(W-{im.width})/2:H*{a.top_frac:g}:enable=\'between(t,{a.start:g},{a.end:g})\'" '
          f'-c:a copy VIDEO_hook.mp4')


if __name__ == "__main__":
    main()
