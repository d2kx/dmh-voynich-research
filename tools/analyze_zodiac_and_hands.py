import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from test_unified_normalization import clean_token, voynich_canonical_root


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def main():
    lines = Path('data/ZL3b-n.txt').read_text(encoding='utf-8', errors='replace').splitlines()

    folio_meta = {}
    cur_folio = None

    # Per-hand stats for the Physical Line & Proclitic rules
    hand_stats = defaultdict(lambda: {
        'folios': set(),
        'sections': Counter(),
        'languages': Counter(),
        'total_words': 0,
        'line0_words': 0,
        'line0_pf': 0,
        'line1plus_words': 0,
        'line1plus_pf': 0,
        'line_start_words': 0,
        'line_start_y': 0,
        'line_mid_words': 0,
        'line_mid_y': 0,
        'line_mid_qo': 0,
        'line_mid_m': 0,
        'line_end_words': 0,
        'line_end_m': 0,
        'after_draw_words': 0,
        'after_draw_y': 0,
        'after_draw_qo': 0,
        'label_words': 0,
        'label_qo': 0,
        'label_o_bare': 0,
    })

    # Zodiac folio data
    zodiac_folios = defaultdict(lambda: {
        'nymph_labels': [],
        'ring_words': [],
        'all_labels': [],
        'comments': [],
    })

    in_para_line_idx = 0

    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            cur_folio = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            folio_meta[cur_folio] = kv
            in_para_line_idx = 0
            continue

        if raw.startswith('# ') and cur_folio:
            if folio_meta.get(cur_folio, {}).get('I') == 'Z':
                zodiac_folios[cur_folio]['comments'].append(raw[2:].strip())
            continue

        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, lnum, ltype, body = m_loc.groups()
        meta = folio_meta.get(f_id, {})
        sec = meta.get('I', '?')
        lang = meta.get('L', '?')
        hand = meta.get('H', '?')

        hs = hand_stats[hand]
        hs['folios'].add(f_id)

        body_nc = re.sub(r'<![^>]*>', '', body)
        is_pstart = '<%>' in body_nc
        is_pend = '<$>' in body_nc
        body_nc = body_nc.replace('<%>', '').replace('<$>', '')

        # Check drawing intrusions <-> before splitting
        segments = body_nc.split('<->')
        seg_tokens = []
        for seg in segments:
            toks = [clean_token(t) for t in re.split(r'[.,\s<>]+', seg)]
            toks = [t for t in toks if t and not t.isdigit() and '?' not in t]
            seg_tokens.append(toks)

        all_toks = [t for seg in seg_tokens for t in seg]
        if not all_toks:
            continue

        hs['total_words'] += len(all_toks)
        hs['sections'][sec] += len(all_toks)
        hs['languages'][lang] += len(all_toks)

        # Zodiac tracking
        if sec == 'Z':
            if 'Lz' in ltype:
                zodiac_folios[f_id]['nymph_labels'].extend(all_toks)
            if 'L' in ltype:
                zodiac_folios[f_id]['all_labels'].extend(all_toks)
            elif 'C' in ltype or 'R' in ltype:
                zodiac_folios[f_id]['ring_words'].extend(all_toks)

        # Label stats per hand
        if 'L' in ltype:
            for w in all_toks:
                hs['label_words'] += 1
                if w.startswith('qo'):
                    hs['label_qo'] += 1
                elif w.startswith('o'):
                    hs['label_o_bare'] += 1
            continue

        # Prose line stats per hand
        if 'P' in ltype:
            if is_pstart:
                in_para_line_idx = 0
            else:
                in_para_line_idx += 1

            for w in all_toks:
                has_pf = any(g in w for g in ('p', 'f'))
                if in_para_line_idx == 0:
                    hs['line0_words'] += 1
                    if has_pf:
                        hs['line0_pf'] += 1
                else:
                    hs['line1plus_words'] += 1
                    if has_pf:
                        hs['line1plus_pf'] += 1

            # Line start / mid / end
            if len(all_toks) >= 2:
                w_start = all_toks[0]
                w_end = all_toks[-1]
                hs['line_start_words'] += 1
                if w_start.startswith('y'):
                    hs['line_start_y'] += 1
                hs['line_end_words'] += 1
                if w_end.endswith('m'):
                    hs['line_end_m'] += 1

                for w_mid in all_toks[1:-1]:
                    hs['line_mid_words'] += 1
                    if w_mid.startswith('y'):
                        hs['line_mid_y'] += 1
                    if w_mid.startswith('qo'):
                        hs['line_mid_qo'] += 1
                    if w_mid.endswith('m'):
                        hs['line_mid_m'] += 1

            # After drawing intrusion (<-> w)
            if len(seg_tokens) > 1:
                for seg in seg_tokens[1:]:
                    if seg:
                        w_after = seg[0]
                        hs['after_draw_words'] += 1
                        if w_after.startswith('y'):
                            hs['after_draw_y'] += 1
                        if w_after.startswith('qo'):
                            hs['after_draw_qo'] += 1

            if is_pend:
                in_para_line_idx = -1

    # Summarize hand_stats
    hand_summary = {}
    for h, st in sorted(hand_stats.items()):
        hand_summary[h] = {
            'folio_count': len(st['folios']),
            'total_words': st['total_words'],
            'sections': dict(st['sections']),
            'languages': dict(st['languages']),
            'top_line_pf_pct': round(100 * st['line0_pf'] / max(1, st['line0_words']), 2),
            'lower_line_pf_pct': round(100 * st['line1plus_pf'] / max(1, st['line1plus_words']), 2),
            'pf_ratio': round((st['line0_pf'] / max(1, st['line0_words'])) / max(0.0001, st['line1plus_pf'] / max(1, st['line1plus_words'])), 1),
            'line_start_y_pct': round(100 * st['line_start_y'] / max(1, st['line_start_words']), 2),
            'line_mid_y_pct': round(100 * st['line_mid_y'] / max(1, st['line_mid_words']), 2),
            'after_draw_y_pct': round(100 * st['after_draw_y'] / max(1, st['after_draw_words']), 2),
            'line_mid_qo_pct': round(100 * st['line_mid_qo'] / max(1, st['line_mid_words']), 2),
            'after_draw_qo_pct': round(100 * st['after_draw_qo'] / max(1, st['after_draw_words']), 2),
            'label_qo_pct': round(100 * st['label_qo'] / max(1, st['label_words']), 2),
            'label_o_bare_pct': round(100 * st['label_o_bare'] / max(1, st['label_words']), 2),
            'line_end_m_pct': round(100 * st['line_end_m'] / max(1, st['line_end_words']), 2),
            'line_mid_m_pct': round(100 * st['line_mid_m'] / max(1, st['line_mid_words']), 2),
            'n_after_draw': st['after_draw_words'],
            'n_labels': st['label_words'],
        }

    # Summarize Zodiac nymph sequences & test sequential similarity along the rings
    zodiac_signs = {
        'f70v2': 'Pisces (Mars)',
        'f70v1': 'Aries I - Dark (Abril)',
        'f71r': 'Aries II - Light (Abril)',
        'f71v': 'Taurus I - Dark (May)',
        'f72r1': 'Taurus II - Light (May)',
        'f72r2': 'Gemini (Juny)',
        'f72r3': 'Cancer (Jolh)',
        'f72v3': 'Leo (Agost)',
        'f72v2': 'Virgo (Setembre)',
        'f72v1': 'Libra (Octobre)',
        'f73r': 'Scorpio (Novembre)',
        'f73v': 'Sagittarius (Desembre)',
    }

    zodiac_summary = {}
    adj_edit_dists = []
    nonadj_edit_dists = []
    shared_prefix2_adj = 0
    shared_prefix2_total = 0
    shared_prefix2_nonadj = 0
    shared_prefix2_nonadj_total = 0

    all_zodiac_nymph_canons = Counter()
    canon_to_zodiac_loci = defaultdict(list)

    for f_id in zodiac_signs:
        z = zodiac_folios[f_id]
        nymphs = z['nymph_labels']
        rings = z['ring_words']
        canons = [voynich_canonical_root(w) for w in nymphs]
        for idx, (w, c) in enumerate(zip(nymphs, canons)):
            all_zodiac_nymph_canons[c] += 1
            canon_to_zodiac_loci[c].append(f"{f_id}[{idx+1}:{w}]")

        for i in range(len(nymphs) - 1):
            w1, w2 = nymphs[i], nymphs[i + 1]
            adj_edit_dists.append(levenshtein(w1, w2))
            shared_prefix2_total += 1
            if len(w1) >= 2 and len(w2) >= 2 and w1[:2] == w2[:2]:
                shared_prefix2_adj += 1

        for i in range(len(nymphs)):
            for j in range(i + 2, len(nymphs)):
                w1, w2 = nymphs[i], nymphs[j]
                nonadj_edit_dists.append(levenshtein(w1, w2))
                shared_prefix2_nonadj_total += 1
                if len(w1) >= 2 and len(w2) >= 2 and w1[:2] == w2[:2]:
                    shared_prefix2_nonadj += 1

        # Match between nymph labels and ring text on the SAME Zodiac folio
        ring_canon_set = set(voynich_canonical_root(w) for w in rings)
        same_folio_ring_matches = [w for w, c in zip(nymphs, canons) if c in ring_canon_set]

        zodiac_summary[f_id] = {
            'sign': zodiac_signs[f_id],
            'n_nymph_labels': len(nymphs),
            'n_ring_words': len(rings),
            'o_initial_pct': round(100 * sum(1 for w in nymphs if w.startswith('o')) / max(1, len(nymphs)), 1),
            'ok_ot_pct': round(100 * sum(1 for w in nymphs if w.startswith(('ok', 'ot'))) / max(1, len(nymphs)), 1),
            'ol_or_pct': round(100 * sum(1 for w in nymphs if w.startswith(('ol', 'or'))) / max(1, len(nymphs)), 1),
            'dy_ending_pct': round(100 * sum(1 for w in nymphs if w.endswith('dy')) / max(1, len(nymphs)), 1),
            'al_ar_ending_pct': round(100 * sum(1 for w in nymphs if w.endswith(('al', 'ar'))) / max(1, len(nymphs)), 1),
            'same_folio_ring_matches': same_folio_ring_matches,
            'sample_nymphs': nymphs[:8],
        }

    repeated_zodiac_nymphs = {
        c: loci for c, loci in sorted(canon_to_zodiac_loci.items(), key=lambda x: -len(x[1]))
        if len(loci) >= 3
    }

    out = {
        'hand_summary': hand_summary,
        'zodiac_summary': zodiac_summary,
        'zodiac_sequential_test': {
            'adj_mean_edit_dist': round(sum(adj_edit_dists) / max(1, len(adj_edit_dists)), 3),
            'nonadj_mean_edit_dist': round(sum(nonadj_edit_dists) / max(1, len(nonadj_edit_dists)), 3),
            'adj_shared_2char_prefix_pct': round(100 * shared_prefix2_adj / max(1, shared_prefix2_total), 2),
            'nonadj_shared_2char_prefix_pct': round(100 * shared_prefix2_nonadj / max(1, shared_prefix2_nonadj_total), 2),
        },
        'repeated_zodiac_nymphs': repeated_zodiac_nymphs,
    }

    Path('data/zodiac_and_hands_analysis.json').write_text(json.dumps(out, indent=2), encoding='utf-8')

    print("=== SCRIBE HAND ($H=1..5) MORPHOLOGICAL INVARIANCE ===")
    for h, st in hand_summary.items():
        print(f"Hand {h} ({st['folio_count']} folios, {st['total_words']} words, langs={st['languages']}):")
        print(f"  Top-line p/f: {st['top_line_pf_pct']}% vs Lower-line: {st['lower_line_pf_pct']}% ({st['pf_ratio']}x)")
        print(f"  y- init: LineStart={st['line_start_y_pct']}%, LineMid={st['line_mid_y_pct']}%, AfterDraw={st['after_draw_y_pct']}% (n={st['n_after_draw']})")
        print(f"  qo- init: LineMid={st['line_mid_qo_pct']}%, AfterDraw={st['after_draw_qo_pct']}%, Labels={st['label_qo_pct']}% (bare o- in labels={st['label_o_bare_pct']}%, n={st['n_labels']})")
        print(f"  -m end: LineEnd={st['line_end_m_pct']}% vs LineMid={st['line_mid_m_pct']}%")

    print("\n=== ZODIAC NYMPH SEQUENTIAL RING TEST ===")
    print(" ", out['zodiac_sequential_test'])
    for f_id, zs in zodiac_summary.items():
        print(f"  {f_id} ({zs['sign']}): nymphs={zs['n_nymph_labels']}, o-init={zs['o_initial_pct']}%, ok/ot={zs['ok_ot_pct']}%, dy-end={zs['dy_ending_pct']}%, ring_matches={zs['same_folio_ring_matches']}")


if __name__ == '__main__':
    main()
