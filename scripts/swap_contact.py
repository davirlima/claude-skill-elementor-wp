#!/usr/bin/env python3
"""Change a phone / WhatsApp number across Elementor documents, optionally only for one contact intent.

Handles wa.me links, the number written as text (icon lists, text editors) and keeps links whose pre-filled
message matches --keep-if-message (e.g. leave "franchise" WhatsApp links on the old number).

Usage:
  swap_contact.py plan  --old 5511999990000 --old-text "9 9999-0000" <type>:<id> ...      # count only, no writes
  swap_contact.py apply --old 5511999990000 --new 5511988880000 \\
                        --old-text "9 9999-0000" --new-text "9 8888-0000" \\
                        --keep-if-message franquia --backup bk <type>:<id> ...

<type> is pages | elementor_library | elementor_snippet (Custom Code is only listed, never rewritten: see below).
After `apply`: save each document through Elementor (MCP elementor-update-page-settings; popups with their FULL
settings), regenerate post_content (plain_content.py --write), update schema.org `telephone` in Rank Math
(updateMeta returns the page schemas with their ids; resend them to updateSchemas) and check the rendered pages.
Also check places no document owns: the rendered footer/header, popups, a 404 URL, and chat/bot widgets.
Needs WP_URL / WP_USER / WP_APP_PASSWORD (see env_from_mcp.py).
"""
import argparse, json, os, re, sys
from urllib.parse import unquote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wp


def make_fixer(a, st):
    def link(m):
        if a.keep_if_message and a.keep_if_message.lower() in unquote(m.group(2)).lower():
            st['kept'] += 1; return m.group(0)
        st['links'] += 1; return m.group(1) + (a.new or '<new>') + m.group(2)
    def fix(s):
        s = re.sub(r'(wa\.me/)' + re.escape(a.old) + r'(\?text=[^"\s<>\\]*|(?=["\s<>\\]))', link, s)
        if a.old_text and a.old_text in s:
            st['text'] += s.count(a.old_text); s = s.replace(a.old_text, a.new_text or '<new>')
        return s
    return fix


def walk(o, fix):
    if isinstance(o, dict):
        for k, v in o.items(): o[k] = fix(v) if isinstance(v, str) else (walk(v, fix) or v)
    elif isinstance(o, list):
        for i, v in enumerate(o): o[i] = fix(v) if isinstance(v, str) else (walk(v, fix) or v)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('mode', choices=['plan', 'apply']); p.add_argument('--old', required=True); p.add_argument('--new')
    p.add_argument('--old-text'); p.add_argument('--new-text'); p.add_argument('--keep-if-message')
    p.add_argument('--backup', default='backup'); p.add_argument('items', nargs='+')
    a = p.parse_args()
    if a.mode == 'apply' and not (a.new and (a.new_text or not a.old_text)): sys.exit('apply needs --new (and --new-text with --old-text)')
    os.makedirs(a.backup, exist_ok=True)
    for it in a.items:
        t, i = it.split(':'); doc = wp.get(t, i)
        if 'meta' not in doc: print(it, 'error', doc); continue
        st = {'links': 0, 'kept': 0, 'text': 0}; fix = make_fixer(a, st)
        if t == 'elementor_snippet':
            # Custom Code (chatbots, widgets) often keeps several numbers as constants (rent, franchise, support):
            # a blind replace would change them all, so only show the lines and edit the right one deliberately.
            code = doc['meta'].get('_elementor_code', '')
            lines = [f'  line {n + 1}: {l.strip()[:110]}' for n, l in enumerate(code.splitlines())
                     if a.old in l or (a.old_text and a.old_text in l)]
            print(it, f'{len(lines)} line(s) with the number — edit the intended constant only:'); print('\n'.join(lines))
            continue
        data = json.loads(doc['meta'].get('_elementor_data') or '[]'); walk(data, fix)
        print(it, st)
        if a.mode == 'apply' and (st['links'] or st['text']):
            json.dump(doc, open(f'{a.backup}/{t}-{i}.json', 'w'), ensure_ascii=False)
            wp.put_data(t, i, data)
    if a.mode == 'apply': print('now save each document through Elementor (MCP), regenerate post_content, fix schema, verify live')


if __name__ == '__main__':
    main()
