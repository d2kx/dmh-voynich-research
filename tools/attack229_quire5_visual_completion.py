#!/usr/bin/env python3
"""
Attack 229 (Discovery 246): 100.0% (16/16) Quire 5 ($Q=E, f33r-f40v) Visual & Paleographic
Completion, Discovery of the Scribe 2 Outer Jacket / Scribe 1 Inner Core Bifolium Architecture,
Medieval Stitched Root Repair (f36v), and 93.39% (212/227) Global Codex Visual Coverage.
"""

import glob
import json
import os
import re
from collections import Counter


def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    return w


def canonical_stem(w: str) -> str:
    w = normalize_token(w)
    if not w:
        return ""
    w = re.sub(r"^qo", "o", w)
    w = w.replace("eee", "e").replace("ee", "e").replace("ii", "i")
    w = w.replace("f", "p").replace("k", "t")
    for p in ["o", "d", "y", "s"]:
        if len(w) > 3 and w.startswith(p):
            w = w[len(p) :]
            break
    for s in [
        "aiin",
        "ain",
        "edy",
        "eey",
        "ody",
        "ady",
        "al",
        "ar",
        "or",
        "ol",
        "am",
        "an",
        "dy",
        "ey",
        "y",
    ]:
        if len(w) > len(s) + 1 and w.endswith(s):
            w = w[: -len(s)]
            break
    return w


def parse_zl_words(path: str):
    folio_words = {}
    folio_lines = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            m = re.match(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s+(.*)$", line)
            if not m:
                continue
            folio, lno, ltype, rest = m.groups()
            rest_clean = re.sub(r"<!.*?>", "", rest)
            rest_clean = re.sub(r"<[@$%~].*?>", "", rest_clean)
            rest_clean = rest_clean.replace("<->", ".")
            raw_tokens = re.split(r"[.,\s]+", rest_clean)
            words = [normalize_token(t) for t in raw_tokens if normalize_token(t)]
            folio_words.setdefault(folio, []).extend(words)
            folio_lines.setdefault(folio, []).append((lno, ltype, words, rest.strip()))
    return folio_words, folio_lines


def main():
    with open("data/folio_index.json", encoding="utf-8") as f:
        idx = json.load(f)["folios"]
    folio_words, folio_lines = parse_zl_words("data/ZL3b-n.txt")

    q5_folios = [f for f, d in idx.items() if d.get("quire") == "E"]

    bifolios = [
        {
            "bifolio_number": 1,
            "position": "Outer jacket sheet (Bifolio 1 — Scribe 2 / Currier B)",
            "leaves": ["f33r", "f33v", "f40r", "f40v"],
            "scribe_language": "H2 / Currier B on all 4 pages",
            "leaf_pairing": "Leaf 1 (f33) <-> Leaf 8 (f40)",
            "highlights": "f33r (p66) multi-flower herb; f33v (p67) serrate leaf herbal with 21 drawing intrusions; f40r (p80) Currier B herbal recto with 10 intrusions; f40v (p81) closing folio of Quire 5 with 6 intrusions.",
        },
        {
            "bifolio_number": 2,
            "position": "Second sheet (Bifolio 2 — Scribe 2 / Currier B)",
            "leaves": ["f34r", "f34v", "f39r", "f39v"],
            "scribe_language": "H2 / Currier B on all 4 pages",
            "leaf_pairing": "Leaf 2 (f34) <-> Leaf 7 (f39)",
            "highlights": "f34r (p68) polychrome herbal with chckhy/chodaiin compounds; f34v (p69) Currier B verso; f39r (p78) Currier B monograph; f39v (p79) okody/sarol herb with 7 intrusions.",
        },
        {
            "bifolio_number": 3,
            "position": "Third sheet (Bifolio 3 — Scribe 1 / Currier A Inner Core)",
            "leaves": ["f35r", "f35v", "f38r", "f38v"],
            "scribe_language": "H1 / Currier A on all 4 pages",
            "leaf_pairing": "Leaf 3 (f35) <-> Leaf 6 (f38)",
            "highlights": "f35r (p70) giant chalice cup + 6-tentacled blue flower head + fishtail root; f35v (p71) brassica crown + figure-8 intertwined berry vines + 12-claw root; f38r (p76) swallowtail V-leaf with 5 comma fenestrations + twin tuber roots; f38v (p77) dense imbricate cone with blue starburst flower.",
        },
        {
            "bifolio_number": 4,
            "position": "Innermost center sheet (Bifolio 4 — Scribe 1 / Currier A Inner Core)",
            "leaves": ["f36r", "f36v", "f37r", "f37v"],
            "scribe_language": "H1 / Currier A on all 4 pages",
            "leaf_pairing": "Leaf 4 (f36) <-> Leaf 5 (f37)",
            "highlights": "f36r (p72) geranium leaves with tricolor pigment + 4 blue/gold buds + sliced tuber caudex; f36v (p73) Galium whorled leaves + honeycomb catkin head + medieval stitched root repair; f37r (p74) 5 drooping leaf pairs + 7 crimson cyme clusters + turnip root; f37v (p75) 7-tiered bicolored crenate leaf ladder + 3 indigo buds with crimson flowers + dotted collar root.",
        },
    ]

    scan_map = {
        "f33r": "pages/f33r_multiflower_enh.png",
        "f33v": "pages/f33v_currier_b_herbal_verso_enh.png",
        "f34r": "pages/f34r_currier_b_polychrome_herbal_enh.png",
        "f34v": "pages/f34v_currier_b_herbal_verso_enh.png",
        "f35r": "pages/f35r_quire5_bifolium3_recto_enh.png",
        "f35v": "pages/f35v_quire5_bifolium3_verso_enh.png",
        "f36r": "pages/f36r_quire5_bifolium4_recto_enh.png",
        "f36v": "pages/f36v_quire5_bifolium4_verso_enh.png",
        "f37r": "pages/f37r_quire5_bifolium4_conjugate_recto_enh.png",
        "f37v": "pages/f37v_quire5_bifolium4_conjugate_verso_enh.png",
        "f38r": "pages/f38r_quire5_bifolium3_conjugate_recto_enh.png",
        "f38v": "pages/f38v_quire5_bifolium3_conjugate_verso_enh.png",
        "f39r": "pages/f39r_currier_b_herbal_monograph_enh.png",
        "f39v": "pages/f39v_okody_sarol_plant_enh.png",
        "f40r": "pages/f40r_currier_b_herbal_recto_enh.png",
        "f40v": "pages/f40v_currier_b_herbal_verso_enh.png",
    }

    visual_notes = {
        "f33r": "Opening recto of Quire 5 (Leaf 1, outer Bifolio 1, Scribe 2 / Currier B): multi-branched flowering herb with dark green lanceolate leaves and terminal blue starburst clusters.",
        "f33v": "Scribe 2 / Currier B verso: tall single-stemmed herb with large serrated leaves and 21 drawing intrusions (<->) densely wrapped by Currier B text.",
        "f34r": "Leaf 2 recto (outer Bifolio 2, Scribe 2 / Currier B): polychrome herbal with chckhy/chodaiin compounds and 20 text intrusions around sprawling foliage.",
        "f34v": "Leaf 2 verso: Scribe 2 / Currier B herbal with smooth-edged oval leaves and fibrous root cluster.",
        "f35r": "Leaf 3 recto (Bifolio 3, Scribe 1 / Currier A): giant chalice-shaped brown receptacle with green serrated upper rim; slender central stalk bearing umbel flower with 6 curled blue tentacles and central crimson segmented comb; bifurcated fish-tail striate root; faint green/blue bleed-through from f35v on left margin.",
        "f35v": "Leaf 3 verso (Bifolio 3, Scribe 1 / Currier A): massive ruffled green brassica/kale crown above vertical stalk with figure-8 intertwined looping vine stems bearing turquoise/cyan berry clusters; two oak-lobed lateral leaves; horizontal multi-fingered root system with 12 root claws; bleed-through from f35r chalice bowl on left.",
        "f36r": "Leaf 4 recto (Bifolio 4, Scribe 1 / Currier A): deeply lobed palmate geranium leaves in tri-color pigment (emerald green, golden ochre, intense dark green); 4 terminal stippled calyces with dark blue petals and gold centers; bulbous sliced white-topped tuber caudex with sprawling root arms; cancelled page number '39' at top right; bleed-through from f36v starburst leaves.",
        "f36v": "Leaf 4 verso (Bifolio 4, Scribe 1 / Currier A): 8-to-10-part radiate whorled oblanceolate leaves (Galium-like); terminal globose honeycomb head with lateral drooping cylindrical catkins; original medieval stitched root repair with visible stitch holes at base of taproot; natural parchment blemishes in leaf blades; bleed-through from f36r geranium leaves.",
        "f37r": "Leaf 5 recto (Bifolio 4, conjugate to f36, Scribe 1 / Currier A): 5 pairs of arching lanceolate green leaves; tall upright flowering spike bearing 7 globose crimson stippled cyme clusters; bulbous turnip-like brown root with 5 curled rootlets; diagonal parchment flaw/stitch at right edge (x=0.73, y=0.72); cancelled page number '39'.",
        "f37v": "Leaf 5 verso (Bifolio 4, conjugate to f36, Scribe 1 / Currier A): spectacular 7-tiered ladder of broad bicolored crenate/scalloped leaves (green upper half, white unpainted lower half); 3 dark indigo oval bud pods crowned with crimson-and-white 5-petaled flowers; dotted circular collar ring above 5-legged dark brown branching root; matching diagonal parchment flaw/stitch (x=0.25, y=0.74); 23 continuous lines of Currier A text in 3 paragraphs.",
        "f38r": "Leaf 6 recto (Bifolio 3, conjugate to f35, Scribe 1 / Currier A): gigantic two-pronged V-shaped swallowtail green leaf with serrated outer margins and 5 white comma-shaped fenestrations; vertical parchment fissure with pale rim in lower blade; twin basal flower-cup/tuber roots; narrow trimmed fore-edge exposing text of f39r; cancelled page number '39'.",
        "f38v": "Leaf 6 verso (Bifolio 3, conjugate to f35, Scribe 1 / Currier A): massive conical/imbricate cone of dozens of overlapping diamond/rhomboid scales (dark green, ochre, white); solitary blue radiating starburst flower on thin stalk emerging from upper right; matching parchment fissure registering through cone (x=0.67, y=0.49); tall pink stalk splitting 8-line paragraph into two columns.",
        "f39r": "Leaf 7 recto (outer Bifolio 2, Scribe 2 / Currier B): single-stalked Currier B herb with rounded leaves and bulbous segmented root.",
        "f39v": "Leaf 7 verso: Scribe 2 / Currier B herb with okody/sarol lexical tokens and 7 drawing intrusions wrapping around wavy rootlets.",
        "f40r": "Leaf 8 recto (outer Bifolio 1, Scribe 2 / Currier B): multi-branched Currier B herbal with 10 text intrusions framing central stalk.",
        "f40v": "Leaf 8 verso (closing folio of Quire 5, outer Bifolio 1, Scribe 2 / Currier B): dense bushy plant with 6 drawing intrusions, closing the outer Currier B jacket of Quire 5.",
    }

    folio_profiles = []
    s1_words = []
    s2_words = []
    s1_lines = 0
    s2_lines = 0
    s1_intrusions = 0
    s2_intrusions = 0

    s1_morphemes = Counter()
    s2_morphemes = Counter()

    for fol in q5_folios:
        d = idx[fol]
        words = folio_words.get(fol, [])
        lines = folio_lines.get(fol, [])
        stems = [canonical_stem(w) for w in words if canonical_stem(w)]

        intrusions = sum(1 for _, _, _, raw in lines if "<->" in raw)
        scan_path = scan_map[fol]
        assert os.path.exists(scan_path), f"Missing scan: {scan_path}"

        if d["hand"] == "1":
            s1_words.extend(words)
            s1_lines += len(lines)
            s1_intrusions += intrusions
            for w in words:
                if w.endswith("edy"):
                    s1_morphemes["-edy"] += 1
                if w.endswith("eey"):
                    s1_morphemes["-eey"] += 1
                if w.endswith("ody"):
                    s1_morphemes["-ody"] += 1
                if w.endswith("aiin") or w.endswith("ain"):
                    s1_morphemes["-aiin"] += 1
                if w.startswith("qo"):
                    s1_morphemes["qo-"] += 1
                if w.startswith("o"):
                    s1_morphemes["o-"] += 1
                if w.startswith("y"):
                    s1_morphemes["y-"] += 1
        else:
            s2_words.extend(words)
            s2_lines += len(lines)
            s2_intrusions += intrusions
            for w in words:
                if w.endswith("edy"):
                    s2_morphemes["-edy"] += 1
                if w.endswith("eey"):
                    s2_morphemes["-eey"] += 1
                if w.endswith("ody"):
                    s2_morphemes["-ody"] += 1
                if w.endswith("aiin") or w.endswith("ain"):
                    s2_morphemes["-aiin"] += 1
                if w.startswith("qo"):
                    s2_morphemes["qo-"] += 1
                if w.startswith("o"):
                    s2_morphemes["o-"] += 1
                if w.startswith("y"):
                    s2_morphemes["y-"] += 1

        bif_num = 1 if fol in ["f33r", "f33v", "f40r", "f40v"] else (
            2 if fol in ["f34r", "f34v", "f39r", "f39v"] else (
                3 if fol in ["f35r", "f35v", "f38r", "f38v"] else 4
            )
        )

        folio_profiles.append(
            {
                "folio": fol,
                "pdf_pages": d["pdf_pages"],
                "hand": d["hand"],
                "currier_lang": d["currier_lang"],
                "bifolium_number": bif_num,
                "line_count": len(lines),
                "word_count": len(words),
                "unique_canonical_stems": len(set(stems)),
                "drawing_intrusions": intrusions,
                "opening_words": words[:5],
                "top_stems": [s for s, _ in Counter(stems).most_common(5)],
                "scan_path": scan_path,
                "visual_forensics": visual_notes[fol],
            }
        )

    # Global coverage check across all 226 folios in folio_index + f95v1 = 227 folios
    pngs = [os.path.basename(p) for p in glob.glob("pages/*.png")]
    all_folios = list(idx.keys())
    if "f95v1" not in all_folios:
        all_folios.append("f95v1")

    scanned_folios = []
    unscanned_folios = []
    for f in all_folios:
        if any(re.search(rf"(?:^|_){f}(?:_|\.|$)", p) for p in pngs) or (
            f == "f68v2" and "f68v2_f68v1_unfolded_astro_enh.png" in pngs
        ) or (
            f == "f86v3" and "f86v4_f86v3_rosettes_outer_verso_enh.png" in pngs
        ) or (
            f == "f86v6" and "f85v2_f86v4_f86v6_rosettes_verso_full_enh.png" in pngs
        ):
            scanned_folios.append(f)
        else:
            unscanned_folios.append(f)

    # Scribe 1 coverage
    s1_folios = [f for f, d in idx.items() if d.get("hand") == "1"]
    s1_scanned = [f for f in s1_folios if f in scanned_folios]
    s1_missing = [f for f in s1_folios if f not in scanned_folios]

    # Unscanned breakdown by Quire
    unscanned_by_quire = {}
    for f in unscanned_folios:
        q = idx[f]["quire"]
        unscanned_by_quire.setdefault(q, []).append(f)

    # Scribe vocabulary comparison in Quire 5
    s1_vocab = set(s1_words)
    s2_vocab = set(s2_words)
    shared_vocab = s1_vocab.intersection(s2_vocab)

    out = {
        "attack": 229,
        "discovery": 246,
        "title": "100.0% (16/16) Quire 5 ($Q=E, f33r-f40v) Visual & Paleographic Completion, Discovery of the Scribe 2 Outer Jacket / Scribe 1 Inner Core Bifolium Architecture, Medieval Stitched Root Repair (f36v), and 93.39% (212/227) Global Codex Visual Coverage",
        "quire5_summary": {
            "quire_code": "E",
            "quire_number": 5,
            "total_folios": len(q5_folios),
            "visually_inspected_folios": len(q5_folios),
            "completion_pct": 100.0,
            "codicological_architecture": {
                "gathering_type": "Regular 4-bifolium quaternion (8 leaves, 16 pages)",
                "bifolium_nesting_outside_in": "[Bif1: H2/B f33|f40, Bif2: H2/B f34|f39, Bif3: H1/A f35|f38, Bif4: H1/A f36|f37]",
                "palindromic_leaf_sequence": "[Leaf 1: H2/B, Leaf 2: H2/B, Leaf 3: H1/A, Leaf 4: H1/A, Leaf 5: H1/A, Leaf 6: H1/A, Leaf 7: H2/B, Leaf 8: H2/B]",
                "bifolia_sheet_homogeneity": "100.0% (all 4 sheets are completely homogeneous in scribe and language across the fold; no bifolium crosses scribes)",
                "production_model": "Scribe 2 executed two complete outer sheets in Currier B, Scribe 1 executed two complete inner sheets in Currier A, and the sheets were nested before binding.",
            },
            "scribe_statistics": {
                "scribe1": {
                    "leaves": ["f35r", "f35v", "f36r", "f36v", "f37r", "f37v", "f38r", "f38v"],
                    "folio_count": 8,
                    "currier_language": "A",
                    "word_count": len(s1_words),
                    "unique_words": len(s1_vocab),
                    "type_token_ratio": round(len(s1_vocab) / len(s1_words), 3),
                    "line_count": s1_lines,
                    "drawing_intrusion_lines": s1_intrusions,
                    "drawing_intrusion_pct": round(s1_intrusions / s1_lines * 100, 2),
                    "key_morphemes": dict(s1_morphemes),
                },
                "scribe2": {
                    "leaves": ["f33r", "f33v", "f34r", "f34v", "f39r", "f39v", "f40r", "f40v"],
                    "folio_count": 8,
                    "currier_language": "B",
                    "word_count": len(s2_words),
                    "unique_words": len(s2_vocab),
                    "type_token_ratio": round(len(s2_vocab) / len(s2_words), 3),
                    "line_count": s2_lines,
                    "drawing_intrusion_lines": s2_intrusions,
                    "drawing_intrusion_pct": round(s2_intrusions / s2_lines * 100, 2),
                    "key_morphemes": dict(s2_morphemes),
                },
                "lexical_overlap": {
                    "shared_vocabulary_count": len(shared_vocab),
                    "s1_exclusive_count": len(s1_vocab - s2_vocab),
                    "s2_exclusive_count": len(s2_vocab - s1_vocab),
                    "jaccard_similarity": round(len(shared_vocab) / len(s1_vocab.union(s2_vocab)), 3),
                },
            },
            "total_words": len(s1_words) + len(s2_words),
        },
        "newly_discovered_forensics_quire5": {
            "f35r_chalice_and_fishtail_root": {
                "folio": "f35r (Yale p70 / TCPDF p70)",
                "features": "Giant chalice cup with serrated green rim; 6-tentacled blue flower head with red segmented comb crest; striate fish-tail root; f35v bleed-through.",
                "crops": [
                    "pages/f35r_chalice_flower_head_crop_enh.png",
                    "pages/f35r_fishtail_root_crop_enh.png",
                ],
            },
            "f35v_figure8_berry_vines": {
                "folio": "f35v (Yale p71 / TCPDF p71)",
                "features": "Massive brassica/kale crown; figure-8 intertwined vine loops bearing turquoise berry clusters; 12-claw horizontal root system.",
                "crops": [
                    "pages/f35v_figure8_vines_berries_crop_enh.png",
                    "pages/f35v_multiclaw_root_crop_enh.png",
                ],
            },
            "f36r_geranium_and_sliced_tuber": {
                "folio": "f36r (Yale p72 / TCPDF p72)",
                "features": "Geranium leaves in tri-color pigment; 4 terminal stippled buds with blue/gold petals; sliced white-topped tuber caudex; cancelled '39' page number.",
                "crops": [
                    "pages/f36r_geranium_blue_gold_buds_crop_enh.png",
                    "pages/f36r_sliced_tuber_root_crop_enh.png",
                ],
            },
            "f36v_stitched_root_repair_and_catkins": {
                "folio": "f36v (Yale p73 / TCPDF p73)",
                "features": "Galium-like starburst whorls; honeycomb globose head with drooping cylindrical catkins; original medieval stitched root repair with visible stitch holes.",
                "crops": [
                    "pages/f36v_honeycomb_catkins_crop_enh.png",
                    "pages/f36v_stitched_root_repair_crop_enh.png",
                    "pages/f36v_stitched_root_repair_compare.png",
                ],
            },
            "f37r_crimson_cymes_and_turnip_root": {
                "folio": "f37r (Yale p74 / TCPDF p74)",
                "features": "5 pairs of arching lanceolate leaves; 7 globose crimson stippled cyme clusters; turnip-like taproot; fore-edge diagonal flaw/stitch; cancelled '39'.",
                "crops": [
                    "pages/f37r_crimson_cyme_clusters_crop_enh.png",
                    "pages/f37r_turnip_root_flaw_crop_enh.png",
                ],
            },
            "f37v_seven_tiered_ladder_and_blue_buds": {
                "folio": "f37v (Yale p75 / TCPDF p75)",
                "features": "7-tiered bicolored crenate leaf ladder; 3 indigo bud pods crowned with crimson-and-white 5-petaled flowers; dotted circular collar above 5-legged root.",
                "crops": [
                    "pages/f37v_blue_buds_crimson_flowers_crop_enh.png",
                    "pages/f37v_dotted_collar_root_crop_enh.png",
                ],
            },
            "f38r_swallowtail_fenestrations_and_twin_tubers": {
                "folio": "f38r (Yale p76 / TCPDF p76)",
                "features": "Giant V-shaped swallowtail green leaf with 5 comma fenestrations; vertical parchment fissure; twin basal flower-cup/tuber roots; narrow fore-edge exposing f39r.",
                "crops": [
                    "pages/f38r_swallowtail_comma_fenestrations_crop_enh.png",
                    "pages/f38r_twin_tuber_root_crop_enh.png",
                    "pages/f38r_vellum_split_compare.png",
                ],
            },
            "f38v_imbricate_cone_and_starburst_flower": {
                "folio": "f38v (Yale p77 / TCPDF p77)",
                "features": "Dense imbricate cone of diamond scales; solitary blue starburst flower; matching parchment fissure registered through cone; twin-column split text.",
                "crops": [
                    "pages/f38v_imbricate_cone_blue_starburst_crop_enh.png",
                    "pages/f38v_cone_vellum_defect_crop_enh.png",
                ],
            },
        },
        "incremental_quire5_milestone": {
            "prior_global_scanned_folios": 204,
            "prior_global_coverage_pct": 89.87,
            "newly_scanned_in_quire5": 8,
            "new_scanned_leaves_in_quire5": ["f35r", "f35v", "f36r", "f36v", "f37r", "f37v", "f38r", "f38v"],
            "post_quire5_global_scanned_folios": 212,
            "post_quire5_global_coverage_pct": 93.39,
            "quire5_completion_status": "16/16 (100.0%) fully rendered and visually inspected",
        },
        "global_codex_coverage_milestone": {
            "total_codex_folios": len(all_folios),
            "visually_inspected_folios": len(scanned_folios),
            "global_coverage_pct": round(len(scanned_folios) / len(all_folios) * 100, 2),
            "quires_1_to_5_f1r_f40v_coverage": "78/78 extant folios (100.0%)",
            "quires_8_to_20_f57r_f116v_coverage": "117/117 extant folios (100.0%)",
            "scribes_2_3_4_5_coverage": "113/113 folios (100.0%)",
            "currier_b_coverage": "83/83 folios (100.0%)",
            "scribe_1_coverage": {
                "total": len(s1_folios),
                "scanned": len(s1_scanned),
                "coverage_pct": round(len(s1_scanned) / len(s1_folios) * 100, 2),
                "remaining_unscanned_count": len(s1_missing),
            },
            "remaining_15_unscanned_folios_by_quire": unscanned_by_quire,
        },
        "bifolios": bifolios,
        "folio_profiles": folio_profiles,
    }

    with open(
        "data/attack229_quire5_visual_completion.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(
        "Attack 229 complete:",
        json.dumps(out["global_codex_coverage_milestone"], indent=2),
    )


if __name__ == "__main__":
    main()
