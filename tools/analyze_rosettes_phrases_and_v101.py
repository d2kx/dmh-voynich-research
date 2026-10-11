import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from test_unified_normalization import clean_token, voynich_canonical_root


def extract_locus_readings(filepath, target_loci):
    text = Path(filepath).read_text(encoding='utf-8', errors='replace')
    found = {}
    for raw in text.splitlines():
        if raw.startswith('#') or not raw.strip():
            continue
        m = re.match(r'^<(f\d+[rv]\d*\.[^,>]+)(?:,[^>]+)?>\s+(.*)$', raw)
        if m:
            loc, body = m.group(1), m.group(2)
            if loc in target_loci:
                body_nc = re.sub(r'<![^>]*>', '', body)
                found[loc] = body_nc.strip()
    return found


def main():
    lines = Path('data/ZL3b-n.txt').read_text(encoding='utf-8', errors='replace').splitlines()

    folio_meta = {}
    cur_folio = None

    # 1. Check separator type ('.' definite space vs ',' uncertain space) and line position for top bigrams
    target_bigrams = [
        ('s', 'aiin'), ('or', 'aiin'), ('ar', 'aiin'), ('r', 'aiin'),
        ('chol', 'daiin'), ('chol', 'chol'), ('ol', 'shedy'), ('ol', 'chedy'),
        ('shedy', 'qokedy'), ('chedy', 'qokeey'), ('chedy', 'qokain'), ('o', 'l'),
    ]
    bigram_stats = {
        f"{w1} {w2}": {'total': 0, 'dot_sep': 0, 'comma_sep': 0, 'line_start': 0, 'line_mid': 0, 'line_end': 0}
        for w1, w2 in target_bigrams
    }

    # Track Rosettes (f85-f86) words and global canonical frequencies
    global_canon_freq = Counter()
    canon_to_folios_by_sec = defaultdict(lambda: defaultdict(set))
    rosettes_labels = []
    rosettes_ring_and_prose = []

    for raw in lines:
        m_h = re.match(r'^<(f[A-Za-z0-9]+)>\s+<!\s*(.*?)>', raw)
        if m_h:
            cur_folio = m_h.group(1)
            kv = dict(re.findall(r'\$([A-Z])=([^\s>]+)', m_h.group(2)))
            folio_meta[cur_folio] = kv
            continue

        if raw.startswith('#'):
            continue

        m_loc = re.match(r'^<(f[A-Za-z0-9]+)\.([^,>]+),([^>]+)>\s+(.*)$', raw)
        if not m_loc:
            continue
        f_id, lnum, ltype, body = m_loc.groups()
        sec = folio_meta.get(f_id, {}).get('I', '?')

        body_nc = re.sub(r'<![^>]*>', '', body).replace('<%>', '').replace('<$>', '')

        # For bigram separator analysis on P lines:
        if 'P' in ltype:
            # Find tokens and the separator immediately following each token
            parts = re.split(r'([.,\s]+)', body_nc.strip())
            clean_seq = []
            seps = []
            for idx in range(0, len(parts), 2):
                w = clean_token(parts[idx])
                sep = parts[idx + 1] if idx + 1 < len(parts) else ''
                if w and not w.isdigit() and '?' not in w:
                    clean_seq.append(w)
                    seps.append(sep)

            n_w = len(clean_seq)
            for i in range(n_w - 1):
                key = f"{clean_seq[i]} {clean_seq[i+1]}"
                if key in bigram_stats:
                    st = bigram_stats[key]
                    st['total'] += 1
                    if ',' in seps[i]:
                        st['comma_sep'] += 1
                    else:
                        st['dot_sep'] += 1
                    if i == 0:
                        st['line_start'] += 1
                    elif i + 1 == n_w - 1:
                        st['line_end'] += 1
                    else:
                        st['line_mid'] += 1

        toks = [clean_token(t) for t in re.split(r'[.,\s<>\-]+', body_nc)]
        toks = [t for t in toks if t and not t.isdigit() and '?' not in t]
        canons = [voynich_canonical_root(t) for t in toks]

        for t, c in zip(toks, canons):
            global_canon_freq[c] += 1
            canon_to_folios_by_sec[c][sec].add(f"{f_id}.{lnum}:{t}")

        if f_id.startswith(('f85', 'f86', 'fRos')):
            for t, c in zip(toks, canons):
                item = {'locus': f"{f_id}.{lnum}", 'ltype': ltype, 'word': t, 'canon': c}
                if f_id == 'fRos' or 'L' in ltype:
                    rosettes_labels.append(item)
                else:
                    rosettes_ring_and_prose.append(item)

    # 2. Find rare Rosettes (f85/f86) labels and ring words (global freq 2..15, len >= 4)
    # and see which sections they link to!
    rare_rosettes_links = []
    seen_c = set()
    for item in rosettes_labels + rosettes_ring_and_prose:
        c = item['canon']
        if c in seen_c or len(c) < 4 or not (2 <= global_canon_freq[c] <= 12):
            continue
        seen_c.add(c)
        other_secs = {
            s: sorted(list(loci))
            for s, loci in canon_to_folios_by_sec[c].items()
        }
        rare_rosettes_links.append({
            'canon': c,
            'global_freq': global_canon_freq[c],
            'rosettes_locus': item['locus'],
            'rosettes_type': item['ltype'],
            'rosettes_word': item['word'],
            'occurrences_by_section': other_secs,
        })

    # 3. Cross-check smoking-gun loci across ZL3b-n.txt, RF1b-er.txt, IT2a-n.txt, GC2a-n.txt
    smoking_gun_loci = {
        'f99v.31', 'f99v.34',
        'f89r2.5', 'f89r2.22',
        'f75v.13', 'f75v.16', 'f75v.40',
        'f82v.13', 'f82v.37', 'f82v.45', 'f82v.46',
        'f84r.2', 'f84r.11', 'f84r.13', 'f84r.30',
        'f102v1.1', 'f106v.2',
        'f102v2.24', 'f105r.30',
        'f100r.6', 'f115r.1',
    }
    corpora = {
        'ZL3b': 'data/ZL3b-n.txt',
        'RF1b': 'data/RF1b-er.txt',
        'IT2a': 'data/IT2a-n.txt',
        'GC2a_v101': 'data/GC2a-n.txt',
    }
    cross_corpus = {name: extract_locus_readings(path, smoking_gun_loci) for name, path in corpora.items()}

    out = {
        'bigram_separator_and_position': bigram_stats,
        'rosettes_label_count': len(rosettes_labels),
        'rosettes_prose_and_ring_count': len(rosettes_ring_and_prose),
        'rare_rosettes_links': rare_rosettes_links[:40],
        'cross_corpus_verification': cross_corpus,
    }
    Path('data/rosettes_phrases_and_v101.json').write_text(json.dumps(out, indent=2), encoding='utf-8')

    print("=== BIGRAM SEPARATOR ('.' Definite vs ',' Uncertain) & POSITION ===")
    for k, st in bigram_stats.items():
        if st['total'] > 0:
            c_pct = 100 * st['comma_sep'] / st['total']
            e_pct = 100 * st['line_end'] / st['total']
            s_pct = 100 * st['line_start'] / st['total']
            print(f"  {k:14s} (n={st['total']:2d}): dot={st['dot_sep']:2d}, comma={st['comma_sep']:2d} ({c_pct:4.1f}% uncertain) | start={s_pct:4.1f}%, mid={100-s_pct-e_pct:4.1f}%, end={e_pct:4.1f}%")

    print(f"\n=== ROSETTES (f85-f86) RARE VOCABULARY LINKS (n={len(rare_rosettes_links)}) ===")
    for r in rare_rosettes_links[:18]:
        print(f"  {r['rosettes_locus']} ({r['rosettes_type']}) '{r['rosettes_word']}' (canon={r['canon']}, freq={r['global_freq']}): {r['occurrences_by_section']}")


if __name__ == '__main__':
    main()
