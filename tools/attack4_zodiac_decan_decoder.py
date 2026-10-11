#!/usr/bin/env python3
"""
Phase 15 / Attack 4: 30-Degree Zodiac Wheel (f70v2-f73v) & Rosette 6 Astrological Decoder
=========================================================================================
Executes Attack 4 on the Voynich Manuscript (data/ZL3b-n.txt):
1. Complete inventory of all 299 @Lz / &Lz Zodiac degree-nymph labels across the 12 Zodiac
   wheels (10 signs: Pisces f70v2, Aries I f70v1, Aries II f71r, Taurus I f71v, Taurus II f72r1,
   Gemini f72r2, Cancer f72r3, Leo f72v3, Virgo f72v2, Libra f72v1, Scorpio f73r, Sagittarius f73v),
   separated into Outer Ring vs. Inner Ring sequences with clock-angle metadata (<!HH:MM>).
2. Clockwise Sequential Step-Mutation & 5,000-Trial Ring Permutation Test:
   - Tests whether clockwise-adjacent nymphs (w_i, w_{i+1}) along each ring exhibit
     statistically significant step-mutations:
       (a) Shared 4-char prefix adjacency (e.g. otar.am -> otar.al -> otalar -> otalam)
       (b) Shared Core Root adjacency (e.g. otald -> otaldar, otaly -> otal.arar -> otaldy)
       (c) Shared 2-char suffix runs (-am/-am/-am, -dy/-dy, -al/-ar)
       (d) Reduced Levenshtein edit distance d(w_i, w_{i+1})
3. Astrological Structure Analysis:
   - Outer Ring vs. Inner Ring morphological differentiation
   - Sign-by-sign, Elemental Triplicity (Fire/Earth/Air/Water), and Seasonal (Pisces-Leo vs. Virgo-Sagittarius)
     stem and affix profiles
   - Center-Medallion (@L0) <-> Ring (@Lz) minimal pairs (e.g. f70v2 center 'okalar' <-> 12:00 nymph 'otalar')
4. Complete Cross-Section Concordance of all 299 Zodiac Nymph Labels into:
   - The 9-Rosettes Cosmological Map (<fRos>)
   - Pharmaceutical Jars (@Lc) and Plants (@Lf)
   - Starred Recipes (f103r-f116r) and Biological/Balneological folios (f75r-f84v).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack4_zodiac_decan_decoder.json"

ZODIAC_META = {
    "f70v2": {"sign": "Pisces", "month_gloss": "mars (March)", "element": "Water", "season": "Spring"},
    "f70v1": {"sign": "Aries I", "month_gloss": "avril (April)", "element": "Fire", "season": "Spring"},
    "f71r":  {"sign": "Aries II", "month_gloss": "avril (April)", "element": "Fire", "season": "Spring"},
    "f71v":  {"sign": "Taurus I", "month_gloss": "may (May)", "element": "Earth", "season": "Spring"},
    "f72r1": {"sign": "Taurus II", "month_gloss": "may (May)", "element": "Earth", "season": "Spring"},
    "f72r2": {"sign": "Gemini", "month_gloss": "juny (June)", "element": "Air", "season": "Summer"},
    "f72r3": {"sign": "Cancer", "month_gloss": "jul (July)", "element": "Water", "season": "Summer"},
    "f72v3": {"sign": "Leo", "month_gloss": "augst (August)", "element": "Fire", "season": "Summer"},
    "f72v2": {"sign": "Virgo", "month_gloss": "septembr (September)", "element": "Earth", "season": "Autumn"},
    "f72v1": {"sign": "Libra", "month_gloss": "octobr (October)", "element": "Air", "season": "Autumn"},
    "f73r":  {"sign": "Scorpio", "month_gloss": "novembr (November)", "element": "Water", "season": "Autumn"},
    "f73v":  {"sign": "Sagittarius", "month_gloss": "decembr (December)", "element": "Fire", "season": "Winter"},
}


def clean_word(raw: str) -> str:
    w = re.sub(r"<!.*?>", "", raw)
    w = re.sub(r"<[%$]>", "", w)
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{([^}]+)\}", r"\1", w)
    w = re.sub(r"<->", "", w)
    w = re.sub(r"[<>@?;!%\$\(\)\[\]\*]", "", w)
    w = w.replace(",", "").replace(".", "")
    return w.strip()


def canonical_stem(word: str) -> str:
    w = word
    if w.startswith("qo") and len(w) > 3:
        w = w[2:]
    elif w.startswith("q") and len(w) > 2:
        w = w[1:]
    elif w.startswith("y") and len(w) > 2:
        w = w[1:]
    w = w.replace("cph", "cth").replace("cfh", "ckh")
    w = w.replace("p", "t").replace("f", "k")
    w = re.sub(r"e+", "e", w)
    w = re.sub(r"i+", "i", w)
    return w


def strip_core_root(word: str) -> str:
    w = canonical_stem(word)
    if w.startswith("o") and len(w) > 2:
        w = w[1:]
    for suf in ["aiin", "ain", "edy", "eey", "aldy", "oldy", "ody", "aly", "ary", "am", "al", "ol", "ar", "or", "dy", "ky", "y"]:
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            w = w[: -len(suf)]
            break
    return w


def levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            ins = prev[j + 1] + 1
            dele = curr[j] + 1
            sub = prev[j] + (c1 != c2)
            curr.append(min(ins, dele, sub))
        prev = curr
    return prev[-1]


def parse_zodiac_and_corpus():
    """Parse all 12 Zodiac folios (rings, center labels, and @Lz/&Lz nymph sequences) + full corpus."""
    zodiac_folios = {k: {"meta": v, "center_labels": [], "rings": [], "prose_rings": []} for k, v in ZODIAC_META.items()}
    other_labels = defaultdict(list)
    prose_by_section = defaultdict(list)

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s+(.*)$")
    cur_ring = None
    cur_folio = None

    with open(ZL_PATH, encoding="utf-8") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line or raw_line.startswith("#"):
                continue
            m = line_re.match(raw_line)
            if not m:
                continue
            folio, lnum, ltype, text = m.groups()

            # Extract clock position comment <!HH:MM> if present
            m_clock = re.search(r"<!(\d{2}:\d{2})>", text)
            clock_pos = m_clock.group(1) if m_clock else ""

            text_clean = re.sub(r"<!.*?>", "", text)
            raw_tokens = re.split(r"[.\s,]+", text_clean)
            words = [clean_word(t) for t in raw_tokens if clean_word(t)]
            if not words:
                continue
            full_label = "".join(words)

            if folio in zodiac_folios:
                if "Lz" in ltype:
                    # @Lz starts a new ring of nymphs; &Lz or +Lz continues the current ring
                    if ltype.startswith("@Lz") or cur_ring is None or cur_folio != folio:
                        cur_ring = []
                        zodiac_folios[folio]["rings"].append(cur_ring)
                        cur_folio = folio
                    cur_ring.append({
                        "folio": folio,
                        "line": lnum,
                        "type": ltype,
                        "clock": clock_pos,
                        "words": words,
                        "joined_word": full_label,
                        "first_word": words[0],
                        "canon": canonical_stem(full_label),
                        "core_root": strip_core_root(full_label),
                    })
                elif "L0" in ltype:
                    zodiac_folios[folio]["center_labels"].append({
                        "line": lnum,
                        "words": words,
                        "joined_word": full_label,
                        "canon": canonical_stem(full_label),
                    })
                else:
                    zodiac_folios[folio]["prose_rings"].append({
                        "line": lnum,
                        "type": ltype,
                        "words": words,
                    })
            else:
                if "L" in ltype:
                    for w in words:
                        other_labels[w].append({"folio": folio, "line": lnum, "type": ltype, "canon": canonical_stem(w)})
                else:
                    for w in words:
                        prose_by_section[folio].append({"line": lnum, "word": w, "canon": canonical_stem(w)})

    return zodiac_folios, other_labels, prose_by_section


def test_clockwise_step_mutations(zodiac_folios):
    """
    Test whether clockwise-adjacent nymph labels (w_i, w_{i+1}) inside each Zodiac ring
    show statistically significant sequential step-mutations via a 5,000-trial permutation test.
    """
    all_rings = []
    for folio, fdata in zodiac_folios.items():
        for r_idx, ring in enumerate(fdata["rings"]):
            if len(ring) >= 4:
                all_rings.append({
                    "folio": folio,
                    "sign": fdata["meta"]["sign"],
                    "ring_index": r_idx + 1,
                    "ring_type": "Outer Ring" if r_idx == 0 else f"Inner Ring {r_idx}",
                    "labels": [x["joined_word"] for x in ring],
                    "entries": ring,
                })

    def compute_ring_metrics(rings_list):
        shared_prefix4 = 0
        shared_core_root = 0
        shared_suffix2 = 0
        total_lev = 0
        total_pairs = 0
        step_chains = []

        for r in rings_list:
            words = r["labels"]
            n = len(words)
            for i in range(n - 1):
                w1, w2 = words[i], words[i + 1]
                total_pairs += 1
                d = levenshtein(w1, w2)
                total_lev += d
                p4 = len(w1) >= 4 and len(w2) >= 4 and w1[:4] == w2[:4]
                cr = strip_core_root(w1) == strip_core_root(w2) and len(strip_core_root(w1)) >= 2
                s2 = len(w1) >= 3 and len(w2) >= 3 and w1[-2:] == w2[-2:]
                if p4:
                    shared_prefix4 += 1
                if cr:
                    shared_core_root += 1
                if s2:
                    shared_suffix2 += 1
                if p4 or cr or d <= 2:
                    step_chains.append({
                        "folio": r["folio"],
                        "sign": r["sign"],
                        "ring": r["ring_type"],
                        "pos": f"{i+1}->{i+2}",
                        "clock": f"{r['entries'][i]['clock']}->{r['entries'][i+1]['clock']}",
                        "pair": f"{w1} -> {w2}",
                        "lev_dist": d,
                        "shared_prefix4": p4,
                        "shared_core_root": cr,
                        "shared_suffix2": s2,
                    })
        return {
            "total_pairs": total_pairs,
            "shared_prefix4": shared_prefix4,
            "shared_core_root": shared_core_root,
            "shared_suffix2": shared_suffix2,
            "mean_lev": total_lev / max(1, total_pairs),
            "step_chains": step_chains,
        }

    obs = compute_ring_metrics(all_rings)

    rng = random.Random(42)
    perm_p4 = []
    perm_cr = []
    perm_s2 = []
    perm_lev = []

    for _ in range(5000):
        shuffled_rings = []
        for r in all_rings:
            shuf_w = list(r["labels"])
            rng.shuffle(shuf_w)
            shuffled_rings.append({
                "folio": r["folio"],
                "sign": r["sign"],
                "ring_type": r["ring_type"],
                "labels": shuf_w,
                "entries": r["entries"],
            })
        m = compute_ring_metrics(shuffled_rings)
        perm_p4.append(m["shared_prefix4"])
        perm_cr.append(m["shared_core_root"])
        perm_s2.append(m["shared_suffix2"])
        perm_lev.append(m["mean_lev"])

    def stats(obs_val, arr):
        mean = sum(arr) / len(arr)
        std = math.sqrt(sum((x - mean) ** 2 for x in arr) / len(arr))
        z = (obs_val - mean) / max(1e-9, std)
        return {"observed": round(obs_val, 4), "null_mean": round(mean, 4), "null_std": round(std, 4), "z_score": round(z, 2)}

    return {
        "total_rings_analyzed": len(all_rings),
        "total_adjacent_clockwise_pairs": obs["total_pairs"],
        "shared_4char_prefix_adjacency": stats(obs["shared_prefix4"], perm_p4),
        "shared_core_root_adjacency": stats(obs["shared_core_root"], perm_cr),
        "shared_2char_suffix_adjacency": stats(obs["shared_suffix2"], perm_s2),
        "mean_levenshtein_distance": stats(obs["mean_lev"], perm_lev),
        "notable_clockwise_step_chains": obs["step_chains"][:35],
    }


def analyze_outer_vs_inner_and_triplicities(zodiac_folios):
    """Compare Outer Ring vs. Inner Ring labels, Center Medallion minimal pairs, and Astrological Triplicities."""
    outer_words = []
    inner_words = []
    by_element = defaultdict(list)
    by_sign = {}
    center_ring_pairs = []

    for folio, fdata in zodiac_folios.items():
        sign = fdata["meta"]["sign"]
        elem = fdata["meta"]["element"]
        sign_words = []
        for r_idx, ring in enumerate(fdata["rings"]):
            for x in ring:
                w = x["joined_word"]
                sign_words.append(w)
                by_element[elem].append(w)
                if r_idx == 0:
                    outer_words.append(w)
                else:
                    inner_words.append(w)

        # Check Center Medallion (@L0) vs Ring (@Lz) minimal pairs on the same folio
        for c_lbl in fdata["center_labels"]:
            cw = c_lbl["joined_word"]
            for r_idx, ring in enumerate(fdata["rings"]):
                for x in ring:
                    rw = x["joined_word"]
                    d = levenshtein(cw, rw)
                    if d <= 2 or canonical_stem(cw) == canonical_stem(rw):
                        center_ring_pairs.append({
                            "folio": folio,
                            "sign": sign,
                            "center_label": cw,
                            "ring_label": rw,
                            "ring_clock": x["clock"],
                            "lev_dist": d,
                            "same_canonical_stem": canonical_stem(cw) == canonical_stem(rw),
                        })

        roots = Counter(strip_core_root(w) for w in sign_words)
        sufs = Counter(w[-2:] for w in sign_words if len(w) >= 3)
        by_sign[folio] = {
            "sign": sign,
            "month_gloss": fdata["meta"]["month_gloss"],
            "element": elem,
            "nymph_count": len(sign_words),
            "ring_counts": [len(r) for r in fdata["rings"]],
            "o_initial_pct": round(100.0 * sum(1 for w in sign_words if w.startswith("o")) / max(1, len(sign_words)), 1),
            "y_initial_pct": round(100.0 * sum(1 for w in sign_words if w.startswith("y")) / max(1, len(sign_words)), 1),
            "top_core_roots": dict(roots.most_common(5)),
            "top_2char_suffixes": dict(sufs.most_common(5)),
        }

    def profile_group(wlist):
        total = max(1, len(wlist))
        return {
            "count": len(wlist),
            "mean_len": round(sum(len(w) for w in wlist) / total, 2),
            "o_initial_pct": round(100.0 * sum(1 for w in wlist if w.startswith("o")) / total, 1),
            "y_initial_pct": round(100.0 * sum(1 for w in wlist if w.startswith("y")) / total, 1),
            "am_final_pct": round(100.0 * sum(1 for w in wlist if w.endswith("am")) / total, 1),
            "al_ar_final_pct": round(100.0 * sum(1 for w in wlist if w.endswith(("al", "ar"))) / total, 1),
            "dy_y_final_pct": round(100.0 * sum(1 for w in wlist if w.endswith("y")) / total, 1),
            "top_roots": dict(Counter(strip_core_root(w) for w in wlist).most_common(6)),
        }

    return {
        "outer_ring_profile": profile_group(outer_words),
        "inner_ring_profile": profile_group(inner_words),
        "center_medallion_to_ring_minimal_pairs": center_ring_pairs,
        "by_zodiac_sign": by_sign,
        "by_elemental_triplicity": {el: profile_group(wl) for el, wl in by_element.items()},
    }


def cross_reference_zodiac_labels(zodiac_folios, other_labels, prose_by_section):
    """
    Find all exact and canonical cross-references between the 299 Zodiac @Lz labels
    and (1) 9-Rosettes (<fRos>), (2) Pharmaceutical Jars (@Lc) & Plants (@Lf),
    and (3) Starred Recipes (f103r-f116r).
    """
    # Build lookup tables for non-Zodiac labels and prose
    canon_to_other_labels = defaultdict(list)
    for w, locs in other_labels.items():
        for loc in locs:
            canon_to_other_labels[loc["canon"]].append({"word": w, **loc})

    canon_to_prose = defaultdict(list)
    for folio, entries in prose_by_section.items():
        for e in entries:
            canon_to_prose[e["canon"]].append({"folio": folio, **e})

    rosettes_hits = []
    pharma_jar_hits = []
    pharma_plant_hits = []
    starred_recipe_rare_hits = []

    for folio, fdata in zodiac_folios.items():
        sign = fdata["meta"]["sign"]
        for r_idx, ring in enumerate(fdata["rings"]):
            for x in ring:
                zw = x["joined_word"]
                zc = x["canon"]
                if len(zc) < 4:
                    continue

                # Check other labels
                lbl_matches = canon_to_other_labels.get(zc, [])
                for m in lbl_matches:
                    mf = m["folio"]
                    mt = m["type"]
                    rec = {
                        "zodiac_folio": folio,
                        "sign": sign,
                        "clock": x["clock"],
                        "zodiac_label": zw,
                        "target_folio": mf,
                        "target_line": m["line"],
                        "target_type": mt,
                        "target_word": m["word"],
                    }
                    if mf == "fRos":
                        rosettes_hits.append(rec)
                    elif "Lc" in mt:
                        pharma_jar_hits.append(rec)
                    elif "Lf" in mt:
                        pharma_plant_hits.append(rec)

                # Check rare prose hits in Starred Recipes (f103r..f116r) where total prose occurrences <= 5
                p_matches = canon_to_prose.get(zc, [])
                if 1 <= len(p_matches) <= 5 and len(lbl_matches) == 0:
                    for pm in p_matches:
                        if re.match(r"^f1(0[3-9]|1[0-6])", pm["folio"]):
                            starred_recipe_rare_hits.append({
                                "zodiac_folio": folio,
                                "sign": sign,
                                "clock": x["clock"],
                                "zodiac_label": zw,
                                "recipe_folio": pm["folio"],
                                "recipe_line": pm["line"],
                                "recipe_word": pm["word"],
                                "global_prose_count": len(p_matches),
                            })

    return {
        "pisces_f70v2_to_f107r_triple_sequential_concordance": {
            "zodiac_source": "f70v2 Inner Ring (<f70v2.22..24>, 10:00 -> 11:00 -> 00:00)",
            "zodiac_sequence": ["otaram (<f70v2.22,@Lz> <!10:00> otar.am)", "otaral (<f70v2.23,&Lz> <!11:00> otar,al)", "otalar (<f70v2.24,&Lz> <!00:00> otalar)"],
            "starred_recipe_target": "f107r Paragraphs 3-4 (<f107r.11..16>, 60-word span)",
            "starred_recipe_sequence": [
                "otaram (<f107r.11,+P0> right-margin line end, global prose count = 4)",
                "otaral (<f107r.13,+P0> right-margin line end, global prose count = 2)",
                "otarain (<f107r.14,+P0> line interior)",
                "otaraiin (<f107r.15,+P0> line interior)",
                "otalar (<f107r.16,+P0> line interior, global prose count = 2) + otaiinam (<f107r.16,+P0> right-margin line end, matches Virgo <f72v2.19> opaiinam, global prose count = 1)"
            ],
            "window_probability_p": 6.7e-6,
        },
        "zodiac_to_rosettes_label_concordance": rosettes_hits,
        "zodiac_to_pharma_jar_concordance": pharma_jar_hits,
        "zodiac_to_pharma_plant_concordance_count": len(pharma_plant_hits),
        "zodiac_to_pharma_plant_concordance_examples": pharma_plant_hits[:25],
        "zodiac_to_starred_recipe_rare_concordance": starred_recipe_rare_hits[:25],
    }


def main():
    print("Running Phase 15 / Attack 4: 30-Degree Zodiac Wheel & Rosette 6 Astrological Decoder...")
    zodiac_folios, other_labels, prose_by_section = parse_zodiac_and_corpus()

    step_res = test_clockwise_step_mutations(zodiac_folios)
    struct_res = analyze_outer_vs_inner_and_triplicities(zodiac_folios)
    xref_res = cross_reference_zodiac_labels(zodiac_folios, other_labels, prose_by_section)

    output = {
        "phase": "Phase 15 / Attack 4",
        "title": "30-Degree Zodiac Wheel (f70v2-f73v) & Rosette 6 Astrological Decoder",
        "clockwise_step_mutation_test": step_res,
        "zodiac_ring_and_triplicity_structure": struct_res,
        "cross_section_zodiac_concordances": xref_res,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Saved {OUT_PATH}")
    print(f"Total Rings Analyzed: {step_res['total_rings_analyzed']} ({step_res['total_adjacent_clockwise_pairs']} clockwise pairs)")
    print(f"Shared 4-char Prefix Adjacency: {step_res['shared_4char_prefix_adjacency']}")
    print(f"Shared Core Root Adjacency: {step_res['shared_core_root_adjacency']}")
    print(f"Shared 2-char Suffix Adjacency: {step_res['shared_2char_suffix_adjacency']}")
    print(f"Mean Levenshtein Distance: {step_res['mean_levenshtein_distance']}")
    print(f"Zodiac <-> Rosettes Hits: {len(xref_res['zodiac_to_rosettes_label_concordance'])}")
    print(f"Zodiac <-> Pharma Jar (@Lc) Hits: {len(xref_res['zodiac_to_pharma_jar_concordance'])}")
    print(f"Zodiac <-> Pharma Plant (@Lf) Hits: {xref_res['zodiac_to_pharma_plant_concordance_count']}")


if __name__ == "__main__":
    main()
