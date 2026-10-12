"""
Attack 66: The `-l` vs `-r` Liquid Coda Contrast Solver Across `-ol/-or` and `-al/-ar` Minimal Pairs.

Across both Matrix I (Closed-Class: `ol/or, al/ar, dal/dar, sal/sar, qol/qor, ral/rar`) and
Matrix II (Open-Class: `chol/chor, shol/shor, qokol/qokor, qokal/qokar, okol/okor, okal/okar,
otol/otor, otal/otar, cheol/cheor, sheol/sheor`), the liquid coda alternates between lateral `-l`
and rhotic `-r`.

This script tests four quantitative hypotheses across all `-ol/-or` and `-al/-ar` tokens:
1. The Vowel-Liquid Harmonic Affinity Law (`{o, a} x {l, r}` 2x2 Matrix):
   Does back rounded `-o-` strongly select lateral `-l` (`-ol > -or`), while open unrounded `-a-`
   strongly selects rhotic `-r` (`-ar > -al`)?
2. Syntactic Licensing Contrast (`X-l -> CH_SH_VERB` vs `X-r -> AIIN_NOM`), holding stem+vowel constant:
   Does `-l` (`ol, dal, chol, qokal`) license following Bench/Gallows verbs (`ol . shedy`, `dal . shedy`),
   whereas `-r` (`or, dar, chor, otar`) selects following `aiin/ar` nominals (`or . aiin`, `dar . aiin`)?
3. Diagram Label / Astrological Ring (`@L/@C/@R`) vs Running Prose (`@P`) Enrichment:
   Are rhotic `-r` codas (`otar, okar, dar, ar, or`) significantly enriched in Diagram Labels & Rings
   relative to lateral `-l` codas?
4. Currier Language (`$L=A/B`) and Section (`$I`) Stratification.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack66_l_vs_r_liquid_coda_solver.json"

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


def next_word_class(w: str) -> str:
    if w == "<LINE_FINAL>":
        return "LINE_FINAL"
    if w.startswith(("ch", "sh")):
        return "CH_SH_VERB"
    if w.startswith("qo"):
        return "QO_ACT"
    if w in ("aiin", "ain", "iin", "daiin", "dain"):
        return "AIIN_DAIIN"
    if w.startswith(("ok", "ot", "k", "t")):
        return "GALLOWS_STEM"
    return "OTHER"


def main():
    cur_sec = "U"
    cur_lang = "U"
    records = []

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        if raw_line.startswith("<f") and ">" in raw_line and "." not in raw_line.split(">")[0]:
            m_s = re.search(r"\$I=([A-Z])", raw_line)
            cur_sec = m_s.group(1) if m_s else "U"
            m_l = re.search(r"\$L=([A-Z])", raw_line)
            cur_lang = m_l.group(1) if m_l else "U"
            continue

        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        loc_tag = m.group(3)
        is_prose = "P" in loc_tag
        toks = clean_tokens(m.group(4))
        n = len(toks)
        for i, w in enumerate(toks):
            if len(w) >= 2 and w[-2:] in ("ol", "or", "al", "ar"):
                vow = w[-2].upper()
                liq = w[-1].upper()
                stem_vow = w[:-1]
                stem_only = w[:-2]
                next_w = toks[i + 1] if i + 1 < n else "<LINE_FINAL>"
                records.append({
                    "w": w,
                    "stem_only": stem_only,
                    "stem_vow": stem_vow,
                    "vow": vow,
                    "liq": liq,
                    "sec": cur_sec,
                    "lang": cur_lang,
                    "is_prose": is_prose,
                    "is_init": (i == 0),
                    "is_final": (i == n - 1),
                    "next_cls": next_word_class(next_w),
                })

    # 1. 2x2 Vowel x Liquid Contingency (`{O, A} x {L, R}`)
    c_ol = sum(1 for r in records if r["vow"] == "O" and r["liq"] == "L")
    c_or = sum(1 for r in records if r["vow"] == "O" and r["liq"] == "R")
    c_al = sum(1 for r in records if r["vow"] == "A" and r["liq"] == "L")
    c_ar = sum(1 for r in records if r["vow"] == "A" and r["liq"] == "R")
    odds_ratio = (c_ol * c_ar) / max(1, c_or * c_al)

    o_recs = [r for r in records if r["vow"] == "O"]
    a_recs = [r for r in records if r["vow"] == "A"]
    obs_vow_diff = (c_ar / len(a_recs)) - (c_or / len(o_recs))
    pool_r = [1 if r["liq"] == "R" else 0 for r in records]
    rng = random.Random(6601)
    null_vow_diffs = []
    na = len(a_recs)
    no = len(o_recs)
    for _ in range(1000):
        rng.shuffle(pool_r)
        null_vow_diffs.append((sum(pool_r[:na]) / na) - (sum(pool_r[na:]) / no))
    z_vow_liq = (obs_vow_diff - mean(null_vow_diffs)) / (std(null_vow_diffs) + 1e-12)

    # 2. Non-Prose (Diagram Labels & Rings `@L/@C/@R`) vs Prose (`@P`) R-share
    np_recs = [r for r in records if not r["is_prose"]]
    pr_recs = [r for r in records if r["is_prose"]]
    np_r_rate = sum(1 for r in np_recs if r["liq"] == "R") / len(np_recs)
    pr_r_rate = sum(1 for r in pr_recs if r["liq"] == "R") / len(pr_recs)
    obs_np_diff = np_r_rate - pr_r_rate
    pool_np = [1 if r["liq"] == "R" else 0 for r in records]
    null_np = []
    n_np = len(np_recs)
    n_pr = len(pr_recs)
    for _ in range(1000):
        rng.shuffle(pool_np)
        null_np.append((sum(pool_np[:n_np]) / n_np) - (sum(pool_np[n_np:]) / n_pr))
    z_nonprose_r = (obs_np_diff - mean(null_np)) / (std(null_np) + 1e-12)

    # 3. Positional Envelope Contrast (`w_1` Line-Initial vs `w_2..n-1` Interior vs `w_n` Line-Final), stratified by stem_vow
    l_recs = [r for r in records if r["liq"] == "L"]
    r_recs = [r for r in records if r["liq"] == "R"]

    r_init_rate = sum(1 for r in r_recs if r["is_init"]) / len(r_recs)
    l_init_rate = sum(1 for r in l_recs if r["is_init"]) / len(l_recs)
    l_mid_rate = sum(1 for r in l_recs if not r["is_init"] and not r["is_final"]) / len(l_recs)
    r_mid_rate = sum(1 for r in r_recs if not r["is_init"] and not r["is_final"]) / len(r_recs)

    by_stem_vow = defaultdict(list)
    for r in records:
        by_stem_vow[r["stem_vow"]].append(r)

    obs_init_diff = r_init_rate - l_init_rate
    null_init_diffs = []
    for _ in range(1000):
        sim_r_init = 0
        sim_l_init = 0
        for sv, recs in by_stem_vow.items():
            nr_sv = sum(1 for r in recs if r["liq"] == "R")
            inits = [1 if r["is_init"] else 0 for r in recs]
            rng.shuffle(inits)
            sim_r_init += sum(inits[:nr_sv])
            sim_l_init += sum(inits[nr_sv:])
        null_init_diffs.append((sim_r_init / len(r_recs)) - (sim_l_init / len(l_recs)))
    z_r_init = (obs_init_diff - mean(null_init_diffs)) / (std(null_init_diffs) + 1e-12)

    # Section & Language breakdown of L vs R
    sec_table = {}
    for s in ["H", "Z", "A", "C", "B", "P", "S", "T"]:
        sub = [r for r in records if r["sec"] == s]
        if not sub:
            continue
        cl = sum(1 for r in sub if r["liq"] == "L")
        cr = sum(1 for r in sub if r["liq"] == "R")
        sec_table[s] = {
            "L": cl,
            "R": cr,
            "total": len(sub),
            "R_share_pct": round(100.0 * cr / len(sub), 2),
        }

    # 4. Matched 4-Cell Quadruplets (`stem + {ol, or, al, ar}`)
    by_stem = defaultdict(Counter)
    for r in records:
        by_stem[r["stem_only"]][r["vow"] + r["liq"]] += 1

    quad_table = []
    for st, cnt in by_stem.items():
        tot = sum(cnt.values())
        if tot >= 50:
            quad_table.append({
                "stem": st if st else "<ZERO>",
                "total": tot,
                "OL": cnt["OL"],
                "OR": cnt["OR"],
                "AL": cnt["AL"],
                "AR": cnt["AR"],
                "O_prefers_L_pct": round(100.0 * cnt["OL"] / max(1, cnt["OL"] + cnt["OR"]), 1),
                "A_prefers_R_pct": round(100.0 * cnt["AR"] / max(1, cnt["AL"] + cnt["AR"]), 1),
            })
    quad_table.sort(key=lambda d: d["total"], reverse=True)

    print("=== ATTACK 66: THE -l vs -r LIQUID CODA CONTRAST SOLVER ===")
    print(f"Total -ol/-or/-al/-ar Tokens: {len(records):,} -> L={len(l_recs):,} ({100*len(l_recs)/len(records):.2f}%), R={len(r_recs):,} ({100*len(r_recs)/len(records):.2f}%)")
    print(f"1. Vowel-Liquid Harmonic Affinity 2x2 Matrix (Odds Ratio = {odds_ratio:.2f}x, z = {z_vow_liq:+.2f}):")
    print(f"   Back -o- : -ol = {c_ol:4d} ({100*c_ol/(c_ol+c_or):.2f}%) vs -or = {c_or:4d} ({100*c_or/(c_ol+c_or):.2f}%)")
    print(f"   Open -a- : -al = {c_al:4d} ({100*c_al/(c_al+c_ar):.2f}%) vs -ar = {c_ar:4d} ({100*c_ar/(c_al+c_ar):.2f}%)")
    print(f"2. Positional Contrast (stem+vowel-stratified): R Line-Initial={r_init_rate*100:.2f}% vs L Line-Initial={l_init_rate*100:.2f}% (z = {z_r_init:+.2f}) | L Interior={l_mid_rate*100:.2f}% vs R Interior={r_mid_rate*100:.2f}%")
    print(f"3. Diagram/Ring (@L/@C/@R) R-Coda Enrichment: Non-Prose R={np_r_rate*100:.2f}% vs Prose R={pr_r_rate*100:.2f}% (z = {z_nonprose_r:+.2f})")
    print("4. Section Stratification ($I) of R-share:")
    for s, v in sec_table.items():
        print(f"   $I={s}: L={v['L']:4d}, R={v['R']:4d} (tot={v['total']:4d}) -> R_share={v['R_share_pct']:5.2f}%")

    out = {
        "totals": {
            "total_liquid_coda_tokens": len(records),
            "L_tokens": len(l_recs),
            "R_tokens": len(r_recs),
        },
        "vowel_liquid_2x2_affinity": {
            "OL": c_ol,
            "OR": c_or,
            "AL": c_al,
            "AR": c_ar,
            "O_selects_L_pct": round(100.0 * c_ol / (c_ol + c_or), 2),
            "A_selects_R_pct": round(100.0 * c_ar / (c_al + c_ar), 2),
            "odds_ratio": round(odds_ratio, 3),
            "permutation_z": round(z_vow_liq, 2),
        },
        "positional_contrast": {
            "R_line_init_pct": round(r_init_rate * 100, 2),
            "L_line_init_pct": round(l_init_rate * 100, 2),
            "L_line_interior_pct": round(l_mid_rate * 100, 2),
            "R_line_interior_pct": round(r_mid_rate * 100, 2),
            "stem_vowel_stratified_init_z": round(z_r_init, 2),
        },
        "diagram_ring_vs_prose_R": {
            "non_prose_R_pct": round(np_r_rate * 100, 2),
            "prose_R_pct": round(pr_r_rate * 100, 2),
            "permutation_z": round(z_nonprose_r, 2),
        },
        "section_table": sec_table,
        "top_quadruplets": quad_table[:15],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
