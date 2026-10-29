# Page patterns and publishing

## 1. Refactoring an existing page
1. Read the old page completely (structure + content + images + links). Keep the user's own recent containers as the reference style if they rebuilt some.
2. Rebuild as a **new page** (draft), with official widgets only, one H1, semantic headings, all copy preserved unless improving it was requested.
3. Show screenshots, iterate on feedback.
4. Publish on approval: new page published with the final title/slug; old page → draft, title + " (antiga)", slug + "-antiga". If it is the home: `PUT /wp/v2/settings {"show_on_front":"page","page_on_front":<id>}`.
5. Update menus/links that pointed to old URLs; keep slugs stable when possible (changing a slug needs redirects).

## 2. Section rhythm
- Hero → content sections → final CTA; alternate backgrounds (white / light) so sections read as distinct.
- Section head = eyebrow (`p`) + H2 + optional lead, centered, max-width ~720px.
- Avoid repeating the same section pattern twice on a page (e.g. two card grids with icons one after the other); merge or change the layout.
- Cards: white, 1px border, radius 20, subtle shadow, hover border in brand color.
- Grids: 3 or 4 columns desktop, 2 or 1 tablet, 1 mobile.

## 3. Heroes
- Home: headline with the main keyword (H1), lead, primary CTA to the main section (anchor) + secondary contact CTA, three short trust points, optional media (image card / rotating product images with a lightweight script).
- Institutional internal pages (About, Franchise, Privacy): centered hero without image, eyebrow + H1 + lead + CTAs.
- Never animate the hero H1, lead or hero image (LCP).

## 4. CTAs and contact
- WhatsApp: `https://wa.me/<digits>?text=<urlencoded message>`; one message per intent; brand icon on the left (`icon_align: row`); open in new tab.
- Dual CTA blocks for two audiences (customer / partner) use neutral eyebrows and equal visual weight; brand-dark gradient for one, brand-color gradient for the other.
- A floating contact button or chatbot is site-wide (Custom Code or footer template), not per page. Keep its z-index below Elementor popups (popups ≈ 9999) so the mobile menu opens over it.

## 5. Header, footer, 404, privacy
- Header (fixed, rounded card style is common): logo with alt "<Brand> — página inicial", menu in the user's order, primary CTA button; mobile menu = Elementor Pro popup sliding from the side (380px / 86vw, overlay in brand dark at ~55%, close button, prevent scroll, a11y navigation).
- Footer: logo, tagline, menu, address/phone/e-mail with icons, only social profiles that exist, privacy policy link, secondary CTA link. When the business has a separate line per intent (e.g. rental vs. franchise), list each number with a label ("Rental: …", "Franchise: …") and link each to its own pre-filled message; keep the mobile-menu popup's contact block consistent with the footer.
- 404 (Theme Builder `error-404`): big number, friendly H1, lead, buttons (home + main section), quick links.
- Privacy policy page in the same visual standard: sections numbered H2, LGPD-aware content (controller, data collected incl. chat/forms, purposes, legal bases, sharing incl. third-party services, retention, rights, contact). Flag that it needs legal review. The contact line of the policy uses the e-mail only (the user preferred no phone number there); the chat/forms and third-party services the site really uses must appear in "data collected" and "sharing".

## 6. Third-party widgets pasted by the user (chatbots etc.)
Install via Custom Code (body end). Before installing, adapt rather than rewrite: brand texts/colors/fonts, links (privacy URL), assets hosted on the client domain (not on another site's staging), z-index, 16px inputs on mobile, focus styles, aria labels, contrast, reset the theme's global button/heading typography inside the widget. Keep the behaviour intact and list every change. Test the flow without submitting real leads.
