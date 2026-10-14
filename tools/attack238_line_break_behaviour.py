"""Attack 238 - Line-break behaviour in Voynichese.

Research question: is the written line a functional unit, and are words ever
split (hyphenated) across line breaks?

Tests (all on running-text lines: unit == 'P', excluding right-justified
titles unit_sub == 't'):

 T1  Line-final vs line-internal word-final glyphs; line-initial vs
     line-internal word-initial glyphs. Stratified Mantel-Haenszel odds ratios
     per glyph (strata = Currier language x section), per-stratum chi-square /
     Cramer's V / total-variation distance, and a within-line word-order
     permutation null (keeps every line's vocabulary, destroys position).
     Repeated for paragraph-internal lines only.
 T2  Split-word test: concat(last word of line i, first word of line i+1)
     attested as a corpus word type? vs (a) permutation null re-pairing the
     line-initial words within the same language x section stratum and
     (b) within-line adjacent word pairs, reweighted to the same strata.
     Plus hapax / length rates of line-final and line-initial words.
 T3  Line-length compensation: glyph length by position (1,2,3 from start;
     -1,-2,-3 from end), end-vs-start correlation with line fullness, and
     whether -m/-g line endings track fullness (space-saving abbreviation?).
 T4  Cross-line dependency: excess mutual information (observed - shuffled)
     for last(line i) -> first(line i+1) vs within-line adjacent pairs,
     on word types and on (final glyph, initial glyph) junctures.
 T5  Robustness: T1/T2/T4 on IT2a-n (Takahashi, EVA) and GC2a-n (Glen
     Claston v101 alphabet, char-level glyphs).

Output: data/attack238_line_break_behaviour.json
Usage:  python tools/attack238_line_break_behaviour.py [--perms N]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voynich_corpus import ROOT, load_lines, paragraphs  # noqa: E402

OUT = os.path.join(ROOT, 'data', 'attack238_line_break_behaviour.json')
TRANSLITS = {
    'ZL3b': ('data/ZL3b-n.txt', 'eva'),
    'IT2a': ('data/IT2a-n.txt', 'eva'),
    'GC2a': ('data/GC2a-n.txt', 'v101'),
}
EVA_MULTI = ('cth', 'ckh', 'cph', 'cfh', 'ch', 'sh')


# ----------------------------------------------------------------- glyphs
def glyphs(w, alpha):
    if alpha != 'eva':
        return list(w)
    out, i = [], 0
    while i < len(w):
        for m in EVA_MULTI:
            if w.startswith(m, i):
                out.append(m)
                i += len(m)
                break
        else:
            out.append(w[i])
            i += 1
    return out


def first_glyph(w, alpha):
    return glyphs(w, alpha)[0]


def last_glyph(w, alpha):
    return w[-1]


def is_clean(w):
    return bool(w) and not any(c in w for c in "?'*")


# ------------------------------------------------------------- statistics
def gammq(a, x):
    """Regularised upper incomplete gamma Q(a, x) (Numerical Recipes)."""
    if x <= 0:
        return 1.0
    if x < a + 1:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-14:
                break
        return max(0.0, 1.0 - s * math.exp(-x + a * math.log(x) - math.lgamma(a)))
    b = x + 1 - a
    c = 1e300
    d = 1 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-14:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_sf(x, df):
    return gammq(df / 2.0, x / 2.0) if df > 0 else 1.0


def chi2_table(c1, c2, min_exp=5):
    """Chi-square of two Counters (categories pooled into OTHER if rare)."""
    n1, n2 = sum(c1.values()), sum(c2.values())
    if n1 == 0 or n2 == 0:
        return None
    N = n1 + n2
    cats = set(c1) | set(c2)
    tot = {k: c1[k] + c2[k] for k in cats}
    keep = [k for k in cats if tot[k] * min(n1, n2) / N >= min_exp]
    other1 = sum(c1[k] for k in cats if k not in keep)
    other2 = sum(c2[k] for k in cats if k not in keep)
    rows = [(c1[k], c2[k]) for k in keep]
    if other1 + other2 > 0:
        rows.append((other1, other2))
    chi = 0.0
    for a, b in rows:
        t = a + b
        e1, e2 = t * n1 / N, t * n2 / N
        chi += (a - e1) ** 2 / e1 + (b - e2) ** 2 / e2
    df = len(rows) - 1
    v = math.sqrt(chi / N) if N else 0.0  # 2 x k table -> min(r,c)-1 = 1
    tvd = 0.5 * sum(abs(c1[k] / n1 - c2[k] / n2) for k in cats)
    return {'n1': n1, 'n2': n2, 'chi2': chi, 'df': df, 'p': chi2_sf(chi, df),
            'cramers_v': v, 'tvd': tvd}


def mantel_haenszel(tables):
    """tables: list of (a,b,c,d) = (exposed&case, exposed&noncase, unexp&case, unexp&noncase).
    Returns MH odds ratio with Robins-Breslow-Greenland 95% CI and MH chi2 p."""
    sR = sS = sPR = sPSQR = sQS = 0.0
    sa = sea = sva = 0.0
    for a, b, c, d in tables:
        n = a + b + c + d
        if n < 2:
            continue
        R, S = a * d / n, b * c / n
        P, Q = (a + d) / n, (b + c) / n
        sR += R
        sS += S
        sPR += P * R
        sPSQR += P * S + Q * R
        sQS += Q * S
        sa += a
        sea += (a + b) * (a + c) / n
        sva += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    if sR == 0 or sS == 0:
        return {'or': None}
    OR = sR / sS
    var = sPR / (2 * sR ** 2) + sPSQR / (2 * sR * sS) + sQS / (2 * sS ** 2)
    se = math.sqrt(var)
    chi = (abs(sa - sea) - 0.5) ** 2 / sva if sva > 0 else 0.0
    return {'or': OR, 'ci95': [OR * math.exp(-1.96 * se), OR * math.exp(1.96 * se)],
            'mh_chi2': chi, 'p': chi2_sf(chi, 1), 'observed': sa, 'expected': sea}


def mutual_info(pairs):
    n = len(pairs)
    if n == 0:
        return 0.0
    cx, cy, cxy = Counter(), Counter(), Counter()
    for x, y in pairs:
        cx[x] += 1
        cy[y] += 1
        cxy[(x, y)] += 1
    mi = 0.0
    for (x, y), c in cxy.items():
        mi += c / n * math.log2(c * n / (cx[x] * cy[y]))
    return mi


def mean(xs):
    return sum(xs) / len(xs) if xs else float('nan')


def sd(xs):
    if len(xs) < 2:
        return float('nan')
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def zscore(obs, null):
    s = sd(null)
    return (obs - mean(null)) / s if s and s > 0 else float('nan')


def rank(xs):
    idx = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and xs[idx[j + 1]] == xs[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            r[idx[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(x, y):
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else float('nan')


def spearman(x, y):
    return pearson(rank(x), rank(y))


def perm_p_upper(obs, null):
    return (1 + sum(1 for v in null if v >= obs)) / (1 + len(null))


def perm_p_lower(obs, null):
    return (1 + sum(1 for v in null if v <= obs)) / (1 + len(null))


# ------------------------------------------------------------ corpus prep
def build(path, alpha):
    lines = load_lines(os.path.join(ROOT, path))
    freq = Counter(w for l in lines for w in l.words if is_clean(w))
    paras = []
    for p in paragraphs(lines):
        p = [l for l in p if l.unit == 'P' and l.unit_sub != 't' and l.words]
        if p:
            paras.append(p)
    recs = []  # one record per line
    for pi, p in enumerate(paras):
        m = len(p)
        for li, l in enumerate(p):
            role = 'para_first' if li == 0 else ('para_last' if li == m - 1 else 'para_internal')
            if m == 1:
                role = 'para_single'
            flank = set()
            for i in l.intrusion_after:
                flank.add(i)
                flank.add(i + 1)
            recs.append({'para': pi, 'li': li, 'm': m, 'role': role, 'line': l,
                         'words': list(l.words), 'flank': flank,
                         'stratum': (l.lang, l.section), 'lang': l.lang,
                         'section': l.section, 'locus': l.locus})
    return lines, paras, recs, freq


# --------------------------------------------------------------------- T1
def t1_counts(recs, alpha, order=None, which='final', roles=None):
    """Return {stratum: (Counter_edge, Counter_internal)}."""
    out = defaultdict(lambda: (Counter(), Counter()))
    for r in recs:
        if roles and r['role'] not in roles:
            continue
        ws = order[id(r)] if order else r['words']
        n = len(ws)
        if n < 3 or r['lang'] not in 'AB':
            continue
        ce, ci = out[r['stratum']]
        edge = n - 1 if which == 'final' else 0
        fn = last_glyph if which == 'final' else first_glyph
        for i, w in enumerate(ws):
            if not is_clean(w):
                continue
            if i == edge:
                ce[fn(w, alpha)] += 1
            elif 0 < i < n - 1 and i not in r['flank']:
                ci[fn(w, alpha)] += 1
    return out


def stratified_chi(counts):
    tot = 0.0
    for ce, ci in counts.values():
        res = chi2_table(ce, ci)
        if res:
            tot += res['chi2']
    return tot


def t1_analysis(recs, alpha, perms, rng, which, roles, top=8):
    counts = t1_counts(recs, alpha, which=which, roles=roles)
    pooled_e, pooled_i = Counter(), Counter()
    for ce, ci in counts.values():
        pooled_e.update(ce)
        pooled_i.update(ci)
    glyph_set = [g for g, c in (pooled_e + pooled_i).most_common() if c >= 30]
    per_glyph = {}
    for g in glyph_set:
        tabs = []
        for ce, ci in counts.values():
            a, b = ce[g], sum(ce.values()) - ce[g]
            c, d = ci[g], sum(ci.values()) - ci[g]
            tabs.append((a, b, c, d))
        mh = mantel_haenszel(tabs)
        mh['edge_rate'] = pooled_e[g] / max(1, sum(pooled_e.values()))
        mh['internal_rate'] = pooled_i[g] / max(1, sum(pooled_i.values()))
        mh['edge_n'] = pooled_e[g]
        per_glyph[g] = mh
    by_lang = {}
    for lang in 'AB':
        ce, ci = Counter(), Counter()
        for (lg, sec), (a, b) in counts.items():
            if lg == lang:
                ce.update(a)
                ci.update(b)
        by_lang[lang] = chi2_table(ce, ci)
    by_stratum = {f'{k[0]}/{k[1]}': chi2_table(*v) for k, v in sorted(counts.items())
                  if sum(v[0].values()) >= 40}
    obs = stratified_chi(counts)
    # within-line permutation null
    null = []
    elig = [r for r in recs if (not roles or r['role'] in roles)]
    for _ in range(perms):
        order = {}
        for r in elig:
            ws = r['words'][:]
            rng.shuffle(ws)
            order[id(r)] = ws
        null.append(stratified_chi(t1_counts(elig, alpha, order=order, which=which, roles=roles)))
    enriched = sorted([(g, v) for g, v in per_glyph.items() if v.get('or')],
                      key=lambda kv: -kv[1]['or'])
    return {
        'n_edge': sum(pooled_e.values()), 'n_internal': sum(pooled_i.values()),
        'pooled': chi2_table(pooled_e, pooled_i),
        'by_lang': by_lang,
        'by_stratum': by_stratum,
        'stratified_chi2_sum': obs,
        'perm_null_mean': mean(null), 'perm_null_sd': sd(null),
        'perm_z': zscore(obs, null), 'perm_p': perm_p_upper(obs, null), 'perms': perms,
        'per_glyph_mh': per_glyph,
        'top_enriched': [g for g, _ in enriched[:top]],
        'top_depleted': [g for g, _ in enriched[::-1][:top]],
    }


# --------------------------------------------------------------------- T2
def breaks(paras_recs):
    """Paragraph-internal line breaks: (a, b, stratum, locus_i, locus_j, rec_i, rec_j)."""
    out = []
    by_para = defaultdict(list)
    for r in paras_recs:
        by_para[r['para']].append(r)
    for pi, rs in by_para.items():
        rs.sort(key=lambda r: r['li'])
        for r1, r2 in zip(rs, rs[1:]):
            a, b = r1['words'][-1], r2['words'][0]
            if r1['lang'] not in 'AB' or not (is_clean(a) and is_clean(b)):
                continue
            out.append({'a': a, 'b': b, 'stratum': r1['stratum'], 'locus_a': r1['locus'],
                        'locus_b': r2['locus'], 'role_a': r1['role'], 'role_b': r2['role']})
    return out


def internal_pairs(recs):
    out = defaultdict(list)
    for r in recs:
        ws = r['words']
        if r['lang'] not in 'AB':
            continue
        for i in range(len(ws) - 1):
            if i in r['line'].intrusion_after:
                continue
            a, b = ws[i], ws[i + 1]
            if is_clean(a) and is_clean(b):
                out[r['stratum']].append((a, b))
    return out


def attested(a, b, freq, thr):
    return freq.get(a + b, 0) >= thr


def t2_analysis(recs, freq, alpha, perms, rng):
    br = breaks(recs)
    res = {'n_breaks': len(br)}
    strata = defaultdict(list)
    for i, x in enumerate(br):
        strata[x['stratum']].append(i)
    ipairs = internal_pairs(recs)
    for thr in (1, 2):
        obs_hits = [attested(x['a'], x['b'], freq, thr) for x in br]
        obs = sum(obs_hits) / len(br)
        null = []
        bs = [x['b'] for x in br]
        for _ in range(perms):
            nb = bs[:]
            for st, idx in strata.items():
                vals = [bs[i] for i in idx]
                rng.shuffle(vals)
                for i, v in zip(idx, vals):
                    nb[i] = v
            null.append(sum(attested(x['a'], nb[i], freq, thr) for i, x in enumerate(br)) / len(br))
        # within-line pairs reweighted to break strata
        w_rate = 0.0
        for st, idx in strata.items():
            ps = ipairs.get(st, [])
            if ps:
                rate = sum(attested(a, b, freq, thr) for a, b in ps) / len(ps)
            else:
                rate = 0.0
            w_rate += rate * len(idx) / len(br)
        res[f'freq_ge_{thr}'] = {
            'observed_hits': sum(obs_hits), 'observed_rate': obs,
            'null_reshuffle_rate': mean(null), 'null_sd': sd(null),
            'z': zscore(obs, null), 'p_upper': perm_p_upper(obs, null),
            'ratio_obs_over_null': obs / mean(null) if mean(null) else None,
            'within_line_pair_rate_reweighted': w_rate,
            'ratio_obs_over_within_line': obs / w_rate if w_rate else None,
        }
    # hapax-fragment conditional: a or b is a hapax and a+b attested (freq>=2)
    def frag(a, b):
        return (freq[a] == 1 or freq[b] == 1) and freq.get(a + b, 0) >= 2
    obs_f = sum(frag(x['a'], x['b']) for x in br)
    n_hapax_side = sum(1 for x in br if freq[x['a']] == 1 or freq[x['b']] == 1)
    w_f = w_n = 0
    for ps in ipairs.values():
        for a, b in ps:
            if freq[a] == 1 or freq[b] == 1:
                w_n += 1
                w_f += frag(a, b)
    res['hapax_fragment'] = {
        'breaks_with_hapax_side': n_hapax_side, 'breaks_hapax_and_concat_attested': obs_f,
        'rate_given_hapax_side': obs_f / n_hapax_side if n_hapax_side else None,
        'within_line_pairs_with_hapax_side': w_n, 'within_line_hapax_and_concat_attested': w_f,
        'within_line_rate_given_hapax_side': w_f / w_n if w_n else None,
    }
    # candidate list (strong split candidates)
    cands = []
    for x in br:
        c = x['a'] + x['b']
        fc = freq.get(c, 0)
        if fc >= 2:
            score = fc / ((freq[x['a']] + 1) * (freq[x['b']] + 1))
            cands.append({**x, 'stratum': '/'.join(x['stratum']), 'concat': c, 'freq_concat': fc,
                          'freq_a': freq[x['a']], 'freq_b': freq[x['b']], 'score': score})
    cands.sort(key=lambda d: -d['score'])
    res['top_candidates'] = cands[:25]
    res['n_candidates_freq_ge_2'] = len(cands)
    return res


def position_profile(recs, freq, alpha, roles=('para_internal',), min_n=7):
    """Mean glyph length and hapax rate by position (1,2,3 / -3,-2,-1 / interior), per language."""
    out = {}
    for lang in ('A', 'B', 'all'):
        pos = defaultdict(list)
        hap = defaultdict(list)
        for r in recs:
            if r['role'] not in roles or (lang != 'all' and r['lang'] != lang) or r['lang'] not in 'AB':
                continue
            ws = r['words']
            n = len(ws)
            if n < min_n:
                continue
            for i, w in enumerate(ws):
                if not is_clean(w):
                    continue
                key = (f'+{i + 1}' if i < 3 else (f'-{n - i}' if i >= n - 3 else 'mid'))
                pos[key].append(len(glyphs(w, alpha)))
                hap[key].append(1 if freq[w] == 1 else 0)
        out[lang] = {k: {'n': len(v), 'mean_glyphs': mean(v), 'hapax_rate': mean(hap[k])}
                     for k, v in sorted(pos.items())}
    return out


def position_perm_test(recs, freq, alpha, perms, rng, roles=('para_internal',), min_n=3):
    """Within-line permutation: are line-final / line-initial words shorter or more often
    hapax than expected from the line's own vocabulary? Stratified by language."""
    res = {}
    for lang in 'AB':
        rs = [r for r in recs if r['role'] in roles and r['lang'] == lang and len(r['words']) >= min_n]

        def stats(get):
            Lf, Li, Hf, Hi = [], [], [], []
            for r in rs:
                ws = get(r)
                f, s = ws[-1], ws[0]
                if is_clean(f):
                    Lf.append(len(glyphs(f, alpha)))
                    Hf.append(freq[f] == 1)
                if is_clean(s):
                    Li.append(len(glyphs(s, alpha)))
                    Hi.append(freq[s] == 1)
            return mean(Lf), mean(Li), mean(Hf), mean(Hi)
        obs = stats(lambda r: r['words'])
        nulls = [[], [], [], []]
        for _ in range(perms):
            sh = {}
            for r in rs:
                ws = r['words'][:]
                rng.shuffle(ws)
                sh[id(r)] = ws
            s = stats(lambda r: sh[id(r)])
            for k in range(4):
                nulls[k].append(s[k])
        names = ['final_len', 'initial_len', 'final_hapax', 'initial_hapax']
        res[lang] = {'n_lines': len(rs)}
        for k, nm in enumerate(names):
            res[lang][nm] = {'observed': obs[k], 'null_mean': mean(nulls[k]),
                             'null_sd': sd(nulls[k]), 'z': zscore(obs[k], nulls[k]),
                             'diff': obs[k] - mean(nulls[k])}
    return res


# --------------------------------------------------------------------- T3
def t3_compensation(recs, paras, alpha, rng, boots=1000):
    out = {}
    for lang in ('A', 'B'):
        rows = []
        by_para = defaultdict(list)
        for r in recs:
            if (r['role'] == 'para_internal' and r['lang'] == lang and len(r['words']) >= 4
                    and not r['line'].intrusion_after and all(is_clean(w) for w in r['words'])):
                by_para[r['para']].append(r)
        for pi, rs in by_para.items():
            if len(rs) < 2:
                continue
            L = [[len(glyphs(w, alpha)) for w in r['words']] for r in rs]
            tot = [sum(x) + len(x) - 1 for x in L]
            rest_last = [t - x[-1] for t, x in zip(tot, L)]
            rest_first = [t - x[0] for t, x in zip(tot, L)]
            mid_idx = [len(x) // 2 for x in L]
            rest_mid = [t - x[m] for t, x, m in zip(tot, L, mid_idx)]
            mrl, mrf, mrm = mean(rest_last), mean(rest_first), mean(rest_mid)
            for k, r in enumerate(rs):
                rows.append({'last': L[k][-1], 'first': L[k][0], 'mid': L[k][mid_idx[k]],
                             'rl': rest_last[k] - mrl, 'rf': rest_first[k] - mrf,
                             'rm': rest_mid[k] - mrm, 'tot': tot[k],
                             'last_m': r['words'][-1][-1] in ('m', 'g') if alpha == 'eva' else None})
        if len(rows) < 30:
            continue

        def cors(rs):
            return (spearman([x['last'] for x in rs], [x['rl'] for x in rs]),
                    spearman([x['first'] for x in rs], [x['rf'] for x in rs]),
                    spearman([x['mid'] for x in rs], [x['rm'] for x in rs]))
        cl, cf, cm = cors(rows)
        diffs = []
        for _ in range(boots):
            smp = [rows[rng.randrange(len(rows))] for _ in rows]
            a, b, _c = cors(smp)
            diffs.append(a - b)
        diffs.sort()
        res = {'n_lines': len(rows), 'spearman_last_vs_rest': cl, 'spearman_first_vs_rest': cf,
               'spearman_mid_vs_rest': cm, 'diff_last_minus_first': cl - cf,
               'diff_ci95': [diffs[int(0.025 * boots)], diffs[int(0.975 * boots)]],
               'line_total_glyphs_mean': mean([x['tot'] for x in rows]),
               'line_total_glyphs_cv': sd([x['tot'] for x in rows]) / mean([x['tot'] for x in rows])}
        if alpha == 'eva':
            m_rows = [x['rl'] for x in rows if x['last_m']]
            o_rows = [x['rl'] for x in rows if not x['last_m']]
            res['last_m_or_g'] = {'n': len(m_rows), 'mean_rest_dev_if_m': mean(m_rows),
                                  'mean_rest_dev_otherwise': mean(o_rows),
                                  'mann_whitney_z': mann_whitney_z(m_rows, o_rows)}
            # fullness quartiles
            srt = sorted(rows, key=lambda x: x['rl'])
            q = len(srt) // 4
            res['m_rate_by_rest_fullness_quartile'] = [
                mean([1 if x['last_m'] else 0 for x in srt[i * q:(i + 1) * q if i < 3 else len(srt)]])
                for i in range(4)]
        out[lang] = res
    # -m/-g rate at line end: para-internal lines vs paragraph-final lines (free space)
    if alpha == 'eva':
        cmp = {}
        for lang in 'AB':
            d = {}
            for role in ('para_first', 'para_internal', 'para_last'):
                ws = [r['words'][-1] for r in recs if r['role'] == role and r['lang'] == lang
                      and is_clean(r['words'][-1])]
                d[role] = {'n': len(ws), 'rate_m_or_g': mean([1 if w[-1] in 'mg' else 0 for w in ws]),
                           'rate_m': mean([1 if w[-1] == 'm' else 0 for w in ws]),
                           'mean_len_last_word': mean([len(glyphs(w, alpha)) for w in ws])}
            cmp[lang] = d
        out['line_end_m_by_line_role'] = cmp
    return out


def mann_whitney_z(x, y):
    if not x or not y:
        return float('nan')
    allv = x + y
    r = rank(allv)
    R1 = sum(r[:len(x)])
    n1, n2 = len(x), len(y)
    U = R1 - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    s = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    return (U - mu) / s


# --------------------------------------------------------------------- T4
def t4_mi(recs, alpha, perms, rng, subsamples=10):
    br = breaks(recs)
    by_stratum_pairs = defaultdict(list)
    start_pairs, end_pairs, mid_pairs = [], [], []
    for r in recs:
        ws = r['words']
        if r['lang'] not in 'AB':
            continue
        n = len(ws)
        if n < 5:
            continue
        intr = set(r['line'].intrusion_after)
        for i in range(n - 1):
            if i in intr or not (is_clean(ws[i]) and is_clean(ws[i + 1])):
                continue
            item = (ws[i], ws[i + 1], r['stratum'])
            if i == 0:
                start_pairs.append(item)
            elif i == n - 2:
                end_pairs.append(item)
            else:
                mid_pairs.append(item)
    cross = [(x['a'], x['b'], x['stratum']) for x in br]
    feats = {
        'word_type': lambda a, b: (a, b),
        'final_glyph_x_initial_glyph': lambda a, b: (last_glyph(a, alpha), first_glyph(b, alpha)),
    }
    N = len(cross)

    def excess(items, feat):
        pairs = [feat(a, b) for a, b, _ in items]
        obs = mutual_info(pairs)
        strata = defaultdict(list)
        for i, (_, _, st) in enumerate(items):
            strata[st].append(i)
        null = []
        ys = [p[1] for p in pairs]
        for _ in range(perms):
            ny = ys[:]
            for idx in strata.values():
                v = [ys[i] for i in idx]
                rng.shuffle(v)
                for i, y in zip(idx, v):
                    ny[i] = y
            null.append(mutual_info([(p[0], y) for p, y in zip(pairs, ny)]))
        return obs, mean(null), sd(null)
    out = {'n_cross_line_pairs': N}
    for fname, feat in feats.items():
        d = {}
        o, nm, ns = excess(cross, feat)
        d['cross_line'] = {'n': N, 'mi': o, 'null_mi': nm, 'excess_mi': o - nm,
                           'z': (o - nm) / ns if ns else None}
        for label, items in (('within_line_start_pair', start_pairs),
                             ('within_line_end_pair', end_pairs),
                             ('within_line_interior', mid_pairs)):
            exs, zs = [], []
            for _ in range(subsamples):
                smp = rng.sample(items, min(N, len(items)))
                o, nm, ns = excess(smp, feat)
                exs.append(o - nm)
                zs.append((o - nm) / ns if ns else 0.0)
            d[label] = {'n_pool': len(items), 'n_sub': min(N, len(items)),
                        'excess_mi_mean': mean(exs), 'z_mean': mean(zs)}
        d['ratio_cross_over_interior_excess'] = (d['cross_line']['excess_mi'] /
                                                 d['within_line_interior']['excess_mi_mean']
                                                 if d['within_line_interior']['excess_mi_mean'] else None)
        out[fname] = d
    # juncture detail: P(initial glyph | final glyph) cross-line vs interior
    if alpha == 'eva':
        def cond(items):
            c = defaultdict(Counter)
            for a, b, _ in items:
                c[last_glyph(a, alpha)][first_glyph(b, alpha)] += 1
            return c
        cc, ci = cond(cross), cond(mid_pairs)
        jt = {}
        for fg in ('y', 'n', 'l', 'r', 'm', 'o', 's'):
            for ig in ('q', 'ch', 'sh', 'o', 'd', 'y', 's', 'p', 't', 'k'):
                nc, ni = sum(cc[fg].values()), sum(ci[fg].values())
                if nc >= 30:
                    jt[f'-{fg} -> {ig}-'] = {'cross_rate': cc[fg][ig] / nc,
                                             'interior_rate': ci[fg][ig] / ni if ni else None,
                                             'n_cross': nc}
        out['juncture_table'] = jt
    return out


# ------------------------------------------------------- follow-up tests
def t2b_fragment_tests(recs, freq, alpha, perms, rng):
    """Follow-ups to T2 targeting *rare* split words whose concatenation would be unattested.

    (a) Do hapax line-final and hapax line-initial words co-occur at the same break more
        than expected (a split rare word would leave two hapax fragments)?
    (b) Fragment shape: is a hapax line-final word more often a proper *prefix* of an
        attested type (freq>=2) than an interior hapax is? Is a hapax line-initial word more
        often a proper *suffix* of an attested type?
    (c) Hapax excess at line end after removing -m/-g endings; at line start after removing
        gallows/p/f-initial words (para-internal lines only).
    """
    out = {}
    br = breaks(recs)
    strata = defaultdict(list)
    for i, x in enumerate(br):
        strata[x['stratum']].append(i)
    ha = [freq[x['a']] == 1 for x in br]
    hb = [freq[x['b']] == 1 for x in br]
    obs = sum(1 for p, q in zip(ha, hb) if p and q)
    null = []
    for _ in range(perms):
        nb = hb[:]
        for idx in strata.values():
            v = [hb[i] for i in idx]
            rng.shuffle(v)
            for i, y in zip(idx, v):
                nb[i] = y
        null.append(sum(1 for p, q in zip(ha, nb) if p and q))
    out['both_sides_hapax'] = {'observed': obs, 'null_mean': mean(null), 'null_sd': sd(null),
                               'z': zscore(obs, null), 'ratio': obs / mean(null) if mean(null) else None,
                               'n_breaks': len(br), 'n_a_hapax': sum(ha), 'n_b_hapax': sum(hb)}
    att = [w for w, c in freq.items() if c >= 2]
    prefixes, suffixes = set(), set()
    for w in att:
        for k in range(1, len(w)):
            prefixes.add(w[:k])
            suffixes.add(w[k:])
    cats = {'final': [], 'initial': [], 'interior': []}
    for r in recs:
        if r['role'] != 'para_internal' or r['lang'] not in 'AB':
            continue
        ws = r['words']
        n = len(ws)
        if n < 3:
            continue
        for i, w in enumerate(ws):
            if not is_clean(w) or freq[w] != 1:
                continue
            key = 'final' if i == n - 1 else ('initial' if i == 0 else 'interior')
            cats[key].append(w)
    shape = {}
    for k, ws in cats.items():
        shape[k] = {'n_hapax': len(ws),
                    'frac_proper_prefix_of_attested': mean([1 if w in prefixes else 0 for w in ws]),
                    'frac_proper_suffix_of_attested': mean([1 if w in suffixes else 0 for w in ws]),
                    'mean_glyphs': mean([len(glyphs(w, alpha)) for w in ws])}
    out['hapax_fragment_shape_para_internal'] = shape
    if alpha == 'eva':
        res = {}
        for lang in 'AB':
            f_all = f_h = i_all = i_h = n_all = n_h = 0
            for r in recs:
                if r['role'] != 'para_internal' or r['lang'] != lang or len(r['words']) < 3:
                    continue
                ws = r['words']
                for i, w in enumerate(ws):
                    if not is_clean(w):
                        continue
                    h = freq[w] == 1
                    if i == len(ws) - 1:
                        if w[-1] not in 'mg':
                            f_all += 1
                            f_h += h
                    elif i == 0:
                        if first_glyph(w, alpha) not in ('p', 'f', 't', 'k'):
                            i_all += 1
                            i_h += h
                    elif w[-1] not in 'mg':
                        n_all += 1
                        n_h += h
            res[lang] = {'final_non_mg_hapax_rate': f_h / f_all if f_all else None, 'n_final': f_all,
                         'initial_non_gallows_hapax_rate': i_h / i_all if i_all else None, 'n_initial': i_all,
                         'interior_non_mg_hapax_rate': n_h / n_all if n_all else None, 'n_interior': n_all}
        out['hapax_rate_controls_para_internal'] = res
    return out


def t3b_margin_tests(recs, freq, alpha):
    """(d) Paragraph-final lines that reach the margin vs. short paragraph-final lines:
    -m/-g rate and last-word length. (e) Line-initial 'strip' test: after removing the
    first glyph, is the remainder an attested word (freq>=5) more often for line-initial
    words than for interior words with the same first glyph?"""
    out = {}
    by_para = defaultdict(list)
    for r in recs:
        by_para[r['para']].append(r)
    groups = defaultdict(lambda: defaultdict(list))
    for pi, rs in by_para.items():
        rs.sort(key=lambda r: r['li'])
        if len(rs) < 3:
            continue
        lang = rs[0]['lang']
        if lang not in 'AB':
            continue
        tot = lambda r: sum(len(glyphs(w, alpha)) for w in r['words']) + len(r['words']) - 1
        internal = sorted(tot(r) for r in rs[1:-1] if not r['line'].intrusion_after)
        if not internal:
            continue
        med = internal[len(internal) // 2]
        last = rs[-1]
        w = last['words'][-1]
        if not is_clean(w) or last['line'].intrusion_after:
            continue
        ratio = tot(last) / med if med else 0
        g = 'near_full_ge_0.85' if ratio >= 0.85 else ('short_le_0.5' if ratio <= 0.5 else 'medium')
        groups[lang][g].append(w)
    for lang, gs in groups.items():
        out.setdefault('para_last_line_by_fullness', {})[lang] = {
            g: {'n': len(ws), 'rate_m_or_g': mean([1 if w[-1] in 'mg' else 0 for w in ws]),
                'mean_len_last_word': mean([len(glyphs(w, alpha)) for w in ws])}
            for g, ws in sorted(gs.items())}
    strip = defaultdict(lambda: {'initial': [0, 0], 'interior': [0, 0]})
    tabs = defaultdict(list)
    for r in recs:
        if r['role'] != 'para_internal' or r['lang'] not in 'AB' or len(r['words']) < 3:
            continue
        ws = r['words']
        for i, w in enumerate(ws):
            if not is_clean(w) or i == len(ws) - 1:
                continue
            g = glyphs(w, alpha)
            if len(g) < 2:
                continue
            rest = w[len(g[0]):]
            hit = freq.get(rest, 0) >= 5
            key = 'initial' if i == 0 else 'interior'
            cell = strip[(r['lang'], g[0])][key]
            cell[0] += hit
            cell[1] += 1
    per = {}
    for (lang, g0), d in sorted(strip.items()):
        a, n1 = d['initial']
        c, n2 = d['interior']
        tabs['all'].append((a, n1 - a, c, n2 - c))
        if n1 >= 20:
            per[f'{lang}:{g0}-'] = {'initial_rate': a / n1, 'n_initial': n1,
                                    'interior_rate': c / n2 if n2 else None, 'n_interior': n2}
    out['line_initial_strip_test'] = {'mh_stratified_by_lang_and_first_glyph': mantel_haenszel(tabs['all']),
                                      'per_first_glyph': per}
    return out


def t4b_juncture_by_lang(recs, alpha, perms, rng):
    out = {}
    for lang in 'AB':
        sub = [r for r in recs if r['lang'] == lang]
        res = t4_mi(sub, alpha, perms, rng, subsamples=5)
        out[lang] = {'n_cross': res['n_cross_line_pairs'],
                     'glyph_cross_excess': res['final_glyph_x_initial_glyph']['cross_line'],
                     'glyph_interior_excess_mean': res['final_glyph_x_initial_glyph']['within_line_interior'],
                     'word_cross_excess': res['word_type']['cross_line'],
                     'word_interior_excess_mean': res['word_type']['within_line_interior']}
    return out


# ------------------------------------------------------------------- main
def clean_json(o):
    if isinstance(o, dict):
        return {str(k): clean_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean_json(v) for v in o]
    if isinstance(o, float):
        if math.isnan(o) or math.isinf(o):
            return None
        return round(o, 6)
    if isinstance(o, bool):
        return o
    return o


def run(name, path, alpha, perms, full):
    rng = random.Random(238)
    lines, paras, recs, freq = build(path, alpha)
    print(f'[{name}] {len(recs)} running-text lines, {len(paras)} paragraphs')
    res = {'n_lines': len(recs), 'n_paragraphs': len(paras),
           'n_words_running_text': sum(len(r['words']) for r in recs)}
    t1p = max(50, perms // 5)
    res['T1_final_glyph_all_lines'] = t1_analysis(recs, alpha, t1p, rng, 'final', None)
    res['T1_final_glyph_para_internal'] = t1_analysis(recs, alpha, t1p, rng, 'final', ('para_internal',))
    res['T1_initial_glyph_all_lines'] = t1_analysis(recs, alpha, t1p, rng, 'initial', None)
    res['T1_initial_glyph_para_internal'] = t1_analysis(recs, alpha, t1p, rng, 'initial', ('para_internal',))
    print(f'[{name}] T1 done')
    res['T2_split_word'] = t2_analysis(recs, freq, alpha, perms, rng)
    res['T2_position_perm_test'] = position_perm_test(recs, freq, alpha, t1p, rng)
    res['T2b_fragment_tests'] = t2b_fragment_tests(recs, freq, alpha, perms, rng)
    print(f'[{name}] T2 done')
    res['T4_cross_line_mi'] = t4_mi(recs, alpha, max(50, perms // 10), rng)
    res['T4b_by_language'] = t4b_juncture_by_lang(recs, alpha, max(50, perms // 10), rng)
    print(f'[{name}] T4 done')
    if full:
        res['T3_position_profile_para_internal_n_ge_7'] = position_profile(recs, freq, alpha)
        res['T3_compensation'] = t3_compensation(recs, paras, alpha, rng)
        res['T3b_margin_tests'] = t3b_margin_tests(recs, freq, alpha)
        print(f'[{name}] T3 done')
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--perms', type=int, default=1000)
    args = ap.parse_args()
    out = {'attack': 238, 'title': 'Line-break behaviour: is the line a functional unit, '
                                   'and are words split across lines?',
           'parameters': {'perms_T2': args.perms, 'perms_T1': max(50, args.perms // 5),
                          'perms_T4': max(50, args.perms // 10), 'seed': 238,
                          'strata': 'Currier language (A/B) x section ($I)',
                          'running_text': "unit=='P' and unit_sub!='t'"},
           'results': {}}
    for name, (path, alpha) in TRANSLITS.items():
        out['results'][name] = run(name, path, alpha, args.perms, full=(name == 'ZL3b'))
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(clean_json(out), fh, indent=1, ensure_ascii=False)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
