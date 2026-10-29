#!/usr/bin/env python3
"""Print `export WP_URL=... WP_USER=... WP_APP_PASSWORD=...` from the Elementor MCP server the user already configured.

Why: the MCP server's Authorization header IS the credential the user handed over for this site, so there is
no reason to stop and ask them to export variables again. The scripts need REST access because the Elementor
MCP cannot read or edit classic (V3) widgets such as buttons, icon lists and social icons.

Usage (the password is never printed to the terminal):
    eval "$(python3 env_from_mcp.py [site-substring])"

With several Elementor MCP servers configured, pass part of the site's host to pick one.
Looks in ~/.claude.json (user + per-project entries) and ./.mcp.json.
"""
import base64, json, os, sys

NEEDLE = sys.argv[1] if len(sys.argv) > 1 else ''


def servers():
    for path in (os.path.expanduser('~/.claude.json'), os.path.join(os.getcwd(), '.mcp.json')):
        try: data = json.load(open(path))
        except (OSError, json.JSONDecodeError): continue
        stack = [data]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == 'mcpServers' and isinstance(v, dict):
                        for name, s in v.items():
                            if isinstance(s, dict): yield name, s
                    else: stack.append(v)
            elif isinstance(o, list): stack.extend(o)


for name, s in servers():
    url = s.get('url', '')
    if '/wp-json/elementor/mcp' not in url or NEEDLE not in url: continue
    auth = next((v for k, v in (s.get('headers') or {}).items() if k.lower() == 'authorization'), '')
    if not auth.lower().startswith('basic '): continue
    try: user, pwd = base64.b64decode(auth.split(None, 1)[1]).decode().split(':', 1)
    except Exception: continue
    site = url.split('/wp-json/')[0]
    q = lambda x: "'" + x.replace("'", "'\\''") + "'"
    print(f'export WP_URL={q(site)} WP_USER={q(user)} WP_APP_PASSWORD={q(pwd)}')
    sys.stderr.write(f'credentials taken from MCP server "{name}" ({site}), user {user}\n')
    sys.exit(0)

sys.stderr.write('no Elementor MCP server with a Basic Authorization header found — ask the user for WP_URL / WP_USER / '
                 'application password once (they can `! export` them), or follow references/setup.md to connect the site, then continue.\n')
sys.exit(1)
