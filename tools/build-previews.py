#!/usr/bin/env python3
"""Build guides/previews/<theme>.html - one finished preview.html per theme.

Each file is what step 2 of the guided build hands the user unchanged: the
theme's values as --tbx-* variables, the layout CSS for that theme only, and
the first 6 sample posts written into the markup. Every theme uses the SAME
card markup; only the root class and CSS differ, so the stack files can render
one card template for all themes.

It also writes templates/themes/<theme>.css + .json (the same CSS and card
layout, read by the starter code), templates/samples/, and one zip per stack
in templates/dist/.

Run from the repo root after changing a sample file, themes-lite.json, the
CSS below or a starter:  python3 tools/build-previews.py
"""
import html
import json
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "guides" / "previews"
THEME_OUT = ROOT / "templates" / "themes"
SAMPLE_OUT = ROOT / "templates" / "samples"
DIST = ROOT / "templates" / "dist"
STACKS = ["php", "nodejs", "react", "html"]
POSTS_PER_PREVIEW = 6
# Gallery sprite: px per thumbnail and WebP quality. Wider = sharper but a longer page to copy.
SPRITE_WIDTH = 300
SPRITE_QUALITY = 40

# Theme name -> (file slug, layout, card parts in order).
# Layouts: grid, list, masonry, collage, slider. Parts: media, head, stars, text.
# Taken from the Taggbox theme thumbnails (bigThumb<themeId>.png).
THEMES = {
    "Classic Card":       ("classic-card",       "grid",    ["head", "text", "media"]),
    "Social Card":        ("social-card",        "grid",    ["media", "head", "text"]),
    "Modern Card":        ("modern-card",        "grid",    ["media", "text", "head"]),
    "Classic Photo":      ("classic-photo",      "grid",    ["media", "head"]),
    "Square Photo":       ("square-photo",       "grid",    ["media"]),
    "Collage":            ("collage",            "collage", ["media", "text"]),
    "Vivid":              ("vivid",              "masonry", ["media", "head", "text"]),
    "Horizontal Slider":  ("horizontal-slider",  "slider",  ["media"]),
    "Horizontal Columns": ("horizontal-columns", "slider",  ["media", "head", "text"]),
    "Slider":             ("slider",             "slider",  ["media"]),
    "Reels":              ("reels",              "slider",  ["media"]),
    "Story Theme":        ("story-theme",        "slider",  ["media", "head"]),
    "Single Post":        ("single-post",        "slider",  ["media"]),
    "Widget Theme":       ("widget-theme",       "list",    ["head", "media", "text"]),
    "Review Box":         ("review-box",         "grid",    ["stars", "text", "head"]),
    "Review Carousel":    ("review-carousel",    "slider",  ["stars", "text", "head"]),
    "Review List":        ("review-list",        "list",    ["head", "stars", "text"]),
    "Rating Badge":       ("rating-badge",       "badge",   []),
    "Badge":              ("badge",              "badge",   []),
}

# Step 1's theme list: number = position here. (themeId, type label, what it looks like)
GALLERY = {
    "Classic Card": (5, "social", "cards: author on top, text, image at the bottom"),
    "Social Card": (19, "social", "cards: image on top, author, then text"),
    "Modern Card": (20, "social", "cards: image on top, text, author at the bottom"),
    "Classic Photo": (3, "social", "16:9 photo cards with only the author row under them"),
    "Square Photo": (4, "social", "a grid of square photos, nothing else"),
    "Collage": (50, "social", "one big photo beside two small stacked ones"),
    "Vivid": (83, "social", "mosaic of cards with pastel gradient text panels"),
    "Horizontal Slider": (16, "social", "one row of photos, arrows on the ends"),
    "Horizontal Columns": (47, "social", "a slider of cards, avatar on the photo edge, centred text"),
    "Slider": (81, "social", "a slider of square rounded photos"),
    "Reels": (61, "social", "a row of tall 9:16 reel tiles"),
    "Story Theme": (60, "social", "tall story cards, the middle one in focus"),
    "Single Post": (52, "social", "one big photo at a time, arrows on its sides"),
    "Widget Theme": (49, "social", "one post centred: author, wide photo, text"),
    "Review Box": (79, "reviews", "a grid of review cards, stars on top"),
    "Review Carousel": (80, "reviews", "one row of review cards, arrows on the ends"),
    "Review List": (85, "reviews", "full-width review rows stacked down the page"),
}

GALLERY_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="https://raw.githack.com/sudarshanbairagi-taggbox/test-code-m/main/guides/" target="_blank">
<title>Social Widget - themes</title>
<style>
  body { margin: 0; font: 15px/1.4 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; background: #f4f5f8; color: #1f1f1f; }
  main { max-width: 1200px; margin: 0 auto; padding: 32px 16px; }
  h1 { margin: 0 0 4px; text-align: center; }
  p { margin: 0 0 24px; text-align: center; opacity: .7; }
  .g { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
  .t { display: flex; flex-direction: column; gap: 4px; padding: 10px; background: #fff; border-radius: 10px;
    box-shadow: 0 1px 6px rgba(0,0,0,.08); color: inherit; text-decoration: none; }
  .t:hover { box-shadow: 0 4px 16px rgba(0,0,0,.14); }
  .t i { display: block; aspect-ratio: 971 / 701; border-radius: 6px; overflow: hidden;
    background: #fff url(SPRITE) 0 0 / 100% FRAMES% no-repeat; }
  .t img { display: block; width: 100%; height: 100%; object-fit: contain; background: #fff; }
</style>
</head>
<body>
<main>
  <h1>Social Widget - pick a theme</h1>
  <p>Reply in the chat with the theme's number. Click a theme to open its preview with sample posts.</p>
  <div class="g">
TILES
  </div>
</main>
</body>
</html>
"""


def gallery_sprite(ids):
    """Every thumbnail stacked in one small base64 WebP. The chat that shows the gallery (step 1)
    often blocks outside images, so this is all it shows - it must be sharp yet short, as the AI
    copies it character for character. The real PNGs load on top of it where they can."""
    try:
        import base64, io
        from PIL import Image, ImageFilter
    except ImportError:  # no Pillow: keep the sprite already in the page
        old = (ROOT / "guides/theme-gallery.html").read_text()
        return old.split("background: #fff url(", 1)[1].split(")", 1)[0]
    w = SPRITE_WIDTH
    h = round(w * 701 / 971)
    sheet = Image.new("RGB", (w, h * len(ids)), "white")
    for i, tid in enumerate(ids):
        im = Image.open(ROOT / f"guides/themes/bigThumb{tid}.png").convert("RGBA")
        flat = Image.new("RGBA", im.size, "white")
        flat.alpha_composite(im)
        im = flat.convert("RGB")
        im.thumbnail((w, h), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(1, 60, 2))
        sheet.paste(im, ((w - im.width) // 2, i * h + (h - im.height) // 2))
    buf = io.BytesIO()
    sheet.save(buf, "WEBP", quality=SPRITE_QUALITY, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def build_gallery():
    """guides/theme-gallery.html: every theme's thumbnail with its number, for step 1."""
    tiles = []
    n = len(GALLERY)
    for i, (name, (tid, *_)) in enumerate(GALLERY.items(), 1):
        slug = THEMES[name][0]
        pos = f"{(i - 1) * 100 / (n - 1):.4g}%"
        tiles.append(f'  <a class="t" href="previews/{slug}.html"><i style="background-position:0 {pos}">'
                     f'<img src="themes/bigThumb{tid}.png" alt="" loading="lazy" onerror="this.remove()"></i>'
                     f'<b>{i}. {esc(name)}</b></a>')
    page = (GALLERY_PAGE.replace("SPRITE", gallery_sprite([v[0] for v in GALLERY.values()]))
            .replace("FRAMES", str(n * 100)).replace("TILES", "\n".join(tiles)))
    (ROOT / "guides/theme-gallery.html").write_text(page)


# Short brand marks for the network badge (no external icon files).
NET_MARK = {
    "instagram": "IG", "facebook": "f", "twitter": "X", "x": "X", "tiktok": "♪",
    "youtube": "▶", "linkedin": "in", "pinterest": "P", "google": "G",
    "yelp": "y", "tripadvisor": "T", "trustpilot": "★",
}

BASE_CSS = """
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--tbx-bg); color: var(--tbx-text);
    font-family: var(--tbx-font); font-weight: var(--tbx-weight); font-size: var(--tbx-size); }
  .tbx-widget { max-width: 1200px; margin: 0 auto; padding: 32px 16px; }
  .tbx-header { margin: 0 0 24px; text-align: center; font-size: 1.9em; font-weight: 700; }
  /* Card: one markup for every theme; the theme block below orders and hides parts */
  .tbx-card { display: flex; flex-direction: column; background: var(--tbx-surface); color: inherit;
    text-decoration: none; border-radius: var(--tbx-radius); overflow: hidden; text-align: var(--tbx-align); }
  /* --tbx-ph: the sample file's tiny base64 thumbnail (preview only; live posts have none) */
  .tbx-media { position: relative; overflow: hidden; border-radius: var(--tbx-img-radius);
    aspect-ratio: var(--tbx-ar, auto);
    background: var(--tbx-ph, none) center / cover no-repeat, linear-gradient(135deg, #e6e8f2, #f3e6ee); }
  /* Fallback tile: chat preview panes block outside images, so show the network name */
  .tbx-media::after { content: attr(data-network); position: absolute; inset: 0; display: grid;
    place-items: center; font-size: .85em; letter-spacing: .06em; text-transform: uppercase; opacity: .45; }
  .tbx-media img { position: relative; z-index: 1; display: block; width: 100%; height: 100%; object-fit: cover; }
  /* Blocked image: cover the broken-image icon with the thumbnail, if any */
  .tbx-media img::before { content: ""; position: absolute; inset: 0;
    background: var(--tbx-ph, none) center / cover no-repeat; }
  .tbx-play { position: absolute; z-index: 2; right: 10px; top: 10px; width: 28px; height: 28px;
    border-radius: 50%; background: rgba(0,0,0,.55); }
  .tbx-play::before { content: ""; position: absolute; left: 11px; top: 8px;
    border-left: 9px solid #fff; border-top: 6px solid transparent; border-bottom: 6px solid transparent; }
  .tbx-head { display: flex; align-items: center; gap: 10px; padding: var(--tbx-pad); }
  .tbx-avatar { flex: none; width: 36px; height: 36px; border-radius: 50%; object-fit: cover;
    background: #d9dbe3; display: grid; place-items: center; font-weight: 700; color: #555; }
  /* Blocked avatar: show the author's initial instead of a broken-image icon */
  img.tbx-avatar { position: relative; }
  img.tbx-avatar::before { content: attr(data-initial); position: absolute; inset: 0; display: grid;
    place-items: center; border-radius: 50%; background: #d9dbe3; }
  .tbx-who { flex: 1; min-width: 0; display: flex; flex-direction: column; text-align: left; }
  .tbx-author { color: var(--tbx-author); font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .tbx-date { font-size: .8em; opacity: .6; }
  .tbx-net { flex: none; width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center;
    background: #888; color: #fff; font: 700 11px/1 system-ui, sans-serif; }
  .tbx-net::before { content: attr(data-mark); }
  .tbx-net[data-net="instagram"] { background: linear-gradient(45deg, #f9ce34, #ee2a7b 55%, #6228d7); }
  .tbx-net[data-net="facebook"] { background: #1877f2; }
  .tbx-net[data-net="twitter"], .tbx-net[data-net="x"], .tbx-net[data-net="tiktok"] { background: #111; }
  .tbx-net[data-net="youtube"] { background: #ff0000; }
  .tbx-net[data-net="linkedin"] { background: #0a66c2; }
  .tbx-net[data-net="pinterest"] { background: #e60023; }
  .tbx-net[data-net="google"] { background: #4285f4; }
  .tbx-net[data-net="yelp"] { background: #d32323; }
  .tbx-net[data-net="tripadvisor"] { background: #34e0a1; color: #000; }
  .tbx-net[data-net="trustpilot"] { background: #00b67a; }
  .tbx-stars { padding: var(--tbx-pad) var(--tbx-pad) 0; text-align: center; color: #f5b50a; letter-spacing: 2px; }
  .tbx-text { margin: 0; padding: 0 var(--tbx-pad) var(--tbx-pad); line-height: 1.5; }
  .tbx-card > :first-child.tbx-text { padding-top: var(--tbx-pad); }
  .tbx-clamp .tbx-text { display: -webkit-box; -webkit-box-orient: vertical;
    -webkit-line-clamp: var(--tbx-lines); line-clamp: var(--tbx-lines); overflow: hidden; }
  /* Starters only: no posts yet, and the "sample posts" note */
  .tbx-empty, .tbx-note { text-align: center; opacity: .7; margin: 0 0 16px; }
"""

LAYOUT_CSS = {
    "grid": """
  /* Grid: --tbx-cols columns, 2 on tablet, 1 on phone */
  .tbx-track { display: grid; gap: var(--tbx-gap); align-items: start;
    grid-template-columns: repeat(var(--tbx-cols), minmax(0, 1fr)); }
  @media (max-width: 900px) { .tbx-track { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 560px) { .tbx-track { grid-template-columns: 1fr; } }
""",
    "list": """
  /* List: one column */
  .tbx-track { display: grid; gap: var(--tbx-gap); max-width: 640px; margin: 0 auto; }
""",
    "masonry": """
  /* Masonry: CSS columns, each card keeps its own height */
  .tbx-track { column-count: var(--tbx-cols); column-gap: var(--tbx-gap); }
  .tbx-card { break-inside: avoid; margin-bottom: var(--tbx-gap); }
  @media (max-width: 900px) { .tbx-track { column-count: 2; } }
  @media (max-width: 560px) { .tbx-track { column-count: 1; } }
""",
    "collage": """
  /* Collage: 3 columns of square tiles, the 1st of every 3 is a 2x2 feature tile */
  .tbx-track { display: grid; gap: var(--tbx-gap); grid-template-columns: repeat(3, minmax(0, 1fr));
    grid-auto-rows: 1fr; grid-auto-flow: dense; max-width: 900px; margin: 0 auto; }
  .tbx-card { position: relative; aspect-ratio: 1 / 1; }
  .tbx-card:nth-child(3n + 1) { grid-column: span 2; grid-row: span 2; }
  .tbx-card:nth-child(6n + 4) { grid-column: 2 / span 2; }
  .tbx-card .tbx-media { position: absolute; inset: 0; }
  .tbx-card .tbx-text { display: none; }
  .tbx-card--text .tbx-text { display: -webkit-box; padding: 16px; }
  .tbx-card--text { justify-content: center; background: linear-gradient(135deg, #fbe3c4, #f6c1d3); }
  /* Hover: darken, network badge and a "View post" button */
  .tbx-card::after { content: "View post"; position: absolute; z-index: 3; left: 50%; top: 58%;
    transform: translateX(-50%); padding: 8px 18px; border: 2px solid #fff; color: #fff;
    background: rgba(0,0,0,.45); opacity: 0; transition: opacity .2s; }
  .tbx-card:hover::after, .tbx-card:focus-visible::after { opacity: 1; }
  /* Phone: 2 columns, only the very first tile is big */
  @media (max-width: 700px) { .tbx-track { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .tbx-card:nth-child(n) { grid-column: auto; grid-row: auto; }
    .tbx-card:first-child { grid-column: span 2; grid-row: span 2; } }
""",
    "badge": """
  /* Badge: one summary of all reviews - logo, average score, stars, count */
  .tbx-badge { display: flex; margin: 0 auto; background: var(--tbx-surface); border-radius: 10px;
    box-shadow: 0 2px 14px rgba(0,0,0,.09); color: inherit; }
  .tbx-badge-nets { display: flex; }
  .tbx-badge-title { font-size: 1.1em; }
  .tbx-badge-score { display: flex; align-items: center; gap: 10px; }
  .tbx-badge-avg { font-weight: 700; line-height: 1; }
  .tbx-badge .tbx-stars { padding: 0; font-size: 1.5em; }
  .tbx-badge-count { font-size: .9em; opacity: .75; }
""",
    "slider": """
  /* Slider: one row that scrolls sideways; the arrows scroll one view */
  .tbx-slider { position: relative; }
  .tbx-track { display: flex; gap: var(--tbx-gap); overflow-x: auto; scroll-snap-type: x mandatory;
    scrollbar-width: none; padding: 4px 2px 12px; }
  .tbx-track::-webkit-scrollbar { display: none; }
  .tbx-card { flex: 0 0 calc((100% - (var(--tbx-cols) - 1) * var(--tbx-gap)) / var(--tbx-cols));
    scroll-snap-align: start; }
  @media (max-width: 900px) { .tbx-card { flex-basis: calc((100% - var(--tbx-gap)) / 2); } }
  @media (max-width: 560px) { .tbx-card { flex-basis: 85%; } }
  .tbx-arrow { position: absolute; z-index: 4; top: 50%; transform: translateY(-50%); width: 36px; height: 36px;
    border: 0; border-radius: 50%; background: #fff; color: #333; font-size: 20px; cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,.2); }
  .tbx-arrow--prev { left: -10px; }
  .tbx-arrow--next { right: -10px; }
""",
}

# Per-theme look, on top of the layout. Scoped to the theme's root class.
THEME_CSS = {
    "modern-card": """
  .tbx-card { border: 1px solid #dcdde3; }
  .tbx-text { padding-top: var(--tbx-pad); }
""",
    "classic-card": """
  .tbx-card { box-shadow: 0 2px 10px rgba(0,0,0,.08); }
""",
    "social-card": """
  .tbx-card { border: 1px solid #dcdde3; }
""",
    "square-photo": """
  .tbx-card { border-radius: 0; background: none; }
  .tbx-media { aspect-ratio: 1 / 1; }
""",
    "classic-photo": """
  .tbx-card { box-shadow: 0 2px 10px rgba(0,0,0,.1); }
""",
    "collage": "",
    "horizontal-columns": """
  .tbx-card { box-shadow: 0 2px 10px rgba(0,0,0,.08); text-align: center; }
  .tbx-media { aspect-ratio: 4 / 3; }
  /* Avatar sits on the image edge, name and badge centred under it */
  .tbx-head { flex-direction: column; margin-top: -28px; position: relative; z-index: 2; gap: 6px; }
  .tbx-avatar { width: 48px; height: 48px; border: 3px solid #fff; }
  .tbx-who { text-align: center; align-items: center; }
""",
    "horizontal-slider": """
  .tbx-card { border-radius: 0; background: none; }
  .tbx-media { aspect-ratio: 7 / 6; }
  .tbx-arrow { border-radius: 2px; background: rgba(0,0,0,.75); color: #fff; }
  .tbx-arrow--prev { left: 8px; } .tbx-arrow--next { right: 8px; }
""",
    "slider": """
  .tbx-card { background: none; }
  .tbx-media { aspect-ratio: 1 / 1; }
  /* Hover: darken the photo and show the network name */
  .tbx-media::before { content: attr(data-network); position: absolute; z-index: 2; inset: 0; display: grid;
    place-items: center; color: #fff; font-weight: 700; background: rgba(0,0,0,.4); opacity: 0; transition: opacity .2s; }
  .tbx-card:hover .tbx-media::before, .tbx-card:focus-visible .tbx-media::before { opacity: 1; }
""",
    "story-theme": """
  .tbx-card { position: relative; background: none; border-radius: 22px; opacity: .45; transform: scale(.92);
    transition: opacity .2s, transform .2s; }
  /* The middle story is in focus; the others fade until hovered */
  .tbx-card:nth-child(2), .tbx-card:hover, .tbx-card:focus-visible { opacity: 1; transform: none; }
  .tbx-media { aspect-ratio: 9 / 15; border-radius: 22px; }
  .tbx-head { position: absolute; z-index: 2; left: 0; right: 0; bottom: 0; flex-direction: column; gap: 4px;
    padding-bottom: 18px; color: #fff; background: linear-gradient(transparent, rgba(0,0,0,.65)); border-radius: 0 0 22px 22px; }
  .tbx-who { text-align: center; align-items: center; }
  .tbx-author { color: #fff; }
  .tbx-avatar { width: 48px; height: 48px; border: 3px solid #fff; }
""",
    "single-post": """
  .tbx-slider { max-width: 560px; margin: 0 auto; }
  .tbx-card { flex-basis: 100%; border-radius: 0; background: none; }
  .tbx-media { aspect-ratio: 1 / 1.07; }
  .tbx-arrow { width: 48px; height: 48px; background: rgba(255,255,255,.85); }
  .tbx-arrow--prev { left: 12px; } .tbx-arrow--next { right: 12px; }
  @media (max-width: 900px) { .tbx-card { flex-basis: 100%; } }
""",
    "reels": """
  .tbx-card { background: none; }
  .tbx-media { aspect-ratio: 9 / 16; }
  .tbx-arrow { display: none; }
""",
    "vivid": """
  /* Each card gets one of six soft gradients; text-only cards are fully tinted */
  .tbx-card { background: var(--tbx-tint); }
  .tbx-card:nth-child(6n + 1) { --tbx-tint: linear-gradient(135deg, #fff1a8, #ffd98a); }
  .tbx-card:nth-child(6n + 2) { --tbx-tint: linear-gradient(135deg, #b8f0c8, #8fdcc0); }
  .tbx-card:nth-child(6n + 3) { --tbx-tint: linear-gradient(135deg, #ffd0b8, #f2a98f); }
  .tbx-card:nth-child(6n + 4) { --tbx-tint: linear-gradient(135deg, #a9c8ff, #5f8ef2); }
  .tbx-card:nth-child(6n + 5) { --tbx-tint: linear-gradient(135deg, #c3eaff, #9fd6f7); }
  .tbx-card:nth-child(6n + 6) { --tbx-tint: linear-gradient(135deg, #ffb3c7, #e8708f); }
""",
    "widget-theme": """
  .tbx-track { gap: 32px; }
  .tbx-card { text-align: center; }
  .tbx-text { padding: var(--tbx-pad) 24px 24px; }
""",
    "review-carousel": """
  .tbx-card { box-shadow: 0 2px 10px rgba(0,0,0,.08); }
  .tbx-stars { padding-top: 16px; }
  .tbx-text { padding-top: 10px; }
""",
    "review-list": """
  .tbx-card { box-shadow: 0 2px 12px rgba(0,0,0,.07); }
  .tbx-stars { padding-top: 0; }
  .tbx-text { padding-top: 8px; }
""",
    "rating-badge": """
  .tbx-badge { width: 180px; flex-direction: column; text-align: center; gap: 8px; padding: 18px 14px; }
  .tbx-badge-nets .tbx-net:not(:first-child) { display: none; }
  .tbx-badge-nets .tbx-net { width: 34px; height: 34px; font-size: 15px; }
  .tbx-badge-score { flex-direction: column; gap: 6px; }
  .tbx-badge-avg { font-size: 2.4em; }
""",
    "badge": """
  .tbx-badge { width: 320px; flex-direction: column; align-items: flex-start; gap: 10px; padding: 20px 24px; }
  .tbx-badge-title { display: none; }
  .tbx-badge-nets .tbx-net { margin-right: -6px; border: 2px solid #fff; }
  .tbx-badge-avg { font-size: 2.1em; }
  .tbx-badge-count { text-decoration: underline; }
""",
    "review-box": """
  .tbx-track { max-width: 760px; margin: 0 auto; }
  .tbx-card { box-shadow: 0 2px 12px rgba(0,0,0,.07); }
  .tbx-stars { padding-top: 16px; }
  .tbx-text { padding-top: 10px; }
""",
}

# Columns (or cards per view) per theme when the theme's numberOfColumn is 0
# or more than 4 - the thumbnails all show 3, or 2 for Review Box.
DEFAULT_COLS = {"review-box": 2, "widget-theme": 1, "review-list": 1, "single-post": 1}


def esc(value):
    return html.escape(str(value), quote=True)


def short_date(iso):
    d = datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")
    return f"{d:%b} {d.day}, {d.year}"


def first_image(post):
    """The first media entry of type image, never media[0] (it can be a video)."""
    for m in post.get("media") or []:
        if m.get("type") == "image" and m.get("cdn_url", "").startswith(("http://", "https://")):
            return m
    return None


def visible(posts, parts):
    """Photo-only themes skip posts without an image - they would be empty cards."""
    if parts != ["media"]:
        return posts
    return [p for p in posts if first_image(p)]


def card(post, parts):
    name = post["author"].get("name") or post["author"].get("handle") or ""
    net = post["network"]
    slug = net["slug"]
    image = first_image(post) if "media" in parts else None
    img = image["cdn_url"] if image else None
    thumb = image.get("preview_data_uri", "") if image else ""
    has_video = any(m.get("type") == "video" for m in post.get("media") or [])
    link = post["source"].get("permalink") or "#"
    text = post["content"].get("text") or ""

    blocks = {}
    if img:
        play = '<span class="tbx-play"></span>' if has_video else ""
        # Tiny data: thumbnail shows where a chat pane blocks the real image.
        # Width/height keep the tile's shape when the image cannot load.
        style = f"--tbx-ar:{image['width']} / {image['height']};" if image.get("width") and image.get("height") else ""
        if thumb.startswith("data:image/"):
            style += f"--tbx-ph:url({thumb})"
        ph = f' style="{esc(style)}"' if style else ""
        blocks["media"] = (f'<div class="tbx-media" data-network="{esc(net["name"])}"{ph}>'
                           f'<img src="{esc(img)}" alt="" loading="lazy">{play}</div>')
    avatar = post["author"].get("avatar_url")
    avatar_html = (f'<img class="tbx-avatar" src="{esc(avatar)}" alt="" loading="lazy" '
                   f'data-initial="{esc(name[:1].upper())}">' if avatar
                   else f'<span class="tbx-avatar">{esc(name[:1].upper())}</span>')
    author_html = f'<span class="tbx-author">{esc(name)}</span>' if name else ""
    blocks["head"] = (f'<div class="tbx-head">{avatar_html}<div class="tbx-who">{author_html}'
                      f'<time class="tbx-date" datetime="{esc(post["created_at"])}">{short_date(post["created_at"])}</time></div>'
                      f'<span class="tbx-net" data-net="{esc(slug)}" data-mark="{esc(NET_MARK.get(slug, net["name"][:1]))}" '
                      f'title="{esc(net["name"])}"></span></div>')
    rating = post.get("rating")
    if rating:
        blocks["stars"] = (f'<div class="tbx-stars" aria-label="{rating} out of 5">'
                           f'{"★" * rating}{"☆" * (5 - rating)}</div>')
    if text:
        blocks["text"] = f'<p class="tbx-text">{esc(text)}</p>'

    inner = "\n      ".join(blocks[p] for p in parts if p in blocks)
    cls = "tbx-card" if img or "media" not in parts else "tbx-card tbx-card--text"
    return (f'    <a class="{cls}" href="{esc(link)}" target="_blank" rel="noopener noreferrer">\n'
            f'      {inner}\n    </a>')


def badge(posts):
    """Rating Badge / Badge: the average of every rated post, its stars and the count."""
    rated = [p for p in posts if isinstance(p.get("rating"), (int, float)) and 1 <= p["rating"] <= 5]
    nets = []
    for p in rated:
        n = p.get("network") or {}
        if n.get("slug") and n["slug"] not in [x["slug"] for x in nets]:
            nets.append({"slug": n["slug"], "name": n.get("name") or ""})
    avg = sum(p["rating"] for p in rated) / len(rated) if rated else 0
    title = f'{nets[0]["name"]} Reviews' if len(nets) == 1 else "Customer Reviews"
    full = int(avg + 0.5)
    marks = "".join(f'<span class="tbx-net" data-net="{esc(n["slug"])}" data-mark="{esc(NET_MARK.get(n["slug"], n["name"][:1]))}" '
                    f'title="{esc(n["name"])}"></span>' for n in nets)
    return (f'  <div class="tbx-badge">\n'
            f'    <div class="tbx-badge-nets">{marks}</div>\n'
            f'    <div class="tbx-badge-title">{esc(title)}</div>\n'
            f'    <div class="tbx-badge-score"><span class="tbx-badge-avg">{avg:.1f}</span>'
            f'<span class="tbx-stars" aria-label="{avg:.1f} out of 5">{"★" * full}{"☆" * (5 - full)}</span></div>\n'
            f'    <div class="tbx-badge-count">Based on {len(rated)} review{"" if len(rated) == 1 else "s"}</div>\n'
            f'  </div>')


def theme_vars(style, slug):
    font = style.get("css_font") or ""
    font_stack = (f'"{font}", ' if font else "") + 'system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif'
    cols = style.get("numberOfColumn") or 0
    if not 1 <= cols <= 4:
        cols = DEFAULT_COLS.get(slug, 3)
    lines = style.get("lineTrim") or 0
    return {
        "--tbx-bg": style.get("backgroundColor") or "#ffffff",
        "--tbx-surface": style.get("cardColor") or style.get("backgroundColor") or "#ffffff",
        "--tbx-text": style.get("fontColor") or "#000000",
        "--tbx-author": style.get("authorColor") or style.get("fontColor") or "#000000",
        "--tbx-font": font_stack,
        "--tbx-weight": style.get("font_varient") or "400",
        "--tbx-size": f'{style.get("fontSize") or 14}px',
        "--tbx-radius": f'{style.get("roundEdge") or 0}px',
        "--tbx-img-radius": f'{style.get("borderRadius") or 0}px',
        # The thumbnails always show a gap, even on themes saved with spacing 0.
        "--tbx-gap": f'{max(style.get("spacing") or 0, 10)}px',
        "--tbx-pad": f'{max(style.get("padding") or 0, 8) + 4}px',
        "--tbx-cols": str(cols),
        "--tbx-align": style.get("textAlignment") or "left",
        "--tbx-lines": str(lines or "none"),
    }, font, lines


def theme_bundle(name, theme_type, style):
    """Everything a starter needs for one theme: its CSS and how to lay out a card."""
    slug, layout, parts = THEMES[name]
    if style.get("hideContent") == 1 and "text" in parts:
        parts = [p for p in parts if p != "text"]
    vars_, font, lines = theme_vars(style, slug)

    # Photo-first themes: white text on a white page is unreadable, so keep text dark.
    if vars_["--tbx-text"].lower() in ("#fff", "#ffffff") and vars_["--tbx-bg"].lower() in ("#fff", "#ffffff"):
        vars_["--tbx-text"] = "#1f1f1f"  # fontColor #ffffff on a white page - darkened so it reads
    ratio = style.get("aspectImageRatio") or 0
    ratio_css = {100: "  .tbx-media { aspect-ratio: 1 / 1; }\n",
                 56.25: "  .tbx-media { aspect-ratio: 16 / 9; }\n"}.get(ratio, "")

    root = "\n".join(f"    {k}: {v};" for k, v in vars_.items())
    css = (f"  /* {name} theme - values from themes-lite.json. Change the look here. */\n"
           f"  :root {{\n{root}\n  }}\n{BASE_CSS}{LAYOUT_CSS[layout]}{THEME_CSS[slug]}{ratio_css}")
    font_url = ""
    if font:
        font_url = f"https://fonts.googleapis.com/css2?family={font.replace(' ', '+')}:wght@300;400;600;700&display=swap"
    meta = {"name": name, "slug": slug, "type": theme_type, "layout": layout, "parts": parts,
            "clamp": bool(lines), "font_url": font_url}
    return meta, css


def build(name, theme_type, style, posts):
    meta, css = theme_bundle(name, theme_type, style)
    slug, layout, parts = meta["slug"], meta["layout"], meta["parts"]
    font_link = ""
    if meta["font_url"]:
        font_link = (f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                     f'<link rel="stylesheet" href="{meta["font_url"]}">\n')

    cards = "\n".join(card(p, parts) for p in visible(posts, parts))
    clamp = " tbx-clamp" if meta["clamp"] else ""
    script = ""
    if layout == "badge":
        body = badge(posts)
    elif layout == "slider":
        body = (f'  <div class="tbx-slider">\n'
                f'  <button class="tbx-arrow tbx-arrow--prev" type="button" data-dir="-1" aria-label="Previous">‹</button>\n'
                f'  <div class="tbx-track">\n{cards}\n  </div>\n'
                f'  <button class="tbx-arrow tbx-arrow--next" type="button" data-dir="1" aria-label="Next">›</button>\n'
                f'  </div>')
        script = ("\n<script>\n  // Arrows scroll the row by one view. No data is fetched.\n"
                  "  document.querySelectorAll('.tbx-arrow').forEach(function (b) {\n"
                  "    b.addEventListener('click', function () {\n"
                  "      var t = b.parentNode.querySelector('.tbx-track');\n"
                  "      t.scrollBy({ left: b.dataset.dir * t.clientWidth, behavior: 'smooth' });\n"
                  "    });\n  });\n</script>")
    else:
        body = f'  <div class="tbx-track">\n{cards}\n  </div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Social Widget</title>
{font_link}<style>
{css}</style>
</head>
<body>
<!-- Social Widget preview: {name}. Sample posts only - calls no API. -->
<section class="tbx-widget tbx-t-{slug} tbx-l-{layout}{clamp}">
  <h1 class="tbx-header">Social Widget</h1>
{body}
</section>{script}
</body>
</html>
"""


def add(z, path, name):
    """Zip entry with a fixed date, so rebuilding unchanged files gives an identical zip."""
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, path.read_bytes())


def build_html_index():
    """Simple HTML's index.html reuses the Node starter's card renderer, so all stacks match."""
    node = (ROOT / "templates/nodejs/server.js").read_text()
    seg = node.split("// ---------- HTML (same markup as preview.html) ----------")[1].split("function renderPage")[0].strip()
    (ROOT / "templates/html/index.html").write_text(HTML_INDEX_BEFORE + seg.replace("\n", "\n  ") + HTML_INDEX_AFTER)


HTML_INDEX_BEFORE = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Social Widget</title>\n<!-- Theme CSS: posts.php serves themes/<WIDGET_THEME>.css + custom.css -->\n<link rel="stylesheet" href="posts.php?css=1">\n</head>\n<body>\n<!-- Social Widget - Simple HTML starter. No framework, no build step.\n     The token lives only in posts.php (View Source here shows none). -->\n<section class="tbx-widget" id="social-widget">\n  <h1 class="tbx-header">Social Widget</h1>\n  <p class="tbx-empty">Loading posts…</p>\n</section>\n<script>\n(function () {\n  // Same card markup as preview.html. Every value is escaped before it is\n  // written; links and images are limited to http(s).\n  '

HTML_INDEX_AFTER = '\n\n  var root = document.getElementById(\'social-widget\');\n\n  function show(data) {\n    var meta = data.theme;\n    var posts = visiblePosts(data.posts || [], meta.parts);\n    root.className = \'tbx-widget tbx-t-\' + meta.slug + \' tbx-l-\' + meta.layout + (meta.clamp ? \' tbx-clamp\' : \'\');\n    var note = data.sample ? \'<p class="tbx-note">Sample posts - set ACCESS_TOKEN in .env to show your gallery.</p>\' : \'\';\n    var track = posts.length\n      ? \'<div class="tbx-track">\' + posts.map(function (p) { return renderCard(p, meta.parts); }).join(\'\\n\') + \'</div>\'\n      : \'<p class="tbx-empty">No posts to show yet.</p>\';\n    if (meta.layout === \'badge\' && posts.length) track = renderBadge(posts);\n    if (meta.layout === \'slider\' && posts.length) {\n      track = \'<div class="tbx-slider"><button class="tbx-arrow tbx-arrow--prev" type="button" data-dir="-1" aria-label="Previous">‹</button>\'\n        + track + \'<button class="tbx-arrow tbx-arrow--next" type="button" data-dir="1" aria-label="Next">›</button></div>\';\n    }\n    root.innerHTML = \'<h1 class="tbx-header">Social Widget</h1>\' + note + track;\n    // Arrows scroll the row by one view.\n    root.querySelectorAll(\'.tbx-arrow\').forEach(function (b) {\n      b.addEventListener(\'click\', function () {\n        var t = b.parentNode.querySelector(\'.tbx-track\');\n        t.scrollBy({ left: b.dataset.dir * t.clientWidth, behavior: \'smooth\' });\n      });\n    });\n  }\n\n  fetch(\'posts.php\')\n    .then(function (r) { if (!r.ok) throw new Error(\'HTTP \' + r.status); return r.json(); })\n    .then(show)\n    .catch(function () {\n      root.querySelector(\'.tbx-empty\').textContent =\n        \'Could not load posts. Open this page through a PHP server (see README) - preview.html shows the design without one.\';\n    });\n})();\n</script>\n</body>\n</html>\n'


def main():
    themes = {t["name"]: t for t in json.loads((ROOT / "guides/themes-lite.json").read_text())["themes"]}
    social = json.loads((ROOT / "guides/sample-posts-social.json").read_text())[:POSTS_PER_PREVIEW]
    reviews = json.loads((ROOT / "guides/sample-posts-reviews.json").read_text())[:POSTS_PER_PREVIEW]
    OUT.mkdir(parents=True, exist_ok=True)
    THEME_OUT.mkdir(parents=True, exist_ok=True)
    for name, (slug, _, _) in THEMES.items():
        theme = themes[name]
        posts = reviews if theme["type"] == "review" else social
        (OUT / f"{slug}.html").write_text(build(name, theme["type"], theme["style"], posts))
        meta, css = theme_bundle(name, theme["type"], theme["style"])
        (THEME_OUT / f"{slug}.css").write_text(css)
        (THEME_OUT / f"{slug}.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"guides/previews/ and templates/themes/: {len(THEMES)} themes")
    build_gallery()
    # Themes no longer in THEMES must not linger as stale files.
    keep = {v[0] for v in THEMES.values()}
    for folder, ext in ((OUT, ".html"), (THEME_OUT, ".css"), (THEME_OUT, ".json")):
        for f in folder.glob("*" + ext):
            if f.stem not in keep:
                f.unlink()

    # The starters show the same 6 sample posts as the previews until a token is set.
    # They run in a real browser, where the images load, so the base64 thumbnails are left out.
    def lean(posts):
        return [{**p, "media": [{k: v for k, v in m.items() if k != "preview_data_uri"} for m in p.get("media") or []]}
                for p in posts]
    SAMPLE_OUT.mkdir(parents=True, exist_ok=True)
    (SAMPLE_OUT / "social.json").write_text(json.dumps(lean(social), indent=2, ensure_ascii=False) + "\n")
    (SAMPLE_OUT / "reviews.json").write_text(json.dumps(lean(reviews), indent=2, ensure_ascii=False) + "\n")

    build_html_index()

    # Simple HTML's posts.php = the PHP starter's settings, API and cache code + a JSON tail,
    # so both PHP files always share one tested implementation.
    php = (ROOT / "templates/php/index.php").read_text()
    core = php.split("// ---------- HTML (same markup as preview.html) ----------")[0]
    core = core.replace("// Social Widget - PHP starter (PHP 8, nothing to install).\n"
                        "// Renders the Taggbox gallery's posts as one finished HTML page.",
                        "// Social Widget - Simple HTML starter: the one server file (PHP 8).\n"
                        "// index.html fetches this file; it calls Taggbox and returns JSON.")
    tail = (ROOT / "templates/html/posts-tail.php.txt").read_text()
    (ROOT / "templates/html/posts.php").write_text(
        "<?php\n// GENERATED by tools/build-previews.py from templates/php/index.php - edit that file.\n"
        + core.split("<?php\n", 1)[1] + tail)

    # One zip per stack: its starter files + every theme + the samples.
    DIST.mkdir(parents=True, exist_ok=True)
    for stack in STACKS:
        src = ROOT / "templates" / stack
        target = DIST / f"social-widget-{stack}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            top = f"social-widget-{stack}/"
            for f in sorted(src.rglob("*")):
                if f.is_file() and not f.name.endswith(".txt") and not (
                        {"node_modules", "cache", "dist", ".env"} & set(f.relative_to(src).parts)):
                    add(z, f, top + f.relative_to(src).as_posix())
            for f in sorted(THEME_OUT.iterdir()):
                add(z, f, top + "themes/" + f.name)
            for f in sorted(SAMPLE_OUT.iterdir()):
                add(z, f, top + "samples/" + f.name)
        print(f"templates/dist/{target.name}")

        # The same files as one text file, for an AI to fetch in one go and hand over in the
        # chat (step 4). Themes are left out - the AI fetches only the one theme it needs.
        parts = []
        files = [f for f in sorted(src.rglob("*")) if f.is_file() and not f.name.endswith(".txt")
                 and not ({"node_modules", "cache", "dist", ".env"} & set(f.relative_to(src).parts))]
        for f in files + sorted(SAMPLE_OUT.iterdir()):
            rel = f.relative_to(src).as_posix() if f.is_relative_to(src) else "samples/" + f.name
            parts.append(f"===== FILE: {rel} =====\n{f.read_text().rstrip()}\n")
        header = (f"# Social Widget - {stack} starter, every file in one text file.\n"
                  f"# Each file below starts with its own FILE line (five = signs, FILE:, its path). Generated by tools/build-previews.py.\n\n")
        (DIST / f"social-widget-{stack}.txt").write_text(header + "\n".join(parts))


if __name__ == "__main__":
    main()
