# Accessibility (Lighthouse 100)

Run `scripts/lighthouse.sh <url> accessibility` on desktop and mobile for every auditable page; it prints failing audits with the offending nodes. 404 pages cannot be audited (status 404) — apply the same fixes and say so.

## Fixes that keep the brand
| Failing audit | Fix |
|---|---|
| Contrast on brand-color buttons with white text (bright orange/yellow/green) | Keep the button color, switch the label/icon to the brand dark (e.g. navy ≈6.5:1); hover stays dark background + white text. |
| Brand-color text on light backgrounds (eyebrows, links, hovers) | Add an accessible darker variant as a global color (e.g. orange `#FD8D14` → `#B45309`) for text on light; keep the bright one on dark backgrounds. |
| Text over gradients measured wrongly | Give the container a solid fallback in custom CSS: `selector{background-color:<darkest stop> !important;}` — but **not** on decorative gradients that fade to transparent (it kills the fade). |
| Muted gray text failing on tinted backgrounds | Use the Text token only on white; darken on tinted backgrounds. |
| Links rely on color | Underline links inside text blocks: `selector a{text-decoration:underline;text-underline-offset:3px;}`. Active menu item: brand-dark text + colored underline instead of color only. |
| Links/buttons without discernible name | `aria-label` via `link.custom_attributes` on icon-only links/buttons (floating WhatsApp, Instagram icon). Logo image alt like "<Brand> — página inicial". |
| Skip link target / no main landmark | Wrap page content in a root container `html_tag: main`, `_element_id: content`. |
| Images without alt | Set alt in the widget **and** in the media library (`alt_text`). Decorative images: empty alt. |
| Headings out of order | Eyebrows/badges as `p`, one H1, H2 per section, H3 in cards. |

For third-party widgets (chat, forms): visible focus styles, labels for inputs, `role="dialog"` with a labelled title, live region for messages, decorative indicators `aria-hidden`.
