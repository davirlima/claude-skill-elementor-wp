"""Component kit for Elementor pages built from Python (containers + official widgets).

Widgets reference the active Kit's global tokens, so pages follow the design system automatically.
Configure once per project, then build sections:

    import sys; sys.path.insert(0, "<skill>/scripts")
    from elementor_kit import *
    configure(site="https://client.com",
              typography={"h1": "primary", "h2": "secondary", "h3": "accent", "body": "text",
                          "h2s": "h2comp1", "label": "rotulo1", "stat": "numero1", "eyebrow": "sobret1",
                          "lead": "textod1", "small": "textop1", "badge": "selo001", "button": "botao01"},
              colors={"primary": "primary", "title": "secondary", "text": "text", "dark": "ddfb581",
                      "white": "4f381b8", "soft": "19c9bd2", "muted": "89fc10d", "border": "f5ac94f",
                      "on_dark": "d5fe309", "accent_text": "b45309a", "tint": "fff1e3a"})
    page = [hero_section([...]), section([section_head("Eyebrow", "Title", "Lead"), grid([...], d=3, t=2)])]
    check(page)  # one H1, official widgets only

The ids above are examples — read the real ones from the Kit (`custom_colors[]._id`, `custom_typography[]._id`).
Spacing tokens: boxed 1200 · section 96/24 (tablet 80/32, mobile 64/20) · gaps 8/12/16/24/32/48/64 · radius 12/20/32.
"""
import copy, json, secrets
from urllib.parse import quote

CFG = {"site": "", "typography": {}, "colors": {}, "boxed": 1200}


def configure(site, typography, colors, boxed=1200):
    CFG.update(site=site.rstrip('/'), typography=typography, colors=colors, boxed=boxed)


# ---------- values ----------
def nid(): return secrets.token_hex(4)[:7]
def px(n): return {"unit": "px", "size": n, "sizes": []}
def em(n): return {"unit": "em", "size": n, "sizes": []}
def pct(n): return {"unit": "%", "size": n, "sizes": []}
def cu(v): return {"unit": "custom", "size": v, "sizes": []}
FULL = pct(100)
def box(t, r=None, b=None, l=None, unit="px"):
    r = t if r is None else r; b = t if b is None else b; l = r if l is None else l
    return {"unit": unit, "top": str(t), "right": str(r), "bottom": str(b), "left": str(l), "isLinked": t == r == b == l}
def gap(n): return {"column": str(n), "row": str(n), "isLinked": True, "unit": "px", "size": n}
def link(url, ext=False, attrs=""): return {"url": url, "is_external": "on" if ext else "", "nofollow": "", "custom_attributes": attrs}
def FA(v, lib="fa-solid"): return {"value": v, "library": lib}
WA_ICON, ARROW, CHECK = FA("fab fa-whatsapp", "fa-brands"), FA("fas fa-arrow-right"), FA("fas fa-check-circle")
def wa(number, msg): return f"https://wa.me/{number}?text={quote(msg)}"

def C_(role):
    """Global color reference for a role (primary, title, text, dark, white, soft, muted, border, on_dark, accent_text, tint)."""
    return f"globals/colors?id={CFG['colors'][role]}"
def T_(kind):
    return f"globals/typography?id={CFG['typography'][kind]}"
def typo(prefix, kind):
    return {f"{prefix}typography_typography": T_(kind)}


# ---------- widgets ----------
def widget(t, s, g=None):
    if g: s["__globals__"] = {**s.get("__globals__", {}), **g}
    return {"id": nid(), "elType": "widget", "widgetType": t, "settings": s, "elements": []}

def heading(title, tag, kind, color="title", align="start", **extra):
    return widget("heading", {"title": title, "header_size": tag, "align": align, **extra},
                  {**typo("", kind), "title_color": C_(color)})

def eyebrow(t, color="dark", align="start"):
    return heading(t, "p", "eyebrow", color=color, align=align)

def text(html, kind="body", color="text", align="start", **extra):
    s = {"editor": html, "align": align, "paragraph_spacing": px(12), **extra}
    g = {**typo("", kind), "text_color": C_(color), "link_color": C_("dark"), "link_hover_color": C_("accent_text")}
    if "<a " in html: s["custom_css"] = "selector a{text-decoration:underline;text-underline-offset:3px;}"
    return widget("text-editor", s, g)

def badge(t, bg="tint", fg="dark"):
    return widget("heading", {"title": t, "header_size": "p", "_element_width": "auto", "_flex_align_self": "flex-start",
                              "custom_css": "selector{width:auto;align-self:flex-start;}",
                              "_background_background": "classic", "_padding": box(6, 10), "_border_radius": box(8)},
                  {**typo("", "badge"), "title_color": C_(fg), "_background_color": C_(bg)})

def button(label, url, variant="primary", icon=None, align="start", full_mobile=True, ext=False, aria=""):
    """Variants: primary (brand bg, dark label — accessible on bright brand colors), dark, outline, outline-light."""
    s = {"text": label, "link": link(url, ext, f"aria-label|{aria}" if aria else ""), "align": align, "size": "md",
         "border_radius": box(12), "button_hover_transition_duration": {"unit": "s", "size": 0.25, "sizes": []},
         "background_background": "classic", "button_background_hover_background": "classic"}
    if full_mobile: s["align_mobile"] = "justify"
    if icon: s.update(selected_icon=icon, icon_align="row" if icon["library"] == "fa-brands" else "row-reverse", icon_indent=px(10))
    g = typo("", "button")
    if variant == "primary":
        g.update(background_color=C_("primary"), button_text_color=C_("dark"), button_background_hover_color=C_("dark"), hover_color=C_("white"))
    elif variant == "dark":
        g.update(background_color=C_("dark"), button_text_color=C_("white"), button_background_hover_color=C_("white"), hover_color=C_("dark"))
    elif variant == "outline":
        s.update(border_border="solid", border_width=box(2), background_color="#FFFFFF00")
        g.update(button_text_color=C_("dark"), border_color=C_("dark"), button_background_hover_color=C_("dark"),
                 hover_color=C_("white"), button_hover_border_color=C_("dark"))
    elif variant == "outline-light":
        s.update(border_border="solid", border_width=box(2), background_color="#FFFFFF00")
        g.update(button_text_color=C_("white"), border_color=C_("white"), button_background_hover_color=C_("white"), hover_color=C_("dark"))
    return widget("button", s, g)

def image(img_id, url, alt="", size="large", **extra):
    return widget("image", {"image": {"id": img_id, "url": url, "alt": alt, "source": "library", "size": ""}, "image_size": size, **extra})

def icon_list(items, inline=False, kind="small", color="text", icon_color="primary", gap_px=12, **extra):
    """items: [(text, icon) or (text, icon, url)]"""
    rows = []
    for it in items:
        t, ic, *rest = it
        row = {"text": t, "selected_icon": ic, "_id": nid()}
        if rest and rest[0]: row["link"] = link(rest[0])
        rows.append(row)
    s = {"icon_list": rows, "icon_size": px(16), "text_indent": px(8), "space_between": px(16 if inline else gap_px),
         "icon_self_vertical_align": "center", **extra}
    if inline: s["view"] = "inline"
    return widget("icon-list", s, {**typo("icon_", kind), "text_color": C_(color), "icon_color": C_(icon_color),
                                   "text_color_hover": C_("accent_text")})

def icon_box(icon, title, desc, dark=False):
    s = {"selected_icon": icon, "title_text": title, "description_text": desc, "title_size": "h3",
         "position": "block-start", "text_align": "start", "view": "stacked", "shape": "rounded",
         "icon_size": px(24), "icon_padding": px(16), "icon_space": px(20), "title_bottom_space": px(8)}
    g = {**typo("title_", "h3"), **typo("description_", "body"), "secondary_color": C_("primary")}
    if dark: s["primary_color"] = "#FFFFFF1A"; g.update(title_color=C_("white"), description_color=C_("on_dark"))
    else: g.update(primary_color=C_("tint"), title_color=C_("title"), description_color=C_("text"))
    return widget("icon-box", s, g)


# ---------- containers ----------
def C(children, inner=True, **s):
    s.setdefault("content_width", "full"); s.setdefault("padding", box(0))
    return {"id": nid(), "elType": "container", "isInner": inner, "settings": s, "elements": children}
def col(ch, g=16, **s): return C(ch, flex_direction="column", flex_gap=gap(g), **s)
def row(ch, g=24, **s): return C(ch, flex_direction="row", flex_gap=gap(g), **s)
def cols(n, g=24): return cu(f"calc((100% - {g * (n - 1)}px) / {n})") if n > 1 else FULL

def section(children, anchor=None, bg=None, g=48, **s):
    """Top-level section. bg: color role ('soft', 'muted', 'dark') or None for white."""
    st = dict(content_width="boxed", boxed_width=px(CFG["boxed"]), flex_direction="column", flex_align_items="stretch",
              flex_gap=gap(g), flex_gap_mobile=gap(32),
              padding=box(96, 24), padding_tablet=box(80, 32), padding_mobile=box(64, 20))
    if bg: st.update(background_background="classic", __globals__={"background_color": C_(bg)})
    if anchor: st.update(_element_id=anchor, custom_css="selector{scroll-margin-top:96px;}")
    st.update(s)
    return C(children, inner=False, **st)

def hero_section(children, **s):
    st = dict(padding=box(176, 24, 96, 24), padding_tablet=box(152, 32, 80, 32), padding_mobile=box(128, 20, 64, 20))
    st.update(s)
    return section(children, **st)

def card(children, g=16, pad=32, **s):
    st = dict(flex_direction="column", flex_gap=gap(g), padding=box(pad), padding_mobile=box(24),
              background_background="classic", border_border="solid", border_width=box(1), border_radius=box(20),
              box_shadow_box_shadow_type="yes",
              box_shadow_box_shadow={"horizontal": 0, "vertical": 8, "blur": 24, "spread": 0, "color": "rgba(0,0,0,0.06)"},
              border_hover_border="solid", border_hover_width=box(1),
              __globals__={"background_color": C_("white"), "border_color": C_("border"), "border_hover_color": C_("primary")})
    st.update(s)
    return C(children, **st)

def grid(children, d, t, m=1, g=24, justify="center"):
    for ch in children: ch['settings'].update(width=cols(d, g), width_tablet=cols(t, g), width_mobile=cols(m, g))
    return C(children, flex_direction="row", flex_wrap="wrap", flex_align_items="stretch", flex_gap=gap(g), flex_justify_content=justify)

def section_head(eb, title, lead=None, align="center", dark=False, tag="h2"):
    items = [eyebrow(eb, color="primary" if dark else "dark", align=align),
             heading(title, tag, "h2", color="white" if dark else "title", align=align)]
    if lead: items.append(text(f"<p>{lead}</p>", "lead", color="on_dark" if dark else "text", align=align))
    return col(items, g=12, flex_align_items="center" if align == "center" else "flex-start",
               custom_css="selector{max-width:720px;margin-inline:auto;}" if align == "center" else "")

def main_wrapper(sections):
    """Root <main id="content"> landmark (fixes the skip link and the 'main landmark' audit)."""
    for s in sections: s["isInner"] = True
    return [{"id": nid(), "elType": "container", "isInner": False, "elements": sections,
             "settings": {"content_width": "full", "html_tag": "main", "_element_id": "content",
                          "flex_direction": "column", "flex_gap": gap(0), "padding": box(0)}}]


# ---------- utilities ----------
def renew_ids(e):
    e = copy.deepcopy(e)
    def r(x):
        x['id'] = nid()
        for c in x.get('elements', []): r(c)
    r(e); return e

def clean(e):
    e['settings'] = {k: v for k, v in e['settings'].items() if v is not None and v != ""}
    for c in e['elements']: clean(c)

OFFICIAL = {"heading", "text-editor", "button", "image", "icon-list", "icon-box", "testimonial", "icon", "divider",
            "social-icons", "html", "spacer", "video", "google_maps", "nav-menu", "form", "table-of-contents",
            "accordion", "nested-accordion", "image-carousel", "counter", "star-rating"}

def check(page, allow=()):
    """Clean empty settings and assert: official widgets only, exactly one H1."""
    h1 = 0
    def chk(e):
        nonlocal h1
        if e['elType'] == 'widget':
            assert e['widgetType'] in OFFICIAL | set(allow), f"non-official widget: {e['widgetType']}"
            if e['settings'].get('header_size') == 'h1': h1 += 1
        for c in e['elements']: chk(c)
    for e in page: clean(e); chk(e)
    assert h1 == 1, f"expected exactly one H1, found {h1}"
    return page
