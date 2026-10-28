# Site cleanup

## Inventory
- Pages/posts with `status=any`: drafts marked "(antiga)/(old)", default "Hello world!", "Privacy Policy" sample.
- `elementor_library`: theme-pack templates (About, Contact, FAQ, Car Listing…), old headers/footers, unused kits, saved sections.
- `elementor_snippet` (including trashed ones).
- Media: `scripts/media_usage.py` cross-references every attachment against the rendered HTML of published pages (incl. 404), the Elementor data of published pages/templates/popups/active Kit, custom code, featured images, site logo/icon, and the OG image. Old optimized-away originals show up as unused.
- **Stores (WooCommerce):** run it with `--store` so product, gallery, variation and category images are protected, and render a few product, category, cart and checkout URLs too. Ask whether images are used outside the site (e-mail marketing, ads, product feeds) — no script can see that.
- Plugins with no remaining use (e.g. a widget pack whose widgets are gone but still loads CSS/JS everywhere) — recommend, don't deactivate without asking.

## Keep
Active Kit, Theme Builder templates in use, brand source files (original logo/icon at full resolution), OG image, everything referenced.

## Delete
1. Trash (reversible, 30 days): drafts, unused templates, sample post.
2. Permanent: trashed snippets you created and the user rejected.
3. Media: download every file to `backup-media-<site>-<date>/` mirroring `uploads/` paths + `manifest.json` (id, path, url, alt), verify each download, then `DELETE /wp/v2/media/<id>?force=true`. Retry individual failures.
4. Kits can't be deleted over REST — leave them and tell the user.

## Verify
All pages (desktop + mobile) load with no broken images and no failed requests (`scripts/page_check.mjs --broken`). Lazy images inside closed widgets (e.g. a chat avatar) can look "incomplete" — check the file returns 200 before calling it broken.
