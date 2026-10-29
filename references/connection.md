# Connection: Elementor MCP + WordPress REST

## Contents
1. Setting up access
2. Environment variables used by the scripts
3. Endpoints that matter
4. Saving through Elementor (MCP)
5. Preview links and CSS cache
6. When authentication suddenly fails

## 1. Setting up access

> Full setup and offboarding flow (enabling **Elementor → Elementor MCP**, the generated connection prompt, `claude mcp add`, revoking at the end): `references/setup.md`. The notes below are the short version.

The user creates an **application password** for an admin user (Users → Profile → Application Passwords). Basic auth header = `base64("<user>:<app password with spaces>")`.

Elementor MCP server (Elementor ≥ 3.30 / 4.x exposes `/wp-json/elementor/mcp/`). The user adds it to Claude Code — auto mode may block Claude from running this, so suggest the `!` prefix:

```
! claude mcp add --transport http <name> https://<site>/wp-json/elementor/mcp/ --header "Authorization: Basic <base64>"
```

Then `/mcp` to (re)connect. The header is stored in plain text in `~/.claude.json`; mention it once.

MCP tools you will use most: `elementor-list-posts`, `elementor-get-page-structure`, `elementor-update-page-settings` (the save trigger), `elementor-create-preview-link`. The atomic-widget tools (`build-composition`, `manage-elements`, `get-widget-schema`) target Elementor 4's new "e-" widgets; classic widgets (heading, text-editor, button, icon-list…) are edited through `_elementor_data` via REST.

## 2. Environment variables

```
export WP_URL="https://example.com"
export WP_USER="agency-user"
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
export CHROME_PATH="$HOME/.cache/ms-playwright/chromium-<ver>/chrome-linux64/chrome"   # optional
```

`scripts/wp.py` uses `curl` under the hood on purpose: ModSecurity on shared hosts rejected Python's default client (HTTP 406) while curl passed.

## 3. Endpoints that matter

| Purpose | Endpoint |
|---|---|
| Pages / posts | `/wp/v2/pages/<id>?context=edit` (meta `_elementor_data`, `_elementor_page_settings`, `_wp_page_template`) |
| Templates | `/wp/v2/elementor_library?context=edit&status=any` (meta `_elementor_template_type`: header, footer, error-404, popup, section, page, kit) |
| Custom Code | `/wp/v2/elementor_snippet` (meta `_elementor_location`: `elementor_head` / `elementor_body_start` / `elementor_body_end`, `_elementor_priority`, `_elementor_code`) |
| Site settings | `/wp/v2/settings` (`page_on_front`, `show_on_front`, `site_logo`, `site_icon`) |
| Plugins | `/wp/v2/plugins` (status, version) |
| Media | `/wp/v2/media` (multipart upload: `-F file=@x.webp;type=image/webp -F alt_text=... -F title=...`) |
| Theme Builder import | `POST /elementor/v1/site-editor/templates` JSON `{"fileName": "x.json", "fileData": "<base64 of template JSON>"}` |
| Theme Builder conditions | `PUT /elementor/v1/site-editor/templates-conditions/<id>` `{"conditions":[{"type":"include","name":"general","sub_name":"","sub_id":""}]}` (404 page: `name:"singular", sub_name:"not_found404"`) |
| Rank Math meta | `POST /rankmath/v1/updateMeta` `{"objectType":"post","objectID":<id>,"meta":{...}}` |
| Rank Math schema | `POST /rankmath/v1/updateSchemas` |

Active Kit: read the body class `elementor-kit-<id>` from the live HTML (the option itself is not exposed over REST).

Do not call `/elementor/v1/site-editor/templates-conditions-conflicts` with guessed parameters — it returned a fatal-error page once (site unaffected, but noisy).

## 4. Saving through Elementor (MCP)

REST writes to `_elementor_data` do **not** regenerate the post CSS file, element cache or `post_content`. After every REST write, call:

```
elementor-update-page-settings  post_id=<id>  settings={}
```

- **Popups:** this call replaces the document settings. Send the **full** popup settings object every time (width, position, entrance animation, overlay, close button, prevent scroll, a11y navigation…). Read them from your backup first.
- **Kit:** same caution — send the full Kit settings object you built.
- Pages/headers/footers/404 templates: `{}` is safe.

The MCP response includes a preview URL with instructions to show it to the user. Include those links in your report (they only work for logged-in editors).

## 5. Preview links and CSS cache

- `elementor-create-preview-link` gives a tokenized preview of drafts for headless screenshots.
- After a save, `wp-content/uploads/elementor/css/post-<id>.css` can 404 or be stale for 1–3 minutes. Poll it (or wait ~30–60 s) before screenshots, or the page looks unstyled.
- Bust page caches with `?v=<anything>`.
- Elementor lazy-loads background images and some images: scroll the whole page before screenshots.

## 6. When authentication suddenly fails

Symptom: REST returns `rest_not_logged_in` / 401 and MCP says the Authorization header was rejected, while the site itself is up.

Usual causes, in order:
1. **Wordfence Login Security** — "Disable WordPress application passwords" or 2FA enforcement on the user. Fix the setting rather than disabling 2FA; or create a dedicated integration user used only through the application password.
2. The application password was revoked or rotated → create a new one and re-add the MCP server, then `/mcp`.
3. A security/hosting layer stripping the `Authorization` header (rare on Apache with the WP default `.htaccess`).

After fixing, test with `GET /wp/v2/users/me?context=edit` before resuming.
