#!/usr/bin/env python3
"""Small WordPress/Elementor REST client (uses curl: survives ModSecurity rules that block Python clients).

Connection from env: WP_URL, WP_USER, WP_APP_PASSWORD.

Usage:
  wp.py whoami
  wp.py list <type> [--status any]                 # pages | posts | elementor_library | elementor_snippet | media
  wp.py get <type> <id> [-o file.json]             # full object with context=edit
  wp.py backup <dir> <type>:<id> [<type>:<id> ...] # saves <dir>/<type>-<id>.json
  wp.py data <type> <id> -o data.json              # just the parsed _elementor_data list
  wp.py put-data <type> <id> data.json             # writes a list (or {"meta":{"_elementor_data":"..."}}) back
  wp.py upload <file> --title T --alt A            # multipart media upload, prints id + url
  wp.py rankmath <id> meta.json                    # POST /rankmath/v1/updateMeta
  wp.py swap-media map.json in.json out.json       # map: [{"old":id,"oldurl":"2026/08/a.png","id":new,"url":"https://..","alt":".."}]

After put-data, trigger an Elementor save with the MCP tool elementor-update-page-settings (see SKILL.md).
"""
import base64, json, os, subprocess, sys, argparse


def env(k):
    v = os.environ.get(k)
    if not v: sys.exit(f"missing env var {k}")
    return v


def auth():
    tok = base64.b64encode(f"{env('WP_USER')}:{env('WP_APP_PASSWORD')}".encode()).decode()
    return f"Authorization: Basic {tok}"


def api(path):
    base = env('WP_URL').rstrip('/')
    return path if path.startswith('http') else f"{base}/wp-json{path}"


def curl(method, path, body=None, extra=None):
    cmd = ['curl', '-s', '-X', method, '-H', auth()]
    if body is not None:
        cmd += ['-H', 'Content-Type: application/json', '--data-binary', '@-']
    cmd += (extra or []) + [api(path)]
    out = subprocess.run(cmd, input=None if body is None else json.dumps(body, ensure_ascii=False),
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        sys.exit(f"non-JSON response from {path}: {out[:300]}")


def get(t, i): return curl('GET', f"/wp/v2/{t}/{i}?context=edit")


def elementor_data(t, i):
    d = get(t, i)
    if 'meta' not in d: sys.exit(f"error: {d}")
    return json.loads(d['meta'].get('_elementor_data') or '[]')


def put_data(t, i, data):
    if isinstance(data, dict) and 'meta' in data: body = data
    else: body = {'meta': {'_elementor_data': json.dumps(data, ensure_ascii=False)}}
    r = curl('POST', f"/wp/v2/{t}/{i}", body)
    if 'id' not in r: sys.exit(f"error: {r}")
    return r


def swap_media(mapping, data):
    """Replace media by id (image/background objects) and by URL (any string, e.g. HTML widgets)."""
    by_id = {int(m['old']): m for m in mapping}
    stats = {'by_id': 0, 'by_url': 0}
    base = env('WP_URL').rstrip('/') + '/wp-content/uploads/'

    def walk(o):
        if isinstance(o, dict):
            if 'id' in o and 'url' in o and str(o['id']).isdigit() and int(o['id']) in by_id:
                m = by_id[int(o['id'])]; o['id'] = m['id']; o['url'] = m['url']; stats['by_id'] += 1
                if 'alt' in o and m.get('alt'): o['alt'] = m['alt']
            for k, v in o.items():
                if isinstance(v, str):
                    for m in mapping:
                        old = base + m['oldurl']
                        if old in v: v = v.replace(old, m['url']); stats['by_url'] += 1
                    o[k] = v
                else: walk(v)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(data)
    return stats


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest='cmd', required=True)
    sp.add_parser('whoami')
    s = sp.add_parser('list'); s.add_argument('type'); s.add_argument('--status', default='any')
    s = sp.add_parser('get'); s.add_argument('type'); s.add_argument('id'); s.add_argument('-o')
    s = sp.add_parser('backup'); s.add_argument('dir'); s.add_argument('items', nargs='+')
    s = sp.add_parser('data'); s.add_argument('type'); s.add_argument('id'); s.add_argument('-o', required=True)
    s = sp.add_parser('put-data'); s.add_argument('type'); s.add_argument('id'); s.add_argument('file')
    s = sp.add_parser('upload'); s.add_argument('file'); s.add_argument('--title', default=''); s.add_argument('--alt', default='')
    s = sp.add_parser('rankmath'); s.add_argument('id'); s.add_argument('file')
    s = sp.add_parser('swap-media'); s.add_argument('map'); s.add_argument('infile'); s.add_argument('outfile')
    a = p.parse_args()

    if a.cmd == 'whoami':
        print(curl('GET', '/wp/v2/users/me?context=edit&_fields=id,name,roles'))
    elif a.cmd == 'list':
        fields = 'id,title,status,slug,modified,meta' if a.type != 'media' else 'id,source_url,mime_type,alt_text'
        page, rows = 1, []
        while True:
            st = '' if a.type == 'media' else f'&status={a.status}'
            r = curl('GET', f"/wp/v2/{a.type}?context=edit&per_page=100&page={page}{st}&_fields={fields}")
            if not isinstance(r, list) or not r: break
            rows += r; page += 1
        for x in rows:
            if a.type == 'media':
                print(x['id'], x['mime_type'], x['source_url'].split('/uploads/')[-1], '|', x.get('alt_text', ''))
            else:
                m = x.get('meta') or {}
                kind = m.get('_elementor_template_type') or m.get('_elementor_location') or ''
                print(x['id'], x['status'], kind, x['slug'], '|', x['title']['raw'])
    elif a.cmd == 'get':
        d = get(a.type, a.id); s = json.dumps(d, ensure_ascii=False, indent=1)
        open(a.o, 'w').write(s) if a.o else print(s)
    elif a.cmd == 'backup':
        os.makedirs(a.dir, exist_ok=True)
        for it in a.items:
            t, i = it.split(':')
            json.dump(get(t, i), open(f"{a.dir}/{t}-{i}.json", 'w'), ensure_ascii=False)
            print('saved', f"{a.dir}/{t}-{i}.json")
    elif a.cmd == 'data':
        json.dump(elementor_data(a.type, a.id), open(a.o, 'w'), ensure_ascii=False, indent=1); print('ok', a.o)
    elif a.cmd == 'put-data':
        r = put_data(a.type, a.id, json.load(open(a.file)))
        print('saved', r['id'], '— now call elementor-update-page-settings (full settings for popups/kit)')
    elif a.cmd == 'upload':
        r = curl('POST', '/wp/v2/media', extra=['-F', f"file=@{a.file}", '-F', f"title={a.title}", '-F', f"alt_text={a.alt}"])
        print(r.get('id'), r.get('source_url'), list((r.get('media_details') or {}).get('sizes', {}).keys()))
    elif a.cmd == 'rankmath':
        meta = json.load(open(a.file))
        print(curl('POST', '/rankmath/v1/updateMeta', {'objectType': 'post', 'objectID': int(a.id), 'meta': meta}))
    elif a.cmd == 'swap-media':
        src = json.load(open(a.infile))
        data = json.loads(src['meta']['_elementor_data']) if isinstance(src, dict) else src
        st = swap_media(json.load(open(a.map)), data)
        json.dump(data, open(a.outfile, 'w'), ensure_ascii=False); print(st)


if __name__ == '__main__':
    main()
