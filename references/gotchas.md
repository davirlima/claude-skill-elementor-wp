# Known traps (read before the first write on a new site)

Each entry: symptom → cause → what to do.

## Saving and rendering
- **Page looks unstyled after a REST write** → post CSS not regenerated / stale → trigger `elementor-update-page-settings` and wait for `post-<id>.css` to return 200 with the new content.
- **Change saved but the live page shows the old version** → Elementor element cache (Elementor → Settings → Performance → *Element Caching*) or a page cache → save through MCP; if a whole category of assets is missing (see animations), ask the user to set Element Caching to inactive and run Elementor → Tools → *Clear Files & Data*.
- **Popup lost its layout (full-width, no animation, no overlay)** → MCP save with partial settings replaced them → resend the full settings object from backup.
- **Rank Math says 0 words / no images / no links on an Elementor page** → `post_content` is empty because the page was never saved in the Elementor editor → rebuild it with `scripts/plain_content.py` and write it to `content` via REST. Elementor overwrites it with equivalent content next time someone saves in the editor.
- **Theme Builder import fails with multipart** → send JSON with base64 `fileData` instead.

## Elementor 4.x option values (classic widgets)
- Alignment values are logical: `start` / `center` / `end` (not `left`/`right`) for heading and text-editor `align`, icon-box `text_align`.
- Icon box position: `block-start` (icon on top) instead of `top`.
- Button icon side: `icon_align` = `row` (icon left) or `row-reverse` (icon right).
- Image object fit key is `object-fit` (with hyphen), plus `object-position`.
- **Button `button_padding` set on the widget is ignored** — every button uses the Kit's `button_padding`. Change padding in the Kit (it changes every button), or force it with `custom_css` on that widget when one button must differ (e.g. a square icon-only button: `selector .elementor-button{width:40px;height:40px;padding:0;display:inline-flex;align-items:center;justify-content:center}`).
- Kit `button_border_radius` etc. apply where the widget does not override.

## Security layers
- **ModSecurity (shared hosting)**: raw binary `POST` to `/wp/v2/media` → 406 → use multipart `-F file=@...`. Python `urllib` page fetches → 406 → use `curl`.
- **Wordfence**: application passwords can be disabled globally; 2FA on the integration user breaks MCP/REST. See `connection.md` §6.
- **Database without utf8mb4**: saving code/text with 4-byte characters (emoji, flag emojis) fails with `rest_meta_database_error` and may leave an empty half-created post → escape them (`&#x1F44B;` in HTML, `\u{1F44B}` in JS) and check for the orphan post.

## Content model
- **Kits cannot be deleted via REST** (`DELETE` returns a WordPress fatal-error page; the site stays fine). Leave unused kits or ask the user to delete them in wp-admin → Templates.
- The active Kit can be a kit imported from a theme pack with a misleading name; identify it by the `elementor-kit-<id>` body class before editing.
- Media has no trash — deletion is permanent.
- `post_content` of Elementor pages may reference old images; it is not what visitors see, but SEO plugins read it.
- `?m=` in a URL is a WordPress date query var → the page 404s in Lighthouse. Use `?v=`.

## Animations
- Entrance animations work in the editor but not on the live site, and elements "blink" in → the animation CSS files (`assets/lib/animations/styles/<name>.min.css`) were not enqueued. Seen with **Element Caching** active. Fix at the source (disable Element Caching, clear files & data). Do not paper over it with a Custom Code stylesheet link — the user explicitly rejected that workaround.
- Elementor's `elementor-invisible` hides an animated element until its waypoint fires — never animate the LCP element (H1, hero text, hero image) or Lighthouse LCP gets worse.

## Headless testing
- Chromium launched without `--user-data-dir` can attach to an already-running instance and exit immediately (the CDP endpoint never appears). Always pass a fresh `--user-data-dir`.
- Headless Chromium reports `(hover: none)`; to test hover styles launch with `--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4`.
- Don't `pkill -f` with a pattern that also matches your own shell command line.
- Carousels/rotators make pixel diffs noisy; freeze them (the screenshot script overrides `setInterval` for a given delay) or crop them out.
