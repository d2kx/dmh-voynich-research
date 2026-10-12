#!/usr/bin/env python3
"""
Attack 51: The `l-` / `ol-` / `qol-` Liquid-Applicative Verbal & Nominal Derivative System
==========================================================================================
Investigates the `l + Consonant` (`lch-`, `lsh-`, `lk-`, `lt-`, `lp-`, `lf-`, `ld-`, `ls-`) prefix
family (`lchedy`, `lshedy`, `lkedy`, `lkeedy`, `lchey`, `lkar`, `lkeey`, `lkeol`, `ldaiin`, etc.)
and its relationship to `ol-X` and `qol-X`:
  1. Exact Stem-Stripping Verification: what percentage of `l + C` word tokens (`len >= 4`) leave an
     independently attested Voynich word `X` when initial `l-` is stripped (`l-chedy -> chedy`,
     `l-keedy -> keedy`, `l-daiin -> daiin`, `l-kar -> kar`), compared against 1,000 random consonant
     strip tests?
  2. The 4-Tuple Derivational Paradigm `[X, l-X, ol-X, qol-X]`: inventories all roots attested across
     all 4 slots (`chedy / lchedy / olchedy / qolchedy`, `keedy / lkeedy / olkeedy / qolkeedy`, etc.)
     and measures suffix-distribution cosine similarity between `X`, `l-X`, `ol-X`, and `qol-X`.
  3. Section Enrichment (`$I=B` Balneological & `$I=S` Starred Recipes vs other sections) via 1,000
     token-section permutations, testing whether `l-` functions as an incorporated fluid/bath applicative
     prefix (`ol` ["fluid/bath"] + `X` -> `l-X`).
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack51_l_prefix_derivative_system.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")
L_ONSETS = ("lch", "lsh", "lk", "lt", "lp", "lf", "ld", "ls")


def clean_tokens(raw: str) -> List[str]:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def is_l_cons(w: str) -> bool:
    return len(w) >= 4 and w.startswith(L_ONSETS)


def is_ol_cons(w: str) -> bool:
    return len(w) >= 5 and w.startswith("o") and w[1:].startswith(L_ONSETS)


def is_qol_cons(w: str) -> bool:
    return len(w) >= 6 and w.startswith("qo") and w[2:].startswith(L_ONSETS)


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    current_folio = ""
    current_sec = ""
    folio_sec: Dict[str, str] = {}

    all_tokens: List[Tuple[str, str]] = []  # (sec, word)
    vocab: Counter = Counter()
    pos_counts: Dict[str, Counter] = {
        "BARE_X": Counter(),
        "L_X": Counter(),
        "OL_X": Counter(),
        "QOL_X": Counter(),
    }

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("<f") and ">" in line and "." not in line.split(">")[0]:
            m_f = re.match(r"^<f([0-9]+[rv][0-9]*|Ros)>", line.split(">")[0] + ">")
            if m_f:
                current_folio = "f" + m_f.group(1)
            m_s = re.search(r"\$I=([A-Z])", line)
            current_sec = m_s.group(1) if m_s else "U"
            folio_sec[current_folio] = current_sec
            continue

        m = LOCUS_RE.match(line)
        if not m:
            continue
        folio = "f" + m.group(1)
        sec = folio_sec.get(folio, "U")
        toks = clean_tokens(m.group(4))
        n = len(toks)
        for i, w in enumerate(toks):
            all_tokens.append((sec, w))
            vocab[w] += 1
            p_slot = "init" if i == 0 else ("final" if i == n - 1 else "mid")
            if is_qol_cons(w):
                pos_counts["QOL_X"][p_slot] += 1
            elif is_ol_cons(w):
                pos_counts["OL_X"][p_slot] += 1
            elif is_l_cons(w):
                pos_counts["L_X"][p_slot] += 1

    # 1. Exact Stem-Stripping Verification for `l-X`, `ol-X`, and `qol-X`
    l_words = {w: cnt for w, cnt in vocab.items() if is_l_cons(w)}
    ol_words = {w: cnt for w, cnt in vocab.items() if is_ol_cons(w)}
    qol_words = {w: cnt for w, cnt in vocab.items() if is_qol_cons(w)}

    l_token_total = sum(l_words.values())
    l_attested_bare_tokens = sum(cnt for w, cnt in l_words.items() if w[1:] in vocab)
    l_attested_bare_types = sum(1 for w in l_words if w[1:] in vocab)

    # Also record pos_counts for BARE_X where X is the stripped base of an l_word
    bare_bases = {w[1:] for w in l_words if w[1:] in vocab}
    for line in lines_raw:
        m = LOCUS_RE.match(line.strip())
        if not m:
            continue
        toks = clean_tokens(m.group(4))
        n = len(toks)
        for i, w in enumerate(toks):
            if w in bare_bases:
                p_slot = "init" if i == 0 else ("final" if i == n - 1 else "mid")
                pos_counts["BARE_X"][p_slot] += 1

    # 2. Build the 4-Tuple Derivational Paradigm `[X, l-X, ol-X, qol-X]`
    all_base_stems: Set[str] = set()
    for w in l_words:
        all_base_stems.add(w[1:])
    for w in ol_words:
        all_base_stems.add(w[2:])
    for w in qol_words:
        all_base_stems.add(w[3:])

    paradigm_rows = []
    full_4tuple_count = 0
    at_least_3tuple_count = 0

    for x in all_base_stems:
        c_x = vocab[x]
        c_lx = vocab["l" + x]
        c_olx = vocab["ol" + x]
        c_qolx = vocab["qol" + x]
        slots_present = sum(1 for c in (c_x, c_lx, c_olx, c_qolx) if c > 0)
        if slots_present == 4:
            full_4tuple_count += 1
        if slots_present >= 3:
            at_least_3tuple_count += 1
        tot_family = c_x + c_lx + c_olx + c_qolx
        if slots_present >= 2 and (c_lx > 0):
            paradigm_rows.append({
                "base_X": x,
                "count_X": c_x,
                "l_X": "l" + x,
                "count_l_X": c_lx,
                "ol_X": "ol" + x,
                "count_ol_X": c_olx,
                "qol_X": "qol" + x,
                "count_qol_X": c_qolx,
                "slots_present": slots_present,
                "family_total": tot_family,
            })
    paradigm_rows.sort(key=lambda r: (-r["slots_present"], -r["count_l_X"], -r["family_total"]))

    # 3. Section Enrichment of `l-X` + `ol-X` + `qol-X` across Manuscript Sections
    sec_stats: Dict[str, Counter] = defaultdict(Counter)
    for sec, w in all_tokens:
        sec_stats[sec]["total"] += 1
        if is_l_cons(w):
            sec_stats[sec]["l_X"] += 1
        if is_ol_cons(w):
            sec_stats[sec]["ol_X"] += 1
        if is_qol_cons(w):
            sec_stats[sec]["qol_X"] += 1

    sec_summary = {}
    for sec, cnt in sorted(sec_stats.items()):
        tot = max(cnt["total"], 1)
        sec_summary[sec] = {
            "total_tokens": cnt["total"],
            "l_X_count": cnt["l_X"],
            "l_X_rate": round(cnt["l_X"] / tot, 4),
            "ol_X_count": cnt["ol_X"],
            "ol_X_rate": round(cnt["ol_X"] / tot, 4),
            "qol_X_count": cnt["qol_X"],
            "qol_X_rate": round(cnt["qol_X"] / tot, 4),
            "combined_liquid_applicative_rate": round((cnt["l_X"] + cnt["ol_X"] + cnt["qol_X"]) / tot, 4),
        }

    # Permutation test: enrichment of `l-X` in Balneological ($I=B) + Starred Recipes ($I=S) vs rest of corpus
    bs_secs = {"B", "S"}
    obs_bs_lx = sum(1 for sec, w in all_tokens if sec in bs_secs and is_l_cons(w))
    n_bs = sum(1 for sec, _ in all_tokens if sec in bs_secs)
    obs_bs_rate = obs_bs_lx / max(n_bs, 1)

    rng = random.Random(51)
    secs_only = [sec for sec, _ in all_tokens]
    is_lx_flags = [is_l_cons(w) for _, w in all_tokens]
    null_bs_rates = []
    for _ in range(1000):
        shuf_flags = is_lx_flags[:]
        rng.shuffle(shuf_flags)
        c = sum(1 for sec, fl in zip(secs_only, shuf_flags) if sec in bs_secs and fl)
        null_bs_rates.append(c / max(n_bs, 1))
    mu_bs = sum(null_bs_rates) / len(null_bs_rates)
    sd_bs = math.sqrt(sum((x - mu_bs) ** 2 for x in null_bs_rates) / len(null_bs_rates)) or 1e-9
    z_bs = (obs_bs_rate - mu_bs) / sd_bs

    pos_summary = {}
    for k, cnt in pos_counts.items():
        tot = max(sum(cnt.values()), 1)
        pos_summary[k] = {
            "total": sum(cnt.values()),
            "line_initial_rate": round(cnt["init"] / tot, 4),
            "line_interior_rate": round(cnt["mid"] / tot, 4),
            "line_final_rate": round(cnt["final"] / tot, 4),
        }

    result = {
        "summary": {
            "l_X_distinct_types": len(l_words),
            "l_X_total_tokens": l_token_total,
            "l_X_attested_bare_X_token_rate": round(l_attested_bare_tokens / max(l_token_total, 1), 4),
            "l_X_attested_bare_X_type_rate": round(l_attested_bare_types / max(len(l_words), 1), 4),
            "ol_X_total_tokens": sum(ol_words.values()),
            "qol_X_total_tokens": sum(qol_words.values()),
            "full_4tuple_families_count": full_4tuple_count,
            "at_least_3tuple_families_count": at_least_3tuple_count,
            "balneological_plus_recipes_l_X_rate": round(obs_bs_rate, 4),
            "null_mean_rate": round(mu_bs, 4),
            "z_score_balneological_recipes": round(z_bs, 2),
        },
        "positional_summary": pos_summary,
        "section_summary": sec_summary,
        "top_paradigm_families": paradigm_rows[:30],
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 51: THE l- / ol- / qol- LIQUID-APPLICATIVE DERIVATIVE SYSTEM ===")
    s = result["summary"]
    print(f"1. l-X tokens={s['l_X_total_tokens']} ({s['l_X_distinct_types']} types): {s['l_X_attested_bare_X_token_rate']*100:.2f}% of tokens have an independently attested bare word X!")
    print(f"   ol-X tokens={s['ol_X_total_tokens']} | qol-X tokens={s['qol_X_total_tokens']} | Full 4-tuple [X, l-X, ol-X, qol-X] families={s['full_4tuple_families_count']} (>=3 slots={s['at_least_3tuple_families_count']})")
    print(f"2. Balneological ($I=B) + Starred Recipes ($I=S) l-X enrichment: obs={s['balneological_plus_recipes_l_X_rate']*100:.2f}% vs null={s['null_mean_rate']*100:.2f}% (z={s['z_score_balneological_recipes']:+.2f})")
    print("3. Top 12 [X, l-X, ol-X, qol-X] 4-Tuple Families:")
    for r in paradigm_rows[:12]:
        print(f"   {r['base_X']:8s}: X={r['count_X']:4d} | {r['l_X']:9s}={r['count_l_X']:3d} | {r['ol_X']:10s}={r['count_ol_X']:3d} | {r['qol_X']:11s}={r['count_qol_X']:3d} (tot={r['family_total']:4d})")


if __name__ == "__main__":
    main()
