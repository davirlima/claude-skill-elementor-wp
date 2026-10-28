---
name: elementor-wordpress
description: Professional workflow for building, refactoring and maintaining WordPress sites made with Elementor / Elementor Pro, operated remotely through the Elementor MCP server and the WordPress REST API. Covers page refactors with containers, Theme Builder (header, footer, 404, popups), global design system in the Elementor Kit, Rank Math SEO, Lighthouse accessibility, media optimization (WebP, SEO file names), entrance animations, site cleanup and safe publishing. Use this skill whenever the user mentions Elementor, an Elementor/WordPress site, a WordPress page, Theme Builder, the Elementor Kit or global styles, Rank Math, WP Rocket, a client site to refactor, "deixar no padrão do Elementor", or asks to create, clone, publish, optimize or clean pages on a WordPress site — even if they don't say "Elementor" explicitly.
---

# Elementor + WordPress — agency workflow

This skill captures how a web agency wants Claude to work on client WordPress sites built with Elementor.
The client sites vary (car rental, clinics, stores…), but the standard of work does not.
Talk to the user in their language (often Brazilian Portuguese), keep reports short, and lead with what changed and how it was verified.

## The standard the work is judged by

These are the reasons past deliveries were accepted or sent back. Keep them in mind on every task.

1. **Official components only.** Use widgets from Elementor, Elementor Pro and WordPress core. Third-party widget packs (Jeg Kit, Essential Addons, snippet plugins with custom effects) are replaced, not extended. When a native option exists (Theme Builder header/footer, Elementor Pro popup for a mobile menu, Custom Code for head tags, Motion Effects for animation), use it instead of hand-rolled HTML/JS. An HTML widget is acceptable only when no widget can do the job (e.g. a small rotation script), and then it is written in Elementor's frontend-handler style.
2. **Elementor conventions.** Flexbox containers (no legacy sections/columns), one boxed width (usually 1200px), consistent spacing tokens, responsive values set for tablet and mobile, header/footer in the Theme Builder instead of copied into each page, global colors and typography from the Kit instead of per-widget values.
3. **Institutional, not landing page.** On institutional sites, avoid landing-page tropes: no image-heavy hero on internal pages (a centered hero with headline, lead and CTAs works), no section repeated with a new skin, no audience labels that make one public feel secondary ("For you" / "For entrepreneurs" → neutral eyebrows such as "Rental" / "Franchise"). Alternate section backgrounds so the rhythm is visible.
4. **Typography and headings serve SEO.** One H1 per page, H2 per section, H3 for items; eyebrows are `<p>`, not headings. Use the brand's title font and text font (ask for them — do not assume), with a fixed scale.
5. **Conversion details matter.** Contact buttons (often WhatsApp) open with a pre-filled message per intent (rent vs. franchise vs. support), the brand icon sits to the left of the label, hero CTAs scroll to the relevant section, and every CTA has a clear verb.
6. **Accessibility 100 in Lighthouse** on every auditable page, achieved by real fixes (contrast, labels, landmarks), never by hiding things from the audit. See `references/accessibility.md`.
7. **Proportionality.** Improve what makes sense for the user. Don't game plugin scores (e.g. adding a number to every SEO title just because Rank Math asks); consistency across pages wins over a few points.
8. **Evidence before "done".** Every change is checked on the live site at desktop and mobile width (screenshots), plus Lighthouse when relevant. When a change should not alter visuals (refactors, token migration), compare before/after pixel by pixel. Say plainly what was not tested.
9. **Honesty about side effects.** If something you did broke something else (a popup losing its settings, a gradient losing its fade), say so, fix it, and mention it in the report.

## Safety rules (non-negotiable)

- **Back up before writing.** Save the current `_elementor_data` / settings of every document you are about to change (local JSON). Media deletion is permanent in WordPress — download originals plus a manifest before deleting.
- **Prefer reversible actions.** Old pages go to draft with the title suffix "(antiga)"/"(old)" and a `-antiga`/`-old` slug before a new version is published. Posts/templates go to the trash, not permanent deletion.
- **Confirm outward or destructive steps** (publishing a replacement home page, deleting content, deactivating plugins, changing slugs) unless the user already asked for exactly that.
- **Credentials stay out of files you share.** Read them from environment variables (`WP_URL`, `WP_USER`, `WP_APP_PASSWORD`). Never write an application password into the skill, a repo, or a published page. Remind the user that `claude mcp add --header` stores the header in plain text in `~/.claude.json`.

## Project kickoff

At the start of a new client/site, gather (from the conversation, the site, or by asking — keep questions few and specific):

- Site URL, WordPress/Elementor/Elementor Pro versions, theme (Hello Elementor is typical), active plugins (`GET /wp/v2/plugins`).
- Connection: Elementor MCP server configured? Application password user? See `references/connection.md`.
- Brand: title font, text font, primary/secondary/accent colors, logo (light/dark), favicon, tone (institutional vs. campaign).
- Contact channels: WhatsApp number(s) and one pre-filled message per intent, e-mail, address, social profiles that really exist (remove icons without a real link).
- Scope: which pages, which templates, SEO plugin (Rank Math assumed), staging or production.

Write the answers into a small project notes file in your scratchpad so later steps reuse them.

## Workflow

Work in this order on a full refactor; for single requests, jump to the relevant step. After each step, verify and report before moving on — the user iterates in small rounds ("only one more detail…"), so expect feedback and keep changes scoped.

1. **Connect and inventory** — pages, templates (`elementor_library` with `_elementor_template_type`), custom code, active Kit, plugins, media. (`references/connection.md`)
2. **Design system first** — organize the active Kit: named colors, typography scale, theme style defaults (body, headings, links, buttons, forms). (`references/design-system.md`)
3. **Theme Builder** — header, footer, 404 and the mobile-menu popup as site-wide templates with conditions. (`references/elementor-json.md` → Theme Builder)
4. **Pages** — build or refactor with `scripts/elementor_kit.py`, publish as a new page, archive the old one, set as front page if it is the home. (`references/page-patterns.md`)
5. **SEO** — per-page Rank Math title (one pattern for all pages), description, focus keyword, OG image, schema; regenerate `post_content` so Rank Math sees the content. (`references/seo-rankmath.md`)
6. **Accessibility** — Lighthouse loop until 100. (`references/accessibility.md`)
7. **Media** — WebP at 2× rendered size, cropped to the slot's ratio, SEO file names, alt text. (`references/media.md`)
8. **Motion** — subtle entrance animations via Motion Effects. (`references/animations.md`)
9. **Cleanup** — drafts, unused templates/kits/snippets, unused media (with backup). (`references/cleanup.md`)

## How changes are applied

The reliable pattern, learned the hard way:

1. `GET` the document with `context=edit` and save a backup.
2. Transform `_elementor_data` in Python (never by hand-editing huge JSON strings).
3. `POST` the new `_elementor_data` through the REST API.
4. Trigger an Elementor save with the MCP tool `elementor-update-page-settings` (`settings: {}`) so CSS, caches and revisions regenerate. **Exception:** popups (and any document whose settings matter) must receive their full settings object — an empty object wipes them.
5. Wait for the page CSS to refresh (it can 404 or be stale for 1–3 minutes), then verify on the live URL with a cache-busting query (`?v=<something>`; avoid `?m=`, which WordPress treats as a date archive).

`references/gotchas.md` lists every known trap (security plugins, ModSecurity, emoji encoding, element cache, Elementor 4 option names, button padding, kits that cannot be deleted…). Read it before the first write on a new site.

## Bundled scripts

All scripts read the connection from `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`, and Chromium from `CHROME_PATH` (falls back to the Playwright cache). Run them with `--help` for usage.

| Script | Use it to |
|---|---|
| `scripts/wp.py` | get/put/backup Elementor data, upload media, call Rank Math, list content |
| `scripts/elementor_kit.py` | build containers and official widgets bound to global tokens (import it) |
| `scripts/apply_tokens.py` | replace per-widget typography/colors with the Kit's global tokens |
| `scripts/add_animations.py` | apply the entrance-animation rules to a document |
| `scripts/plain_content.py` | rebuild `post_content` from the rendered `<main>` (for Rank Math/search) |
| `scripts/media_usage.py` | find media no published page/template uses; back up before deleting |
| `scripts/to_webp.mjs` | resize/crop/convert images to WebP in headless Chromium |
| `scripts/shoot.mjs` | full-page screenshots (desktop/mobile) with animations finished |
| `scripts/pixel_diff.mjs` | before/after pixel comparison and zoomed crops |
| `scripts/page_check.mjs` | rendered vs. natural image sizes, broken images, stuck animations, horizontal overflow |
| `scripts/lighthouse.sh` | Lighthouse accessibility/performance/SEO summary with failing items |

## Definition of done (per delivery)

- Live page checked at ~1440px and ~390px; screenshots looked at, not just taken.
- Lighthouse accessibility 100 on auditable pages (404s cannot be audited — say so).
- No horizontal overflow, no broken images, no element stuck invisible.
- Backups saved; anything deleted is recoverable (trash or local backup).
- Report: what changed (grouped, plain language), how it was verified, what was not tested, anything the user must do in wp-admin, and the preview links returned by the MCP tool (they require the user to be logged in).
