#!/usr/bin/env python3
"""Find media that nothing on the site uses, back it up, and (optionally) delete it.

A file counts as used when its base name or ID appears in: the rendered HTML of the given public URLs
(always include a 404 URL so the 404 template is rendered), the Elementor data/settings of published
pages and templates (incl. popups and the active Kit), Custom Code snippets, featured images, the site
logo/icon and — with --store — WooCommerce product, gallery, variation and category images.
Also render a few product, category, cart and checkout URLs on stores. Images used outside the site
(e-mail marketing, ads, product feeds) can't be detected: ask the user before deleting.
`--keep` adds IDs that must survive anyway (brand source files, OG image).

Usage:
  media_usage.py report --urls https://site/ https://site/about/ https://site/xyz-404/ [--keep 119 770] [--store]
  media_usage.py backup <dir>            # downloads every unused file + manifest.json (from the last report)
  media_usage.py delete <dir> --yes      # permanently deletes files whose backup in <dir> succeeded

Needs WP_URL, WP_USER, WP_APP_PASSWORD. Writes media_usage.json in the current directory.
"""
import json, os, re, subprocess, sys, argparse, base64

STATE = 'media_usage.json'


def auth():
    tok = base64.b64encode(f"{os.environ['WP_USER']}:{os.environ['WP_APP_PASSWORD']}".encode()).decode()
    return ['-H', f'Authorization: Basic {tok}']


def rest(path, method='GET'):
    base = os.environ['WP_URL'].rstrip('/') + '/wp-json/wp/v2'
    out = subprocess.run(['curl', '-s', '-X', method] + auth() + [base + path], capture_output=True, text=True).stdout
    return json.loads(out)


def all_items(t, fields, status='publish'):
    rows, page = [], 1
    while True:
        st = f'&status={status}' if status else ''
        r = rest(f'/{t}?context=edit&per_page=100&page={page}{st}&_fields={fields}')
        if not isinstance(r, list) or not r: return rows
        rows += r; page += 1


def store_images():
    """IDs used by WooCommerce (product image + gallery, variation images, category thumbnails). Empty if no Woo."""
    ids, base = set(), os.environ['WP_URL'].rstrip('/') + '/wp-json/wc/v3'
    def wc(path):
        out = subprocess.run(['curl', '-s'] + auth() + [base + path], capture_output=True, text=True).stdout
        try: return json.loads(out)
        except json.JSONDecodeError: return None
    for kind in ('products', 'products/categories'):
        page = 1
        while True:
            r = wc(f'/{kind}?per_page=100&page={page}')
            if not isinstance(r, list) or not r: break
            for it in r:
                imgs = it.get('images') or ([it['image']] if it.get('image') else [])
                ids |= {i['id'] for i in imgs if i}
                for vid in it.get('variations') or []:
                    v = wc(f"/products/{it['id']}/variations/{vid}")
                    if isinstance(v, dict) and v.get('image'): ids.add(v['image']['id'])
            page += 1
    return ids


def report(a):
    media = all_items('media', 'id,source_url,mime_type,media_details,post', status=None)
    blob, featured = '', set()
    types = ['pages', 'posts', 'elementor_library', 'elementor_snippet'] + (['product'] if a.store else [])
    for t in types:
        for it in all_items(t, 'id,meta,featured_media'):
            blob += json.dumps(it.get('meta', {}), ensure_ascii=False)
            if it.get('featured_media'): featured.add(it['featured_media'])
    for u in a.urls:
        blob += subprocess.run(['curl', '-s', u], capture_output=True, text=True).stdout
    blob = blob.replace('\\/', '/')
    settings = rest('/settings?_fields=site_logo,site_icon')
    keep = set(a.keep or []) | {settings.get('site_logo'), settings.get('site_icon')} | featured
    if a.store:
        woo = store_images(); keep |= woo
        print(f'WooCommerce images protected: {len(woo)}')
    used, unused = [], []
    for m in media:
        rel = m['source_url'].split('/uploads/')[-1]
        base = re.sub(r'\.\w+$', '', rel)
        by_id = re.search(r'"id"\s*:\s*"?%d"?[,}]' % m['id'], blob)
        size = (m.get('media_details') or {}).get('filesize') or 0
        row = {'id': m['id'], 'file': rel, 'url': m['source_url'], 'bytes': size}
        (used if (base in blob or by_id or m['id'] in keep) else unused).append(row)
    json.dump({'used': used, 'unused': unused}, open(STATE, 'w'), indent=1)
    print(f'used: {len(used)}  unused: {len(unused)}  ({sum(r["bytes"] for r in unused) / 1048576:.1f} MB)')
    for r in unused: print(f'  {r["id"]:>5} {r["file"]}  {r["bytes"] // 1024} KB')
    print('post_content is ignored on purpose (it can reference media that pages no longer render).')


def backup(a):
    st = json.load(open(STATE)); os.makedirs(a.dir, exist_ok=True); man = []
    for r in st['unused']:
        p = os.path.join(a.dir, r['file']); os.makedirs(os.path.dirname(p), exist_ok=True)
        ok = subprocess.run(['curl', '-s', '-f', '-o', p, r['url']]).returncode == 0 and os.path.getsize(p) > 0
        man.append({**r, 'backup_ok': ok})
    json.dump(man, open(os.path.join(a.dir, 'manifest.json'), 'w'), indent=1)
    print(f'backed up {sum(m["backup_ok"] for m in man)}/{len(man)} -> {a.dir}')


def delete(a):
    if not a.yes: sys.exit('refusing to delete without --yes (deletion is permanent)')
    man = json.load(open(os.path.join(a.dir, 'manifest.json')))
    done = 0
    for m in man:
        if not m['backup_ok']: print('skip (no backup):', m['id']); continue
        for _ in range(2):
            try:
                if rest(f"/media/{m['id']}?force=true", 'DELETE').get('deleted'): done += 1; break
            except json.JSONDecodeError: pass
        else: print('failed:', m['id'])
    print(f'deleted {done}/{len(man)}')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('report'); s.add_argument('--urls', nargs='+', required=True); s.add_argument('--keep', nargs='*', type=int)
    s.add_argument('--store', action='store_true', help='WooCommerce site: protect product, gallery, variation and category images')
    s = sp.add_parser('backup'); s.add_argument('dir')
    s = sp.add_parser('delete'); s.add_argument('dir'); s.add_argument('--yes', action='store_true')
    a = p.parse_args()
    {'report': report, 'backup': backup, 'delete': delete}[a.cmd](a)


if __name__ == '__main__':
    main()
