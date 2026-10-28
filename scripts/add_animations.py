#!/usr/bin/env python3
"""Entrance animations (Elementor Motion Effects) for a page or template.

Rules:
- Fade variations, "fast" duration, short cascading delays (0-300 ms).
- First section: never animates the H1, the paragraph right after it, or images (protects LCP).
- Grids (wrapping rows): each card animates as a block, staggered by column.
- Side-by-side columns: the second column starts 100 ms after the first.
- Short widgets use fadeInUp; images, HTML, boxed containers and long text use fadeIn.
Idempotent: clears previous animation keys first.

Usage: add_animations.py <doc.json> <out.json>
  doc.json: REST object or bare element list. out.json: bare element list (for wp.py put-data).
"""
import json, re, sys

src = json.load(open(sys.argv[1]))
data = json.loads(src['meta']['_elementor_data']) if isinstance(src, dict) else src
STEP, MAX = 80, 240
stats = {}

def is_widget(e): return e['elType'] == 'widget'

def has_box(s):
    return bool(s.get('background_background') or s.get('border_border') or
                (s.get('__globals__') or {}).get('background_color'))

def kind(e):
    s = e['settings']
    if is_widget(e):
        w = e['widgetType']
        if w in ('image', 'html', 'video', 'google_maps'): return 'fadeIn'
        if w == 'text-editor' and len(re.sub('<[^>]+>', '', s.get('editor', ''))) > 280: return 'fadeIn'
        return 'fadeInUp'
    return 'fadeIn' if has_box(s) else 'fadeInUp'

def animate(e, delay, anim=None):
    anim = anim or kind(e)
    s = e['settings']
    if is_widget(e):
        s['_animation'] = anim; s['_animation_delay'] = delay
    else:
        s['animation'] = anim; s['animation_delay'] = delay
    s['animation_duration'] = 'fast'
    stats[anim] = stats.get(anim, 0) + 1

def is_grid(e):
    s = e['settings']
    return not is_widget(e) and s.get('flex_wrap') == 'wrap' and len(e.get('elements', [])) > 1

def is_split(e):
    s = e['settings']
    return (not is_widget(e) and s.get('flex_direction') == 'row' and s.get('flex_wrap') != 'wrap'
            and len(e.get('elements', [])) > 1 and all(not is_widget(c) for c in e['elements']))

def contains(e, ids):
    return any(c['id'] in ids or contains(c, ids) for c in e.get('elements', []))

def process(e, base, skip):
    kids = e.get('elements', [])
    if is_grid(e):
        n = len(kids); cols = n if n <= 4 else 3
        for i, c in enumerate(kids):
            if c['id'] in skip: continue
            if contains(c, skip): process(c, base, skip); continue
            animate(c, min(base + (i % cols) * 100, 300))
        return
    if is_split(e):
        for j, c in enumerate(kids):
            process(c, min(base + j * 100, 200), skip)
        return
    i = 0
    for c in kids:
        if c['id'] in skip: continue
        d = min(base + i * STEP, MAX)
        if is_widget(c) or (has_box(c) and not contains(c, skip)):
            animate(c, d)
        else:
            process(c, d, skip)
        i += 1

def hero_skip(sec):
    """IDs never animated in the first section: H1, the text right after it, and images."""
    skip = set()
    def walk(e):
        kids = e.get('elements', [])
        for i, c in enumerate(kids):
            if c.get('widgetType') == 'heading' and c['settings'].get('header_size') == 'h1':
                skip.add(c['id'])
                if i + 1 < len(kids) and kids[i + 1].get('widgetType') == 'text-editor':
                    skip.add(kids[i + 1]['id'])
            if c.get('widgetType') in ('image', 'html'):
                skip.add(c['id'])
            walk(c)
    walk(sec)
    return skip

def clear(e):
    for k in ('_animation', '_animation_delay', 'animation', 'animation_delay', 'animation_duration'):
        e['settings'].pop(k, None)
    for c in e.get('elements', []): clear(c)

for e in data: clear(e)  # idempotent
root = data[0] if len(data) == 1 and data[0]['settings'].get('html_tag') == 'main' else None
sections = root['elements'] if root else data
for n, sec in enumerate(sections):
    process(sec, 0, hero_skip(sec) if n == 0 else set())

json.dump(data, open(sys.argv[2], 'w'), ensure_ascii=False)
print(sys.argv[1], 'sections:', len(sections), stats)
