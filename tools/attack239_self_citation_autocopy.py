"""Attack 239 - Independent test of the Timm & Schinner "self-citation" hypothesis.

Hypothesis (Timm & Schinner 2019/2020): each Voynich word was produced by copying a
word seen recently on the same page (often the line directly above, near the same
horizontal position) and modifying it slightly.

Testable predictions on running text (unit == 'P', clean words only):
  1. Distance decay: a token's minimum Levenshtein distance to the words of a line
     d lines back grows with d, more steeply than when the folio's line order is
     shuffled (null c), and the local similarity exceeds what the vocabulary of other
     folios of the same Currier language / hand / section gives (null a).
  2. Backward > forward asymmetry (null b): the line(s) *above* a token contain closer
     relatives than the line(s) *below*, for the same token, at the same lag, with the
     candidate-set size equalised exactly (hypergeometric expectation of the minimum
     over a random size-m subset).
  3. Vertical alignment: in the line directly above, the most similar word sits at a
     similar relative horizontal position, more than under word-position shuffling and
     more than at lags 2-5 / in other-folio lines (which control for positional
     morphology such as line-initial and line-final word forms).
  4. Stratification by Currier language, Davis hand and section.

Two glyph schemes: raw EVA characters, and a "unit" scheme where
ch/sh/cth/ckh/cph/cfh/ain/aiin/aiiin are single symbols.

Pure Python (no numpy available in this environment). Runtime ~ a few minutes.
Outputs: data/attack239_self_citation_autocopy.json
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voynich_corpus import ROOT, _is_uncertain, load_lines, paragraphs  # noqa: E402

MAXLAG = 10
MAXWIN = 5          # window sizes used for the asymmetry test
ALIGN_LAGS = 5
SEED = 239
NBOOT = 1000
NFLIP = 10000
UNIT_MAP = [('aiiin', 'N'), ('aiin', 'M'), ('ain', 'L'), ('cth', 'T'), ('ckh', 'K'),
            ('cph', 'P'), ('cfh', 'F'), ('ch', 'C'), ('sh', 'S')]
OUT = os.path.join(ROOT, 'data', 'attack239_self_citation_autocopy.json')


def to_units(w: str) -> str:
    for a, b in UNIT_MAP:
        w = w.replace(a, b)
    return w


def lev(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    lb = len(b)
    if lb == 0:
        return len(a)
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        left = i
        for j in range(lb):
            x = prev[j] + (ca != b[j])
            y = prev[j + 1] + 1
            if y < x:
                x = y
            y = left + 1
            if y < x:
                x = y
            cur.append(x)
            left = x
        prev = cur
    return prev[-1]


@lru_cache(maxsize=None)
def comb(n: int, k: int) -> int:
    return math.comb(n, k)


def hyper_stats(A, m):
    """Expected min, P(min==0), P(min<=1) over a uniformly random m-subset of A."""
    n = len(A)
    if m >= n:
        mn = min(A)
        return float(mn), float(mn == 0), float(mn <= 1)
    cnt = Counter(A)
    total = comb(n, m)
    below = 0
    E = 0.0
    p0 = p1 = 1.0
    for t in range(1, max(A) + 1):
        below += cnt.get(t - 1, 0)
        p = comb(n - below, m) / total if n - below >= m else 0.0   # P(min >= t)
        if t == 1:
            p0 = 1.0 - p
        elif t == 2:
            p1 = 1.0 - p
        E += p
        if p == 0.0:
            break
    if max(A) < 2 and p0 < 1.0:
        p1 = 1.0
    return E, p0, p1


# ----------------------------------------------------------------------------
# corpus
# ----------------------------------------------------------------------------

def build_corpus(scheme: str):
    all_lines = load_lines()
    pid = {}
    for i, p in enumerate(paragraphs(all_lines)):
        for l in p:
            pid[id(l)] = i
    conv = to_units if scheme == 'units' else (lambda w: w)
    folios = {}
    for l in all_lines:
        if l.unit != 'P':
            continue
        words = l.words
        n = len(words)
        lens = [len(w) for w in words]
        total = sum(lens) + max(0, n - 1)
        start = 0
        types, rc, rw, inter = [], [], [], []
        for k, w in enumerate(words):
            c = (start + lens[k] / 2.0) / total if total else 0.5
            start += lens[k] + 1
            if w and not _is_uncertain(w):
                types.append(conv(w))
                rc.append(c)
                rw.append((k + 0.5) / n)
                inter.append(0 < k < n - 1)
        folios.setdefault(l.folio, []).append(dict(
            folio=l.folio, locus=l.locus, para=(l.folio, pid.get(id(l))), types=types,
            rc=rc, rw=rw, inter=inter, lang=l.lang, hand=l.hand, section=l.section))
    for L in folios.values():
        for i, r in enumerate(L):
            r['pfirst'] = i == 0 or L[i - 1]['para'] != r['para']
            r['plast'] = i == len(L) - 1 or L[i + 1]['para'] != r['para']
    return folios


class Dist:
    def __init__(self):
        self.ids = {}
        self.cache = {}

    def gid(self, t):
        i = self.ids.get(t)
        if i is None:
            i = self.ids[t] = len(self.ids)
        return i

    def __call__(self, a, b):
        if a == b:
            return 0
        ia, ib = self.gid(a), self.gid(b)
        key = (ia << 20) | ib if ia < ib else (ib << 20) | ia
        v = self.cache.get(key)
        if v is None:
            v = self.cache[key] = lev(a, b)
        return v


def groups_of(meta):
    lang, hand, sec = meta
    g = ['all']
    if lang in ('A', 'B'):
        g.append('L:' + lang)
    if hand in '12345' and hand:
        g.append('H:' + hand)
    if sec and sec != '?':
        g.append('I:' + sec)
    combo = f'{lang}{hand}{sec}'
    if combo in ('A1H', 'B2B', 'B3S', 'B2H', 'A1P', 'B2T'):
        g.append('LHI:' + combo)
    return g


# ----------------------------------------------------------------------------
# main analysis for one scheme
# ----------------------------------------------------------------------------

def analyse(scheme: str, nperm: int, rng: random.Random):
    t0 = time.time()
    folios = build_corpus(scheme)
    dist = Dist()

    # stratum index for cross-folio null: key -> nclean -> list of line recs
    strata = defaultdict(lambda: defaultdict(list))
    for f, L in folios.items():
        for r in L:
            if r['types']:
                for key in ((r['lang'], r['hand'], r['section']), (r['lang'], r['section']), (r['lang'],), ()):
                    strata[key][len(r['types'])].append(r)

    def cross_line(r, n):
        f = r['folio']
        for key in ((r['lang'], r['hand'], r['section']), (r['lang'], r['section']), (r['lang'],), ()):
            byn = strata.get(key)
            if not byn:
                continue
            for delta in (0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5):
                cands = byn.get(n + delta)
                if not cands:
                    continue
                for _ in range(8):
                    c = rng.choice(cands)
                    if c['folio'] != f:
                        return c
                other = [c for c in cands if c['folio'] != f]
                if other:
                    return rng.choice(other)
        return None

    acc = {}           # folio -> defaultdict(float)
    fmeta = {}
    fdata = {}         # folio -> (n_lines, para list, tok_li, tok_mind)
    examples = []
    for f, L in folios.items():
        A = acc[f] = defaultdict(float)
        r0 = L[0]
        fmeta[f] = (r0['lang'], r0['hand'], r0['section'])
        n = len(L)
        ftypes = sorted({t for r in L for t in r['types']})
        loc = {t: i for i, t in enumerate(ftypes)}
        V = len(ftypes)
        Dm = [[0] * V for _ in range(V)]
        for i in range(V):
            ti = ftypes[i]
            row = Dm[i]
            for j in range(i + 1, V):
                d = dist(ti, ftypes[j])
                row[j] = d
                Dm[j][i] = d
        lloc = [[loc[t] for t in r['types']] for r in L]
        tok_li, tok_mind = [], []
        for li, r in enumerate(L):
            for k, u in enumerate(lloc[li]):
                row = Dm[u]
                dl = [list(map(row.__getitem__, lloc[l])) if (l != li and lloc[l]) else None
                      for l in range(n)]
                mind = [min(x) if x else None for x in dl]
                tok_li.append(li)
                tok_mind.append(mind)
                A['ntok'] += 1
                # ---------- observed backward / forward decay, windows
                wb = wf = None
                for d in range(1, MAXLAG + 1):
                    if li - d >= 0:
                        v = mind[li - d]
                        if v is not None:
                            A[f'ob_min_{d}'] += v; A[f'ob_n0_{d}'] += v == 0
                            A[f'ob_n1_{d}'] += v <= 1; A[f'ob_c_{d}'] += 1
                            wb = v if wb is None or v < wb else wb
                        if wb is not None:
                            A[f'wb_min_{d}'] += wb; A[f'wb_n0_{d}'] += wb == 0
                            A[f'wb_n1_{d}'] += wb <= 1; A[f'wb_c_{d}'] += 1
                    if li + d < n:
                        v = mind[li + d]
                        if v is not None:
                            A[f'of_min_{d}'] += v; A[f'of_n0_{d}'] += v == 0
                            A[f'of_n1_{d}'] += v <= 1; A[f'of_c_{d}'] += 1
                            wf = v if wf is None or v < wf else wf
                        if wf is not None:
                            A[f'wf_min_{d}'] += wf; A[f'wf_n0_{d}'] += wf == 0
                            A[f'wf_n1_{d}'] += wf <= 1; A[f'wf_c_{d}'] += 1
                # ---------- null (a): cross-folio same-stratum, candidate-count matched
                wc = None
                xline1 = None
                for d in range(1, MAXLAG + 1):
                    if li - d < 0:
                        break
                    if not lloc[li - d]:
                        if wc is not None:
                            A[f'wcr_min_{d}'] += wc; A[f'wcr_n0_{d}'] += wc == 0
                            A[f'wcr_n1_{d}'] += wc <= 1; A[f'wcr_c_{d}'] += 1
                        continue
                    xl = cross_line(r, len(lloc[li - d]))
                    if xl is None:
                        continue
                    if d == 1:
                        xline1 = xl
                    tt = r['types'][k]
                    v = min(dist(tt, w) for w in xl['types'])
                    A[f'cr_min_{d}'] += v; A[f'cr_n0_{d}'] += v == 0
                    A[f'cr_n1_{d}'] += v <= 1; A[f'cr_c_{d}'] += 1
                    wc = v if wc is None or v < wc else wc
                    A[f'wcr_min_{d}'] += wc; A[f'wcr_n0_{d}'] += wc == 0
                    A[f'wcr_n1_{d}'] += wc <= 1; A[f'wcr_c_{d}'] += 1
                # ---------- null (b): backward vs forward, size-matched, paired
                for d in range(1, MAXLAG + 1):
                    if li - d < 0 or li + d >= n:
                        break
                    Ab, Af = dl[li - d], dl[li + d]
                    if not Ab or not Af:
                        continue
                    m = min(len(Ab), len(Af))
                    eb, b0, b1 = hyper_stats(Ab, m)
                    ef, f0, f1 = hyper_stats(Af, m)
                    same = L[li - d]['para'] == r['para'] == L[li + d]['para']
                    core = same and not L[li - d]['pfirst'] and not L[li + d]['plast']
                    for var in (('all', 'par', 'cor') if core else ('all', 'par') if same else ('all',)):
                        A[f'as_{var}_{d}_dE'] += ef - eb
                        A[f'as_{var}_{d}_dP0'] += b0 - f0
                        A[f'as_{var}_{d}_dP1'] += b1 - f1
                        A[f'as_{var}_{d}_c'] += 1
                for w in range(1, MAXWIN + 1):
                    if li - w < 0 or li + w >= n:
                        break
                    Ab = [x for l in range(li - w, li) if dl[l] for x in dl[l]]
                    Af = [x for l in range(li + 1, li + w + 1) if dl[l] for x in dl[l]]
                    if not Ab or not Af:
                        continue
                    m = min(len(Ab), len(Af))
                    eb, b0, b1 = hyper_stats(Ab, m)
                    ef, f0, f1 = hyper_stats(Af, m)
                    same = all(L[l]['para'] == r['para'] for l in range(li - w, li + w + 1))
                    core = same and not L[li - w]['pfirst'] and not L[li + w]['plast']
                    for var in (('all', 'par', 'cor') if core else ('all', 'par') if same else ('all',)):
                        A[f'aw_{var}_{w}_dE'] += ef - eb
                        A[f'aw_{var}_{w}_dP0'] += b0 - f0
                        A[f'aw_{var}_{w}_dP1'] += b1 - f1
                        A[f'aw_{var}_{w}_c'] += 1
                # ---------- within-line (lag 0) asymmetry: w words to the left vs right,
                # all interior (no line-initial / line-final words), equal candidate counts
                ll = lloc[li]
                inter = r['inter']
                for w in (1, 2, 3):
                    if k - w < 0 or k + w >= len(ll):
                        break
                    if not all(inter[q] for q in range(k - w, k + w + 1)):
                        break
                    lb = min(row[ll[q]] for q in range(k - w, k))
                    lf = min(row[ll[q]] for q in range(k + 1, k + w + 1))
                    A[f'il_{w}_dE'] += lf - lb
                    A[f'il_{w}_dP0'] += (lb == 0) - (lf == 0)
                    A[f'il_{w}_dP1'] += (lb <= 1) - (lf <= 1)
                    A[f'il_{w}_c'] += 1
                # ---------- vertical alignment (lags 1..5 back + cross-folio line)
                targets = [(str(d), L[li - d], dl[li - d]) for d in range(1, ALIGN_LAGS + 1)
                           if li - d >= 0 and dl[li - d]]
                if xline1 is not None:
                    tt = r['types'][k]
                    targets.append(('X', xline1, [dist(tt, w) for w in xline1['types']]))
                for tag, lr, ds in targets:
                    for var in ('all', 'strict'):
                        if var == 'all':
                            idx = list(range(len(ds)))
                        else:
                            if not r['inter'][k]:
                                continue
                            idx = [q for q in range(len(ds)) if lr['inter'][q]]
                            if len(idx) < 2:
                                continue
                        best = min(ds[q] for q in idx)
                        if var == 'strict' and best > 1:
                            continue
                        S = [q for q in idx if ds[q] == best]
                        if len(S) == len(idx):
                            continue
                        for mode, key in (('c', 'rc'), ('w', 'rw')):
                            rx = r[key][k]
                            pos = lr[key]
                            obs = sum(abs(rx - pos[q]) for q in S) / len(S)
                            exp = sum(abs(rx - pos[q]) for q in idx) / len(idx)
                            A[f'al_{tag}_{var}_{mode}_s'] += obs - exp
                            A[f'al_{tag}_{var}_{mode}_o'] += obs
                            A[f'al_{tag}_{var}_{mode}_e'] += exp
                        A[f'al_{tag}_{var}_c'] += 1
                        if tag == '1' and var == 'strict' and best == 1 and len(examples) < 40 \
                                and rng.random() < 0.01:
                            q = S[0]
                            examples.append(dict(token=r['types'][k], locus=r['locus'], pos=k,
                                                 above=lr['types'][q], above_locus=lr['locus'], above_pos=q))
        paras = [r['para'] for r in L]
        fdata[f] = (n, paras, tok_li, tok_mind)
    t_obs = time.time() - t0
    print(f'[{scheme}] observed + cross + asym + align done in {t_obs:.1f}s; '
          f'{len(dist.cache)} cached type pairs', flush=True)

    # ---------- null (c): shuffled line order (whole folio) and within-paragraph
    perm_records = {'sh': [], 'ps': []}
    for null in ('sh', 'ps'):
        for p in range(nperm):
            rec = {}
            for f, (n, paras, tok_li, tok_mind) in fdata.items():
                A = acc[f]
                if null == 'sh':
                    order = list(range(n))
                    rng.shuffle(order)
                else:
                    order = []
                    blk = []
                    for i in range(n):
                        if blk and paras[i] != paras[blk[-1]]:
                            rng.shuffle(blk)
                            order.extend(blk)
                            blk = []
                        blk.append(i)
                    rng.shuffle(blk)
                    order.extend(blk)
                # order[newpos] = old line index; pos[old] = newpos
                pos = [0] * n
                for npos, old in enumerate(order):
                    pos[old] = npos
                s = defaultdict(float)
                for li, mind in zip(tok_li, tok_mind):
                    pp = pos[li]
                    wb = None
                    for d in range(1, min(MAXLAG, pp) + 1):
                        v = mind[order[pp - d]]
                        if v is not None:
                            s[f'min_{d}'] += v; s[f'n0_{d}'] += v == 0
                            s[f'n1_{d}'] += v <= 1; s[f'c_{d}'] += 1
                            wb = v if wb is None or v < wb else wb
                        if wb is not None:
                            s[f'wmin_{d}'] += wb; s[f'wn0_{d}'] += wb == 0
                            s[f'wn1_{d}'] += wb <= 1; s[f'wc_{d}'] += 1
                for key, v in s.items():
                    if key[0] == 'w':
                        A[f'w{null}_{key[1:]}'] += v / nperm
                    else:
                        A[f'{null}_{key}'] += v / nperm
                far_n1 = sum(s[f'n1_{d}'] for d in range(6, MAXLAG + 1))
                far_c = sum(s[f'c_{d}'] for d in range(6, MAXLAG + 1))
                rec[f] = (s['min_1'], s['n1_1'], s['n0_1'], s['c_1'], far_n1, far_c)
            perm_records[null].append(rec)
        print(f'[{scheme}] null {null}: {nperm} permutations done at {time.time() - t0:.1f}s', flush=True)

    return dict(acc=acc, fmeta=fmeta, perm=perm_records, examples=examples,
                n_types=len(dist.ids), n_pairs=len(dist.cache), runtime_s=time.time() - t0)


# ----------------------------------------------------------------------------
# statistics helpers
# ----------------------------------------------------------------------------

def tot(acc, fl, keys):
    out = dict.fromkeys(keys, 0.0)
    for f in fl:
        a = acc[f]
        for k in keys:
            out[k] += a.get(k, 0.0)
    return out


def bootstrap_multi(acc, fl, keys, fns, rng, B=NBOOT):
    """Folio-cluster bootstrap; one set of resamples shared by all statistics in fns."""
    cols = [[acc[f].get(k, 0.0) for f in fl] for k in keys]
    n = len(fl)
    vals = {name: [] for name in fns}
    for _ in range(B):
        idx = [rng.randrange(n) for _i in range(n)]
        s = dict(zip(keys, (sum(col[i] for i in idx) for col in cols)))
        for name, fn in fns.items():
            try:
                v = fn(s)
            except ZeroDivisionError:
                continue
            if v == v:
                vals[name].append(v)
    out = {}
    for name, vs in vals.items():
        vs.sort()
        out[name] = [vs[int(0.025 * len(vs))], vs[min(len(vs) - 1, int(0.975 * len(vs)))]] if vs else [None, None]
    return out


def bootstrap(acc, fl, keys, fn, rng, B=NBOOT):
    return bootstrap_multi(acc, fl, keys, {'x': fn}, rng, B)['x']


def signflip(contribs, rng, nflip=NFLIP):
    obs = sum(contribs)
    ge = 0
    for _ in range(nflip):
        s = sum(c if rng.random() < 0.5 else -c for c in contribs)
        if abs(s) >= abs(obs) - 1e-12:
            ge += 1
    return (ge + 1) / (nflip + 1)


def r6(x):
    return None if x is None else round(x, 6)


def ratio(t, a, b):
    return t[a] / t[b] if t[b] else None


def summarise(res, rng, full=True):
    acc, fmeta, perm = res['acc'], res['fmeta'], res['perm']
    allf = list(acc)
    G = defaultdict(list)
    for f in allf:
        for g in groups_of(fmeta[f]):
            G[g].append(f)

    out = {'n_folios': len(allf), 'n_tokens': int(sum(acc[f]['ntok'] for f in allf)),
           'n_types': res['n_types'], 'n_type_pairs_computed': res['n_pairs'],
           'runtime_s': round(res['runtime_s'], 1)}

    # ---- decay tables (all folios)
    decay, window = [], []
    for d in range(1, MAXLAG + 1):
        row = {'lag': d}
        for pre, name in (('ob', 'backward_observed'), ('of', 'forward_observed'),
                          ('sh', 'backward_shuffled_lines'), ('ps', 'backward_shuffled_within_paragraph'),
                          ('cr', 'cross_folio_same_stratum')):
            keys = [f'{pre}_min_{d}', f'{pre}_n0_{d}', f'{pre}_n1_{d}', f'{pre}_c_{d}']
            t = tot(acc, allf, keys)
            c = t[keys[3]]
            row[name] = {'mean_min_dist': r6(t[keys[0]] / c) if c else None,
                         'frac_exact': r6(t[keys[1]] / c) if c else None,
                         'frac_le1': r6(t[keys[2]] / c) if c else None, 'n': round(c)}
        decay.append(row)
        roww = {'window_k': d}
        for pre, name in (('wb', 'backward_observed'), ('wf', 'forward_observed'),
                          ('wsh', 'backward_shuffled_lines'), ('wps', 'backward_shuffled_within_paragraph'),
                          ('wcr', 'cross_folio_same_stratum')):
            keys = [f'{pre}_min_{d}', f'{pre}_n0_{d}', f'{pre}_n1_{d}', f'{pre}_c_{d}']
            t = tot(acc, allf, keys)
            c = t[keys[3]]
            roww[name] = {'mean_min_dist': r6(t[keys[0]] / c) if c else None,
                          'frac_exact': r6(t[keys[1]] / c) if c else None,
                          'frac_le1': r6(t[keys[2]] / c) if c else None, 'n': round(c)}
        window.append(roww)
    out['decay_by_lag'] = decay
    out['window_k_lines_back'] = window

    # ---- asymmetry tables
    asym = []
    vname = {'all': 'all_lines', 'par': 'same_paragraph', 'cor': 'same_paragraph_no_boundary_lines'}
    specs = [('lag', d, f'as_{v}_{d}', v) for d in range(1, MAXLAG + 1) for v in ('all', 'par', 'cor')] + \
            [('window', d, f'aw_{v}_{d}', v) for d in range(1, MAXWIN + 1) for v in ('all', 'par', 'cor')] + \
            [('within_line_interior', w, f'il_{w}', 'all') for w in (1, 2, 3)]
    for kind, d, base, var in specs:
        keys = [f'{base}_dE', f'{base}_dP0', f'{base}_dP1', f'{base}_c']
        t = tot(acc, allf, keys)
        c = t[keys[3]]
        if not c:
            continue
        row = {'kind': kind, 'd': d, 'variant': vname[var] if kind != 'within_line_interior' else 'interior_words',
               'n_tokens': round(c),
               'fwd_minus_bwd_expected_min_dist': r6(t[keys[0]] / c),
               'bwd_minus_fwd_P_exact': r6(t[keys[1]] / c),
               'bwd_minus_fwd_P_le1': r6(t[keys[2]] / c)}
        if full or (d in (1, 3) and var in ('par', 'cor')) or kind == 'within_line_interior':
            cis = bootstrap_multi(acc, allf, keys, {
                'min': lambda s, k=keys: s[k[0]] / s[k[3]],
                'le1': lambda s, k=keys: s[k[2]] / s[k[3]]}, rng, 500)
            row['ci95_fwd_minus_bwd_min'] = [r6(x) for x in cis['min']]
            row['ci95_bwd_minus_fwd_P_le1'] = [r6(x) for x in cis['le1']]
            row['signflip_p_min'] = r6(signflip([acc[f].get(keys[0], 0.0) for f in allf], rng, 2000))
            row['signflip_p_le1'] = r6(signflip([acc[f].get(keys[2], 0.0) for f in allf], rng, 2000))
        asym.append(row)
    out['asymmetry_backward_vs_forward'] = asym

    # ---- alignment table
    align = []
    for tag in [str(d) for d in range(1, ALIGN_LAGS + 1)] + ['X']:
        for var in ('all', 'strict'):
            for mode in ('c', 'w'):
                keys = [f'al_{tag}_{var}_{mode}_s', f'al_{tag}_{var}_{mode}_o', f'al_{tag}_{var}_{mode}_e',
                        f'al_{tag}_{var}_c']
                t = tot(acc, allf, keys)
                c = t[keys[3]]
                if not c:
                    continue
                row = {'line': 'cross_folio_matched' if tag == 'X' else f'lag_{tag}', 'variant': var,
                       'position': 'char_centre' if mode == 'c' else 'word_index', 'n': round(c),
                       'mean_obs_abs_dpos': r6(t[keys[1]] / c), 'mean_shuffle_expected_abs_dpos': r6(t[keys[2]] / c),
                       'obs_minus_expected': r6(t[keys[0]] / c)}
                if full or tag in ('1', 'X'):
                    row['ci95'] = [r6(x) for x in bootstrap(acc, allf, [keys[0], keys[3]],
                                                             lambda s, k=keys: s[k[0]] / s[k[3]], rng, 500)]
                align.append(row)
    out['vertical_alignment'] = align

    # ---- key effects per group
    def decay_effects(fl, g):
        e = {'n_folios': len(fl), 'n_tokens': int(sum(acc[f]['ntok'] for f in fl))}
        k1 = ['ob_n1_1', 'ob_c_1', 'sh_n1_1', 'sh_c_1', 'ps_n1_1', 'ps_c_1', 'cr_n1_1', 'cr_c_1',
              'ob_min_1', 'sh_min_1', 'cr_min_1', 'ob_n0_1', 'sh_n0_1', 'cr_n0_1', 'ps_min_1']
        far = [f'{p}_{s}_{d}' for p in ('ob', 'sh') for s in ('n1', 'c') for d in range(6, MAXLAG + 1)]
        keys = k1 + far
        t = tot(acc, fl, keys)
        if not t['ob_c_1']:
            return e

        def p1(t, p):
            return t[f'{p}_n1_1'] / t[f'{p}_c_1']

        def far1(t, p):
            c = sum(t[f'{p}_c_{d}'] for d in range(6, MAXLAG + 1))
            return sum(t[f'{p}_n1_{d}'] for d in range(6, MAXLAG + 1)) / c if c else float('nan')

        fns = {
            'lag1_frac_le1_observed': lambda t: p1(t, 'ob'),
            'lag1_frac_le1_shuffled': lambda t: p1(t, 'sh'),
            'lag1_frac_le1_para_shuffled': lambda t: p1(t, 'ps'),
            'lag1_frac_le1_cross_folio': lambda t: p1(t, 'cr'),
            'excess_le1_vs_shuffle': lambda t: p1(t, 'ob') - p1(t, 'sh'),
            'excess_le1_vs_para_shuffle': lambda t: p1(t, 'ob') - p1(t, 'ps'),
            'excess_le1_vs_cross_folio': lambda t: p1(t, 'ob') - p1(t, 'cr'),
            'folio_topic_effect_shuffle_minus_cross': lambda t: p1(t, 'sh') - p1(t, 'cr'),
            'excess_exact_vs_shuffle': lambda t: t['ob_n0_1'] / t['ob_c_1'] - t['sh_n0_1'] / t['sh_c_1'],
            'reduction_mean_min_vs_shuffle': lambda t: t['sh_min_1'] / t['sh_c_1'] - t['ob_min_1'] / t['ob_c_1'],
            'reduction_mean_min_vs_para_shuffle': lambda t: t['ps_min_1'] / t['ps_c_1'] - t['ob_min_1'] / t['ob_c_1'],
            'reduction_mean_min_vs_cross_folio': lambda t: t['cr_min_1'] / t['cr_c_1'] - t['ob_min_1'] / t['ob_c_1'],
            'decay_contrast_le1_lag1_minus_lag6to10_observed': lambda t: p1(t, 'ob') - far1(t, 'ob'),
            'decay_contrast_le1_lag1_minus_lag6to10_shuffled': lambda t: p1(t, 'sh') - far1(t, 'sh'),
        }
        ci_fns = {k: v for k, v in fns.items() if k.startswith(('excess', 'reduction', 'decay', 'folio'))}
        cis = bootstrap_multi(acc, fl, keys, ci_fns, rng, NBOOT if g == 'all' else 400)
        for name, fn in fns.items():
            try:
                v = fn(t)
            except ZeroDivisionError:
                v = None
            ci = cis.get(name)
            e[name] = {'value': r6(v), 'ci95': [r6(x) for x in ci]} if ci else r6(v)
        # permutation p-values from the shuffle distributions (one-sided: observed > null)
        for null, lab in (('sh', 'shuffled_lines'), ('ps', 'shuffled_within_paragraph')):
            o_p1 = p1(t, 'ob')
            o_far = far1(t, 'ob')
            o_con = o_p1 - o_far
            ge1 = gec = 0
            dist_p1 = []
            for rec in perm[null]:
                s_min, s_n1, s_n0, s_c, s_fn1, s_fc = (sum(rec[f][i] for f in fl) for i in range(6))
                v = s_n1 / s_c
                dist_p1.append(v)
                ge1 += v >= o_p1
                if s_fc and null == 'sh':
                    gec += (v - s_fn1 / s_fc) >= o_con
            np_ = len(perm[null])
            mu = sum(dist_p1) / np_
            sd = (sum((x - mu) ** 2 for x in dist_p1) / max(1, np_ - 1)) ** 0.5
            e[f'perm_{lab}'] = {'p_lag1_le1': r6((ge1 + 1) / (np_ + 1)),
                                'z_lag1_le1': r6((o_p1 - mu) / sd) if sd else None}
            if null == 'sh':
                e[f'perm_{lab}']['p_decay_contrast'] = r6((gec + 1) / (np_ + 1))
        # asymmetry (same paragraph, lag 1 and window 3; all lines lag 1)
        for base, name in (('as_all_1', 'asym_lag1_all'), ('as_par_1', 'asym_lag1_par'),
                           ('as_cor_1', 'asym_lag1_core'), ('aw_cor_3', 'asym_window3_core'),
                           ('il_2', 'asym_within_line_w2')):
            keys = [f'{base}_dE', f'{base}_dP1', f'{base}_c']
            tt = tot(acc, fl, keys)
            if not tt[keys[2]]:
                continue
            cis = bootstrap_multi(acc, fl, keys, {'min': lambda s, k=keys: s[k[0]] / s[k[2]],
                                                  'le1': lambda s, k=keys: s[k[1]] / s[k[2]]}, rng, 400)
            e[name] = {
                'n': round(tt[keys[2]]),
                'fwd_minus_bwd_min': r6(tt[keys[0]] / tt[keys[2]]),
                'ci95_min': [r6(x) for x in cis['min']],
                'bwd_minus_fwd_le1': r6(tt[keys[1]] / tt[keys[2]]),
                'ci95_le1': [r6(x) for x in cis['le1']],
                'signflip_p_min': r6(signflip([acc[f].get(keys[0], 0.0) for f in fl], rng, 2000)),
            }
        # alignment lag1 vs lags 2-5 vs cross (strict, char position)
        for var in ('all', 'strict'):
            keys = [f'al_{tag}_{var}_c_{x}' for tag in ('1', '2', '3', '4', '5', 'X') for x in ('s',)] + \
                   [f'al_{tag}_{var}_c' for tag in ('1', '2', '3', '4', '5', 'X')]
            tt = tot(acc, fl, keys)
            if not tt[f'al_1_{var}_c']:
                continue

            def a1(s, var=var):
                return s[f'al_1_{var}_c_s'] / s[f'al_1_{var}_c']

            def a25(s, var=var):
                return sum(s[f'al_{t}_{var}_c_s'] for t in '2345') / sum(s[f'al_{t}_{var}_c'] for t in '2345')

            def ax(s, var=var):
                return s[f'al_X_{var}_c_s'] / s[f'al_X_{var}_c']
            ent = {'n_lag1': round(tt[f'al_1_{var}_c'])}
            afns = {'lag1_obs_minus_exp': a1, 'lag2to5_obs_minus_exp': a25, 'cross_obs_minus_exp': ax,
                    'lag1_minus_lag2to5': lambda s, a1=a1, a25=a25: a1(s) - a25(s),
                    'lag1_minus_cross': lambda s, a1=a1, ax=ax: a1(s) - ax(s)}
            acis = bootstrap_multi(acc, fl, keys, afns, rng, 400)
            for nm, fn in afns.items():
                try:
                    v = fn(tt)
                except ZeroDivisionError:
                    v = None
                ent[nm] = {'value': r6(v), 'ci95': [r6(x) for x in acis[nm]]}
            e[f'alignment_{var}_char'] = ent
        return e

    order = ['all', 'L:A', 'L:B', 'H:1', 'H:2', 'H:3', 'H:4', 'H:5',
             'I:H', 'I:S', 'I:B', 'I:P', 'I:T', 'I:C', 'I:A',
             'LHI:A1H', 'LHI:A1P', 'LHI:B2B', 'LHI:B2H', 'LHI:B2T', 'LHI:B3S']
    groups_to_do = order if full else ['all', 'L:A', 'L:B']
    out['effects_by_group'] = {g: decay_effects(G[g], g) for g in groups_to_do if G.get(g)}
    out['alignment_examples_lag1_one_edit'] = res['examples'][:20]
    return out


def main():
    rng = random.Random(SEED)
    result = {
        'attack': 239,
        'title': 'Self-citation / auto-copying test (Timm & Schinner) with shuffle, cross-folio, forward and positional nulls',
        'config': {'source': 'data/ZL3b-n.txt via tools/voynich_corpus.py', 'unit': 'P (running text), clean words only',
                   'max_lag': MAXLAG, 'max_window_asym': MAXWIN, 'align_lags': ALIGN_LAGS, 'seed': SEED,
                   'n_boot_all': NBOOT, 'unit_scheme_map': UNIT_MAP,
                   'notes': ['min distance = minimum glyph-level Levenshtein distance to words of the comparison line(s)',
                             'asymmetry uses exact hypergeometric expected minimum over a random subset of size '
                             'm = min(n_back, n_forward) so both sides have identical candidate counts',
                             'cross-folio null draws a running-text line of the same clean-word count from a different '
                             'folio of the same (language, hand, section); fallback (language, section) -> language -> all',
                             'CIs are folio-cluster bootstrap percentiles; asymmetry p-values are folio-level sign-flip '
                             '(time-reversal) tests; shuffle p-values are one-sided permutation tests',
                             'alignment: rel. position of best-matching word(s) in comparison line vs token position; '
                             'expected value is exact under random permutation of word slots in that line; '
                             'strict = token and candidates interior (not line-initial/final) and best distance <= 1']},
        'schemes': {},
    }
    quick = '--quick' in sys.argv
    plan = (('eva_chars', 3, True),) if quick else (('eva_chars', 100, True), ('units', 40, False))
    for scheme, nperm, full in plan:
        res = analyse(scheme, nperm, rng)
        result['schemes'][scheme] = summarise(res, rng, full=full)
        result['schemes'][scheme]['n_permutations_per_null'] = nperm
        print(f'[{scheme}] summarised', flush=True)
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump(result, fh, indent=1)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
