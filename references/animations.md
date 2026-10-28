# Entrance animations (Motion Effects)

What the user wants: subtle fade variations, fast speed, minimal delay — using Elementor's own Motion Effects, nothing custom.

Rules applied by `scripts/add_animations.py`:
- Duration `fast`; delays 0–300 ms, cascading in steps of ~80–100 ms.
- Short widgets (headings, short text, buttons, lists, icon boxes) → `fadeInUp`. Images, HTML, long text (>280 chars) and boxed containers (cards, panels) → `fadeIn` (a 400px card sliding up 100% of its height looks heavy).
- Grids (wrapping rows): each card animates as one block, staggered by column (0/100/200 ms).
- Side-by-side columns: the second column starts 100 ms after the first.
- First section: never animate the H1, the paragraph right after it, or images (they are LCP candidates; `elementor-invisible` would delay them). Animate eyebrow, buttons, trust list.
- Header, footer, floating buttons: no animation.
- Avoid Left/Right variants on large elements (they translate 100% of the width and can cause horizontal overflow on mobile).

Verify with `scripts/page_check.mjs <url> --animations`: after scrolling, no element may stay `.elementor-invisible`, `animationName` must not be `none` on animated elements, and horizontal overflow must be 0.

If animations run in the editor but not on the live site (elements blink in), the animation stylesheets are not being enqueued — see gotchas (Element Caching). Fix the setting with the user; don't inject the CSS manually.
