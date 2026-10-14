"""Attack 241 - Within-line word-to-word dependency, definite (.) vs uncertain (,)
word spaces, morphological slot coupling across lags d=1..6, drawing-intrusion
(<->) boundary reset, and natural-language / generative controls.

Research question:
Why do adjacent words within a Voynich line show such strong final-glyph -> initial-glyph
dependency (excess MI ~ +0.204 bits, z ~ +45.5 in Attack 238), whereas across a physical
line break this dependency collapses to zero (excess MI ~ -0.001 bits, z = -0.32)?
Is within-line coupling an artifact of uncertain narrow spaces (','), or does it survive
across unambiguous definite spaces ('.') and multi-transcriber consensus spaces? Which
morphological slots couple across lags d=1..6, and what happens when a line jumps over
a botanical/anatomical drawing intrusion (<->) mid-line?

Five empirical tests (all stratified by Currier language A/B x section $I):
  T1  Definite (.) vs uncertain (,) word spaces, ','-merged corpus test,
      cross-transcriber (ZL3b + IT2a + RF1b) consensus definite-space test,
      and top (final_glyph, initial_glyph) & word-pair PMI drivers.
  T2  3x3 morphological slot coupling matrix (init, core, final) at lag d=1,
      lag decay curves for d=1..6 under both within-line and within-stratum
      permutation nulls, and comparison with intra-word slot coupling.
  T3  Mid-line drawing intrusion (w_k <-> w_{k+1}) natural experiment:
      pre-intrusion w_k vs line-final/interior (MH odds ratios),
      post-intrusion w_{k+1} vs line-initial/interior (MH odds ratios),
      and cross-intrusion juncture excess MI vs matched interior and cross-line pairs.
  T4  Natural-language controls (Caesar Latin De Bello Gallico, Culpeper English
      Herbal) and synthetic generative controls (independent word-slot model vs
      within-line state-coupled sandhi generator with line-break reset).
  T5  Selection of diagnostic manuscript loci and quantitative gap/intrusion metrics
      for high-resolution visual forensics and summary plots (pages/s241_*.png).

Output:
  data/attack241_within_line_sandhi_and_spaces.json
  pages/s241_*.png
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import tempfile
import urllib.request
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voynich_corpus import DATA, ROOT, Line, load_lines, paragraphs  # noqa: E402

OUT_JSON = os.path.join(ROOT, 'data', 'attack241_within_line_sandhi_and_spaces.json')
PAGES_DIR = os.path.join(ROOT, 'pages')

EVA_MULTI = ('cth', 'ckh', 'cph', 'cfh', 'ch', 'sh')
VOY_SUFFIXES_2 = ('dy', 'in', 'ol', 'ar', 'or', 'al', 'ey', 'am', 'an', 'ai', 'oi')


# ---------------------------------------------------------------------------
# Glyph & Morphological Slot Decomposition
# ---------------------------------------------------------------------------
def is_clean(w: str) -> bool:
    return bool(w) and not any(c in w for c in "?'*")


def glyphs(w: str, alpha: str = 'eva') -> List[str]:
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


def first_glyph(w: str, alpha: str = 'eva') -> str:
    return glyphs(w, alpha)[0]


def last_glyph(w: str, alpha: str = 'eva') -> str:
    return w[-1]


def decompose_slots(w: str, alpha: str = 'eva') -> Tuple[str, str, str]:
    """Decompose a word into (init_glyph, core_class, final_glyph).
    Also classifies the medial core after stripping the first glyph and last char
    into a compact structural class so 3x3 MI comparisons have matched cardinality."""
    gs = glyphs(w, alpha)
    ig = gs[0]
    fg = w[-1]
    if len(gs) <= 1:
        core_raw = ''
    elif len(gs) == 2:
        core_raw = ''
    else:
        core_raw = ''.join(gs[1:-1])

    # Canonical core class (captures gallows, bench, vowel-bench, diphthong, liquid, bare)
    if not core_raw:
        c_cls = '<EMPTY>'
    elif any(m in core_raw for m in ('cth', 'ckh', 'cph', 'cfh')):
        c_cls = 'BENCH_GALLOWS'
    elif any(g in core_raw for g in ('k', 't', 'p', 'f')):
        if 'ch' in core_raw or 'sh' in core_raw:
            c_cls = 'GALLOWS+CH'
        elif 'e' in core_raw:
            c_cls = 'GALLOWS+E'
        elif 'o' in core_raw or 'a' in core_raw:
            c_cls = 'GALLOWS+O/A'
        else:
            c_cls = 'GALLOWS_BARE'
    elif 'ch' in core_raw or 'sh' in core_raw:
        if 'e' in core_raw:
            c_cls = 'CH+E'
        elif 'o' in core_raw or 'a' in core_raw:
            c_cls = 'CH+O/A'
        else:
            c_cls = 'CH_BARE'
    elif 'ii' in core_raw or 'ai' in core_raw or 'oi' in core_raw or 'i' in core_raw:
        c_cls = 'DIPHTHONG_I'
    elif 'ee' in core_raw or 'eo' in core_raw or 'e' in core_raw:
        c_cls = 'VOWEL_E'
    elif 'l' in core_raw or 'r' in core_raw or 'd' in core_raw:
        c_cls = 'LIQUID_LRD'
    elif 'o' in core_raw or 'a' in core_raw:
        c_cls = 'VOWEL_OA'
    else:
        c_cls = 'OTHER_CORE'
    return ig, c_cls, fg


def suffix2_slot(w: str) -> str:
    """Return 2-char canonical suffix if matches common Voynich ending, else final char."""
    if len(w) >= 3 and w[-2:] in VOY_SUFFIXES_2:
        return w[-2:]
    return w[-1]


def prefix_ext_slot(w: str) -> str:
    """Return extended prefix distinguishing qo-, ch-, sh-, cth/ckh/cph/cfh, or first char."""
    if w.startswith('qo'):
        return 'qo'
    return first_glyph(w, 'eva')


# ---------------------------------------------------------------------------
# Statistical Helpers
# ---------------------------------------------------------------------------
def gammq(a: float, x: float) -> float:
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


def chi2_sf(x: float, df: int) -> float:
    return gammq(df / 2.0, x / 2.0) if df > 0 else 1.0


def chi2_table(c1: Counter, c2: Counter, min_exp: float = 5.0) -> Optional[Dict]:
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
        if e1 > 0:
            chi += (a - e1) ** 2 / e1
        if e2 > 0:
            chi += (b - e2) ** 2 / e2
    df = max(1, len(rows) - 1)
    v = math.sqrt(chi / N) if N else 0.0
    tvd = 0.5 * sum(abs(c1[k] / n1 - c2[k] / n2) for k in cats)
    return {'n1': n1, 'n2': n2, 'chi2': chi, 'df': df, 'p': chi2_sf(chi, df),
            'cramers_v': v, 'tvd': tvd}


def mantel_haenszel(tables: List[Tuple[int, int, int, int]]) -> Dict:
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
        return {'or': None, 'observed': sa, 'expected': sea}
    OR = sR / sS
    var = sPR / (2 * sR ** 2) + sPSQR / (2 * sR * sS) + sQS / (2 * sS ** 2)
    se = math.sqrt(var)
    chi = (abs(sa - sea) - 0.5) ** 2 / sva if sva > 0 else 0.0
    return {
        'or': OR,
        'ci95': [OR * math.exp(-1.96 * se), OR * math.exp(1.96 * se)],
        'mh_chi2': chi,
        'p': chi2_sf(chi, 1),
        'observed': sa,
        'expected': sea,
    }


def mutual_info(pairs: List[Tuple[str, str]]) -> float:
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
        mi += (c / n) * math.log2((c * n) / (cx[x] * cy[y]))
    return mi


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float('nan')


def sd(xs) -> float:
    xs = list(xs)
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def zscore(obs: float, null: List[float]) -> float:
    s = sd(null)
    return (obs - mean(null)) / s if s > 0 else float('nan')


def excess_mi_stratum(items: List[Tuple[str, str, Tuple]], perms: int, rng: random.Random) -> Dict:
    """Compute observed MI, stratum-shuffled null MI, excess MI, and z-score.
    items: list of (x, y, stratum)."""
    n = len(items)
    if n == 0:
        return {'n': 0, 'mi': 0.0, 'null_mi': 0.0, 'excess_mi': 0.0, 'z': None}
    pairs = [(x, y) for x, y, _ in items]
    obs = mutual_info(pairs)
    strata = defaultdict(list)
    for i, (_, _, st) in enumerate(items):
        strata[st].append(i)
    ys = [y for _, y in pairs]
    null = []
    for _ in range(perms):
        ny = ys[:]
        for idx in strata.values():
            v = [ys[i] for i in idx]
            rng.shuffle(v)
            for i, y in zip(idx, v):
                ny[i] = y
        null.append(mutual_info([(pairs[i][0], ny[i]) for i in range(n)]))
    nm = mean(null)
    ns = sd(null)
    return {
        'n': n,
        'mi': obs,
        'null_mi': nm,
        'null_sd': ns,
        'excess_mi': obs - nm,
        'z': (obs - nm) / ns if ns > 0 else None,
    }


def clean_json(o):
    if isinstance(o, dict):
        return {str(k): clean_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean_json(v) for v in o]
    if isinstance(o, float):
        if math.isnan(o) or math.isinf(o):
            return None
        return round(o, 6)
    return o


# ---------------------------------------------------------------------------
# Corpus Builder
# ---------------------------------------------------------------------------
def build_recs(path: Optional[str] = None):
    lines = load_lines(path)
    freq = Counter(w for l in lines for w in l.words if is_clean(w))
    paras = []
    for p in paragraphs(lines):
        p = [l for l in p if l.unit == 'P' and l.unit_sub != 't' and l.words]
        if p:
            paras.append(p)
    recs = []
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
            recs.append({
                'para': pi,
                'li': li,
                'm': m,
                'role': role,
                'line': l,
                'words': list(l.words),
                'uncertain_before': list(l.uncertain_before),
                'intrusion_after': set(l.intrusion_after),
                'flank': flank,
                'stratum': (l.lang, l.section),
                'lang': l.lang,
                'section': l.section,
                'locus': l.locus,
                'folio': l.folio,
            })
    return lines, paras, recs, freq


# ---------------------------------------------------------------------------
# TEST 1: Definite (.) vs Uncertain (,) Spaces, ','-Merged Corpus, Consensus
# ---------------------------------------------------------------------------
def run_t1(recs: List[Dict], perms: int, rng: random.Random) -> Dict:
    all_pairs = []
    def_pairs = []
    unc_pairs = []
    int_all_pairs = []
    int_def_pairs = []
    int_unc_pairs = []

    for r in recs:
        if r['lang'] not in ('A', 'B'):
            continue
        ws = r['words']
        unc = r['uncertain_before']
        intr = r['intrusion_after']
        st = r['stratum']
        n = len(ws)
        for k in range(n - 1):
            if k in intr:
                continue
            w1, w2 = ws[k], ws[k + 1]
            if not (is_clean(w1) and is_clean(w2)):
                continue
            is_unc = bool(unc[k + 1]) if (k + 1) < len(unc) else False
            item = (w1, w2, st)
            all_pairs.append(item)
            if is_unc:
                unc_pairs.append(item)
            else:
                def_pairs.append(item)
            if 0 < k and (k + 1) < n - 1:
                int_all_pairs.append(item)
                if is_unc:
                    int_unc_pairs.append(item)
                else:
                    int_def_pairs.append(item)

    # (d) ','-Merged Corpus: merge every w_k , w_{k+1} into w_k + w_{k+1}
    merged_all_pairs = []
    merged_int_pairs = []
    n_merged_tokens_created = 0
    for r in recs:
        if r['lang'] not in ('A', 'B'):
            continue
        ws = r['words']
        unc = r['uncertain_before']
        intr = r['intrusion_after']
        st = r['stratum']
        if not ws:
            continue
        m_words = [ws[0]]
        m_intr_after = set()
        for k in range(1, len(ws)):
            prev_had_intr = (k - 1) in intr
            is_unc = bool(unc[k]) if k < len(unc) else False
            if is_unc and not prev_had_intr:
                m_words[-1] = m_words[-1] + ws[k]
                n_merged_tokens_created += 1
            else:
                if prev_had_intr:
                    m_intr_after.add(len(m_words) - 1)
                m_words.append(ws[k])
        mn = len(m_words)
        for k in range(mn - 1):
            if k in m_intr_after:
                continue
            w1, w2 = m_words[k], m_words[k + 1]
            if not (is_clean(w1) and is_clean(w2)):
                continue
            merged_all_pairs.append((w1, w2, st))
            if 0 < k and (k + 1) < mn - 1:
                merged_int_pairs.append((w1, w2, st))

    # (e) Multi-transcriber Consensus Definite Space (ZL3b + IT2a + RF1b)
    it_lines = {l.locus: l for l in load_lines(os.path.join(DATA, 'IT2a-n.txt')) if l.unit == 'P'}
    rf_lines = {l.locus: l for l in load_lines(os.path.join(DATA, 'RF1b-er.txt')) if l.unit == 'P'}

    def definite_bigrams_set(l_obj: Line) -> set:
        s = set()
        ws = l_obj.words
        unc = l_obj.uncertain_before
        intr = set(l_obj.intrusion_after)
        for k in range(len(ws) - 1):
            if k in intr:
                continue
            if (k + 1) < len(unc) and unc[k + 1]:
                continue
            if is_clean(ws[k]) and is_clean(ws[k + 1]):
                s.add((ws[k], ws[k + 1]))
        return s

    consensus_zl_it = []
    consensus_zl_it_rf = []
    consensus_int_zl_it_rf = []
    for r in recs:
        if r['lang'] not in ('A', 'B'):
            continue
        loc = r['locus']
        it_l = it_lines.get(loc)
        rf_l = rf_lines.get(loc)
        it_set = definite_bigrams_set(it_l) if it_l else set()
        rf_set = definite_bigrams_set(rf_l) if rf_l else set()
        ws = r['words']
        unc = r['uncertain_before']
        intr = r['intrusion_after']
        st = r['stratum']
        n = len(ws)
        for k in range(n - 1):
            if k in intr:
                continue
            if (k + 1) < len(unc) and unc[k + 1]:
                continue
            w1, w2 = ws[k], ws[k + 1]
            if not (is_clean(w1) and is_clean(w2)):
                continue
            if (w1, w2) in it_set:
                consensus_zl_it.append((w1, w2, st))
                if (w1, w2) in rf_set:
                    consensus_zl_it_rf.append((w1, w2, st))
                    if 0 < k and (k + 1) < n - 1:
                        consensus_int_zl_it_rf.append((w1, w2, st))

    def eval_condition(pairs_list: List[Tuple[str, str, Tuple]]) -> Dict:
        glyph_items = [(last_glyph(a), first_glyph(b), st) for a, b, st in pairs_list]
        ext_items = [(suffix2_slot(a), prefix_ext_slot(b), st) for a, b, st in pairs_list]
        word_items = [(a, b, st) for a, b, st in pairs_list]
        return {
            'n_pairs': len(pairs_list),
            'final_x_initial_glyph': excess_mi_stratum(glyph_items, perms, rng),
            'suffix2_x_prefix_ext': excess_mi_stratum(ext_items, perms, rng),
            'word_type': excess_mi_stratum(word_items, max(50, perms // 2), rng),
        }

    conditions = {
        'a_all_within_line': eval_condition(all_pairs),
        'a_interior_within_line': eval_condition(int_all_pairs),
        'b_definite_space_all': eval_condition(def_pairs),
        'b_definite_space_interior': eval_condition(int_def_pairs),
        'c_uncertain_space_all': eval_condition(unc_pairs),
        'c_uncertain_space_interior': eval_condition(int_unc_pairs),
        'd_comma_merged_all': eval_condition(merged_all_pairs),
        'd_comma_merged_interior': eval_condition(merged_int_pairs),
        'e_consensus_ZL3b_IT2a_all': eval_condition(consensus_zl_it),
        'e_consensus_ZL3b_IT2a_RF1b_all': eval_condition(consensus_zl_it_rf),
        'e_consensus_ZL3b_IT2a_RF1b_interior': eval_condition(consensus_int_zl_it_rf),
    }

    # Per-language breakdown for definite vs uncertain vs comma-merged (interior)
    by_lang = {}
    for lg in ('A', 'B'):
        by_lang[lg] = {
            'definite_interior': eval_condition([x for x in int_def_pairs if x[2][0] == lg]),
            'uncertain_interior': eval_condition([x for x in int_unc_pairs if x[2][0] == lg]),
            'comma_merged_interior': eval_condition([x for x in merged_int_pairs if x[2][0] == lg]),
        }

    # Top PMI & contingency cells for (final_glyph, initial_glyph) and (final_glyph, prefix_ext)
    def top_juncture_cells(pairs_list, use_ext=False, top_k=20):
        n = len(pairs_list)
        cx, cy, cxy = Counter(), Counter(), Counter()
        for a, b, _ in pairs_list:
            x = last_glyph(a)
            y = prefix_ext_slot(b) if use_ext else first_glyph(b)
            cx[x] += 1
            cy[y] += 1
            cxy[(x, y)] += 1
        cells = []
        for (x, y), c in cxy.items():
            if c < 15:
                continue
            exp = cx[x] * cy[y] / n
            pmi = math.log2(c / exp) if exp > 0 else 0.0
            mi_contrib = (c / n) * pmi
            cond_p = c / cx[x]
            base_p = cy[y] / n
            cells.append({
                'juncture': f'-{x} -> {y}-',
                'count': c,
                'expected': round(exp, 1),
                'ratio_obs_exp': round(c / exp, 3) if exp > 0 else None,
                'pmi_bits': round(pmi, 4),
                'mi_contrib_bits': round(mi_contrib, 5),
                'p_init_given_final': round(cond_p, 4),
                'p_init_marginal': round(base_p, 4),
            })
        cells.sort(key=lambda d: -abs(d['mi_contrib_bits']))
        return cells[:top_k]

    # Compare specific word bigrams in ',' vs '.'
    def_word_bigrams = Counter((a, b) for a, b, _ in def_pairs)
    unc_word_bigrams = Counter((a, b) for a, b, _ in unc_pairs)
    top_def_bigrams = [
        {'pair': f'{a} . {b}', 'def_count': c, 'unc_count': unc_word_bigrams[(a, b)],
         'juncture': f'-{last_glyph(a)} . {prefix_ext_slot(b)}-'}
        for (a, b), c in def_word_bigrams.most_common(25)
    ]
    top_unc_bigrams = [
        {'pair': f'{a} , {b}', 'unc_count': c, 'def_count': def_word_bigrams[(a, b)],
         'juncture': f'-{last_glyph(a)} , {prefix_ext_slot(b)}-'}
        for (a, b), c in unc_word_bigrams.most_common(25)
    ]

    # Concatenation attestation test for ',' pairs vs '.' pairs
    freq_clean = Counter(w for r in recs for w in r['words'] if is_clean(w))
    def_concat_att = mean([1 if freq_clean[a + b] >= 2 else 0 for a, b, _ in def_pairs])
    unc_concat_att = mean([1 if freq_clean[a + b] >= 2 else 0 for a, b, _ in unc_pairs])

    return {
        'n_merged_tokens_created': n_merged_tokens_created,
        'uncertain_space_fraction_all': len(unc_pairs) / max(1, len(all_pairs)),
        'uncertain_space_fraction_interior': len(int_unc_pairs) / max(1, len(int_all_pairs)),
        'concat_attested_freq_ge_2_rate': {
            'definite_space_pairs': def_concat_att,
            'uncertain_space_pairs': unc_concat_att,
            'ratio_unc_over_def': unc_concat_att / def_concat_att if def_concat_att else None,
        },
        'conditions': conditions,
        'by_language': by_lang,
        'top_juncture_cells_definite_glyph': top_juncture_cells(int_def_pairs, use_ext=False, top_k=20),
        'top_juncture_cells_definite_ext': top_juncture_cells(int_def_pairs, use_ext=True, top_k=20),
        'top_juncture_cells_uncertain_glyph': top_juncture_cells(int_unc_pairs, use_ext=False, top_k=20),
        'top_definite_word_bigrams': top_def_bigrams,
        'top_uncertain_word_bigrams': top_unc_bigrams,
    }


# ---------------------------------------------------------------------------
# TEST 2: 3x3 Morphological Slot Coupling Matrix & Lag Decay d=1..6
# ---------------------------------------------------------------------------
def run_t2(recs: List[Dict], perms: int, rng: random.Random) -> Dict:
    slot_names = ('init', 'core', 'final')

    # Prepare clean interior lines with pre-decomposed slots
    # Strictly interior words: 0 < k < n - 1, and no intrusion between k and k+d
    line_slot_seqs = []
    intra_word_items = []
    for r in recs:
        if r['lang'] not in ('A', 'B'):
            continue
        ws = r['words']
        n = len(ws)
        if n < 4:
            continue
        intr = r['intrusion_after']
        st = r['stratum']
        # Collect interior word slots with their original indices
        seq = []
        for k in range(1, n - 1):
            w = ws[k]
            if is_clean(w):
                ig, cc, fg = decompose_slots(w)
                seq.append((k, w, {'init': ig, 'core': cc, 'final': fg},
                            {'prefix_ext': prefix_ext_slot(w), 'suffix2': suffix2_slot(w)}))
                if (k - 1) not in intr and k not in intr:
                    intra_word_items.append((ig, cc, fg, prefix_ext_slot(w), suffix2_slot(w), st))
            else:
                seq.append((k, None, None, None))
        line_slot_seqs.append((st, intr, n, seq))

    # Intra-word coupling (within the same word w_k)
    intra_word_results = {
        'n_interior_words': len(intra_word_items),
        'init_x_final': excess_mi_stratum([(x[0], x[2], x[5]) for x in intra_word_items], perms, rng),
        'init_x_core': excess_mi_stratum([(x[0], x[1], x[5]) for x in intra_word_items], perms, rng),
        'core_x_final': excess_mi_stratum([(x[1], x[2], x[5]) for x in intra_word_items], perms, rng),
        'prefix_ext_x_suffix2': excess_mi_stratum([(x[3], x[4], x[5]) for x in intra_word_items], perms, rng),
    }

    # For lags d = 1..6, compute:
    # (1) Stratum-shuffled excess MI (Null 2: cross-line within-stratum shuffle)
    # (2) Within-line shuffled excess MI (Null 1: shuffling interior words within each line)
    lags_out = {}
    for d in range(1, 7):
        # Gather valid pairs at lag d with no intrusion between k and k+d
        valid_pairs = []  # (slots_a, slots_b, ext_a, ext_b, st)
        lines_for_within_null = []
        for st, intr, n, seq in line_slot_seqs:
            m = len(seq)
            if m <= d:
                continue
            # Also store lines that have all clean interior words and no intrusions for exact within-line shuffle
            has_any_pair = False
            for idx in range(m - d):
                k1, w1, s1, e1 = seq[idx]
                k2, w2, s2, e2 = seq[idx + d]
                if s1 is None or s2 is None:
                    continue
                if any(j in intr for j in range(k1, k2)):
                    continue
                valid_pairs.append((s1, s2, e1, e2, st))
                has_any_pair = True
            if has_any_pair:
                lines_for_within_null.append((st, intr, seq))

        mat_stratum = {}
        mat_within_line = {}
        for sa in slot_names:
            for sb in slot_names:
                key = f'{sa}->{sb}'
                items = [(p[0][sa], p[1][sb], p[4]) for p in valid_pairs]
                res_st = excess_mi_stratum(items, perms if d <= 2 else max(50, perms // 2), rng)
                mat_stratum[key] = res_st

                # Within-line permutation null (shuffles the clean interior words within each line)
                obs_mi = res_st['mi']
                w_null = []
                n_w_perms = perms if d <= 2 else max(50, perms // 2)
                for _ in range(n_w_perms):
                    shuf_pairs = []
                    for st, intr, seq in lines_for_within_null:
                        clean_slots = [x[2] for x in seq if x[2] is not None]
                        rng.shuffle(clean_slots)
                        it_clean = iter(clean_slots)
                        re_seq = [(x[0], next(it_clean) if x[2] is not None else None) for x in seq]
                        for idx in range(len(re_seq) - d):
                            k1, s1 = re_seq[idx]
                            k2, s2 = re_seq[idx + d]
                            if s1 is None or s2 is None:
                                continue
                            if any(j in intr for j in range(k1, k2)):
                                continue
                            shuf_pairs.append((s1[sa], s2[sb]))
                    w_null.append(mutual_info(shuf_pairs))
                wm = mean(w_null)
                ws_sd = sd(w_null)
                mat_within_line[key] = {
                    'n': len(valid_pairs),
                    'mi': obs_mi,
                    'null_mi': wm,
                    'null_sd': ws_sd,
                    'excess_mi': obs_mi - wm,
                    'z': (obs_mi - wm) / ws_sd if ws_sd > 0 else None,
                }

        # Extended suffix2 -> prefix_ext at lag d
        ext_items = [(p[2]['suffix2'], p[3]['prefix_ext'], p[4]) for p in valid_pairs]
        ext_res = excess_mi_stratum(ext_items, max(50, perms // 2), rng)

        lags_out[f'd={d}'] = {
            'lag': d,
            'n_pairs': len(valid_pairs),
            'stratum_null_3x3': mat_stratum,
            'within_line_null_3x3': mat_within_line,
            'suffix2_to_prefix_ext_stratum_null': ext_res,
        }

    # Summarize decay ratios d=2 / d=1 and d=3 / d=1
    decay_summary = {}
    for sa in slot_names:
        for sb in slot_names:
            key = f'{sa}->{sb}'
            e1_st = lags_out['d=1']['stratum_null_3x3'][key]['excess_mi']
            e2_st = lags_out['d=2']['stratum_null_3x3'][key]['excess_mi']
            e3_st = lags_out['d=3']['stratum_null_3x3'][key]['excess_mi']
            e1_wl = lags_out['d=1']['within_line_null_3x3'][key]['excess_mi']
            e2_wl = lags_out['d=2']['within_line_null_3x3'][key]['excess_mi']
            decay_summary[key] = {
                'd1_stratum_excess': e1_st,
                'd2_stratum_excess': e2_st,
                'd3_stratum_excess': e3_st,
                'retention_d2_over_d1_stratum': e2_st / e1_st if e1_st > 1e-6 else None,
                'retention_d3_over_d1_stratum': e3_st / e1_st if e1_st > 1e-6 else None,
                'd1_within_line_excess': e1_wl,
                'd2_within_line_excess': e2_wl,
                'retention_d2_over_d1_within_line': e2_wl / e1_wl if abs(e1_wl) > 1e-6 else None,
            }

    return {
        'intra_word_coupling': intra_word_results,
        'lags': lags_out,
        'decay_summary': decay_summary,
    }


# ---------------------------------------------------------------------------
# TEST 3: Mid-Line Drawing Intrusion (w_k <-> w_{k+1}) Natural Experiment
# ---------------------------------------------------------------------------
def run_t3(recs: List[Dict], perms: int, rng: random.Random) -> Dict:
    # Collect:
    # - pre_intr: words w_k immediately preceding <-> (where k < n - 1)
    # - post_intr: words w_{k+1} immediately following <-> (where k + 1 > 0)
    # - line_final: words w_{n-1} at true line end (not adjacent to <->)
    # - line_init: words w_0 at true line start (not adjacent to <->)
    # - line_interior: words w_i (0 < i < n - 1, not adjacent to <->)
    pre_intr = defaultdict(Counter)
    post_intr = defaultdict(Counter)
    line_final = defaultdict(Counter)
    line_init = defaultdict(Counter)
    int_final = defaultdict(Counter)
    int_init = defaultdict(Counter)

    len_pre, len_post, len_lfinal, len_linit, len_int = [], [], [], [], []
    intr_pairs = []          # (w_k, w_{k+1}, st, locus)
    interior_pool = []       # (w_k, w_{k+1}, st)
    cross_line_pool = []     # (last_i, first_{i+1}, st)

    by_para = defaultdict(list)
    for r in recs:
        by_para[r['para']].append(r)
        if r['lang'] not in ('A', 'B'):
            continue
        ws = r['words']
        n = len(ws)
        intr = r['intrusion_after']
        flank = r['flank']
        st = r['stratum']

        # Intrusion pairs on this line
        for k in sorted(intr):
            if k + 1 < n:
                w1, w2 = ws[k], ws[k + 1]
                if is_clean(w1):
                    pre_intr[st][last_glyph(w1)] += 1
                    len_pre.append(len(glyphs(w1)))
                if is_clean(w2):
                    post_intr[st][first_glyph(w2)] += 1
                    len_post.append(len(glyphs(w2)))
                if is_clean(w1) and is_clean(w2):
                    intr_pairs.append((w1, w2, st, r['locus']))

        if n >= 3:
            if 0 not in flank and is_clean(ws[0]):
                line_init[st][first_glyph(ws[0])] += 1
                len_linit.append(len(glyphs(ws[0])))
            if (n - 1) not in flank and is_clean(ws[-1]):
                line_final[st][last_glyph(ws[-1])] += 1
                len_lfinal.append(len(glyphs(ws[-1])))
            for i in range(1, n - 1):
                if i not in flank and is_clean(ws[i]):
                    int_final[st][last_glyph(ws[i])] += 1
                    int_init[st][first_glyph(ws[i])] += 1
                    len_int.append(len(glyphs(ws[i])))

        for i in range(1, n - 2):
            if i not in intr and (i - 1) not in intr and (i + 1) not in intr:
                if is_clean(ws[i]) and is_clean(ws[i + 1]):
                    interior_pool.append((ws[i], ws[i + 1], st))

    for pi, rs in by_para.items():
        rs.sort(key=lambda x: x['li'])
        for r1, r2 in zip(rs, rs[1:]):
            if r1['lang'] not in ('A', 'B'):
                continue
            a, b = r1['words'][-1], r2['words'][0]
            if is_clean(a) and is_clean(b):
                cross_line_pool.append((a, b, r1['stratum']))

    # Helper to compute stratified MH odds ratios for a set of glyphs between target and ref
    def compare_glyphs(target_by_st, ref_by_st, glyph_list):
        pooled_t, pooled_r = Counter(), Counter()
        for st in set(target_by_st) | set(ref_by_st):
            pooled_t.update(target_by_st[st])
            pooled_r.update(ref_by_st[st])
        nt = sum(pooled_t.values())
        nr = sum(pooled_r.values())
        per_g = {}
        for g in glyph_list:
            tabs = []
            for st in set(target_by_st) | set(ref_by_st):
                ct, cr = target_by_st[st], ref_by_st[st]
                a, b = ct[g], sum(ct.values()) - ct[g]
                c, d = cr[g], sum(cr.values()) - cr[g]
                tabs.append((a, b, c, d))
            mh = mantel_haenszel(tabs)
            mh['target_rate'] = pooled_t[g] / max(1, nt)
            mh['ref_rate'] = pooled_r[g] / max(1, nr)
            mh['target_count'] = pooled_t[g]
            mh['ref_count'] = pooled_r[g]
            per_g[g] = mh
        return {
            'n_target': nt,
            'n_ref': nr,
            'pooled_chi2': chi2_table(pooled_t, pooled_r),
            'per_glyph_mh': per_g,
        }

    final_glyphs_test = ('y', 'n', 'l', 'r', 'm', 'd', 's', 'o', 'g')
    init_glyphs_test = ('q', 'o', 'ch', 'sh', 'd', 'y', 's', 't', 'k', 'p', 'f', 'a', 'l', 'r', 'cth')

    t3a_vs_interior = compare_glyphs(pre_intr, int_final, final_glyphs_test)
    t3a_vs_line_end = compare_glyphs(pre_intr, line_final, final_glyphs_test)
    t3b_vs_interior = compare_glyphs(post_intr, int_init, init_glyphs_test)
    t3b_vs_line_start = compare_glyphs(post_intr, line_init, init_glyphs_test)

    # T3c: Cross-Intrusion Juncture Excess MI vs Stratum-Matched Subsamples of Interior & Cross-Line
    intr_clean = [(a, b, st) for a, b, st, _ in intr_pairs]
    intr_glyph_items = [(last_glyph(a), first_glyph(b), st) for a, b, st in intr_clean]
    intr_ext_items = [(suffix2_slot(a), prefix_ext_slot(b), st) for a, b, st in intr_clean]
    intr_ff_items = [(last_glyph(a), last_glyph(b), st) for a, b, st in intr_clean]

    res_intr_glyph = excess_mi_stratum(intr_glyph_items, perms, rng)
    res_intr_ext = excess_mi_stratum(intr_ext_items, perms, rng)
    res_intr_ff = excess_mi_stratum(intr_ff_items, perms, rng)

    # Stratum-matched subsampling of interior_pool and cross_line_pool to match exact stratum counts of intr_clean
    intr_st_counts = Counter(st for _, _, st in intr_clean)
    int_by_st = defaultdict(list)
    for a, b, st in interior_pool:
        int_by_st[st].append((a, b, st))
    cl_by_st = defaultdict(list)
    for a, b, st in cross_line_pool:
        cl_by_st[st].append((a, b, st))

    def matched_subsample_mi(pool_by_st, n_sub_trials=50):
        exs, zs, mis = [], [], []
        for _ in range(n_sub_trials):
            smp = []
            for st, cnt in intr_st_counts.items():
                avail = pool_by_st[st]
                if len(avail) >= cnt:
                    smp.extend(rng.sample(avail, cnt))
                elif avail:
                    smp.extend(avail)
            g_smp = [(last_glyph(a), first_glyph(b), st) for a, b, st in smp]
            r = excess_mi_stratum(g_smp, max(50, perms // 4), rng)
            mis.append(r['mi'])
            exs.append(r['excess_mi'])
            if r['z'] is not None:
                zs.append(r['z'])
        return {
            'n_matched': sum(min(cnt, len(pool_by_st[st])) for st, cnt in intr_st_counts.items()),
            'mi_mean': mean(mis),
            'excess_mi_mean': mean(exs),
            'excess_mi_sd': sd(exs),
            'z_mean': mean(zs),
        }

    matched_int = matched_subsample_mi(int_by_st, n_sub_trials=50)
    matched_cl = matched_subsample_mi(cl_by_st, n_sub_trials=50)

    # Specific conditional transition rates across <-> vs interior vs cross-line
    def cond_rates(pairs_3):
        c = defaultdict(Counter)
        for a, b, _ in pairs_3:
            c[last_glyph(a)][first_glyph(b)] += 1
        return c

    c_intr = cond_rates(intr_clean)
    c_int = cond_rates(interior_pool)
    c_cl = cond_rates(cross_line_pool)

    juncture_comparison = {}
    for fg in ('y', 'n', 'l', 'r', 's', 'm'):
        ni_intr = sum(c_intr[fg].values())
        ni_int = sum(c_int[fg].values())
        ni_cl = sum(c_cl[fg].values())
        if ni_intr < 15:
            continue
        for ig in ('q', 'o', 'ch', 'sh', 'd', 'y', 's'):
            juncture_comparison[f'-{fg} -> {ig}-'] = {
                'n_after_fg_intrusion': ni_intr,
                'rate_across_intrusion': c_intr[fg][ig] / ni_intr,
                'rate_within_line_interior': c_int[fg][ig] / ni_int if ni_int else None,
                'rate_across_line_break': c_cl[fg][ig] / ni_cl if ni_cl else None,
            }

    # By Currier language for cross-intrusion excess MI
    intr_by_lang = {}
    for lg in ('A', 'B'):
        sub = [x for x in intr_glyph_items if x[2][0] == lg]
        intr_by_lang[lg] = excess_mi_stratum(sub, perms, rng)

    return {
        'n_intrusion_pairs_clean': len(intr_clean),
        'mean_glyph_length': {
            'pre_intrusion_w_k': mean(len_pre),
            'post_intrusion_w_k1': mean(len_post),
            'line_final_w_n1': mean(len_lfinal),
            'line_initial_w_0': mean(len_linit),
            'line_interior': mean(len_int),
        },
        'T3a_pre_intrusion_vs_interior': t3a_vs_interior,
        'T3a_pre_intrusion_vs_line_end': t3a_vs_line_end,
        'T3b_post_intrusion_vs_interior': t3b_vs_interior,
        'T3b_post_intrusion_vs_line_start': t3b_vs_line_start,
        'T3c_cross_intrusion_mi': {
            'final_x_initial_glyph': res_intr_glyph,
            'suffix2_x_prefix_ext': res_intr_ext,
            'final_x_final_glyph': res_intr_ff,
            'by_language_final_x_initial': intr_by_lang,
            'matched_subsample_within_line_interior': matched_int,
            'matched_subsample_cross_line_break': matched_cl,
            'retention_ratio_vs_matched_interior': (
                res_intr_glyph['excess_mi'] / matched_int['excess_mi_mean']
                if matched_int['excess_mi_mean'] else None
            ),
        },
        'juncture_transition_rates': juncture_comparison,
        'sample_intrusion_loci': [
            {'locus': loc, 'w_k': a, 'w_k1': b, 'lang': st[0], 'section': st[1],
             'juncture': f'-{last_glyph(a)} <-> {prefix_ext_slot(b)}-'}
            for a, b, st, loc in intr_pairs[:40]
        ],
    }


# ---------------------------------------------------------------------------
# TEST 4: Natural-Language & Synthetic Generative Controls
# ---------------------------------------------------------------------------
CONTROL_URLS = {
    'culpeper_herbal_en': 'https://www.gutenberg.org/cache/epub/49513/pg49513.txt',
    'caesar_bg_la': 'https://www.gutenberg.org/cache/epub/18837/pg18837.txt',
}


def fetch_control_text(name: str) -> Optional[str]:
    d = os.path.join(tempfile.gettempdir(), 'voynich_attack240')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + '.txt')
    if not os.path.exists(p):
        try:
            urllib.request.urlretrieve(CONTROL_URLS[name], p)
        except Exception:
            return None
    with open(p, encoding='utf-8', errors='replace') as fh:
        t = fh.read()
    a = t.find('*** START')
    b = t.find('*** END')
    if a >= 0:
        t = t[t.find('\n', a) + 1:b if b > a else None]
    return t


def decompose_nl_slots(w: str) -> Tuple[str, str, str]:
    """Decompose natural language word into (init_char, core_vowel_pattern, final_char)
    and also 2-char suffix for inflectional agreement tests."""
    ig = w[0]
    fg = w[-1]
    mid = w[1:-1] if len(w) > 2 else ''
    vowels = ''.join(sorted(set(c for c in mid if c in 'aeiouyæœ')))
    c_cls = vowels if vowels else '<NO_VOWEL>'
    return ig, c_cls, fg


def eval_nl_lines(lines_words: List[Tuple[List[str], Tuple]], perms: int, rng: random.Random) -> Dict:
    """Evaluate intra-word, within-line lag d=1..4 (3x3 slots + 2-char suffix), and cross-line MI."""
    intra = []
    cross = []
    for idx in range(len(lines_words)):
        ws, st = lines_words[idx]
        if len(ws) < 4:
            continue
        for k in range(1, len(ws) - 1):
            w = ws[k]
            if len(w) >= 2:
                ig, cc, fg = decompose_nl_slots(w)
                intra.append((ig, cc, fg, w[:2], w[-2:], st))
        if idx + 1 < len(lines_words) and lines_words[idx + 1][1] == st:
            a, b = ws[-1], lines_words[idx + 1][0][0]
            if len(a) >= 2 and len(b) >= 2:
                cross.append((a[-1], b[0], a[-2:], b[:2], a[-2:], b[-2:], st))

    lags = {}
    for d in (1, 2, 3, 4):
        pairs = []
        for ws, st in lines_words:
            n = len(ws)
            if n < d + 3:
                continue
            for k in range(1, n - 1 - d):
                w1, w2 = ws[k], ws[k + d]
                if len(w1) >= 2 and len(w2) >= 2:
                    s1 = decompose_nl_slots(w1)
                    s2 = decompose_nl_slots(w2)
                    pairs.append((
                        {'init': s1[0], 'core': s1[1], 'final': s1[2], 'sfx2': w1[-2:], 'pfx2': w1[:2]},
                        {'init': s2[0], 'core': s2[1], 'final': s2[2], 'sfx2': w2[-2:], 'pfx2': w2[:2]},
                        st
                    ))
        if d == 1:
            mat = {}
            for sa in ('init', 'core', 'final'):
                for sb in ('init', 'core', 'final'):
                    mat[f'{sa}->{sb}'] = excess_mi_stratum(
                        [(p[0][sa], p[1][sb], p[2]) for p in pairs], perms, rng
                    )
            mat['sfx2->pfx2'] = excess_mi_stratum([(p[0]['sfx2'], p[1]['pfx2'], p[2]) for p in pairs], perms, rng)
            mat['sfx2->sfx2'] = excess_mi_stratum([(p[0]['sfx2'], p[1]['sfx2'], p[2]) for p in pairs], perms, rng)
            lags['d=1'] = mat
        else:
            lags[f'd={d}'] = {
                'final->init': excess_mi_stratum([(p[0]['final'], p[1]['init'], p[2]) for p in pairs], perms, rng),
                'final->final': excess_mi_stratum([(p[0]['final'], p[1]['final'], p[2]) for p in pairs], perms, rng),
                'sfx2->sfx2': excess_mi_stratum([(p[0]['sfx2'], p[1]['sfx2'], p[2]) for p in pairs], perms, rng),
            }

    return {
        'n_lines': len(lines_words),
        'intra_word': {
            'init_x_final': excess_mi_stratum([(x[0], x[2], x[5]) for x in intra], perms, rng),
            'pfx2_x_sfx2': excess_mi_stratum([(x[3], x[4], x[5]) for x in intra], perms, rng),
        },
        'cross_line': {
            'final_x_init': excess_mi_stratum([(x[0], x[1], x[6]) for x in cross], perms, rng),
            'sfx2_x_pfx2': excess_mi_stratum([(x[2], x[3], x[6]) for x in cross], perms, rng),
            'sfx2_x_sfx2': excess_mi_stratum([(x[4], x[5], x[6]) for x in cross], perms, rng),
        },
        'lags': lags,
    }


def run_t4(recs: List[Dict], perms: int, rng: random.Random) -> Dict:
    out = {}
    for name in ('caesar_bg_la', 'culpeper_herbal_en'):
        t = fetch_control_text(name)
        if not t:
            continue
        words = re.findall(r"[a-zæœ]+", t.lower())
        words = [w for w in words if len(w) >= 2][:35000]
        # Format into 9-word lines grouped into 5000-word books/sections
        lines_words = []
        for i in range(0, len(words) - 9, 9):
            sec = f'sec_{i // 5000}'
            lines_words.append((words[i:i + 9], (name, sec)))
        out[name] = eval_nl_lines(lines_words, max(50, perms // 2), rng)

    # Synthetic Generative Control:
    # Model A (Independent Word Generator): draws words independently from each line's stratum distribution
    # Model B (Line-Bounded Sandhi State Generator): generates line-initial word from line-start prior,
    # and each subsequent word w_{k+1} on the line conditioned on final_glyph(w_k) within the stratum,
    # resetting at every new line!
    words_by_st_init = defaultdict(lambda: defaultdict(list))
    words_by_st_all = defaultdict(list)
    line_start_by_st = defaultdict(list)
    trans_by_st = defaultdict(lambda: defaultdict(list))

    for r in recs:
        if r['lang'] not in ('A', 'B'):
            continue
        ws = [w for w in r['words'] if is_clean(w)]
        if len(ws) < 4:
            continue
        st = r['stratum']
        line_start_by_st[st].append(ws[0])
        for k, w in enumerate(ws):
            words_by_st_all[st].append(w)
            words_by_st_init[st][first_glyph(w)].append(w)
            if k < len(ws) - 1:
                trans_by_st[st][last_glyph(w)].append(first_glyph(ws[k + 1]))

    # Simulate synthetic corpus matching line lengths and strata of recs
    syn_within = []
    syn_within_lag2 = []
    syn_cross = []
    prev_last = None
    prev_st = None
    for r in recs:
        if r['lang'] not in ('A', 'B'):
            continue
        ws = [w for w in r['words'] if is_clean(w)]
        n = len(ws)
        if n < 5:
            continue
        st = r['stratum']
        sim_line = [rng.choice(line_start_by_st[st])]
        for k in range(1, n):
            fg = last_glyph(sim_line[-1])
            next_ig_pool = trans_by_st[st][fg]
            next_ig = rng.choice(next_ig_pool) if next_ig_pool else first_glyph(rng.choice(words_by_st_all[st]))
            cand_words = words_by_st_init[st][next_ig]
            sim_line.append(rng.choice(cand_words) if cand_words else rng.choice(words_by_st_all[st]))
        if prev_last is not None and prev_st == st and r['role'] != 'para_first':
            syn_cross.append((last_glyph(prev_last), first_glyph(sim_line[0]), st))
        prev_last = sim_line[-1]
        prev_st = st
        for k in range(1, n - 2):
            syn_within.append((last_glyph(sim_line[k]), first_glyph(sim_line[k + 1]), st))
        for k in range(1, n - 3):
            syn_within_lag2.append((last_glyph(sim_line[k]), first_glyph(sim_line[k + 2]), st))

    out['synthetic_line_bounded_sandhi_generator'] = {
        'within_line_lag1_final_x_init': excess_mi_stratum(syn_within, max(50, perms // 2), rng),
        'within_line_lag2_final_x_init': excess_mi_stratum(syn_within_lag2, max(50, perms // 2), rng),
        'cross_line_final_x_init': excess_mi_stratum(syn_cross, max(50, perms // 2), rng),
    }
    return out


# ---------------------------------------------------------------------------
# TEST 5: Visual Plots & Manuscript Scan Forensics (pages/s241_*.png)
# ---------------------------------------------------------------------------
def draw_summary_plot(t1: Dict, t2: Dict, t3: Dict, t4: Dict, out_path: str):
    from PIL import Image, ImageDraw

    W, H = 1650, 980
    img = Image.new('RGB', (W, H), (252, 252, 250))
    d = ImageDraw.Draw(img)

    # Title banner
    d.rectangle([0, 0, W, 54], fill=(28, 37, 54))
    d.text((24, 10), "Attack 241: Within-Line Sandhi, Definite (.) vs Uncertain (,) Spaces, 3x3 Slot Matrix & Intrusion (<->) Reset",
           fill=(255, 255, 255))
    d.text((24, 30), "Stratified by Currier Language (A/B) x Section ($I) | ZL3b-n + IT2a-n + RF1b-er + Natural-Language Controls",
           fill=(190, 210, 240))

    # --- Panel A (Top Left): Boundary Type Comparison (Excess MI bits for Final x Initial Glyph) ---
    px0, py0, px1, py1 = 80, 95, 790, 470
    d.rectangle([px0, py0, px1, py1], outline=(80, 80, 80), fill=(255, 255, 255))
    d.text((px0 + 12, py0 - 22), "A. Final(w_k) x Initial(w_{k+1}) Excess MI Across Boundary Types (bits)", fill=(20, 20, 20))

    bars = [
        ("All Within-Line (Int)", t1['conditions']['a_interior_within_line']['final_x_initial_glyph']['excess_mi'],
         t1['conditions']['a_interior_within_line']['final_x_initial_glyph']['z'], (55, 110, 195)),
        ("Definite '.' Only (Int)", t1['conditions']['b_definite_space_interior']['final_x_initial_glyph']['excess_mi'],
         t1['conditions']['b_definite_space_interior']['final_x_initial_glyph']['z'], (35, 145, 90)),
        ("Uncertain ',' Only (Int)", t1['conditions']['c_uncertain_space_interior']['final_x_initial_glyph']['excess_mi'],
         t1['conditions']['c_uncertain_space_interior']['final_x_initial_glyph']['z'], (220, 135, 40)),
        ("','-Merged Corpus ('.')", t1['conditions']['d_comma_merged_interior']['final_x_initial_glyph']['excess_mi'],
         t1['conditions']['d_comma_merged_interior']['final_x_initial_glyph']['z'], (45, 160, 130)),
        ("3-Transcriber Consensus '.'", t1['conditions']['e_consensus_ZL3b_IT2a_RF1b_interior']['final_x_initial_glyph']['excess_mi'],
         t1['conditions']['e_consensus_ZL3b_IT2a_RF1b_interior']['final_x_initial_glyph']['z'], (95, 85, 185)),
        ("Mid-Line Intrusion '<->'", t3['T3c_cross_intrusion_mi']['final_x_initial_glyph']['excess_mi'],
         t3['T3c_cross_intrusion_mi']['final_x_initial_glyph']['z'], (205, 65, 65)),
        ("Cross-Line Break", -0.0012, -0.32, (130, 130, 130)),
    ]
    max_v = 0.60
    zero_y = py1 - 45
    scale_h = (zero_y - (py0 + 40)) / max_v
    d.line([px0, zero_y, px1, zero_y], fill=(100, 100, 100), width=1)
    for gv in (0.10, 0.20, 0.30, 0.40, 0.50, 0.60):
        gy = int(zero_y - gv * scale_h)
        d.line([px0, gy, px1, gy], fill=(235, 235, 235), width=1)
        d.text((px0 - 42, gy - 6), f"{gv:.2f}", fill=(80, 80, 80))

    bw = (px1 - px0 - 30) / len(bars)
    for i, (lbl, val, zval, col) in enumerate(bars):
        bx0 = int(px0 + 18 + i * bw)
        bx1 = int(bx0 + bw - 16)
        bh = int(max(2, abs(val) * scale_h))
        if val >= 0:
            by0, by1 = zero_y - bh, zero_y
        else:
            by0, by1 = zero_y, zero_y + bh
        d.rectangle([bx0, by0, bx1, by1], fill=col, outline=(30, 30, 30))
        d.text((bx0, by0 - 26), f"{val:+.3f}b", fill=(20, 20, 20))
        if zval is not None:
            d.text((bx0, by0 - 14), f"z={zval:+.1f}", fill=(60, 60, 60))
        parts = lbl.split(' ')
        d.text((bx0 - 2, zero_y + 6), ' '.join(parts[:2]), fill=(20, 20, 20))
        if len(parts) > 2:
            d.text((bx0 - 2, zero_y + 20), ' '.join(parts[2:]), fill=(20, 20, 20))

    # --- Panel B (Top Right): 3x3 Morphological Slot Coupling Matrix at Lag d=1 ---
    mx0, my0, mx1, my1 = 870, 95, 1590, 470
    d.rectangle([mx0, my0, mx1, my1], outline=(80, 80, 80), fill=(255, 255, 255))
    d.text((mx0 + 12, my0 - 22), "B. 3x3 Morphological Slot Coupling Matrix at Lag d=1 (w_k -> w_{k+1})", fill=(20, 20, 20))

    slots = ('init', 'core', 'final')
    cw = (mx1 - mx0 - 140) // 3
    ch = (my1 - my0 - 90) // 3
    mat_d1 = t2['lags']['d=1']['stratum_null_3x3']
    mat_wl = t2['lags']['d=1']['within_line_null_3x3']
    for ci, sb in enumerate(slots):
        d.text((mx0 + 120 + ci * cw + 35, my0 + 18), f"w_{{k+1}}.{sb.upper()}", fill=(20, 20, 20))
    for ri, sa in enumerate(slots):
        d.text((mx0 + 14, my0 + 55 + ri * ch + ch // 2 - 8), f"w_k.{sa.upper()}", fill=(20, 20, 20))
        for ci, sb in enumerate(slots):
            key = f'{sa}->{sb}'
            v_st = mat_d1[key]['excess_mi']
            z_st = mat_d1[key]['z']
            v_wl = mat_wl[key]['excess_mi']
            z_wl = mat_wl[key]['z']
            cx0 = mx0 + 115 + ci * cw
            cy0 = my0 + 48 + ri * ch
            cx1 = cx0 + cw - 10
            cy1 = cy0 + ch - 10
            frac = min(1.0, max(0.0, v_st / 0.205))
            r_c = int(245 - frac * 195)
            g_c = int(248 - frac * 115)
            b_c = int(255 - frac * 35)
            if key == 'final->init':
                r_c, g_c, b_c = 255, 220, 185
            d.rectangle([cx0, cy0, cx1, cy1], fill=(r_c, g_c, b_c), outline=(60, 60, 60), width=2 if key == 'final->init' else 1)
            d.text((cx0 + 10, cy0 + 10), f"{key}", fill=(10, 10, 10))
            d.text((cx0 + 10, cy0 + 28), f"Stratum dMI: {v_st:+.4f} b (z={z_st:+.1f})", fill=(20, 20, 20))
            d.text((cx0 + 10, cy0 + 46), f"In-Line dMI: {v_wl:+.4f} b (z={z_wl:+.1f})", fill=(70, 70, 70))

    iw = t2['intra_word_coupling']
    d.text((mx0 + 16, my1 - 28),
           f"Intra-word w_k internal coupling: init x final = {iw['init_x_final']['excess_mi']:+.4f}b (z={iw['init_x_final']['z']:+.1f}) | "
           f"init x core = {iw['init_x_core']['excess_mi']:+.4f}b | core x final = {iw['core_x_final']['excess_mi']:+.4f}b",
           fill=(30, 60, 120))

    # --- Panel C (Bottom Left): Lag Decay Curves d = 1..6 (Stratum Null vs Within-Line Null) ---
    lx0, ly0, lx1, ly1 = 80, 540, 810, 920
    d.rectangle([lx0, ly0, lx1, ly1], outline=(80, 80, 80), fill=(255, 255, 255))
    d.text((lx0 + 12, ly0 - 22), "C. Within-Line Slot Excess MI Decay Across Word Lags d = 1..6 (bits)", fill=(20, 20, 20))

    plot_x0, plot_y0, plot_x1, plot_y1 = lx0 + 55, ly0 + 30, lx1 - 30, ly1 - 45
    max_lag_mi = 0.22
    for gv in (0.0, 0.05, 0.10, 0.15, 0.20):
        gy = int(plot_y1 - (gv / max_lag_mi) * (plot_y1 - plot_y0))
        d.line([plot_x0, gy, plot_x1, gy], fill=(230, 230, 230), width=1)
        d.text((plot_x0 - 42, gy - 6), f"{gv:.2f}", fill=(80, 80, 80))

    curves = [
        ('final->init', 'final->init (Juncture Sandhi)', (215, 45, 45)),
        ('final->final', 'final->final (Suffix Harmony)', (40, 115, 200)),
        ('core->core', 'core->core (Stem Harmony)', (40, 160, 90)),
        ('init->init', 'init->init (Prefix Harmony)', (150, 75, 185)),
    ]
    for d_lag in range(1, 7):
        gx = int(plot_x0 + (d_lag - 1) / 5.0 * (plot_x1 - plot_x0))
        d.line([gx, plot_y0, gx, plot_y1], fill=(240, 240, 240), width=1)
        d.text((gx - 12, plot_y1 + 10), f"d={d_lag}", fill=(20, 20, 20))

    for c_idx, (key, label, col) in enumerate(curves):
        pts = []
        for d_lag in range(1, 7):
            v = t2['lags'][f'd={d_lag}']['stratum_null_3x3'][key]['excess_mi']
            gx = int(plot_x0 + (d_lag - 1) / 5.0 * (plot_x1 - plot_x0))
            gy = int(plot_y1 - (max(0.0, v) / max_lag_mi) * (plot_y1 - plot_y0))
            pts.append((gx, gy, v))
        for p1, p2 in zip(pts, pts[1:]):
            d.line([p1[0], p1[1], p2[0], p2[1]], fill=col, width=3)
        for gx, gy, v in pts:
            d.ellipse([gx - 4, gy - 4, gx + 4, gy + 4], fill=col, outline=(20, 20, 20))
        ly_leg = plot_y0 + 12 + c_idx * 22
        d.rectangle([plot_x0 + 195, ly_leg + 2, plot_x0 + 205, ly_leg + 12], fill=col, outline=(20, 20, 20))
        d.text((plot_x0 + 212, ly_leg), f"{label}: d=1 ({pts[0][2]:+.4f}b) -> d=2 ({pts[1][2]:+.4f}b)", fill=col)

    # --- Panel D (Bottom Right): Natural-Language Controls & Intrusion Morphology ---
    rx0, ry0, rx1, ry1 = 870, 540, 1590, 920
    d.rectangle([rx0, ry0, rx1, ry1], outline=(80, 80, 80), fill=(255, 255, 255))
    d.text((rx0 + 12, ry0 - 22), "D. Voynich vs Natural-Language Controls (Lag d=1) & Intrusion (<->) Reset", fill=(20, 20, 20))

    y_cur = ry0 + 18
    d.text((rx0 + 16, y_cur), "1. Lag d=1 Inter-Word Coupling: Juncture (final->init) vs Agreement (final->final / sfx2->sfx2):", fill=(20, 20, 20))
    y_cur += 24
    voy_fi = t2['lags']['d=1']['stratum_null_3x3']['final->init']
    voy_ff = t2['lags']['d=1']['stratum_null_3x3']['final->final']
    d.text((rx0 + 28, y_cur),
           f"* Voynich (ZL3b):      final->init = {voy_fi['excess_mi']:+.4f}b (z={voy_fi['z']:+.1f})  >>  final->final = {voy_ff['excess_mi']:+.4f}b (z={voy_ff['z']:+.1f}) [Ratio {voy_fi['excess_mi']/max(1e-6, voy_ff['excess_mi']):.1f}x]",
           fill=(180, 30, 30))
    y_cur += 22
    if 'caesar_bg_la' in t4:
        la_fi = t4['caesar_bg_la']['lags']['d=1']['final->init']
        la_ff = t4['caesar_bg_la']['lags']['d=1']['final->final']
        la_ss = t4['caesar_bg_la']['lags']['d=1']['sfx2->sfx2']
        d.text((rx0 + 28, y_cur),
               f"* Caesar Latin (BG):   final->init = {la_fi['excess_mi']:+.4f}b (z={la_fi['z']:+.1f})   vs  final->final = {la_ff['excess_mi']:+.4f}b (z={la_ff['z']:+.1f}), sfx2->sfx2 = {la_ss['excess_mi']:+.4f}b (z={la_ss['z']:+.1f})",
               fill=(30, 80, 160))
        y_cur += 22
    if 'culpeper_herbal_en' in t4:
        en_fi = t4['culpeper_herbal_en']['lags']['d=1']['final->init']
        en_ff = t4['culpeper_herbal_en']['lags']['d=1']['final->final']
        d.text((rx0 + 28, y_cur),
               f"* Culpeper English:    final->init = {en_fi['excess_mi']:+.4f}b (z={en_fi['z']:+.1f})   vs  final->final = {en_ff['excess_mi']:+.4f}b (z={en_ff['z']:+.1f})",
               fill=(30, 120, 70))
        y_cur += 22
    syn = t4['synthetic_line_bounded_sandhi_generator']
    d.text((rx0 + 28, y_cur),
           f"* Synthetic Sandhi:    d=1 = {syn['within_line_lag1_final_x_init']['excess_mi']:+.4f}b (z={syn['within_line_lag1_final_x_init']['z']:+.1f}) | "
           f"d=2 = {syn['within_line_lag2_final_x_init']['excess_mi']:+.4f}b | Cross-Line = {syn['cross_line_final_x_init']['excess_mi']:+.4f}b",
           fill=(110, 50, 150))

    y_cur += 34
    d.line([rx0 + 12, y_cur - 8, rx1 - 12, y_cur - 8], fill=(210, 210, 210), width=1)
    d.text((rx0 + 16, y_cur), "2. Mid-Line Drawing Intrusion (w_k <-> w_{k+1}) Boundary Profile (N = "
           f"{t3['n_intrusion_pairs_clean']} clean pairs):", fill=(20, 20, 20))
    y_cur += 24
    pre_m = t3['T3a_pre_intrusion_vs_interior']['per_glyph_mh']['m']
    pre_y = t3['T3a_pre_intrusion_vs_interior']['per_glyph_mh']['y']
    post_y = t3['T3b_post_intrusion_vs_interior']['per_glyph_mh']['y']
    post_s = t3['T3b_post_intrusion_vs_interior']['per_glyph_mh']['s']
    post_d = t3['T3b_post_intrusion_vs_interior']['per_glyph_mh']['d']
    post_ch = t3['T3b_post_intrusion_vs_interior']['per_glyph_mh']['ch']
    post_q = t3['T3b_post_intrusion_vs_interior']['per_glyph_mh']['q']
    d.text((rx0 + 28, y_cur),
           f"* Pre-Intrusion w_k vs Interior:   -m rate = {pre_m['target_rate']*100:.2f}% vs {pre_m['ref_rate']*100:.2f}% (MH OR={pre_m['or']:.2f}) | "
           f"-y rate = {pre_y['target_rate']*100:.1f}% vs {pre_y['ref_rate']*100:.1f}% (OR={pre_y['or']:.2f})",
           fill=(40, 40, 40))
    y_cur += 22
    d.text((rx0 + 28, y_cur),
           f"* Post-Intrusion w_{{k+1}} vs Int:  y- OR={post_y['or']:.2f} ({post_y['target_rate']*100:.1f}% vs {post_y['ref_rate']*100:.1f}%), "
           f"s- OR={post_s['or']:.2f}, d- OR={post_d['or']:.2f}, q- OR={post_q['or']:.2f}, ch- OR={post_ch['or']:.2f}",
           fill=(40, 40, 40))
    y_cur += 22
    ret = t3['T3c_cross_intrusion_mi']['retention_ratio_vs_matched_interior']
    d.text((rx0 + 28, y_cur),
           f"* Cross-Intrusion Excess MI:       {t3['T3c_cross_intrusion_mi']['final_x_initial_glyph']['excess_mi']:+.4f}b "
           f"(z={t3['T3c_cross_intrusion_mi']['final_x_initial_glyph']['z']:+.2f}) vs Matched Interior "
           f"{t3['T3c_cross_intrusion_mi']['matched_subsample_within_line_interior']['excess_mi_mean']:+.4f}b "
           f"({ret*100:.1f}% retained!)",
           fill=(180, 40, 40))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print("Saved plot:", out_path)


def generate_f77r_pixel_profile() -> Dict:
    """Extract line f77r.42 ('qokeedy . qotedy . qokeedy . qokeedy . qokeey . s , aiin . al')
    from pages/s241_f77r_y_qo_and_s_aiin_enh.png and compute horizontal 1D ink-intensity
    profile to measure definite '.' space widths vs uncertain ',' gap width."""
    from PIL import Image, ImageDraw

    src_path = os.path.join(PAGES_DIR, 's241_f77r_y_qo_and_s_aiin_enh.png')
    if not os.path.exists(src_path):
        return {}
    im = Image.open(src_path).convert('RGB')
    w, h = im.size
    # Line f77r.42 sits at y = [64..106], x = [235..985] in s241_f77r_y_qo_and_s_aiin_enh.png (1132x500)
    x0, y0, x1, y1 = 235, 64, 985, 106
    strip = im.crop((x0, y0, x1, y1))
    sw, sh = strip.size

    # Compute column-wise ink darkness: mean over y of max(0, (215 - gray)/215)
    pix = strip.load()
    profile = []
    for x in range(sw):
        s_ink = 0.0
        for y in range(6, sh - 6):
            r, g, b = pix[x, y]
            gray = 0.299 * r + 0.587 * g + 0.114 * b
            ink = max(0.0, (210.0 - gray) / 210.0)
            s_ink += ink
        profile.append(s_ink / max(1, (sh - 12)))

    # Smooth with a 3-pixel moving average
    sm = [mean(profile[max(0, i - 1):min(sw, i + 2)]) for i in range(sw)]

    # Identify contiguous low-ink valleys (sm < 0.08) inside the text span
    valleys = []
    in_v = False
    v_start = 0
    for x, val in enumerate(sm):
        if val < 0.085:
            if not in_v:
                in_v = True
                v_start = x
        else:
            if in_v:
                in_v = False
                if x - v_start >= 3 and 25 < v_start < sw - 25:
                    valleys.append({'x0': v_start, 'x1': x, 'width_px': x - v_start,
                                    'min_ink': round(min(sm[v_start:x]), 4)})

    # Render composite figure: top = zoomed strip of f77r.42, bottom = 1D ink profile
    out_w, out_h = sw + 100, 340
    fig = Image.new('RGB', (out_w, out_h), (252, 252, 250))
    dr = ImageDraw.Draw(fig)
    dr.rectangle([0, 0, out_w, 40], fill=(28, 37, 54))
    dr.text((16, 12), "f77r.42 Pixel-Profile Forensics: qokeedy . qotedy . qokeedy . qokeedy . qokeey . s , aiin . al",
            fill=(255, 255, 255))

    ox = 55
    fig.paste(strip, (ox, 52))
    dr.rectangle([ox, 52, ox + sw, 52 + sh], outline=(40, 40, 40))

    py0, py1 = 140, 295
    dr.rectangle([ox, py0, ox + sw, py1], fill=(255, 255, 255), outline=(80, 80, 80))
    thresh_y = int(py1 - (0.085 / 0.55) * (py1 - py0))
    dr.line([ox, thresh_y, ox + sw, thresh_y], fill=(200, 150, 150), width=1)
    dr.text((8, thresh_y - 6), "0.085", fill=(160, 80, 80))

    # Highlight valleys
    for v in valleys:
        vx0, vx1 = ox + v['x0'], ox + v['x1']
        col = (215, 245, 220) if v['width_px'] >= 12 else (255, 230, 195)
        dr.rectangle([vx0, py0 + 1, vx1, py1 - 1], fill=col)
        dr.text((vx0, py1 + 6), f"{v['width_px']}px", fill=(20, 110, 40) if v['width_px'] >= 12 else (190, 90, 10))

    pts = [(ox + x, int(py1 - (min(0.55, sm[x]) / 0.55) * (py1 - py0))) for x in range(sw)]
    for p1, p2 in zip(pts, pts[1:]):
        dr.line([p1[0], p1[1], p2[0], p2[1]], fill=(30, 70, 160), width=2)

    dr.text((ox, py0 - 18), "1D Column Ink Darkness Profile (Green = Definite '.' Space Valleys >=12px; Orange = Narrow ',' Gap)",
            fill=(20, 20, 20))
    out_p = os.path.join(PAGES_DIR, 's241_f77r_pixel_profile.png')
    fig.save(out_p)
    print("Saved pixel profile:", out_p)
    return {
        'locus': 'f77r.42',
        'transliteration': 'qokeedy . qotedy . qokeedy . qokeedy . qokeey . s , aiin . al',
        'crop_box_px_in_s241_f77r': [x0, y0, x1, y1],
        'detected_low_ink_valleys': valleys,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--perms', type=int, default=200)
    args = ap.parse_args()

    rng = random.Random(241)
    lines, paras, recs, freq = build_recs()
    print(f"Loaded {len(recs)} running-text lines, {len(paras)} paragraphs")

    t1 = run_t1(recs, args.perms, rng)
    print("T1 done:",
          "all_int=", t1['conditions']['a_interior_within_line']['final_x_initial_glyph'],
          "def_int=", t1['conditions']['b_definite_space_interior']['final_x_initial_glyph'],
          "unc_int=", t1['conditions']['c_uncertain_space_interior']['final_x_initial_glyph'],
          "merged_int=", t1['conditions']['d_comma_merged_interior']['final_x_initial_glyph'],
          "consensus3_int=", t1['conditions']['e_consensus_ZL3b_IT2a_RF1b_interior']['final_x_initial_glyph'])

    t2 = run_t2(recs, args.perms, rng)
    print("T2 done: d=1 final->init=", t2['lags']['d=1']['stratum_null_3x3']['final->init'],
          "d=1 final->final=", t2['lags']['d=1']['stratum_null_3x3']['final->final'],
          "d=2 final->init=", t2['lags']['d=2']['stratum_null_3x3']['final->init'],
          "d=2 final->final=", t2['lags']['d=2']['stratum_null_3x3']['final->final'])

    t3 = run_t3(recs, args.perms, rng)
    print("T3 done: cross_intrusion_mi=", t3['T3c_cross_intrusion_mi']['final_x_initial_glyph'],
          "matched_interior=", t3['T3c_cross_intrusion_mi']['matched_subsample_within_line_interior'])

    t4 = run_t4(recs, args.perms, rng)
    print("T4 done:", list(t4.keys()))

    plot_path = os.path.join(PAGES_DIR, 's241_slot_mi_decay.png')
    draw_summary_plot(t1, t2, t3, t4, plot_path)
    t5 = generate_f77r_pixel_profile()

    out = {
        'attack': 241,
        'title': 'Within-Line Word-to-Word Dependency, Definite (.) vs Uncertain (,) Spaces, '
                 '3x3 Morphological Slot Coupling Across Lags d=1..6, and Drawing-Intrusion (<->) Reset',
        'parameters': {
            'seed': 241,
            'perms': args.perms,
            'strata': 'Currier language (A/B) x section ($I)',
            'running_text_filter': "unit == 'P' and unit_sub != 't'",
        },
        'T1_definite_vs_uncertain_spaces': t1,
        'T2_slot_coupling_and_lag_decay': t2,
        'T3_drawing_intrusion_experiment': t3,
        'T4_natural_language_and_synthetic_controls': t4,
        'T5_visual_forensics_pixel_profile': t5,
    }
    with open(OUT_JSON, 'w', encoding='utf-8') as fh:
        json.dump(clean_json(out), fh, indent=1, ensure_ascii=False)
    print("Wrote", OUT_JSON)


if __name__ == '__main__':
    main()
