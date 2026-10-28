# Design system in the Elementor Kit

Goal: every color and text style on the site comes from the active Kit, with names a designer understands, so a change in Site Settings updates the whole site and new elements are born on-brand.

## 1. Inventory first
- Identify the active Kit (`elementor-kit-<id>` body class). Theme packs leave extra kits and a kit named after the theme ("Kit Styles: <Theme>") — rename it, don't create another.
- Scan what the pages actually use: typography signatures and hex colors per widget (`scripts/apply_tokens.py --scan`). The most frequent combinations become the tokens; one-offs stay local.
- Note leftovers from the theme (unused fonts like Poppins, tokens named "Price", "Coming Soon"…) — they get removed.

## 2. Token set (adapt names to the brand)
Colors — system: Primary (brand), Secondary (titles), Text, Accent. Custom, named by role, not by hue alone:
- Brand dark (e.g. navy) · Brand color for text on light backgrounds (accessible variant) · Soft tint for icon/badge backgrounds · White · Light background · Muted background · Border · Text on dark backgrounds.

Typography — system: Primary = H1, Secondary = H2, Accent = H3, Text = body. Custom: compact H2, label/H4, highlight number, eyebrow, lead text, small text, badge, button, menu. Each with desktop/tablet/mobile sizes and line height.

A proven starting scale (adjust per brand fonts):

| Token | Size D/T/M | LH | Notes |
|---|---|---|---|
| H1 | 60/48/36 | 1.05 | title font, 600 |
| H2 | 44/36/30 | 1.15 | |
| H2 compact | 32/28/26 | 1.15 | CTA panels |
| H3 | 22/20/20 | 1.2 | cards, items |
| Label (H4) | 16 | 1.3 | letter-spacing 1 |
| Number | 48/44/40 | 1.0 | 700 |
| Eyebrow | 13/13/12 | 1.4 | text font 600, uppercase, spacing 2 |
| Lead | 18/17/16 | 1.6 | |
| Body | 16/16/15 | 1.6 | |
| Small | 14 | 1.5 | |
| Badge | 12 | 1.2 | 600, uppercase |
| Button | 14 | 1.2 | 600, uppercase, spacing 1 |
| Menu | 15 | 1.2 | 500 |

Spacing: section padding 96/24 (tablet 80/32, mobile 64/20); gaps 8·12·16·24·32·48·64; radius 12 (buttons/icons) · 20 (cards) · 32 (panels); boxed width 1200.

Ask before deciding title color: keeping titles in a neutral dark (graphite) and reserving the brand dark color for clickable things reads better; some brands prefer brand-colored titles.

## 3. Theme style defaults (Kit `__globals__`)
Set body typography/color, link normal/hover colors, H1–H6 typography and color, button typography/text/background/hover colors, form label/field typography and colors, button radius and padding, form field radius/padding, container width. The Kit's `button_padding` is what every button really uses (widget padding is ignored in Elementor 4) — set it to the value the approved design already shows, or every button on the site changes size.

## 4. Applying the Kit
1. Build the full Kit settings object (keep existing keys like `viewport_*`, `site_name`, Hello theme options).
2. Write it via REST (`meta._elementor_page_settings` on the kit post, plus a clear title), then call `elementor-update-page-settings` on the kit with the **full** object so the global CSS regenerates.
3. Run `scripts/apply_tokens.py` on every page and Theme Builder template: groups whose values exactly match a token become global references; matching hex colors become global colors. Report the leftovers (intentional one-offs).
4. Save each document through MCP (popups with full settings).
5. Verify: fonts loaded (only the brand fonts should appear in `fonts.googleapis.com` links), global CSS contains the new variables, and a before/after pixel diff of every page at desktop and mobile shows no visual change. Differences of a few pixels in page height usually come from button padding or line-height rounding — find the first changed region with a zoomed crop before accepting.
