#!/usr/bin/env python3
"""
Attack 87 (Discovery 104): Full-Corpus Paragraph Typology & Intra-Folio Monograph
Progression (`P_1 -> P_mid -> P_last`) Across All Multi-Line Paragraphs

Tests:
1. Extracts all multi-line prose paragraphs (`n_lines >= 2`, `n_words >= 15`) across all `226` folios
   (`n = 720+` multi-line paragraphs, `32,500+` tokens).
2. Tests the **Intra-Folio Paragraph Progression Hypothesis (`P_first` Top Paragraph vs. `P_mid`
   Interior Paragraph vs. `P_last` Bottom Paragraph on folios with >= 2 paragraphs)**:
   - Stratified within `(Section $I, Currier Language $L)`, does a folio's paragraph sequence
     (`P_1 -> P_2 -> ... -> P_k`) progress systematically in:
     * Paragraph Length (`n_words`, `n_lines`)
     * Compound Botanical Cores (`cth/ckh/kch/tch`) vs. Simplex Verbal Cores (`k/t/ch/sh`)
     * Active Processing Prefix (`qo-`) & Applicative (`l-/ol-/qol-`) Density
     * Procedural `-edy/-dy` vs. Nominal/Liquid `-ol/-al/-or/-ar` & Colophon `-am/-m` Closure
     * Cross-Paragraph Anaphoric Stem Carryover (`does P_{i+1} inherit open-class stems from P_i on the same folio?` vs. stratified random folio pairs!)
3. Classifies every multi-line paragraph in the Voynich Manuscript into 5 structural Monograph/Recipe
   Archetypes and measures `I(Archetype_5 ; Section_8)` (`z`-score against 500 permutations):
   - `ARCH_1_BOTANICAL_TAXONOMIC_HEAD` (high `cth/ckh/kch/tch` compounds, `o-/ch-`, `-ol/-or/-y`)
   - `ARCH_2_AQUEOUS_BALNEOLOGICAL_PROCEDURE` (high `qo-` + `l-/ol-/qol-` applicative + `-edy/-dy`)
   - `ARCH_3_QUANTITATIVE_MEASURE_FORMULARY` (high `-aiin/-ain/-in` + `daiin/dar/dal` measures)
   - `ARCH_4_SHORT_STARRED_DECOCTION_RECIPE` (compact 3–8 line recipe with high `qo-/o-` + `-am/-y` closer)
   - `ARCH_5_COSMOLOGICAL_ASTRONOMICAL_SPEC` (high `T_CLASS` `t/te/ot-` + `-ar/-al/-or`)
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
OUT_JSON = DATA_DIR / "attack87_paragraph_typology_and_monograph_classifier.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def extract_open_stem(w: str):
    if not any(g in w for g in ("k", "t", "p", "f", "ch", "sh")):
        return None
    rem = w
    for p in ("qol", "dal", "ol", "al", "qo", "po", "fo", "o", "y", "s", "d", "l", "q"):
        if rem.startswith(p) and len(rem) > len(p) + 1 and any(g in rem[len(p):] for g in ("k", "t", "p", "f", "ch", "sh")):
            rem = rem[len(p):]
            break
    s_norm = rem.replace("cph", "cth").replace("cfh", "ckh").replace("p", "t").replace("f", "k")
    s_norm = re.sub(r"e+", "e", s_norm)
    s_norm = re.sub(r"i+", "i", s_norm)
    return s_norm


def para_features(lines: list) -> dict:
    words = [w for l in lines for w in l]
    n = max(len(words), 1)
    n_lines = len(lines)
    stems = {extract_open_stem(w) for w in words if extract_open_stem(w)}

    # Intra-paragraph line-to-line stem persistence
    seen_stems = set()
    persist_hits = 0
    for idx, l in enumerate(lines):
        l_stems = {extract_open_stem(w) for w in l if extract_open_stem(w)}
        if idx > 0 and (l_stems & seen_stems):
            persist_hits += 1
        seen_stems.update(l_stems)
    line_persist_rate = persist_hits / max(n_lines - 1, 1)

    w_first = lines[0][0] if lines and lines[0] else ""
    w_last = lines[-1][-1] if lines and lines[-1] else ""

    return {
        "n_lines": n_lines,
        "n_words": len(words),
        "stems": stems,
        "has_top_pf_opener": 1.0 if any(g in w_first[:3] for g in ("p", "f")) else 0.0,
        "has_am_colophon": 1.0 if w_last.endswith(("am", "om", "em", "im", "m")) else 0.0,
        "line_persist_rate": line_persist_rate,
        "qo_rate": sum(1 for w in words if w.startswith("q")) / n,
        "l_appl_rate": sum(1 for w in words if w.startswith(("l", "ol", "qol", "dal")) and len(w) > 3) / n,
        "compound_rate": sum(1 for w in words if any(c in w for c in ("cth", "ckh", "cph", "cfh", "kch", "tch", "pch", "fch"))) / n,
        "t_class_rate": sum(1 for w in words if any(g in w for g in ("t", "p"))) / n,
        "k_class_rate": sum(1 for w in words if any(g in w for g in ("k", "f"))) / n,
        "dy_rate": sum(1 for w in words if w.endswith("dy")) / n,
        "y_bare_rate": sum(1 for w in words if w.endswith("y") and not w.endswith("dy")) / n,
        "in_meas_rate": sum(1 for w in words if w.endswith(("aiin", "ain", "oiin", "in"))) / n,
        "liq_l_rate": sum(1 for w in words if w.endswith(("ol", "al"))) / n,
        "liq_r_rate": sum(1 for w in words if w.endswith(("or", "ar"))) / n,
    }


def classify_paragraph_archetype(pf: dict) -> str:
    # Rule-based structural archetype classifier using purely internal morphological densities
    if pf["qo_rate"] + pf["l_appl_rate"] >= 0.28 and pf["dy_rate"] >= 0.22:
        return "ARCH_2_AQUEOUS_BALNEOLOGICAL_PROCEDURE"
    if pf["compound_rate"] >= 0.12 and pf["dy_rate"] < 0.15:
        return "ARCH_1_BOTANICAL_TAXONOMIC_HEAD"
    if pf["in_meas_rate"] >= 0.16 and (pf["liq_l_rate"] + pf["liq_r_rate"]) >= 0.14:
        return "ARCH_3_QUANTITATIVE_MEASURE_FORMULARY"
    if pf["t_class_rate"] > pf["k_class_rate"] and (pf["liq_r_rate"] + pf["liq_l_rate"]) >= 0.15:
        return "ARCH_5_COSMOLOGICAL_ASTRONOMICAL_SPEC"
    if pf["n_lines"] <= 9 and pf["qo_rate"] >= 0.12 and (pf["dy_rate"] >= 0.14 or pf["has_am_colophon"] > 0):
        return "ARCH_4_SHORT_STARRED_DECOCTION_RECIPE"
    # Fallback by highest relative signature
    scores = [
        (pf["compound_rate"] * 2.5 + pf["y_bare_rate"], "ARCH_1_BOTANICAL_TAXONOMIC_HEAD"),
        (pf["qo_rate"] + pf["l_appl_rate"] * 2.0 + pf["dy_rate"], "ARCH_2_AQUEOUS_BALNEOLOGICAL_PROCEDURE"),
        (pf["in_meas_rate"] * 2.2 + pf["liq_l_rate"], "ARCH_3_QUANTITATIVE_MEASURE_FORMULARY"),
        (pf["qo_rate"] + pf["has_am_colophon"] * 0.15, "ARCH_4_SHORT_STARRED_DECOCTION_RECIPE"),
        (pf["t_class_rate"] * 2.0 + pf["liq_r_rate"] * 1.5, "ARCH_5_COSMOLOGICAL_ASTRONOMICAL_SPEC"),
    ]
    return max(scores, key=lambda kv: kv[0])[1]


def mutual_info(joint: Counter) -> float:
    total = sum(joint.values())
    if total == 0:
        return 0.0
    rx = Counter()
    cy = Counter()
    for (x, y), c in joint.items():
        rx[x] += c
        cy[y] += c
    mi = 0.0
    for (x, y), c in joint.items():
        if c > 0:
            mi += (c / total) * math.log2((c / total) / ((rx[x] / total) * (cy[y] / total)))
    return mi


def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def main():
    folio_paras = defaultdict(list)
    cur_meta = None
    cur_lines = []

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            if cur_lines and cur_meta:
                folio_paras[cur_meta["folio"]].append((cur_meta, list(cur_lines)))
                cur_lines = []
            fname = raw_s.split(">")[0][1:]
            tags = dict(re.findall(r"\$([A-Z])=([0-9A-Za-z]+)", raw_s))
            cur_meta = {
                "folio": fname,
                "Q": tags.get("Q", "U"),
                "I": tags.get("I", "U"),
                "L": tags.get("L", "U"),
                "H": tags.get("H", "U"),
            }
            continue
        m = LOCUS_RE.match(raw_s)
        if m and cur_meta is not None:
            ltype = m.group(3)
            raw_text = m.group(4)
            if ltype.startswith(("L", "R", "C", "S")):
                continue
            if "<%>" in raw_text and cur_lines:
                folio_paras[cur_meta["folio"]].append((cur_meta, list(cur_lines)))
                cur_lines = []
            toks = clean_tokens(raw_text)
            if toks:
                cur_lines.append(toks)
            if "<$>" in raw_text and cur_lines:
                folio_paras[cur_meta["folio"]].append((cur_meta, list(cur_lines)))
                cur_lines = []
    if cur_lines and cur_meta:
        folio_paras[cur_meta["folio"]].append((cur_meta, list(cur_lines)))

    all_paras = []
    zone_buckets = defaultdict(list)
    same_folio_adj_para_jacc = []
    same_folio_nonadj_para_jacc = []
    by_il_paras = defaultdict(list)

    for fname, p_list in folio_paras.items():
        # Filter to multi-line prose paragraphs (>= 2 lines, >= 12 words)
        valid_p = []
        for meta, lines in p_list:
            pf = para_features(lines)
            if pf["n_lines"] >= 2 and pf["n_words"] >= 12:
                pf["folio"] = fname
                pf["I"] = meta["I"]
                pf["L"] = meta["L"]
                pf["H"] = meta["H"]
                pf["archetype"] = classify_paragraph_archetype(pf)
                valid_p.append(pf)

        k = len(valid_p)
        for idx, pf in enumerate(valid_p):
            if k == 1:
                p_zone = "P_SINGLE"
            elif idx == 0:
                p_zone = "P_FIRST_TOP"
            elif idx == k - 1:
                p_zone = "P_LAST_BOT"
            else:
                p_zone = "P_MID_INT"
            pf["p_zone"] = p_zone
            all_paras.append(pf)
            if k >= 2:
                zone_buckets[p_zone].append(pf)
            by_il_paras[(pf["I"], pf["L"])].append(pf)

        if k >= 2:
            for i in range(k - 1):
                same_folio_adj_para_jacc.append(jaccard(valid_p[i]["stems"], valid_p[i + 1]["stems"]))
            for i in range(k):
                for j in range(i + 2, k):
                    same_folio_nonadj_para_jacc.append(jaccard(valid_p[i]["stems"], valid_p[j]["stems"]))

    # Stratified Null Baseline for Cross-Paragraph Anaphoric Stem Carryover on the same folio
    # Compare Same-Folio Consecutive Paragraphs (P_i -> P_{i+1}) vs Random Pairs in the exact same (I, L)
    rng = random.Random(87)
    diff_folio_same_il_jacc = []
    for (sec, lang), plist in by_il_paras.items():
        if len(plist) < 4:
            continue
        for _ in range(300):
            a, b = rng.sample(plist, 2)
            if a["folio"] != b["folio"]:
                diff_folio_same_il_jacc.append(jaccard(a["stems"], b["stems"]))

    obs_adj_jacc = sum(same_folio_adj_para_jacc) / len(same_folio_adj_para_jacc)
    null_il_jacc = sum(diff_folio_same_il_jacc) / len(diff_folio_same_il_jacc)

    # Permutation z-score for Same-Folio Adjacent Paragraph Stem Carryover within (I, L)
    null_means = []
    for _ in range(300):
        sim_vals = []
        for (sec, lang), plist in by_il_paras.items():
            if len(plist) < 2:
                continue
            shuffled = list(plist)
            rng.shuffle(shuffled)
            for i in range(0, min(len(shuffled) - 1, 40), 2):
                sim_vals.append(jaccard(shuffled[i]["stems"], shuffled[i + 1]["stems"]))
        null_means.append(sum(sim_vals) / len(sim_vals))
    nm = sum(null_means) / len(null_means)
    ns = math.sqrt(sum((x - nm) ** 2 for x in null_means) / len(null_means)) or 1e-9
    z_para_carryover = (obs_adj_jacc - nm) / ns

    # Summarize P_FIRST_TOP vs P_MID_INT vs P_LAST_BOT on multi-paragraph folios
    keys_to_avg = (
        "n_lines", "n_words", "has_top_pf_opener", "has_am_colophon", "line_persist_rate",
        "qo_rate", "l_appl_rate", "compound_rate", "t_class_rate", "k_class_rate",
        "dy_rate", "y_bare_rate", "in_meas_rate", "liq_l_rate", "liq_r_rate"
    )
    zone_summary = {}
    for pz in ("P_FIRST_TOP", "P_MID_INT", "P_LAST_BOT", "P_SINGLE"):
        plist = zone_buckets[pz] if pz != "P_SINGLE" else [p for p in all_paras if p["p_zone"] == "P_SINGLE"]
        if not plist:
            continue
        m = len(plist)
        row = {"n_paragraphs": m}
        for k in keys_to_avg:
            row[k] = round(sum(p[k] for p in plist) / m, 4)
        arch_c = Counter(p["archetype"] for p in plist)
        row["top_archetypes"] = {a: round(100.0 * c / m, 1) for a, c in arch_c.most_common(3)}
        zone_summary[pz] = row

    # Archetype x Section Contingency Table and Permutation MI Test
    joint_arch_sec = Counter((p["archetype"], p["I"]) for p in all_paras)
    obs_mi = mutual_info(joint_arch_sec)
    sec_list = [p["I"] for p in all_paras]
    arch_list = [p["archetype"] for p in all_paras]
    null_mis = []
    for _ in range(500):
        sh_s = list(sec_list)
        rng.shuffle(sh_s)
        null_mis.append(mutual_info(Counter(zip(arch_list, sh_s))))
    mi_mean = sum(null_mis) / len(null_mis)
    mi_std = math.sqrt(sum((x - mi_mean) ** 2 for x in null_mis) / len(null_mis)) or 1e-9
    z_arch_sec = (obs_mi - mi_mean) / mi_std

    arch_summary = []
    for arch_name, cnt in Counter(arch_list).most_common():
        sub = [p for p in all_paras if p["archetype"] == arch_name]
        sec_c = Counter(p["I"] for p in sub)
        pzone_c = Counter(p["p_zone"] for p in sub)
        arch_summary.append({
            "archetype": arch_name,
            "n_paragraphs": cnt,
            "pct_of_paragraphs": round(100.0 * cnt / len(all_paras), 2),
            "mean_words": round(sum(p["n_words"] for p in sub) / cnt, 1),
            "mean_lines": round(sum(p["n_lines"] for p in sub) / cnt, 2),
            "mean_qo_rate": round(sum(p["qo_rate"] for p in sub) / cnt, 4),
            "mean_l_appl_rate": round(sum(p["l_appl_rate"] for p in sub) / cnt, 4),
            "mean_compound_rate": round(sum(p["compound_rate"] for p in sub) / cnt, 4),
            "mean_dy_rate": round(sum(p["dy_rate"] for p in sub) / cnt, 4),
            "mean_in_meas_rate": round(sum(p["in_meas_rate"] for p in sub) / cnt, 4),
            "am_colophon_pct": round(100.0 * sum(p["has_am_colophon"] for p in sub) / cnt, 1),
            "section_distribution": dict(sec_c.most_common()),
            "page_zone_distribution": dict(pzone_c.most_common()),
        })

    out = {
        "corpus_paragraph_summary": {
            "total_multiline_paragraphs": len(all_paras),
            "total_paragraph_tokens": sum(p["n_words"] for p in all_paras),
            "mean_intra_paragraph_line_persist_rate": round(
                sum(p["line_persist_rate"] for p in all_paras) / len(all_paras), 4
            ),
            "same_folio_consecutive_para_stem_jacc": round(obs_adj_jacc, 4),
            "same_folio_nonconsecutive_para_stem_jacc": round(
                sum(same_folio_nonadj_para_jacc) / max(len(same_folio_nonadj_para_jacc), 1), 4
            ),
            "diff_folio_same_IL_para_stem_jacc": round(null_il_jacc, 4),
            "z_score_same_folio_para_carryover": round(z_para_carryover, 2),
            "archetype_section_mi_bits": round(obs_mi, 4),
            "null_archetype_section_mi_bits": round(mi_mean, 4),
            "z_score_archetype_section_mi": round(z_arch_sec, 2),
        },
        "intra_folio_paragraph_progression": zone_summary,
        "paragraph_archetypes": arch_summary,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Corpus Paragraph Summary:", out["corpus_paragraph_summary"])
    print("Intra-Folio Paragraph Progression:")
    for pz, row in zone_summary.items():
        print(
            f"  {pz:12s} (n={row['n_paragraphs']:3d}): words={row['n_words']:5.1f}, "
            f"topPF={row['has_top_pf_opener']:.3f}, amCol={row['has_am_colophon']:.3f}, "
            f"qo={row['qo_rate']:.4f}, l_appl={row['l_appl_rate']:.4f}, "
            f"cmp={row['compound_rate']:.4f}, dy={row['dy_rate']:.4f}, in={row['in_meas_rate']:.4f}"
        )
    print("Paragraph Archetypes:")
    for a in arch_summary:
        print(f"  {a['archetype']}: n={a['n_paragraphs']} ({a['pct_of_paragraphs']}%) secs={a['section_distribution']}")


if __name__ == "__main__":
    main()
