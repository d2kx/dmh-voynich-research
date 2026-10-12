"""
Attack 58: The `ch-` vs `sh-` Plume Contrast Solver.

Building on Attack 57 (which established the 8x6x8 Open-Class Gallows/Bench Matrix),
the simplex Bench core splits into:
  - `ch-` (unplumed bench, 6,053 tokens across all prefixes/stems)
  - `sh-` (`s`-plumed bench, 3,261 tokens across all prefixes/stems)

Wait: in EVA paleography, `sh` is literally `ch` surmounted by an `s`-like plume!
Earlier in Attack 53 (Discovery 70), we proved that simplex `s-` (`saiin, sar, sal, sor, sol`)
is the Continuation Line-Initial Sibilant Series (42.73% line-initial vs 17.62% for `d-`).
Does the `s`-plume on `sh-` encode a systematic grammatical/phonological contrast with `ch-`?

This script tests four rigorous hypotheses across all `ch-` and `sh-` words:
1. Prefix Compatibility (`Prefix x [CH vs SH]`): How do the 8 prefixes (`ZERO, O-, QO-, L-, D-, S-, Y-, R-`)
   select between `ch` and `sh`?
2. Vocalic `-e-` / `-ee-` Grading (`0-e` vs `1-e` vs `2-ee` stems): Does `sh-` strongly select
   vocalic `-e-` / `-ee-` stems (`shedy, shey, sheey, sheedy`) while avoiding bare `0-e` stems
   (`chol, chor, char, chal, chdy, chaiin`)?
3. Sibilant-Plume Line-Initial Homology: Just as `s-` > `d-` at line-initial `w_1`, is `sh-`
   significantly enriched at line-initial `w_1` relative to `ch-` (especially on bare `0-e` stems
   `shor, shol, shar, shaiin, shdy`)?
4. Currier Language A vs B & Section Stratification (`$L=A/B` and `$I=H/P/Z/B/C/S`).
"""

import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "attack58_ch_vs_sh_plume_contrast_solver.json"


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))



def load_lines():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        idx = json.load(f)["folios"]
    lines = []
    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith("#") or not raw.startswith("<f"):
                continue
            parts = raw.split(">", 1)
            if len(parts) < 2:
                continue
            loc = parts[0][1:]
            txt = parts[1].strip()
            folio = loc.split(".")[0]
            fmeta = idx.get(folio, {})
            lang = fmeta.get("language", "U")
            sec = fmeta.get("section", "U")
            is_para = "<%>" in txt
            clean = txt.replace("<%>", "").replace("<$>", "").replace("<->", " . ")
            import re
            clean = re.sub(r"\{[^}]*\}", "", clean)
            clean = re.sub(r"\[([^\]:]+):[^\]]+\]", r"\1", clean)
            clean = re.sub(r"[@!&*?<>]", "", clean)
            words = [w.strip() for w in clean.replace(",", ".").split(".") if w.strip()]
            if words:
                lines.append({
                    "loc": loc,
                    "folio": folio,
                    "lang": lang,
                    "sec": sec,
                    "is_para": is_para,
                    "is_prose": "@P" in loc or "+P" in loc,
                    "words": words,
                })
    return lines


def parse_ch_sh_prefix(w: str):
    """If w contains a simplex ch or sh core (not kch/tch/pch/fch/ckh/cth/cph/cfh), return (prefix, core, stem)."""
    for g in ("kch", "tch", "pch", "fch", "ckh", "cth", "cph", "cfh"):
        if g in w:
            return None
    for core in ("ch", "sh"):
        pos = w.find(core)
        if pos != -1:
            pre = w[:pos]
            stem = w[pos + 2:]
            if pre == "":
                p_cat = "ZERO"
            elif pre.startswith("qo"):
                p_cat = "QO"
            elif pre.startswith("ol") or pre.startswith("qol") or pre.startswith("l"):
                p_cat = "L_APPL"
            elif pre.startswith("o"):
                p_cat = "O_VOW"
            elif pre.startswith("d"):
                p_cat = "D_DEIC"
            elif pre.startswith("s"):
                p_cat = "S_SIB"
            elif pre.startswith("y"):
                p_cat = "Y_CONJ"
            elif pre.startswith("r") or pre.startswith("ar") or pre.startswith("al"):
                p_cat = "R_PORT"
            else:
                p_cat = "OTHER"
            return (p_cat, core.upper(), stem)
    return None


def main():
    lines = load_lines()
    matched_stems = [
        "edy", "ey", "eey", "eedy", "dy", "y",
        "ol", "or", "al", "ar",
        "eo", "eol", "eor", "eody", "aiin"
    ]

    # 1. Prefix x [CH vs SH] contingency
    prefix_counts = defaultdict(lambda: Counter())
    e_grade_counts = defaultdict(lambda: Counter())
    e_grade_init = defaultdict(lambda: defaultdict(list))

    pair_stats = {s: {"ch": [], "sh": []} for s in matched_stems}
    all_ch_sh_records = []

    for ln in lines:
        words = ln["words"]
        n = len(words)
        for i, w in enumerate(words):
            parsed = parse_ch_sh_prefix(w)
            if parsed:
                p_cat, core, stem = parsed
                prefix_counts[p_cat][core] += 1
                if p_cat == "ZERO":
                    if stem.startswith("ee"):
                        egrade = "2_EE"
                    elif stem.startswith("e"):
                        egrade = "1_E"
                    else:
                        egrade = "0_NO_E"
                    e_grade_counts[egrade][core] += 1
                    e_grade_init[egrade][core].append(1 if i == 0 else 0)

            for s in matched_stems:
                if w == "ch" + s or w == "sh" + s:
                    core = w[:2]
                    prev_w = words[i - 1] if i > 0 else "<LINE_INIT>"
                    next_w = words[i + 1] if i + 1 < n else "<LINE_FINAL>"
                    rec = {
                        "stem": s,
                        "core": core,
                        "folio": ln["folio"],
                        "lang": ln["lang"],
                        "sec": ln["sec"],
                        "is_para_line1": ln["is_para"] and i == 0,
                        "is_line_init": i == 0,
                        "is_line_final": i == n - 1,
                        "rel_pos": i / (n - 1) if n > 1 else 0.5,
                        "prev_w": prev_w,
                        "next_w": next_w,
                    }
                    pair_stats[s][core].append(rec)
                    all_ch_sh_records.append(rec)

    # Compute Prefix x Core stats
    prefix_summary = {}
    for p_cat in ["ZERO", "O_VOW", "QO", "L_APPL", "D_DEIC", "S_SIB", "Y_CONJ", "R_PORT", "OTHER"]:
        c_ch = prefix_counts[p_cat]["CH"]
        c_sh = prefix_counts[p_cat]["SH"]
        tot = c_ch + c_sh
        if tot > 0:
            prefix_summary[p_cat] = {
                "CH": c_ch,
                "SH": c_sh,
                "total": tot,
                "SH_share_pct": round(100.0 * c_sh / tot, 2),
            }

    # Compute E-grade stats (0_NO_E vs 1_E vs 2_EE)
    egrade_summary = {}
    for eg in ["0_NO_E", "1_E", "2_EE"]:
        c_ch = e_grade_counts[eg]["CH"]
        c_sh = e_grade_counts[eg]["SH"]
        tot = c_ch + c_sh
        init_ch = mean(e_grade_init[eg]["CH"]) * 100.0 if e_grade_init[eg]["CH"] else 0.0
        init_sh = mean(e_grade_init[eg]["SH"]) * 100.0 if e_grade_init[eg]["SH"] else 0.0
        egrade_summary[eg] = {
            "CH": c_ch,
            "SH": c_sh,
            "total": tot,
            "SH_share_pct": round(100.0 * c_sh / tot, 2) if tot else 0.0,
            "CH_line_init_pct": round(float(init_ch), 2),
            "SH_line_init_pct": round(float(init_sh), 2),
            "SH_over_CH_init_lift": round(float(init_sh / init_ch), 2) if init_ch > 0 else None,
        }

    # Permutation test 1: SH share across E-grade (2_EE + 1_E vs 0_NO_E)
    e_plus_sh = e_grade_counts["1_E"]["SH"] + e_grade_counts["2_EE"]["SH"]
    e_plus_tot = (
        e_grade_counts["1_E"]["CH"] + e_grade_counts["1_E"]["SH"]
        + e_grade_counts["2_EE"]["CH"] + e_grade_counts["2_EE"]["SH"]
    )
    e_zero_sh = e_grade_counts["0_NO_E"]["SH"]
    e_zero_tot = e_grade_counts["0_NO_E"]["CH"] + e_grade_counts["0_NO_E"]["SH"]
    obs_e_diff = (e_plus_sh / e_plus_tot) - (e_zero_sh / e_zero_tot)
    pool_e = [1] * (e_plus_sh + e_zero_sh) + [0] * ((e_plus_tot + e_zero_tot) - (e_plus_sh + e_zero_sh))
    rng = random.Random(5801)
    null_e_diffs = []
    for _ in range(1000):
        rng.shuffle(pool_e)
        s1 = sum(pool_e[:e_plus_tot]) / e_plus_tot
        s0 = sum(pool_e[e_plus_tot:]) / e_zero_tot
        null_e_diffs.append(s1 - s0)
    z_egrade = (obs_e_diff - mean(null_e_diffs)) / (std(null_e_diffs) + 1e-12)

    # Permutation test 2: Suffix-stratified Line-Initial Rate (SH vs CH) across 15 matched pairs
    ch_recs = [r for r in all_ch_sh_records if r["core"] == "ch"]
    sh_recs = [r for r in all_ch_sh_records if r["core"] == "sh"]
    ch_init_rate = sum(1 for r in ch_recs if r["is_line_init"]) / len(ch_recs)
    sh_init_rate = sum(1 for r in sh_recs if r["is_line_init"]) / len(sh_recs)
    obs_init_diff = sh_init_rate - ch_init_rate

    by_stem = defaultdict(list)
    for r in all_ch_sh_records:
        by_stem[r["stem"]].append(r)

    null_diffs = []
    for _ in range(1000):
        sim_ch_init = 0
        sim_sh_init = 0
        for s, recs in by_stem.items():
            n_sh = sum(1 for r in recs if r["core"] == "sh")
            inits = [1 if r["is_line_init"] else 0 for r in recs]
            rng.shuffle(inits)
            sim_sh_init += sum(inits[:n_sh])
            sim_ch_init += sum(inits[n_sh:])
        null_diffs.append((sim_sh_init / len(sh_recs)) - (sim_ch_init / len(ch_recs)))

    null_mean = mean(null_diffs)
    null_std = std(null_diffs) or 1e-9
    z_init = (obs_init_diff - null_mean) / null_std

    # Detailed per-stem table
    stem_table = []
    for s in matched_stems:
        c_list = pair_stats[s]["ch"]
        s_list = pair_stats[s]["sh"]
        n_c = len(c_list)
        n_s = len(s_list)
        tot = n_c + n_s
        c_init = sum(1 for r in c_list if r["is_line_init"]) / n_c if n_c else 0
        s_init = sum(1 for r in s_list if r["is_line_init"]) / n_s if n_s else 0
        c_b = sum(1 for r in c_list if r["lang"] == "B") / n_c if n_c else 0
        s_b = sum(1 for r in s_list if r["lang"] == "B") / n_s if n_s else 0
        stem_table.append({
            "stem": s,
            "ch_word": "ch" + s,
            "sh_word": "sh" + s,
            "ch_count": n_c,
            "sh_count": n_s,
            "sh_share_pct": round(100.0 * n_s / tot, 2) if tot else 0,
            "ch_line_init_pct": round(100.0 * c_init, 2),
            "sh_line_init_pct": round(100.0 * s_init, 2),
            "ch_langB_pct": round(100.0 * c_b, 2),
            "sh_langB_pct": round(100.0 * s_b, 2),
        })

    print("=== ATTACK 58: THE ch- vs sh- PLUME CONTRAST SOLVER ===")
    print("1. Prefix Compatibility (Prefix x [CH vs SH]):")
    for k, v in prefix_summary.items():
        print(f"   {k:8s}: CH={v['CH']:4d}, SH={v['SH']:4d} (total={v['total']:4d}) -> SH_share={v['SH_share_pct']:5.2f}%")
    print("\n2. Vocalic -e-/-ee- Stem Grading (ZERO-prefix CH vs SH):")
    for eg, v in egrade_summary.items():
        print(
            f"   {eg:8s}: CH={v['CH']:4d}, SH={v['SH']:4d} -> SH_share={v['SH_share_pct']:5.2f}% "
            f"| Line-Init: CH={v['CH_line_init_pct']:5.2f}% vs SH={v['SH_line_init_pct']:5.2f}% (lift={v['SH_over_CH_init_lift']}x)"
        )
    print(f"   -> Vocalic -e-/-ee- Enrichment in SH vs 0-e: z = {z_egrade:+.2f}")
    print(
        f"\n3. Line-Initial Rate across 15 Matched Pairs: SH={sh_init_rate*100:.2f}% (n={len(sh_recs)}) "
        f"vs CH={ch_init_rate*100:.2f}% (n={len(ch_recs)}) -> {sh_init_rate/ch_init_rate:.2f}x lift (suffix-stratified z={z_init:+.2f})"
    )

    out = {
        "prefix_compatibility": prefix_summary,
        "vocalic_e_grading": egrade_summary,
        "vocalic_e_enrichment_z": round(z_egrade, 2),
        "overall_matched_pairs": {
            "ch_tokens": len(ch_recs),
            "sh_tokens": len(sh_recs),
            "ch_line_init_pct": round(ch_init_rate * 100, 2),
            "sh_line_init_pct": round(sh_init_rate * 100, 2),
            "sh_over_ch_line_init_lift": round(sh_init_rate / ch_init_rate, 2),
            "line_init_suffix_stratified_z": round(z_init, 2),
        },
        "stem_table": stem_table,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Saved -> {OUT_PATH}")


if __name__ == "__main__":
    main()
