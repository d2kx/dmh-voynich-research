import json
import re
from collections import Counter, defaultdict
from pathlib import Path

def clean_token(w: str) -> str:
    w = re.sub(r'\[([^:\]]+):[^\]]+\]', r'\1', w)
    w = re.sub(r'\{([^}]+)\}', r'\1', w)
    w = re.sub(r'[@!?;*\'"]', '', w)
    return w.strip()

def strip_affixes(w: str) -> tuple[str, str, str]:
    """Decompose a Voynich word into (prefix, stem, suffix) using common EVA affixes."""
    prefixes = ['qo', 'ch', 'sh', 'cth', 'ckh', 'cph', 'cfh', 'ok', 'ot', 'yk', 'yt', 'da', 'sa', 'so', 'ol', 'or', 'al', 'ar', 'o', 'y', 'd', 's']
    suffixes = ['aiin', 'oiin', 'eiin', 'iin', 'ain', 'edy', 'ody', 'eey', 'ey', 'dy', 'hy', 'ky', 'ly', 'ry', 'ty', 'ol', 'al', 'or', 'ar', 'am', 'om', 'an', 'in', 'y', 'l', 'r', 'm', 'n', 's']
    p_found = ''
    s_found = ''
    rem = w
    for p in prefixes:
        if rem.startswith(p) and len(rem) > len(p) + 1:
            p_found = p
            rem = rem[len(p):]
            break
    for s in suffixes:
        if rem.endswith(s) and len(rem) > len(s):
            s_found = s
            rem = rem[:-len(s)]
            break
    return p_found, rem, s_found

def main():
    zl_path = Path('data/ZL3b-n.txt')
    lines = zl_path.read_text(encoding='utf-8', errors='replace').splitlines()

    folio_meta = {}
    folio_words = defaultdict(list)
    folio_labels = defaultdict(list)
    plant_xrefs = []

    # Positional buckets
    pos_buckets = {
        'para_start': [],
        'line_start': [],
        'line_mid': [],
        'before_drawing': [],
        'after_drawing': [],
        'line_end': [],
        'para_end': [],
        'right_title_Pt': [],
        'labels': [],
    }

    cur_folio = None
    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            cur_folio = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            folio_meta[cur_folio] = kv
            folio_meta[cur_folio]['comments'] = []
            continue

        if cur_folio and raw.startswith('# '):
            c = raw[2:].strip()
            folio_meta[cur_folio]['comments'].append(c)
            if 'Same plant' in c or 'same plant' in c or 'f99' in c or 'f100' in c or 'f101' in c or 'f102' in c or 'f88' in c or 'f89' in c:
                plant_xrefs.append((cur_folio, c))
            continue

        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, loc_num, loc_type, body = m_loc.groups()

        # Remove inline comments <! ... >
        body_nc = re.sub(r'<![^>]*>', '', body)
        is_para_start = '<%>' in body_nc
        is_para_end = '<$>' in body_nc
        body_nc = body_nc.replace('<%>', '').replace('<$>', '')

        # Check if label
        if 'L' in loc_type:
            toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
            toks = [t for t in toks if t and not t.isdigit()]
            for t in toks:
                pos_buckets['labels'].append(t)
                folio_labels[f_id].append((loc_type, t))
                folio_words[f_id].append(t)
            continue

        if loc_type == '=Pt':
            toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
            toks = [t for t in toks if t and not t.isdigit()]
            for t in toks:
                pos_buckets['right_title_Pt'].append(t)
                folio_words[f_id].append(t)
            continue

        if 'P' in loc_type:
            # Split by drawing intrusion <-> first
            segments = body_nc.split('<->')
            seg_tokens = []
            for seg in segments:
                toks = [clean_token(t) for t in re.split(r'[.,\s]+', seg)]
                toks = [t for t in toks if t and not t.isdigit() and '?' not in t]
                seg_tokens.append(toks)
                for t in toks:
                    folio_words[f_id].append(t)

            # Flatten to check line positions
            all_line_toks = [t for seg in seg_tokens for t in seg]
            if not all_line_toks:
                continue

            if is_para_start:
                pos_buckets['para_start'].append(all_line_toks[0])
            else:
                pos_buckets['line_start'].append(all_line_toks[0])

            if is_para_end:
                pos_buckets['para_end'].append(all_line_toks[-1])
            else:
                pos_buckets['line_end'].append(all_line_toks[-1])

            # Check drawing boundaries
            if len(seg_tokens) > 1:
                for s_idx in range(len(seg_tokens) - 1):
                    if seg_tokens[s_idx]:
                        pos_buckets['before_drawing'].append(seg_tokens[s_idx][-1])
                    if seg_tokens[s_idx + 1]:
                        pos_buckets['after_drawing'].append(seg_tokens[s_idx + 1][0])

            # Interior words (not first or last of any segment)
            for seg in seg_tokens:
                if len(seg) > 2:
                    for t in seg[1:-1]:
                        pos_buckets['line_mid'].append(t)

    # 1. Analyze positional morphology (initial char/digraph and final char/digraph)
    pos_report = {}
    for bucket, words in pos_buckets.items():
        n = len(words)
        if n == 0:
            continue
        end_m = sum(1 for w in words if w.endswith('m')) / n * 100
        end_y = sum(1 for w in words if w.endswith('y')) / n * 100
        end_in = sum(1 for w in words if w.endswith('iin') or w.endswith('in')) / n * 100
        end_ol_al = sum(1 for w in words if w.endswith(('ol', 'al', 'or', 'ar'))) / n * 100
        start_qo = sum(1 for w in words if w.startswith('qo')) / n * 100
        start_o = sum(1 for w in words if w.startswith('o') and not w.startswith('qo')) / n * 100
        start_y = sum(1 for w in words if w.startswith('y')) / n * 100
        start_d_s = sum(1 for w in words if w.startswith(('d', 's'))) / n * 100
        has_gallows_init = sum(1 for w in words if re.match(r'^[tkpf]|^c[tkpf]h', w)) / n * 100
        avg_len = sum(len(w) for w in words) / n
        pos_report[bucket] = {
            'count': n,
            'avg_len': round(avg_len, 2),
            'init_gallows_pct': round(has_gallows_init, 1),
            'start_qo_pct': round(start_qo, 1),
            'start_y_pct': round(start_y, 1),
            'start_o_pct': round(start_o, 1),
            'start_d_s_pct': round(start_d_s, 1),
            'end_m_pct': round(end_m, 1),
            'end_y_pct': round(end_y, 1),
            'end_in_pct': round(end_in, 1),
            'end_liquid_pct': round(end_ol_al, 1),
            'top_words': Counter(words).most_common(8),
        }

    # 2. Analyze Labels vs Main Text
    all_para_words = Counter()
    for f_id, words in folio_words.items():
        lbl_set = [w for _, w in folio_labels[f_id]]
        # count paragraph words
    para_word_folios = defaultdict(set)
    for f_id, words in folio_words.items():
        lbl_words = [w for _, w in folio_labels[f_id]]
        # separate para words
    # Let's build clean para_words per folio
    folio_para_words = defaultdict(list)
    for bucket in ['para_start', 'line_start', 'line_mid', 'before_drawing', 'after_drawing', 'line_end', 'para_end']:
        for w in pos_buckets[bucket]:
            all_para_words[w] += 1

    label_words = [w for w in pos_buckets['labels'] if '?' not in w and len(w) >= 2]
    label_counter = Counter(label_words)
    label_in_para = sum(1 for w in label_words if all_para_words[w] > 0)

    # 3. Check Plant Cross-References between Herbal and Pharmaceutical
    xref_results = []
    for f_id, comment in plant_xrefs:
        targets = re.findall(r'f\d+[rv]\d*', comment)
        for t_f in targets:
            if t_f in folio_words and f_id in folio_words:
                w1 = set(w for w in folio_words[f_id] if '?' not in w and len(w) >= 3)
                w2 = set(w for w in folio_words[t_f] if '?' not in w and len(w) >= 3)
                shared = w1 & w2
                # filter out top 50 ultra-common words
                top50 = {w for w, _ in all_para_words.most_common(50)}
                rare_shared = shared - top50
                lbl1 = [w for _, w in folio_labels[f_id]]
                lbl2 = [w for _, w in folio_labels[t_f]]
                # check stem overlap of labels with target folio words
                stems1 = {strip_affixes(w)[1]: w for w in lbl1 if len(strip_affixes(w)[1]) >= 2}
                stems2 = {strip_affixes(w)[1]: w for w in lbl2 if len(strip_affixes(w)[1]) >= 2}
                xref_results.append({
                    'source_folio': f_id,
                    'target_folio': t_f,
                    'comment': comment,
                    'source_labels': lbl1[:10],
                    'target_labels': lbl2[:10],
                    'shared_words_count': len(shared),
                    'rare_shared_words': sorted(list(rare_shared))[:15],
                })

    # 4. Currier Language A vs B & Scribe Hands
    hand_stats = {}
    for f_id, kv in folio_meta.items():
        lang = kv.get('L', '?')
        hand = kv.get('H', '?')
        key = f"Lang_{lang}_Hand_{hand}"
        hand_stats.setdefault(key, []).extend([w for w in folio_words[f_id] if '?' not in w])

    hand_summary = {}
    for key, words in sorted(hand_stats.items()):
        if not words:
            continue
        n = len(words)
        hand_summary[key] = {
            'total_words': n,
            'unique_words': len(set(words)),
            'edy_pct': round(sum(1 for w in words if w.endswith('edy')) / n * 100, 2),
            'aiin_pct': round(sum(1 for w in words if w.endswith('aiin')) / n * 100, 2),
            'qo_pct': round(sum(1 for w in words if w.startswith('qo')) / n * 100, 2),
            'top5': Counter(words).most_common(5),
        }

    results = {
        'positional_morphology': pos_report,
        'label_stats': {
            'total_clean_labels': len(label_words),
            'unique_label_words': len(label_counter),
            'labels_appearing_in_paragraphs': label_in_para,
            'labels_in_paragraphs_pct': round(label_in_para / len(label_words) * 100, 1) if label_words else 0,
            'top_repeated_labels': label_counter.most_common(20),
        },
        'herbal_pharma_xrefs': xref_results,
        'language_and_hands': hand_summary,
    }

    Path('data/structural_analysis.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print("Saved data/structural_analysis.json")
    print("\n--- POSITIONAL MORPHOLOGY SUMMARY ---")
    for k, v in pos_report.items():
        print(f"{k:16s} (n={v['count']:5d}): len={v['avg_len']:.2f}, init_gallows={v['init_gallows_pct']:4.1f}%, qo-={v['start_qo_pct']:4.1f}%, y-={v['start_y_pct']:4.1f}%, -m={v['end_m_pct']:4.1f}%, -y={v['end_y_pct']:4.1f}%, -in={v['end_in_pct']:4.1f}%")

if __name__ == '__main__':
    main()
