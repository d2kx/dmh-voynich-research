#!/usr/bin/env python3
"""
Attack 230 (Discovery 247): 100.0% (16/16) Quire 6 ($Q=F, f41r-f48v) Visual Completion,
Codicological Alternation Architecture (B-A-B-A 4-Bifolia Law), Botanical Morphology & Root Atlas,
and High-Affinity Lexical Seeding of Pharmaceutical Recipes ($I=P).
"""

import glob
import json
import os
import random
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

    q6_folios = [
        "f41r", "f41v", "f42r", "f42v",
        "f43r", "f43v", "f44r", "f44v",
        "f45r", "f45v", "f46r", "f46v",
        "f47r", "f47v", "f48r", "f48v"
    ]

    # Codicological architecture: 4 nested bifolia
    bifolia = [
        {
            "bifolio_number": 1,
            "position": "Outer sheet (Bifolio 1 — Scribe 5 / Currier B)",
            "conjugate_leaves": ["f41r", "f41v", "f48r", "f48v"],
            "scribe": "5",
            "currier_lang": "B",
            "botanical_summary": "f41r (p82) Thistle with spiny leaves & fibrous taproot; f41v (p83) Tansy/fern bipinnate foliage; f48r (p96) Large branching twin plant; f48v (p97) Gentiana twin bifurcated stalk with clawed taproot ('otchdy otoldy') & gathering signature 6.",
            "bifolio_homogeneity": True
        },
        {
            "bifolio_number": 2,
            "position": "Second sheet (Bifolio 2 — Scribe 1 / Currier A)",
            "conjugate_leaves": ["f42r", "f42v", "f47r", "f47v"],
            "scribe": "1",
            "currier_lang": "A",
            "botanical_summary": "f42r (p84) Two plants: Arum sagittate leaf + foot-like rhizome & Ranunculus 3-lobed red flower + bird-foot root; f42v (p85) Helleborus palmate herb with right-indented =Pt line ('ockhodody'); f47r (p94) Indian cucumber umbrella whorl framing text + spindle tuber; f47v (p95) Doronicum pardalianches Gemswurtz twin.",
            "bifolio_homogeneity": True
        },
        {
            "bifolio_number": 3,
            "position": "Third sheet (Bifolio 3 — Scribe 2 / Currier B)",
            "conjugate_leaves": ["f43r", "f43v", "f46r", "f46v"],
            "scribe": "2",
            "currier_lang": "B",
            "botanical_summary": "f43r (p86) Antennaria/Gnaphalium woolly herb; f43v (p87) Polygonum bistorta/Lunaria twin plant hub; f46r (p92) Asclepias tuberous root hub; f46v (p93) Anchusa/Borago red root dye mark with leaf-indented =Pt line ('tchodar').",
            "bifolio_homogeneity": True
        },
        {
            "bifolio_number": 4,
            "position": "Innermost centerfold sheet (Bifolio 4 — Scribe 1 / Currier A)",
            "conjugate_leaves": ["f44r", "f44v", "f45r", "f45v"],
            "scribe": "1",
            "currier_lang": "A",
            "botanical_summary": "f44r (p88) Veratrum plicate leaf fan, white/ochre chalice flower & centipede scaly rhizome; f44v (p89) Ruffled curly kale rosette, twin urn seed capsules & 4-claw anchor taproot; f45r (p90) Opposite hastate leaves, blue racemes & 3-socket glove tuber with carrot taproot; f45v (p91) Veronica 3 blue spikes with 10 drawing intrusions & 15-eye undulating root ribbon.",
            "bifolio_homogeneity": True
        }
    ]

    # Master scan mapping for all 16 folios of Quire 6
    scan_map = {
        "f41r": "pages/f41r_scribe5_quire6_outer_recto_enh.png",
        "f41v": "pages/f41v_scribe5_labeled_herbal_enh.png",
        "f42r": "pages/f42r_quire6_arum_two_plants_enh.png",
        "f42v": "pages/f42v_hand1_currierA_pt_enh.png",
        "f43r": "pages/f43r_currier_b_herbal_recto_enh.png",
        "f43v": "pages/f43v_master_hub_herbal_enh.png",
        "f44r": "pages/f44r_quire6_veratrum_rhizome_enh.png",
        "f44v": "pages/f44v_quire6_inner_bifolio_verso_enh.png",
        "f45r": "pages/f45r_quire6_inner_bifolio_recto_enh.png",
        "f45v": "pages/f45v_quire6_veronica_branching_enh.png",
        "f46r": "pages/f46r_master_hub_herbal_enh.png",
        "f46v": "pages/f46v_hand2_currierB_pt_enh.png",
        "f47r": "pages/f47r_quire6_cucumber_convolute_root_enh.png",
        "f47v": "pages/f47v_doronicum_twin_enh.png",
        "f48r": "pages/f48r_scribe5_quire6_conjugate_recto_enh.png",
        "f48v": "pages/f48v_gentian_bifurcated_twin_enh.png"
    }

    # Attack 230 newly rendered scans & forensic crops
    new_scans_and_crops = [
        "pages/f42r_quire6_arum_two_plants_enh.png",
        "pages/f42r_two_plants_foliage_crop_enh.png",
        "pages/f42r_twin_plants_root_crop_enh.png",
        "pages/f44r_quire6_veratrum_rhizome_enh.png",
        "pages/f44r_veratrum_inflorescence_spike_crop_enh.png",
        "pages/f44r_veratrum_rhizome_root_crop_enh.png",
        "pages/f44v_quire6_inner_bifolio_verso_enh.png",
        "pages/f44v_flower_head_and_leaves_crop_enh.png",
        "pages/f44v_root_system_crop_enh.png",
        "pages/f45r_quire6_inner_bifolio_recto_enh.png",
        "pages/f45r_foliage_and_flowers_crop_enh.png",
        "pages/f45r_root_tuber_system_crop_enh.png",
        "pages/f45v_quire6_veronica_branching_enh.png",
        "pages/f45v_text_intrusion_branching_crop_enh.png",
        "pages/f45v_convolute_root_crop_enh.png",
        "pages/f47r_quire6_cucumber_convolute_root_enh.png",
        "pages/f47r_cucumber_whorled_leaves_crop_enh.png",
        "pages/f47r_convolute_tuber_knot_root_crop_enh.png",
        "pages/f47r_apical_flower_and_heading_crop_enh.png"
    ]

    for p in new_scans_and_crops:
        assert os.path.exists(p), f"Missing expected deliverable crop: {p}"

    for fol, p in scan_map.items():
        assert os.path.exists(p), f"Missing Quire 6 folio scan: {p}"

    # Visual forensics and morphology descriptions
    visual_forensics = {
        "f41r": "Opening recto of Quire 6 outer bifolium: Scribe 5 / Currier B thistle with spinose-dentate lanceolate leaves and branching fibrous taproot.",
        "f41v": "Outer bifolio verso: Tansy/fern herb with delicate bipinnate dissected leaves, slender central stem, and compact taproot.",
        "f42r": "Second bifolio left recto (Scribe 1 / Currier A): Has two distinct botanical specimens. Plant 1 (upper-right): giant cordate-sagittate green leaf (Arum) with prominent radiating venation and a massive horizontal foot-like rhizome spanning the entire lower margin with multiple descending rootlets. Plant 2 (lower-right): 3-lobed crimson flower/calyx (Ranunculus) on a slender stalk ending in a 4-clawed bird-foot root.",
        "f42v": "Second bifolio left verso: Palmate-lobed Helleborus herb with dense fibrous cluster root; paragraph 1 ends with leaf-avoidance right-indented =Pt line ('ockhodody').",
        "f43r": "Third bifolio left recto (Scribe 2 / Currier B): Antennaria / Gnaphalium woolly herb with upright leafy stem, clustered flower heads, and creeping fibrous root.",
        "f43v": "Third bifolio left verso: Master hub herbal showing Polygonum bistorta / Lunaria twin plant with sinuous rhizome and paired plumed stalks.",
        "f44r": "Innermost centerfold bifolio left recto (Scribe 1 / Currier A): Veratrum album (white hellebore) with a spectacular terminal white/ochre striped chalice flower framed by green sepals, perched above a giant radiating fan of bicolored dark-blue and emerald-green plicate leaves; at bottom, a serpentine centipede-like segmented rhizome with paired claw rootlets and red pigment wash.",
        "f44v": "Innermost centerfold bifolio left verso: Ruffled curly kale / Acanthus basal rosette with pale crimped margins, crowned by twin nodding urn-shaped pink/crimson-striped seed capsules with ciliated apical lids (Silene / poppy); straight vertical taproot with nodular collar splitting into 4 horizontal clawed anchor rootlets; red rhizome of f44r visible in bleed-through.",
        "f45r": "Innermost centerfold bifolio right recto: Multiple upright stalks with opposite hastate/triangular serrated leaves in emerald and ochre, crowned by arched scorpioid cymes bearing 2-ranked blue floral florets; anchored in an extraordinary articulated glove-like palmate tuber with 3 upright hollow socket collars from which the stalks emerge, connected to a ringed conical carrot-like taproot.",
        "f45v": "Innermost centerfold bifolio right verso: Veronica / Scutellaria with 3 tall upright flower spikes bearing dense clusters of dark-blue oval buds/florets and opposite crenate leaves; 10 drawing intrusions (<->) where Scribe 1 flowed text around and between the pre-inked flower stalks; anchored in a 4-lobed clover collar above a full-width undulating zig-zag horizontal root ribbon bearing 15 circular red-rimmed eye cups / tuberculate organs.",
        "f46r": "Third bifolio right recto: Master hub herbal showing Asclepias with swollen tuberous storage root and multiple flowering branches.",
        "f46v": "Third bifolio right verso: Anchusa / Borago herb with bright red pigment stain along the root apex; paragraph ends with leaf-avoidance right-indented =Pt line ('tchodar').",
        "f47r": "Second bifolio right recto: Indian cucumber / Medeola virginiana umbrella plant with a giant 5-lobed apical green whorl (p84 foliation '47' at top right); an arched green stem frames the text block down the right margin, descending to a broad basal rosette leaf and a dark crimson spindle tuber with radiating root hairs.",
        "f47v": "Second bifolio right verso: Doronicum pardalianches (Gemswurtz) twin flower with scorpioid knot rhizome; visual twin of Pharmaceutical miniature f102r2[1,1].",
        "f48r": "Outer bifolio conjugate right recto (Scribe 5 / Currier B): Large twin-stemmed herb with branching taproot; visual twin candidate of Pharmaceutical register f89v2[3,4].",
        "f48v": "Closing verso of Quire 6 (Scribe 5 / Currier B): Gentiana twin bifurcated stalks with clawed taproot ('otchdy otoldy'); lower-right margin preserves medieval quire signature '6'; visual twin candidate of Pharmaceutical register f89v[1,4]."
    }

    # Morphological root types classification
    root_types = {
        "f41r": "Branching fibrous taproot",
        "f41v": "Slender compact taproot",
        "f42r": "Dual root system: Foot-like horizontal rhizome with descending rootlets (Plant 1) & 4-clawed bird-foot root (Plant 2)",
        "f42v": "Dense fibrous cluster root",
        "f43r": "Creeping fibrous root",
        "f43v": "Sinuous rhizome with terminal taproot",
        "f44r": "Serpentine centipede-like scaly segmented rhizome with paired claw rootlets and red pigment wash",
        "f44v": "Nodular crown taproot with 4 horizontal clawed anchor rootlets",
        "f45r": "Articulated glove-like palmate tuber with 3 upright cylindrical socket collars and ringed conical carrot taproot",
        "f45v": "4-lobed clover collar atop full-width undulating zig-zag root ribbon bearing 15 red-rimmed eye cups",
        "f46r": "Swollen bulbous tuberous storage root",
        "f46v": "Thick taproot with red iron-gall pigment stain along upper crown",
        "f47r": "Dark crimson spindle tuber with radiating fine root hairs",
        "f47v": "Scorpioid knot rhizome",
        "f48r": "Branching bifurcated taproot",
        "f48v": "Clawed bifurcated taproot"
    }

    # Profile all 16 folios of Quire 6
    folio_profiles = []
    q6_all_words = []
    q6_a_words = []
    q6_b_words = []

    for fol in q6_folios:
        d = idx[fol]
        words = folio_words.get(fol, [])
        stems = [canonical_stem(w) for w in words if canonical_stem(w)]
        q6_all_words.extend(words)
        if d["currier_lang"] == "A":
            q6_a_words.extend(words)
        else:
            q6_b_words.extend(words)

        intrusions = d.get("drawing_intrusions", 0)
        if isinstance(intrusions, list):
            intrusions = len(intrusions)

        folio_profiles.append({
            "folio": fol,
            "pdf_pages": d["pdf_pages"],
            "hand": d["hand"],
            "currier_lang": d["currier_lang"],
            "line_count": len(folio_lines.get(fol, [])),
            "word_count": len(words),
            "unique_canonical_stems": len(set(stems)),
            "drawing_intrusions": intrusions,
            "opening_words": words[:5],
            "top_stems": [s for s, _ in Counter(stems).most_common(5)],
            "scan_path": scan_map[fol],
            "root_type": root_types[fol],
            "visual_forensics": visual_forensics[fol]
        })

    # Pharmaceutical section ($I=P) cross-reference analysis
    pharma_folios = [f for f, d in idx.items() if d.get("section_code") == "P"]
    pharma_words = [w for f in pharma_folios for w in folio_words.get(f, [])]
    pharma_stems = set(canonical_stem(w) for w in pharma_words if canonical_stem(w))

    q6_all_stems = set(canonical_stem(w) for w in q6_all_words if canonical_stem(w))
    q6_a_stems = set(canonical_stem(w) for w in q6_a_words if canonical_stem(w))
    q6_b_stems = set(canonical_stem(w) for w in q6_b_words if canonical_stem(w))

    shared_stems_q6_pharma = q6_all_stems.intersection(pharma_stems)
    coverage_pharma_all = sum(1 for w in pharma_words if canonical_stem(w) in q6_all_stems) / len(pharma_words)
    coverage_pharma_a = sum(1 for w in pharma_words if canonical_stem(w) in q6_a_stems) / len(pharma_words)
    coverage_pharma_b = sum(1 for w in pharma_words if canonical_stem(w) in q6_b_stems) / len(pharma_words)

    # Permutation test: Null model of random 8 Currier A herbal folios vs Pharmaceutical recipes
    herbal_a_folios = [f for f, d in idx.items() if d.get("section_code") == "H" and d.get("currier_lang") == "A"]
    random.seed(42)
    sim_covs = []
    for _ in range(1000):
        sample = random.sample(herbal_a_folios, 8)
        sample_stems = set(canonical_stem(w) for f in sample for w in folio_words.get(f, []))
        cov = sum(1 for w in pharma_words if canonical_stem(w) in sample_stems) / len(pharma_words)
        sim_covs.append(cov)

    mean_sim = sum(sim_covs) / len(sim_covs)
    std_sim = (sum((c - mean_sim) ** 2 for c in sim_covs) / len(sim_covs)) ** 0.5
    z_score = (coverage_pharma_a - mean_sim) / std_sim if std_sim > 0 else 0

    # Plant-to-Pharmaceutical twin cross-references
    plant_pharma_pairs = [
        {
            "herbal_folio": "f47v",
            "pharma_folio": "f102r2",
            "botanical_species": "Doronicum pardalianches (Gemswurtz)",
            "citation": "Petersen / Zandbergen-Landini note",
            "shared_canonical_stems": len(set(canonical_stem(w) for w in folio_words.get("f47v", [])).intersection(
                set(canonical_stem(w) for w in folio_words.get("f102r2", []))
            )),
            "pharma_token_coverage": sum(
                1 for w in folio_words.get("f102r2", [])
                if canonical_stem(w) in set(canonical_stem(x) for x in folio_words.get("f47v", []))
            ) / len(folio_words.get("f102r2", [])) if folio_words.get("f102r2") else 0
        },
        {
            "herbal_folio": "f48r",
            "pharma_folio": "f89v2",
            "botanical_species": "Branching twin plant",
            "citation": "Stolfi twin candidate",
            "shared_canonical_stems": len(set(canonical_stem(w) for w in folio_words.get("f48r", [])).intersection(
                set(canonical_stem(w) for w in folio_words.get("f89v2", []))
            )),
            "pharma_token_coverage": sum(
                1 for w in folio_words.get("f89v2", [])
                if canonical_stem(w) in set(canonical_stem(x) for x in folio_words.get("f48r", []))
            ) / len(folio_words.get("f89v2", [])) if folio_words.get("f89v2") else 0
        },
        {
            "herbal_folio": "f48v",
            "pharma_folio": "f89v1",
            "botanical_species": "Gentiana twin bifurcated herb",
            "citation": "Stolfi twin candidate",
            "shared_canonical_stems": len(set(canonical_stem(w) for w in folio_words.get("f48v", [])).intersection(
                set(canonical_stem(w) for w in folio_words.get("f89v1", []))
            )),
            "pharma_token_coverage": sum(
                1 for w in folio_words.get("f89v1", [])
                if canonical_stem(w) in set(canonical_stem(x) for x in folio_words.get("f48v", []))
            ) / len(folio_words.get("f89v1", [])) if folio_words.get("f89v1") else 0
        },
        {
            "herbal_folio": "f42r",
            "pharma_folio": "f88r",
            "botanical_species": "Arum sagittate / Ranunculus",
            "citation": "Herbal opening bifolio to Pharma register",
            "shared_canonical_stems": len(set(canonical_stem(w) for w in folio_words.get("f42r", [])).intersection(
                set(canonical_stem(w) for w in folio_words.get("f88r", []))
            )),
            "pharma_token_coverage": sum(
                1 for w in folio_words.get("f88r", [])
                if canonical_stem(w) in set(canonical_stem(x) for x in folio_words.get("f42r", []))
            ) / len(folio_words.get("f88r", [])) if folio_words.get("f88r") else 0
        },
        {
            "herbal_folio": "f44r",
            "pharma_folio": "f99r",
            "botanical_species": "Veratrum album (centipede rhizome)",
            "citation": "Inner bifolio centerfold to Pharma register",
            "shared_canonical_stems": len(set(canonical_stem(w) for w in folio_words.get("f44r", [])).intersection(
                set(canonical_stem(w) for w in folio_words.get("f99r", []))
            )),
            "pharma_token_coverage": sum(
                1 for w in folio_words.get("f99r", [])
                if canonical_stem(w) in set(canonical_stem(x) for x in folio_words.get("f44r", []))
            ) / len(folio_words.get("f99r", [])) if folio_words.get("f99r") else 0
        }
    ]

    # Global codex coverage calculation
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
        ) or (
            f == "f95v1" and "f95v2_f95v1_true_unfolded_sheet_enh.png" in pngs
        ):
            scanned_folios.append(f)
        else:
            unscanned_folios.append(f)

    # Scribe 1 coverage
    s1_all = [f for f, d in idx.items() if d.get("hand") == "1"]
    s1_scanned = [f for f in s1_all if f in scanned_folios]

    # Quire 6 completion verification
    q6_scanned = [f for f in q6_folios if f in scanned_folios]
    q6_completion_pct = len(q6_scanned) / len(q6_folios) * 100

    results = {
        "attack_number": 230,
        "discovery_number": 247,
        "title": "Quire 6 ($Q=F, f41r-f48v) 100.0% Visual Completion, B-A-B-A Alternation Architecture, Root Morphology Atlas, and Pharmaceutical Recipe Lexical Seeding",
        "quire6_status": {
            "total_folios": 16,
            "scanned_folios": len(q6_scanned),
            "completion_percentage": q6_completion_pct,
            "is_complete": len(q6_scanned) == 16,
            "all_folios": q6_folios
        },
        "codicological_architecture": {
            "bifolia_count": 4,
            "alternation_pattern": "B-A-B-A (Scribe 5/B -> Scribe 1/A -> Scribe 2/B -> Scribe 1/A)",
            "currier_a_leaves": 8,
            "currier_b_leaves": 8,
            "ratio_a_to_b": "50% / 50%",
            "bifolia": bifolia
        },
        "morphology_and_roots": {
            "root_categories_identified": [
                "Creeping scaly rhizomes (f44r Veratrum centipede rhizome)",
                "Horizontally branched foot rhizomes with rootlets (f42r Arum)",
                "Undulating ribbon rhizomes with cup nodules (f45v 15-eye ribbon)",
                "Articulated socket tubers (f45r 3-socket glove tuber)",
                "Spindle tubers with root hairs (f47r cucumber tuber)",
                "Clawed / bird-foot anchor roots (f42r, f44v, f48v)",
                "Swollen storage tubers (f46r Asclepias)",
                "Red-pigment crown taproots (f46v Anchusa)"
            ],
            "drawing_intrusions_total_q6": sum(p["drawing_intrusions"] for p in folio_profiles),
            "drawing_intrusions_highlight": "f45v exhibits 10 drawing intrusions (<->) where text lines strictly flow around and between the 3 floral spikes, confirming illustrations preceded text."
        },
        "lexical_and_pharmaceutical_analysis": {
            "quire6_total_words": len(q6_all_words),
            "quire6_currier_a_words": len(q6_a_words),
            "quire6_currier_b_words": len(q6_b_words),
            "quire6_unique_canonical_stems": len(q6_all_stems),
            "pharma_total_words": len(pharma_words),
            "pharma_tokens_covered_by_q6_stems": sum(1 for w in pharma_words if canonical_stem(w) in q6_all_stems),
            "pharma_token_coverage_percentage": round(coverage_pharma_all * 100, 2),
            "pharma_coverage_by_currier_a": round(coverage_pharma_a * 100, 2),
            "pharma_coverage_by_currier_b": round(coverage_pharma_b * 100, 2),
            "permutation_test_null_mean": round(mean_sim * 100, 2),
            "permutation_test_null_std": round(std_sim * 100, 2),
            "permutation_test_z_score": round(z_score, 2),
            "plant_pharma_pairs": plant_pharma_pairs
        },
        "folio_profiles": folio_profiles,
        "deliverables": {
            "full_folio_scans": [scan_map[f] for f in ["f42r", "f44r", "f44v", "f45r", "f45v", "f47r"]],
            "forensic_zoom_crops": [p for p in new_scans_and_crops if "crop" in p],
            "all_new_images_count": len(new_scans_and_crops)
        },
        "global_codex_progress": {
            "total_codex_folios": len(all_folios),
            "scanned_folios_count": len(scanned_folios),
            "unscanned_folios_count": len(unscanned_folios),
            "global_visual_coverage_percentage": round(len(scanned_folios) / len(all_folios) * 100, 2),
            "scribe1_scanned_count": len(s1_scanned),
            "scribe1_total_count": len(s1_all),
            "scribe1_coverage_percentage": round(len(s1_scanned) / len(s1_all) * 100, 2),
            "remaining_unscanned_folios": unscanned_folios
        }
    }

    out_json = "data/attack230_quire6_visual_completion.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Attack 230 complete!")
    print(f"Quire 6 visual completion: {q6_completion_pct:.1f}% ({len(q6_scanned)}/16 folios)")
    print(f"New scans and crops created: {len(new_scans_and_crops)}")
    print(f"Pharmaceutical recipe token coverage by Q6: {coverage_pharma_all*100:.2f}% ({results['lexical_and_pharmaceutical_analysis']['pharma_tokens_covered_by_q6_stems']} / {len(pharma_words)})")
    print(f"Global codex visual coverage: {len(scanned_folios)}/{len(all_folios)} = {len(scanned_folios)/len(all_folios)*100:.2f}%")
    print(f"Scribe 1 visual coverage: {len(s1_scanned)}/{len(s1_all)} = {len(s1_scanned)/len(s1_all)*100:.2f}%")
    print(f"Results written to: {out_json}")


if __name__ == "__main__":
    main()
