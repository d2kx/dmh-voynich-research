"""
Phase 10 (Avenue C): Astronomical & Botanical Cribs, Pharmaceutical Container (@Lc)
vs. Plant (@Lf/@Lr) Taxonomic Morphology, and the f66r Corner Crib Analysis.

Outputs:
- data/cribs_and_taxonomy.json
"""

import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "cribs_and_taxonomy.json"


def clean_word(raw: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", raw)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "")
    w = w.replace("'", "").replace(",", "").strip()
    return w


def canonicalize(w: str) -> str:
    if not w:
        return ""
    s = w
    if len(s) > 2 and s[0] in ("q", "y"):
        s = s[1:]
    s = s.replace("cth", "ckh").replace("cph", "ckh").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    if len(s) > 2 and s.endswith("m"):
        s = s[:-1] + "r"
    return s


def stem_prefix(w: str, n: int = 4) -> str:
    c = canonicalize(w)
    return c[:n] if len(c) >= n else c


def main():
    lines = []
    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw_line.startswith("#") or not raw_line.strip():
            continue
        # Skip folio header lines like `<f66r> <! $I=T ...>`
        if re.match(r"^<(f[0-9]+[rv][0-9]*|fRos)>\s*<!", raw_line):
            continue
        m_l = re.match(r"^<([^>]+)>\s+(.*)$", raw_line)
        if not m_l:
            continue
        header, body = m_l.group(1), m_l.group(2)
        loc_part = header.split(",")[0] if "," in header else header
        loc_type = header.split(",")[1] if "," in header else ""
        folio = loc_part.split(".")[0]
        body_clean = re.sub(r"<[^>]*>", " ", body)
        toks = [clean_word(t) for t in re.split(r"[.,\s]+", body_clean) if clean_word(t)]
        if not toks:
            continue
        lines.append({
            "folio": folio,
            "loc": loc_part,
            "loc_type": loc_type,
            "raw_body": body,
            "words": toks,
            "canon_words": [canonicalize(w) for w in toks],
        })

    global_canon_counts = Counter()
    canon_to_loci = defaultdict(list)
    for l in lines:
        for w, cw in zip(l["words"], l["canon_words"]):
            if cw:
                global_canon_counts[cw] += 1
                canon_to_loci[cw].append({
                    "folio": l["folio"],
                    "loc": l["loc"],
                    "loc_type": l["loc_type"],
                    "word": w,
                })

    # 1. Taxonomic Morphology Across All Label Categories (@Lc, @Lf, @Lr, @Ln, @Lt, @Ls, @Lz, @La, @L0)
    label_categories = defaultdict(list)
    pharma_folio_labels = defaultdict(list)
    for l in lines:
        lt = l["loc_type"]
        if "L" in lt:
            cat = re.sub(r"^[@+*&]", "", lt)
            for w in l["words"]:
                if len(w) >= 2:
                    label_categories[cat].append((l["folio"], l["loc"], w, canonicalize(w)))
            if l["folio"].startswith(("f88", "f89", "f99", "f100", "f101", "f102")):
                pharma_folio_labels[l["folio"]].append({
                    "loc": l["loc"],
                    "cat": cat,
                    "words": l["words"],
                    "canon": [canonicalize(w) for w in l["words"]],
                })

    category_profiles = {}
    for cat, items in sorted(label_categories.items(), key=lambda x: -len(x[1])):
        ws = [w for _, _, w, _ in items]
        if len(ws) < 5:
            continue
        n = len(ws)
        category_profiles[cat] = {
            "count": n,
            "avg_len": round(sum(len(w) for w in ws) / n, 2),
            "o_initial_pct": round(100.0 * sum(1 for w in ws if w.startswith("o")) / n, 1),
            "d_initial_pct": round(100.0 * sum(1 for w in ws if w.startswith("d")) / n, 1),
            "s_initial_pct": round(100.0 * sum(1 for w in ws if w.startswith("s")) / n, 1),
            "ok_of_initial_pct": round(100.0 * sum(1 for w in ws if w.startswith(("ok", "of"))) / n, 1),
            "ot_op_initial_pct": round(100.0 * sum(1 for w in ws if w.startswith(("ot", "op"))) / n, 1),
            "ol_initial_pct": round(100.0 * sum(1 for w in ws if w.startswith("ol")) / n, 1),
            "or_initial_pct": round(100.0 * sum(1 for w in ws if w.startswith("or")) / n, 1),
            "y_final_pct": round(100.0 * sum(1 for w in ws if w.endswith("y")) / n, 1),
            "r_final_pct": round(100.0 * sum(1 for w in ws if w.endswith("r")) / n, 1),
            "l_final_pct": round(100.0 * sum(1 for w in ws if w.endswith("l")) / n, 1),
            "s_final_pct": round(100.0 * sum(1 for w in ws if w.endswith("s")) / n, 1),
            "in_final_pct": round(100.0 * sum(1 for w in ws if w.endswith("n")) / n, 1),
            "examples": [f"{f}:{w}" for f, _, w, _ in items[:10]],
        }

    # 2. Pharmaceutical Container (@Lc) vs Same-Page Plant (@Lf/@Lr) Root Sharing Test
    # On each Pharmaceutical folio, check if the @Lc container jar label shares a 4-char canonical prefix
    # (or 3-char core stem) with any @Lf/@Lr plant label on the SAME folio, and test via permutation!
    lc_items = []
    folio_plant_labels = defaultdict(list)
    for f, llist in pharma_folio_labels.items():
        for entry in llist:
            if entry["cat"] == "Lc":
                for w, cw in zip(entry["words"], entry["canon"]):
                    if len(cw) >= 3:
                        lc_items.append({"folio": f, "loc": entry["loc"], "word": w, "canon": cw})
            elif entry["cat"] in ("Lf", "Lr", "L0"):
                for w, cw in zip(entry["words"], entry["canon"]):
                    if len(cw) >= 3:
                        folio_plant_labels[f].append({"loc": entry["loc"], "cat": entry["cat"], "word": w, "canon": cw})

    lc_to_plant_matches = []
    for jar in lc_items:
        f = jar["folio"]
        jc = jar["canon"]
        j_pref4 = jc[:4]
        j_pref3 = jc[:3]
        same_page_plants = folio_plant_labels.get(f, [])
        matches_4 = [p for p in same_page_plants if p["canon"][:4] == j_pref4]
        matches_3 = [p for p in same_page_plants if p["canon"][:3] == j_pref3]
        # Also check global matches of the jar's exact canonical word
        other_loci = [loc for loc in canon_to_loci.get(jc, []) if loc["loc"] != jar["loc"]]
        lc_to_plant_matches.append({
            "folio": f,
            "jar_loc": jar["loc"],
            "jar_word": jar["word"],
            "jar_canon": jc,
            "global_canon_count": global_canon_counts[jc],
            "same_folio_4char_plant_matches": matches_4,
            "same_folio_3char_plant_matches": matches_3,
            "exact_canon_matches_elsewhere": other_loci[:8],
        })

    # Permutation test: how often does a jar (@Lc) share a 4-character canonical stem with a plant (@Lf/@Lr) on the SAME folio?
    obs_4char_pairs = sum(1 for m in lc_to_plant_matches if m["same_folio_4char_plant_matches"])
    all_pharma_folios_with_plants = [f for f in set(j["folio"] for j in lc_items) if folio_plant_labels.get(f)]
    rng = random.Random(42)
    null_counts = []
    for _ in range(5000):
        shuffled_folios = [j["folio"] for j in lc_items]
        rng.shuffle(shuffled_folios)
        cnt = 0
        for jar, rf in zip(lc_items, shuffled_folios):
            j_pref4 = jar["canon"][:4]
            if any(p["canon"][:4] == j_pref4 for p in folio_plant_labels.get(rf, [])):
                cnt += 1
        null_counts.append(cnt)
    null_mean = sum(null_counts) / len(null_counts)
    null_std = (sum((x - null_mean) ** 2 for x in null_counts) / len(null_counts)) ** 0.5
    z_lc_plant = (obs_4char_pairs - null_mean) / null_std if null_std > 0 else 0.0
    p_lc_plant = sum(1 for x in null_counts if x >= obs_4char_pairs) / len(null_counts)

    # 3. Astronomical & Zodiac Star Cluster Cribs:
    # - f68r3 (Pleiades 7-star cluster + Aldebaran/Moon wheel)
    # - f71v (Taurus I - "abril", 15 nymphs/stars) & f72r1 (Taurus II - "may", 15 nymphs/stars)
    # - f66r (Bottom-left corner scene with "den mus" / "del" and @Lx labels)
    crib_folios = ["f68r3", "f71v", "f72r1", "f66r"]
    crib_folio_details = {}
    for cf in crib_folios:
        flines = [l for l in lines if l["folio"] == cf]
        rare_links = []
        all_labels = []
        for l in flines:
            if "L" in l["loc_type"] or cf == "f66r":
                for w, cw in zip(l["words"], l["canon_words"]):
                    cnt = global_canon_counts[cw]
                    if "L" in l["loc_type"]:
                        all_labels.append({
                            "loc": l["loc"],
                            "loc_type": l["loc_type"],
                            "word": w,
                            "canon": cw,
                            "global_count": cnt,
                        })
                    if 2 <= cnt <= 6 and len(cw) >= 4:
                        others = [x for x in canon_to_loci[cw] if x["folio"] != cf]
                        if others:
                            rare_links.append({
                                "loc": l["loc"],
                                "loc_type": l["loc_type"],
                                "word": w,
                                "canon": cw,
                                "global_count": cnt,
                                "other_loci": others,
                            })
        crib_folio_details[cf] = {
            "total_lines": len(flines),
            "labels": all_labels,
            "rare_cross_section_links": rare_links,
        }

    results = {
        "label_category_profiles": category_profiles,
        "pharma_jar_to_plant_analysis": {
            "total_lc_jar_labels": len(lc_items),
            "observed_jars_sharing_4char_stem_with_same_page_plant": obs_4char_pairs,
            "null_mean": round(null_mean, 4),
            "null_std": round(null_std, 4),
            "z_score": round(z_lc_plant, 2),
            "p_value": round(p_lc_plant, 4),
            "jar_entries": lc_to_plant_matches,
        },
        "astronomical_and_corner_cribs": crib_folio_details,
    }

    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== 1. TAXONOMIC LABEL PROFILES ACROSS CATEGORIES (@Lc, @Lf, @Lr, @Ln, @Lt, @Ls, @Lz) ===")
    for cat, prof in category_profiles.items():
        print(
            f"  @{cat:3s} (n={prof['count']:3d}, len={prof['avg_len']:.2f}): "
            f"o-={prof['o_initial_pct']:4.1f}% (ok={prof['ok_of_initial_pct']:4.1f}%, ot={prof['ot_op_initial_pct']:4.1f}%, "
            f"ol={prof['ol_initial_pct']:4.1f}%, or={prof['or_initial_pct']:4.1f}%) | "
            f"-y={prof['y_final_pct']:4.1f}%, -r={prof['r_final_pct']:4.1f}%, -l={prof['l_final_pct']:4.1f}%, -n={prof['in_final_pct']:4.1f}%"
        )

    print("\n=== 2. PHARMACEUTICAL CONTAINER (@Lc) vs SAME-PAGE PLANT (@Lf/@Lr) STEM SHARING ===")
    print(
        f"  Jars sharing 4-char canonical stem with same-page plant: {obs_4char_pairs}/{len(lc_items)} "
        f"(null = {null_mean:.3f} ± {null_std:.3f}, z = {z_lc_plant:+.2f}, p = {p_lc_plant:.4f})"
    )
    for m in lc_to_plant_matches:
        p4 = [f"{p['loc']}:{p['word']}" for p in m["same_folio_4char_plant_matches"]]
        p3 = [f"{p['loc']}:{p['word']}" for p in m["same_folio_3char_plant_matches"]]
        ext = [f"{x['loc']}({x['loc_type']}):{x['word']}" for x in m["exact_canon_matches_elsewhere"]]
        print(
            f"  {m['jar_loc']:10s} jar='{m['jar_word']}' (canon='{m['jar_canon']}', cnt={m['global_canon_count']}) "
            f"-> same_page_4ch={p4} | 3ch={p3[:3]} | exact_elsewhere={ext[:3]}"
        )

    print("\n=== 3. ASTRONOMICAL & CORNER CRIB LINKS (f68r3, f71v, f72r1, f66r) ===")
    for cf in crib_folios:
        info = crib_folio_details[cf]
        print(f"  --- {cf} (labels={len(info['labels'])}, rare_links={len(info['rare_cross_section_links'])}) ---")
        for rl in info["rare_cross_section_links"][:10]:
            others = [f"{o['loc']}({o['loc_type']}):{o['word']}" for o in rl["other_loci"]]
            print(f"    {rl['loc']:10s} ({rl['loc_type']:3s}) '{rl['word']}' (cnt={rl['global_count']}) -> {others}")


if __name__ == "__main__":
    main()
