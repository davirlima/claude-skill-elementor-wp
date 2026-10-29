# Media optimization

## 1. Measure before converting
`scripts/page_check.mjs <url> --images` at 1440 and 390 lists each uploaded image's file, natural size, rendered size, object-fit, and total image bytes transferred. Note images rendered at a fraction of their size, PNG photos, and images used by scripts (rotators) that bypass `srcset`.

## 2. Convert
- Target width ≈ 2× the largest rendered width (cap at the original size — never upscale).
- Crop to the slot's ratio when the slot is fixed (cards with `object-fit: cover`), respecting `object-position` (e.g. `center top`) and the subject (check the crop visually — a centered crop once cut the subject named in the alt text; adjust the vertical focus).
- Keep transparency for product cut-outs (WebP supports alpha).
- Quality ≈ 0.8–0.85 for photos, 0.95 for logos. `scripts/to_webp.mjs spec.json` does resize/crop/convert in headless Chromium (no ImageMagick needed).
- Skip files that are already tiny (≤10 KB logos, 56px avatars) — not worth the risk.

## 3. Name for SEO
Lowercase, hyphenated, descriptive, local intent where honest: `aluguel-vw-polo-campo-grande.webp`, `franquia-locadora-de-veiculos-<brand>.webp`, `logo-<brand>-branco.webp`. No hashes, no "ChatGPT-Image-…", no duplicated words.

## 4. Upload and swap
- Multipart upload with `title` and `alt_text`; WordPress generates WebP intermediate sizes.
- Swap references by media ID **and** by URL across pages, Theme Builder templates and HTML widgets (`scripts/wp.py swap-media map.json <doc>`).
- Keep `image_size` sensible (`large`/`medium_large` for cards so `srcset` serves small files on mobile).
- Verify: no old filenames left in `_elementor_data`, rendered images load (no broken images), visual check, Lighthouse performance before/after (report weight, LCP, score).
- Old originals stay in the library until the user approves; deleting them is part of cleanup.

## 5. Images with text baked in (posters, banners, AI-generated art)
- **Never let a fixed-height slot crop them.** `object-fit: cover` with a fixed height (and `object-position: center top`) silently cuts the sides or the bottom at other breakpoints — where phone numbers and URLs usually sit. Give the image its own proportion at tablet/mobile (`aspect-ratio: W/H; height: auto`, optionally `max-width` + centered) and look at the result at 1440, ~820 and ~390 px.
- **Read the text in the image before publishing.** Generated images often drop or alter digits (a Brazilian mobile number missing its leading 9, a wrong URL). Zoom into the contact area (`to_webp.mjs` with a `crop`) and compare it with the real data; if it is wrong, stop and ask for a corrected image instead of publishing.
- **Replacing an image:** upload the new one under a new descriptive name (re-using the old name makes WordPress append `-1`), swap references with `wp.py swap-media`, verify on the live page, then download a backup of the old file and delete it (media has no trash).
