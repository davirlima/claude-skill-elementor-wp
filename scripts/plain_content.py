#!/usr/bin/env python3
"""Rebuild a page's post_content from its rendered <main> (what SEO plugins like Rank Math analyze).

Elementor only writes post_content when a page is saved in the editor; pages built through the
REST API keep it empty, so Rank Math reports 0 words, no images, no links.

Usage:
  plain_content.py <page-url> <out.html>                 # extract and save
  plain_content.py <page-url> <out.html> --write <id>    # also write it to the page (needs WP_* env)

Keeps h1-h6, p, ul/ol/li, a (href/target/rel), img (src/alt/width/height), strong/em/br.
Requires the page content to be inside <main> (see accessibility: root container html_tag=main).
"""
import sys, re, json, subprocess, base64, os
from html.parser import HTMLParser
from html import escape

KEEP = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'a', 'img', 'strong', 'em', 'br'}
ATTRS = {'a': ('href', 'target', 'rel'), 'img': ('src', 'alt', 'width', 'height')}
SKIP = {'script', 'style', 'svg', 'noscript', 'template'}


class Extract(HTMLParser):
    def __init__(s): super().__init__(); s.out = []; s.main = 0; s.skip = 0

    def handle_starttag(s, t, a):
        a = dict(a)
        if t == 'main': s.main += 1; return
        if not s.main: return
        if t in SKIP: s.skip += 1; return
        if s.skip or t not in KEEP: return
        attrs = ''.join(f' {k}="{escape(a[k] or "")}"' for k in ATTRS.get(t, ()) if a.get(k) is not None)
        s.out.append(f'<{t}{attrs} />' if t in ('img', 'br') else f'<{t}{attrs}>')

    def handle_endtag(s, t):
        if t == 'main': s.main -= 1; return
        if not s.main: return
        if t in SKIP: s.skip -= 1; return
        if s.skip or t not in KEEP or t in ('img', 'br'): return
        s.out.append(f'</{t}>')

    def handle_data(s, d):
        if s.main and not s.skip and d.strip(): s.out.append(escape(re.sub(r'\s+', ' ', d)))


def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    url, out = sys.argv[1], sys.argv[2]
    html = subprocess.run(['curl', '-s', url], capture_output=True, text=True).stdout
    p = Extract(); p.feed(html)
    content = ''.join(p.out)
    content = re.sub(r'<(p|li|h\d|strong|em)>\s*</\1>', '', content)
    content = re.sub(r'(</(?:h\d|p|ul|ol|li)>)', r'\1\n', content)
    if not content.strip(): sys.exit('no <main> content found — wrap the page in a root container with html_tag=main')
    open(out, 'w').write(content)
    words = len(re.sub('<[^>]+>', ' ', content).split())
    print(f'{url}: {words} words, {content.count("<img")} images, {content.count("<a ")} links -> {out}')
    if '--write' in sys.argv:
        pid = sys.argv[sys.argv.index('--write') + 1]
        tok = base64.b64encode(f"{os.environ['WP_USER']}:{os.environ['WP_APP_PASSWORD']}".encode()).decode()
        r = subprocess.run(['curl', '-s', '-H', f'Authorization: Basic {tok}', '-H', 'Content-Type: application/json',
                            '--data-binary', '@-', f"{os.environ['WP_URL'].rstrip('/')}/wp-json/wp/v2/pages/{pid}"],
                           input=json.dumps({'content': content}), capture_output=True, text=True).stdout
        print('written:', json.loads(r).get('id'))


if __name__ == '__main__':
    main()
