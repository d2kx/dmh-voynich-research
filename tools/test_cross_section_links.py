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
    pending_star_comment = None

    folio_label_groups = defaultdict(list)
    folio_prose_lines = defaultdict(list)
    starred_paragraphs = defaultdict(list)

    cur_label_group = []
    cur_para = None

    global_canon_freq = Counter()

    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            if cur_folio and cur_label_group:
                folio_label_groups[cur_folio].append(cur_label_group)
                cur_label_group = []
            if cur_para and cur_para['sec'] == 'S':
                starred_paragraphs[cur_para['folio']].append(cur_para)
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

        body_nc = re.sub(r'<![^>]*>', '', body)
        is_pstart = '<%>' in body_nc
        is_pend = '<$>' in body_nc
        body_nc = body_nc.replace('<%>', '').replace('<$>', '')
        toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
        toks = [t for t in toks if t and not t.isdigit() and '?' not in t]
        canons = [voynich_canonical_root(t) for t in toks]

        for c in canons:
            global_canon_freq[c] += 1

        if 'L' in ltype:
            for t, c in zip(toks, canons):
                cur_label_group.append({
                    'lnum': lnum,
                    'ltype': ltype,
                    'word': t,
                    'canon': c,
                })
            continue
        else:
            if cur_label_group:
                folio_label_groups[f_id].append(cur_label_group)
                cur_label_group = []

        if 'P' in ltype:
            folio_prose_lines[f_id].append({
                'lnum': lnum,
                'ltype': ltype,
                'words': toks,
                'canons': canons,
            })

            if is_pstart or cur_para is None:
                if cur_para and cur_para['sec'] == 'S':
                    starred_paragraphs[cur_para['folio']].append(cur_para)
                sc = (pending_star_comment or 'none').lower()
                code = 'D' if 'dark' in sc else ('L.' if 'dotted' in sc else ('L' if 'light' in sc else '?'))
                cur_para = {
                    'folio': f_id,
                    'sec': sec,
                    'star': code,
                    'star_comment': pending_star_comment,
                    'words': list(toks),
                    'canons': list(canons),
                }
                pending_star_comment = None
            else:
                if pending_star_comment and cur_para.get('star') == '?':
                    sc = pending_star_comment.lower()
                    cur_para['star'] = 'D' if 'dark' in sc else ('L.' if 'dotted' in sc else ('L' if 'light' in sc else '?'))
                    cur_para['star_comment'] = pending_star_comment
                    pending_star_comment = None
                cur_para['words'].extend(toks)
                cur_para['canons'].extend(canons)

            if is_pend and cur_para:
                if cur_para['sec'] == 'S':
                    starred_paragraphs[cur_para['folio']].append(cur_para)
                cur_para = None

    if cur_folio and cur_label_group:
        folio_label_groups[cur_folio].append(cur_label_group)
    if cur_para and cur_para['sec'] == 'S':
        starred_paragraphs[cur_para['folio']].append(cur_para)

    # TEST 1: Horizontal (x-coordinate) correlation between label position in its row/group
    # and word position in the paragraph line on the same folio
    x_pairs = []
    for f, groups in folio_label_groups.items():
        label_x_map = {}
        for g in groups:
            if len(g) >= 3:
                for idx, item in enumerate(g):
                    c = item['canon']
                    if len(c) >= 3 and global_canon_freq[c] <= 30:
                        label_x_map[c] = idx / (len(g) - 1)

        for ln in folio_prose_lines[f]:
            n_words = len(ln['canons'])
            if n_words < 3:
                continue
            for w_idx, c in enumerate(ln['canons']):
                if c in label_x_map:
                    word_x = w_idx / (n_words - 1)
                    label_x = label_x_map[c]
                    x_pairs.append({
                        'folio': f,
                        'canon': c,
                        'global_freq': global_canon_freq[c],
                        'label_x': round(label_x, 3),
                        'word_x': round(word_x, 3),
                        'line_num': ln['lnum'],
                        'word': ln['words'][w_idx],
                    })

    if len(x_pairs) >= 3:
        lx = [p['label_x'] for p in x_pairs]
        wx = [p['word_x'] for p in x_pairs]
        mean_lx = sum(lx) / len(lx)
        mean_wx = sum(wx) / len(wx)
        num = sum((a - mean_lx) * (b - mean_wx) for a, b in zip(lx, wx))
        den = math.sqrt(sum((a - mean_lx) ** 2 for a in lx) * sum((b - mean_wx) ** 2 for b in wx))
        r_obs = num / den if den > 0 else 0.0

        rng = random.Random(42)
        ge_count = 0
        n_perm = 10000
        for _ in range(n_perm):
            wx_shuf = list(wx)
            rng.shuffle(wx_shuf)
            num_s = sum((a - mean_lx) * (b - mean_wx) for a, b in zip(lx, wx_shuf))
            r_s = num_s / den if den > 0 else 0.0
            if r_s >= r_obs:
                ge_count += 1
        p_val_x = ge_count / n_perm
    else:
        r_obs, p_val_x = 0.0, 1.0

    # TEST 2: Starred Recipes (f103r-f116r) Paired Binary Alternation Test (L. vs L)
    paired_jaccards = []
    unpaired_adj_jaccards = []
    same_folio_nonadj_jaccards = []

    for f, paras in starred_paragraphs.items():
        if len(paras) < 4:
            continue
        for i in range(len(paras) - 1):
            s1, s2 = set(paras[i]['canons']), set(paras[i + 1]['canons'])
            if not s1 or not s2:
                continue
            jac = len(s1 & s2) / len(s1 | s2)
            st1, st2 = paras[i]['star'], paras[i + 1]['star']
            if st1 == 'L.' and st2 == 'L':
                paired_jaccards.append(jac)
            elif st1 == 'L' and st2 == 'L.':
                unpaired_adj_jaccards.append(jac)

        for i in range(len(paras)):
            for j in range(i + 2, len(paras)):
                s1, s2 = set(paras[i]['canons']), set(paras[j]['canons'])
                if s1 and s2:
                    same_folio_nonadj_jaccards.append(len(s1 & s2) / len(s1 | s2))

    alt_folios = ['f103v', 'f104v', 'f105v', 'f106r', 'f106v', 'f107v', 'f108v', 'f112v', 'f113v', 'f114r', 'f114v', 'f115v']
    l_dot_stats = {'n': 0, 'words': 0, 'init_p_f': 0, 'init_t_k': 0, 'init_q': 0, 'init_o': 0, 'init_d_s': 0}
    l_plain_stats = {'n': 0, 'words': 0, 'init_p_f': 0, 'init_t_k': 0, 'init_q': 0, 'init_o': 0, 'init_d_s': 0}

    for f in alt_folios:
        for p in starred_paragraphs.get(f, []):
            st = p['star']
            w0 = p['words'][0] if p['words'] else ''
            target = l_dot_stats if st == 'L.' else (l_plain_stats if st == 'L' else None)
            if not target:
                continue
            target['n'] += 1
            target['words'] += len(p['words'])
            if w0.startswith(('p', 'f', 'cph', 'cfh', 'op', 'of')):
                target['init_p_f'] += 1
            elif w0.startswith(('t', 'k', 'cth', 'ckh', 'ot', 'ok')):
                target['init_t_k'] += 1
            elif w0.startswith('q'):
                target['init_q'] += 1
            elif w0.startswith('o'):
                target['init_o'] += 1
            elif w0.startswith(('d', 's')):
                target['init_d_s'] += 1

    # TEST 3: Cross-Section Label Density in Starred Recipes (S) & Herbal (H)
    s_prose_canons = Counter()
    h_prose_canons = Counter()
    b_prose_canons = Counter()
    p_prose_canons = Counter()
    for f, lns in folio_prose_lines.items():
        sec = folio_meta.get(f, {}).get('I', '')
        for ln in lns:
            if sec == 'S':
                s_prose_canons.update(ln['canons'])
            elif sec == 'H':
                h_prose_canons.update(ln['canons'])
            elif sec == 'B':
                b_prose_canons.update(ln['canons'])
            elif sec == 'P':
                p_prose_canons.update(ln['canons'])

    section_label_cross = {}
    for label_sec in ['P', 'B', 'Z', 'A', 'C']:
        rare_labels = set()
        for f, groups in folio_label_groups.items():
            if folio_meta.get(f, {}).get('I', '') == label_sec:
                for g in groups:
                    for item in g:
                        c = item['canon']
                        if len(c) >= 4 and 2 <= global_canon_freq[c] <= 15:
                            rare_labels.add(c)
        if not rare_labels:
            continue
        in_s = sum(1 for c in rare_labels if s_prose_canons[c] > 0)
        in_h = sum(1 for c in rare_labels if h_prose_canons[c] > 0)
        in_b = sum(1 for c in rare_labels if b_prose_canons[c] > 0)
        in_p = sum(1 for c in rare_labels if p_prose_canons[c] > 0)
        section_label_cross[label_sec] = {
            'rare_label_types': len(rare_labels),
            'in_S_pct': round(100 * in_s / len(rare_labels), 2),
            'in_H_pct': round(100 * in_h / len(rare_labels), 2),
            'in_B_pct': round(100 * in_b / len(rare_labels), 2),
            'in_P_pct': round(100 * in_p / len(rare_labels), 2),
            'S_matches': sorted([c for c in rare_labels if s_prose_canons[c] > 0]),
            'H_matches': sorted([c for c in rare_labels if h_prose_canons[c] > 0]),
        }

    out = {
        'horizontal_x_alignment': {
            'n_pairs': len(x_pairs),
            'pearson_r': round(r_obs, 4),
            'perm_p_value': round(p_val_x, 4),
            'pairs': x_pairs,
        },
        'starred_alternation_test': {
            'paired_Ldot_to_L_jaccard': round(sum(paired_jaccards) / max(1, len(paired_jaccards)), 4),
            'unpaired_L_to_Ldot_jaccard': round(sum(unpaired_adj_jaccards) / max(1, len(unpaired_adj_jaccards)), 4),
            'nonadjacent_same_folio_jaccard': round(sum(same_folio_nonadj_jaccards) / max(1, len(same_folio_nonadj_jaccards)), 4),
            'L_dot_stats': l_dot_stats,
            'L_plain_stats': l_plain_stats,
        },
        'section_label_cross': section_label_cross,
    }

    Path('data/cross_section_and_alignment.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f"Horizontal x alignment: n={len(x_pairs)}, r={r_obs:.4f}, p={p_val_x:.4f}")
    for p in x_pairs:
        print(" ", p)
    print("\nStarred alternation Jaccard:")
    print(f"  Paired (L. -> L, n={len(paired_jaccards)}):", out['starred_alternation_test']['paired_Ldot_to_L_jaccard'])
    print(f"  Unpaired adj (L -> L., n={len(unpaired_adj_jaccards)}):", out['starred_alternation_test']['unpaired_L_to_Ldot_jaccard'])
    print(f"  Non-adj same folio (n={len(same_folio_nonadj_jaccards)}):", out['starred_alternation_test']['nonadjacent_same_folio_jaccard'])
    print("  L. stats:", l_dot_stats)
    print("  L plain stats:", l_plain_stats)
    print("\nCross-section rare label (freq 2..15) recurrence:")
    for k, v in section_label_cross.items():
        print(f"  Label sec {k} (n={v['rare_label_types']}): S={v['in_S_pct']}%, H={v['in_H_pct']}%, B={v['in_B_pct']}%, P={v['in_P_pct']}%")


if __name__ == '__main__':
    main()
