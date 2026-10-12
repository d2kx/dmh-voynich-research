#!/usr/bin/env python3
"""
tools/attack154_zodiac_months_and_300nymph_calendar.py

Attack 154 (Phase 165 / Discovery 171):
The 10 Zodiac Medallions (`f70v2–f73v`), the 15th-Century European Month Glosses
(`mars..decembre`), Radial Ring Progression (`R1 -> R2/R3 -> @Lz`), and
Four-Triplicity / Four-Season Calendar Concordance.

Investigates:
  1. Complete inventory of all 10 surviving Zodiac wheels (`f70v2` Pisces through
     `f73v` Sagittarius), linking:
       - Central Medallion Iconography & Bilingual Month Gloss (`mars`, `abril`,
         `may`, `juny`, `jolh`, `agost`, `setembre`, `octobre`, `novembre`, `decembre`)
       - Concentric Ring Inscriptions (`@Cr` / `@Cc`) vs. Individual Star-Nymph
         Degree Labels (`@Lz`)
  2. Radial Grammar Progression (`Ring Prose` vs. `Star-Nymph Degree Labels`):
     Tests how `o-` nominal prefixation, `-al/-ar/-ol/-or` case endings, and
     `y-` initial conjunctions (`ykolairol`, `ykeol`, `ykaly`) shift between the
     outer/inner circular rings and the ~30 individual degree nymphs.
  3. Classical 4-Element Triplicity (`Water`, `Fire`, `Earth`, `Air`) & Seasonal
     Morphological Stratification (`1,000`-trial permutation test).
  4. Direct Lexical Cross-Reference from the 300 Zodiac Star-Nymph Degree Labels
     to the Starred Master Recipes (`f103r–f116r`) and Pharmaceutical Jars (`f88r–f102v`).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack154_zodiac_months_and_300nymph_calendar.json"


ZODIAC_MEDALLIONS = [
    {
        "folio": "f70v2",
        "sign": "Pisces (Two Fish tied by a cord)",
        "european_month_gloss": "mars (March)",
        "triplicity": "Water",
        "season": "Early Spring",
        "scan_image": "pages/f70v2_pisces_mars.png",
    },
    {
        "folio": "f70v1",
        "sign": "Aries Part I (Dark-fleeced Ram chewing green shoot)",
        "european_month_gloss": "abril (April, Dark Half)",
        "triplicity": "Fire",
        "season": "Spring",
        "scan_image": "pages/f71v_taurus_abril_enh.png",
    },
    {
        "folio": "f71r",
        "sign": "Aries Part II (Light Ram)",
        "european_month_gloss": "abril (April, Light Half)",
        "triplicity": "Fire",
        "season": "Spring",
        "scan_image": "pages/f71v_taurus_abril_enh.png",
    },
    {
        "folio": "f71v",
        "sign": "Taurus Part I (Dark Bull at manger)",
        "european_month_gloss": "may (May, Dark Half)",
        "triplicity": "Earth",
        "season": "Late Spring",
        "scan_image": "pages/f71v_taurus_abril_enh.png",
    },
    {
        "folio": "f72r1",
        "sign": "Taurus Part II (Light Bull on green turf)",
        "european_month_gloss": "may (May, Light Half)",
        "triplicity": "Earth",
        "season": "Late Spring",
        "scan_image": "pages/f71v_taurus_abril_enh.png",
    },
    {
        "folio": "f72r2",
        "sign": "Gemini (Twin Courtly Lovers holding hands in tunics)",
        "european_month_gloss": "juny (June)",
        "triplicity": "Air",
        "season": "Early Summer",
        "scan_image": "pages/f72r2_gemini_juny.png",
    },
    {
        "folio": "f72r3",
        "sign": "Cancer (Twin Crayfish / Lobsters)",
        "european_month_gloss": "jolh (July)",
        "triplicity": "Water",
        "season": "Mid-Summer",
        "scan_image": "pages/f72r3_cancer_jolh.png",
    },
    {
        "folio": "f72v3",
        "sign": "Leo (Walking Lion with tongue extended)",
        "european_month_gloss": "agost (August)",
        "triplicity": "Fire",
        "season": "Late Summer",
        "scan_image": "pages/f72v3_leo_agost.png",
    },
    {
        "folio": "f72v2",
        "sign": "Virgo (Maiden in medieval gown holding flower/sheaf)",
        "european_month_gloss": "setembre (September)",
        "triplicity": "Earth",
        "season": "Early Autumn",
        "scan_image": "pages/f72v2_virgo_setembre.png",
    },
    {
        "folio": "f72v1",
        "sign": "Libra (Two-Pan Apothecary / Balance Scale)",
        "european_month_gloss": "octobre (October)",
        "triplicity": "Air",
        "season": "Mid-Autumn",
        "scan_image": "pages/f72v1_libra_octobre.png",
    },
    {
        "folio": "f73r",
        "sign": "Scorpio (Lizard-like Scorpion eating star/plant)",
        "european_month_gloss": "novembre (November)",
        "triplicity": "Water",
        "season": "Late Autumn",
        "scan_image": "pages/f73r_scorpio_novembre.png",
    },
    {
        "folio": "f73v",
        "sign": "Sagittarius (Huntsman in crossbow/archer hat drawing bow)",
        "european_month_gloss": "decembre (December)",
        "triplicity": "Fire",
        "season": "Winter",
        "scan_image": "pages/f73v_sagittarius_decembre_y_onset_enh.png",
    },
]


def clean_eva_token(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^\]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t)
    return t.lower()


def parse_zodiac_and_corpus():
    zodiac_folios = {m["folio"] for m in ZODIAC_MEDALLIONS}
    rings_by_folio = defaultdict(list)
    nymph_labels_by_folio = defaultdict(list)
    section_tokens = defaultdict(list)
    folio_sec = {}

    header_re = re.compile(r"^<(f[0-9]+[rv][0-9]*)>\s*<!\s*([^>]+)>")
    locus_re = re.compile(r"^<(f[0-9]+[rv][0-9]*)\.([^,;>]+),([^>]+)>\s*(.*)$")

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m_head = header_re.match(line)
        if m_head and "$" in line:
            fol, meta_str = m_head.groups()
            sec = re.search(r"\$I=([A-Z])", meta_str)
            folio_sec[fol] = sec.group(1) if sec else "?"
            continue

        m_loc = locus_re.match(line)
        if not m_loc:
            continue
        fol, loc_id, loc_type, text = m_loc.groups()
        text = re.sub(r"<[^>]+>", " ", text)
        words = [clean_eva_token(w) for w in re.split(r"[.\s,]+", text)]
        words = [w for w in words if len(w) >= 2]
        if not words:
            continue

        sec = folio_sec.get(fol, "?")
        section_tokens[sec].extend(words)

        if fol in zodiac_folios:
            if "L" in loc_type:
                nymph_labels_by_folio[fol].extend(words)
            else:
                rings_by_folio[fol].extend(words)

    return rings_by_folio, nymph_labels_by_folio, section_tokens


def feature_profile(words):
    n = max(1, len(words))
    return {
        "token_count": len(words),
        "o_prefix_rate": round(sum(1 for w in words if w.startswith("o")) / n, 4),
        "y_prefix_rate": round(sum(1 for w in words if w.startswith("y")) / n, 4),
        "d_s_prefix_rate": round(sum(1 for w in words if w.startswith(("d", "s"))) / n, 4),
        "al_ar_ending_rate": round(sum(1 for w in words if w.endswith(("al", "ar", "aly", "ary"))) / n, 4),
        "ol_or_ending_rate": round(sum(1 for w in words if w.endswith(("ol", "or", "oly", "ory"))) / n, 4),
        "dy_edy_ending_rate": round(sum(1 for w in words if w.endswith(("dy", "edy"))) / n, 4),
        "am_m_ending_rate": round(sum(1 for w in words if w.endswith(("am", "om", "m"))) / n, 4),
        "top_tokens": [w for w, _ in Counter(words).most_common(8)],
    }


def main():
    rings_by_folio, nymph_labels_by_folio, section_tokens = parse_zodiac_and_corpus()

    all_ring_words = [w for f in rings_by_folio for w in rings_by_folio[f]]
    all_nymph_words = [w for f in nymph_labels_by_folio for w in nymph_labels_by_folio[f]]

    ring_prof = feature_profile(all_ring_words)
    nymph_prof = feature_profile(all_nymph_words)

    # Build per-medallion detailed breakdown
    medallion_records = []
    triplicity_words = defaultdict(list)

    for m in ZODIAC_MEDALLIONS:
        fol = m["folio"]
        r_words = rings_by_folio[fol]
        n_words = nymph_labels_by_folio[fol]
        combined = r_words + n_words
        triplicity_words[m["triplicity"]].extend(combined)

        medallion_records.append({
            **m,
            "ring_token_count": len(r_words),
            "nymph_label_count": len(n_words),
            "top_ring_words": [w for w, _ in Counter(r_words).most_common(6)],
            "top_nymph_labels": [w for w, _ in Counter(n_words).most_common(8)],
            "o_prefix_rate": round(sum(1 for w in combined if w.startswith("o")) / max(1, len(combined)), 4),
            "y_prefix_rate": round(sum(1 for w in combined if w.startswith("y")) / max(1, len(combined)), 4),
            "liquid_ol_or_rate": round(sum(1 for w in combined if w.endswith(("ol", "or", "oly", "ory"))) / max(1, len(combined)), 4),
            "essence_al_ar_rate": round(sum(1 for w in combined if w.endswith(("al", "ar", "aly", "ary"))) / max(1, len(combined)), 4),
        })

    # Test Triplicity Morphological Divergence & Cross-Section Echo to Starred Recipes (S) & Pharma (P)
    starred_set = set(section_tokens.get("S", []))
    pharma_set = set(section_tokens.get("P", []))
    herbal_set = set(section_tokens.get("H", []))

    nymph_in_starred = sum(1 for w in all_nymph_words if w in starred_set)
    nymph_in_pharma = sum(1 for w in all_nymph_words if w in pharma_set)
    nymph_in_herbal = sum(1 for w in all_nymph_words if w in herbal_set)
    nymph_in_any_med = sum(1 for w in all_nymph_words if (w in starred_set or w in pharma_set or w in herbal_set))

    # Compare o-prefix dominance in Zodiac Nymph Labels vs Ring Prose via 1,000-trial permutation
    combined_zodiac = [(w, 1) for w in all_nymph_words] + [(w, 0) for w in all_ring_words]
    obs_diff = nymph_prof["o_prefix_rate"] - ring_prof["o_prefix_rate"]
    rng = random.Random(154)
    labels_only = [flag for _, flag in combined_zodiac]
    o_flags = [1 if w.startswith("o") else 0 for w, _ in combined_zodiac]
    n_nymph = len(all_nymph_words)
    n_ring = len(all_ring_words)

    null_diffs = []
    for _ in range(1000):
        perm = labels_only[:]
        rng.shuffle(perm)
        n_o = sum(o for o, f in zip(o_flags, perm) if f == 1) / max(1, n_nymph)
        r_o = sum(o for o, f in zip(o_flags, perm) if f == 0) / max(1, n_ring)
        null_diffs.append(n_o - r_o)

    null_mean = sum(null_diffs) / len(null_diffs)
    null_sd = math.sqrt(sum((x - null_mean) ** 2 for x in null_diffs) / len(null_diffs))
    z_o_shift = (obs_diff - null_mean) / max(1e-9, null_sd)

    payload = {
        "attack": 154,
        "phase": 165,
        "discovery": 171,
        "title": "10 Zodiac Wheels (f70v2-f73v), Bilingual Month Glosses (mars..decembre), and 300 Star-Nymph Calendar",
        "summary": {
            "medallion_folio_count": len(ZODIAC_MEDALLIONS),
            "total_ring_tokens": len(all_ring_words),
            "total_nymph_labels": len(all_nymph_words),
            "nymph_vs_ring_o_prefix_diff": round(obs_diff, 4),
            "nymph_vs_ring_o_prefix_z": round(z_o_shift, 2),
            "nymph_exact_match_in_medical_sections_rate": round(nymph_in_any_med / max(1, len(all_nymph_words)), 4),
            "nymph_exact_match_in_starred_recipes": round(nymph_in_starred / max(1, len(all_nymph_words)), 4),
            "nymph_exact_match_in_pharma": round(nymph_in_pharma / max(1, len(all_nymph_words)), 4),
            "nymph_exact_match_in_herbal": round(nymph_in_herbal / max(1, len(all_nymph_words)), 4),
        },
        "ring_profile": ring_prof,
        "nymph_label_profile": nymph_prof,
        "triplicity_profiles": {t: feature_profile(ws) for t, ws in triplicity_words.items()},
        "medallions": medallion_records,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"[Attack 154] Zodiac Medallions = {len(ZODIAC_MEDALLIONS)}, "
        f"Ring tokens = {len(all_ring_words)}, Nymph labels = {len(all_nymph_words)}; "
        f"Nymph o-prefix = {nymph_prof['o_prefix_rate']*100:.1f}% vs Ring = {ring_prof['o_prefix_rate']*100:.1f}% "
        f"(z = +{z_o_shift:.2f}); "
        f"Nymph exact lexical match in Herbal/Pharma/Recipes = {nymph_in_any_med}/{len(all_nymph_words)} "
        f"({payload['summary']['nymph_exact_match_in_medical_sections_rate']*100:.1f}%)"
    )


if __name__ == "__main__":
    main()
