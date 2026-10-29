# Recipes for common edit requests

Each recipe is end-to-end: do all the steps, verify on the live site, then report. Credentials: `scripts/env_from_mcp.py` (see SKILL.md → Never stop at access).

## Change a phone / WhatsApp number "everywhere"

Typical request: "the WhatsApp number for rentals is now X — change it across the site, the footer, and check the chat bot".

1. **Clarify only what is ambiguous, and decide the rest.** Several numbers can coexist (rental vs. franchise vs. support). Change only the intent the user named; leave the others and say so. Links are told apart by their pre-filled message (`wa.me/<n>?text=...`).
2. **Find every place** (dry run): `swap_contact.py plan --old <digits> --old-text "<as written>" --keep-if-message <other intent word> pages:<id> ... elementor_library:<id> ...` over all pages, the header, footer, mobile-menu popup and 404 template; `elementor_snippet:<id>` lists the lines of Custom Code. Also grep the rendered HTML of 4–5 URLs (including a 404) for the number in all its spellings (`5567…`, `+55 67 …`, `(67) 9 …-…`).
3. **Back up, then apply**: `swap_contact.py apply --old … --new … --old-text … --new-text … --keep-if-message … --backup bk <docs>`. The number as visible text (footer, privacy policy contact line) changes with the links; text baked into images cannot be changed — report it.
4. **Chat/bot widgets in Custom Code**: they keep numbers as constants per intent (`numeroLocacao`, `numeroFranquia`). Edit only the intended constant (`wp.py` GET the snippet, replace the single line, POST `meta._elementor_code`); 4-byte emoji must stay escaped. A bot on an external platform (n8n, Meta API, Chatwoot) is outside the site — ask where it runs only if the site really doesn't hold the logic.
5. **Save through Elementor** (MCP `elementor-update-page-settings`; popups with their full settings) and **regenerate `post_content`** (`plain_content.py <url> out.html --write <id>`).
6. **Structured data**: Rank Math `telephone` lives in the page schema. `POST /rankmath/v1/updateMeta` with a harmless meta (`{"rank_math_rich_snippet":"custom"}`) returns the page's schemas with their ids; change the number and resend them with the same ids to `updateSchemas`. Schemas that belong to another intent (franchise page) stay.
7. **Verify live**: no link of the changed intent still points to the old number; the other intent's links are intact; the visible text is new; schema `telephone` updated; footer screenshot. For a chat widget, run its flow in headless Chromium with the lead submission stubbed (override `fetch` for the form endpoint and hold any redirect timer) so no real lead is created, and read the final `wa.me` URL for each option.
8. Report: counts per page, what was intentionally left (other intents, the number inside an image), what was verified.

## Update contact data other than a number
Same shape: dry-run search over documents + rendered pages + Custom Code + schema, back up, apply with a script, save via Elementor, regenerate `post_content`, verify.
