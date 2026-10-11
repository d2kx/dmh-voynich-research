import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from test_unified_normalization import clean_token, voynich_canonical_root


def main():
    lines = Path('data/ZL3b-n.txt').read_text(encoding='utf-8', errors='replace').splitlines()

    folio_meta = {}
    cur_folio = None

    prose_lines = []  # (folio, sec, lang, hand, quire, lnum, words, canons)
    quire_map = defaultdict(lambda: {'folios': [], 'langs': Counter(), 'hands': Counter(), 'sections': Counter()})
    marginal_and_exotic = []

    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            cur_folio = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            folio_meta[cur_folio] = kv
            q = kv.get('Q', '?')
            quire_map[q]['folios'].append(cur_folio)
            quire_map[q]['langs'][kv.get('L', '?')] += 1
            quire_map[q]['hands'][kv.get('H', '?')] += 1
            quire_map[q]['sections'][kv.get('I', '?')] += 1
            continue

        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, lnum, ltype, body = m_loc.groups()
        meta = folio_meta.get(f_id, {})
        sec = meta.get('I', '?')
        lang = meta.get('L', '?')
        hand = meta.get('H', '?')
        quire = meta.get('Q', '?')

        if 'X' in ltype or 'M' in ltype or '@Ex' in body:
            marginal_and_exotic.append({'locus': f"{f_id}.{lnum}", 'type': ltype, 'body': body})

        body_nc = re.sub(r'<![^>]*>', '', body).replace('<%>', '').replace('<$>', '')
        toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
        toks = [t for t in toks if t and not t.isdigit() and '?' not in t]
        canons = [voynich_canonical_root(t) for t in toks]

        if 'P' in ltype and len(toks) >= 2:
            prose_lines.append({
                'folio': f_id,
                'sec': sec,
                'lang': lang,
                'hand': hand,
                'quire': quire,
                'lnum': lnum,
                'words': toks,
                'canons': canons,
            })

    # 1. Bigram, Trigram, and Adjacent-Word Harmony Analysis
    raw_bigrams = Counter()
    canon_bigrams = Counter()
    raw_trigrams = Counter()
    canon_trigrams = Counter()

    total_adj_pairs = 0
    exact_redup = Counter()          # w1 == w2
    canon_redup_diff_raw = Counter() # w1 != w2 but canon(w1) == canon(w2)
    q_proclitic_pairs = Counter()    # w2 == 'q' + w1 or w1 == 'q' + w2
    one_edit_pairs = Counter()       # len >= 4, differ by exactly 1 char substitution

    adj_same_pref2 = 0
    adj_same_suf2 = 0

    all_line_words_for_null = []

    for ln in prose_lines:
        ws = ln['words']
        cs = ln['canons']
        all_line_words_for_null.append((ws, cs))

        for i in range(len(ws) - 1):
            w1, w2 = ws[i], ws[i + 1]
            c1, c2 = cs[i], cs[i + 1]
            total_adj_pairs += 1
            raw_bigrams[f"{w1} {w2}"] += 1
            canon_bigrams[f"{c1} {c2}"] += 1

            if w1 == w2:
                exact_redup[w1] += 1
            elif c1 == c2 and len(c1) >= 3:
                canon_redup_diff_raw[f"{w1} -> {w2} ({c1})"] += 1

            if w2 == 'q' + w1 or w1 == 'q' + w2:
                q_proclitic_pairs[f"{w1} {w2}"] += 1

            if len(w1) == len(w2) and len(w1) >= 4 and w1 != w2:
                diffs = sum(1 for a, b in zip(w1, w2) if a != b)
                if diffs == 1:
                    one_edit_pairs[f"{w1} {w2}"] += 1

            if len(w1) >= 2 and len(w2) >= 2:
                if w1[:2] == w2[:2]:
                    adj_same_pref2 += 1
                if w1[-2:] == w2[-2:]:
                    adj_same_suf2 += 1

        for i in range(len(ws) - 2):
            raw_trigrams[f"{ws[i]} {ws[i+1]} {ws[i+2]}"] += 1
            canon_trigrams[f"{cs[i]} {cs[i+1]} {cs[i+2]}"] += 1

    # Permutation baseline for adjacent-word harmony (shuffling words within each line)
    rng = random.Random(42)
    null_exact = []
    null_canon_diff = []
    null_one_edit = []
    null_pref2 = []
    null_suf2 = []

    for _ in range(200):
        e_cnt, cd_cnt, oe_cnt, p2_cnt, s2_cnt = 0, 0, 0, 0, 0
        for ws, cs in all_line_words_for_null:
            idx = list(range(len(ws)))
            rng.shuffle(idx)
            for k in range(len(idx) - 1):
                w1, w2 = ws[idx[k]], ws[idx[k + 1]]
                c1, c2 = cs[idx[k]], cs[idx[k + 1]]
                if w1 == w2:
                    e_cnt += 1
                elif c1 == c2 and len(c1) >= 3:
                    cd_cnt += 1
                if len(w1) == len(w2) and len(w1) >= 4 and w1 != w2:
                    if sum(1 for a, b in zip(w1, w2) if a != b) == 1:
                        oe_cnt += 1
                if len(w1) >= 2 and len(w2) >= 2:
                    if w1[:2] == w2[:2]:
                        p2_cnt += 1
                    if w1[-2:] == w2[-2:]:
                        s2_cnt += 1
        null_exact.append(e_cnt)
        null_canon_diff.append(cd_cnt)
        null_one_edit.append(oe_cnt)
        null_pref2.append(p2_cnt)
        null_suf2.append(s2_cnt)

    def stat_summary(obs, null_list):
        mean = sum(null_list) / len(null_list)
        std = (sum((x - mean) ** 2 for x in null_list) / len(null_list)) ** 0.5
        z = (obs - mean) / std if std > 0 else 0.0
        return {'observed': obs, 'expected_within_line_shuffle': round(mean, 2), 'std': round(std, 2), 'z_score': round(z, 2)}

    harmony_stats = {
        'total_adjacent_pairs': total_adj_pairs,
        'exact_reduplication': stat_summary(sum(exact_redup.values()), null_exact),
        'canonical_twin_adjacent': stat_summary(sum(canon_redup_diff_raw.values()), null_canon_diff),
        'one_char_substitution_adjacent': stat_summary(sum(one_edit_pairs.values()), null_one_edit),
        'same_2char_prefix_adjacent': stat_summary(adj_same_pref2, null_pref2),
        'same_2char_suffix_adjacent': stat_summary(adj_same_suf2, null_suf2),
        'top_exact_reduplications': exact_redup.most_common(15),
        'top_canonical_twin_pairs': canon_redup_diff_raw.most_common(20),
        'top_q_proclitic_adjacent_pairs': q_proclitic_pairs.most_common(15),
        'top_one_edit_adjacent_pairs': one_edit_pairs.most_common(20),
        'top_raw_bigrams': raw_bigrams.most_common(25),
        'top_canon_bigrams': canon_bigrams.most_common(25),
        'top_raw_trigrams': raw_trigrams.most_common(20),
        'top_canon_trigrams': canon_trigrams.most_common(20),
    }

    quire_summary = {}
    for q in sorted(quire_map.keys()):
        qm = quire_map[q]
        quire_summary[q] = {
            'folio_range': f"{qm['folios'][0]}..{qm['folios'][-1]}" if qm['folios'] else '',
            'n_folios': len(qm['folios']),
            'sections': dict(qm['sections']),
            'languages': dict(qm['langs']),
            'hands': dict(qm['hands']),
        }

    out = {
        'harmony_stats': harmony_stats,
        'quire_summary': quire_summary,
        'marginal_and_exotic_count': len(marginal_and_exotic),
        'marginal_and_exotic': marginal_and_exotic[:30],
    }

    Path('data/collocations_and_quires.json').write_text(json.dumps(out, indent=2), encoding='utf-8')

    print("=== ADJACENT WORD HARMONY & REDUPLICATION (vs Within-Line Shuffle) ===")
    for k in ['exact_reduplication', 'canonical_twin_adjacent', 'one_char_substitution_adjacent', 'same_2char_prefix_adjacent', 'same_2char_suffix_adjacent']:
        print(f"  {k}: {harmony_stats[k]}")
    print("\nTop Canonical Twin Adjacent Pairs (w1 != w2, canon(w1) == canon(w2)):")
    for p, c in harmony_stats['top_canonical_twin_pairs'][:15]:
        print(f"  {p}: {c}")
    print("\nTop 1-Char Substitution Adjacent Pairs (w1 ~ w2):")
    for p, c in harmony_stats['top_one_edit_adjacent_pairs'][:15]:
        print(f"  {p}: {c}")
    print("\nTop Raw Bigrams:", harmony_stats['top_raw_bigrams'][:12])
    print("Top Raw Trigrams:", harmony_stats['top_raw_trigrams'][:10])


if __name__ == '__main__':
    main()
