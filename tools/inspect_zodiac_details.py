import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from test_unified_normalization import clean_token, voynich_canonical_root


def chi2_2x2(a, b, c, d):
    n = a + b + c + d
    if n == 0 or (a + b) == 0 or (c + d) == 0 or (a + c) == 0 or (b + d) == 0:
        return 0.0
    num = n * (a * d - b * c) ** 2
    den = (a + b) * (c + d) * (a + c) * (b + d)
    return num / den


def main():
    lines = Path('data/ZL3b-n.txt').read_text(encoding='utf-8', errors='replace').splitlines()

    folio_meta = {}
    cur_folio = None
    global_canon_freq = Counter()

    zodiac_order = [
        'f70v2', 'f70v1', 'f71r', 'f71v', 'f72r1', 'f72r2',
        'f72r3', 'f72v3', 'f72v2', 'f72v1', 'f73r', 'f73v'
    ]
    zodiac_data = {f: {'nymphs': [], 'rings': [], 'comments': []} for f in zodiac_order}
    label_type_prefixes = defaultdict(Counter)

    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            cur_folio = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            folio_meta[cur_folio] = kv
            continue

        if raw.startswith('#') and cur_folio in zodiac_data:
            zodiac_data[cur_folio]['comments'].append(raw.strip())
            continue

        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, lnum, ltype, body = m_loc.groups()
        sec = folio_meta.get(f_id, {}).get('I', '?')
        body_nc = re.sub(r'<![^>]*>', '', body).replace('<%>', '').replace('<$>', '')
        toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
        toks = [t for t in toks if t and not t.isdigit() and '?' not in t]
        canons = [voynich_canonical_root(t) for t in toks]
        for c in canons:
            global_canon_freq[c] += 1

        if 'L' in ltype:
            bucket = f"{sec}:{ltype}"
            for t in toks:
                if t.startswith(('ot', 'op')):
                    label_type_prefixes[bucket]['ot_op'] += 1
                elif t.startswith(('ok', 'of')):
                    label_type_prefixes[bucket]['ok_of'] += 1
                elif t.startswith(('ol', 'or')):
                    label_type_prefixes[bucket]['ol_or'] += 1
                else:
                    label_type_prefixes[bucket]['other'] += 1
                label_type_prefixes[bucket]['total'] += 1

        if f_id in zodiac_data:
            if 'Lz' in ltype:
                for t, c in zip(toks, canons):
                    zodiac_data[f_id]['nymphs'].append({'locus': f"{f_id}.{lnum}", 'word': t, 'canon': c})
            elif 'C' in ltype or 'R' in ltype or 'P' in ltype:
                for t, c in zip(toks, canons):
                    zodiac_data[f_id]['rings'].append({'locus': f"{f_id}.{lnum}", 'word': t, 'canon': c})

    # Test barreled Zodiac folios (f70v2..f72r1) vs unbarreled Zodiac folios (f72r2..f73v)
    barreled_folios = ['f70v2', 'f70v1', 'f71r', 'f71v', 'f72r1']
    unbarreled_folios = ['f72r2', 'f72r3', 'f72v3', 'f72v2', 'f72v1', 'f73r', 'f73v']

    b_ot = sum(1 for f in barreled_folios for n in zodiac_data[f]['nymphs'] if n['word'].startswith(('ot', 'op')))
    b_ok = sum(1 for f in barreled_folios for n in zodiac_data[f]['nymphs'] if n['word'].startswith(('ok', 'of')))
    u_ot = sum(1 for f in unbarreled_folios for n in zodiac_data[f]['nymphs'] if n['word'].startswith(('ot', 'op')))
    u_ok = sum(1 for f in unbarreled_folios for n in zodiac_data[f]['nymphs'] if n['word'].startswith(('ok', 'of')))

    chi2_zod = chi2_2x2(b_ot, b_ok, u_ot, u_ok)
    print(f"Zodiac Barreled (f70v2-f72r1) vs Unbarreled (f72r2-f73v) ot/op vs ok/of:")
    print(f"  Barreled:   ot/op={b_ot}, ok/of={b_ok} ({100*b_ot/max(1,b_ot+b_ok):.1f}% ot/op)")
    print(f"  Unbarreled: ot/op={u_ot}, ok/of={u_ok} ({100*u_ot/max(1,u_ot+u_ok):.1f}% ot/op)")
    print(f"  Chi2 = {chi2_zod:.2f}")

    print("\n=== LABEL PREFIX BREAKDOWN BY SECTION & LABEL TYPE ===")
    for k, cnt in sorted(label_type_prefixes.items()):
        tot = cnt['total']
        if tot < 5:
            continue
        ot_p = 100 * cnt['ot_op'] / tot
        ok_p = 100 * cnt['ok_of'] / tot
        ol_p = 100 * cnt['ol_or'] / tot
        print(f"  {k:10s} (n={tot:3d}): ot/op={cnt['ot_op']:3d} ({ot_p:4.1f}%), ok/of={cnt['ok_of']:3d} ({ok_p:4.1f}%), ol/or={cnt['ol_or']:3d} ({ol_p:4.1f}%)")

    # Save JSON summary
    out = {
        'zodiac_barrel_vs_unbarreled': {
            'barreled_folios': barreled_folios,
            'unbarreled_folios': unbarreled_folios,
            'barreled_ot_op': b_ot,
            'barreled_ok_of': b_ok,
            'barreled_ot_pct': round(100 * b_ot / max(1, b_ot + b_ok), 2),
            'unbarreled_ot_op': u_ot,
            'unbarreled_ok_of': u_ok,
            'unbarreled_ot_pct': round(100 * u_ot / max(1, u_ot + u_ok), 2),
            'chi2': round(chi2_zod, 2),
        },
        'label_type_prefixes': {k: dict(v) for k, v in label_type_prefixes.items()},
    }
    Path('data/zodiac_prefix_split.json').write_text(json.dumps(out, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
