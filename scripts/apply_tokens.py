#!/usr/bin/env python3
"""Bind per-widget typography and colors to the Elementor Kit's global tokens.

A typography group set to "custom" whose values exactly match a Kit typography token becomes
`__globals__[<prefix>typography_typography] = globals/typography?id=<token>`; hex colors equal to a
Kit color become global color references. Anything without a match stays local and is reported.

Usage:
  apply_tokens.py --kit kit.json --scan doc1.json [doc2.json ...]     # list signatures/colors in use
  apply_tokens.py --kit kit.json doc.json out.json                    # write the token-bound version

kit.json: the Kit post from `wp.py get elementor_library <kitId>` (or just its _elementor_page_settings).
doc.json: a document from `wp.py get` / `wp.py data` (REST object or the bare element list).
Output is the bare element list (feed it to `wp.py put-data`).
"""
import json, sys, collections, argparse

GROUP_KEYS = ['typography_typography', 'typography_font_family', 'typography_font_weight', 'typography_font_style',
              'typography_text_decoration', 'typography_text_transform']
for base in ('font_size', 'line_height', 'letter_spacing', 'word_spacing'):
    GROUP_KEYS += [f'typography_{base}{sfx}' for sfx in ('', '_tablet', '_mobile')]


def size(v): return v.get('size') if isinstance(v, dict) else None
def num(n):
    try: return float(n)
    except (TypeError, ValueError): return n


def sig_from(get):
    return (get('typography_font_family'), str(get('typography_font_weight') or ''), num(size(get('typography_font_size'))),
            num(size(get('typography_font_size_tablet'))), num(size(get('typography_font_size_mobile'))),
            num(size(get('typography_line_height'))), get('typography_text_transform') or '',
            num(size(get('typography_letter_spacing'))))


def load_kit(path):
    k = json.load(open(path))
    if 'meta' in k: k = k['meta']['_elementor_page_settings']
    tokens = {}
    for t in k.get('system_typography', []) + k.get('custom_typography', []):
        if t.get('typography_typography') == 'custom':
            tokens[sig_from(lambda key, t=t: t.get(key))] = t['_id']
    colors = {}
    for c in k.get('system_colors', []) + k.get('custom_colors', []):
        colors.setdefault(c['color'].upper(), c['_id'])
    return tokens, colors


def load_doc(path):
    d = json.load(open(path))
    if isinstance(d, dict): d = json.loads(d['meta']['_elementor_data'])
    return d


def groups(s):
    for k, v in list(s.items()):
        if k.endswith('typography_typography') and v == 'custom':
            yield k[:-len('typography_typography')]


def walk_all(data, fn):
    def w(e):
        fn(e)
        for c in e.get('elements', []): w(c)
    for e in data: w(e)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--kit', required=True); p.add_argument('--scan', action='store_true'); p.add_argument('files', nargs='+')
    a = p.parse_args()
    tokens, colors = load_kit(a.kit)

    if a.scan:
        sigs, hexes = collections.Counter(), collections.Counter()
        for f in a.files:
            def scan(e):
                s = e['settings']
                for pfx in groups(s): sigs[(sig_from(lambda k: s.get(pfx + k)), e.get('widgetType'))] += 1
                for k, v in s.items():
                    if 'color' in k and isinstance(v, str) and v.startswith('#'): hexes[v.upper()] += 1
            walk_all(load_doc(f), scan)
        print('TYPOGRAPHY SIGNATURES (count, signature, widget, token):')
        for (sg, w), n in sigs.most_common(): print(f'  {n:3} {sg} {w} -> {tokens.get(sg, "-")}')
        print('HEX COLORS (count, value, token):')
        for h, n in hexes.most_common(): print(f'  {n:3} {h} -> {colors.get(h, "-")}')
        return

    src, out = a.files
    data = load_doc(src); stats = collections.Counter(); left = collections.Counter()

    def bind(e):
        s = e['settings']; gl = s.get('__globals__') or {}
        for pfx in list(groups(s)):
            tok = tokens.get(sig_from(lambda k: s.get(pfx + k)))
            if tok:
                for gk in GROUP_KEYS: s.pop(pfx + gk, None)
                gl[pfx + 'typography_typography'] = f'globals/typography?id={tok}'; stats['typography'] += 1
            else:
                left[f"{e.get('widgetType')}:{pfx or '-'} {sig_from(lambda k: s.get(pfx + k))[:5]}"] += 1
        for k, v in list(s.items()):
            if 'color' in k and isinstance(v, str) and v.upper() in colors and not gl.get(k):
                gl[k] = f'globals/colors?id={colors[v.upper()]}'; s.pop(k); stats['color'] += 1
        if gl: s['__globals__'] = gl
    walk_all(data, bind)
    json.dump(data, open(out, 'w'), ensure_ascii=False)
    print(src, dict(stats))
    if left: print('  left local (no matching token):', dict(left))


if __name__ == '__main__':
    main()
