#!/usr/bin/env bash
# Lighthouse summary: scores + key metrics + failing audits with offending nodes.
# Usage: lighthouse.sh <url> [categories=accessibility,performance,seo] [desktop|mobile]
# Uses a cache-busting query is up to you (use ?v=..., never ?m= which is a WordPress date archive).
set -euo pipefail
URL="$1"; CATS="${2:-accessibility,performance,seo}"; FORM="${3:-mobile}"
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "${CHROME_PATH:-}" ]; then
  CHROME_PATH="$(node -e "import('$DIR/cdp.mjs').then(m=>console.log(m.chromePath()))")"; export CHROME_PATH
fi
OUT="$(mktemp --suffix=.json)"
PRESET=""; [ "$FORM" = "desktop" ] && PRESET="--preset=desktop"
npx -y lighthouse@12.8.2 "$URL" $PRESET --only-categories="$CATS" --output=json --output-path="$OUT" \
  --chrome-flags="--headless=new --no-sandbox" --quiet 2>/dev/null
python3 - "$OUT" "$FORM" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])); a = r['audits']
print(f"{r['finalDisplayedUrl']} ({sys.argv[2]})")
print('  ' + ' | '.join(f"{k}: {round(v['score'] * 100)}" for k, v in r['categories'].items()))
if 'performance' in r['categories']:
    print(f"  LCP {a['largest-contentful-paint']['displayValue']} | FCP {a['first-contentful-paint']['displayValue']} | "
          f"CLS {a['cumulative-layout-shift']['displayValue']} | {a['total-byte-weight']['displayValue']}")
for cat in r['categories'].values():
    for ref in cat['auditRefs']:
        au = a[ref['id']]
        if au.get('score') is not None and au['score'] < 1 and ref.get('weight', 0) > 0:
            items = (au.get('details') or {}).get('items', [])
            print(f"  FAIL [{cat['id']}] {ref['id']}: {au['title']} ({len(items)} items)")
            for it in items[:6]:
                n = it.get('node') or {}
                print('     ', (n.get('snippet') or it.get('url') or '')[:140], '|', (n.get('explanation') or '').replace('\n', ' ')[:160])
PY
rm -f "$OUT"
