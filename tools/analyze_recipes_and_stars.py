import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from test_unified_normalization import clean_token, voynich_canonical_root

def main():
    lines = Path('data/ZL3b-n.txt').read_text(encoding='utf-8', errors='replace').splitlines()

    folio_meta = {}
    cur_folio = None
    pending_star_comment = None

    starred_paras = []
    cur_para = None

    all_labels = []  # (folio, sec, locus, ltype, word, canon)
    para_records = []  # (folio, sec, lang, hand, para_id, star_info, words, canons, loci)
    special_lines = []  # =Pt, +Pr, +Pc

    global_word_freq = Counter()
    global_canon_freq = Counter()

    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            if cur_para:
                para_records.append(cur_para)
                cur_para = None
            cur_folio = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            folio_meta[cur_folio] = kv
            pending_star_comment = None
            continue

        if raw.startswith('# '):
            c = raw[2:].strip()
            if 'star' in c.lower():
                pending_star_comment = c
            continue

        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, lnum, ltype, body = m_loc.groups()
        sec = folio_meta.get(f_id, {}).get('I', '?')
        lang = folio_meta.get(f_id, {}).get('L', '?')
        hand = folio_meta.get(f_id, {}).get('H', '?')

        body_nc = re.sub(r'<![^>]*>', '', body)
        is_pstart = '<%>' in body_nc
        is_pend = '<$>' in body_nc
        body_nc = body_nc.replace('<%>', '').replace('<$>', '')
        toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
        toks = [t for t in toks if t and not t.isdigit() and '?' not in t]

        for t in toks:
            global_word_freq[t] += 1
            global_canon_freq[voynich_canonical_root(t)] += 1

        if ltype in ('=Pt', '+Pr', '+Pc'):
            special_lines.append({
                'folio': f_id,
                'sec': sec,
                'locus': f"{f_id}.{lnum}",
                'type': ltype,
                'words': toks,
                'canons': [voynich_canonical_root(t) for t in toks],
            })

        if 'L' in ltype:
            for t in toks:
                all_labels.append({
                    'folio': f_id,
                    'sec': sec,
                    'locus': f"{f_id}.{lnum}",
                    'type': ltype,
                    'word': t,
                    'canon': voynich_canonical_root(t),
                })
            continue

        if 'P' in ltype:
            if is_pstart or cur_para is None:
                if cur_para:
                    para_records.append(cur_para)
                cur_para = {
                    'folio': f_id,
                    'sec': sec,
                    'lang': lang,
                    'hand': hand,
                    'start_locus': f"{f_id}.{lnum}",
                    'star_comment': pending_star_comment,
                    'words': list(toks),
                    'lines': [toks],
                }
                pending_star_comment = None
            else:
                if pending_star_comment and not cur_para.get('star_comment'):
                    cur_para['star_comment'] = pending_star_comment
                    pending_star_comment = None
                cur_para['words'].extend(toks)
                cur_para['lines'].append(toks)

            if is_pend and cur_para:
                para_records.append(cur_para)
                cur_para = None

    if cur_para:
        para_records.append(cur_para)

    # 1. Analyze Starred Recipes (sec == 'S') by star type (Dark vs Light vs Dotted vs Tail)
    star_buckets = defaultdict(list)
    for p in para_records:
        if p['sec'] != 'S' or not p['words']:
            continue
        sc = (p['star_comment'] or 'none').lower()
        if 'dark' in sc:
            stype = 'dark_star'
        elif 'dotted' in sc:
            stype = 'light_dotted_star'
        elif 'light' in sc:
            stype = 'light_plain_star'
        else:
            stype = 'unmarked_or_other'
        star_buckets[stype].append(p)
        if 'tail' in sc:
            star_buckets['has_tail'].append(p)
        elif stype != 'unmarked_or_other':
            star_buckets['no_tail'].append(p)

    star_stats = {}
    for stype, plist in star_buckets.items():
        all_w = [w for p in plist for w in p['words']]
        first_w = [p['words'][0] for p in plist if p['words']]
        last_w = [p['words'][-1] for p in plist if p['words']]
        n_p = len(plist)
        n_w = len(all_w)
        star_stats[stype] = {
            'paragraphs': n_p,
            'avg_words_per_para': round(n_w / n_p, 2) if n_p else 0,
            'avg_lines_per_para': round(sum(len(p['lines']) for p in plist) / n_p, 2) if n_p else 0,
            'first_word_p_pct': round(sum(1 for w in first_w if w.startswith(('p', 'cph', 'op'))) / n_p * 100, 1),
            'first_word_t_pct': round(sum(1 for w in first_w if w.startswith(('t', 'cth', 'ot'))) / n_p * 100, 1),
            'first_word_k_pct': round(sum(1 for w in first_w if w.startswith(('k', 'ckh', 'ok'))) / n_p * 100, 1),
            'first_word_q_pct': round(sum(1 for w in first_w if w.startswith('q')) / n_p * 100, 1),
            'edy_pct': round(sum(1 for w in all_w if w.endswith('edy')) / n_w * 100, 2),
            'aiin_pct': round(sum(1 for w in all_w if w.endswith('aiin')) / n_w * 100, 2),
            'qo_pct': round(sum(1 for w in all_w if w.startswith('qo')) / n_w * 100, 2),
            'top_first_words': Counter(first_w).most_common(5),
            'top_last_words': Counter(last_w).most_common(5),
        }

    #Check alternation pattern of stars on Starred Recipe pages (e.g. Dark / Light / Dotted sequence)
    star_sequences_by_folio = defaultdict(list)
    for p in para_records:
        if p['sec'] == 'S':
            sc = (p['star_comment'] or 'none').lower()
            code = 'D' if 'dark' in sc else ('L.' if 'dotted' in sc else ('L' if 'light' in sc else '?'))
            star_sequences_by_folio[p['folio']].append(code)

    # 2. Build Plant/Jar Label Concordance across Sections:
    # Which rare labels (len >= 4, global canonical frequency <= 15) in Pharmaceutical (P) or Herbal (H) or Biological (B) or Zodiac (Z)
    # appear in Starred Recipes (S) or Herbal (H) paragraphs?
    canon_to_paras = defaultdict(list)
    for p in para_records:
        for w in set(p['words']):
            cw = voynich_canonical_root(w)
            canon_to_paras[cw].append({
                'folio': p['folio'],
                'sec': p['sec'],
                'start_locus': p['start_locus'],
                'word': w,
            })

    rare_label_concordance = []
    seen_lbl = set()
    for lbl in all_labels:
        lw = lbl['word']
        cw = lbl['canon']
        if len(lw) < 4 or global_canon_freq[cw] > 15:
            continue
        key = (lbl['folio'], lw)
        if key in seen_lbl:
            continue
        seen_lbl.add(key)
        matches = canon_to_paras.get(cw, [])
        if matches:
            rare_label_concordance.append({
                'label_folio': lbl['folio'],
                'label_sec': lbl['sec'],
                'label_locus': lbl['locus'],
                'label_type': lbl['type'],
                'label_word': lw,
                'canonical_root': cw,
                'global_canon_freq': global_canon_freq[cw],
                'paragraph_occurrences': matches,
            })

    # 3. Check Right-Justified Paragraph Titles (=Pt) and whether they appear as labels or paragraph words elsewhere
    pt_analysis = []
    for sp in special_lines:
        if sp['type'] == '=Pt':
            for w, cw in zip(sp['words'], sp['canons']):
                pt_analysis.append({
                    'folio': sp['folio'],
                    'locus': sp['locus'],
                    'word': w,
                    'canon': cw,
                    'global_word_freq': global_word_freq[w],
                    'global_canon_freq': global_canon_freq[cw],
                    'other_occurrences': [m for m in canon_to_paras.get(cw, []) if m['folio'] != sp['folio']][:8],
                })

    out = {
        'starred_recipes_by_star_type': star_stats,
        'star_sequences_by_folio': {k: ''.join(v) for k, v in star_sequences_by_folio.items()},
        'rare_label_to_paragraph_concordance_count': len(rare_label_concordance),
        'rare_label_to_paragraph_concordance': rare_label_concordance,
        'right_justified_Pt_titles': pt_analysis,
    }

    Path('data/recipes_and_stars_analysis.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print("=== STARRED RECIPES BY STAR TYPE ===")
    print(json.dumps(star_stats, indent=2))
    print("\n=== STAR SEQUENCES BY FOLIO (L=Light plain, L.=Light dotted, D=Dark) ===")
    for f, seq in star_sequences_by_folio.items():
        print(f"  {f:6s}: {' '.join(seq)}")
    print(f"\n=== RARE LABEL CONCORDANCE (n={len(rare_label_concordance)}) ===")
    for item in rare_label_concordance[:30]:
        locs = [f"{m['folio']}({m['sec']}):{m['word']}" for m in item['paragraph_occurrences']]
        print(f"  {item['label_locus']} [{item['label_sec']}] '{item['label_word']}' (canon='{item['canonical_root']}', freq={item['global_canon_freq']}) -> {locs}")
    print("\n=== RIGHT-JUSTIFIED =Pt TITLES ===")
    for pt in pt_analysis:
        print(" ", pt)

if __name__ == '__main__':
    main()
