# Elementor data model (classic widgets, containers)

## Contents
1. Document shape
2. Units and common value objects
3. Global tokens in element settings
4. Typography groups per widget
5. Widgets used most (key settings)
6. Custom CSS, attributes, anchors
7. Theme Builder, popups, Custom Code
8. Motion Effects keys

## 1. Document shape
`_elementor_data` is a JSON **string** holding a list of elements:

```json
{"id": "a1b2c3d", "elType": "container", "isInner": false,
 "settings": {"content_width": "boxed", "flex_direction": "column"},
 "elements": [
   {"id": "e4f5a6b", "elType": "widget", "widgetType": "heading",
    "settings": {"title": "…", "header_size": "h2"}, "elements": []}
 ]}
```

- IDs: 7 lowercase hex chars, unique per document. Use `renew_ids()` when copying elements between documents.
- Top-level containers have `isInner: false`; nested ones `true`.
- Wrapping a page's content in one root container with `html_tag: "main"` and `_element_id: "content"` gives a `<main id="content">` landmark that makes the Hello theme skip link work.
- Page template for full-width pages built with Theme Builder header/footer: `_wp_page_template = "elementor_header_footer"`.

## 2. Units and value objects
- Size: `{"unit": "px", "size": 24, "sizes": []}` (also `em`, `%`, `vw`, `custom` with a string size like `"calc(50% - 16px)"`).
- Box (padding/margin/radius/border width): `{"unit": "px", "top": "16", "right": "28", "bottom": "16", "left": "28", "isLinked": false}` — values are strings.
- Gap: `{"column": "24", "row": "24", "isLinked": true, "unit": "px", "size": 24}`.
- Responsive variants: append `_tablet` / `_mobile` to the key (`padding_mobile`, `width_tablet`, `flex_direction_tablet`).
- Link: `{"url": "…", "is_external": "on"|"", "nofollow": "", "custom_attributes": "aria-label|Text"}`.
- Icon: `{"value": "fab fa-whatsapp", "library": "fa-brands"}` / `{"value": "fas fa-arrow-right", "library": "fa-solid"}`.

## 3. Global tokens in element settings
Globals live under `settings.__globals__`, keyed by the same control name; when a global is set, delete the local value:

```json
"__globals__": {"title_color": "globals/colors?id=secondary",
                "typography_typography": "globals/typography?id=primary"}
```

System IDs: colors `primary`, `secondary`, `text`, `accent`; typography `primary`, `secondary`, `text`, `accent`. Custom IDs are 7-char strings defined in the Kit (`custom_colors[]._id`, `custom_typography[]._id`).

## 4. Typography groups per widget
A typography group is the set of keys sharing a prefix and ending in `typography_typography` (`"custom"` when local). Common prefixes:

| Widget | Prefixes |
|---|---|
| heading, text-editor, button | `typography_` |
| icon-list | `icon_typography_` |
| icon-box | `title_typography_`, `description_typography_` |
| testimonial | `content_typography_`, `name_typography_`, `job_typography_` |

Keys in a group: `_font_family`, `_font_weight`, `_font_size(_tablet/_mobile)`, `_line_height(…)`, `_letter_spacing(…)`, `_text_transform`, `_font_style`, `_text_decoration`, `_word_spacing`. `scripts/apply_tokens.py` handles all of them generically.

## 5. Widgets used most
- **heading**: `title`, `header_size` (h1–h6, `p` for eyebrows/badges), `align`, `title_color`.
- **text-editor**: `editor` (HTML), `text_color`, `link_color`, `link_hover_color`, `paragraph_spacing`.
- **button**: `text`, `link`, `selected_icon`, `icon_align`, `icon_indent`, `background_color`, `button_text_color`, `button_background_hover_color`, `hover_color`, `border_*`, `align`, `align_mobile: "justify"` for full-width mobile buttons. Padding comes from the Kit (see gotchas).
- **image**: `image {id,url,alt,source:"library"}`, `image_size` (`full`, `large`, `medium_large`…), `width`, `height`, `object-fit`, `object-position`, `image_border_radius`.
- **icon-list**: `icon_list[] {text, selected_icon, link, _id}`, `view: "inline"`, `text_color`, `icon_color`, `text_color_hover`.
- **icon-box**: `selected_icon`, `title_text`, `description_text`, `title_size`, `position: "block-start"`, `view: "stacked"`, `primary_color`/`secondary_color`.
- **testimonial**, **icon**, **divider**, **social-icons**, **html** (last resort).
- Elementor Pro: **nav-menu**, **popup** documents, **table-of-contents**, **form**.

## 6. Custom CSS, attributes, anchors
- Pro custom CSS per element: `custom_css` with the `selector` keyword (`selector a{text-decoration:underline}`).
- Element ID / anchor: `_element_id` (`frota`, `unidades`); add `selector{scroll-margin-top:96px}` when the header is fixed.
- CSS classes: `_css_classes`.
- Link attributes (aria-label on icon-only links): `link.custom_attributes = "aria-label|Talk to us on WhatsApp"`.

## 7. Theme Builder, popups, Custom Code
- Header/footer/404 live in `elementor_library` with `_elementor_template_type` = `header` / `footer` / `error-404`; create them by importing template JSON (`{"version":"0.4","title":…,"type":"header","content":[…],"page_settings":[]}`) through the Site Editor endpoint, then set conditions (see connection.md).
- Once headers/footers are global, remove any copies embedded inside pages and set pages to `elementor_header_footer`.
- Active menu item on a shared header: highlight via the current-page class or per-page CSS; never duplicate headers per page.
- Popup trigger on a button/icon link (dynamic tag):
  `"__dynamic__": {"link": "[elementor-tag id=\"<7hex>\" name=\"popup\" settings=\"%7B%22popup%22%3A%22<popupId>%22%7D\"]"}`
- Head/body code (verification meta tags, third-party widgets/chatbots): Custom Code post (`elementor_snippet`), not a theme file edit and not an HTML widget repeated per page.

## 8. Motion Effects keys
- Widgets: `_animation` (e.g. `fadeInUp`), `_animation_delay` (ms, int), `animation_duration` (`""`, `"fast"`, `"slow"`).
- Containers: `animation`, `animation_delay`, `animation_duration`.
