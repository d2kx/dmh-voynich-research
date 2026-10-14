"""Attack 240 - Vocabulary dynamics at multiple scales.

Research question: does Voynichese vocabulary behave like natural-language prose,
like a list/glossary, or like a generated text?  Five tests, all with explicit
nulls and stratified by Currier language ($L) and section ($I):

1. Heaps' law V(N) in manuscript order vs. token-order shuffles (global, per
   language, per section x language); beta fits with nulls + half-sample CI;
   vocabulary "bursts" at section / quire / language boundaries.
2. Word burstiness of frequent types (freq >= 20) across folios: stratified
   index of dispersion and Church & Gale residual IDF (RIDF), each compared to a
   within-(language, section) token-shuffle null; bimodality tests.
3. Paragraph-level novelty: rate of first-occurrence-on-folio tokens in line 1
   of multi-line paragraphs vs later lines, against a within-paragraph
   line-order shuffle null.
4. Herbal page "name" candidates: folio-specific repeated types, their excess
   over a bag-of-words null, and their positional concentration in the first
   line / first word of the page (plus a gallows-stripped first-word test).
5. Robustness: tests 1 and 2 re-run on data/IT2a-n.txt (Takahashi).

Only running-text lines (unit 'P') and fully legible words (clean_words) are
used.  Pure Python (numpy is not installed in this environment).

Usage:  python tools/attack240_vocabulary_dynamics.py
Output: data/attack240_vocabulary_dynamics.json, pages/vd240_*.png
"""
from __future__ import annotations

import json
import math
import os
import random
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voynich_corpus import ROOT, DATA, load_lines, paragraphs  # noqa: E402

SEED = 240
N_SHUF_HEAPS = 200
N_SHUF_BURST = 200
N_SHUF_PARA = 300
N_SHUF_NAMES = 300
GALLOWS_PREFIXES = ('cth', 'ckh', 'cph', 'cfh', 't', 'k', 'p', 'f')


# ----------------------------------------------------------------------------
# basic helpers
# ----------------------------------------------------------------------------
def mean(x):
    x = list(x)
    return sum(x) / len(x) if x else float('nan')


def sd(x):
    x = list(x)
    return statistics.pstdev(x) if len(x) > 1 else 0.0


def pct(x, q):
    x = sorted(x)
    if not x:
        return float('nan')
    k = (len(x) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return x[lo] + (x[hi] - x[lo]) * (k - lo)


def ols(xs, ys):
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    return b, my - b * mx


def ranks(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    mx, my = mean(rx), mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float('nan')


def r4(x):
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None
        return round(x, 4)
    return x


def emp_p_two(obs, null):
    """Two-sided empirical p (add-one)."""
    m = mean(null)
    k = sum(1 for v in null if abs(v - m) >= abs(obs - m) - 1e-12)
    return (k + 1) / (len(null) + 1)


def emp_p_greater(obs, null):
    k = sum(1 for v in null if v >= obs - 1e-12)
    return (k + 1) / (len(null) + 1)


def zscore(obs, null):
    s = sd(null)
    return (obs - mean(null)) / s if s > 0 else float('nan')


# ----------------------------------------------------------------------------
# corpus
# ----------------------------------------------------------------------------
class Tok:
    __slots__ = ('w', 'folio', 'fi', 'lang', 'sec', 'quire', 'hand', 'line_rank', 'pos', 'para_id', 'pline')

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def build_corpus(path=None):
    lines = load_lines(path)
    P = [l for l in lines if l.unit == 'P']
    paras = paragraphs(lines)
    para_of = {}
    for pid, para in enumerate(paras):
        for k, l in enumerate(para):
            para_of[id(l)] = (pid, k)
    folio_order = []
    seen = set()
    line_rank = Counter()
    toks = []
    for l in P:
        if l.folio not in seen:
            seen.add(l.folio)
            folio_order.append(l.folio)
        lr = line_rank[l.folio]
        line_rank[l.folio] += 1
        pid, k = para_of.get(id(l), (-1, -1))
        for j, w in enumerate(l.clean_words):
            toks.append(Tok(w=w, folio=l.folio, fi=len(folio_order) - 1, lang=l.lang, sec=l.section,
                            quire=l.quire, hand=l.hand, line_rank=lr, pos=j, para_id=pid, pline=k))
    return lines, P, paras, folio_order, toks


# ----------------------------------------------------------------------------
# Natural-language control corpora (downloaded from Project Gutenberg into the
# OS temp dir; skipped gracefully if offline).  They are re-shaped to mimic the
# Voynich layout: "folio" = one herbal entry (Culpeper) or ~170-token block of
# paragraphs (Caesar), lines of 9 words, paragraphs = blank-line paragraphs.
# ----------------------------------------------------------------------------
CONTROL_URLS = {
    'culpeper_herbal_en': 'https://www.gutenberg.org/cache/epub/49513/pg49513.txt',
    'caesar_bg_la': 'https://www.gutenberg.org/cache/epub/18837/pg18837.txt',
}
WORDS_PER_LINE = 9
PAGE_TOKENS = 170


class CLine:
    def __init__(self, folio, words, lang, section):
        self.folio, self.clean_words, self.lang, self.section = folio, words, lang, section


def fetch_control(name):
    import tempfile
    import urllib.request
    d = os.path.join(tempfile.gettempdir(), 'voynich_attack240')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + '.txt')
    if not os.path.exists(p):
        try:
            urllib.request.urlretrieve(CONTROL_URLS[name], p)
        except Exception as e:  # pragma: no cover
            print('control download failed', name, e)
            return None
    with open(p, encoding='utf-8', errors='replace') as fh:
        t = fh.read()
    a = t.find('*** START')
    b = t.find('*** END')
    if a >= 0:
        t = t[t.find('\n', a) + 1:b if b > a else None]
    return t


def _norm_words(s):
    import re
    return re.findall(r"[a-zæœàâäéèêëïîôöùûüç]+", s.lower())


def control_pages(name, max_tokens=35000):
    """Return list of pages; page = list of paragraphs; paragraph = list of words."""
    import re
    t = fetch_control(name)
    if t is None:
        return None
    t = t.replace('\r', '')
    pages = []
    if name == 'culpeper_herbal_en':
        lines = t.split('\n')
        head = re.compile(r"^ {4}([A-Z][A-Z \-',’]+)[\.,]?\s*$")
        start = next(i for i, l in enumerate(lines) if l.strip() == 'AMARA DULCIS.')
        entries, cur = [], None
        for l in lines[start:]:
            if head.match(l):
                if cur:
                    entries.append(cur)
                cur = []
                continue
            if cur is not None:
                cur.append(l)
        if cur:
            entries.append(cur)
        for e in entries:
            paras = [_norm_words(p) for p in '\n'.join(e).split('\n\n')]
            paras = [p for p in paras if p]
            # cap entry at PAGE_TOKENS tokens (Voynich folios average ~168 P tokens)
            out, n = [], 0
            for p in paras:
                if n >= PAGE_TOKENS:
                    break
                p = p[:PAGE_TOKENS - n]
                out.append(p)
                n += len(p)
            if n >= 40:
                pages.append(out)
    else:
        body = re.sub(r'\[[^\]]*\]', ' ', t)
        paras = [_norm_words(p) for p in body.split('\n\n')]
        paras = [p for p in paras if len(p) >= 15]
        cur, n = [], 0
        for p in paras:
            cur.append(p)
            n += len(p)
            if n >= PAGE_TOKENS:
                pages.append(cur)
                cur, n = [], 0
    # truncate to max_tokens
    out, n = [], 0
    for pg in pages:
        out.append(pg)
        n += sum(len(p) for p in pg)
        if n >= max_tokens:
            break
    return out


def control_corpus(name, max_tokens=35000):
    pages = control_pages(name, max_tokens)
    if not pages:
        return None
    toks, paras, folio_order = [], [], []
    pid = 0
    for fi, pg in enumerate(pages):
        folio = f'{name}_{fi:03d}'
        folio_order.append(folio)
        lr = 0
        for para in pg:
            plines = []
            for k in range(0, len(para), WORDS_PER_LINE):
                ws = para[k:k + WORDS_PER_LINE]
                plines.append(CLine(folio, ws, 'X', 'H'))
                for j, w in enumerate(ws):
                    toks.append(Tok(w=w, folio=folio, fi=fi, lang='X', sec='H', quire='X', hand='X',
                                    line_rank=lr, pos=j, para_id=pid, pline=len(plines) - 1))
                lr += 1
            paras.append(plines)
            pid += 1
    return paras, folio_order, toks


def run_controls(rng):
    res = {}
    for name in CONTROL_URLS:
        cc = control_corpus(name)
        if cc is None:
            res[name] = {'skipped': 'download failed'}
            continue
        paras, fo, toks = cc
        print('control', name, len(toks), len(set(t.w for t in toks)), len(fo))
        r = {'n_tokens': len(toks), 'n_types': len(set(t.w for t in toks)), 'n_pages': len(fo),
             'layout': f'{WORDS_PER_LINE} words/line, <= {PAGE_TOKENS} tokens/page'}
        hb = heaps_block(toks, rng, n_shuf=100, label=name)
        hb.pop('curve')
        r['heaps'] = hb
        # size-matched Heaps: truncate to the Voynich Currier-A and -B token counts
        bt = burstiness_test(toks, fo, rng, n_shuf=100, detail=True)
        rows = bt.pop('rows')
        r['burstiness'] = {k: v for k, v in bt.items() if not k.startswith('histogram')}
        r['burstiness']['top_even_types_freq_ge50'] = [{'type': x['type'], 'freq': x['freq'],
                                                        'ridf_excess': x['ridf_excess']}
                                                       for x in bt['top_even_types_freq_ge50'][:10]]
        r['burstiness']['top_bursty_types'] = [{'type': x['type'], 'freq': x['freq'],
                                                'ridf_excess': x['ridf_excess'], 'top_folio_share': x['top_folio_share']}
                                               for x in bt['top_bursty_types'][:15]]
        r['burstiness'].pop('top_concentrated_types', None)
        r['histogram_ridf_excess'] = bt['histogram_ridf_excess']
        r['concentration_f5_share50'] = concentration_test(toks, fo, rng, n_shuf=50, min_freq=5, share=0.5)
        r['concentration_f5_share50'].pop('examples')
        gf = Counter(t.w for t in toks)
        pn = para_novelty(paras, rng, n_shuf=150, min_lines=3, global_freq=gf)
        r['paragraph_novelty_min3'] = {v: d.get('ALL') for v, d in pn['variants'].items()}
        r['paragraph_novelty_min3']['n_paragraphs'] = pn['n_paragraphs']
        hn = herbal_names(toks, fo, rng, n_shuf=100)
        r['page_specific_types'] = {k: v for k, v in hn.items() if k not in ('first_words', 'top_examples')}
        r['page_specific_types']['top_examples'] = [{k: e[k] for k in ('folio', 'type', 'on_folio', 'elsewhere', 'in_line1')}
                                                    for e in hn['top_examples'][:10]]
        res[name] = r
    return res

# ----------------------------------------------------------------------------
# Test 1: Heaps' law
# ----------------------------------------------------------------------------
def checkpoints(n, lo=100, k=40):
    if n <= lo:
        return [n]
    pts = sorted({int(round(math.exp(math.log(lo) + (math.log(n) - math.log(lo)) * i / (k - 1)))) for i in range(k)})
    return [p for p in pts if 1 <= p <= n]


def heaps_curve(words, cps):
    seen = set()
    out = []
    ci = 0
    for i, w in enumerate(words, 1):
        seen.add(w)
        while ci < len(cps) and i == cps[ci]:
            out.append(len(seen))
            ci += 1
    return out


def fit_beta(cps, vs):
    b, a = ols([math.log(c) for c in cps], [math.log(v) for v in vs])
    return b, math.exp(a)


def heaps_block(toks, rng, n_shuf=N_SHUF_HEAPS, label=''):
    words = [t.w for t in toks]
    n = len(words)
    cps = checkpoints(n)
    ms = heaps_curve(words, cps)
    b_ms, k_ms = fit_beta(cps, ms)
    # token-shuffle null
    shuf_curves, shuf_b = [], []
    w2 = words[:]
    for _ in range(n_shuf):
        rng.shuffle(w2)
        c = heaps_curve(w2, cps)
        shuf_curves.append(c)
        shuf_b.append(fit_beta(cps, c)[0])
    mean_curve = [mean(c[i] for c in shuf_curves) for i in range(len(cps))]
    lo_curve = [pct([c[i] for c in shuf_curves], 0.025) for i in range(len(cps))]
    hi_curve = [pct([c[i] for c in shuf_curves], 0.975) for i in range(len(cps))]
    # folio-order shuffle null (keep within-folio order)
    by_folio = defaultdict(list)
    for t in toks:
        by_folio[t.fi].append(t.w)
    fol = list(by_folio)
    fold_b = []
    for _ in range(n_shuf):
        rng.shuffle(fol)
        seq = [w for f in fol for w in by_folio[f]]
        fold_b.append(fit_beta(cps, heaps_curve(seq, cps))[0])
    # delete-half jackknife: random 50% folio subsets kept in manuscript order
    half_b = []
    fol_sorted = sorted(by_folio)
    for _ in range(n_shuf):
        sub = sorted(rng.sample(fol_sorted, max(1, len(fol_sorted) // 2)))
        seq = [w for f in sub for w in by_folio[f]]
        cp2 = checkpoints(len(seq))
        half_b.append(fit_beta(cp2, heaps_curve(seq, cp2))[0])
    # mid-text deficit of manuscript order relative to shuffled
    i_half = min(range(len(cps)), key=lambda i: abs(cps[i] - n / 2))
    deficit = [(ms[i] - mean_curve[i]) / mean_curve[i] for i in range(len(cps))]
    max_def_i = min(range(len(cps)), key=lambda i: deficit[i])
    return {
        'label': label,
        'n_tokens': n,
        'n_types': ms[-1],
        'n_folios': len(by_folio),
        'beta_manuscript_order': r4(b_ms),
        'K_manuscript_order': r4(k_ms),
        'beta_token_shuffle_mean': r4(mean(shuf_b)),
        'beta_token_shuffle_95': [r4(pct(shuf_b, .025)), r4(pct(shuf_b, .975))],
        'beta_folio_order_shuffle_mean': r4(mean(fold_b)),
        'beta_folio_order_shuffle_95': [r4(pct(fold_b, .025)), r4(pct(fold_b, .975))],
        'beta_half_sample_ci95': [r4(pct(half_b, .025)), r4(pct(half_b, .975))],
        'V_at_half_ms': ms[i_half],
        'V_at_half_shuffle_mean': r4(mean_curve[i_half]),
        'V_at_half_shuffle_95': [r4(lo_curve[i_half]), r4(hi_curve[i_half])],
        'max_relative_deficit_vs_shuffle': r4(deficit[max_def_i]),
        'max_deficit_at_N': cps[max_def_i],
        'curve': {'N': cps, 'V_ms': ms, 'V_shuf_mean': [r4(v) for v in mean_curve],
                  'V_shuf_lo': [r4(v) for v in lo_curve], 'V_shuf_hi': [r4(v) for v in hi_curve]},
    }


def boundary_bursts(toks, folio_order, rng, n_shuf=N_SHUF_HEAPS, window=1500):
    """Per-folio global novelty excess vs token shuffle and local novelty at boundaries."""
    words = [t.w for t in toks]
    spans = {}
    for i, t in enumerate(toks):
        s = spans.setdefault(t.fi, [i, i])
        s[1] = i
    fis = sorted(spans)
    meta = {}
    for t in toks:
        meta.setdefault(t.fi, (t.sec, t.quire, t.lang, t.folio))

    def new_counts(seq):
        seen = set()
        out = {}
        for fi in fis:
            a, b = spans[fi]
            c = 0
            for w in seq[a:b + 1]:
                if w not in seen:
                    seen.add(w)
                    c += 1
            out[fi] = c
        return out

    obs = new_counts(words)
    acc = defaultdict(list)
    w2 = words[:]
    for _ in range(n_shuf):
        rng.shuffle(w2)
        nc = new_counts(w2)
        for fi in fis:
            acc[fi].append(nc[fi])
    excess = {fi: (obs[fi] - mean(acc[fi])) / (spans[fi][1] - spans[fi][0] + 1) for fi in fis}

    # local novelty: share of folio tokens whose type is absent from previous `window` tokens
    local = {}
    for fi in fis:
        a, b = spans[fi]
        prev = set(words[max(0, a - window):a])
        if a < window:          # not enough history
            continue
        seg = words[a:b + 1]
        local[fi] = sum(1 for w in seg if w not in prev) / len(seg)

    out = {}
    for kind, idx in (('section', 0), ('quire', 1), ('language', 2)):
        bset = set()
        for k in range(1, len(fis)):
            if meta[fis[k]][idx] != meta[fis[k - 1]][idx]:
                bset.add(fis[k])
        res = {'n_boundaries': len(bset), 'boundary_folios': [meta[f][3] for f in sorted(bset)]}
        for mname, metric in (('global_novelty_excess_per_token', excess), ('local_novelty_share', local)):
            keys = [f for f in fis if f in metric]
            bk = [f for f in keys if f in bset]
            if len(bk) < 2:
                continue
            obs_d = mean(metric[f] for f in bk) - mean(metric[f] for f in keys if f not in bset)
            # permutation within section strata (boundary label shuffled among folios of the same section)
            strata = defaultdict(list)
            for f in keys:
                strata[meta[f][0]].append(f)
            nb_per = Counter(meta[f][0] for f in bk)
            null = []
            for _ in range(2000):
                chosen = set()
                for s, n_b in nb_per.items():
                    chosen.update(rng.sample(strata[s], min(n_b, len(strata[s]))))
                null.append(mean(metric[f] for f in chosen) - mean(metric[f] for f in keys if f not in chosen))
            res[mname] = {'boundary_mean': r4(mean(metric[f] for f in bk)),
                          'other_mean': r4(mean(metric[f] for f in keys if f not in bset)),
                          'diff': r4(obs_d), 'null_diff_mean': r4(mean(null)),
                          'z': r4(zscore(obs_d, null)), 'p_greater': r4(emp_p_greater(obs_d, null))}
        out[kind] = res
    top = sorted(fis, key=lambda f: -excess[f])[:12]
    out['top_global_novelty_excess_folios'] = [
        {'folio': meta[f][3], 'section': meta[f][0], 'quire': meta[f][1], 'lang': meta[f][2],
         'excess_new_types_per_token': r4(excess[f]), 'observed_new_types': obs[f],
         'expected_new_types': r4(mean(acc[f]))} for f in top]
    return out


# ----------------------------------------------------------------------------
# Test 2: burstiness
# ----------------------------------------------------------------------------
def burst_stats(toks, min_freq=20, only=None):
    """Return per-type stratified dispersion and RIDF for tokens (order irrelevant)."""
    fol_n = Counter(t.fi for t in toks)
    fol_b = {}
    for t in toks:
        fol_b[t.fi] = (t.lang, t.sec)
    b_n = Counter()
    for fi, n in fol_n.items():
        b_n[fol_b[fi]] += n
    freq = Counter(t.w for t in toks)
    types = [w for w, c in freq.items() if c >= min_freq and (only is None or w in only)]
    tset = set(types)
    cnt = defaultdict(Counter)     # w -> folio -> count
    bcnt = defaultdict(Counter)    # w -> bucket -> count
    for t in toks:
        if t.w in tset:
            cnt[t.w][t.fi] += 1
            bcnt[t.w][fol_b[t.fi]] += 1
    N = len(toks)
    fis = list(fol_n)
    out = {}
    for w in types:
        chi_s = chi_g = 0.0
        nf_s = 0
        pred_df_s = pred_df_g = 0.0
        f = freq[w]
        for fi in fis:
            c = cnt[w].get(fi, 0)
            eg = f * fol_n[fi] / N
            chi_g += (c - eg) ** 2 / eg
            pred_df_g += 1 - math.exp(-eg)
            b = fol_b[fi]
            es = bcnt[w].get(b, 0) * fol_n[fi] / b_n[b]
            pred_df_s += 1 - math.exp(-es)
            if es > 0:
                chi_s += (c - es) ** 2 / es
                nf_s += 1
        obs_df = len(cnt[w])
        n_buckets = len(bcnt[w])
        out[w] = {
            'freq': f,
            'df': obs_df,
            'disp_global': chi_g / (len(fis) - 1),
            'disp_strat': chi_s / max(1, nf_s - n_buckets),
            'ridf_global': math.log2(pred_df_g / obs_df),
            'ridf_strat': math.log2(pred_df_s / obs_df),
            'top_folio_share': max(cnt[w].values()) / f,
            'top_folio_fi': max(cnt[w], key=cnt[w].get),
        }
    return out


def shuffle_within_buckets(toks, rng):
    """Return new token list with words permuted within (lang, section) buckets."""
    groups = defaultdict(list)
    for i, t in enumerate(toks):
        groups[(t.lang, t.sec)].append(i)
    new_w = [t.w for t in toks]
    for idx in groups.values():
        ws = [new_w[i] for i in idx]
        rng.shuffle(ws)
        for i, w in zip(idx, ws):
            new_w[i] = w
    out = []
    for t, w in zip(toks, new_w):
        out.append(Tok(w=w, folio=t.folio, fi=t.fi, lang=t.lang, sec=t.sec, quire=t.quire, hand=t.hand,
                       line_rank=t.line_rank, pos=t.pos, para_id=t.para_id, pline=t.pline))
    return out


def moments(x):
    n = len(x)
    m = mean(x)
    s2 = sum((v - m) ** 2 for v in x) / n
    s = math.sqrt(s2)
    g1 = sum((v - m) ** 3 for v in x) / n / s ** 3
    g2 = sum((v - m) ** 4 for v in x) / n / s2 ** 2 - 3
    # sample-corrected
    G1 = g1 * math.sqrt(n * (n - 1)) / (n - 2)
    G2 = ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3))
    return G1, G2


def bimodality_coefficient(x):
    n = len(x)
    G1, G2 = moments(x)
    return (G1 ** 2 + 1) / (G2 + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))


def gmm_bic(x, iters=500):
    n = len(x)
    m, s = mean(x), sd(x)

    def lpdf(v, mu, sg):
        return -0.5 * math.log(2 * math.pi * sg * sg) - (v - mu) ** 2 / (2 * sg * sg)

    ll1 = sum(lpdf(v, m, s) for v in x)
    bic1 = -2 * ll1 + 2 * math.log(n)
    best = None
    for init in ((0.25, 0.75), (0.1, 0.9), (0.5, 0.95)):
        mu = [pct(x, init[0]), pct(x, init[1])]
        sg = [s / 2, s / 2]
        pi = [0.5, 0.5]
        ll = None
        for _ in range(iters):
            resp = []
            ll_new = 0.0
            for v in x:
                a = math.log(pi[0]) + lpdf(v, mu[0], sg[0])
                b = math.log(pi[1]) + lpdf(v, mu[1], sg[1])
                mx = max(a, b)
                tot = mx + math.log(math.exp(a - mx) + math.exp(b - mx))
                ll_new += tot
                resp.append(math.exp(a - tot))
            r0 = sum(resp)
            r1 = n - r0
            if r0 < 1e-6 or r1 < 1e-6:
                break
            mu = [sum(r * v for r, v in zip(resp, x)) / r0, sum((1 - r) * v for r, v in zip(resp, x)) / r1]
            sg = [max(1e-3, math.sqrt(sum(r * (v - mu[0]) ** 2 for r, v in zip(resp, x)) / r0)),
                  max(1e-3, math.sqrt(sum((1 - r) * (v - mu[1]) ** 2 for r, v in zip(resp, x)) / r1))]
            pi = [r0 / n, r1 / n]
            if ll is not None and abs(ll_new - ll) < 1e-7:
                ll = ll_new
                break
            ll = ll_new
        if ll is not None and (best is None or ll > best[0]):
            best = (ll, mu, sg, pi)
    ll2, mu, sg, pi = best
    bic2 = -2 * ll2 + 5 * math.log(n)
    # Ashman's D separation
    ashman = math.sqrt(2) * abs(mu[0] - mu[1]) / math.sqrt(sg[0] ** 2 + sg[1] ** 2)
    return {'bic_1comp': r4(bic1), 'bic_2comp': r4(bic2), 'delta_bic_2_minus_1': r4(bic2 - bic1),
            'mu': [r4(v) for v in mu], 'sigma': [r4(v) for v in sg], 'weights': [r4(v) for v in pi],
            'ashman_D': r4(ashman)}


def burstiness_test(toks, folio_order, rng, n_shuf=N_SHUF_BURST, min_freq=20, detail=True):
    obs = burst_stats(toks, min_freq)
    types = sorted(obs, key=lambda w: -obs[w]['freq'])
    null = defaultdict(lambda: defaultdict(list))
    pooled_null_ridf = []
    pooled_null_logd = []
    for k in range(n_shuf):
        st = burst_stats(shuffle_within_buckets(toks, rng), min_freq=1, only=set(types))
        for w in types:
            s = st.get(w)
            if s is None:
                continue
            null[w]['ridf_strat'].append(s['ridf_strat'])
            null[w]['disp_strat'].append(s['disp_strat'])
            null[w]['top_folio_share'].append(s['top_folio_share'])
            if k < 20:
                pooled_null_ridf.append(s['ridf_strat'])
                pooled_null_logd.append(math.log10(max(1e-3, s['disp_strat'])))
    rows = []
    for w in types:
        o = obs[w]
        nr = null[w]['ridf_strat']
        nd = null[w]['disp_strat']
        rows.append({
            'type': w, 'freq': o['freq'], 'df': o['df'],
            'disp_global': r4(o['disp_global']), 'disp_strat': r4(o['disp_strat']),
            'disp_strat_null_mean': r4(mean(nd)), 'disp_strat_z': r4(zscore(o['disp_strat'], nd)),
            'ridf_global': r4(o['ridf_global']), 'ridf_strat': r4(o['ridf_strat']),
            'ridf_strat_null_mean': r4(mean(nr)), 'ridf_excess': r4(o['ridf_strat'] - mean(nr)),
            'ridf_strat_z': r4(zscore(o['ridf_strat'], nr)),
            'p_disp_greater': r4(emp_p_greater(o['disp_strat'], nd)),
            'top_folio': folio_order[o['top_folio_fi']], 'top_folio_share': r4(o['top_folio_share']),
            'top_folio_share_null_mean': r4(mean(null[w]['top_folio_share'])),
        })
    n = len(rows)
    sig_disp = sum(1 for r in rows if r['p_disp_greater'] is not None and r['p_disp_greater'] <= 0.01)
    under = sum(1 for r in rows if r['disp_strat_z'] is not None and r['disp_strat_z'] < -2)
    ridf_ex = [r['ridf_excess'] for r in rows]
    logd = [math.log10(max(1e-3, obs[r['type']]['disp_strat'])) for r in rows]
    logf = [math.log10(r['freq']) for r in rows]
    res = {
        'n_types_tested': n,
        'min_freq': min_freq,
        'n_shuffles': n_shuf,
        'share_overdispersed_p01': r4(sig_disp / n),
        'share_underdispersed_z_lt_-2': r4(under / n),
        'median_disp_strat': r4(statistics.median(obs[w]['disp_strat'] for w in types)),
        'median_disp_strat_null': r4(statistics.median(mean(null[w]['disp_strat']) for w in types)),
        'median_ridf_strat': r4(statistics.median(obs[w]['ridf_strat'] for w in types)),
        'median_ridf_excess': r4(statistics.median(ridf_ex)),
        'spearman_logfreq_vs_ridf_excess': r4(spearman(logf, ridf_ex)),
        'spearman_logfreq_vs_logdisp': r4(spearman(logf, logd)),
        'bimodality': {
            'ridf_excess_BC': r4(bimodality_coefficient(ridf_ex)),
            'ridf_null_pooled_BC': r4(bimodality_coefficient(pooled_null_ridf)),
            'log10_disp_BC': r4(bimodality_coefficient(logd)),
            'log10_disp_null_pooled_BC': r4(bimodality_coefficient(pooled_null_logd)),
            'BC_threshold_note': 'BC > 0.555 suggests bimodality (uniform distribution = 0.555)',
            'gmm_ridf_excess': gmm_bic(ridf_ex) if detail else None,
            'gmm_log10_disp': gmm_bic(logd) if detail else None,
        },
    }
    # frequency-banded summaries
    bands = [(20, 50), (50, 100), (100, 300), (300, 100000)]
    res['by_freq_band'] = []
    for lo, hi in bands:
        sub = [r for r in rows if lo <= r['freq'] < hi]
        if not sub:
            continue
        res['by_freq_band'].append({
            'band': f'{lo}-{hi - 1 if hi < 100000 else "max"}', 'n_types': len(sub),
            'median_disp_strat': r4(statistics.median(r['disp_strat'] for r in sub)),
            'median_ridf_excess': r4(statistics.median(r['ridf_excess'] for r in sub)),
            'share_overdispersed_p01': r4(sum(1 for r in sub if r['p_disp_greater'] <= 0.01) / len(sub)),
        })
    if detail:
        ev = [r for r in rows if r['freq'] >= 50]
        res['top_even_types_freq_ge50'] = sorted(ev, key=lambda r: r['ridf_excess'])[:15]
        res['top_bursty_types'] = sorted(rows, key=lambda r: -r['ridf_excess'])[:25]
        res['top_concentrated_types'] = sorted(rows, key=lambda r: -r['top_folio_share'])[:15]
        res['histogram_ridf_excess'] = histogram(ridf_ex, -0.4, 2.0, 24)
        res['histogram_ridf_null'] = histogram([v - mean(pooled_null_ridf) for v in pooled_null_ridf], -0.4, 2.0, 24)
        res['rows'] = rows
    return res


def histogram(x, lo, hi, nb):
    h = [0] * nb
    for v in x:
        k = int((v - lo) / (hi - lo) * nb)
        k = min(nb - 1, max(0, k))
        h[k] += 1
    return {'lo': lo, 'hi': hi, 'counts': h}


def concentration_test(toks, folio_order, rng, n_shuf=100, min_freq=5, share=0.5):
    """Count types (freq>=min_freq) with >=share of occurrences on one folio vs bucket-shuffle null."""
    def count(ts):
        freq = Counter(t.w for t in ts)
        c = defaultdict(Counter)
        for t in ts:
            if freq[t.w] >= min_freq:
                c[t.w][t.fi] += 1
        hits = [(w, folio_order[max(cc, key=cc.get)], max(cc.values()), freq[w]) for w, cc in c.items()
                if max(cc.values()) / freq[w] >= share]
        return hits
    obs = count(toks)
    null = [len(count(shuffle_within_buckets(toks, rng))) for _ in range(n_shuf)]
    return {'min_freq': min_freq, 'share': share, 'observed_types': len(obs),
            'null_mean': r4(mean(null)), 'null_95': [r4(pct(null, .025)), r4(pct(null, .975))],
            'ratio': r4(len(obs) / mean(null)) if mean(null) else None,
            'z': r4(zscore(len(obs), null)),
            'examples': [{'type': w, 'folio': f, 'on_folio': k, 'freq': n}
                         for w, f, k, n in sorted(obs, key=lambda x: (-x[2], -x[3]))[:25]]}


# ----------------------------------------------------------------------------
# Test 3: paragraph novelty
# ----------------------------------------------------------------------------
def para_novelty(paras, rng, n_shuf=N_SHUF_PARA, min_lines=3, global_freq=None):
    """Line-1 vs later-line first-occurrence-on-folio rates with within-paragraph line-shuffle null."""
    # group paragraphs by folio in order
    fol_paras = defaultdict(list)
    for p in paras:
        if not p:
            continue
        fol_paras[p[0].folio].append([l.clean_words for l in p] + [None] * 0)
    meta = {}
    for p in paras:
        if p:
            meta[p[0].folio] = (p[0].lang, p[0].section)

    variants = ('all', 'skip_line_initial', 'common_types_f10', 'para_novelty', 'introduced_and_reused')

    def stats(fp_lines):
        # fp_lines: folio -> list of paragraphs (list of word-lists)
        agg = {v: defaultdict(lambda: [0, 0, 0, 0]) for v in variants}  # stratum -> [hit1, n1, hitL, nL]
        for folio, plist in fp_lines.items():
            lang, sec = meta[folio]
            strata = ('ALL', 'sec_' + ('H' if sec == 'H' else sec), 'lang_' + lang)
            seen_f = set()
            for para in plist:
                eligible = len(para) >= min_lines
                seen_p = set()
                later_types = []
                # precompute "type occurs later in paragraph" counts
                remaining = Counter(w for line in para for w in line)
                for li, line in enumerate(para):
                    for j, w in enumerate(line):
                        remaining[w] -= 1
                        newf = w not in seen_f
                        newp = w not in seen_p
                        if eligible:
                            slot = 0 if li == 0 else 2
                            vals = {
                                'all': (newf, True),
                                'skip_line_initial': (newf, j > 0),
                                'common_types_f10': (newf, global_freq.get(w, 0) >= 10),
                                'para_novelty': (newp, True),
                                'introduced_and_reused': (newf and remaining[w] > 0, True),
                            }
                            for v, (hit, ok) in vals.items():
                                if not ok:
                                    continue
                                for s in strata:
                                    a = agg[v][s]
                                    a[slot] += 1 if hit else 0
                                    a[slot + 1] += 1
                        seen_f.add(w)
                        seen_p.add(w)
        out = {}
        for v in variants:
            out[v] = {}
            for s, a in agg[v].items():
                r1 = a[0] / a[1] if a[1] else float('nan')
                rL = a[2] / a[3] if a[3] else float('nan')
                out[v][s] = (r1, rL, r1 - rL, a[1], a[3])
        return out

    obs = stats(fol_paras)
    nulls = defaultdict(list)
    for _ in range(n_shuf):
        sh = {}
        for folio, plist in fol_paras.items():
            npl = []
            for para in plist:
                q = para[:]
                rng.shuffle(q)
                npl.append(q)
            sh[folio] = npl
        st = stats(sh)
        for v in variants:
            for s, tup in st[v].items():
                nulls[(v, s)].append(tup[2])
    res = {}
    for v in variants:
        res[v] = {}
        for s, (r1, rL, d, n1, nL) in sorted(obs[v].items()):
            nl = nulls[(v, s)]
            res[v][s] = {'rate_line1': r4(r1), 'rate_later': r4(rL), 'diff': r4(d), 'n_tokens_line1': n1,
                         'n_tokens_later': nL, 'null_diff_mean': r4(mean(nl)),
                         'null_diff_95': [r4(pct(nl, .025)), r4(pct(nl, .975))],
                         'excess_over_null': r4(d - mean(nl)), 'z': r4(zscore(d, nl)),
                         'p_two': r4(emp_p_two(d, nl))}
    n_par = sum(1 for p in paras if len(p) >= min_lines)
    return {'min_lines': min_lines, 'n_paragraphs': n_par, 'n_shuffles': n_shuf, 'variants': res}


# ----------------------------------------------------------------------------
# Test 4: herbal page-name candidates
# ----------------------------------------------------------------------------
def strip_gallows(w):
    for g in GALLOWS_PREFIXES:
        if w.startswith(g) and len(w) > len(g) + 1:
            if g in ('cth', 'ckh', 'cph', 'cfh'):
                return 'ch' + w[len(g):]
            return w[len(g):]
    return None


VOY_SUFFIXES = sorted(['aiin', 'aiir', 'ain', 'air', 'iin', 'iir', 'eedy', 'edy', 'dy', 'eey', 'ey', 'ody',
                       'ol', 'or', 'al', 'ar', 'am', 'an', 'y', 's', 'l', 'r', 'n', 'm', 'o', 'd'],
                      key=len, reverse=True)


def voy_stem(w):
    """Coarse 'core' of a Voynich word: drop q-/qo- proclitic and one terminal suffix (>=2 glyphs kept)."""
    if w.startswith('qo') and len(w) > 3:
        w = w[2:]
    elif w.startswith('q') and len(w) > 2:
        w = w[1:]
    for s in VOY_SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 2:
            return w[:-len(s)]
    return w


def herbal_names(toks, folio_order, rng, n_shuf=N_SHUF_NAMES):
    freq = Counter(t.w for t in toks)
    D = len(set(t.fi for t in toks))
    df = Counter()
    for w, fi in set((t.w, t.fi) for t in toks):
        df[w] += 1

    RULES = {
        'exclusive_tf2': dict(min_tf=2, max_else=1, min_share=None,
                              desc='>=2 tokens on one Herbal folio and <=1 token anywhere else'),
        'enriched_tf2_share50': dict(min_tf=2, max_else=None, min_share=0.5,
                                     desc='>=2 tokens on one Herbal folio and >=50% of all its tokens there'),
        'enriched_tf3_share50': dict(min_tf=3, max_else=None, min_share=0.5,
                                     desc='>=3 tokens on one Herbal folio and >=50% of all its tokens there'),
    }

    FI = [t.fi for t in toks]
    ISH = [t.sec == 'H' for t in toks]

    def candidates(words, rule):
        fq = Counter(words)
        per = defaultdict(Counter)
        for w, fi, h in zip(words, FI, ISH):
            if h:
                per[fi][w] += 1
        cands = {}
        for fi, c in per.items():
            lst = []
            for w, k in c.items():
                if k < rule['min_tf']:
                    continue
                if rule['max_else'] is not None and fq[w] - k > rule['max_else']:
                    continue
                if rule['min_share'] is not None and k / fq[w] < rule['min_share']:
                    continue
                lst.append((w, k))
            cands[fi] = lst
        return cands

    shuffled = [[t.w for t in shuffle_within_buckets(toks, rng)] for _ in range(n_shuf)]
    obs_words = [t.w for t in toks]
    by_f = defaultdict(list)
    for t in toks:
        if t.sec == 'H':
            by_f[t.fi].append(t)
    rules_out = {}
    examples = []
    obs_c_main = None
    for rname, rule in RULES.items():
        obs_c = candidates(obs_words, rule)
        if rname == 'enriched_tf2_share50':
            obs_c_main = obs_c
        n_obs_types = sum(len(v) for v in obs_c.values())
        n_obs_folios = sum(1 for v in obs_c.values() if v)
        null_types, null_folios = [], []
        for sh in shuffled:
            sc = candidates(sh, rule)
            null_types.append(sum(len(v) for v in sc.values()))
            null_folios.append(sum(1 for v in sc.values() if v))
        cand_tok_line1 = cand_tok = 0
        exp_line1 = 0.0
        first_word_is_cand = 0
        first_word_exp = 0.0
        n_perm = 1000
        perm_line1 = [0] * n_perm
        for fi, ts in by_f.items():
            cset = {w for w, k in obs_c.get(fi, [])}
            nf = len(ts)
            l1 = sum(1 for t in ts if t.line_rank == 0)
            flags = [t.w in cset for t in ts]
            k = sum(flags)
            if not k:
                continue
            cand_tok += k
            cand_tok_line1 += sum(1 for t, f in zip(ts, flags) if f and t.line_rank == 0)
            exp_line1 += k * l1 / nf
            first_word_is_cand += 1 if flags[0] else 0
            first_word_exp += k / nf
            for s in range(n_perm):
                pos = rng.sample(range(nf), k)
                perm_line1[s] += sum(1 for p in pos if ts[p].line_rank == 0)
        rules_out[rname] = {
            'definition': rule['desc'],
            'observed_candidate_types': n_obs_types,
            'null_candidate_types_mean': r4(mean(null_types)),
            'null_candidate_types_95': [r4(pct(null_types, .025)), r4(pct(null_types, .975))],
            'candidate_types_ratio': r4(n_obs_types / mean(null_types)) if mean(null_types) else None,
            'candidate_types_z': r4(zscore(n_obs_types, null_types)),
            'candidate_types_p_greater': r4(emp_p_greater(n_obs_types, null_types)),
            'observed_folios_with_candidate': n_obs_folios,
            'null_folios_with_candidate_mean': r4(mean(null_folios)),
            'candidate_tokens': cand_tok,
            'candidate_tokens_in_line1': cand_tok_line1,
            'expected_in_line1': r4(exp_line1),
            'line1_ratio': r4(cand_tok_line1 / exp_line1) if exp_line1 else None,
            'line1_perm_p_greater': r4(emp_p_greater(cand_tok_line1, perm_line1)),
            'line1_perm_z': r4(zscore(cand_tok_line1, perm_line1)),
            'first_word_is_candidate': first_word_is_cand,
            'first_word_expected': r4(first_word_exp),
        }
    for fi, ts in by_f.items():
        for w, kk in obs_c_main.get(fi, []):
            in_l1 = sum(1 for t in ts if t.w == w and t.line_rank == 0)
            tfidf = kk * math.log(D / df[w])
            examples.append({'folio': folio_order[fi], 'lang': ts[0].lang, 'type': w, 'on_folio': kk,
                             'elsewhere': freq[w] - kk, 'in_line1': in_l1, 'is_first_word': ts[0].w == w,
                             'line_ranks': [t.line_rank for t in ts if t.w == w],
                             'n_lines_on_folio': max(t.line_rank for t in ts) + 1,
                             'tfidf': r4(tfidf),
                             'first_line': ' '.join(t.w for t in ts if t.line_rank == 0)})
    examples.sort(key=lambda e: (-e['on_folio'], e['elsewhere'], -e['tfidf']))
    n_fol = len(by_f)

    # gallows-stripped first-word residue test
    herb_folios = sorted(by_f)
    fw = {}
    for fi in herb_folios:
        ts = by_f[fi]
        fw[fi] = (ts[0].w, strip_gallows(ts[0].w), set(t.w for t in ts[1:]), ts[0].lang)
    def residue_hits(pairing):
        h_res = h_full = 0
        for fi, fj in pairing.items():
            w, r, _, _ = fw[fi]
            other = fw[fj][2] if fj != fi else fw[fi][2]
            if r and r in other:
                h_res += 1
            if w in other:
                h_full += 1
        return h_res, h_full
    ident = {fi: fi for fi in herb_folios}
    obs_res, obs_full = residue_hits(ident)
    n_with_res = sum(1 for fi in herb_folios if fw[fi][1])
    null_res, null_full = [], []
    langs = defaultdict(list)
    for fi in herb_folios:
        langs[fw[fi][3]].append(fi)
    for _ in range(2000):
        pairing = {}
        for lg, fl in langs.items():
            perm = fl[:]
            while True:
                rng.shuffle(perm)
                if len(fl) < 2 or all(a != b for a, b in zip(fl, perm)):
                    break
            pairing.update(dict(zip(fl, perm)))
        a, b = residue_hits(pairing)
        null_res.append(a)
        null_full.append(b)
    first_words = [{'folio': folio_order[fi], 'first_word': fw[fi][0], 'residue': fw[fi][1],
                    'residue_on_same_folio': bool(fw[fi][1] and fw[fi][1] in fw[fi][2]),
                    'full_word_on_same_folio': fw[fi][0] in fw[fi][2]} for fi in herb_folios]
    return {
        'n_herbal_folios': n_fol,
        'rules': rules_out,
        'first_word_residue_test': {
            'n_folios_with_gallows_first_word': n_with_res,
            'residue_found_on_same_folio': obs_res,
            'residue_found_on_random_same_language_folio_mean': r4(mean(null_res)),
            'residue_null_95': [r4(pct(null_res, .025)), r4(pct(null_res, .975))],
            'residue_ratio': r4(obs_res / mean(null_res)) if mean(null_res) else None,
            'residue_p_greater': r4(emp_p_greater(obs_res, null_res)),
            'full_first_word_on_same_folio': obs_full,
            'full_first_word_null_mean': r4(mean(null_full)),
            'full_first_word_p_greater': r4(emp_p_greater(obs_full, null_full)),
        },
        'top_examples': examples[:30],
        'first_words': first_words,
    }


# ----------------------------------------------------------------------------
# charts (PIL only)
# ----------------------------------------------------------------------------
def chart_heaps(blocks, path):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    W, H = 1500, 560
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    panel_w = W // len(blocks)
    for bi, (name, blk) in enumerate(blocks):
        x0 = bi * panel_w + 60
        x1 = (bi + 1) * panel_w - 20
        y0, y1 = 50, H - 60
        c = blk['curve']
        Ns = c['N']
        lx = [math.log10(n) for n in Ns]
        ys = c['V_ms'] + c['V_shuf_hi']
        ly_lo, ly_hi = math.log10(min(ys)), math.log10(max(ys))
        X = lambda v: x0 + (math.log10(v) - lx[0]) / (lx[-1] - lx[0]) * (x1 - x0)
        Y = lambda v: y1 - (math.log10(v) - ly_lo) / (ly_hi - ly_lo) * (y1 - y0)
        d.rectangle([x0, y0, x1, y1], outline='black')
        band = [(X(n), Y(v)) for n, v in zip(Ns, c['V_shuf_hi'])] + \
               [(X(n), Y(v)) for n, v in reversed(list(zip(Ns, c['V_shuf_lo'])))]
        d.polygon(band, fill=(200, 200, 255))
        d.line([(X(n), Y(v)) for n, v in zip(Ns, c['V_shuf_mean'])], fill='blue', width=2)
        d.line([(X(n), Y(v)) for n, v in zip(Ns, c['V_ms'])], fill='red', width=3)
        d.text((x0 + 5, 10), f"{name}: beta_ms={blk['beta_manuscript_order']} shuffle={blk['beta_token_shuffle_mean']}",
               fill='black')
        d.text((x0 + 5, 28), 'red = manuscript order, blue = token shuffle (95% band)', fill='black')
        for n in (100, 1000, 10000):
            if Ns[0] <= n <= Ns[-1]:
                d.text((X(n) - 10, y1 + 8), str(n), fill='black')
        d.text(((x0 + x1) // 2 - 40, y1 + 30), 'tokens N (log)', fill='black')
        for v in (100, 300, 1000, 3000, 8000):
            if min(ys) <= v <= max(ys):
                d.text((x0 - 45, Y(v) - 6), str(v), fill='black')
    img.save(path)
    return path


def chart_hist(obs_h, null_h, path, title):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    W, H = 900, 480
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    x0, x1, y0, y1 = 70, W - 30, 60, H - 60
    nb = len(obs_h['counts'])
    no = sum(obs_h['counts'])
    nn = sum(null_h['counts'])
    fo = [c / no for c in obs_h['counts']]
    fn = [c / nn for c in null_h['counts']]
    mx = max(fo + fn)
    bw = (x1 - x0) / nb
    for i in range(nb):
        h1 = fo[i] / mx * (y1 - y0)
        h2 = fn[i] / mx * (y1 - y0)
        d.rectangle([x0 + i * bw + 2, y1 - h2, x0 + (i + 1) * bw - 2, y1], fill=(190, 190, 250))
        d.rectangle([x0 + i * bw + bw * 0.3, y1 - h1, x0 + (i + 1) * bw - bw * 0.3, y1], fill=(220, 40, 40))
    d.rectangle([x0, y0, x1, y1], outline='black')
    for i in range(0, nb + 1, 4):
        v = obs_h['lo'] + (obs_h['hi'] - obs_h['lo']) * i / nb
        d.text((x0 + i * bw - 10, y1 + 8), f'{v:.1f}', fill='black')
    d.text((x0, 15), title, fill='black')
    d.text((x0, 33), 'red = observed types (freq>=20), blue = within-(lang,section) shuffle null (pooled)', fill='black')
    d.text(((x0 + x1) // 2 - 80, y1 + 30), 'RIDF excess over null (bits)', fill='black')
    img.save(path)
    return path


# ----------------------------------------------------------------------------
def run_heaps_suite(toks, rng, folio_order, include_sections=True):
    blocks = {'ALL': heaps_block(toks, rng, label='ALL')}
    for lg in ('A', 'B'):
        sub = [t for t in toks if t.lang == lg]
        blocks['lang_' + lg] = heaps_block(sub, rng, label='lang_' + lg)
    if include_sections:
        for key in sorted({(t.sec, t.lang) for t in toks}):
            sub = [t for t in toks if (t.sec, t.lang) == key]
            if len(sub) >= 1500:
                blocks[f'sec_{key[0]}_lang_{key[1]}'] = heaps_block(sub, rng, label=f'sec_{key[0]}_lang_{key[1]}')
        for sec in sorted({t.sec for t in toks}):
            sub = [t for t in toks if t.sec == sec]
            if len(sub) >= 1500:
                blocks[f'sec_{sec}'] = heaps_block(sub, rng, label=f'sec_{sec}')
    return blocks


def strip_curves(blocks):
    return {k: {kk: vv for kk, vv in v.items() if kk != 'curve'} for k, v in blocks.items()}


def main():
    rng = random.Random(SEED)
    out = {'attack': 240, 'title': 'Vocabulary dynamics at multiple scales', 'seed': SEED,
           'token_definition': "unit 'P' running-text lines, clean_words (no ?/'/* words), tools/voynich_corpus.py"}
    lines, P, paras, folio_order, toks = build_corpus()
    out['corpus'] = {'n_tokens': len(toks), 'n_types': len(set(t.w for t in toks)), 'n_folios': len(folio_order),
                     'tokens_by_lang': dict(Counter(t.lang for t in toks)),
                     'tokens_by_section': dict(Counter(t.sec for t in toks))}
    print('corpus', out['corpus'])

    # ---- Test 1
    blocks = run_heaps_suite(toks, rng, folio_order)
    out['test1_heaps'] = {'blocks': strip_curves(blocks), 'curves': {k: blocks[k]['curve'] for k in ('ALL', 'lang_A', 'lang_B')}}
    for k, b in blocks.items():
        print('heaps', k, b['n_tokens'], b['beta_manuscript_order'], b['beta_token_shuffle_95'],
              b['beta_folio_order_shuffle_95'], b['beta_half_sample_ci95'], b['max_relative_deficit_vs_shuffle'])
    out['test1_boundary_bursts'] = boundary_bursts(toks, folio_order, rng)
    for k in ('section', 'quire', 'language'):
        print('boundary', k, json.dumps(out['test1_boundary_bursts'][k].get('global_novelty_excess_per_token')),
              json.dumps(out['test1_boundary_bursts'][k].get('local_novelty_share')))
    chart_heaps([(k, blocks[k]) for k in ('ALL', 'lang_A', 'lang_B')], os.path.join(ROOT, 'pages', 'vd240_heaps_curves.png'))

    # ---- Test 2
    bt = burstiness_test(toks, folio_order, rng)
    out['test2_burstiness'] = bt
    print('burst', {k: v for k, v in bt.items() if k not in ('rows', 'top_even_types_freq_ge50', 'top_bursty_types',
                                                              'top_concentrated_types', 'histogram_ridf_excess',
                                                              'histogram_ridf_null')})
    print('even', [(r['type'], r['freq'], r['ridf_excess'], r['disp_strat']) for r in bt['top_even_types_freq_ge50']])
    print('bursty', [(r['type'], r['freq'], r['ridf_excess'], r['top_folio'], r['top_folio_share']) for r in bt['top_bursty_types']])
    chart_hist(bt['histogram_ridf_excess'], bt['histogram_ridf_null'], os.path.join(ROOT, 'pages', 'vd240_ridf_hist.png'),
               'Attack 240: residual-IDF excess of 20+ frequency types (ZL3b)')
    out['test2_concentration'] = {
        'f5_share50': concentration_test(toks, folio_order, rng, min_freq=5, share=0.5),
        'f3_share100_single_folio': concentration_test(toks, folio_order, rng, min_freq=3, share=1.0),
    }
    print('conc', {k: {kk: vv for kk, vv in v.items() if kk != 'examples'} for k, v in out['test2_concentration'].items()})

    # ---- Test 3
    gfreq = Counter(t.w for t in toks)
    out['test3_paragraph_novelty'] = {
        'min3': para_novelty(paras, rng, min_lines=3, global_freq=gfreq),
        'min2': para_novelty(paras, rng, n_shuf=150, min_lines=2, global_freq=gfreq),
    }
    for v, d in out['test3_paragraph_novelty']['min3']['variants'].items():
        for s, r in d.items():
            print('para', v, s, r['rate_line1'], r['rate_later'], r['diff'], r['null_diff_mean'], r['z'], r['p_two'])

    # ---- Test 4
    hn = herbal_names(toks, folio_order, rng)
    out['test4_herbal_names'] = hn
    print('names', {k: v for k, v in hn.items() if k not in ('top_examples', 'first_words')})
    for e in hn['top_examples'][:15]:
        print('  ', e)
    toks_stem = [Tok(w=voy_stem(t.w), folio=t.folio, fi=t.fi, lang=t.lang, sec=t.sec, quire=t.quire, hand=t.hand,
                     line_rank=t.line_rank, pos=t.pos, para_id=t.para_id, pline=t.pline) for t in toks]
    hs = herbal_names(toks_stem, folio_order, rng, n_shuf=200)
    out['test4_herbal_names_coarse_stems'] = {
        'stemmer': 'voy_stem: drop q-/qo- and one terminal suffix from ' + ','.join(VOY_SUFFIXES),
        'n_stem_types': len(set(t.w for t in toks_stem)),
        'rules': hs['rules'], 'top_examples': hs['top_examples'][:20]}
    print('names stem', json.dumps(hs['rules']))

    # ---- Test 5 robustness on IT2a
    _, _, _, fo2, toks2 = build_corpus(os.path.join(DATA, 'IT2a-n.txt'))
    rng2 = random.Random(SEED + 1)
    b2 = run_heaps_suite(toks2, rng2, fo2, include_sections=False)
    bt2 = burstiness_test(toks2, fo2, rng2, n_shuf=100, detail=False)
    bt2.pop('rows', None)
    out['test5_robustness_IT2a'] = {'corpus': {'n_tokens': len(toks2), 'n_types': len(set(t.w for t in toks2))},
                                    'heaps': strip_curves(b2), 'burstiness': bt2,
                                    'boundary_bursts': {k: v for k, v in boundary_bursts(toks2, fo2, rng2, n_shuf=100).items()
                                                        if k in ('section', 'quire', 'language')}}
    for k, b in b2.items():
        print('IT2a heaps', k, b['beta_manuscript_order'], b['beta_token_shuffle_95'], b['max_relative_deficit_vs_shuffle'])
    print('IT2a burst', bt2)

    # ---- Test 6 natural-language controls
    out['test6_natural_language_controls'] = run_controls(random.Random(SEED + 2))
    for k, v in out['test6_natural_language_controls'].items():
        if 'heaps' in v:
            print('CTRL', k, v['heaps']['beta_manuscript_order'], v['heaps']['beta_token_shuffle_95'],
                  v['heaps']['max_relative_deficit_vs_shuffle'])
            print('CTRL burst', k, {kk: vv for kk, vv in v['burstiness'].items()
                                    if kk not in ('top_even_types_freq_ge50', 'top_bursty_types')})
            print('CTRL even', v['burstiness']['top_even_types_freq_ge50'])
            print('CTRL bursty', v['burstiness']['top_bursty_types'])
            print('CTRL conc', v['concentration_f5_share50'])
            print('CTRL para', json.dumps(v['paragraph_novelty_min3']))
            print('CTRL pages', json.dumps(v['page_specific_types'])[:1500])

    with open(os.path.join(DATA, 'attack240_vocabulary_dynamics.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('wrote data/attack240_vocabulary_dynamics.json')


if __name__ == '__main__':
    main()
