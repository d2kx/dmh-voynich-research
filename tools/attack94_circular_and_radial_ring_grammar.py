#!/usr/bin/env python3
"""
Attack 94 (Discovery 111): Complete Circular (`@C`) & Radial (`@R`) Ring Grammar
(`n = 2,497` Tokens on `f57v, f67r–f73v, f85v2, f86v4, fRos`) — Continuous Circular
Prose Rings vs. Discrete Radial Sector Lists, Ring-Internal `<->` Sector Closers (`-am/-m`),
and Clockwise Paradigm Cadence

Tests:
1. Extracts all `@C` (Circular Ring) and `@R` (Radial Spoke/Sector) loci from `data/ZL3b-n.txt`
   and stratifies them into:
   - `SHORT_RADIAL_SPOKES` (1..3 words per locus, e.g., radial star/nymph sector labels),
   - `MEDIUM_RING_ARCS` (4..9 words per locus, e.g., broken ring arcs separated by `<->`),
   - `LONG_CONTINUOUS_RINGS` (>= 10 words per locus, e.g., 360-degree outer/inner rings).
2. Tests the `o-` vs. `qo-` Gradient across Ring Length:
   - Do Short Radial Spokes behave like `@L` Figure Labels (`o-` dominant, `qo-` ~ 0%),
     while Long Continuous Rings re-activate `qo-` and `da-` clause linkers?
3. Tests the **Marginless Circular `-am/-m` Sector-Boundary Law**:
   - On a 360-degree circular ring with no physical right page margin, where do `-am/-m`
     terminator tokens occur?
   - Tests enrichment of `-am/-m` at **Ring/Spoke Termini (final word of `@C/@R` locus or
     immediately preceding an internal `<->` spoke intrusion)** vs. ring-interior tokens
     (1,000-trial permutation test).
4. Tests **Clockwise Adjacent-Token Core & Minim Cadence**:
   - Measures adjacent-token edit similarity (`EditDist(w_t, w_{t+1}) <= 2`) and shared-core
     persistence on `@C/@R` rings vs. linear `@P` prose and shuffled ring order.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack94_circular_and_radial_ring_grammar.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

PREFIXES = ("qok", "qot", "qop", "qof", "qol", "qo", "po", "fo", "so", "do", "yo", "lo", "ro",
            "ol", "al", "or", "ar", "da", "sa", "yk", "yt", "ok", "ot", "op", "of", "ch", "sh",
            "q", "o", "y", "s", "d", "l", "r", "")
SUFFIXES = ("aiin", "oiin", "eiin", "ain", "oin", "ein", "iin", "in",
            "edy", "ody", "ady", "eey", "ey", "dy", "hy", "ky", "ty", "py", "fy", "ly", "ry", "sy", "y",
            "eol", "eal", "ol", "al", "el", "il", "ul",
            "eor", "ear", "or", "ar", "er", "ir",
            "am", "om", "em", "im", "m", "n", "s", "d", "l", "r", "o", "a", "")


def parse_tokens_with_boundaries(raw: str):
    """
    Returns list of dicts: {'word': w, 'before_gap_or_end': bool, 'after_start_or_gap': bool}
    where gaps include `<->` drawing/spoke intrusions and `<$>` explicit terminators.
    """
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    # Replace `<->` and `<$>` with special token `__GAP__`
    s = s.replace("<->", " . __GAP__ . ").replace("<$>", " . __END__ . ").replace("<%>", " . __START__ . ")
    s = re.sub(r"<[^>]*>", " ", s)
    raw_parts = [p.strip() for p in s.replace(".", " ").split() if p.strip()]
    words = []
    for idx, p in enumerate(raw_parts):
        if p in ("__GAP__", "__END__", "__START__"):
            continue
        w = re.sub(r"[^a-zA-Z]", "", p).lower()
        if not w:
            continue
        # Check if next non-empty part in raw_parts is __GAP__ or __END__ or end of list
        next_part = raw_parts[idx + 1] if idx + 1 < len(raw_parts) else "__END__"
        prev_part = raw_parts[idx - 1] if idx - 1 >= 0 else "__START__"
        words.append({
            "word": w,
            "before_gap_or_end": next_part in ("__GAP__", "__END__"),
            "before_internal_gap": next_part == "__GAP__" and idx + 1 < len(raw_parts) - 1,
            "after_start_or_gap": prev_part in ("__START__", "__GAP__"),
        })
    if words:
        words[-1]["before_gap_or_end"] = True
        words[-1]["is_locus_final"] = True
        for d in words[:-1]:
            d["is_locus_final"] = False
    return words


def edit_distance_le2(w1: str, w2: str) -> int:
    if abs(len(w1) - len(w2)) > 2:
        return 3
    dp = list(range(len(w2) + 1))
    for i, c1 in enumerate(w1, 1):
        new_dp = [i]
        for j, c2 in enumerate(w2, 1):
            cost = 0 if c1 == c2 else 1
            new_dp.append(min(new_dp[-1] + 1, dp[j] + 1, dp[j - 1] + cost))
        dp = new_dp
        if min(dp) > 2:
            return 3
    return dp[-1]


def get_onset_class(w: str) -> str:
    if w.startswith("qo"):
        return "QO_ACTIVE"
    if w.startswith(("ok", "ot", "op", "of", "ol", "or", "o")):
        return "O_NOMINAL"
    if w.startswith(("da", "d")):
        return "DA_D_LINKER"
    if w.startswith(("ch", "sh")):
        return "CH_SH_BENCH"
    if w.startswith(("y", "s")):
        return "Y_S_INIT"
    return "OTHER"


def is_am_closer(w: str) -> bool:
    return w.endswith(("am", "om", "em", "im", "m", "ag", "og", "eg")) and len(w) >= 2


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}
    cr_loci = []
    prose_loci = []

    for raw_line in raw_lines:
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        mf = FOLIO_META_RE.match(raw_s)
        if mf:
            cur_folio = "f" + mf.group(1)
            meta_str = mf.group(2)
            cur_meta = {}
            for kv in meta_str.split():
                if "=" in kv:
                    k, v = kv.lstrip("$").split("=", 1)
                    cur_meta[k] = v
            continue
        ml = LOCUS_RE.match(raw_s)
        if ml and cur_folio:
            lnum, ltype, text = ml.group(2), ml.group(3), ml.group(4)
            toks = parse_tokens_with_boundaries(text)
            if not toks:
                continue
            ltype_clean = ltype.lstrip("@+*=")
            rec = {
                "folio": cur_folio,
                "loc": f"{cur_folio}.{lnum}",
                "ltype": ltype,
                "ltype_clean": ltype_clean,
                "section": cur_meta.get("I", "U"),
                "lang": cur_meta.get("L", "U"),
                "tokens": toks,
                "n_words": len(toks),
            }
            if ltype_clean.startswith(("C", "R")):
                cr_loci.append(rec)
            elif ltype_clean.startswith("P"):
                prose_loci.append(rec)

    # 1. Stratify @C and @R into Short Spokes (1..3), Medium Arcs (4..9), Long Continuous Rings (>=10)
    strata = {
        "SHORT_RADIAL_SPOKES_1_TO_3": [],
        "MEDIUM_RING_ARCS_4_TO_9": [],
        "LONG_CONTINUOUS_RINGS_GE_10": [],
    }
    by_code = {"C_CIRCULAR": [], "R_RADIAL": []}

    for rec in cr_loci:
        n = rec["n_words"]
        if n <= 3:
            strata["SHORT_RADIAL_SPOKES_1_TO_3"].append(rec)
        elif n <= 9:
            strata["MEDIUM_RING_ARCS_4_TO_9"].append(rec)
        else:
            strata["LONG_CONTINUOUS_RINGS_GE_10"].append(rec)
        if rec["ltype_clean"].startswith("C"):
            by_code["C_CIRCULAR"].append(rec)
        else:
            by_code["R_RADIAL"].append(rec)

    def summarize_group(recs):
        n_loci = len(recs)
        all_toks = [t for r in recs for t in r["tokens"]]
        n_toks = len(all_toks)
        if n_toks == 0:
            return {}
        onsets = Counter(get_onset_class(t["word"]) for t in all_toks)
        am_count = sum(1 for t in all_toks if is_am_closer(t["word"]))
        dy_count = sum(1 for t in all_toks if t["word"].endswith("dy"))
        aiin_count = sum(1 for t in all_toks if t["word"].endswith(("aiin", "ain", "iin")))
        return {
            "n_loci": n_loci,
            "n_tokens": n_toks,
            "o_nominal_pct": round(100.0 * onsets["O_NOMINAL"] / n_toks, 2),
            "qo_active_pct": round(100.0 * onsets["QO_ACTIVE"] / n_toks, 2),
            "da_linker_pct": round(100.0 * onsets["DA_D_LINKER"] / n_toks, 2),
            "ch_sh_bench_pct": round(100.0 * onsets["CH_SH_BENCH"] / n_toks, 2),
            "am_closer_pct": round(100.0 * am_count / n_toks, 2),
            "dy_suffix_pct": round(100.0 * dy_count / n_toks, 2),
            "aiin_suffix_pct": round(100.0 * aiin_count / n_toks, 2),
        }

    strata_summary = {k: summarize_group(v) for k, v in strata.items()}
    code_summary = {k: summarize_group(v) for k, v in by_code.items()}
    prose_summary = summarize_group(prose_loci)

    # 2. Test the Marginless Circular `-am/-m` Sector-Boundary Law on Medium + Long Rings (len >= 4)
    multi_word_rings = [r for r in cr_loci if r["n_words"] >= 4]
    ring_tokens = [t for r in multi_word_rings for t in r["tokens"]]
    boundary_tokens = [t for t in ring_tokens if t["before_gap_or_end"]]
    interior_tokens = [t for t in ring_tokens if not t["before_gap_or_end"]]

    am_at_boundary = sum(1 for t in boundary_tokens if is_am_closer(t["word"]))
    am_at_interior = sum(1 for t in interior_tokens if is_am_closer(t["word"]))
    rate_boundary = am_at_boundary / len(boundary_tokens) if boundary_tokens else 0.0
    rate_interior = am_at_interior / len(interior_tokens) if interior_tokens else 0.0
    lift_boundary = rate_boundary / (rate_interior or 1e-9)

    # Also check specifically internal `<->` spoke gaps inside `@C/@R` lines!
    internal_gap_tokens = [t for t in ring_tokens if t["before_internal_gap"]]
    locus_final_tokens = [t for t in ring_tokens if t["is_locus_final"]]
    am_at_internal_gap = sum(1 for t in internal_gap_tokens if is_am_closer(t["word"]))
    am_at_locus_final = sum(1 for t in locus_final_tokens if is_am_closer(t["word"]))

    # Permutation test: shuffle word order within each `@C/@R` locus (len >= 4) 1,000 times
    rng = random.Random(94)
    null_boundary_counts = []
    for _ in range(1000):
        c = 0
        for r in multi_word_rings:
            words_list = [t["word"] for t in r["tokens"]]
            rng.shuffle(words_list)
            for idx, d in enumerate(r["tokens"]):
                if d["before_gap_or_end"] and is_am_closer(words_list[idx]):
                    c += 1
        null_boundary_counts.append(c)

    null_mean = sum(null_boundary_counts) / len(null_boundary_counts)
    null_std = math.sqrt(sum((x - null_mean) ** 2 for x in null_boundary_counts) / len(null_boundary_counts)) or 1e-9
    z_am_boundary = (am_at_boundary - null_mean) / null_std

    # Collect concrete examples of `-am/-m` at ring/spoke boundaries
    am_boundary_examples = []
    for r in multi_word_rings:
        for idx, t in enumerate(r["tokens"]):
            if t["before_gap_or_end"] and is_am_closer(t["word"]):
                prev_w = r["tokens"][idx - 1]["word"] if idx > 0 else "<START>"
                next_w = r["tokens"][idx + 1]["word"] if idx + 1 < len(r["tokens"]) else "<END>"
                am_boundary_examples.append({
                    "loc": r["loc"],
                    "ltype": r["ltype"],
                    "word": t["word"],
                    "position": "INTERNAL_SPOKE_GAP_<->" if t["before_internal_gap"] else "RING_LOCUS_FINAL",
                    "context": f"{prev_w} . [{t['word']}] . {next_w}",
                })

    # 3. Clockwise Adjacent-Token Edit Similarity (`EditDist <= 2`) & Wrap-Around Closure (`w_last -> w_first`)
    adj_pairs_ring = 0
    adj_sim_ring = 0
    wrap_pairs_ring = 0
    wrap_sim_ring = 0
    adj_sim_examples = []

    for r in multi_word_rings:
        ws = [t["word"] for t in r["tokens"] if len(t["word"]) >= 2]
        for i in range(len(ws) - 1):
            adj_pairs_ring += 1
            if edit_distance_le2(ws[i], ws[i + 1]) <= 2:
                adj_sim_ring += 1
                if len(adj_sim_examples) < 15 and ws[i] != ws[i + 1]:
                    adj_sim_examples.append({
                        "loc": r["loc"],
                        "pair": f"{ws[i]} -> {ws[i + 1]}",
                        "edit_dist": edit_distance_le2(ws[i], ws[i + 1]),
                    })
        if r["ltype_clean"].startswith("C") and len(ws) >= 10:
            wrap_pairs_ring += 1
            if edit_distance_le2(ws[-1], ws[0]) <= 2 or get_onset_class(ws[-1]) == get_onset_class(ws[0]):
                wrap_sim_ring += 1

    obs_adj_sim_rate = adj_sim_ring / adj_pairs_ring if adj_pairs_ring else 0.0

    # Compare against within-ring shuffled adjacent similarity (1,000 trials)
    null_adj_rates = []
    for _ in range(1000):
        sim_c = 0
        for r in multi_word_rings:
            ws = [t["word"] for t in r["tokens"] if len(t["word"]) >= 2]
            rng.shuffle(ws)
            for i in range(len(ws) - 1):
                if edit_distance_le2(ws[i], ws[i + 1]) <= 2:
                    sim_c += 1
        null_adj_rates.append(sim_c / adj_pairs_ring)

    null_adj_mean = sum(null_adj_rates) / len(null_adj_rates)
    null_adj_std = math.sqrt(sum((x - null_adj_mean) ** 2 for x in null_adj_rates) / len(null_adj_rates)) or 1e-9
    z_adj_sim = (obs_adj_sim_rate - null_adj_mean) / null_adj_std

    # Also compute linear @P prose adjacent edit similarity for comparison
    prose_adj_pairs = 0
    prose_adj_sim = 0
    for r in prose_loci:
        ws = [t["word"] for t in r["tokens"] if len(t["word"]) >= 2]
        for i in range(len(ws) - 1):
            prose_adj_pairs += 1
            if edit_distance_le2(ws[i], ws[i + 1]) <= 2:
                prose_adj_sim += 1
    prose_adj_sim_rate = prose_adj_sim / prose_adj_pairs if prose_adj_pairs else 0.0

    # Top Longest Continuous Rings in the Manuscript
    top_rings = sorted(cr_loci, key=lambda x: -x["n_words"])[:15]
    top_rings_table = []
    for r in top_rings:
        s = summarize_group([r])
        top_rings_table.append({
            "loc": r["loc"],
            "ltype": r["ltype"],
            "section": r["section"],
            "n_words": r["n_words"],
            "o_nominal_pct": s["o_nominal_pct"],
            "qo_active_pct": s["qo_active_pct"],
            "da_linker_pct": s["da_linker_pct"],
            "am_closer_pct": s["am_closer_pct"],
            "opening_3_words": " . ".join(t["word"] for t in r["tokens"][:3]),
            "closing_3_words": " . ".join(t["word"] for t in r["tokens"][-3:]),
        })

    out = {
        "corpus_overview": {
            "total_cr_loci": len(cr_loci),
            "total_cr_tokens": sum(r["n_words"] for r in cr_loci),
            "by_code": code_summary,
            "by_ring_length_stratum": strata_summary,
            "linear_prose_baseline": prose_summary,
        },
        "marginless_ring_am_boundary_law": {
            "multi_word_ring_loci": len(multi_word_rings),
            "total_tokens": len(ring_tokens),
            "boundary_positions_end_or_spoke_gap": len(boundary_tokens),
            "interior_positions": len(interior_tokens),
            "am_at_boundary": am_at_boundary,
            "am_at_boundary_rate": round(rate_boundary, 4),
            "am_at_interior": am_at_interior,
            "am_at_interior_rate": round(rate_interior, 4),
            "boundary_vs_interior_lift": round(lift_boundary, 2),
            "am_at_locus_final": am_at_locus_final,
            "locus_final_total": len(locus_final_tokens),
            "am_at_internal_spoke_gap": am_at_internal_gap,
            "internal_spoke_gap_total": len(internal_gap_tokens),
            "null_mean_boundary_hits": round(null_mean, 2),
            "null_std": round(null_std, 2),
            "z_score": round(z_am_boundary, 2),
            "examples": am_boundary_examples[:15],
        },
        "clockwise_adjacent_cadence": {
            "ring_adjacent_pairs": adj_pairs_ring,
            "ring_adjacent_edit_le2_count": adj_sim_ring,
            "ring_adjacent_edit_le2_rate": round(obs_adj_sim_rate, 4),
            "within_ring_shuffled_null_rate": round(null_adj_mean, 4),
            "within_ring_shuffled_z": round(z_adj_sim, 2),
            "linear_prose_adjacent_edit_le2_rate": round(prose_adj_sim_rate, 4),
            "ring_vs_prose_cadence_ratio": round(obs_adj_sim_rate / (prose_adj_sim_rate or 1e-9), 2),
            "examples": adj_sim_examples,
        },
        "top_15_longest_continuous_rings": top_rings_table,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Strata Summary:", json.dumps(strata_summary, indent=2))
    print("Marginless Ring -am/-m Boundary Law:", json.dumps({k: v for k, v in out["marginless_ring_am_boundary_law"].items() if k != "examples"}, indent=2))
    print("Clockwise Adjacent Cadence:", json.dumps({k: v for k, v in out["clockwise_adjacent_cadence"].items() if k != "examples"}, indent=2))


if __name__ == "__main__":
    main()
