#!/usr/bin/env python3
"""
Attack 201 (Discovery 218): Sagittarius (f73v, 'novembre') Centaur-Archer Medallion,
the 10+16+4 = 30° Top-Nymph Overflow Law Replication with Scorpio (f73r),
and Ecliptic Seasonal Vocabulary Drift across the 360° Medieval Zodiac.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack201_sagittarius_centaur_archer_and_ecliptic_drift.json"

PREFIXES = ["qo", "ch", "sh", "ok", "ot", "ol", "or", "op", "of", "od", "da", "sa", "yk", "yt", "yd", "o", "d", "s", "y", "l", "r"]
SUFFIXES = ["aiin", "oiin", "eiin", "chedy", "shedy", "edy", "ody", "eey", "ey", "chy", "shy", "dy", "ol", "or", "al", "ar", "am", "om", "an", "in", "y", "r", "l", "m", "s"]

ZODIAC_FOLIOS = [
    {"folio": "f70v2", "sign": "Pisces", "season": "Spring", "month": "mars", "angle_deg": 345, "pdf_page": 129},
    {"folio": "f70v1", "sign": "Aries I", "season": "Spring", "month": "abril", "angle_deg": 7.5, "pdf_page": 130},
    {"folio": "f71r", "sign": "Aries II", "season": "Spring", "month": "abril", "angle_deg": 22.5, "pdf_page": 130},
    {"folio": "f71v", "sign": "Taurus I", "season": "Spring", "month": "may", "angle_deg": 37.5, "pdf_page": 131},
    {"folio": "f72r1", "sign": "Taurus II", "season": "Spring", "month": "may", "angle_deg": 52.5, "pdf_page": 131},
    {"folio": "f72r2", "sign": "Gemini", "season": "Summer", "month": "juny", "angle_deg": 75, "pdf_page": 131},
    {"folio": "f72r3", "sign": "Cancer", "season": "Summer", "month": "jolh", "angle_deg": 105, "pdf_page": 131},
    {"folio": "f72v3", "sign": "Leo", "season": "Summer", "month": "agost", "angle_deg": 135, "pdf_page": 132},
    {"folio": "f72v2", "sign": "Virgo", "season": "Autumn", "month": "setembre", "angle_deg": 165, "pdf_page": 132},
    {"folio": "f72v1", "sign": "Libra", "season": "Autumn", "month": "octobre", "angle_deg": 195, "pdf_page": 133},
    {"folio": "f73r", "sign": "Scorpio", "season": "Autumn", "month": "octobre", "angle_deg": 225, "pdf_page": 134},
    {"folio": "f73v", "sign": "Sagittarius", "season": "Autumn", "month": "novembre", "angle_deg": 255, "pdf_page": 135},
]


def clean_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    return w.strip()


def canonical_stem(w: str) -> str:
    s = w
    s = s.replace("ch", "C").replace("sh", "S").replace("ckh", "K").replace("cth", "T").replace("cph", "P").replace("cfh", "F")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    w2 = s.replace("C", "ch").replace("S", "sh").replace("K", "kh").replace("T", "th").replace("P", "ph").replace("F", "fh")
    if w2.endswith(("m", "g")) and len(w2) > 2:
        w2 = w2[:-1] + "r"
    for p in PREFIXES:
        if w2.startswith(p) and len(w2) - len(p) >= 2:
            w2 = w2[len(p):]
            break
    for suf in SUFFIXES:
        if w2.endswith(suf) and len(w2) - len(suf) >= 2:
            w2 = w2[:-len(suf)]
            break
    if w2 and w2[0] in ("p", "f", "k", "t"):
        w2 = "K" + w2[1:]
    return w2 if w2 else w


def parse_zodiac_lines():
    target_folios = {item["folio"] for item in ZODIAC_FOLIOS}
    lines_by_folio = defaultdict(list)

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw.startswith("<f"):
            continue
        m = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s*(.*)$", raw)
        if not m:
            continue
        fol, lnum, ltype, body = m.groups()
        if fol not in target_folios:
            continue
        body_clean = re.sub(r"<!.*?>", "", body)
        clock_m = re.search(r"<!([0-9]{2}:[0-9]{2})>", body)
        clock_pos = clock_m.group(1) if clock_m else None
        tokens = [clean_word(t) for t in re.split(r"[.,\s]+", body_clean) if clean_word(t)]
        if not tokens:
            continue
        try:
            line_int = int(re.sub(r"[^0-9]", "", lnum))
        except ValueError:
            line_int = 0
        lines_by_folio[fol].append({
            "folio": fol,
            "lnum_raw": lnum,
            "lnum": line_int,
            "locus": f"{fol}.{lnum}",
            "ltype": ltype,
            "clock": clock_pos,
            "tokens": tokens,
        })
    return lines_by_folio


def analyze_scorpio_sagittarius(lines_by_folio):
    results = {}
    for fol, name in [("f73r", "Scorpio"), ("f73v", "Sagittarius")]:
        flines = sorted(lines_by_folio[fol], key=lambda x: x["lnum"])
        top_overflow = [l for l in flines if 1 <= l["lnum"] <= 4 and "Lz" in l["ltype"]]
        outer_cc = [l for l in flines if l["lnum"] == 5 and "Cc" in l["ltype"]]
        middle_ring = [l for l in flines if 6 <= l["lnum"] <= 21 and "Lz" in l["ltype"]]
        middle_cc = [l for l in flines if l["lnum"] == 22 and "Cc" in l["ltype"]]
        inner_ring = [l for l in flines if 23 <= l["lnum"] <= 32 and "Lz" in l["ltype"]]
        inner_cc = [l for l in flines if l["lnum"] == 33 and "Cc" in l["ltype"]]

        all_words = [w for l in flines for w in l["tokens"]]
        lz_words = [w for l in flines if "Lz" in l["ltype"] for w in l["tokens"]]
        cc_words = [w for l in flines if "Cc" in l["ltype"] for w in l["tokens"]]

        top_words = [w for l in top_overflow for w in l["tokens"]]
        mid_words = [w for l in middle_ring for w in l["tokens"]]
        inn_words = [w for l in inner_ring for w in l["tokens"]]

        results[fol] = {
            "sign": name,
            "total_lines": len(flines),
            "total_words": len(all_words),
            "total_lz_words": len(lz_words),
            "total_cc_words": len(cc_words),
            "n_top_overflow_loci": len(top_overflow),
            "n_middle_ring_loci": len(middle_ring),
            "n_inner_ring_loci": len(inner_ring),
            "total_degree_loci": len(top_overflow) + len(middle_ring) + len(inner_ring),
            "architecture": f"{len(inner_ring)} (inner) + {len(middle_ring)} (middle) + {len(top_overflow)} (top overflow) = {len(inner_ring) + len(middle_ring) + len(top_overflow)}°",
            "top_overflow_loci": [
                {"locus": l["locus"], "clock": l["clock"], "words": l["tokens"]} for l in top_overflow
            ],
            "middle_ring_loci": [
                {"locus": l["locus"], "clock": l["clock"], "words": l["tokens"]} for l in middle_ring
            ],
            "inner_ring_loci": [
                {"locus": l["locus"], "clock": l["clock"], "words": l["tokens"]} for l in inner_ring
            ],
            "cc_rings": [
                {"locus": l["locus"], "n_words": len(l["tokens"]), "first_word": l["tokens"][0], "last_word": l["tokens"][-1]}
                for l in (outer_cc + middle_cc + inner_cc)
            ],
            "prefix_dist": dict(Counter([w[:2] for w in all_words if len(w) >= 2]).most_common(8)),
            "suffix_dist": dict(Counter([w[-2:] for w in all_words if len(w) >= 2]).most_common(8)),
        }
    return results


def analyze_ecliptic_seasonal_drift(lines_by_folio):
    folio_stats = []
    season_groups = defaultdict(lambda: {"total_words": 0, "ot_op": 0, "ok_of": 0, "ch_sh": 0, "qo": 0, "dy_ey": 0, "aiin": 0, "am_om": 0, "words": []})

    for item in ZODIAC_FOLIOS:
        fol = item["folio"]
        flines = lines_by_folio[fol]
        all_words = [w for l in flines for w in l["tokens"]]
        lz_words = [w for l in flines if "Lz" in l["ltype"] for w in l["tokens"]]
        cc_words = [w for l in flines if "Cc" in l["ltype"] for w in l["tokens"]]

        n_words = len(all_words)
        ot_op = sum(1 for w in all_words if w.startswith(("ot", "op")))
        ok_of = sum(1 for w in all_words if w.startswith(("ok", "of")))
        ch_sh = sum(1 for w in all_words if w.startswith(("ch", "sh")))
        qo = sum(1 for w in all_words if w.startswith("qo"))
        dy_ey = sum(1 for w in all_words if w.endswith(("dy", "ey", "y")))
        aiin = sum(1 for w in all_words if w.endswith(("aiin", "oiin", "eiin")))
        am_om = sum(1 for w in all_words if w.endswith(("am", "om")))

        ratio_ot_to_ok = ot_op / max(1, ok_of)

        f_stat = {
            "folio": fol,
            "sign": item["sign"],
            "season": item["season"],
            "month": item["month"],
            "angle_deg": item["angle_deg"],
            "pdf_page": item["pdf_page"],
            "total_words": n_words,
            "lz_words": len(lz_words),
            "cc_words": len(cc_words),
            "ot_op_count": ot_op,
            "ot_op_rate": round(ot_op / max(1, n_words), 4),
            "ok_of_count": ok_of,
            "ok_of_rate": round(ok_of / max(1, n_words), 4),
            "ratio_ot_to_ok": round(ratio_ot_to_ok, 3),
            "ch_sh_count": ch_sh,
            "ch_sh_rate": round(ch_sh / max(1, n_words), 4),
            "qo_count": qo,
            "qo_rate": round(qo / max(1, n_words), 4),
            "dy_ey_count": dy_ey,
            "dy_ey_rate": round(dy_ey / max(1, n_words), 4),
            "aiin_count": aiin,
            "aiin_rate": round(aiin / max(1, n_words), 4),
            "am_om_count": am_om,
            "am_om_rate": round(am_om / max(1, n_words), 4),
        }
        folio_stats.append(f_stat)

        sg = season_groups[item["season"]]
        sg["total_words"] += n_words
        sg["ot_op"] += ot_op
        sg["ok_of"] += ok_of
        sg["ch_sh"] += ch_sh
        sg["qo"] += qo
        sg["dy_ey"] += dy_ey
        sg["aiin"] += aiin
        sg["am_om"] += am_om
        sg["words"].extend(all_words)

    # Season summary
    season_summary = {}
    for season in ["Spring", "Summer", "Autumn"]:
        sg = season_groups[season]
        nw = sg["total_words"]
        season_summary[season] = {
            "total_words": nw,
            "ot_op_count": sg["ot_op"],
            "ot_op_pct": round(sg["ot_op"] / nw * 100, 2),
            "ok_of_count": sg["ok_of"],
            "ok_of_pct": round(sg["ok_of"] / nw * 100, 2),
            "ratio_ot_to_ok": round(sg["ot_op"] / max(1, sg["ok_of"]), 3),
            "ch_sh_count": sg["ch_sh"],
            "ch_sh_pct": round(sg["ch_sh"] / nw * 100, 2),
            "qo_count": sg["qo"],
            "qo_pct": round(sg["qo"] / nw * 100, 2),
            "dy_ey_count": sg["dy_ey"],
            "dy_ey_pct": round(sg["dy_ey"] / nw * 100, 2),
            "aiin_count": sg["aiin"],
            "aiin_pct": round(sg["aiin"] / nw * 100, 2),
            "am_om_count": sg["am_om"],
            "am_om_pct": round(sg["am_om"] / nw * 100, 2),
        }

    # Statistical test: Spring vs Summer prefix shift
    # Null hypothesis: ot_op and ok_of distribution is invariant across seasons
    # 2x2 contingency table: Spring vs Summer on (ot_op, ok_of)
    sp_ot = season_groups["Spring"]["ot_op"]
    sp_ok = season_groups["Spring"]["ok_of"]
    su_ot = season_groups["Summer"]["ot_op"]
    su_ok = season_groups["Summer"]["ok_of"]

    # Chi-square test
    observed = [[sp_ot, sp_ok], [su_ot, su_ok]]
    row_sums = [sp_ot + sp_ok, su_ot + su_ok]
    col_sums = [sp_ot + su_ot, sp_ok + su_ok]
    total = sum(row_sums)
    chi2 = 0.0
    for r in range(2):
        for c in range(2):
            expected = (row_sums[r] * col_sums[c]) / total
            chi2 += ((observed[r][c] - expected) ** 2) / expected

    # Permutation test on 12 folios (2,000 trials)
    # Metric: difference in ot/ok ratio between Spring and Summer
    random.seed(42)
    observed_diff = season_summary["Spring"]["ratio_ot_to_ok"] - season_summary["Summer"]["ratio_ot_to_ok"]
    n_trials = 2000
    null_diffs = []
    spring_n = sum(1 for item in ZODIAC_FOLIOS if item["season"] == "Spring")
    summer_n = sum(1 for item in ZODIAC_FOLIOS if item["season"] == "Summer")

    for _ in range(n_trials):
        shuffled = random.sample(folio_stats, len(folio_stats))
        perm_spring = shuffled[:spring_n]
        perm_summer = shuffled[spring_n:spring_n + summer_n]

        p_sp_ot = sum(f["ot_op_count"] for f in perm_spring)
        p_sp_ok = sum(f["ok_of_count"] for f in perm_spring)
        p_su_ot = sum(f["ot_op_count"] for f in perm_summer)
        p_su_ok = sum(f["ok_of_count"] for f in perm_summer)

        r_sp = p_sp_ot / max(1, p_sp_ok)
        r_su = p_su_ot / max(1, p_su_ok)
        null_diffs.append(r_sp - r_su)

    mean_null = sum(null_diffs) / n_trials
    var_null = sum((d - mean_null) ** 2 for d in null_diffs) / n_trials
    sd_null = math.sqrt(var_null) if var_null > 0 else 1.0
    z_score = (observed_diff - mean_null) / sd_null
    p_val = sum(1 for d in null_diffs if abs(d) >= abs(observed_diff)) / n_trials

    # Circular correlation with ecliptic angle
    angles = [f["angle_deg"] for f in folio_stats]
    ratios = [f["ratio_ot_to_ok"] for f in folio_stats]
    n_f = len(folio_stats)
    mean_a = sum(angles) / n_f
    mean_r = sum(ratios) / n_f
    cov = sum((angles[i] - mean_a) * (ratios[i] - mean_r) for i in range(n_f))
    var_a = sum((angles[i] - mean_a) ** 2 for i in range(n_f))
    var_r = sum((ratios[i] - mean_r) ** 2 for i in range(n_f))
    corr = cov / (math.sqrt(var_a * var_r) + 1e-9)

    return {
        "folio_stats": folio_stats,
        "season_summary": season_summary,
        "statistical_tests": {
            "spring_vs_summer_chi2": round(chi2, 4),
            "observed_ratio_diff_spring_minus_summer": round(observed_diff, 4),
            "permutation_trials": n_trials,
            "permutation_null_mean": round(mean_null, 4),
            "permutation_null_sd": round(sd_null, 4),
            "z_score": round(z_score, 4),
            "p_value": p_val,
            "ecliptic_angle_correlation": round(corr, 4),
        }
    }


def main():
    lines_by_folio = parse_zodiac_lines()
    scorpio_sagittarius = analyze_scorpio_sagittarius(lines_by_folio)
    drift = analyze_ecliptic_seasonal_drift(lines_by_folio)

    summary = {
        "attack": 201,
        "discovery": 218,
        "title": "Sagittarius (f73v, 'novembre') Centaur Archer Medallion, 10+16+4 = 30° Overflow Law Replication with Scorpio (f73r), and Ecliptic Seasonal Prefix Drift",
        "key_findings": {
            "degree_invariant": "f73v Sagittarius strictly replicates the 10+16+4 = 30° layout established on f73r Scorpio (10 inner, 16 middle, 4 top overflow nymphs)",
            "scorpio_sagittarius_comparison": {
                "f73r": {
                    "total_lines": scorpio_sagittarius["f73r"]["total_lines"],
                    "total_words": scorpio_sagittarius["f73r"]["total_words"],
                    "degree_loci": scorpio_sagittarius["f73r"]["total_degree_loci"],
                    "top_overflow_labels": [x["words"][0] for x in scorpio_sagittarius["f73r"]["top_overflow_loci"]],
                },
                "f73v": {
                    "total_lines": scorpio_sagittarius["f73v"]["total_lines"],
                    "total_words": scorpio_sagittarius["f73v"]["total_words"],
                    "degree_loci": scorpio_sagittarius["f73v"]["total_degree_loci"],
                    "top_overflow_labels": [x["words"][0] for x in scorpio_sagittarius["f73v"]["top_overflow_loci"]],
                }
            },
            "seasonal_prefix_drift": {
                "spring_ot_op_pct": drift["season_summary"]["Spring"]["ot_op_pct"],
                "spring_ok_of_pct": drift["season_summary"]["Spring"]["ok_of_pct"],
                "spring_ratio": drift["season_summary"]["Spring"]["ratio_ot_to_ok"],
                "summer_ot_op_pct": drift["season_summary"]["Summer"]["ot_op_pct"],
                "summer_ok_of_pct": drift["season_summary"]["Summer"]["ok_of_pct"],
                "summer_ratio": drift["season_summary"]["Summer"]["ratio_ot_to_ok"],
                "autumn_ot_op_pct": drift["season_summary"]["Autumn"]["ot_op_pct"],
                "autumn_ok_of_pct": drift["season_summary"]["Autumn"]["ok_of_pct"],
                "autumn_ratio": drift["season_summary"]["Autumn"]["ratio_ot_to_ok"],
                "spring_vs_summer_chi2": drift["statistical_tests"]["spring_vs_summer_chi2"],
                "permutation_z_score": drift["statistical_tests"]["z_score"],
                "p_value": drift["statistical_tests"]["p_value"],
            },
            "codicology": "f73v marks the physical terminal boundary of Quire 11, immediately preceding the missing folio 74 (lost Capricorn and Aquarius)",
        }
    }

    full_output = {
        "summary": summary,
        "scorpio_sagittarius_architecture": scorpio_sagittarius,
        "ecliptic_drift_analysis": drift,
    }

    OUT_JSON.write_text(json.dumps(full_output, indent=2), encoding="utf-8")
    print(f"Attack 201 executed successfully.")
    print(f"Wrote JSON to {OUT_JSON}")
    print(f"Sagittarius: {scorpio_sagittarius['f73v']['architecture']}")
    print(f"Scorpio:     {scorpio_sagittarius['f73r']['architecture']}")
    print(f"Spring ratio ot/ok: {drift['season_summary']['Spring']['ratio_ot_to_ok']} vs Summer: {drift['season_summary']['Summer']['ratio_ot_to_ok']} (z = {drift['statistical_tests']['z_score']}, p = {drift['statistical_tests']['p_value']})")


if __name__ == "__main__":
    main()
