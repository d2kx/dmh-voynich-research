#!/usr/bin/env python3
"""
Phase 21 / Attack 10: Zodiac 300-Degree Ecliptic Coordinate System, Astrological Aspect
Geometry & The "12° Cancer + 12° Scorpio = 120° Water-Trigon Trine" Discovery (`f70v2–f73v`).

Maps all 299 labeled Zodiac nymphs across the 12 Zodiac medallions (10 signs, 300 degrees
from Pisces through Sagittarius) to their exact:
  - Astrological Sign, Element/Trigon (Fire, Earth, Air, Water), and Modality (Cardinal, Fixed, Mutable)
  - Cumulative Sign Degree d in {1..30} and Ecliptic Longitude lambda in [0..360)
  - Folio Locus number (.k), Concentric Ring index (Ring 1, 2, 3), and Decan (1, 2, 3)
  - Clock-face angle theta in [0..360) parsed from <!HH:MM> comments in ZL3b-n.txt

Tests:
1. Exact verification of the `f113r` Paragraph 1 (`<f113r.1..3>`) Double Hapax Crib:
   - `<f72r3.13,&Lz> ykolairol` = Nymph #12 of Cancer (12° Cancer, lambda = 102°, Water Trigon)
   - `<f73r.13,&Lz> oteeosy`   = Nymph #12 of Scorpio (12° Scorpio, lambda = 222°, Water Trigon)
   - Exact ecliptic separation Delta_lambda = 222° - 102° = 120.0° (Partile Water-Trigon Trine, Delta_d = 0°)!
2. Internal Zodiac Cross-Sign & Within-Sign Label Sharing Geometry:
   - When the same canonical label appears on two different Zodiac nymphs, how often do they share
     the same Sign, same Elemental Trigon (Trine), same Ring, same Decan, or matching Clock Angle?
3. Prose Multi-Zodiac Co-Occurrence Geometry (5,000-trial Monte Carlo Permutation Test):
   - Across all prose paragraphs citing >= 2 rare Zodiac nymph labels (rarity <= 10 and <= 5),
     test enrichment for:
       a) Exact/Near Degree Synchronization (|d_A - d_B| <= 1 or |loc_A - loc_B| <= 1)
       b) Same-Sign Contiguous Arcs (S_A == S_B and |d_A - d_B| <= 2)
       c) Same Elemental Trigon / Trine Aspect (Element_A == Element_B)
       d) Same Concentric Ring (Ring_A == Ring_B) and Same Decan (Decan_A == Decan_B)
4. Starred Recipes (`f103r–f116r`) & Herbal/Biological Folio-by-Folio Ecliptic Calendar Profile.
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

from attack7_positional_envelope_fst import (
    stage3_positional_proclitic_margin,
    extract_core_root_and_envelope,
)

ZL_PATH = os.path.join("data", "ZL3b-n.txt")
INDEX_PATH = os.path.join("data", "folio_index.json")
OUT_JSON = os.path.join("data", "attack10_zodiac_aspect_geometry.json")

# Metadata for the 12 Zodiac medallions (in manuscript order f70v2..f73v)
ZODIAC_FOLIO_META = {
    "f70v2": {
        "sign": "Pisces",
        "sign_idx": 12,  # 1=Aries .. 12=Pisces
        "ecliptic_start_deg": 330,
        "element": "Water",
        "modality": "Mutable",
        "month": "March",
        "deg_offset": 0,  # 1..30
        "half": "Full_30",
    },
    "f70v1": {
        "sign": "Aries",
        "sign_idx": 1,
        "ecliptic_start_deg": 0,
        "element": "Fire",
        "modality": "Cardinal",
        "month": "April (1-15)",
        "deg_offset": 0,  # 1..15
        "half": "Dark_1_15",
    },
    "f71r": {
        "sign": "Aries",
        "sign_idx": 1,
        "ecliptic_start_deg": 0,
        "element": "Fire",
        "modality": "Cardinal",
        "month": "April (16-30)",
        "deg_offset": 15,  # 16..30
        "half": "Light_16_30",
    },
    "f71v": {
        "sign": "Taurus",
        "sign_idx": 2,
        "ecliptic_start_deg": 30,
        "element": "Earth",
        "modality": "Fixed",
        "month": "May (1-15)",
        "deg_offset": 0,  # 1..15
        "half": "Dark_1_15",
    },
    "f72r1": {
        "sign": "Taurus",
        "sign_idx": 2,
        "ecliptic_start_deg": 30,
        "element": "Earth",
        "modality": "Fixed",
        "month": "May (16-30)",
        "deg_offset": 15,  # 16..30
        "half": "Light_16_30",
    },
    "f72r2": {
        "sign": "Gemini",
        "sign_idx": 3,
        "ecliptic_start_deg": 60,
        "element": "Air",
        "modality": "Mutable",
        "month": "June",
        "deg_offset": 0,
        "half": "Full_30",
    },
    "f72r3": {
        "sign": "Cancer",
        "sign_idx": 4,
        "ecliptic_start_deg": 90,
        "element": "Water",
        "modality": "Cardinal",
        "month": "July",
        "deg_offset": 0,
        "half": "Full_30",
    },
    "f72v3": {
        "sign": "Leo",
        "sign_idx": 5,
        "ecliptic_start_deg": 120,
        "element": "Fire",
        "modality": "Fixed",
        "month": "August",
        "deg_offset": 0,
        "half": "Full_30",
    },
    "f72v2": {
        "sign": "Virgo",
        "sign_idx": 6,
        "ecliptic_start_deg": 150,
        "element": "Earth",
        "modality": "Mutable",
        "month": "September",
        "deg_offset": 0,
        "half": "Full_30",
    },
    "f72v1": {
        "sign": "Libra",
        "sign_idx": 7,
        "ecliptic_start_deg": 180,
        "element": "Air",
        "modality": "Cardinal",
        "month": "October",
        "deg_offset": 0,
        "half": "Full_30",
    },
    "f73r": {
        "sign": "Scorpio",
        "sign_idx": 8,
        "ecliptic_start_deg": 210,
        "element": "Water",
        "modality": "Fixed",
        "month": "November",
        "deg_offset": 0,
        "half": "Full_30",
    },
    "f73v": {
        "sign": "Sagittarius",
        "sign_idx": 9,
        "ecliptic_start_deg": 240,
        "element": "Fire",
        "modality": "Mutable",
        "month": "December",
        "deg_offset": 0,
        "half": "Full_30",
    },
}


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("-", "").strip()
    return t


def parse_clock_angle(comment_str: str):
    """Converts <!HH:MM> clock position (where 00:00/12:00 is top=0°, 03:00=90°, 06:00=180°, 09:00=270°) to degrees."""
    m = re.search(r"(\d{1,2}):(\d{2})", comment_str)
    if not m:
        return None
    hh = int(m.group(1)) % 12
    mm = int(m.group(2))
    deg = (hh * 30.0) + (mm * 0.5)
    return round(deg % 360.0, 1)


def angular_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def parse_zodiac_and_prose():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        folio_index = json.load(f)["folios"]

    zodiac_nymphs = []  # One entry per @Lz/&Lz line (299 total)
    prose_paragraphs = []

    cur_folio = None
    cur_sec = "?"
    cur_lang = "?"
    cur_para_lines = []
    p_idx_by_folio = Counter()

    folio_nymph_counter = Counter()
    folio_ring_counter = Counter()

    line_re = re.compile(r"^<([^.]+)\.([^,>]+),([^>]+)>\s+(.*)$")

    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line or raw_line.startswith("#"):
                continue
            m_f = re.match(r"^<f?([^>]+)>\s*<!(.*)$", raw_line)
            if m_f and "." not in m_f.group(1):
                if cur_para_lines and cur_folio:
                    p_idx_by_folio[cur_folio] += 1
                    prose_paragraphs.append({
                        "folio": cur_folio,
                        "sec": cur_sec,
                        "lang": cur_lang,
                        "p_idx": p_idx_by_folio[cur_folio],
                        "lines": cur_para_lines,
                    })
                    cur_para_lines = []
                cur_folio = "f" + m_f.group(1) if not m_f.group(1).startswith("f") else m_f.group(1)
                meta = folio_index.get(cur_folio, {})
                cur_sec = meta.get("section", "?")
                cur_lang = meta.get("currier_language", "?")
                continue

            m = line_re.match(raw_line)
            if not m:
                continue
            folio, loc_num, tag, rest = m.group(1), m.group(2), m.group(3), m.group(4)
            meta = folio_index.get(folio, {})
            sec = meta.get("section", cur_sec if folio == cur_folio else "?")
            lang = meta.get("currier_language", cur_lang if folio == cur_folio else "?")

            # Extract inline comments for clock angle
            comments = " ".join(re.findall(r"<!([^>]*)>", rest))
            clock_deg = parse_clock_angle(comments)

            has_para_start = "<%>" in rest
            has_para_end = "<$>" in rest

            rest_clean = re.sub(r"<!([^>]*)>", "", rest)
            rest_clean = rest_clean.replace("<%>", "").replace("<$>", "").replace("<->", " ")
            raw_toks = [clean_tok(t) for t in rest_clean.split(".") if clean_tok(t)]
            if not raw_toks:
                continue

            if folio in ZODIAC_FOLIO_META and tag in ("@Lz", "&Lz"):
                if tag == "@Lz":
                    folio_ring_counter[folio] += 1
                folio_nymph_counter[folio] += 1
                zmeta = ZODIAC_FOLIO_META[folio]
                folio_ord = folio_nymph_counter[folio]  # 1..30 (or 1..15)
                sign_deg = zmeta["deg_offset"] + folio_ord  # 1..30 within the sign
                decan = 1 if sign_deg <= 10 else (2 if sign_deg <= 20 else 3)
                ecliptic_lon = (zmeta["ecliptic_start_deg"] + sign_deg) % 360

                # Join multi-token label (e.g. otar.am -> otaram) AND include individual tokens >= 4 chars
                joined_surf = "".join(raw_toks)
                candidate_surfs = [joined_surf] + [t for t in raw_toks if len(t) >= 4 and t != joined_surf]
                tok_canons = []
                for cs in candidate_surfs:
                    c_val = stage3_positional_proclitic_margin(cs)
                    if len(c_val) >= 4 and c_val not in tok_canons:
                        tok_canons.append(c_val)
                primary_surf = joined_surf if len(raw_toks) == 2 and len(raw_toks[1]) <= 3 else raw_toks[0]
                primary_canon = stage3_positional_proclitic_margin(primary_surf)
                pos_sig, env_sig, core_root = extract_core_root_and_envelope(primary_surf, "MEDIAL")

                zodiac_nymphs.append({
                    "folio": folio,
                    "loc": f"{folio}.{loc_num}",
                    "loc_int": int(re.sub(r"\D", "", loc_num) or 0),
                    "tag": tag,
                    "sign": zmeta["sign"],
                    "sign_idx": zmeta["sign_idx"],
                    "element": zmeta["element"],
                    "modality": zmeta["modality"],
                    "half": zmeta["half"],
                    "ring": folio_ring_counter[folio],
                    "folio_ordinal": folio_ord,
                    "sign_degree": sign_deg,
                    "decan": decan,
                    "ecliptic_lon": ecliptic_lon,
                    "clock_deg": clock_deg,
                    "raw_tokens": raw_toks,
                    "canons": tok_canons,
                    "primary_surface": primary_surf,
                    "primary_canon": primary_canon,
                    "core_root": core_root,
                    "env_sig": env_sig,
                })
            elif not (tag.startswith("@L") or tag.startswith("&L") or tag.startswith("@C") or tag.startswith("&C") or tag.startswith("@R") or tag.startswith("&R")):
                if has_para_start and cur_para_lines:
                    p_idx_by_folio[folio] += 1
                    prose_paragraphs.append({
                        "folio": folio,
                        "sec": sec,
                        "lang": lang,
                        "p_idx": p_idx_by_folio[folio],
                        "lines": cur_para_lines,
                    })
                    cur_para_lines = []

                line_objs = []
                for w_i, tok in enumerate(raw_toks):
                    canon = stage3_positional_proclitic_margin(tok)
                    pos_sig, env_sig, core_root = extract_core_root_and_envelope(tok, "MEDIAL")
                    line_objs.append({
                        "folio": folio,
                        "loc": f"{folio}.{loc_num}",
                        "surface": tok,
                        "canon": canon,
                        "core_root": core_root,
                        "env_sig": env_sig,
                        "w_idx": w_i,
                        "line_len": len(raw_toks),
                    })
                cur_para_lines.append(line_objs)

                if has_para_end and cur_para_lines:
                    p_idx_by_folio[folio] += 1
                    prose_paragraphs.append({
                        "folio": folio,
                        "sec": sec,
                        "lang": lang,
                        "p_idx": p_idx_by_folio[folio],
                        "lines": cur_para_lines,
                    })
                    cur_para_lines = []

    if cur_para_lines and cur_folio:
        p_idx_by_folio[cur_folio] += 1
        prose_paragraphs.append({
            "folio": cur_folio,
            "sec": cur_sec,
            "lang": cur_lang,
            "p_idx": p_idx_by_folio[cur_folio],
            "lines": cur_para_lines,
        })

    return zodiac_nymphs, prose_paragraphs


def main():
    random.seed(42)
    zodiac_nymphs, prose_paragraphs = parse_zodiac_and_prose()

    # Global prose canonical counts
    global_prose_counts = Counter()
    for p in prose_paragraphs:
        flat = []
        for l_i, line in enumerate(p["lines"]):
            for t in line:
                t["l_idx"] = l_i
                global_prose_counts[t["canon"]] += 1
                flat.append(t)
        p["flat_tokens"] = flat

    # Map canonical forms to Zodiac nymph entries
    canon_to_nymphs = defaultdict(list)
    for zn in zodiac_nymphs:
        for c in set(zn["canons"]):
            if len(c) >= 3:
                canon_to_nymphs[c].append(zn)

    print(f"Mapped {len(zodiac_nymphs)} Zodiac nymphs across 12 medallions ({len(canon_to_nymphs)} unique canonical stems).")

    # =========================================================================
    # TEST 1: Verify the `f113r` Paragraph 1 Water-Trigon 12° Partile Trine Crib
    # =========================================================================
    cancer_12 = [z for z in zodiac_nymphs if z["loc"] == "f72r3.13"][0]
    scorpio_12 = [z for z in zodiac_nymphs if z["loc"] == "f73r.13"][0]
    water_trine_verification = {
        "cancer_nymph": cancer_12,
        "scorpio_nymph": scorpio_12,
        "same_element_trigon": cancer_12["element"] == scorpio_12["element"] == "Water",
        "same_sign_degree": cancer_12["sign_degree"] == scorpio_12["sign_degree"] == 12,
        "same_folio_locus_number": cancer_12["loc_int"] == scorpio_12["loc_int"] == 13,
        "same_decan": cancer_12["decan"] == scorpio_12["decan"] == 2,
        "ecliptic_longitude_cancer_12": cancer_12["ecliptic_lon"],
        "ecliptic_longitude_scorpio_12": scorpio_12["ecliptic_lon"],
        "exact_ecliptic_angle_deg": angular_diff(cancer_12["ecliptic_lon"], scorpio_12["ecliptic_lon"]),
        "aspect_type": "Partile Water-Trigon Trine (120.0 degrees, 12 deg Cancer <-> 12 deg Scorpio)",
        "global_prose_count_ykolairol": global_prose_counts[cancer_12["primary_canon"]],
        "global_prose_count_oteeosy": global_prose_counts[scorpio_12["primary_canon"]],
    }

    # =========================================================================
    # TEST 2: Internal Zodiac Label Sharing & Morphological Profile by Element/Decan/Half
    # =========================================================================
    # Check all canonical labels that appear >= 2 times inside the Zodiac nymphs themselves
    internal_zodiac_pairs = []
    for c, nlist in canon_to_nymphs.items():
        if len(nlist) >= 2:
            for i in range(len(nlist)):
                for j in range(i + 1, len(nlist)):
                    a, b = nlist[i], nlist[j]
                    sign_dist = min(abs(a["sign_idx"] - b["sign_idx"]), 12 - abs(a["sign_idx"] - b["sign_idx"]))
                    deg_diff = abs(a["sign_degree"] - b["sign_degree"])
                    clock_diff = angular_diff(a["clock_deg"], b["clock_deg"]) if (a["clock_deg"] is not None and b["clock_deg"] is not None) else None
                    internal_zodiac_pairs.append({
                        "canon": c,
                        "nymph_a": f"{a['loc']}({a['sign']} {a['sign_degree']}deg, {a['element']}, R{a['ring']}, {a['primary_surface']})",
                        "nymph_b": f"{b['loc']}({b['sign']} {b['sign_degree']}deg, {b['element']}, R{b['ring']}, {b['primary_surface']})",
                        "same_sign": a["sign"] == b["sign"],
                        "sign_dist": sign_dist,
                        "same_element": a["element"] == b["element"],
                        "same_modality": a["modality"] == b["modality"],
                        "same_decan": a["decan"] == b["decan"],
                        "same_ring": a["ring"] == b["ring"],
                        "deg_diff": deg_diff,
                        "clock_diff": clock_diff,
                    })

    # Also check Dark (f70v1, f71v) vs Light (f71r, f72r1) split medallions in Aries & Taurus
    dark_vs_light_medallions = {}
    for half_type in ("Dark_1_15", "Light_16_30"):
        sub = [z for z in zodiac_nymphs if z["half"] == half_type]
        pfx_c = Counter()
        sfx_c = Counter()
        for z in sub:
            es = z["env_sig"]
            pfx = "y-" if "P:y-" in es else ("o-" if "N:o-" in es else "bare")
            sfx = [p[2:] for p in es.split("|") if p.startswith("S:")][0]
            pfx_c[pfx] += 1
            sfx_c[sfx] += 1
        dark_vs_light_medallions[half_type] = {
            "nymph_count": len(sub),
            "prefix_pct": {k: round(100.0 * v / len(sub), 2) for k, v in pfx_c.most_common()},
            "top_suffix_pct": {k: round(100.0 * v / len(sub), 2) for k, v in sfx_c.most_common(6)},
        }

    # =========================================================================
    # TEST 3: Prose Paragraph Co-Occurring Zodiac Citations — Ecliptic & Degree Synchronization
    # =========================================================================
    # Find all prose paragraphs that contain >= 2 distinct rare Zodiac canons (1 <= global_prose_count <= 10, len >= 4)
    # To avoid ambiguity, focus on canons that map to a unique Zodiac nymph (or take all mapped pairs)
    rare_zodiac_canons_10 = {
        c: nlist for c, nlist in canon_to_nymphs.items()
        if 1 <= global_prose_counts[c] <= 10 and len(c) >= 4 and len(nlist) == 1
    }
    rare_zodiac_canons_5 = {
        c: nlist[0] for c, nlist in rare_zodiac_canons_10.items()
        if global_prose_counts[c] <= 5
    }

    cooccurring_prose_pairs_10 = []
    cooccurring_prose_pairs_5 = []

    for p in prose_paragraphs:
        # Exclude Zodiac & Astro circular text (already excluded, but ensure folio not in ZODIAC_FOLIO_META)
        if p["folio"] in ZODIAC_FOLIO_META:
            continue
        hits_10 = []
        seen_c = set()
        for idx, t in enumerate(p["flat_tokens"]):
            c = t["canon"]
            if c in rare_zodiac_canons_10 and c not in seen_c:
                seen_c.add(c)
                zn = rare_zodiac_canons_10[c][0]
                hits_10.append({
                    "prose_loc": t["loc"],
                    "prose_w_idx": idx,
                    "prose_surface": t["surface"],
                    "canon": c,
                    "global_prose_count": global_prose_counts[c],
                    "zodiac": zn,
                })
        if len(hits_10) >= 2:
            for i in range(len(hits_10)):
                for j in range(i + 1, len(hits_10)):
                    ha, hb = hits_10[i], hits_10[j]
                    za, zb = ha["zodiac"], hb["zodiac"]
                    sign_dist = min(abs(za["sign_idx"] - zb["sign_idx"]), 12 - abs(za["sign_idx"] - zb["sign_idx"]))
                    deg_diff = abs(za["sign_degree"] - zb["sign_degree"])
                    loc_diff = abs(za["loc_int"] - zb["loc_int"])
                    folio_ord_diff = abs(za["folio_ordinal"] - zb["folio_ordinal"])
                    ecliptic_diff = angular_diff(za["ecliptic_lon"], zb["ecliptic_lon"])
                    pair_rec = {
                        "folio": p["folio"],
                        "sec": p["sec"],
                        "p_idx": p["p_idx"],
                        "token_dist": abs(hb["prose_w_idx"] - ha["prose_w_idx"]),
                        "hit_a": f"{ha['prose_loc']}:{ha['prose_surface']} (cnt={ha['global_prose_count']})",
                        "hit_b": f"{hb['prose_loc']}:{hb['prose_surface']} (cnt={hb['global_prose_count']})",
                        "zodiac_a": f"{za['loc']} ({za['sign']} deg={za['sign_degree']}, ord={za['folio_ordinal']}, R{za['ring']}, {za['element']}, {za['primary_surface']})",
                        "zodiac_b": f"{zb['loc']} ({zb['sign']} deg={zb['sign_degree']}, ord={zb['folio_ordinal']}, R{zb['ring']}, {zb['element']}, {zb['primary_surface']})",
                        "same_sign": za["sign"] == zb["sign"],
                        "same_folio": za["folio"] == zb["folio"],
                        "sign_dist": sign_dist,
                        "same_element": za["element"] == zb["element"],
                        "same_modality": za["modality"] == zb["modality"],
                        "same_ring": za["ring"] == zb["ring"],
                        "same_decan": za["decan"] == zb["decan"],
                        "deg_diff": deg_diff,
                        "loc_diff": loc_diff,
                        "folio_ord_diff": folio_ord_diff,
                        "ecliptic_diff": ecliptic_diff,
                        "max_prose_count": max(ha["global_prose_count"], hb["global_prose_count"]),
                    }
                    cooccurring_prose_pairs_10.append(pair_rec)
                    if ha["global_prose_count"] <= 5 and hb["global_prose_count"] <= 5:
                        cooccurring_prose_pairs_5.append(pair_rec)

    # Monte Carlo Permutation Test for `cooccurring_prose_pairs_5` and `cooccurring_prose_pairs_10`:
    # What if the rare Zodiac citations across prose paragraphs were randomly permuted across paragraphs?
    def evaluate_pair_metrics(pairs):
        n = len(pairs)
        if n == 0:
            return {}
        return {
            "total_pairs": n,
            "same_folio": sum(1 for r in pairs if r["same_folio"]),
            "same_sign": sum(1 for r in pairs if r["same_sign"]),
            "contiguous_same_sign_deg_le_2": sum(1 for r in pairs if r["same_sign"] and r["deg_diff"] <= 2),
            "exact_or_adj_deg_diff_le_1": sum(1 for r in pairs if r["deg_diff"] <= 1),
            "exact_or_adj_loc_diff_le_1": sum(1 for r in pairs if r["loc_diff"] <= 1),
            "exact_or_adj_ord_diff_le_1": sum(1 for r in pairs if r["folio_ord_diff"] <= 1),
            "same_element_trigon": sum(1 for r in pairs if r["same_element"]),
            "cross_sign_trine_sign_dist_4": sum(1 for r in pairs if r["sign_dist"] == 4),
            "same_ring": sum(1 for r in pairs if r["same_ring"]),
            "same_decan": sum(1 for r in pairs if r["same_decan"]),
            "mean_deg_diff": round(sum(r["deg_diff"] for r in pairs) / n, 3),
            "mean_loc_diff": round(sum(r["loc_diff"] for r in pairs) / n, 3),
        }

    obs_5 = evaluate_pair_metrics(cooccurring_prose_pairs_5)
    obs_10 = evaluate_pair_metrics(cooccurring_prose_pairs_10)

    # Run 5,000 random pair draws from the pool of prose hit tokens (weighted by their occurrence in multi-hit paragraphs)
    def run_permutation_null(pairs_list, pool_nymphs, n_trials=5000):
        n_pairs = len(pairs_list)
        if n_pairs == 0 or len(pool_nymphs) < 2:
            return {}
        metrics = [
            "same_folio",
            "same_sign",
            "contiguous_same_sign_deg_le_2",
            "exact_or_adj_deg_diff_le_1",
            "exact_or_adj_loc_diff_le_1",
            "exact_or_adj_ord_diff_le_1",
            "same_element_trigon",
            "cross_sign_trine_sign_dist_4",
            "same_ring",
            "same_decan",
        ]
        null_Accum = {m: [] for m in metrics}
        for _ in range(n_trials):
            sim_pairs = []
            for _ in range(n_pairs):
                za, zb = random.sample(pool_nymphs, 2)
                sign_dist = min(abs(za["sign_idx"] - zb["sign_idx"]), 12 - abs(za["sign_idx"] - zb["sign_idx"]))
                deg_diff = abs(za["sign_degree"] - zb["sign_degree"])
                loc_diff = abs(za["loc_int"] - zb["loc_int"])
                folio_ord_diff = abs(za["folio_ordinal"] - zb["folio_ordinal"])
                sim_pairs.append({
                    "same_folio": za["folio"] == zb["folio"],
                    "same_sign": za["sign"] == zb["sign"],
                    "deg_diff": deg_diff,
                    "loc_diff": loc_diff,
                    "folio_ord_diff": folio_ord_diff,
                    "same_element": za["element"] == zb["element"],
                    "sign_dist": sign_dist,
                    "same_ring": za["ring"] == zb["ring"],
                    "same_decan": za["decan"] == zb["decan"],
                })
            ev = evaluate_pair_metrics(sim_pairs)
            for m in metrics:
                null_Accum[m].append(ev[m])

        obs_ev = evaluate_pair_metrics(pairs_list)
        summary = {}
        for m in metrics:
            vals = null_Accum[m]
            mean_v = sum(vals) / len(vals)
            std_v = math.sqrt(sum((x - mean_v) ** 2 for x in vals) / len(vals)) or 1e-9
            obs_v = obs_ev[m]
            z = (obs_v - mean_v) / std_v
            p_val = sum(1 for x in vals if x >= obs_v) / len(vals)
            summary[m] = {
                "observed": obs_v,
                "expected_mean": round(mean_v, 2),
                "expected_std": round(std_v, 2),
                "enrichment_ratio": round(obs_v / mean_v, 2) if mean_v > 0 else None,
                "z_score": round(z, 2),
                "p_value": round(p_val, 4),
            }
        return summary

    pool_5 = list(rare_zodiac_canons_5.values())
    pool_10 = [v[0] for v in rare_zodiac_canons_10.values()]
    perm_5 = run_permutation_null(cooccurring_prose_pairs_5, pool_5, n_trials=5000)
    perm_10 = run_permutation_null(cooccurring_prose_pairs_10, pool_10, n_trials=5000)

    # Sort cooccurring_prose_pairs_5 by degree synchronization / contiguous arc / trine
    cooccurring_prose_pairs_5.sort(key=lambda x: (x["deg_diff"], x["loc_diff"], x["max_prose_count"]))

    # =========================================================================
    # TEST 4: Starred Recipes (`f103r–f116r`) Dominant Astrological Sign & Trigon Profile per Folio
    # =========================================================================
    starred_folio_zodiac_profile = {}
    for p in prose_paragraphs:
        if p["sec"] != "Starred Recipes":
            continue
        fol = p["folio"]
        if fol not in starred_folio_zodiac_profile:
            starred_folio_zodiac_profile[fol] = {
                "sign_counts": Counter(),
                "element_counts": Counter(),
                "decan_counts": Counter(),
                "rare_hits": [],
            }
        for t in p["flat_tokens"]:
            c = t["canon"]
            if c in rare_zodiac_canons_10:
                zn = rare_zodiac_canons_10[c][0]
                starred_folio_zodiac_profile[fol]["sign_counts"][zn["sign"]] += 1
                starred_folio_zodiac_profile[fol]["element_counts"][zn["element"]] += 1
                starred_folio_zodiac_profile[fol]["decan_counts"][f"Decan_{zn['decan']}"] += 1
                if global_prose_counts[c] <= 5:
                    starred_folio_zodiac_profile[fol]["rare_hits"].append(
                        f"{t['loc']}:{t['surface']} -> {zn['loc']}({zn['sign']} {zn['sign_degree']}deg, {zn['element']})"
                    )

    starred_profile_clean = {}
    for fol, d in sorted(starred_folio_zodiac_profile.items()):
        starred_profile_clean[fol] = {
            "total_rare_10_zodiac_hits": sum(d["sign_counts"].values()),
            "top_signs": dict(d["sign_counts"].most_common(4)),
            "elements": dict(d["element_counts"].most_common()),
            "decans": dict(d["decan_counts"].most_common()),
            "ultra_rare_5_hits": d["rare_hits"][:10],
        }

    out = {
        "summary": {
            "total_zodiac_medallions": 12,
            "total_zodiac_signs": 10,
            "total_labeled_nymphs": len(zodiac_nymphs),
            "unique_zodiac_canons": len(canon_to_nymphs),
            "unambiguous_rare_10_zodiac_canons": len(rare_zodiac_canons_10),
            "unambiguous_rare_5_zodiac_canons": len(rare_zodiac_canons_5),
        },
        "water_trine_f113r_verification": water_trine_verification,
        "dark_vs_light_split_medallions": dark_vs_light_medallions,
        "internal_zodiac_duplicate_label_pairs": internal_zodiac_pairs,
        "prose_cooccurrence_permutation_rare_5": perm_5,
        "prose_cooccurrence_permutation_rare_10": perm_10,
        "top_cooccurring_prose_pairs_rare_5": cooccurring_prose_pairs_5[:35],
        "starred_recipes_folio_zodiac_profile": starred_profile_clean,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"\nSaved Attack 10 analysis to {OUT_JSON}")
    print("\n--- TEST 1: WATER-TRIGON 12° PARTILE TRINE VERIFICATION (f113r.1..3) ---")
    print(json.dumps({
        k: v for k, v in water_trine_verification.items()
        if k not in ("cancer_nymph", "scorpio_nymph")
    }, indent=2))

    print("\n--- TEST 2: DARK (1-15 deg) VS LIGHT (16-30 deg) SPLIT MEDALLIONS (Aries & Taurus) ---")
    print(json.dumps(dark_vs_light_medallions, indent=2))

    print("\n--- TEST 3: PROSE CO-OCCURRING ZODIAC PAIRS PERMUTATION (RARE <= 5) ---")
    print(json.dumps(perm_5, indent=2))

    print("\n--- TEST 3B: PROSE CO-OCCURRING ZODIAC PAIRS PERMUTATION (RARE <= 10) ---")
    print(json.dumps(perm_10, indent=2))

    print("\n--- TOP 15 CO-OCCURRING RARE (<= 5) ZODIAC PAIRS IN PROSE ---")
    for r in cooccurring_prose_pairs_5[:15]:
        print(
            f"  {r['folio']} P{r['p_idx']} (dist={r['token_dist']}): "
            f"{r['hit_a']} + {r['hit_b']}  ==>  {r['zodiac_a']}  <->  {r['zodiac_b']} "
            f"[deg_diff={r['deg_diff']}, loc_diff={r['loc_diff']}, same_sign={r['same_sign']}, same_elem={r['same_element']}]"
        )


if __name__ == "__main__":
    main()
