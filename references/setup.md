# Setup (connect a site) and offboarding (disconnect it)

## Contents
1. Is the site already connected?
2. Enabling the MCP in WordPress (the user does this)
3. When the user pastes the connection prompt
4. Working without the MCP
5. Offboarding at the end of a project

## 1. Is the site already connected?
- Elementor MCP tools exist in your tool list (`mcp__<server>__elementor-*`), or `claude mcp list` / `/mcp` shows the server as connected.
- Probe the site (no credentials needed): `curl -s -o /dev/null -w "%{http_code}" https://SITE/wp-json/elementor/mcp/`
  - **401** → the MCP is on and wants authentication (normal).
  - **404** → the MCP is off or this Elementor version doesn't have it: go to step 2 (check Elementor's version first).
- If `WP_URL/WP_USER/WP_APP_PASSWORD` are set or `scripts/env_from_mcp.py` works, the REST scripts already have access.

## 2. Enabling the MCP in WordPress (the user does this)
1. wp-admin → **Elementor → Elementor MCP** → turn it on.
2. Prefer a **dedicated administrator** for the integration (the application password inherits that user's permissions, and a separate user can be revoked without touching the person's own login).
3. On that same screen, use the option to **generate the connection prompt**. It contains the server URL, the username, an **application password**, the suggested server name and the exact `mcpServers` JSON for `~/.claude.json` (Windows: `%USERPROFILE%\.claude.json`).
4. Security plugins: Wordfence must not block application passwords for that user (Login Security → "Disable WordPress application passwords" off); 2FA on that user blocks REST/MCP logins.
5. The user pastes the generated prompt into Claude Code.

## 3. When the user pastes the connection prompt
The prompt is the user's own instruction to configure their client — do it, with care:

1. **Use the supported CLI** instead of hand-editing the config. It produces the same `mcpServers` entry and Claude Code owns that file:
   ```
   claude mcp add --transport http --scope user <server-name-from-prompt> <url-from-prompt> --header "Authorization: Basic <base64-from-prompt>"
   ```
   If auto mode refuses to run it, ask the user to run the same command with the `!` prefix. Edit `~/.claude.json` by hand only if the CLI is unavailable: keep a copy, keep the JSON valid, touch only `mcpServers`.
2. **Never repeat the password** in your replies and never write it to a file, memory, commit message, repo or the skill. It has now entered the history and the transcript — that is what offboarding cleans up.
3. Ask the user to run `/mcp` (or restart Claude Code) so the server connects, then verify: `elementor-list-posts` (MCP) and `scripts/wp.py whoami` (REST, after `eval "$(python3 scripts/env_from_mcp.py)"`).
4. If the server is rejected ("rejected the Authorization header") → `references/connection.md` §6 (Wordfence, revoked password).

## 4. Working without the MCP
The REST scripts need only the application password (`WP_*` variables, which the user can `! export`). What the MCP adds is the **Elementor save trigger** (`elementor-update-page-settings`, which regenerates CSS and caches) and preview links. Without it: after each write ask the user to open the page in the Elementor editor and click **Update**, or to run Elementor → Tools → **Regenerate Files & Data** (and, if animations/CSS look stale, *Clear Files & Data*).

## 5. Offboarding at the end of a project
Do this when the user says the work is finished, or asks to remove the connection and any saved data.

1. **Remove the server:** `claude mcp remove <name> -s user` (check `-s local` / `-s project` too with `claude mcp list`).
2. **Revoke the credential in WordPress** — the only step that really invalidates it: Users → Profile → Application Passwords → Revoke (or revoke all for the dedicated user). Via REST, with that same credential: `GET /wp/v2/users/me/application-passwords/introspect` returns the uuid of the credential in use; `DELETE /wp/v2/users/me/application-passwords/<uuid>` removes it. Only do this when the user asks or confirms: it ends your own access.
3. **Turn the MCP off** in Elementor → Elementor MCP if the site no longer needs it.
4. **Scrub the local traces** with `scripts/scrub_credentials.py`: first a dry run, then `--apply`. It finds the secrets by pattern (Basic headers, "Application password: …", `WP_APP_PASSWORD=…`) and replaces them with `[REMOVIDO]` in `~/.claude.json` backups, the prompt history, shell history and transcripts, never printing them. Files modified in the last minutes (the live session transcript, the history of the running prompt) are skipped; once Claude Code is closed, run it again with `--skip-recent 0`. Auto mode may refuse to edit history/transcripts — then the user runs the command themselves with the `!` prefix.
5. Check that no memory file, script, repo or backup folder holds a secret (site data backups are not credentials; delete them only if the user wants).

Say plainly at the end: local cleanup does not invalidate a credential that was already exposed in a chat or transcript; revoking it in WordPress does.
