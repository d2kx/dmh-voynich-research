"""
Attack 67: Double-Core & Internal-Infix Compound Architecture Solver (`[Prefix + Core_1 + Infix/Core_2 + Coda]`).

In Attack 62 (Discovery 79), adding the Secondary Radical Skeleton (Level 5) raised explained
word entropy from 88.34% to 97.28% (+0.9625 bits).
What are the exact structural rules governing multi-core and infixed words in the Voynich Manuscript?

This script analyzes all extended/compound open-class tokens (words containing a secondary consonant
between the primary Core_1 and the terminal Coda) and tests four productive compound patterns:
  1. Pattern A (`LIQUID_INFIX_DENOMINAL`: `Core_1 + [ol/or/al/ar] + [dy/y/aiin]`, e.g. `choldy, okoldy, otoldy, qokoldy, chordy, otardy`)
     -> Double-suffixed denominal verbs/participles (`[Stem-ol] + -dy`)!
  2. Pattern B (`BENCH_TO_PEDESTAL`: `[ch/sh] + (e/o) + [ckh/cth/cph/cfh] + Coda`, e.g. `chckhy, chcthy, shckhy, checkhy, checthy`)
     vs reverse `PEDESTAL_TO_BENCH` (`[ckh/cth] + ... + [ch/sh]`). Tests 100% directional asymmetry!
  3. Pattern C (`BENCH_O_GALLOWS`: `[ch/sh] + [o/e] + [k/t] + Coda`, e.g. `choky, choty, shoky, shoty, chokaiin, chotaiin, chekar`)
     vs `GALLOWS_E_BENCH` (`[k/t/p/f] + [e/o] + [ch/sh] + Coda`, e.g. `kechedy, techedy, kchody, pchody`).
     Tests the Linking-Vowel Asymmetry Law (`ch + o + k/t` vs `k/t + (e) + ch`)!
  4. Pattern D (`DENTAL_INFIX`: `Core_1 + [o/eo/e] + d + [aiin/ar/al/or/ol]`, e.g. `chedaiin, shedaiin, qokedaiin, qokedy/qokedar, pchedar`).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack67_double_core_and_infix_compound_solver.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def classify_compound(w: str):
    """
    Identify if `w` is an extended/compound word with two cores or an internal consonant infix
    between the primary core and the coda.
    """
    # Pattern B1: Bench + (vowel) + Pedestal Gallows (`chckh, chcth, shckh, shcth, checkh, checth...`)
    m_b1 = re.search(r"(ch|sh)([aeio]*)(ckh|cth|cph|cfh)", w)
    if m_b1:
        return ("B_BENCH_TO_PEDESTAL", m_b1.group(1), m_b1.group(2), m_b1.group(3))

    # Pattern B2 (reverse check): Pedestal Gallows + (vowel) + Bench
    m_b2 = re.search(r"(ckh|cth|cph|cfh)([aeio]*)(ch|sh)", w)
    if m_b2:
        return ("B_REV_PEDESTAL_TO_BENCH", m_b2.group(1), m_b2.group(2), m_b2.group(3))

    # Pattern C1: Bench + vowel + Simplex Gallows (`chok, chot, shok, shot, chek, chet, shek, shet`)
    m_c1 = re.search(r"(ch|sh)([aeio]+)(k|t|p|f)(?!h)", w)
    if m_c1:
        return ("C1_BENCH_VOW_GALLOWS", m_c1.group(1), m_c1.group(2), m_c1.group(3))

    # Pattern C2: Simplex Gallows + vowel + Bench (`kech, tech, koch, toch, pech, fech`)
    m_c2 = re.search(r"(?<![cs])(k|t|p|f)([aeio]+)(ch|sh)", w)
    if m_c2:
        return ("C2_GALLOWS_VOW_BENCH", m_c2.group(1), m_c2.group(2), m_c2.group(3))

    # Pattern A: Core + Liquid (`ol/or/al/ar/l/r`) + Suffix (`dy/y/aiin/ain/in/am`)
    m_a = re.search(r"(kch|tch|pch|fch|ckh|cth|cph|cfh|ch|sh|k|t|p|f)([aeio]*[lr])(dy|y|aiin|ain|iin|in|am|om)", w)
    if m_a:
        return ("A_LIQUID_INFIX_DENOMINAL", m_a.group(1), m_a.group(2), m_a.group(3))

    # Pattern D: Core + Vowel + `d` + Non-y Suffix (`daiin, dar, dal, dor, dol, dam`, e.g. `chedaiin, shedaiin, pchedar, qokedar`)
    m_d = re.search(r"(kch|tch|pch|fch|ckh|cth|cph|cfh|ch|sh|k|t|p|f)([aeio]*d)(aiin|ain|iin|in|ar|al|or|ol|am|om)", w)
    if m_d:
        return ("D_DENTAL_INFIX_COMPOUND", m_d.group(1), m_d.group(2), m_d.group(3))

    # Pattern E: Double Gallows or Double Bench (`k...k`, `t...t`, `ch...ch`)
    m_e = re.search(r"(ch|sh|k|t|p|f)([aeio]+)(ch|sh|k|t|p|f)", w)
    if m_e:
        return ("E_REDUPLICATED_CORE", m_e.group(1), m_e.group(2), m_e.group(3))

    return None


def main():
    cat_counts = Counter()
    cat_words = defaultdict(Counter)
    c1_vow_counts = Counter()
    c2_vow_counts = Counter()

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        for w in clean_tokens(m.group(4)):
            res = classify_compound(w)
            if res:
                cat, c1, mid, c2 = res
                cat_counts[cat] += 1
                cat_words[cat][w] += 1
                if cat == "C1_BENCH_VOW_GALLOWS":
                    c1_vow_counts["O_VOW" if "o" in mid else "E_A_VOW"] += 1
                elif cat == "C2_GALLOWS_VOW_BENCH":
                    c2_vow_counts["O_VOW" if "o" in mid else "E_A_VOW"] += 1

    total_compounds = sum(cat_counts.values())

    # Test 1: Directional Asymmetry of Bench + Pedestal (`B_BENCH_TO_PEDESTAL` vs `B_REV_PEDESTAL_TO_BENCH`)
    n_b1 = cat_counts["B_BENCH_TO_PEDESTAL"]
    n_b2 = cat_counts["B_REV_PEDESTAL_TO_BENCH"]
    b_asym_pct = 100.0 * n_b1 / max(1, n_b1 + n_b2)

    # Test 2: Linking-Vowel Polarity Law (`Bench + V + Gallows` selects `-o-` [`chok/chot/shok/shot`]
    # whereas `Gallows + V + Bench` selects `-e-` [`kech/tech`])
    c1_tot = sum(c1_vow_counts.values())
    c2_tot = sum(c2_vow_counts.values())
    c1_o_rate = c1_vow_counts["O_VOW"] / max(1, c1_tot)
    c2_o_rate = c2_vow_counts["O_VOW"] / max(1, c2_tot)
    obs_vdiff = c1_o_rate - c2_o_rate

    pool_v = [1] * (c1_vow_counts["O_VOW"] + c2_vow_counts["O_VOW"]) + [0] * (c1_vow_counts["E_A_VOW"] + c2_vow_counts["E_A_VOW"])
    rng = random.Random(6701)
    null_v = []
    for _ in range(1000):
        rng.shuffle(pool_v)
        null_v.append((sum(pool_v[:c1_tot]) / c1_tot) - (sum(pool_v[c1_tot:]) / c2_tot))
    z_link_vow = (obs_vdiff - mean(null_v)) / (std(null_v) + 1e-12)

    summary_rows = []
    for cat in [
        "C1_BENCH_VOW_GALLOWS",
        "A_LIQUID_INFIX_DENOMINAL",
        "D_DENTAL_INFIX_COMPOUND",
        "B_BENCH_TO_PEDESTAL",
        "C2_GALLOWS_VOW_BENCH",
        "E_REDUPLICATED_CORE",
        "B_REV_PEDESTAL_TO_BENCH",
    ]:
        cnt = cat_counts[cat]
        summary_rows.append({
            "category": cat,
            "tokens": cnt,
            "share_pct": round(100.0 * cnt / max(1, total_compounds), 2),
            "unique_types": len(cat_words[cat]),
            "top_8_words": dict(cat_words[cat].most_common(8)),
        })

    print("=== ATTACK 67: DOUBLE-CORE & INTERNAL-INFIX COMPOUND ARCHITECTURE SOLVER ===")
    print(f"Total Multi-Core / Infixed Compound Tokens Identified: {total_compounds:,}\n")
    for r in summary_rows:
        print(f"  {r['category']:28s}: {r['tokens']:4d} tokens ({r['share_pct']:5.2f}%), {r['unique_types']:3d} types | Top: {list(r['top_8_words'].items())[:5]}")
    print(f"\n1. Bench->Pedestal Directional Asymmetry: ch/sh + ckh/cth = {n_b1} vs ckh/cth + ch/sh = {n_b2} ({b_asym_pct:.2f}% unidirectional!)")
    print(
        f"2. Linking-Vowel Polarity Law: Bench+V+Gallows uses -o- in {100*c1_o_rate:.2f}% (n={c1_tot}, e.g. choky/choty/shoky) "
        f"vs Gallows+V+Bench uses -o- in {100*c2_o_rate:.2f}% (n={c2_tot}, {100*(1-c2_o_rate):.2f}% -e-, e.g. kechedy/techedy) -> z = {z_link_vow:+.2f}"
    )

    out = {
        "total_compound_tokens": total_compounds,
        "bench_to_pedestal_asymmetry": {
            "bench_then_pedestal": n_b1,
            "pedestal_then_bench": n_b2,
            "unidirectional_pct": round(b_asym_pct, 2),
        },
        "linking_vowel_polarity": {
            "bench_vow_gallows_total": c1_tot,
            "bench_vow_gallows_O_pct": round(100.0 * c1_o_rate, 2),
            "gallows_vow_bench_total": c2_tot,
            "gallows_vow_bench_O_pct": round(100.0 * c2_o_rate, 2),
            "gallows_vow_bench_E_pct": round(100.0 * (1.0 - c2_o_rate), 2),
            "permutation_z": round(z_link_vow, 2),
        },
        "compound_categories": summary_rows,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
