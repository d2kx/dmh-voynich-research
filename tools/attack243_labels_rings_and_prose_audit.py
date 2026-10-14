#!/usr/bin/env python3
"""
Attack 243: Comprehensive Audit & Structural Analysis of Labels (unit == 'L'),
Circular Rings (unit == 'C'), and Radial Spokes (unit == 'R') vs. Running Prose (unit == 'P').

Implements five empirical tests (T1-T5):
  T1: Structural & Morphological Taxonomy of P vs L vs C vs R (ZL3b-n.txt & IT2a-n.txt),
      with Stratified Mantel-Haenszel Odds Ratios controlling for (lang, section).
  T2: Within-Unit Sandhi (Adjacent-Word Final x Initial Glyph Excess MI) & Sequential
      Clockwise Similarity in C (Rings), R (Spokes), and L (Labels) vs P (Prose).
  T3: Strict 4-Tier Permutation & Length-Weighted Null Audit of Same-Folio Label-to-Prose
      (L -> P) and Label-to-Ring/Spoke (L -> C/R) Matching.
  T4: Cross-Folio & Cross-Section Rare Label-to-Prose Concordance Audit against a
      (Frequency, Length)-Matched Random Vocabulary Baseline.
  T5: High-Resolution Visual Forensic Scan Crops (f99v, f89r2, f82v, f75v) & Diagnostic Plot.

Outputs:
  - data/attack243_labels_rings_and_prose_audit.json
  - pages/l243_unit_taxonomy_and_matching.png
  - pages/l243_f99v_doldam_exact_match.png
  - pages/l243_f89r2_opcheor_exact_match.png
  - pages/l243_f82v_okoldy_olkol_matches.png
  - pages/l243_f75v_olol_qolol_matches.png
"""

from __future__ import annotations

import io
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Tuple

import pymupdf
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from voynich_corpus import Line, load_folio_meta, load_lines, paragraphs  # noqa: E402

DATA_DIR = ROOT / "data"
PAGES_DIR = ROOT / "pages"
OUT_JSON = DATA_DIR / "attack243_labels_rings_and_prose_audit.json"
PDF_YALE = ROOT / "books" / "voynich-yale-beinecke-2026-highres-214p.pdf"

EVA_MULTI = ("cth", "ckh", "cph", "cfh", "ch", "sh")


# ---------------------------------------------------------------------------
# Glyph & Morphological Normalization Helpers
# ---------------------------------------------------------------------------

def eva_glyphs(w: str) -> List[str]:
    out: List[str] = []
    i = 0
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


def first_glyph(w: str) -> str:
    gs = eva_glyphs(w)
    return gs[0] if gs else ""


def last_glyph(w: str) -> str:
    return w[-1] if w else ""


def tier0_exact(w: str) -> str:
    """Tier 0: Exact surface match (zero normalization)."""
    return w.strip().lower()


def tier1_proclitic(w: str) -> str:
    """Tier 1: Proclitic q-/y- stripping only (allows oX <-> qoX and X <-> yX)."""
    s = w.strip().lower()
    if s.startswith("qo") and len(s) > 3:
        return s[1:]
    if s.startswith("y") and len(s) > 3:
        return s[1:]
    return s


def tier2_4rule(w: str) -> str:
    """Tier 2: 4-Rule Canonical Form (proclitic strip + gallows merge + vowel run + -m->-r)."""
    s = tier1_proclitic(w)
    s = s.replace("cph", "cth").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    if s.endswith("m") and len(s) >= 4:
        s = s[:-1] + "r"
    return s


def tier3_stem230(w: str) -> str:
    """Tier 3: Aggressive prefix+suffix stripper from Attack 230."""
    s = re.sub(r"[^a-zA-Z]", "", w).lower()
    if not s:
        return ""
    s = re.sub(r"^qo", "o", s)
    s = s.replace("eee", "e").replace("ee", "e").replace("ii", "i")
    s = s.replace("f", "p").replace("k", "t")
    for p in ["o", "d", "y", "s"]:
        if len(s) > 3 and s.startswith(p):
            s = s[len(p):]
            break
    for sfx in [
        "aiin", "ain", "edy", "eey", "ody", "ady",
        "al", "ar", "or", "ol", "am", "an", "dy", "ey", "y",
    ]:
        if len(s) > len(sfx) + 1 and s.endswith(sfx):
            s = s[:-len(sfx)]
            break
    return s


# ---------------------------------------------------------------------------
# Statistical Helpers
# ---------------------------------------------------------------------------

def mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def sd(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def zscore(obs: float, null: List[float]) -> float:
    s = sd(null)
    return (obs - mean(null)) / s if s > 1e-12 else 0.0


def perm_p_upper(obs: float, null: List[float]) -> float:
    return (1 + sum(1 for v in null if v >= obs)) / (1 + len(null))


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


def mantel_haenszel(tables: List[Tuple[int, int, int, int]]) -> Dict[str, Any]:
    """Robins-Breslow-Greenland Mantel-Haenszel odds ratio across 2x2 strata (a,b,c,d)."""
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
        return {"or": None, "ci95": [None, None], "mh_chi2": 0.0, "p": 1.0}
    OR = sR / sS
    var = sPR / (2 * sR ** 2) + sPSQR / (2 * sR * sS) + sQS / (2 * sS ** 2)
    se = math.sqrt(max(0.0, var))
    chi = (abs(sa - sea) - 0.5) ** 2 / sva if sva > 0 else 0.0
    return {
        "or": round(OR, 4),
        "ci95": [round(OR * math.exp(-1.96 * se), 4), round(OR * math.exp(1.96 * se), 4)],
        "mh_chi2": round(chi, 2),
        "p": chi2_sf(chi, 1),
        "observed": int(sa),
        "expected": round(sea, 2),
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


def tvd_counters(c1: Counter, c2: Counter) -> float:
    n1, n2 = sum(c1.values()), sum(c2.values())
    if n1 == 0 or n2 == 0:
        return 0.0
    cats = set(c1.keys()) | set(c2.keys())
    return 0.5 * sum(abs(c1[k] / n1 - c2[k] / n2) for k in cats)


def levenshtein_sim(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    la, lb = len(a), len(b)
    dp = list(range(lb + 1))
    for i in range(1, la + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, lb + 1):
            temp = dp[j]
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + cost)
            prev = temp
    return 1.0 - dp[lb] / max(la, lb)


# ---------------------------------------------------------------------------
# T1: Structural & Morphological Taxonomy of P vs L vs C vs R
# ---------------------------------------------------------------------------

def compute_token_bucket_stats(
    tokens: List[str],
    loci_count: int,
    global_freq: Counter,
    rng: random.Random,
) -> Dict[str, Any]:
    n = len(tokens)
    if n == 0:
        return {"loci": loci_count, "tokens": 0}
    types = len(set(tokens))
    lengths = [len(eva_glyphs(w)) for w in tokens]
    hapaxes = sum(1 for w in tokens if global_freq[w] == 1)

    # Subsampled TTR at k=200 and k=35
    ttr_200 = None
    if n >= 200:
        subs = [len(set(rng.sample(tokens, 200))) / 200.0 for _ in range(200)]
        ttr_200 = round(mean(subs), 4)
    ttr_35 = None
    if n >= 35:
        subs35 = [len(set(rng.sample(tokens, 35))) / 35.0 for _ in range(200)]
        ttr_35 = round(mean(subs35), 4)

    init_c = Counter(first_glyph(w) for w in tokens)
    final_c = Counter(last_glyph(w) for w in tokens)

    def rate(pred: Callable[[str], bool]) -> float:
        return round(sum(1 for w in tokens if pred(w)) / n, 4)

    return {
        "loci": loci_count,
        "tokens": n,
        "types": types,
        "raw_ttr": round(types / n, 4),
        "ttr_at_200": ttr_200,
        "ttr_at_35": ttr_35,
        "mean_glyph_len": round(mean(lengths), 3),
        "sd_glyph_len": round(sd(lengths), 3),
        "global_hapax_rate": round(hapaxes / n, 4),
        "initial_rates": {
            "q": round(init_c["q"] / n, 4),
            "o": round(init_c["o"] / n, 4),
            "y": round(init_c["y"] / n, 4),
            "d": round(init_c["d"] / n, 4),
            "s": round(init_c["s"] / n, 4),
            "ch": round(init_c["ch"] / n, 4),
            "sh": round(init_c["sh"] / n, 4),
            "pf": round((init_c["p"] + init_c["f"] + init_c["cph"] + init_c["cfh"]) / n, 4),
            "tk": round((init_c["t"] + init_c["k"] + init_c["cth"] + init_c["ckh"]) / n, 4),
        },
        "final_rates": {
            "y": round(final_c["y"] / n, 4),
            "n": round(final_c["n"] / n, 4),
            "l": round(final_c["l"] / n, 4),
            "r": round(final_c["r"] / n, 4),
            "s": round(final_c["s"] / n, 4),
            "d": round(final_c["d"] / n, 4),
            "m": round(final_c["m"] / n, 4),
            "g": round(final_c["g"] / n, 4),
        },
        "suffix_rates": {
            "edy": rate(lambda w: w.endswith("edy")),
            "aiin_ain": rate(lambda w: w.endswith(("aiin", "ain"))),
            "ol_al_or_ar": rate(lambda w: w.endswith(("ol", "al", "or", "ar"))),
            "am_om": rate(lambda w: w.endswith(("am", "om"))),
        },
        "_init_counter": init_c,
        "_final_counter": final_c,
    }


def run_t1_taxonomy(lines: List[Line], dataset_name: str = "ZL3b") -> Dict[str, Any]:
    rng = random.Random(24301)
    global_freq = Counter(w for l in lines for w in l.clean_words)

    buckets: Dict[str, List[str]] = defaultdict(list)
    loci_counts: Counter = Counter()

    # Strata token lists for Mantel-Haenszel: (lang, section) -> unit -> list of words
    strata_words: Dict[Tuple[str, str], Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))

    for l in lines:
        ws = l.clean_words
        u = l.unit
        sub = l.unit_sub
        loci_counts[f"unit_{u}"] += 1
        loci_counts[f"sub_{u}{sub}"] += 1
        if l.folio != "fRos":
            loci_counts[f"no_fRos_unit_{u}"] += 1

        if not ws:
            continue

        buckets[f"unit_{u}"].extend(ws)
        buckets[f"sub_{u}{sub}"].extend(ws)
        if l.folio != "fRos":
            buckets[f"no_fRos_unit_{u}"].extend(ws)

        st = (l.lang, l.section)
        strata_words[st][u].extend(ws)

        if u == "P":
            if len(ws) >= 3:
                buckets["P_line_start"].append(ws[0])
                loci_counts["P_line_start"] += 1
                buckets["P_line_end"].append(ws[-1])
                loci_counts["P_line_end"] += 1
                buckets["P_line_mid"].extend(ws[1:-1])
                loci_counts["P_line_mid"] += len(ws) - 2
        elif u == "L":
            if len(ws) == 1:
                buckets["L_single_word"].extend(ws)
                loci_counts["L_single_word"] += 1
            else:
                buckets["L_multi_word"].extend(ws)
                loci_counts["L_multi_word"] += 1

    bucket_order = [
        "unit_P", "no_fRos_unit_P", "P_line_start", "P_line_mid", "P_line_end", "sub_Pb",
        "unit_L", "no_fRos_unit_L", "L_single_word", "L_multi_word",
        "sub_Lz", "sub_Lf", "sub_L0", "sub_Ls", "sub_Ln", "sub_Lt", "sub_Lc",
        "unit_C", "no_fRos_unit_C", "sub_Cc",
        "unit_R", "sub_Ri", "sub_Ro",
    ]

    raw_stats = {}
    for b in bucket_order:
        if b in buckets or loci_counts[b] > 0:
            raw_stats[b] = compute_token_bucket_stats(buckets[b], loci_counts[b], global_freq, rng)

    # Compute TVD between L, C, R and P_line_start / P_line_mid / P_line_end
    tvd_matrix = {}
    for u_key in ["unit_L", "unit_C", "unit_R", "sub_Lf", "sub_Lz", "sub_Ln", "sub_Lc"]:
        if u_key not in raw_stats or raw_stats[u_key]["tokens"] == 0:
            continue
        tvd_matrix[u_key] = {}
        for p_key in ["unit_P", "P_line_start", "P_line_mid", "P_line_end"]:
            tvd_init = tvd_counters(raw_stats[u_key]["_init_counter"], raw_stats[p_key]["_init_counter"])
            tvd_fin = tvd_counters(raw_stats[u_key]["_final_counter"], raw_stats[p_key]["_final_counter"])
            tvd_matrix[u_key][p_key] = {
                "tvd_initial": round(tvd_init, 4),
                "tvd_final": round(tvd_fin, 4),
                "tvd_mean": round(0.5 * (tvd_init + tvd_fin), 4),
            }

    # Remove internal counters before JSON serialization
    for b in raw_stats:
        raw_stats[b].pop("_init_counter", None)
        raw_stats[b].pop("_final_counter", None)

    # Stratified Mantel-Haenszel Odds Ratios: L vs P, C vs P, R vs P
    features: Dict[str, Callable[[str], bool]] = {
        "init_q": lambda w: first_glyph(w) == "q",
        "init_o": lambda w: first_glyph(w) == "o",
        "init_y": lambda w: first_glyph(w) == "y",
        "init_d": lambda w: first_glyph(w) == "d",
        "init_s": lambda w: first_glyph(w) == "s",
        "init_ch": lambda w: first_glyph(w) == "ch",
        "init_sh": lambda w: first_glyph(w) == "sh",
        "init_pf": lambda w: first_glyph(w) in ("p", "f", "cph", "cfh"),
        "init_tk": lambda w: first_glyph(w) in ("t", "k", "cth", "ckh"),
        "final_y": lambda w: last_glyph(w) == "y",
        "final_n": lambda w: last_glyph(w) == "n",
        "final_l": lambda w: last_glyph(w) == "l",
        "final_r": lambda w: last_glyph(w) == "r",
        "final_s": lambda w: last_glyph(w) == "s",
        "final_m": lambda w: last_glyph(w) == "m",
        "sfx_edy": lambda w: w.endswith("edy"),
        "sfx_aiin": lambda w: w.endswith(("aiin", "ain")),
        "sfx_ol_al_or_ar": lambda w: w.endswith(("ol", "al", "or", "ar")),
    }

    mh_results: Dict[str, Dict[str, Any]] = {}
    for cmp_name, target_u in [("L_vs_P", "L"), ("C_vs_P", "C"), ("R_vs_P", "R")]:
        mh_results[cmp_name] = {}
        # Use section/lang strata where both target_u and P exist, plus pooled Currier-language fallback
        for fname, fpred in features.items():
            tables_sec = []
            for st, udict in strata_words.items():
                ws_u = udict.get(target_u, [])
                ws_p = udict.get("P", [])
                if not ws_u or not ws_p:
                    continue
                a = sum(1 for w in ws_u if fpred(w))
                b = len(ws_u) - a
                c = sum(1 for w in ws_p if fpred(w))
                d = len(ws_p) - c
                tables_sec.append((a, b, c, d))
            # Also compute pooled 2x2 across all tokens of target_u vs P
            ws_u_all = buckets[f"unit_{target_u}"]
            ws_p_all = buckets["unit_P"]
            a0 = sum(1 for w in ws_u_all if fpred(w))
            b0 = len(ws_u_all) - a0
            c0 = sum(1 for w in ws_p_all if fpred(w))
            d0 = len(ws_p_all) - c0
            pooled_or = ((a0 + 0.5) * (d0 + 0.5)) / ((b0 + 0.5) * (c0 + 0.5))
            mh_sec = mantel_haenszel(tables_sec)
            mh_sec["pooled_or"] = round(pooled_or, 4)
            mh_sec["target_rate"] = round(a0 / max(1, len(ws_u_all)), 4)
            mh_sec["prose_rate"] = round(c0 / max(1, len(ws_p_all)), 4)
            mh_results[cmp_name][fname] = mh_sec

    return {
        "dataset": dataset_name,
        "buckets": raw_stats,
        "tvd_to_prose_positions": tvd_matrix,
        "mantel_haenszel": mh_results,
    }


# ---------------------------------------------------------------------------
# T2: Within-Unit Sandhi & Sequential Order Test in C, R, and L vs P
# ---------------------------------------------------------------------------

def compute_excess_mi(
    items: List[Tuple[str, str, Tuple[str, str]]],
    perms: int = 2000,
    seed: int = 24302,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    n = len(items)
    if n == 0:
        return {"n_pairs": 0}
    pairs = [(a, b) for a, b, _ in items]
    obs = mutual_info(pairs)
    strata = defaultdict(list)
    for idx, (_, _, st) in enumerate(items):
        strata[st].append(idx)
    ys = [b for _, b in pairs]
    null_vals = []
    for _ in range(perms):
        ny = ys[:]
        for idxs in strata.values():
            sub = [ys[i] for i in idxs]
            rng.shuffle(sub)
            for i, v in zip(idxs, sub):
                ny[i] = v
        null_vals.append(mutual_info([(pairs[i][0], ny[i]) for i in range(n)]))
    m = mean(null_vals)
    s = sd(null_vals)
    z = (obs - m) / s if s > 1e-12 else 0.0
    return {
        "n_pairs": n,
        "obs_mi_bits": round(obs, 4),
        "null_mean_bits": round(m, 4),
        "null_sd_bits": round(s, 4),
        "excess_mi_bits": round(obs - m, 4),
        "z_score": round(z, 2),
        "perm_p": perm_p_upper(obs, null_vals),
    }


def run_t2_sandhi_and_sequence(lines: List[Line]) -> Dict[str, Any]:
    rng = random.Random(24302)
    within_items: Dict[str, List[Tuple[str, str, Tuple[str, str]]]] = defaultdict(list)
    ring_wrap_items: List[Tuple[str, str, Tuple[str, str]]] = []

    for l in lines:
        ws = l.clean_words
        intr = set(l.intrusion_after)
        st = (l.lang, l.section)
        for i in range(len(ws) - 1):
            if i in intr:
                continue
            within_items[l.unit].append((last_glyph(ws[i]), first_glyph(ws[i + 1]), st))
        if l.unit == "C" and len(ws) >= 4:
            # Wrap-around pair: last word of circular ring -> first word of same circular ring
            ring_wrap_items.append((last_glyph(ws[-1]), first_glyph(ws[0]), st))

    # Consecutive L loci on the same folio & subtype
    l_consec_items: List[Tuple[str, str, Tuple[str, str]]] = []
    by_fol_sub_L: Dict[Tuple[str, str], List[Line]] = defaultdict(list)
    for l in lines:
        if l.unit == "L" and l.clean_words:
            by_fol_sub_L[(l.folio, l.unit_sub)].append(l)
    for (fol, sub), llist in by_fol_sub_L.items():
        for i in range(len(llist) - 1):
            w1 = llist[i].clean_words[-1]
            w2 = llist[i + 1].clean_words[0]
            l_consec_items.append((last_glyph(w1), first_glyph(w2), (llist[i].lang, llist[i].section)))

    # Consecutive R loci on the same folio & subtype
    r_consec_items: List[Tuple[str, str, Tuple[str, str]]] = []
    by_fol_sub_R: Dict[Tuple[str, str], List[Line]] = defaultdict(list)
    for l in lines:
        if l.unit == "R" and l.clean_words:
            by_fol_sub_R[(l.folio, l.unit_sub)].append(l)
    for (fol, sub), llist in by_fol_sub_R.items():
        for i in range(len(llist) - 1):
            w1 = llist[i].clean_words[-1]
            w2 = llist[i + 1].clean_words[0]
            r_consec_items.append((last_glyph(w1), first_glyph(w2), (llist[i].lang, llist[i].section)))

    # Subsample P to match C (n=2248) and R (n=203)
    p_sub_2248 = rng.sample(within_items["P"], min(len(within_items["C"]), len(within_items["P"])))
    p_sub_203 = rng.sample(within_items["P"], min(len(within_items["R"]), len(within_items["P"])))

    sandhi_results = {
        "P_within_line_all": compute_excess_mi(within_items["P"], perms=1000, seed=101),
        "P_within_line_sub2248": compute_excess_mi(p_sub_2248, perms=1000, seed=102),
        "P_within_line_sub203": compute_excess_mi(p_sub_203, perms=1000, seed=103),
        "C_within_ring": compute_excess_mi(within_items["C"], perms=2000, seed=104),
        "C_ring_wraparound_last_to_first": compute_excess_mi(ring_wrap_items, perms=2000, seed=105),
        "R_within_spoke": compute_excess_mi(within_items["R"], perms=2000, seed=106),
        "R_across_consecutive_spokes": compute_excess_mi(r_consec_items, perms=2000, seed=107),
        "L_within_multiword_label": compute_excess_mi(within_items["L"], perms=2000, seed=108),
        "L_across_consecutive_labels": compute_excess_mi(l_consec_items, perms=2000, seed=109),
    }

    # Also inspect circular ring start vs internal initial glyph distribution (to see if @Cc has a true start marker)
    c_start_words = [l.clean_words[0] for l in lines if l.unit == "C" and len(l.clean_words) >= 4]
    c_end_words = [l.clean_words[-1] for l in lines if l.unit == "C" and len(l.clean_words) >= 4]
    c_mid_words = [w for l in lines if l.unit == "C" and len(l.clean_words) >= 4 for w in l.clean_words[1:-1]]
    ring_boundary_profile = {
        "n_rings_ge4": len(c_start_words),
        "start_pf_tk_gallows_rate": round(sum(1 for w in c_start_words if first_glyph(w) in ("p", "f", "t", "k", "cph", "cfh", "cth", "ckh")) / max(1, len(c_start_words)), 4),
        "mid_pf_tk_gallows_rate": round(sum(1 for w in c_mid_words if first_glyph(w) in ("p", "f", "t", "k", "cph", "cfh", "cth", "ckh")) / max(1, len(c_mid_words)), 4),
        "start_o_rate": round(sum(1 for w in c_start_words if first_glyph(w) == "o") / max(1, len(c_start_words)), 4),
        "mid_o_rate": round(sum(1 for w in c_mid_words if first_glyph(w) == "o") / max(1, len(c_mid_words)), 4),
        "end_m_rate": round(sum(1 for w in c_end_words if last_glyph(w) == "m") / max(1, len(c_end_words)), 4),
        "mid_m_rate": round(sum(1 for w in c_mid_words if last_glyph(w) == "m") / max(1, len(c_mid_words)), 4),
    }

    # Clockwise / sequential orthographic similarity of consecutive labels within (folio, unit_sub)
    seq_similarity_by_sub: Dict[str, Any] = {}
    for target_sub in ["ALL", "z", "f", "0", "s", "n", "t", "c"]:
        groups: List[List[str]] = []
        for (fol, sub), llist in sorted(by_fol_sub_L.items()):
            if target_sub != "ALL" and sub != target_sub:
                continue
            ws = [l.clean_words[0] for l in llist if l.clean_words and len(l.clean_words[0]) >= 3]
            if len(ws) >= 4:
                groups.append(ws)
        if not groups:
            continue

        def seq_metrics(glist: List[List[str]]) -> Tuple[float, float, float]:
            sims, pref2, suf2 = [], [], []
            for ws in glist:
                for i in range(len(ws) - 1):
                    a, b = ws[i], ws[i + 1]
                    sims.append(levenshtein_sim(a, b))
                    pref2.append(1.0 if a[:2] == b[:2] else 0.0)
                    suf2.append(1.0 if a[-2:] == b[-2:] else 0.0)
            return mean(sims), mean(pref2), mean(suf2)

        obs_sim, obs_p2, obs_s2 = seq_metrics(groups)
        null_sim, null_p2, null_s2 = [], [], []
        for _ in range(3000):
            shuf_groups = []
            for ws in groups:
                wcopy = ws[:]
                rng.shuffle(wcopy)
                shuf_groups.append(wcopy)
            ms, mp, msf = seq_metrics(shuf_groups)
            null_sim.append(ms)
            null_p2.append(mp)
            null_s2.append(msf)

        n_adj = sum(len(ws) - 1 for ws in groups)
        seq_similarity_by_sub[f"L_{target_sub}"] = {
            "n_folio_groups": len(groups),
            "n_adjacent_pairs": n_adj,
            "levenshtein_sim": {
                "obs": round(obs_sim, 4),
                "null_mean": round(mean(null_sim), 4),
                "null_sd": round(sd(null_sim), 4),
                "z": round(zscore(obs_sim, null_sim), 2),
                "p": round(perm_p_upper(obs_sim, null_sim), 4),
            },
            "shared_prefix2": {
                "obs": round(obs_p2, 4),
                "null_mean": round(mean(null_p2), 4),
                "z": round(zscore(obs_p2, null_p2), 2),
                "p": round(perm_p_upper(obs_p2, null_p2), 4),
            },
            "shared_suffix2": {
                "obs": round(obs_s2, 4),
                "null_mean": round(mean(null_s2), 4),
                "z": round(zscore(obs_s2, null_s2), 2),
                "p": round(perm_p_upper(obs_s2, null_s2), 4),
            },
        }

    return {
        "juncture_sandhi_mi": sandhi_results,
        "circular_ring_boundary_profile": ring_boundary_profile,
        "sequential_label_clustering": seq_similarity_by_sub,
    }


# ---------------------------------------------------------------------------
# T3: Strict 4-Tier Permutation & Length-Weighted Null Audit of Same-Folio L->P
# ---------------------------------------------------------------------------

def run_t3_same_folio_matching(lines: List[Line], n_perms: int = 10000) -> Dict[str, Any]:
    rng = random.Random(24303)

    fol_L: Dict[str, List[str]] = defaultdict(list)
    fol_L_loci: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    fol_P: Dict[str, List[str]] = defaultdict(list)
    fol_P_loci: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    fol_CR: Dict[str, List[str]] = defaultdict(list)
    fol_meta: Dict[str, Tuple[str, str]] = {}

    for l in lines:
        fol_meta[l.folio] = (l.section, l.lang)
        ws = l.clean_words
        if l.unit == "L":
            fol_L[l.folio].extend(ws)
            for w in ws:
                fol_L_loci[l.folio].append((w, l.locus, f"{l.pos_code}{l.unit}{l.unit_sub}"))
        elif l.unit == "P":
            fol_P[l.folio].extend(ws)
            for w in ws:
                fol_P_loci[l.folio].append((w, l.locus))
        elif l.unit in ("C", "R"):
            fol_CR[l.folio].extend(ws)

    both_LP = sorted([f for f in fol_L if fol_L[f] and fol_P[f]])
    both_LCR = sorted([f for f in fol_L if fol_L[f] and fol_CR[f]])

    all_P_words = [w for l in lines if l.unit == "P" for w in l.clean_words]
    total_P_tokens = len(all_P_words)

    tiers: List[Tuple[str, Callable[[str], str]]] = [
        ("Tier0_Exact", tier0_exact),
        ("Tier1_Proclitic_qy", tier1_proclitic),
        ("Tier2_4Rule_Canonical", tier2_4rule),
        ("Tier3_Attack230_Stemmer", tier3_stem230),
    ]

    thresholds = [
        ("all", 999999),
        ("freq_le_25", 25),
        ("freq_le_10", 10),
        ("freq_le_5", 5),
        ("freq_eq_1", 1),
    ]

    tier_results: Dict[str, Any] = {}

    for tname, fn in tiers:
        # Global frequency of transformed tokens in running prose P
        global_tfreq = Counter(fn(w) for w in all_P_words if fn(w))

        # Per-folio unique label roots (for labels with surface length >= 4)
        fol_L_roots: Dict[str, Set[str]] = {}
        fol_L_root_to_surface: Dict[str, Dict[str, Tuple[str, str, str]]] = {}
        for f in both_LP:
            rset: Set[str] = set()
            rmap: Dict[str, Tuple[str, str, str]] = {}
            for w, loc, utag in fol_L_loci[f]:
                if len(w) < 4:
                    continue
                rw = fn(w)
                if rw:
                    rset.add(rw)
                    if rw not in rmap:
                        rmap[rw] = (w, loc, utag)
            fol_L_roots[f] = rset
            fol_L_root_to_surface[f] = rmap

        fol_P_roots: Dict[str, Set[str]] = {}
        fol_P_root_to_surface: Dict[str, Dict[str, Tuple[str, str]]] = {}
        for f in both_LP:
            pset: Set[str] = set()
            pmap: Dict[str, Tuple[str, str]] = {}
            for w, loc in fol_P_loci[f]:
                rw = fn(w)
                if rw:
                    pset.add(rw)
                    if rw not in pmap:
                        pmap[rw] = (w, loc)
            fol_P_roots[f] = pset
            fol_P_root_to_surface[f] = pmap

        # Group folios by (section, lang) stratum for permutation null
        strata_folios: Dict[Tuple[str, str], List[str]] = defaultdict(list)
        for f in both_LP:
            strata_folios[fol_meta[f]].append(f)

        # Precompute analytical length-weighted expected match probability per (folio, label_root)
        # If root rw occurs F times in global prose (or stratum prose), probability that at least 1 token
        # lands in a random prose block of size N_P(f) is 1 - (1 - N_P(f)/N_total)^F
        tier_thresh_out: Dict[str, Any] = {}

        for th_name, max_f in thresholds:
            # Observed matches (overall and by section)
            obs_total = 0
            obs_by_sec = Counter()
            analytical_exp_total = 0.0
            analytical_var_total = 0.0
            analytical_exp_by_sec: Dict[str, float] = defaultdict(float)
            match_records = []

            for f in both_LP:
                sec, lang = fol_meta[f]
                n_pf = len(fol_P[f])
                q_f = n_pf / total_P_tokens
                pset = fol_P_roots[f]
                for rw in sorted(fol_L_roots[f]):
                    F = global_tfreq[rw]
                    if F == 0 or F > max_f:
                        continue
                    # Analytical binomial hit probability for a bag-of-words prose page of size n_pf
                    p_hit = 1.0 - ((1.0 - q_f) ** F)
                    analytical_exp_total += p_hit
                    analytical_var_total += p_hit * (1.0 - p_hit)
                    analytical_exp_by_sec[sec] += p_hit

                    if rw in pset:
                        obs_total += 1
                        obs_by_sec[sec] += 1
                        lw_surf, lw_loc, lw_utag = fol_L_root_to_surface[f][rw]
                        pw_surf, pw_loc = fol_P_root_to_surface[f][rw]
                        match_records.append({
                            "folio": f,
                            "section": sec,
                            "lang": lang,
                            "label_word": lw_surf,
                            "label_locus": lw_loc,
                            "label_type": lw_utag,
                            "prose_word": pw_surf,
                            "prose_locus": pw_loc,
                            "canonical_key": rw,
                            "global_prose_freq": F,
                            "folio_prose_words": n_pf,
                            "single_word_chance_prob": round(p_hit, 5),
                        })

            # 10,000-trial stratum-preserving permutation null
            null_totals = []
            null_sec_counts: Dict[str, List[int]] = defaultdict(list)

            # Pre-filter eligible label roots per folio for this threshold
            elig_L: Dict[str, Set[str]] = {
                f: {rw for rw in fol_L_roots[f] if 1 <= global_tfreq[rw] <= max_f}
                for f in both_LP
            }

            for _ in range(n_perms):
                shuf_P: Dict[str, Set[str]] = {}
                for st, flist in strata_folios.items():
                    psets = [fol_P_roots[f] for f in flist]
                    rng.shuffle(psets)
                    for f, ps in zip(flist, psets):
                        shuf_P[f] = ps
                tot_c = 0
                sec_c = Counter()
                for f in both_LP:
                    hits = len(elig_L[f] & shuf_P[f])
                    tot_c += hits
                    sec_c[fol_meta[f][0]] += hits
                null_totals.append(tot_c)
                for sec_k in ["P", "B", "H", "A", "C", "T"]:
                    null_sec_counts[sec_k].append(sec_c[sec_k])

            analyt_sd = math.sqrt(max(1e-12, analytical_var_total))
            analyt_z = (obs_total - analytical_exp_total) / analyt_sd

            sec_breakdown = {}
            for sec_k in ["P", "B", "H", "A", "C", "T"]:
                if sum(1 for f in both_LP if fol_meta[f][0] == sec_k) == 0:
                    continue
                s_obs = obs_by_sec[sec_k]
                s_null = null_sec_counts[sec_k]
                sec_breakdown[sec_k] = {
                    "obs": s_obs,
                    "perm_null_mean": round(mean(s_null), 3),
                    "perm_null_sd": round(sd(s_null), 3),
                    "perm_z": round(zscore(s_obs, s_null), 2),
                    "perm_p": round(perm_p_upper(s_obs, s_null), 4),
                    "length_weighted_exp": round(analytical_exp_by_sec[sec_k], 3),
                }

            tier_thresh_out[th_name] = {
                "obs_matches": obs_total,
                "perm_null_mean": round(mean(null_totals), 3),
                "perm_null_sd": round(sd(null_totals), 3),
                "perm_z": round(zscore(obs_total, null_totals), 2),
                "perm_p": round(perm_p_upper(obs_total, null_totals), 5),
                "length_weighted_exp": round(analytical_exp_total, 3),
                "length_weighted_sd": round(analyt_sd, 3),
                "length_weighted_z": round(analyt_z, 2),
                "by_section": sec_breakdown,
                "matches": sorted(match_records, key=lambda x: (x["global_prose_freq"], x["folio"])) if max_f <= 25 else match_records[:25],
            }

        tier_results[tname] = tier_thresh_out

    # Also test same-folio Label-to-Circular/Radial (L -> C/R) matching on the 21 diagram folios
    all_CR_words = [w for l in lines if l.unit in ("P", "C", "R") for w in l.clean_words]
    cr_freq_t0 = Counter(tier0_exact(w) for w in all_CR_words)
    cr_freq_t1 = Counter(tier1_proclitic(w) for w in all_CR_words)

    l_to_cr_matches = []
    for f in both_LCR:
        cset_t0 = {tier0_exact(w): w for w in fol_CR[f]}
        cset_t1 = {tier1_proclitic(w): w for w in fol_CR[f]}
        for lw in sorted(set(fol_L[f])):
            if len(lw) < 4:
                continue
            if lw in cset_t0 and cr_freq_t0[lw] <= 15:
                l_to_cr_matches.append({
                    "folio": f,
                    "section": fol_meta[f][0],
                    "tier": "Tier0_Exact",
                    "label_word": lw,
                    "ring_or_spoke_word": cset_t0[lw],
                    "global_pcr_freq": cr_freq_t0[lw],
                })
            elif tier1_proclitic(lw) in cset_t1 and cr_freq_t1[tier1_proclitic(lw)] <= 15:
                l_to_cr_matches.append({
                    "folio": f,
                    "section": fol_meta[f][0],
                    "tier": "Tier1_Proclitic",
                    "label_word": lw,
                    "ring_or_spoke_word": cset_t1[tier1_proclitic(lw)],
                    "global_pcr_freq": cr_freq_t1[tier1_proclitic(lw)],
                })

    return {
        "n_folios_with_both_L_and_P": len(both_LP),
        "folios_with_both_L_and_P": both_LP,
        "n_folios_with_both_L_and_CR": len(both_LCR),
        "tiers": tier_results,
        "same_folio_L_to_CR_rare_matches": sorted(l_to_cr_matches, key=lambda x: x["global_pcr_freq"]),
    }


# ---------------------------------------------------------------------------
# T4: Cross-Folio & Cross-Section Rare Label-to-Prose Concordance Audit
# ---------------------------------------------------------------------------

def run_t4_cross_section_concordance(lines: List[Line], n_perms: int = 5000) -> Dict[str, Any]:
    rng = random.Random(24304)

    target_sections = ["H", "P", "B", "S", "T", "C", "A"]
    prose_by_sec: Dict[str, Counter] = {sec: Counter() for sec in target_sections}
    all_prose_counter = Counter()

    for l in lines:
        if l.unit == "P" and l.section in prose_by_sec:
            for w in l.clean_words:
                prose_by_sec[l.section][w] += 1
                all_prose_counter[w] += 1

    section_token_shares = {
        sec: {
            "tokens": sum(prose_by_sec[sec].values()),
            "share": round(sum(prose_by_sec[sec].values()) / max(1, sum(all_prose_counter.values())), 4),
            "rare_types_le5": sum(1 for w, c in prose_by_sec[sec].items() if 1 <= all_prose_counter[w] <= 5 and len(w) >= 4),
        }
        for sec in target_sections
    }

    # Build pool of all prose word types with len >= 4 grouped by exact global frequency F
    # so we can sample frequency-matched random word types
    pool_by_freq_t0: Dict[int, List[str]] = defaultdict(list)
    for w, c in all_prose_counter.items():
        if len(w) >= 4:
            pool_by_freq_t0[c].append(w)

    # Also build Tier 1 proclitic counters
    prose_by_sec_t1: Dict[str, Counter] = {sec: Counter() for sec in target_sections}
    all_prose_t1 = Counter()
    for sec in target_sections:
        for w, c in prose_by_sec[sec].items():
            rw = tier1_proclitic(w)
            prose_by_sec_t1[sec][rw] += c
            all_prose_t1[rw] += c

    pool_by_freq_t1: Dict[int, List[str]] = defaultdict(list)
    for rw, c in all_prose_t1.items():
        if len(rw) >= 4:
            pool_by_freq_t1[c].append(rw)

    subtypes = ["f", "c", "n", "t", "z", "s", "0"]
    concordance_results: Dict[str, Any] = {}

    for tier_label, fn, sec_cnts, glob_cnts, freq_pool in [
        ("Tier0_Exact", tier0_exact, prose_by_sec, all_prose_counter, pool_by_freq_t0),
        ("Tier1_Proclitic_qy", tier1_proclitic, prose_by_sec_t1, all_prose_t1, pool_by_freq_t1),
    ]:
        tier_out: Dict[str, Any] = {}
        for max_f in [5, 10]:
            sub_out: Dict[str, Any] = {}
            for sub in subtypes:
                l_roots = sorted({
                    fn(w)
                    for l in lines
                    if l.unit == "L" and l.unit_sub == sub
                    for w in l.clean_words
                    if len(w) >= 4 and 1 <= glob_cnts[fn(w)] <= max_f
                })
                if not l_roots:
                    continue

                obs_sec = {sec: sum(1 for r in l_roots if sec_cnts[sec][r] > 0) for sec in target_sections}
                freqs = [glob_cnts[r] for r in l_roots]

                null_sec: Dict[str, List[int]] = {sec: [] for sec in target_sections}
                for _ in range(n_perms):
                    samp = [rng.choice(freq_pool[F]) for F in freqs]
                    for sec in target_sections:
                        null_sec[sec].append(sum(1 for r in samp if sec_cnts[sec][r] > 0))

                sec_stats = {}
                for sec in target_sections:
                    obs_v = obs_sec[sec]
                    nl = null_sec[sec]
                    sec_stats[sec] = {
                        "obs_types": obs_v,
                        "obs_rate": round(obs_v / len(l_roots), 4),
                        "null_mean": round(mean(nl), 2),
                        "null_rate": round(mean(nl) / len(l_roots), 4),
                        "z": round(zscore(obs_v, nl), 2),
                        "p": round(perm_p_upper(obs_v, nl), 4),
                    }

                sub_out[f"L{sub}"] = {
                    "n_rare_label_types": len(l_roots),
                    "target_sections": sec_stats,
                }
            tier_out[f"freq_le_{max_f}"] = sub_out
        concordance_results[tier_label] = tier_out

    # Compile complete catalog of ultra-rare (global prose freq == 1 or == 2) Tier 0 & Tier 1 label-to-prose matches across the codex
    fol_prose_loci_map: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)
    for l in lines:
        if l.unit == "P":
            for w in l.clean_words:
                fol_prose_loci_map[tier1_proclitic(w)].append((w, l.locus, l.section))

    ultra_rare_catalog = []
    seen_pairs = set()
    for l in lines:
        if l.unit != "L":
            continue
        for lw in l.clean_words:
            if len(lw) < 4:
                continue
            rw = tier1_proclitic(lw)
            F1 = all_prose_t1[rw]
            if 1 <= F1 <= 3:
                for pw, ploc, psec in fol_prose_loci_map[rw]:
                    key = (l.locus, lw, ploc, pw)
                    if key in seen_pairs:
                        continue
                    seen_pairs.add(key)
                    ultra_rare_catalog.append({
                        "label_folio": l.folio,
                        "label_locus": l.locus,
                        "label_subtype": f"L{l.unit_sub}",
                        "label_section": l.section,
                        "label_word": lw,
                        "prose_folio": ploc.split(".")[0],
                        "prose_locus": ploc,
                        "prose_section": psec,
                        "prose_word": pw,
                        "same_folio": l.folio == ploc.split(".")[0],
                        "same_section": l.section == psec,
                        "match_tier": "Tier0_Exact" if lw == pw else "Tier1_Proclitic_qy",
                        "global_prose_freq_t0": all_prose_counter[lw],
                        "global_prose_freq_t1": F1,
                    })

    ultra_rare_catalog.sort(key=lambda x: (not x["same_folio"], x["global_prose_freq_t1"], x["label_folio"]))

    return {
        "prose_section_token_shares": section_token_shares,
        "frequency_matched_concordance": concordance_results,
        "ultra_rare_label_to_prose_catalog_top60": ultra_rare_catalog[:60],
    }


# ---------------------------------------------------------------------------
# T5: High-Res Visual Forensic Scan Crops & Diagnostic Chart
# ---------------------------------------------------------------------------

def extract_folio_image(doc: pymupdf.Document, folio: str, idx_data: Dict[str, Any]) -> Image.Image:
    rec = idx_data["folios"][folio]["pdf_pages"][0]
    pno = rec["pdf1_page"]
    page = doc[pno - 1]
    info = page.get_image_info(xrefs=True)
    if info and info[0].get("xref"):
        base_img = doc.extract_image(info[0]["xref"])
        img = Image.open(io.BytesIO(base_img["image"])).convert("RGB")
    else:
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    # Apply subtle ink enhancement
    r, g, b = img.split()
    merged = Image.merge(
        "RGB",
        (ImageOps.autocontrast(r, cutoff=1), ImageOps.autocontrast(g, cutoff=1), ImageOps.autocontrast(b, cutoff=1)),
    )
    merged = ImageEnhance.Contrast(merged).enhance(1.35)
    merged = ImageEnhance.Sharpness(merged).enhance(1.35)
    return merged


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_side_by_side_card(
    img: Image.Image,
    crop_left: Tuple[float, float, float, float],
    crop_right: Tuple[float, float, float, float],
    title: str,
    left_caption: str,
    right_caption: str,
    out_path: Path,
) -> str:
    w, h = img.size
    x0, y0, x1, y1 = crop_left
    c1 = img.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    x0, y0, x1, y1 = crop_right
    c2 = img.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))

    target_h = 520
    w1 = int(c1.width * (target_h / c1.height))
    w2 = int(c2.width * (target_h / c2.height))
    c1 = c1.resize((w1, target_h), Image.Resampling.LANCZOS)
    c2 = c2.resize((w2, target_h), Image.Resampling.LANCZOS)

    pad = 24
    header_h = 92
    canvas_w = w1 + w2 + pad * 3
    canvas_h = target_h + header_h + pad
    canvas = Image.new("RGB", (canvas_w, canvas_h), (20, 24, 33))
    draw = ImageDraw.Draw(canvas)

    f_title = load_font(20, bold=True)
    f_sub = load_font(15, bold=False)

    draw.text((pad, 14), title, fill=(245, 222, 145), font=f_title)
    draw.text((pad, 48), left_caption, fill=(165, 230, 185), font=f_sub)
    draw.text((pad * 2 + w1, 48), right_caption, fill=(165, 210, 250), font=f_sub)

    canvas.paste(c1, (pad, header_h))
    canvas.paste(c2, (pad * 2 + w1, header_h))
    draw.rectangle([pad - 2, header_h - 2, pad + w1 + 2, header_h + target_h + 2], outline=(110, 200, 140), width=2)
    draw.rectangle(
        [pad * 2 + w1 - 2, header_h - 2, pad * 2 + w1 + w2 + 2, header_h + target_h + 2],
        outline=(110, 175, 235),
        width=2,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return str(out_path.relative_to(ROOT)).replace("\\", "/")


def generate_diagnostic_chart(t1: Dict[str, Any], t2: Dict[str, Any], t3: Dict[str, Any], out_path: Path) -> str:
    W, H = 1480, 880
    img = Image.new("RGB", (W, H), (18, 22, 30))
    draw = ImageDraw.Draw(img)
    f_h1 = load_font(22, bold=True)
    f_h2 = load_font(16, bold=True)
    f_body = load_font(14, bold=False)
    f_small = load_font(12, bold=False)

    draw.text(
        (28, 18),
        "Attack 243: Structural & Lexical Audit of Labels (L), Circular Rings (C), and Radial Spokes (R) vs Prose (P)",
        fill=(245, 225, 155),
        font=f_h1,
    )

    # Panel 1 (Top-Left): Initial q- vs Initial o- vs Suffix -edy across Units & Label Subtypes
    px0, py0, pw, ph = 28, 64, 690, 380
    draw.rectangle([px0, py0, px0 + pw, py0 + ph], fill=(26, 31, 42), outline=(70, 85, 110), width=2)
    draw.text((px0 + 16, py0 + 12), "T1: Morphological Shift Across Units & Label Subtypes (%)", fill=(180, 220, 255), font=f_h2)

    cats = [
        ("P (Prose)", "unit_P"),
        ("C (Rings)", "unit_C"),
        ("R (Spokes)", "unit_R"),
        ("L (All Labels)", "unit_L"),
        ("@Lf (Plants)", "sub_Lf"),
        ("@Lc (Jars)", "sub_Lc"),
        ("@Lz (Zodiac)", "sub_Lz"),
        ("@Ln (Nymphs)", "sub_Ln"),
        ("@Lt (Tubes)", "sub_Lt"),
    ]
    bstats = t1["buckets"]
    chart_x0, chart_y0, chart_w, chart_h = px0 + 135, py0 + 52, 330, 285
    for idx, (label_txt, bkey) in enumerate(cats):
        row_y = chart_y0 + idx * 31
        draw.text((px0 + 14, row_y + 4), label_txt, fill=(225, 230, 240), font=f_small)
        st = bstats[bkey]
        q_r = st["initial_rates"]["q"]
        o_r = st["initial_rates"]["o"]
        edy_r = st["suffix_rates"]["edy"]
        # Draw 3 horizontal mini-bars (max scale = 0.65)
        q_w = int((q_r / 0.65) * chart_w)
        o_w = int((o_r / 0.65) * chart_w)
        e_w = int((edy_r / 0.65) * chart_w)
        draw.rectangle([chart_x0, row_y + 2, chart_x0 + max(2, q_w), row_y + 9], fill=(235, 105, 95))
        draw.rectangle([chart_x0, row_y + 11, chart_x0 + max(2, o_w), row_y + 18], fill=(95, 195, 245))
        draw.rectangle([chart_x0, row_y + 20, chart_x0 + max(2, e_w), row_y + 27], fill=(130, 225, 145))
        draw.text(
            (chart_x0 + max(q_w, o_w, e_w) + 8, row_y + 5),
            f"q:{q_r*100:.1f}%  o:{o_r*100:.1f}%  -edy:{edy_r*100:.1f}%",
            fill=(195, 205, 215),
            font=f_small,
        )
    draw.text((px0 + 135, py0 + ph - 26), "Red = Initial q-     Blue = Initial o-     Green = Suffix -edy", fill=(200, 210, 225), font=f_small)

    # Panel 2 (Top-Right): T2 Within-Unit vs Cross-Unit Sandhi Excess MI (bits)
    px0, py0, pw, ph = 750, 64, 700, 380
    draw.rectangle([px0, py0, px0 + pw, py0 + ph], fill=(26, 31, 42), outline=(70, 85, 110), width=2)
    draw.text((px0 + 16, py0 + 12), "T2: Final x Initial Glyph Sandhi Excess MI (Delta MI in bits)", fill=(180, 220, 255), font=f_h2)

    mi_rows = [
        ("P: Within-Line Prose (n=29,913)", "P_within_line_all", (110, 210, 145)),
        ("P: Subsampled Prose (n=2,248)", "P_within_line_sub2248", (110, 210, 145)),
        ("C: Within Circular Ring (n=2,248)", "C_within_ring", (95, 195, 245)),
        ("C: Ring Wrap-Around Last->First (n=83)", "C_ring_wraparound_last_to_first", (155, 175, 245)),
        ("R: Within Multi-Word Spoke (n=203)", "R_within_spoke", (245, 195, 95)),
        ("R: Across Consecutive Spokes (n=129)", "R_across_consecutive_spokes", (235, 110, 100)),
        ("L: Within Multi-Word Label (n=162)", "L_within_multiword_label", (245, 195, 95)),
        ("L: Across Consecutive Labels (n=913)", "L_across_consecutive_labels", (235, 110, 100)),
    ]
    sdata = t2["juncture_sandhi_mi"]
    cx0, cy0, cw = px0 + 275, py0 + 56, 220
    for idx, (rlabel, rkey, col) in enumerate(mi_rows):
        ry = cy0 + idx * 38
        draw.text((px0 + 14, ry + 6), rlabel, fill=(225, 230, 240), font=f_small)
        rec = sdata[rkey]
        dmi = max(0.0, rec["excess_mi_bits"])
        z = rec["z_score"]
        bw = int((dmi / 0.24) * cw)
        draw.rectangle([cx0, ry + 4, cx0 + max(3, bw), ry + 24], fill=col)
        draw.text((cx0 + max(3, bw) + 8, ry + 6), f"{rec['excess_mi_bits']:+.4f}b (z={z:+.2f})", fill=(235, 240, 245), font=f_small)

    # Panel 3 (Bottom): T3 Same-Folio Label-to-Prose 4-Tier Permutation Audit
    px0, py0, pw, ph = 28, 468, 1422, 384
    draw.rectangle([px0, py0, px0 + pw, py0 + ph], fill=(26, 31, 42), outline=(70, 85, 110), width=2)
    draw.text(
        (px0 + 16, py0 + 14),
        "T3: Same-Folio Label-to-Prose Matching Audit Across 4 Equivalence Tiers (40 Folios with Both L & P, 10,000 Permutations)",
        fill=(180, 220, 255),
        font=f_h2,
    )

    headers = [
        "Equivalence Tier",
        "All Labels (Obs / Null / z)",
        "Rare <=25 (Obs / Null / z)",
        "Rare <=10 (Obs / Null / z)",
        "Rare <=5 (Obs / Null / z)",
        "Unique ==1 (Obs / Null / z)",
    ]
    col_x = [px0 + 18, px0 + 275, px0 + 505, px0 + 735, px0 + 965, px0 + 1190]
    for cx, htxt in zip(col_x, headers):
        draw.text((cx, py0 + 50), htxt, fill=(245, 215, 135), font=f_body)
    draw.line([px0 + 16, py0 + 74, px0 + pw - 16, py0 + 74], fill=(80, 95, 120), width=1)

    t_rows = [
        ("Tier 0: Exact Surface", "Tier0_Exact"),
        ("Tier 1: Proclitic q-/y-", "Tier1_Proclitic_qy"),
        ("Tier 2: 4-Rule Canonical", "Tier2_4Rule_Canonical"),
        ("Tier 3: Attack 230 Stem", "Tier3_Attack230_Stemmer"),
    ]
    th_keys = ["all", "freq_le_25", "freq_le_10", "freq_le_5", "freq_eq_1"]
    for r_idx, (t_label, t_key) in enumerate(t_rows):
        ry = py0 + 88 + r_idx * 42
        draw.text((col_x[0], ry), t_label, fill=(235, 240, 250), font=f_body)
        for c_idx, thk in enumerate(th_keys):
            cell = t3["tiers"][t_key][thk]
            obs = cell["obs_matches"]
            nm = cell["perm_null_mean"]
            z = cell["perm_z"]
            col_fill = (130, 235, 160) if z >= 2.5 else ((245, 210, 130) if z >= 1.65 else (195, 200, 210))
            draw.text((col_x[c_idx + 1], ry), f"{obs:3d} / {nm:5.2f} (z={z:+.2f})", fill=col_fill, font=f_body)

    # Highlight box at bottom of Panel 3 with headline rare matches
    draw.line([px0 + 16, py0 + 266, px0 + pw - 16, py0 + 266], fill=(80, 95, 120), width=1)
    draw.text(
        (px0 + 18, py0 + 278),
        "Verified Same-Folio Rare Label <-> Prose Matches (Tier 0 Exact & Tier 1 Proclitic oX <-> qoX, Global Prose Freq <= 10):",
        fill=(245, 222, 145),
        font=f_h2,
    )
    highlights = [
        "1. f89r2 ($I=P): @Lf 'opcheor' (f89r2.5) == Prose 'opcheor' (f89r2.22, Global Prose Freq = 1! Followed immediately by 'opcheol')",
        "2. f99v ($I=P):  @Lf 'doldam'  (f99v.31)  == Prose 'doldam'  (f99v.34, Global Prose Freq = 1! Line-final token below 3rd-row plant)",
        "3. f82v ($I=B):  @Lt 'olkol'   (f82v.46)  == Prose 'olkol'   (f82v.37, Global Prose Freq = 2) + @Lt 'okoldy' (f82v.45) <-> 'qokoldy' (f82v.13, Freq = 8)",
        "4. f99r ($I=P):  @Lf 'okeoly'  (f99r.25)  == Prose 'okeoly'  (f99r.18, Global Prose Freq = 3) + f89v1 @Lf 'opol' <-> 'qopol' (Freq = 8) + f102v2 'okeos' <-> 'qokeos' (Freq = 10)",
    ]
    for h_i, h_txt in enumerate(highlights):
        draw.text((px0 + 24, py0 + 304 + h_i * 19), h_txt, fill=(195, 230, 210), font=f_small)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return str(out_path.relative_to(ROOT)).replace("\\", "/")


def run_t5_visual_forensics(t1: Dict[str, Any], t2: Dict[str, Any], t3: Dict[str, Any]) -> Dict[str, Any]:
    with open(DATA_DIR / "folio_index.json", "r", encoding="utf-8") as fh:
        idx_data = json.load(fh)
    doc = pymupdf.open(str(PDF_YALE))

    chart_path = generate_diagnostic_chart(t1, t2, t3, PAGES_DIR / "l243_unit_taxonomy_and_matching.png")

    # 1. f99v: Register 3 (<f99v.31,@Lf> 'doldam' at far-right of 3rd plant row, y=0.43..0.60)
    # and <f99v.34,+P0> '...or.aiin.doldam' at right end of 3rd line of Register 3 paragraph (y=0.52..0.68)
    img_99v = extract_folio_image(doc, "f99v", idx_data)
    p_99v = make_side_by_side_card(
        img_99v,
        crop_left=(0.55, 0.42, 0.96, 0.62),
        crop_right=(0.15, 0.50, 0.90, 0.69),
        title="f99v ($I=P, Scribe 1): Exact Same-Folio Match 'doldam' <-> 'doldam' (Global Prose Freq = 1)",
        left_caption="Register 3 Right (<f99v.31,@Lf>): Plant #113 label 'doldam'",
        right_caption="Register 3 Prose (<f99v.34,+P0>): '...qokeeor.or.aiin.doldam'",
        out_path=PAGES_DIR / "l243_f99v_doldam_exact_match.png",
    )

    # 2. f89r2 (right panel of spread, x=0.52..0.98):
    # Top row right (<f89r2.5,@Lf> 'opcheor', x=0.68..0.98, y=0.04..0.36)
    # vs Bottom paragraph first line (<f89r2.22,@P0> 'kolches.sheol.qokeoefy.sheey.opcheor.opcheol...', x=0.54..0.92, y=0.54..0.95)
    img_89r2 = extract_folio_image(doc, "f89r2", idx_data)
    p_89r2 = make_side_by_side_card(
        img_89r2,
        crop_left=(0.68, 0.04, 0.98, 0.36),
        crop_right=(0.54, 0.54, 0.92, 0.95),
        title="f89r2 ($I=P, Scribe 1): Exact Same-Folio Match 'opcheor' <-> 'opcheor.opcheol' (Global Prose Freq = 1)",
        left_caption="Top Register Right (<f89r2.5,@Lf>): Botanical label 'opcheor'",
        right_caption="Bottom Paragraph (<f89r2.22,@P0>): 'kolches...sheey.opcheor.opcheol...'",
        out_path=PAGES_DIR / "l243_f89r2_opcheor_exact_match.png",
    )

    # 3. f82v: Bottom pool (<f82v.45,@Lt> 'okoldy' & <f82v.46,@Lt> 'olkol', x=0.14..0.75, y=0.75..0.98)
    # vs Prose lines (<f82v.13,+P0> '...qokoldy' and <f82v.37,+P0> '...chol.olkol.chckhy...', x=0.18..0.94, y=0.58..0.82)
    img_82v = extract_folio_image(doc, "f82v", idx_data)
    p_82v = make_side_by_side_card(
        img_82v,
        crop_left=(0.14, 0.75, 0.78, 0.98),
        crop_right=(0.16, 0.56, 0.92, 0.80),
        title="f82v ($I=B, Scribe 2): Dual Tube-Label Match 'olkol' == 'olkol' (Freq=2) & 'okoldy' <-> 'qokoldy' (Freq=8)",
        left_caption="Bottom Pool (<f82v.45-46,@Lt>): Adjacent labels 'okoldy' & 'olkol'",
        right_caption="Lower Prose (<f82v.37,+P0>): '...alchey.chol.olkol.chckhy...' above pool",
        out_path=PAGES_DIR / "l243_f82v_okoldy_olkol_matches.png",
    )

    # 4. f75v: Bottom pool (<f75v.50-52,=Lt> 'otal.opal / okeey.lol / olol', x=0.12..0.52, y=0.62..0.86)
    # vs Mid-prose (<f75v.40,+P0> '...qokain.olol', x=0.14..0.90, y=0.45..0.68)
    img_75v = extract_folio_image(doc, "f75v", idx_data)
    p_75v = make_side_by_side_card(
        img_75v,
        crop_left=(0.12, 0.62, 0.52, 0.86),
        crop_right=(0.14, 0.45, 0.92, 0.68),
        title="f75v ($I=B, Scribe 2): Both Tier 0 Exact ('olol'=='olol') & Tier 1 Proclitic ('olol'<->'qolol') on One Page",
        left_caption="Bottom Pool (<f75v.52,=Lt>): Label 'olol' above bathing nymphs",
        right_caption="Mid Prose (<f75v.40,+P0>): '...dol.ol,sheey.qokain.olol' at line end",
        out_path=PAGES_DIR / "l243_f75v_olol_qolol_matches.png",
    )

    return {
        "diagnostic_chart": chart_path,
        "forensic_crops": [p_99v, p_89r2, p_82v, p_75v],
    }


def main() -> None:
    print("Loading ZL3b-n.txt and IT2a-n.txt via voynich_corpus.py ...")
    lines_zl = load_lines(str(DATA_DIR / "ZL3b-n.txt"))
    lines_it = load_lines(str(DATA_DIR / "IT2a-n.txt"))

    print("Running T1: Structural & Morphological Taxonomy (ZL3b & IT2a) ...")
    t1_zl = run_t1_taxonomy(lines_zl, "ZL3b-n")
    t1_it = run_t1_taxonomy(lines_it, "IT2a-n")

    print("Running T2: Within-Unit Sandhi & Sequential Order Test ...")
    t2 = run_t2_sandhi_and_sequence(lines_zl)

    print("Running T3: Strict 4-Tier Permutation Audit of Same-Folio Label-to-Prose Matching ...")
    t3 = run_t3_same_folio_matching(lines_zl, n_perms=10000)

    print("Running T4: Cross-Folio & Cross-Section Rare Label Concordance Audit ...")
    t4 = run_t4_cross_section_concordance(lines_zl, n_perms=5000)

    print("Running T5: Generating High-Res Visual Forensic Crops & Diagnostic Plot ...")
    t5 = run_t5_visual_forensics(t1_zl, t2, t3)

    payload = {
        "attack": 243,
        "title": "Comprehensive Audit & Structural Analysis of Labels (L), Circular Rings (C), and Radial Spokes (R) vs Running Prose (P)",
        "T1_taxonomy_ZL3b": t1_zl,
        "T1_taxonomy_IT2a": {
            "buckets": {k: v for k, v in t1_it["buckets"].items() if k in ("unit_P", "unit_L", "unit_C", "unit_R", "sub_Lf", "sub_Lz", "sub_Ln", "sub_Lc")},
            "mantel_haenszel": t1_it["mantel_haenszel"],
        },
        "T2_sandhi_and_sequence": t2,
        "T3_same_folio_matching": t3,
        "T4_cross_section_concordance": t4,
        "T5_visual_forensics": t5,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print(f"Saved {OUT_JSON} ({OUT_JSON.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
