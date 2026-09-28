# Fallback palette — only when the themes cannot be read

Part of [widget-design-spec.md](../widget-design-spec.md), section 2. Use it
only when themes-lite.json cannot be fetched at all.

If the network is blocked and you genuinely cannot fetch the catalogue, say so
in one line and use these instead. Never mix them with a theme's values — a
build is skinned by one or the other, not both.

```css
/* Brand */
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

Every text/surface pair above is at or beyond WCAG AA — the muted tone is
5.6:1 on the card. Do not substitute a lighter grey for it: that is the usual
way this palette gets broken, and dates and handles are the first things to
become unreadable.
