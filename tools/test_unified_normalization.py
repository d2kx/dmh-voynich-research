import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

def clean_token(w: str) -> str:
    w = re.sub(r'\[([^:\]]+):[^\]]+\]', r'\1', w)
    w = re.sub(r'\{([^}]+)\}', r'\1', w)
    w = re.sub(r'[@!?;*\'"]', '', w)
    return w.strip()

def voynich_canonical_root(w: str) -> str:
    """
    Apply the 4 empirically discovered Voynich orthographic/morphological equivalence rules:
    1. Proclitic stripping: qo- -> o-, initial y- -> stripped
    2. Top-line gallows allography: p -> t, f -> k (cph -> cth, cfh -> ckh)
    3. Vowel run compression: e+ -> e, i+ -> i, o+ -> o, a+ -> a
    4. Line-end coda neutralization: final -am/-om/-im -> -ar/-or/-ir (or -m -> -r)
    """
    s = w
    if s.startswith('qo') and len(s) > 3:
        s = s[1:]
    elif s.startswith('y') and len(s) > 3:
        s = s[1:]
    # Gallows allographs
    s = s.replace('cph', 'cth').replace('cfh', 'ckh')
    s = s.replace('p', 't').replace('f', 'k')
    # Vowel runs
    s = re.sub(r'e+', 'e', s)
    s = re.sub(r'i+', 'i', s)
    s = re.sub(r'o+', 'o', s)
    s = re.sub(r'a+', 'a', s)
    # Line-final -m neutralization
    if s.endswith('m') and len(s) >= 4:
        s = s[:-1] + 'r'
    return s

def main():
    lines = Path('data/ZL3b-n.txt').read_text(encoding='utf-8', errors='replace').splitlines()

    folio_para = defaultdict(list)
    folio_labels = defaultdict(list)
    folio_lang = {}
    folio_sec = {}
    global_word_counts = Counter()
    global_canon_counts = Counter()

    cur_f = None
    for raw in lines:
        m_h = re.match(r'^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>', raw)
        if m_h:
            cur_f = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            folio_lang[cur_f] = kv.get('L', '?')
            folio_sec[cur_f] = kv.get('I', '?')
            continue
        m_loc = re.match(r'^<(f\d+[rv]\d*)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, lnum, ltype, body = m_loc.groups()
        body_nc = re.sub(r'<![^>]*>', '', body).replace('<%>', '').replace('<$>', '')
        toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
        toks = [t for t in toks if t and not t.isdigit() and '?' not in t]
        for t in toks:
            global_word_counts[t] += 1
            global_canon_counts[voynich_canonical_root(t)] += 1
        if 'L' in ltype:
            folio_labels[f_id].extend(toks)
        elif 'P' in ltype:
            folio_para[f_id].extend(toks)

    folios = [f for f in sorted(folio_labels.keys()) if folio_para[f]]

    # Test canonical root matches between labels on folio f and paragraph words on folio f
    # Specifically look at all labels (len >= 4) and rare labels (canonical root count <= 25 in entire MS)
    all_matches = 0
    rare_matches = 0
    rare_match_examples = []

    folio_para_canon = {f: {voynich_canonical_root(w): w for w in folio_para[f]} for f in folios}

    for f in folios:
        p_map = folio_para_canon[f]
        for lw in folio_labels[f]:
            if len(lw) < 4:
                continue
            clw = voynich_canonical_root(lw)
            if clw in p_map:
                all_matches += 1
                if global_canon_counts[clw] <= 25:
                    rare_matches += 1
                    rare_match_examples.append({
                        'folio': f,
                        'sec': folio_sec[f],
                        'label': lw,
                        'para_word': p_map[clw],
                        'canonical_root': clw,
                        'global_root_freq': global_canon_counts[clw],
                    })

    # Permutation test (1000 trials shuffling paragraphs within same Currier language)
    random.seed(12345)
    null_all = []
    null_rare = []
    for _ in range(1000):
        shuf_map = {}
        for lang in ['A', 'B', '?']:
            flist = [f for f in folios if folio_lang[f] == lang]
            pmaps = [folio_para_canon[f] for f in flist]
            random.shuffle(pmaps)
            for f, pm in zip(flist, pmaps):
                shuf_map[f] = pm
        a_cnt, r_cnt = 0, 0
        for f in folios:
            pm = shuf_map[f]
            for lw in folio_labels[f]:
                if len(lw) < 4:
                    continue
                clw = voynich_canonical_root(lw)
                if clw in pm:
                    a_cnt += 1
                    if global_canon_counts[clw] <= 25:
                        r_cnt += 1
        null_all.append(a_cnt)
        null_rare.append(r_cnt)

    def stats(obs, null_dist):
        mean = sum(null_dist) / len(null_dist)
        sd = math.sqrt(sum((x - mean) ** 2 for x in null_dist) / len(null_dist))
        z = (obs - mean) / sd if sd > 0 else 0
        pval = sum(1 for x in null_dist if x >= obs) / len(null_dist)
        return {'observed': obs, 'null_mean': round(mean, 2), 'null_sd': round(sd, 2), 'z_score': round(z, 2), 'empirical_p': pval}

    res = {
        'total_raw_word_types': len(global_word_counts),
        'total_canonical_root_types': len(global_canon_counts),
        'vocabulary_compression_ratio_pct': round((1 - len(global_canon_counts) / len(global_word_counts)) * 100, 1),
        'all_labels_len4_match_stats': stats(all_matches, null_all),
        'rare_labels_freq25_match_stats': stats(rare_matches, null_rare),
        'rare_canonical_matches': rare_match_examples,
    }

    Path('data/canonical_normalization_test.json').write_text(json.dumps(res, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in res.items() if k != 'rare_canonical_matches'}, indent=2))
    print("\nRare Canonical Matches (Global root count <= 25):")
    for m in rare_match_examples:
        print(f"  {m['folio']} [{m['sec']}]: label='{m['label']}' <-> para='{m['para_word']}' (canon='{m['canonical_root']}', MS_freq={m['global_root_freq']})")

if __name__ == '__main__':
    main()
