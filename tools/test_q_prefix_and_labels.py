import json
import re
import random
from collections import Counter, defaultdict
from pathlib import Path

def clean_token(w: str) -> str:
    w = re.sub(r'\[([^:\]]+):[^\]]+\]', r'\1', w)
    w = re.sub(r'\{([^}]+)\}', r'\1', w)
    w = re.sub(r'[@!?;*\'"]', '', w)
    return w.strip()

def get_core_stem(w: str) -> str:
    """Strip grammatical proclitics (q-, y-, d-, s-) and common endings to get the core stem."""
    s = w
    if s.startswith('qo') and len(s) > 3:
        s = s[1:]  # qoX -> oX first
    # Also compute bare root without initial o/y/d/s
    bare = s
    for p in ['o', 'y', 'd', 's']:
        if bare.startswith(p) and len(bare) > 3:
            bare = bare[1:]
            break
    for suf in ['aiin', 'iin', 'ain', 'edy', 'ody', 'eey', 'ey', 'dy', 'ly', 'ry', 'ol', 'al', 'or', 'ar', 'am', 'y', 's', 'd']:
        if bare.endswith(suf) and len(bare) - len(suf) >= 2:
            bare = bare[:-len(suf)]
            break
    return bare

def main():
    lines = Path('data/ZL3b-n.txt').read_text(encoding='utf-8', errors='replace').splitlines()

    folio_para_words = defaultdict(list)
    folio_labels = defaultdict(list)
    folio_lang = {}
    folio_sec = {}

    # Also track row-level label blocks -> immediately following paragraph on Pharmaceutical pages
    pharma_blocks = []
    cur_folio = None
    cur_labels = []

    all_words = Counter()
    label_words = Counter()

    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            cur_folio = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            folio_lang[cur_folio] = kv.get('L', '?')
            folio_sec[cur_folio] = kv.get('I', '?')
            cur_labels = []
            continue

        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, loc_num, loc_type, body = m_loc.groups()
        body_nc = re.sub(r'<![^>]*>', '', body).replace('<%>', '').replace('<$>', '')
        toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
        toks = [t for t in toks if t and not t.isdigit() and '?' not in t]

        if 'L' in loc_type:
            for t in toks:
                folio_labels[f_id].append(t)
                label_words[t] += 1
                cur_labels.append(t)
        elif 'P' in loc_type:
            for t in toks:
                folio_para_words[f_id].append(t)
                all_words[t] += 1
            if cur_labels and folio_sec.get(f_id) == 'P':
                pharma_blocks.append({
                    'folio': f_id,
                    'labels': list(cur_labels),
                    'para_words': list(toks),
                })
                cur_labels = []
            elif pharma_blocks and pharma_blocks[-1]['folio'] == f_id and not cur_labels:
                pharma_blocks[-1]['para_words'].extend(toks)

    # 1. Test the q- + oX = qoX hypothesis across the entire vocabulary
    qo_words = {w: c for w, c in all_words.items() if w.startswith('qo') and len(w) >= 3}
    o_words = {w: c for w, c in all_words.items() if w.startswith('o') and len(w) >= 2}
    q_non_o = {w: c for w, c in all_words.items() if w.startswith('q') and not w.startswith('qo')}

    qo_with_o_twin = 0
    qo_token_with_o_twin = 0
    twin_examples = []
    for qw, qc in sorted(qo_words.items(), key=lambda x: -x[1]):
        ow = qw[1:]  # strip 'q', leaving 'o...'
        oc = all_words.get(ow, 0) + label_words.get(ow, 0)
        if oc > 0:
            qo_with_twin = True
            qo_with_o_twin += 1
            qo_token_with_o_twin += qc
            if len(twin_examples) < 25:
                twin_examples.append({
                    'qo_word': qw,
                    'qo_para_count': qc,
                    'qo_label_count': label_words.get(qw, 0),
                    'o_word': ow,
                    'o_para_count': all_words.get(ow, 0),
                    'o_label_count': label_words.get(ow, 0),
                })

    # Also check y + oX / d + aX / s + aX proclitic patterns
    proclitic_tests = {}
    for proc, base_init in [('q', 'o'), ('y', 'o'), ('y', 'k'), ('y', 't'), ('y', 'ch'), ('y', 'sh'), ('d', 'a'), ('s', 'a')]:
        p_words = {w: c for w, c in all_words.items() if w.startswith(proc + base_init) and len(w) >= 3}
        matched_types = sum(1 for w in p_words if (all_words.get(w[len(proc):], 0) + label_words.get(w[len(proc):], 0)) > 0)
        matched_tokens = sum(c for w, c in p_words.items() if (all_words.get(w[len(proc):], 0) + label_words.get(w[len(proc):], 0)) > 0)
        tot_tokens = sum(p_words.values())
        proclitic_tests[f"{proc}+{base_init}..."] = {
            'types': len(p_words),
            'types_with_bare_twin_pct': round(matched_types / len(p_words) * 100, 1) if p_words else 0,
            'tokens': tot_tokens,
            'tokens_with_bare_twin_pct': round(matched_tokens / tot_tokens * 100, 1) if tot_tokens else 0,
        }

    # 2. Test whether labels on a folio match the paragraph text on the SAME folio vs OTHER folios
    # Check: (a) exact match, (b) q-prefix match (oX <-> qoX), (c) core stem match
    same_folio_exact = 0
    same_folio_qtwin = 0
    same_folio_stem = 0
    total_tested_labels = 0
    exact_matches_detail = []

    folios_with_both = [f for f in folio_labels if folio_para_words[f]]
    for f_id in folios_with_both:
        p_set = set(folio_para_words[f_id])
        p_stems = {get_core_stem(w): w for w in p_set if len(get_core_stem(w)) >= 2}
        for lw in folio_labels[f_id]:
            if len(lw) < 2:
                continue
            total_tested_labels += 1
            is_exact = lw in p_set
            is_qtwin = ('q' + lw) in p_set or (lw.startswith('qo') and lw[1:] in p_set)
            lstem = get_core_stem(lw)
            is_stem = len(lstem) >= 2 and lstem in p_stems
            if is_exact:
                same_folio_exact += 1
            if is_qtwin:
                same_folio_qtwin += 1
            if is_stem:
                same_folio_stem += 1
            if is_exact or is_qtwin:
                exact_matches_detail.append({
                    'folio': f_id,
                    'section': folio_sec.get(f_id, ''),
                    'label': lw,
                    'exact_in_folio_para': is_exact,
                    'qtwin_in_folio_para': ('q' + lw) if ('q' + lw) in p_set else None,
                })

    # Null baseline: shuffle paragraph sets among folios with same Currier language
    random.seed(42)
    null_exact, null_qtwin, null_stem = [], [], []
    for _ in range(200):
        shuffled_map = {}
        for lang in ['A', 'B', '?']:
            flist = [f for f in folios_with_both if folio_lang.get(f, '?') == lang]
            plist = [folio_para_words[f] for f in flist]
            random.shuffle(plist)
            for f, p in zip(flist, plist):
                shuffled_map[f] = set(p)
        e_cnt, q_cnt, s_cnt = 0, 0, 0
        for f_id in folios_with_both:
            p_set = shuffled_map[f_id]
            p_stems = {get_core_stem(w) for w in p_set if len(get_core_stem(w)) >= 2}
            for lw in folio_labels[f_id]:
                if len(lw) < 2:
                    continue
                if lw in p_set:
                    e_cnt += 1
                if ('q' + lw) in p_set:
                    q_cnt += 1
                lstem = get_core_stem(lw)
                if len(lstem) >= 2 and lstem in p_stems:
                    s_cnt += 1
        null_exact.append(e_cnt)
        null_qtwin.append(q_cnt)
        null_stem.append(s_cnt)

    out = {
        'q_proclitic_analysis': {
            'total_qo_types': len(qo_words),
            'total_qo_tokens': sum(qo_words.values()),
            'q_without_o_tokens': sum(q_non_o.values()),
            'qo_types_with_exact_o_twin': qo_with_o_twin,
            'qo_types_with_exact_o_twin_pct': round(qo_with_o_twin / len(qo_words) * 100, 1),
            'qo_tokens_with_exact_o_twin': qo_token_with_o_twin,
            'qo_tokens_with_exact_o_twin_pct': round(qo_token_with_o_twin / sum(qo_words.values()) * 100, 1),
            'top_25_qo_vs_o_twins': twin_examples,
            'proclitic_comparison': proclitic_tests,
        },
        'label_to_same_folio_paragraph_test': {
            'folios_with_labels_and_paragraphs': len(folios_with_both),
            'total_tested_labels': total_tested_labels,
            'same_folio_exact_matches': same_folio_exact,
            'null_shuffled_exact_mean': round(sum(null_exact) / len(null_exact), 2),
            'same_folio_qtwin_matches': same_folio_qtwin,
            'null_shuffled_qtwin_mean': round(sum(null_qtwin) / len(null_qtwin), 2),
            'same_folio_stem_matches': same_folio_stem,
            'null_shuffled_stem_mean': round(sum(null_stem) / len(null_stem), 2),
            'matched_examples': exact_matches_detail,
        }
    }

    Path('data/q_and_label_analysis.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps(out['q_proclitic_analysis']['proclitic_comparison'], indent=2))
    print("qo tokens with exact o-twin:", out['q_proclitic_analysis']['qo_tokens_with_exact_o_twin_pct'], "%")
    print("Label->Same Folio Paragraph test:", json.dumps({k: v for k, v in out['label_to_same_folio_paragraph_test'].items() if k != 'matched_examples'}, indent=2))
    print("\n=== RARE LABEL -> SAME-FOLIO PARAGRAPH MATCHES (Global count <= 15) ===")
    word_locs = defaultdict(list)
    for raw in lines:
        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, lnum, ltype, body = m_loc.groups()
        body_nc = re.sub(r'<![^>]*>', '', body).replace('<%>', '').replace('<$>', '')
        for t in [clean_token(x) for x in re.split(r'[.,\s<>\-]+', body_nc)]:
            if t and not t.isdigit() and '?' not in t:
                word_locs[t].append(f"{f_id}.{lnum}({ltype})")

    seen = set()
    for m in exact_matches_detail:
        lw = m['label']
        qw = m['qtwin_in_folio_para']
        key = (m['folio'], lw, qw)
        if key in seen:
            continue
        seen.add(key)
        locs_l = word_locs.get(lw, [])
        locs_q = word_locs.get(qw, []) if qw else []
        if (m['exact_in_folio_para'] and len(locs_l) <= 15) or (qw and len(locs_q) <= 15):
            print(f"  {m['folio']} [{m['section']}]: label='{lw}' (MS count={len(locs_l)}: {locs_l[:6]}) | qtwin='{qw}' (MS count={len(locs_q)}: {locs_q[:6]})")

if __name__ == '__main__':
    main()
