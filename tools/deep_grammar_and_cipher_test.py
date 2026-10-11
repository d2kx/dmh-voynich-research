import json
import math
import re
import random
from collections import Counter, defaultdict
from pathlib import Path

def clean_token(w: str) -> str:
    w = re.sub(r'\[([^:\]]+):[^\]]+\]', r'\1', w)
    w = re.sub(r'\{([^}]+)\}', r'\1', w)
    w = re.sub(r'[@!?;*\'"]', '', w)
    return w.strip()

def edit_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
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

def normalize_voynich_stem(w: str) -> str:
    """Normalize a Voynich word by stripping proclitics (q, y) and collapsing eee/ee->e, iii/ii->i."""
    s = w
    if s.startswith('qo') and len(s) > 3:
        s = s[1:]
    elif s.startswith('y') and len(s) > 3:
        s = s[1:]
    s = re.sub(r'e+', 'e', s)
    s = re.sub(r'i+', 'i', s)
    return s

SLOT_REGEX = re.compile(
    r'^(?P<proc>q|y|d|s|l|r)?'
    r'(?P<v1>o|a|e|i+)?'
    r'(?P<core>cth|ckh|cph|cfh|ch|sh|k|t|p|f|d|s|l|r|m|n)?'
    r'(?P<v2>e+|o+|a+|i+)?'
    r'(?P<c2>cth|ckh|cph|cfh|ch|sh|k|t|p|f|d|l|r)?'
    r'(?P<suf>aiin|oiin|eiin|iin|ain|edy|ody|eey|ey|dy|hy|ky|ly|ry|ty|ol|al|or|ar|am|om|an|in|y|l|r|m|n|s)?$'
)

def main():
    lines = Path('data/ZL3b-n.txt').read_text(encoding='utf-8', errors='replace').splitlines()

    # 1. Parse row-level [Label Block -> Paragraph Block] across Pharmaceutical & Biological & Astrological
    blocks = []
    cur_folio = None
    cur_sec = None
    cur_lang = None
    cur_labels = []
    cur_para = []
    cur_para_loci = []

    all_tokens = []
    para_lines = []  # (folio, sec, lang, line_idx_in_para, is_last_line, tokens)

    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            if cur_labels and cur_para:
                blocks.append({
                    'folio': cur_folio, 'sec': cur_sec, 'lang': cur_lang,
                    'labels': cur_labels, 'para': cur_para, 'loci': cur_para_loci
                })
            cur_folio = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            cur_sec = kv.get('I', '?')
            cur_lang = kv.get('L', '?')
            cur_labels = []
            cur_para = []
            cur_para_loci = []
            p_line_idx = 0
            continue

        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, lnum, ltype, body = m_loc.groups()
        body_nc = re.sub(r'<![^>]*>', '', body)
        is_pstart = '<%>' in body_nc
        is_pend = '<$>' in body_nc
        body_nc = body_nc.replace('<%>', '').replace('<$>', '')
        toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
        toks = [t for t in toks if t and not t.isdigit() and '?' not in t]

        if 'L' in ltype:
            if cur_labels and cur_para:
                blocks.append({
                    'folio': cur_folio, 'sec': cur_sec, 'lang': cur_lang,
                    'labels': cur_labels, 'para': cur_para, 'loci': cur_para_loci
                })
                cur_labels = []
                cur_para = []
                cur_para_loci = []
            for t in toks:
                cur_labels.append((f"{f_id}.{lnum}", t))
        elif 'P' in ltype:
            if is_pstart:
                p_line_idx = 0
            else:
                p_line_idx += 1
            if toks:
                para_lines.append((f_id, cur_sec, cur_lang, p_line_idx, is_pend, toks))
                all_tokens.extend(toks)
            for t in toks:
                cur_para.append((f"{f_id}.{lnum}", t))
            cur_para_loci.append(f"{f_id}.{lnum}")

    if cur_labels and cur_para:
        blocks.append({
            'folio': cur_folio, 'sec': cur_sec, 'lang': cur_lang,
            'labels': cur_labels, 'para': cur_para, 'loci': cur_para_loci
        })

    # Analyze close morphological/orthographic matches (edit distance <= 1 on normalized stem of len >= 5)
    # between a label and the paragraph in the same block!
    global_freq = Counter(all_tokens)
    block_close_hits = []
    for b in blocks:
        for l_loc, lw in b['labels']:
            if len(lw) < 4:
                continue
            nlw = normalize_voynich_stem(lw)
            for p_loc, pw in b['para']:
                if len(pw) < 4:
                    continue
                npw = normalize_voynich_stem(pw)
                dist = edit_distance(nlw, npw)
                if dist == 0 or (dist == 1 and len(nlw) >= 5 and len(npw) >= 5):
                    # Filter out ultra-common words (global count > 30)
                    if global_freq[lw] <= 25 and global_freq[pw] <= 35:
                        block_close_hits.append({
                            'folio': b['folio'],
                            'sec': b['sec'],
                            'label_locus': l_loc,
                            'label': lw,
                            'label_global_count': global_freq[lw],
                            'para_locus': p_loc,
                            'para_word': pw,
                            'para_global_count': global_freq[pw],
                            'norm_edit_dist': dist,
                        })

    # 2. Gallows distribution by line index within paragraph (Line 0 vs Line 1+ of paragraph)
    line0_words = [toks[0] for _, _, _, lidx, _, toks in para_lines if lidx == 0 and toks]
    line1p_words = [toks[0] for _, _, _, lidx, _, toks in para_lines if lidx > 0 and toks]
    interior_words = [t for _, _, _, _, _, toks in para_lines for t in toks[1:]]

    def gallows_breakdown(wlist):
        n = len(wlist)
        return {
            'total': n,
            'p_or_cph_pct': round(sum(1 for w in wlist if w.startswith(('p', 'cph', 'op'))) / n * 100, 2),
            'f_or_cfh_pct': round(sum(1 for w in wlist if w.startswith(('f', 'cfh', 'of'))) / n * 100, 2),
            't_or_cth_pct': round(sum(1 for w in wlist if w.startswith(('t', 'cth', 'ot', 'qot'))) / n * 100, 2),
            'k_or_ckh_pct': round(sum(1 for w in wlist if w.startswith(('k', 'ckh', 'ok', 'qok'))) / n * 100, 2),
        }

    # Also check anywhere inside word on Line 0 of paragraph vs Line 1+ of paragraph!
    line0_all_toks = [t for _, _, _, lidx, _, toks in para_lines if lidx == 0 for t in toks]
    line1p_all_toks = [t for _, _, _, lidx, _, toks in para_lines if lidx > 0 for t in toks]
    pf_in_line0 = sum(1 for w in line0_all_toks if 'p' in w or 'f' in w) / len(line0_all_toks) * 100
    pf_in_line1p = sum(1 for w in line1p_all_toks if 'p' in w or 'f' in w) / len(line1p_all_toks) * 100
    kt_in_line0 = sum(1 for w in line0_all_toks if 'k' in w or 't' in w) / len(line0_all_toks) * 100
    kt_in_line1p = sum(1 for w in line1p_all_toks if 'k' in w or 't' in w) / len(line1p_all_toks) * 100

    # 3. Test Slot Regex coverage and Adjacent Word Lockstep (Repetition / Rhyme / Prefix-Suffix Harmony)
    slot_matched = sum(1 for w in all_tokens if SLOT_REGEX.match(w))
    slot_coverage_pct = round(slot_matched / len(all_tokens) * 100, 2)

    # Adjacent word similarity within lines vs shuffled lines
    adj_exact = 0
    adj_dist1 = 0
    adj_same_suffix = 0
    adj_same_prefix = 0
    total_adj_pairs = 0

    null_exact, null_dist1, null_suf = 0, 0, 0
    for _, _, _, _, _, toks in para_lines:
        if len(toks) < 2:
            continue
        shuf = list(toks)
        random.shuffle(shuf)
        for i in range(len(toks) - 1):
            w1, w2 = toks[i], toks[i + 1]
            total_adj_pairs += 1
            if w1 == w2:
                adj_exact += 1
            elif len(w1) >= 4 and len(w2) >= 4 and edit_distance(w1, w2) == 1:
                adj_dist1 += 1
            if len(w1) >= 3 and len(w2) >= 3 and w1[-2:] == w2[-2:]:
                adj_same_suffix += 1
            if len(w1) >= 3 and len(w2) >= 3 and w1[:2] == w2[:2]:
                adj_same_prefix += 1

            sw1, sw2 = shuf[i], shuf[i + 1]
            if sw1 == sw2:
                null_exact += 1
            elif len(sw1) >= 4 and len(sw2) >= 4 and edit_distance(sw1, sw2) == 1:
                null_dist1 += 1
            if len(sw1) >= 3 and len(sw2) >= 3 and sw1[-2:] == sw2[-2:]:
                null_suf += 1

    out = {
        'gallows_top_line_effect': {
            'para_first_word': gallows_breakdown(line0_words),
            'subsequent_line_first_word': gallows_breakdown(line1p_words),
            'line_interior_words': gallows_breakdown(interior_words),
            'pf_gallows_in_top_line_of_para_pct': round(pf_in_line0, 2),
            'pf_gallows_in_lower_lines_of_para_pct': round(pf_in_line1p, 2),
            'kt_gallows_in_top_line_of_para_pct': round(kt_in_line0, 2),
            'kt_gallows_in_lower_lines_of_para_pct': round(kt_in_line1p, 2),
        },
        'slot_grammar_and_adjacent_harmony': {
            'total_tokens': len(all_tokens),
            'slot_template_coverage_pct': slot_coverage_pct,
            'total_adjacent_pairs': total_adj_pairs,
            'adjacent_exact_repeats': adj_exact,
            'within_line_shuffled_exact_repeats': null_exact,
            'adjacent_edit_dist_1_pairs': adj_dist1,
            'within_line_shuffled_edit_dist_1_pairs': null_dist1,
            'adjacent_same_2char_suffix_pct': round(adj_same_suffix / total_adj_pairs * 100, 2),
            'within_line_shuffled_same_2char_suffix_pct': round(null_suf / total_adj_pairs * 100, 2),
            'adjacent_same_2char_prefix_pct': round(adj_same_prefix / total_adj_pairs * 100, 2),
        },
        'rare_block_label_to_para_matches': block_close_hits[:50],
    }

    Path('data/deep_grammar_analysis.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps(out['gallows_top_line_effect'], indent=2))
    print(json.dumps(out['slot_grammar_and_adjacent_harmony'], indent=2))
    print(f"Found {len(block_close_hits)} rare block-level label->paragraph close matches:")
    for h in block_close_hits[:25]:
        print(" ", h)

if __name__ == '__main__':
    main()
