#!/usr/bin/env python3
"""
Phase 39 / Attack 28: The 9-Rosettes Foldout (fRos / f85v2) 9-Sphere Cosmological
Routing Map & Causeway/Rim Decoder.

Parses all 160 loci of <fRos> (the 6-page foldout f85v2) in data/ZL3b-n.txt using
Petersen's explicit sub-locus tags (<!1:1>..<!9:7>, <!I>..<!VIII>, <!Spiral>,
clock annotations, and @Cc rim texts) and tests:
1. 3x3 Grid Architecture of the 9 Spheres (Circles 1..9) + 8 Causeways (I..VIII):
   - Separates Rim Circular Texts (@Cc) from Interior Labels (@L0/@Pb) for each
     of the 9 circles (1=NW, 2=W, 3=SW, 4=N, 5=Center, 6=S, 7=NE, 8=E, 9=SE).
2. Morphological Contrast (Rim @Cc vs. Sphere Interior Labels vs. Causeway Bridges I..VIII):
   - Tests how qok-/qot- operators, op-/of- container/surface prefixes, and o-/d-/s-
     nominal labels distribute across rims, interiors, and causeways.
3. Manuscript Section & Quire N Routing Matrix (1,000-trial permutation test):
   - Tests whether rare/moderately-rare canonical tokens (2 <= df <= 15) on fRos
     route preferentially into the adjacent Quire N Cosmological/Text pages
     (f85r1, f85r2, f86v4, f86v6, f86v5, f86v3) and into specific manuscript sections
     ($I=P Pharmaceutical, $I=B Biological, $I=Z Zodiac, $I=H Herbal, $I=S Recipes).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack28_rosettes_9sphere_routing_decoder.json"

CIRCLE_GRID_NAMES = {
    "1": "Circle 1 (NW Corner)",
    "2": "Circle 2 (W Middle)",
    "3": "Circle 3 (SW Corner / Clock)",
    "4": "Circle 4 (N Middle)",
    "5": "Circle 5 (Center Hub)",
    "6": "Circle 6 (S Middle)",
    "7": "Circle 7 (NE Corner / Spiral)",
    "8": "Circle 8 (E Middle)",
    "9": "Circle 9 (SE Corner)",
}

CC_LOCUS_TO_CIRCLE = {
    "2": "1",
    "20": "4",
    "35": "7",
    "36": "7",  # Spiral
    "47": "2",
    "62": "5",
    "87": "8",
    "94": "3",
    "113": "3",  # above clock
    "114": "3",  # below clock
    "122": "6",
    "133": "9",
}


def normalize_eva(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    return w


def canonical_4rule(w: str) -> str:
    if not w:
        return ""
    s = w
    if s.startswith("qo") and len(s) > 2:
        s = s[2:]
    elif s.startswith("q") and len(s) > 1:
        s = s[1:]
    s = s.replace("ckh", "kh").replace("cth", "th").replace("cph", "ph").replace("cfh", "fh")
    s = re.sub(r"i{2,}", "i", s)
    s = re.sub(r"e{2,}", "e", s)
    if len(s) > 1 and s.startswith("p"):
        s = "t" + s[1:]
    elif len(s) > 1 and s.startswith("f"):
        s = "k" + s[1:]
    return s


def parse_zl_with_fros():
    folios = {}
    fros_loci = []
    current_folio = None
    meta = {}

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    meta_re = re.compile(r"\$([A-Z])=([A-Za-z0-9]+)")

    with open(ZL_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            if raw.startswith("<f") and ">" in raw and "." not in raw.split(">")[0]:
                m_f = re.match(r"^<(f[A-Za-z0-9]+)>", raw)
                if m_f:
                    current_folio = m_f.group(1)
                    meta = dict(meta_re.findall(raw))
                    folios[current_folio] = {
                        "folio": current_folio,
                        "section": meta.get("I", ""),
                        "language": meta.get("L", ""),
                        "hand": meta.get("H", ""),
                        "quire": meta.get("Q", ""),
                        "lines": [],
                    }
                continue
            m = line_re.match(raw)
            if m and current_folio:
                f_id, loc_id, loc_type, body = m.groups()
                comments = re.findall(r"<!([^>]+)>", body)
                body_clean = re.sub(r"<!.*?>", "", body)
                raw_tokens = re.split(r"[.\s,]+", body_clean)
                tokens = [normalize_eva(t) for t in raw_tokens]
                tokens = [t for t in tokens if t]
                entry = {
                    "loc_id": loc_id,
                    "loc_type": loc_type,
                    "comments": comments,
                    "tokens": tokens,
                }
                folios[current_folio]["lines"].append(entry)
                if f_id == "fRos":
                    fros_loci.append(entry)
    return folios, fros_loci


def morph_profile(tokens):
    n = max(len(tokens), 1)
    return {
        "token_count": len(tokens),
        "unique_types": len(set(tokens)),
        "mean_length": round(sum(len(t) for t in tokens) / n, 3),
        "qok_qot_rate": round(sum(1 for t in tokens if t.startswith(("qok", "qot", "qo"))) / n, 4),
        "op_of_labial_rate": round(sum(1 for t in tokens if "p" in t or "f" in t) / n, 4),
        "ok_ot_gallows_rate": round(sum(1 for t in tokens if t.startswith(("ok", "ot", "yk", "yt"))) / n, 4),
        "o_initial_rate": round(sum(1 for t in tokens if t.startswith("o")) / n, 4),
        "d_s_initial_rate": round(sum(1 for t in tokens if t.startswith(("d", "s"))) / n, 4),
        "edy_dy_verbal_rate": round(sum(1 for t in tokens if t.endswith(("edy", "eedy", "dy"))) / n, 4),
        "ar_al_or_ol_liquid_rate": round(sum(1 for t in tokens if t.endswith(("ar", "al", "or", "ol"))) / n, 4),
        "aiin_unit_rate": round(sum(1 for t in tokens if t.endswith(("aiin", "iin", "in"))) / n, 4),
    }


def main():
    random.seed(42)
    folios, fros_loci = parse_zl_with_fros()

    # Global canonical df across all folios
    global_df = Counter()
    folio_canon_sets = {}
    for f_id, fdata in folios.items():
        cset = set()
        for ln in fdata["lines"]:
            for t in ln["tokens"]:
                c = canonical_4rule(t)
                if len(c) >= 3:
                    cset.add(c)
        folio_canon_sets[f_id] = cset
        for c in cset:
            global_df[c] += 1

    # Partition fRos loci into:
    # - 9 circles (1..9), each with rim_tokens (@Cc/+Ca) and interior_tokens (@L0/@Pb)
    # - 8 causeways (I..VIII)
    circles = {
        str(i): {
            "circle_id": str(i),
            "name": CIRCLE_GRID_NAMES[str(i)],
            "rim_tokens": [],
            "interior_tokens": [],
            "interior_loci": [],
        }
        for i in range(1, 10)
    }
    causeways = {}
    current_causeway = None

    all_rim_tokens = []
    all_interior_tokens = []
    all_causeway_tokens = []

    for loc in fros_loci:
        lid = loc["loc_id"]
        ltype = loc["loc_type"]
        comms = loc["comments"]
        toks = loc["tokens"]

        # Check if this is a Rim @Cc/+Ca locus
        if lid in CC_LOCUS_TO_CIRCLE:
            cid = CC_LOCUS_TO_CIRCLE[lid]
            circles[cid]["rim_tokens"].extend(toks)
            all_rim_tokens.extend(toks)
            continue

        # Check if comment has circle:locus e.g. 1:1 .. 9:7 or clock
        assigned = False
        for c in comms:
            m_cl = re.match(r"^([1-9]):([0-9]+)$", c.strip())
            if m_cl:
                cid, sub = m_cl.groups()
                circles[cid]["interior_tokens"].extend(toks)
                circles[cid]["interior_loci"].append({"sub_locus": c, "tokens": toks})
                all_interior_tokens.extend(toks)
                assigned = True
                break
            if "clock" in c:
                circles["3"]["interior_tokens"].extend(toks)
                circles["3"]["interior_loci"].append({"sub_locus": c, "tokens": toks})
                all_interior_tokens.extend(toks)
                assigned = True
                break
            if c.strip() in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII"):
                current_causeway = c.strip()
                if current_causeway not in causeways:
                    causeways[current_causeway] = {"causeway_id": current_causeway, "tokens": [], "loci": []}
                causeways[current_causeway]["tokens"].extend(toks)
                causeways[current_causeway]["loci"].append({"loc_id": lid, "tokens": toks})
                all_causeway_tokens.extend(toks)
                assigned = True
                break

        if not assigned and current_causeway and int(lid) >= 137:
            causeways[current_causeway]["tokens"].extend(toks)
            causeways[current_causeway]["loci"].append({"loc_id": lid, "tokens": toks})
            all_causeway_tokens.extend(toks)
        elif not assigned:
            # Continuation of Circle 1 block (loci 4..10)
            circles["1"]["interior_tokens"].extend(toks)
            circles["1"]["interior_loci"].append({"sub_locus": f"1:cont_{lid}", "tokens": toks})
            all_interior_tokens.extend(toks)

    # Compute morphological profiles for each circle and causeway
    circle_reports = []
    for i in range(1, 10):
        cid = str(i)
        cdata = circles[cid]
        combined = cdata["rim_tokens"] + cdata["interior_tokens"]
        c_canon = set(canonical_4rule(t) for t in combined if len(canonical_4rule(t)) >= 3)

        # Find rare links (2 <= global_df <= 10) to other folios
        rare_links = []
        section_hits = Counter()
        quire_n_hits = []
        for c_tok in sorted(c_canon):
            df = global_df[c_tok]
            if 2 <= df <= 12:
                other_folios = [f for f, fset in folio_canon_sets.items() if f != "fRos" and c_tok in fset]
                for of in other_folios:
                    sec = folios[of]["section"]
                    section_hits[sec] += 1
                    if folios[of]["quire"] == "N":
                        quire_n_hits.append({"canonical": c_tok, "target_folio": of, "global_df": df})
                rare_links.append({
                    "canonical": c_tok,
                    "global_df": df,
                    "target_folios": other_folios[:8],
                })

        circle_reports.append({
            "circle_id": cid,
            "name": cdata["name"],
            "rim_profile": morph_profile(cdata["rim_tokens"]),
            "interior_profile": morph_profile(cdata["interior_tokens"]),
            "sample_rim_tokens": cdata["rim_tokens"][:15],
            "sample_interior_tokens": cdata["interior_tokens"][:15],
            "section_routing_counts_df2_12": dict(section_hits),
            "quire_N_links": quire_n_hits,
            "rare_manuscript_links": rare_links[:12],
        })

    causeway_reports = []
    for cid in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]:
        if cid not in causeways:
            continue
        cw = causeways[cid]
        c_canon = set(canonical_4rule(t) for t in cw["tokens"] if len(canonical_4rule(t)) >= 3)
        rare_links = []
        for c_tok in sorted(c_canon):
            df = global_df[c_tok]
            if 2 <= df <= 15:
                other_folios = [f for f, fset in folio_canon_sets.items() if f != "fRos" and c_tok in fset]
                rare_links.append({
                    "canonical": c_tok,
                    "global_df": df,
                    "target_folios": other_folios[:8],
                })
        causeway_reports.append({
            "causeway_id": cid,
            "profile": morph_profile(cw["tokens"]),
            "tokens": cw["tokens"],
            "rare_manuscript_links": rare_links,
        })

    # Permutation test: Do fRos rare canonical tokens (2 <= df <= 10) co-occur in the same
    # Quire N foldout neighborhood (f85r1, f85r2, f86v4, f86v6, f86v5, f86v3) significantly
    # above random Currier-B folio sets of the same size (6 folios)?
    fros_rare = [c for c in folio_canon_sets["fRos"] if 2 <= global_df[c] <= 10]
    quire_n_others = [f for f, fd in folios.items() if fd["quire"] == "N" and f != "fRos"]
    quire_n_union = set()
    for f in quire_n_others:
        quire_n_union |= folio_canon_sets[f]

    obs_quire_n_shared = sum(1 for c in fros_rare if c in quire_n_union)

    currier_b_candidates = [f for f, fd in folios.items() if fd["language"] == "B" and f != "fRos"]
    null_shared = []
    for _ in range(1000):
        sampled = random.sample(currier_b_candidates, len(quire_n_others))
        u = set()
        for sf in sampled:
            u |= folio_canon_sets[sf]
        null_shared.append(sum(1 for c in fros_rare if c in u))

    mean_null = sum(null_shared) / len(null_shared)
    std_null = math.sqrt(sum((x - mean_null) ** 2 for x in null_shared) / len(null_shared)) or 1.0
    z_quire_n = (obs_quire_n_shared - mean_null) / std_null
    p_quire_n = sum(1 for x in null_shared if x >= obs_quire_n_shared) / len(null_shared)

    # Also compute section-level enrichment of fRos rare tokens (2 <= df <= 10) across all manuscript sections
    section_folios = defaultdict(list)
    for f_id, fd in folios.items():
        if f_id != "fRos":
            section_folios[fd["section"]].append(f_id)

    section_routing_summary = {}
    for sec, sfolios in sorted(section_folios.items()):
        sec_union = set()
        for sf in sfolios:
            sec_union |= folio_canon_sets[sf]
        shared = [c for c in fros_rare if c in sec_union]
        section_routing_summary[sec] = {
            "folio_count": len(sfolios),
            "shared_rare_fRos_tokens_df2_10": len(shared),
            "shared_rate_per_folio": round(len(shared) / max(len(sfolios), 1), 3),
            "examples": shared[:12],
        }

    result = {
        "phase": "Phase 39 / Attack 28",
        "title": "The 9-Rosettes Foldout (fRos / f85v2) 9-Sphere Cosmological Routing Map & Causeway/Rim Decoder",
        "overall_fRos_counts": {
            "total_loci": len(fros_loci),
            "rim_token_count": len(all_rim_tokens),
            "interior_label_token_count": len(all_interior_tokens),
            "causeway_token_count": len(all_causeway_tokens),
            "total_fRos_tokens": len(all_rim_tokens) + len(all_interior_tokens) + len(all_causeway_tokens),
            "rare_canonical_types_df2_10": len(fros_rare),
        },
        "layer_morphological_comparison": {
            "rim_Cc_profile": morph_profile(all_rim_tokens),
            "sphere_interior_L0_profile": morph_profile(all_interior_tokens),
            "causeway_I_VIII_profile": morph_profile(all_causeway_tokens),
        },
        "quire_N_foldout_cohesion_test": {
            "quire_N_companion_folios": quire_n_others,
            "fRos_rare_tokens_df2_10_count": len(fros_rare),
            "observed_shared_with_quire_N": obs_quire_n_shared,
            "null_currierB_6folio_mean": round(mean_null, 3),
            "null_currierB_6folio_std": round(std_null, 3),
            "z_score": round(z_quire_n, 2),
            "p_value": round(p_quire_n, 4),
            "shared_examples": [c for c in fros_rare if c in quire_n_union],
        },
        "section_routing_summary_df2_10": section_routing_summary,
        "nine_spheres": circle_reports,
        "eight_causeways": causeway_reports,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Overall fRos counts:", json.dumps(result["overall_fRos_counts"], indent=2))
    print("Layer morphology:", json.dumps(result["layer_morphological_comparison"], indent=2))
    print("Quire N cohesion:", json.dumps(result["quire_N_foldout_cohesion_test"], indent=2))
    print("Section routing:", json.dumps(result["section_routing_summary_df2_10"], indent=2))


if __name__ == "__main__":
    main()
