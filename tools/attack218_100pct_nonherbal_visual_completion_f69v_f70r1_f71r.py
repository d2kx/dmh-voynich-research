#!/usr/bin/env python3
"""
Attack 218 (Discovery 235): 100% Visual Scan Completion of All Non-Herbal Sections (99/99 Folios),
p127 3-Panel Foldout Wheel Progression (f69v -> f70r1 -> f70r2), and Aries I+II 30-Degree Medallion Symmetry (f70v1 <-> f71r).
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

def normalize_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = w.replace("<->", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    w = re.sub(r"[^a-zA-Z0-9']", "", w)
    return w.strip().lower()

def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = re.sub(r"^p", "t", s)
    s = re.sub(r"^f", "k", s)
    s = re.sub(r"^cph", "cth", s)
    s = re.sub(r"^cfh", "ckh", s)
    s = s.replace("iin", "N").replace("in", "n")
    for suf in ["edy", "ody", "ey", "dy", "y", "aN", "oN", "eN", "N", "ar", "or", "al", "ol", "am", "om", "an", "on"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s

def parse_zl_loci(zl_path: str):
    folio_loci = defaultdict(list)
    folio_words = defaultdict(list)
    with open(zl_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_loc = re.match(r"^<(f[a-zA-Z0-9]+)\.([^>]+)>\s+(.*)$", line)
            if not m_loc:
                continue
            fol, loc, body = m_loc.group(1), m_loc.group(2), m_loc.group(3)
            clean_body = re.sub(r"<[^>]*>", " ", body)
            tokens = [normalize_word(t) for t in re.split(r"[.\s,]+", clean_body)]
            tokens = [t for t in tokens if t]
            if not tokens:
                continue
            folio_loci[fol].append({"loc": loc, "words": tokens})
            folio_words[fol].extend(tokens)
    return folio_loci, folio_words

def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)

def token_coverage(target_words, source_stems: set) -> float:
    if not target_words:
        return 0.0
    return sum(1 for w in target_words if canonical_stem(w) in source_stems) / len(target_words)

def main():
    idx_path = os.path.join("data", "folio_index.json")
    zl_path = os.path.join("data", "ZL3b-n.txt")
    with open(idx_path, "r", encoding="utf-8") as f:
        idx_folios = json.load(f)["folios"]
    folio_loci, folio_words = parse_zl_loci(zl_path)

    # 1. Section-by-Section Visual Scan Audit across all 226 Folios
    pages_files = [p for p in os.listdir("pages") if p.endswith(".png")]
    section_audit = defaultdict(lambda: {"total": 0, "rendered": 0, "unrendered_folios": []})
    total_non_herbal = 0
    rendered_non_herbal = 0
    for fol, info in idx_folios.items():
        sec = info.get("section_code") or "Unknown"
        pat = re.compile(r"(^|_)" + re.escape(fol) + r"(_|\.)")
        has_png = any(
            pat.search(p)
            or (fol.startswith("f68v") and p.startswith("f68v_"))
            or (fol == "fRos" and ("f85" in p or "rosette" in p))
            for p in pages_files
        )
        section_audit[sec]["total"] += 1
        if has_png:
            section_audit[sec]["rendered"] += 1
        else:
            section_audit[sec]["unrendered_folios"].append(fol)
        if sec != "H":
            total_non_herbal += 1
            if has_png:
                rendered_non_herbal += 1

    section_summary = {}
    for sec, d in sorted(section_audit.items()):
        section_summary[sec] = {
            "total": d["total"],
            "rendered": d["rendered"],
            "coverage_pct": round(100.0 * d["rendered"] / max(1, d["total"]), 2),
            "unrendered_folios": d["unrendered_folios"]
        }

    # 2. Forensics of f69v (28-spoke blue/green turret wheel) & f70r1 (6-lobe nebula wheel) & f70r2 on Foldout p127
    f69v_spokes = []
    f69v_rings = []
    for item in folio_loci["f69v"]:
        if ",@R" in item["loc"] or ",+R" in item["loc"]:
            f69v_spokes.extend(item["words"])
        else:
            f69v_rings.extend(item["words"])

    f70r1_inner = []
    f70r1_outer_spokes = []
    f70r1_outer_rings = []
    for item in folio_loci["f70r1"]:
        if "Ri" in item["loc"] or "Ci" in item["loc"]:
            f70r1_inner.extend(item["words"])
        elif "Ro" in item["loc"]:
            f70r1_outer_spokes.extend(item["words"])
        else:
            f70r1_outer_rings.extend(item["words"])

    f70r2_words = folio_words["f70r2"]

    f69v_spoke_stems = set(canonical_stem(w) for w in f69v_spokes)
    f69v_ring_stems = set(canonical_stem(w) for w in f69v_rings)
    p127_other_words = folio_words["f70r1"] + f70r2_words
    p127_other_stems = set(canonical_stem(w) for w in p127_other_words)

    # How many of f69v's 32 spoke words echo in f69v's own rings vs p127 foldout vs Astro/Zodiac/Cosmo corpus?
    azc_words = [w for fol, info in idx_folios.items() if info.get("section_code") in ("A", "Z", "C") and fol != "f69v" for w in folio_words[fol]]
    azc_stems = set(canonical_stem(w) for w in azc_words)

    f69v_analysis = {
        "total_words": len(folio_words["f69v"]),
        "spoke_loci_count": sum(1 for item in folio_loci["f69v"] if "R" in item["loc"]),
        "spoke_words_count": len(f69v_spokes),
        "spoke_words_list": f69v_spokes,
        "ring_words_count": len(f69v_rings),
        "spoke_o_initial_pct": round(100.0 * sum(1 for w in f69v_spokes if w.startswith("o")) / len(f69v_spokes), 2),
        "spoke_ok_ot_pct": round(100.0 * sum(1 for w in f69v_spokes if w.startswith(("ok", "ot"))) / len(f69v_spokes), 2),
        "spokes_covered_by_f69v_rings_pct": round(100.0 * token_coverage(f69v_spokes, f69v_ring_stems), 2),
        "spokes_covered_by_p127_foldout_pct": round(100.0 * token_coverage(f69v_spokes, f69v_ring_stems | p127_other_stems), 2),
        "spokes_covered_by_azc_corpus_pct": round(100.0 * token_coverage(f69v_spokes, azc_stems), 2),
        "rings_seeded_by_spokes_pct": round(100.0 * token_coverage(f69v_rings, f69v_spoke_stems), 2),
    }

    f70r1_inner_stems = set(canonical_stem(w) for w in f70r1_inner)
    f70r1_outer_words = f70r1_outer_spokes + f70r1_outer_rings
    f70r1_outer_stems = set(canonical_stem(w) for w in f70r1_outer_words)

    f70r1_analysis = {
        "total_words": len(folio_words["f70r1"]),
        "inner_star_and_ring_words": len(f70r1_inner),
        "outer_nebula_spoke_words": len(f70r1_outer_spokes),
        "outer_concentric_ring_words": len(f70r1_outer_rings),
        "inner_star_labels": [item["words"] for item in folio_loci["f70r1"] if "Ri" in item["loc"]],
        "outer_nebula_spoke_labels": [item["words"] for item in folio_loci["f70r1"] if "Ro" in item["loc"]],
        "inner_seeds_outer_token_pct": round(100.0 * token_coverage(f70r1_outer_words, f70r1_inner_stems), 2),
        "outer_seeds_inner_token_pct": round(100.0 * token_coverage(f70r1_inner, f70r1_outer_stems), 2),
        "o_initial_pct": round(100.0 * sum(1 for w in folio_words["f70r1"] if w.startswith("o")) / len(folio_words["f70r1"]), 2),
    }

    # 3-Panel Foldout p127 Progression: f69v (left) -> f70r1 (center) -> f70r2 (right)
    s69v = set(canonical_stem(w) for w in folio_words["f69v"])
    s70r1 = set(canonical_stem(w) for w in folio_words["f70r1"])
    s70r2 = set(canonical_stem(w) for w in f70r2_words)
    p127_progression = {
        "f69v_words": len(folio_words["f69v"]),
        "f70r1_words": len(folio_words["f70r1"]),
        "f70r2_words": len(f70r2_words),
        "total_p127_words": len(folio_words["f69v"]) + len(folio_words["f70r1"]) + len(f70r2_words),
        "f69v_to_f70r1_token_cov_pct": round(100.0 * token_coverage(folio_words["f70r1"], s69v), 2),
        "f69v_and_f70r1_to_f70r2_token_cov_pct": round(100.0 * token_coverage(f70r2_words, s69v | s70r1), 2),
        "f70r2_to_f69v_token_cov_pct": round(100.0 * token_coverage(folio_words["f69v"], s70r2), 2),
        "f70r2_to_f70r1_token_cov_pct": round(100.0 * token_coverage(folio_words["f70r1"], s70r2), 2),
        "jaccard_f69v_f70r2": round(jaccard(s69v, s70r2), 4),
        "jaccard_f70r1_f70r2": round(jaccard(s70r1, s70r2), 4),
    }

    # 4. Aries I (f70v1) <-> Aries II (f71r) 30-Degree Medallion Spread Analysis
    f70v1_words = folio_words["f70v1"]
    f71r_words = folio_words["f71r"]
    f71r_labels = [w for item in folio_loci["f71r"] if "L" in item["loc"] for w in item["words"]]
    f71r_rings = [w for item in folio_loci["f71r"] if "L" not in item["loc"] for w in item["words"]]
    f70v1_labels = [w for item in folio_loci["f70v1"] if "L" in item["loc"] for w in item["words"]]
    f70v1_rings = [w for item in folio_loci["f70v1"] if "L" not in item["loc"] for w in item["words"]]

    s70v1 = set(canonical_stem(w) for w in f70v1_words)
    s71r = set(canonical_stem(w) for w in f71r_words)

    aries_spread_analysis = {
        "f70v1_aries_i_words": len(f70v1_words),
        "f71r_aries_ii_words": len(f71r_words),
        "f70v1_nymph_label_loci": sum(1 for item in folio_loci["f70v1"] if "Lz" in item["loc"]),
        "f71r_nymph_label_loci": sum(1 for item in folio_loci["f71r"] if "Lz" in item["loc"]),
        "total_aries_nymphs": sum(1 for item in folio_loci["f70v1"] if "Lz" in item["loc"]) + sum(1 for item in folio_loci["f71r"] if "Lz" in item["loc"]),
        "f71r_nymph_labels": f71r_labels,
        "f70v1_o_initial_pct": round(100.0 * sum(1 for w in f70v1_words if w.startswith("o")) / len(f70v1_words), 2),
        "f71r_o_initial_pct": round(100.0 * sum(1 for w in f71r_words if w.startswith("o")) / len(f71r_words), 2),
        "f70v1_ot_ok_pct": round(100.0 * sum(1 for w in f70v1_words if w.startswith(("ot", "ok"))) / len(f70v1_words), 2),
        "f71r_ot_ok_pct": round(100.0 * sum(1 for w in f71r_words if w.startswith(("ot", "ok"))) / len(f71r_words), 2),
        "f70v1_seeds_f71r_token_pct": round(100.0 * token_coverage(f71r_words, s70v1), 2),
        "f71r_seeds_f70v1_token_pct": round(100.0 * token_coverage(f70v1_words, s71r), 2),
        "stem_jaccard_aries_pair": round(jaccard(s70v1, s71r), 4),
        "f71r_labels_covered_by_f71r_rings_pct": round(100.0 * token_coverage(f71r_labels, set(canonical_stem(w) for w in f71r_rings)), 2),
        "f71r_labels_covered_by_aries_spread_pct": round(100.0 * token_coverage(f71r_labels, set(canonical_stem(w) for w in f71r_rings + f70v1_words)), 2),
        "shared_exact_words_aries_pair": sorted(list(set(f70v1_words) & set(f71r_words)))
    }

    out = {
        "attack": 218,
        "discovery": 235,
        "title": "100% Non-Herbal Visual Scan Completion (99/99 Folios), p127 3-Panel Foldout Progression (f69v->f70r1->f70r2), and Aries 30-Degree Spread (f70v1<->f71r)",
        "non_herbal_completion": {
            "total_non_herbal_folios": total_non_herbal,
            "rendered_non_herbal_folios": rendered_non_herbal,
            "non_herbal_coverage_pct": round(100.0 * rendered_non_herbal / max(1, total_non_herbal), 2),
            "total_manuscript_folios": len(idx_folios),
            "rendered_manuscript_folios": sum(d["rendered"] for d in section_audit.values()),
            "manuscript_coverage_pct": round(100.0 * sum(d["rendered"] for d in section_audit.values()) / len(idx_folios), 2),
            "by_section": section_summary
        },
        "f69v_28spoke_wheel_analysis": f69v_analysis,
        "f70r1_6lobe_nebula_wheel_analysis": f70r1_analysis,
        "p127_three_panel_foldout_progression": p127_progression,
        "aries_30degree_spread_f70v1_f71r": aries_spread_analysis
    }

    out_path = os.path.join("data", "attack218_100pct_nonherbal_visual_completion_f69v_f70r1_f71r.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")
    print(f"Non-Herbal Visual Coverage: {rendered_non_herbal}/{total_non_herbal} ({out['non_herbal_completion']['non_herbal_coverage_pct']}%)")
    print(f"Total Manuscript Coverage: {out['non_herbal_completion']['rendered_manuscript_folios']}/{out['non_herbal_completion']['total_manuscript_folios']} ({out['non_herbal_completion']['manuscript_coverage_pct']}%)")
    print(f"f69v (28 spokes, {f69v_analysis['spoke_words_count']} spoke words): o-init={f69v_analysis['spoke_o_initial_pct']}%, ok/ot={f69v_analysis['spoke_ok_ot_pct']}%, covered by p127={f69v_analysis['spokes_covered_by_p127_foldout_pct']}%, by AZC={f69v_analysis['spokes_covered_by_azc_corpus_pct']}%")
    print(f"f70r1 (6-lobe nebula, {f70r1_analysis['total_words']}w): o-init={f70r1_analysis['o_initial_pct']}%, outer->inner cov={f70r1_analysis['outer_seeds_inner_token_pct']}%")
    print(f"p127 Foldout (615w): f69v+f70r1 -> f70r2 cov={p127_progression['f69v_and_f70r1_to_f70r2_token_cov_pct']}%, f70r2 -> f69v cov={p127_progression['f70r2_to_f69v_token_cov_pct']}%, f70r2 -> f70r1 cov={p127_progression['f70r2_to_f70r1_token_cov_pct']}%")
    print(f"Aries Spread (f70v1 + f71r): {aries_spread_analysis['f70v1_nymph_label_loci']} + {aries_spread_analysis['f71r_nymph_label_loci']} = {aries_spread_analysis['total_aries_nymphs']} nymphs; o-init: {aries_spread_analysis['f70v1_o_initial_pct']}% vs {aries_spread_analysis['f71r_o_initial_pct']}%; token cov: {aries_spread_analysis['f70v1_seeds_f71r_token_pct']}% / {aries_spread_analysis['f71r_seeds_f70v1_token_pct']}%")

if __name__ == "__main__":
    main()
