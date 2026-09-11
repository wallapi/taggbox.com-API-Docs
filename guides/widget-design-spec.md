# Widget design spec — tokens, layouts, states

The visual half of the brief for anything built on the Taggbox Developer API
(v3): the design tokens, the two default layouts, the card treatment and the
states a feed has to handle. The data half — endpoints, envelope, field names,
caching, the token rule — lives in [llms.txt](../llms.txt); this file never
contradicts it.

Point an AI at it instead of pasting a hundred lines of CSS into every prompt:

```
Design spec (tokens, layouts, states) - follow it exactly:
https://raw.githubusercontent.com/wallapi/taggbox.com-API-Docs/main/guides/widget-design-spec.md
```

If the AI cannot browse, the five brand colours below are the minimum worth
pasting inline: `--tbx-purple:#613983`, `--tbx-pink:#cc3d6f`,
`--tbx-pink-ink:#a82b56`, `--tbx-pink-lite:#eb5c99`, `--tbx-accent:#ff492c`.

---

## 1. Scoping — a widget is a guest on someone else's page

- Declare every custom property **on the widget's own root element**, never on
  `:root` and never on `<body>`. A host page may already define `--surface` or
  `--radius`; the two must not collide — which is also why every name is
  prefixed `--tbx-`.
- Prefix every class (`.tbx-*`) or render inside a shadow root. Do not style
  bare element selectors, and do not load a CSS framework.
- Set the font on the widget root only. Load Inter from Google Fonts only if
  the host page does not already load it; otherwise fall back to the stack.
- The widget must work more than once on the same page, and take per-instance
  options from `data-` attributes (`data-limit`, `data-layout`, `data-theme`,
  `data-mode`), never from globals.

## 2. Design tokens

Use exactly these. Do not invent other colours.

```css
/* Brand — identical in both themes */
--tbx-purple:    #613983;  /* headings, active states             */
--tbx-pink:      #cc3d6f;  /* links, primary accents              */
--tbx-pink-ink:  #a82b56;  /* link hover — darker, stays readable */
--tbx-pink-lite: #eb5c99;  /* gradients and fills ONLY, never text*/
--tbx-accent:    #ff492c;  /* one highlight only — use sparingly  */

/* Light theme */
--tbx-ink:       #09090b;  /* author names, headings              */
--tbx-body:      #3f3f46;  /* post text — softer than ink         */
--tbx-muted:     #6b6478;  /* handles, network, dates             */
--tbx-surface:   #ffffff;  /* card                                */
--tbx-bg:        #f7f7f9;  /* widget background behind the cards  */
--tbx-line:      rgba(9,9,11,.09);    /* hairline card border     */

/* Shape, depth, motion */
--tbx-radius:    14px;     /* cards; 8px for chips and buttons    */
--tbx-shadow:    0 1px 2px rgba(9,9,11,.05),
                 0 4px 12px rgba(9,9,11,.05);
--tbx-shadow-up: 0 2px 4px rgba(9,9,11,.06),
                 0 12px 28px rgba(9,9,11,.10);  /* card hover     */
--tbx-ring:      0 0 0 3px rgba(204,61,111,.35); /* focus ring    */
--tbx-ease:      150ms cubic-bezier(.2,0,.2,1);

/* Type and rhythm */
--tbx-font:      Inter, -apple-system, "Segoe UI", Roboto,
                 Helvetica, Arial, sans-serif;
--tbx-text:      15px/1.55;   /* post text                        */
--tbx-meta:      13px/1.4;    /* handle, network, date            */
--tbx-gap:       20px;        /* grid gutter and card padding     */
```

A gradient, where one is wanted:
`linear-gradient(135deg, var(--tbx-purple), var(--tbx-pink))`.

### Dark theme — ON BY DEFAULT

Remap **only** these tokens under `@media (prefers-color-scheme: dark)`, so the
brand hues stay recognisable. `data-theme="light"` / `data-theme="dark"` on the
mount element must override the OS preference in both directions — a host page
is often light while the OS is dark, so that override has to win.

```css
--tbx-ink:      #f4f4f5;   --tbx-body:     #d4d4d8;
--tbx-muted:    #a1a1aa;   --tbx-surface:  #18181b;
--tbx-bg:       #101012;   --tbx-line:     rgba(255,255,255,.10);
--tbx-pink:     #f472a0;   --tbx-pink-ink: #f9a8c4;
--tbx-purple:   #c4a5e0;
```

Every text/surface pair above is at or beyond WCAG AA (the muted tone is 5.6:1
on light, 6.9:1 on dark). Do not substitute a lighter grey for the muted tone —
that is the usual way this palette gets broken, and dates and handles are the
first things to become unreadable.

## 3. Card treatment (the shared baseline)

- `--tbx-surface` background, `--tbx-radius` corners, `--tbx-shadow`, **and** a
  1px `--tbx-line` border — the border is what keeps a card visible on a dark
  host page, where a shadow alone disappears.
- Hover lifts the card 2px and swaps to `--tbx-shadow-up` over `--tbx-ease`.
- Image flush to the top edge, `object-fit: cover`, with a `--tbx-bg`
  placeholder behind it so the grid never jumps while images load. Explicit
  `width`/`height` plus `loading="lazy" decoding="async"`.
- Header row: 32px round avatar (`author.avatar_url`, omitted entirely when
  null) beside the author name in `--tbx-ink` at 14px/600. Under it, handle +
  network name + date in `--tbx-muted` at `--tbx-meta`, separated by "·", the
  date wrapped in `<time datetime="…">`.
- Body: `content.text` in `--tbx-body` at `--tbx-text`, clamped to 5 lines
  (`-webkit-line-clamp`) so cards in a row stay comparable in height.
- Footer: the "View post" link in `--tbx-pink`, gaining an underline and
  `--tbx-pink-ink` on hover.
- Responsive to the **container**, not the viewport — the widget may sit in a
  narrow sidebar on a wide screen. Size the grid with a container query (or
  `grid-template-columns: repeat(auto-fill, minmax(260px, 1fr))`), not a
  viewport media query. Gutter and card padding both `--tbx-gap`.

## 4. Layout A — REEL (default for an embedded widget)

A rail of 9:16 media tiles, the shape people already read on their phone. It is
the default for a widget because the widget sits inside a page it does not own
and has to earn attention in a small space.

- Each post is one tile at `aspect-ratio: 9/16`, `--tbx-radius` corners,
  overflow hidden. Media fills the tile (`object-fit: cover`). No white card
  frame around it — the media IS the card.
- Horizontal scroll-snap rail: `display:flex`, `overflow-x:auto`,
  `scroll-snap-type: x mandatory`, `gap: --tbx-gap`. Each tile gets
  `scroll-snap-align: start` and a flex-basis near 280px. Hide the scrollbar
  visually, keep wheel and keyboard scrolling. Below a **container** width of
  480px, switch the same tiles to one column and let the page scroll them.
- Text sits ON the media, never under it: a bottom scrim
  `linear-gradient(to top, rgba(0,0,0,.78), rgba(0,0,0,.35) 45%, transparent)`
  with `content.text` over it in white, clamped to 3 lines. The scrim is what
  keeps text readable over an unpredictable photo — never put white text
  straight on an image.
- Author overlays the top-left over a matching top scrim: 28px round avatar
  plus handle in white at `--tbx-meta`.
- The whole tile is one `<a>` to `source.permalink`, showing `--tbx-ring` on
  `:focus-visible`. No separate "View post" button — the tile is the link.
- A post with no `"image"` entry in `media` gets a gradient tile instead:
  `linear-gradient(135deg, var(--tbx-purple), var(--tbx-pink))` with the text
  centred, white, clamped to 6 lines. A reel with holes in it looks broken; a
  text tile does not.
- A `"video"` entry renders as `<video muted playsinline loop preload="none">`
  with a poster, playing only while the tile is in view
  (`IntersectionObserver`) and pausing when it leaves.
- Arrow buttons at each end scroll by exactly one tile and hide when there is
  nothing further to scroll to. Left/right arrow keys move focus between tiles.

## 5. Layout B — WALL (default for a section on your own site)

A masonry mosaic. It is the default there because the section gets real width,
and a wall reads as a wall precisely BECAUSE the tiles are different heights.

- Columns via CSS multi-column so heights pack naturally: `columns: 4`,
  `column-gap: --tbx-gap`, every card `break-inside: avoid` with
  `margin-bottom: --tbx-gap`. Step down on **container** width, not viewport:
  4 above 1100px, 3 above 800px, 2 above 520px, 1 below.
- Keep each image's OWN aspect ratio: `width:100%`, `height:auto`, and the real
  `width`/`height` attributes on the `<img>` so nothing reflows as it loads. Do
  NOT crop to a fixed ratio — uniform crops are what turn a wall into a generic
  card grid.
- Card as in §3, but padding `--tbx-gap` on the text half only; the image stays
  flush to the top and side edges.
- Text-only posts become a tinted tile rather than an empty card: the
  `--tbx-purple` → `--tbx-pink` gradient at 8% opacity over `--tbx-surface`,
  `content.text` at 17px/1.5 in `--tbx-ink`, clamped to 10 lines. These tiles
  give the wall its rhythm — without them a text-heavy feed collapses into gaps.
- Footer row per card: 24px avatar, author name in `--tbx-ink`, network name and
  date in `--tbx-muted` at `--tbx-meta`, the "View post" link in `--tbx-pink`
  pushed right.
- Hover lifts the card 2px to `--tbx-shadow-up` and scales the image inside to
  1.03, clipped by the card's overflow.
- Every image `loading="lazy" decoding="async"`. A wall puts far more media on
  screen at once than a reel does; this is where it pays.

Other layouts on request: a uniform card grid, a vertical feed, or a
full-screen signage view — all of them reuse §2 and §3 unchanged.

## 6. States

- **Empty and error states render INSIDE the container.** The widget must never
  throw into the host page and never leave the container blank with no
  explanation.
- **Stale over blank.** When the API call fails, the server keeps serving the
  last successful cached copy (see llms.txt rule 7); the UI shows that copy, not
  an error.
- **Preview fallback.** Ship a small inline `SAMPLE_POSTS` array (3–4 posts, the
  same shape as `body.posts`). On load, try the endpoint first; if that fetch
  fails for ANY reason — a preview sandbox whose CSP blocks `connect-src`, a
  `file://` origin, no server running yet — render `SAMPLE_POSTS` instead of an
  error, with a small dismissible note: "preview data — live posts load when
  this runs on your server". A failed fetch must never be fatal, or the design
  cannot be reviewed at all. Never put a token on that path.
- **Loading.** Skeleton tiles in `--tbx-bg` at the final tile shape, so the
  layout does not jump when posts arrive.

## 7. Accessibility and motion

- Every link and control shows `--tbx-ring` on `:focus-visible`. Never
  `outline: none` without a replacement.
- Under `prefers-reduced-motion`, drop the hover lift, the image scale and every
  transition; never autoplay video — show the poster and a play affordance.
- Keep every text/surface pair at WCAG AA after any restyle, in both themes.
- Escape every value you print, and allow only `http(s)` URLs in `href` and
  `src` attributes.
