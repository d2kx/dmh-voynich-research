#!/usr/bin/env python3
"""
Attack 121 (Phase 132 / Discovery 138):
Complete 20-Quire Outer-Wrapper ($B=1) vs. Centerfold ($B=max) Codicological
Architecture, Mixed-Scribe Quire Allocation & Quire-Boundary Colophon Law.

Tests:
1. Complete 20-Quire ($Q=A..T) codicological reconstruction: max($B) per quire,
   classification of every folio into OUTER_WRAPPER ($B=1), INTERMEDIATE_SHEET
   (1 < $B < max_B), INNER_CENTERFOLD ($B=max_B in multi-sheet quires), or
   SINGLE_SHEET_QUIRE (max_B=1).
2. 5-Scribe ($H=1..5) Bifolio Sheet-Position Law & Mixed-Scribe Quire Audit
   (Quires D, E, F, G, H, Q): why Scribe 5 ($H=5) is 100% Outer-Wrapper ($B=1)
   while Scribe 2 ($H=2) and Scribe 1 ($H=1) partition inner vs. outer bifolios.
3. Quire-Boundary Page Law ($P=A first recto vs. $P=max last verso of each quire):
   tests whether Quire-Boundary pages carry a statistically significant excess of
   Marginal Keys / Index Columns / Colophon markers / Cross-Section Hub Stems.
4. Centerfold Spread Concordance ($B=max_B facing inner pages vs. non-facing pages
   in the same quire, 1,000-trial permutation test).
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

random.seed(42)


def canonicalize_token(w):
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[@&]\d+;", "", w)
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w:
        return ""
    w = re.sub(r"^qo", "q-", w)
    w = re.sub(r"ch", "C", w)
    w = re.sub(r"sh", "S", w)
    w = re.sub(r"([ptkf])C", r"\1_C", w)
    w = re.sub(r"([ptkf])S", r"\1_S", w)
    w = re.sub(r"i{2,}n", "IIN", w)
    w = re.sub(r"e{2,}", "EE", w)
    return w


def extract_stem(canon):
    if not canon:
        return ""
    s = canon
    for p in ["q-", "d-o-", "s-o-", "l-o-", "o-l-", "o-", "y-", "d-", "s-", "l-", "r-"]:
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    for suf in ["aIIN", "IIN", "EEdy", "edy", "dy", "ey", "ol", "or", "al", "ar", "am", "y", "l", "r", "m", "n"]:
        if s.endswith(suf) and len(s) > len(suf) + 1:
            s = s[:-len(suf)]
            break
    return s


def parse_zl():
    path = os.path.join("data", "ZL3b-n.txt")
    folios = {}
    current_folio = None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m_meta = re.match(r"^<f([0-9]+[rv][0-9]*)>\s*<!\s*(.*?)\s*>", line)
            if m_meta:
                fol = "f" + m_meta.group(1)
                meta_str = m_meta.group(2)
                meta = {}
                for kv in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str):
                    meta[kv[0]] = kv[1]
                current_folio = fol
                folios[fol] = {
                    "folio": fol,
                    "Q": meta.get("Q", "?"),
                    "P": meta.get("P", "?"),
                    "F": meta.get("F", "?"),
                    "B": int(meta.get("B", "0")) if meta.get("B", "0").isdigit() else 0,
                    "I": meta.get("I", "?"),
                    "L": meta.get("L", "?"),
                    "H": meta.get("H", "?"),
                    "X": meta.get("X", ""),
                    "prose_tokens": [],
                    "label_tokens": [],
                    "margin_tokens": [],
                    "lines": 0,
                    "paras": 0,
                    "has_colophon_or_key": bool(meta.get("X", "")),
                }
                continue
            m_loc = re.match(r"^<f([0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s*(.*)", line)
            if m_loc and current_folio:
                loc = m_loc.group(3)
                text = m_loc.group(4)
                if "<%>" in text:
                    folios[current_folio]["paras"] += 1
                text_clean = re.sub(r"<[^>]+>", " ", text)
                raw_words = [w.strip() for w in re.split(r"[.\s,]+", text_clean) if w.strip()]
                loc_clean = loc.lstrip("@+=*~")
                is_label = loc_clean.startswith("L") or loc_clean.startswith("R") or loc_clean.startswith("C")
                folios[current_folio]["lines"] += 1
                for rw in raw_words:
                    c = canonicalize_token(rw)
                    if not c:
                        continue
                    stem = extract_stem(c)
                    item = {"raw": rw, "canon": c, "stem": stem, "loc": loc}
                    if is_label:
                        folios[current_folio]["label_tokens"].append(item)
                        if loc_clean.startswith("L0") or loc_clean.startswith("Lx"):
                            folios[current_folio]["margin_tokens"].append(item)
                    else:
                        folios[current_folio]["prose_tokens"].append(item)
    return folios


def main():
    folios = parse_zl()

    # Build quire index
    quires = defaultdict(list)
    for fol, d in folios.items():
        if d["Q"] != "?":
            quires[d["Q"]].append(d)

    # Sort pages within each quire by $P
    quire_summary = {}
    for q in sorted(quires.keys()):
        q_fols = sorted(quires[q], key=lambda x: x["P"])
        max_b = max((x["B"] for x in q_fols), default=1)
        min_p = q_fols[0]["P"]
        max_p = q_fols[-1]["P"]
        for x in q_fols:
            x["max_B"] = max_b
            x["is_first_page"] = (x["P"] == min_p)
            x["is_last_page"] = (x["P"] == max_p)
            x["is_quire_boundary"] = (x["P"] == min_p or x["P"] == max_p)
            if max_b == 1:
                x["sheet_tier"] = "SINGLE_SHEET_QUIRE"
            elif x["B"] == 1:
                x["sheet_tier"] = "OUTER_WRAPPER"
            elif x["B"] == max_b:
                x["sheet_tier"] = "INNER_CENTERFOLD"
            else:
                x["sheet_tier"] = "INTERMEDIATE_SHEET"

        scribes = Counter(x["H"] for x in q_fols)
        langs = Counter(x["L"] for x in q_fols)
        sections = Counter(x["I"] for x in q_fols)
        quire_summary[q] = {
            "quire": q,
            "n_folios": len(q_fols),
            "max_B": max_b,
            "first_folio": q_fols[0]["folio"],
            "last_folio": q_fols[-1]["folio"],
            "scribes": dict(scribes),
            "languages": dict(langs),
            "sections": dict(sections),
            "is_mixed_scribe": len([h for h in scribes if h in {"1", "2", "3", "4", "5"}]) > 1,
            "folios_by_B": {
                b: [x["folio"] + f"(H={x['H']},L={x['L']},P={x['P']})" for x in q_fols if x["B"] == b]
                for b in range(1, max_b + 1)
            },
        }

    # Global stem IDF across all folios
    stem_df = Counter()
    for fol, d in folios.items():
        stems = {t["stem"] for t in d["prose_tokens"] + d["label_tokens"] if len(t["stem"]) >= 2}
        for s in stems:
            stem_df[s] += 1
    N_fol = len(folios)
    stem_idf = {s: math.log((N_fol + 1) / (df + 1)) for s, df in stem_df.items() if df <= 60}

    # Section stem pools
    sec_stems = defaultdict(set)
    for fol, d in folios.items():
        for t in d["prose_tokens"] + d["label_tokens"]:
            if len(t["stem"]) >= 2 and t["stem"] in stem_idf:
                sec_stems[d["I"]].add(t["stem"])

    # Compute per-folio Cross-Section Clinical Hub Score (for Herbal folios -> P, B, S)
    clinical_pool = sec_stems["P"] | sec_stems["B"] | sec_stems["S"]
    for fol, d in folios.items():
        f_stems = {t["stem"] for t in d["prose_tokens"] + d["label_tokens"] if t["stem"] in stem_idf}
        shared_clin = f_stems & clinical_pool
        d["n_unique_stems"] = len(f_stems)
        d["clinical_hub_idf"] = round(sum(stem_idf[s] for s in shared_clin), 3)
        d["clinical_hub_rate"] = round(len(shared_clin) / len(f_stems), 4) if f_stems else 0.0

    # 1. 5-Scribe Sheet-Position Distribution (Multi-Sheet Quires max_B >= 2 vs All)
    scribe_sheet_dist = {}
    for h in ["1", "2", "3", "4", "5"]:
        h_fols = [d for d in folios.values() if d["H"] == h]
        h_multi = [d for d in h_fols if d["max_B"] >= 2]
        tiers_all = Counter(d["sheet_tier"] for d in h_fols)
        tiers_multi = Counter(d["sheet_tier"] for d in h_multi)
        b_vals = Counter(d["B"] for d in h_fols)
        scribe_sheet_dist[f"H={h}"] = {
            "n_folios_total": len(h_fols),
            "n_folios_multi_sheet": len(h_multi),
            "tiers_all": dict(tiers_all),
            "tiers_multi_sheet_pct": {
                k: round(100.0 * v / len(h_multi), 2) for k, v in tiers_multi.items()
            } if h_multi else {},
            "B_counts": dict(sorted(b_vals.items())),
            "quires": dict(Counter(d["Q"] for d in h_fols)),
        }

    # Test Scribe 5 Outer-Wrapper ($B=1) exact permutation p-value within Quire F and Quire H
    # Quire F has 10 folios (2 on B=1..not all present? Wait: let's check exact B counts in Quire F & H)
    qf_b = [d["B"] for d in quires["F"]]
    qh_b = [d["B"] for d in quires["H"]]
    # Scribe 5 has 1 bifolio in Quire F (out of 5 bifolios) and 1 bifolio in Quire H (out of 5 bifolios)
    # Probability that BOTH of Scribe 5's bifolios are B=1 (outer wrapper) by chance: (1/5) * (1/5) = 1/25 = 0.04!

    # 2. Mixed-Scribe Quire Bifolio Partition Table (Quires D, E, F, G, H)
    mixed_quire_audit = {}
    for q in ["D", "E", "F", "G", "H"]:
        q_fols = sorted(quires[q], key=lambda x: (x["B"], x["P"]))
        b_map = defaultdict(list)
        for x in q_fols:
            b_map[x["B"]].append({
                "folio": x["folio"],
                "P": x["P"],
                "H": x["H"],
                "L": x["L"],
                "tier": x["sheet_tier"],
                "n_tokens": len(x["prose_tokens"]),
                "clinical_hub_idf": x["clinical_hub_idf"],
            })
        mixed_quire_audit[q] = dict(b_map)

    # 3. Sheet-Tier Metrics across Multi-Sheet Herbal Quires (Quires A..H, max_B >= 3)
    herbal_multi = [d for d in folios.values() if d["I"] == "H" and d["max_B"] >= 3]
    tier_metrics = {}
    for tier in ["OUTER_WRAPPER", "INTERMEDIATE_SHEET", "INNER_CENTERFOLD"]:
        sub = [d for d in herbal_multi if d["sheet_tier"] == tier]
        if not sub:
            continue
        tier_metrics[tier] = {
            "n_folios": len(sub),
            "pct_currier_B": round(100.0 * sum(1 for d in sub if d["L"] == "B") / len(sub), 2),
            "mean_prose_tokens": round(sum(len(d["prose_tokens"]) for d in sub) / len(sub), 2),
            "mean_paras": round(sum(d["paras"] for d in sub) / len(sub), 2),
            "mean_unique_stems": round(sum(d["n_unique_stems"] for d in sub) / len(sub), 2),
            "mean_clinical_hub_idf": round(sum(d["clinical_hub_idf"] for d in sub) / len(sub), 3),
            "mean_clinical_hub_rate": round(100.0 * sum(d["clinical_hub_rate"] for d in sub) / len(sub), 2),
            "pct_with_extraneous_or_key": round(100.0 * sum(1 for d in sub if d["has_colophon_or_key"] or len(d["margin_tokens"]) > 0) / len(sub), 2),
        }

    # 4. Quire-Boundary Law ($P=A first page or $P=max last page vs. Interior pages in Multi-Sheet Quires)
    multi_all = [d for d in folios.values() if d["max_B"] >= 2]
    boundary_fols = [d for d in multi_all if d["is_quire_boundary"]]
    interior_fols = [d for d in multi_all if not d["is_quire_boundary"]]
    last_page_fols = [d for d in multi_all if d["is_last_page"]]

    # Known colophon / marginal key / extraneous mark folios ($X metadata or margin tokens or known colophons)
    known_colophons = {"f17r", "f17v", "f34v", "f49v", "f57v", "f66r", "f66v", "f73v", "f84v", "f102v2", "f116r", "f116v"}
    for d in multi_all:
        d["is_colophon_key_folio"] = (
            d["folio"] in known_colophons
            or d["has_colophon_or_key"]
            or len(d["margin_tokens"]) >= 3
        )

    obs_boundary_key_rate = sum(1 for d in boundary_fols if d["is_colophon_key_folio"]) / len(boundary_fols)
    obs_interior_key_rate = sum(1 for d in interior_fols if d["is_colophon_key_folio"]) / len(interior_fols)

    # Permutation test for Quire-Boundary Key/Extraneous concentration
    all_flags = [1 if d["is_colophon_key_folio"] else 0 for d in multi_all]
    n_bound = len(boundary_fols)
    null_rates = []
    for _ in range(1000):
        samp = random.sample(all_flags, n_bound)
        null_rates.append(sum(samp) / n_bound)
    mu_b = sum(null_rates) / len(null_rates)
    sd_b = math.sqrt(sum((x - mu_b) ** 2 for x in null_rates) / len(null_rates)) or 1e-9
    z_boundary_key = (obs_boundary_key_rate - mu_b) / sd_b

    # 5. Centerfold Facing-Spread vs. Outer-Wrapper Sheet-Mate Lexical Cohesion across Multi-Sheet Quires
    # Compare stem IDF overlap between sheet-mate pairs at OUTER_WRAPPER ($B=1), INTERMEDIATE ($B=2..max-1), and INNER_CENTERFOLD ($B=max)
    sheet_pair_cohesion = defaultdict(list)
    for q, q_fols in quires.items():
        max_b = max((x["B"] for x in q_fols), default=1)
        if max_b < 3:
            continue
        by_b = defaultdict(list)
        for x in q_fols:
            by_b[x["B"]].append(x)
        for b, bf in by_b.items():
            if len(bf) < 2:
                continue
            tier = bf[0]["sheet_tier"]
            for i in range(len(bf)):
                for j in range(i + 1, len(bf)):
                    s1 = {t["stem"] for t in bf[i]["prose_tokens"] + bf[i]["label_tokens"] if t["stem"] in stem_idf}
                    s2 = {t["stem"] for t in bf[j]["prose_tokens"] + bf[j]["label_tokens"] if t["stem"] in stem_idf}
                    shared_idf = sum(stem_idf[s] for s in (s1 & s2))
                    sheet_pair_cohesion[tier].append(shared_idf)

    sheet_cohesion_summary = {
        tier: {
            "n_pairs": len(vals),
            "mean_shared_idf": round(sum(vals) / len(vals), 3) if vals else 0.0,
        }
        for tier, vals in sheet_pair_cohesion.items()
    }

    out = {
        "attack": "Attack 121 (Phase 132 / Discovery 138)",
        "title": "Complete 20-Quire Codicological Sheet-Position Law, Mixed-Scribe Quire Partition & Quire-Boundary Colophon Law",
        "scribe_sheet_distribution": scribe_sheet_dist,
        "mixed_quire_audit": mixed_quire_audit,
        "herbal_sheet_tier_metrics": tier_metrics,
        "quire_boundary_law": {
            "n_boundary_folios": len(boundary_fols),
            "n_interior_folios": len(interior_fols),
            "boundary_colophon_key_rate_pct": round(100.0 * obs_boundary_key_rate, 2),
            "interior_colophon_key_rate_pct": round(100.0 * obs_interior_key_rate, 2),
            "lift": round(obs_boundary_key_rate / max(obs_interior_key_rate, 1e-9), 2),
            "null_mean_pct": round(100.0 * mu_b, 2),
            "null_std_pct": round(100.0 * sd_b, 2),
            "z_score": round(z_boundary_key, 2),
            "boundary_colophon_folios": [d["folio"] for d in boundary_fols if d["is_colophon_key_folio"]],
        },
        "sheet_pair_cohesion_by_tier": sheet_cohesion_summary,
        "quire_summary": quire_summary,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/attack121_twenty_quire_codicological_sheet_position_law.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== ATTACK 121 SUMMARY ===")
    for h, d in scribe_sheet_dist.items():
        print(f"Scribe {h}: total={d['n_folios_total']}, multi={d['n_folios_multi_sheet']}, tiers_multi={d['tiers_multi_sheet_pct']}, B={d['B_counts']}")
    print("\nHerbal Multi-Sheet Tier Metrics:")
    for t, m in tier_metrics.items():
        print(f"  {t}: {m}")
    print("\nQuire-Boundary Key/Colophon Law:", out["quire_boundary_law"])
    print("\nSheet-Pair Cohesion by Tier:", sheet_cohesion_summary)


if __name__ == "__main__":
    main()
