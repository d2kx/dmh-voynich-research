#!/usr/bin/env python3
"""
Attack 134 (Phase 145 / Discovery 151):
The Complete Multi-Folio Cross-Section Canonical Stem Dictionary & Within-Stem
Supply-to-Clinical Inflectional Transformation Law.

Investigates:
1. All multi-folio canonical stems (`df_folios >= 2`, `len(stem) >= 2`) across
   the 226 folios of the Voynich Manuscript: total occurrences, folio DF, IDF,
   8-section distribution (`H, A, Z, B, P, S, C, T`), locus distribution
   (`LABEL`, `RING`, `PROSE`), and 6-way functional semantic classification.
2. Complete 8-Slot Inflectional Paradigm for each stem (`NOM_O`, `ACT_QO`,
   `HERB_BENCH`, `TOP_D`, `APPL_L`, `PROC_EDY`, `DOSE_AIIN`, `LIQ_OLOR`) with
   top attested surface word forms.
3. Paired Within-Stem Supply-to-Clinical Inflectional Transformation Test
   (1,000-trial paired permutation test across all stems attested >= 3 times in
   both Supply/Diagram sections `H ∪ A ∪ Z ∪ C` and Clinical sections `B ∪ P ∪ S`).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack134_complete_cross_section_stem_dictionary.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def canon_stem(w: str) -> str:
    s = w
    if s.startswith("q") and len(s) > 2:
        s = s[1:]
    for p in ["ch", "sh", "da", "sa", "ol", "al", "or", "ar", "ok", "ot", "yk", "yt", "d", "s", "y", "o", "l"]:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ["aiin", "oiin", "iin", "eedy", "edy", "ody", "ady", "dy", "ey", "oy", "ol", "al", "or", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n", "s"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def loc_macro(loc: str) -> str:
    l = loc.lstrip("@+=*~&/")
    if l.startswith("L"):
        return "LABEL"
    if l.startswith(("C", "R")):
        return "RING"
    return "PROSE"


def inflection_slots(w: str) -> dict:
    return {
        "NOM_O": w.startswith("o") and not w.startswith("ol"),
        "ACT_QO": w.startswith("qo"),
        "HERB_BENCH": w.startswith(("ch", "sh")),
        "TOP_D": w.startswith("d"),
        "APPL_L": w.startswith(("l", "ol", "al")),
        "PROC_EDY": w.endswith(("edy", "eedy")),
        "DOSE_AIIN": w.endswith(("aiin", "oiin", "iin")),
        "LIQ_OLOR": w.endswith(("ol", "or", "al", "ar")),
    }


def classify_stem_domain(sec_counts: Counter, df: int) -> str:
    n_secs = sum(1 for k, v in sec_counts.items() if v > 0)
    if df > 45:
        return "CLASS_1_CORE_GRAMMATICAL_AND_UNIVERSAL_ROOT"
    has_supply = (sec_counts["H"] + sec_counts["A"] + sec_counts["Z"] + sec_counts["C"]) > 0
    has_clin = (sec_counts["B"] + sec_counts["P"] + sec_counts["S"]) > 0
    if n_secs >= 4 and has_supply and has_clin:
        return "CLASS_2_PAN_MEDICAL_CROSS_SECTION_HUB"
    if (sec_counts["H"] + sec_counts["P"]) > 0 and sec_counts["S"] > sec_counts["B"]:
        return "CLASS_3_APOTHECARY_DECOCTION_SPECIMEN"
    if has_supply and sec_counts["B"] >= sec_counts["S"] and sec_counts["B"] > 0:
        return "CLASS_4_BALNEOLOGICAL_HYDROTHERAPY_SPECIMEN"
    if (sec_counts["A"] + sec_counts["Z"] + sec_counts["C"]) > (sec_counts["H"] + sec_counts["S"]):
        return "CLASS_5_CELESTIAL_COSMOLOGICAL_TERM"
    return "CLASS_6_BOTANICAL_OR_SECTION_LOCAL_STEM"


def main():
    random.seed(42)
    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx["folios"]

    stem_tokens = defaultdict(list)
    stem_folios = defaultdict(set)
    stem_sec_counts = defaultdict(Counter)
    stem_loc_counts = defaultdict(Counter)
    stem_surface_forms = defaultdict(Counter)
    stem_slot_forms = defaultdict(lambda: defaultdict(Counter))

    # Track Supply (H,A,Z,C) vs Clinical (B,P,S) occurrences per stem
    stem_supply_toks = defaultdict(list)
    stem_clinical_toks = defaultdict(list)

    with open(ZL_PATH, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_line = re.match(r"^<(f[0-9a-zA-Z]+)\.([^>]+)>\s+(.*)$", line)
            if not m_line:
                continue
            fol, loc_part, text = m_line.groups()
            loc = loc_part.split(",")[-1] if "," in loc_part else loc_part
            l_mac = loc_macro(loc)
            sec = folio_meta.get(fol, {}).get("section_code", "?")

            text_no_comm = re.sub(r"<![^>]+>", "", text)
            raw_toks = re.split(r"[.\s,]+", text_no_comm)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if len(t) >= 2]

            for w in toks:
                st = canon_stem(w)
                if len(st) < 2:
                    continue
                stem_tokens[st].append(w)
                stem_folios[st].add(fol)
                stem_sec_counts[st][sec] += 1
                stem_loc_counts[st][l_mac] += 1
                stem_surface_forms[st][w] += 1

                slots = inflection_slots(w)
                for sk, flag in slots.items():
                    if flag:
                        stem_slot_forms[st][sk][w] += 1

                if sec in ("H", "A", "Z", "C"):
                    stem_supply_toks[st].append(w)
                elif sec in ("B", "P", "S"):
                    stem_clinical_toks[st].append(w)

    n_total_folios = 226
    multi_folio_stems = [s for s, fols in stem_folios.items() if len(fols) >= 2]
    multi_folio_stems.sort(key=lambda s: (-len(stem_tokens[s]), s))

    class_counts = Counter()
    stem_entries = []

    for rank, st in enumerate(multi_folio_stems, 1):
        df = len(stem_folios[st])
        tot = len(stem_tokens[st])
        idf = round(math.log(n_total_folios / df), 3)
        sc = stem_sec_counts[st]
        lc = stem_loc_counts[st]
        sem_class = classify_stem_domain(sc, df)
        class_counts[sem_class] += 1

        paradigm = {}
        for sk in ["NOM_O", "ACT_QO", "HERB_BENCH", "TOP_D", "APPL_L", "PROC_EDY", "DOSE_AIIN", "LIQ_OLOR"]:
            c_map = stem_slot_forms[st][sk]
            if c_map:
                top_w, top_c = c_map.most_common(1)[0]
                paradigm[sk] = {"count": sum(c_map.values()), "top_form": top_w, "top_form_count": top_c}
            else:
                paradigm[sk] = {"count": 0, "top_form": "-", "top_form_count": 0}

        stem_entries.append({
            "rank": rank,
            "stem": st,
            "total_tokens": tot,
            "df_folios": df,
            "idf": idf,
            "semantic_class": sem_class,
            "section_counts": {k: sc[k] for k in ["H", "A", "Z", "C", "T", "P", "B", "S"] if sc[k] > 0},
            "locus_counts": dict(lc),
            "top_surface_forms": [{"word": w, "count": c} for w, c in stem_surface_forms[st].most_common(5)],
            "inflectional_paradigm": paradigm,
        })

    # Paired Within-Stem Supply (H,A,Z,C) -> Clinical (B,P,S) Inflectional Shift Test
    shared_bridge_stems = [
        st for st in multi_folio_stems
        if len(stem_supply_toks[st]) >= 3 and len(stem_clinical_toks[st]) >= 3
    ]

    slot_keys = ["NOM_O", "ACT_QO", "HERB_BENCH", "TOP_D", "APPL_L", "PROC_EDY", "DOSE_AIIN", "LIQ_OLOR"]
    supply_rates = {sk: [] for sk in slot_keys}
    clinical_rates = {sk: [] for sk in slot_keys}
    paired_diffs = []  # Clinical Action (ACT_QO + APPL_L + PROC_EDY + DOSE_AIIN) - Nominal Supply (NOM_O + LIQ_OLOR)

    for st in shared_bridge_stems:
        sup_w = stem_supply_toks[st]
        cli_w = stem_clinical_toks[st]
        ns = len(sup_w)
        nc = len(cli_w)

        s_slots = {sk: sum(1 for w in sup_w if inflection_slots(w)[sk]) / ns for sk in slot_keys}
        c_slots = {sk: sum(1 for w in cli_w if inflection_slots(w)[sk]) / nc for sk in slot_keys}
        for sk in slot_keys:
            supply_rates[sk].append(s_slots[sk])
            clinical_rates[sk].append(c_slots[sk])

        sup_clin_idx = (s_slots["ACT_QO"] + s_slots["APPL_L"] + s_slots["PROC_EDY"] + s_slots["DOSE_AIIN"]) - (s_slots["NOM_O"] + s_slots["LIQ_OLOR"])
        cli_clin_idx = (c_slots["ACT_QO"] + c_slots["APPL_L"] + c_slots["PROC_EDY"] + c_slots["DOSE_AIIN"]) - (c_slots["NOM_O"] + c_slots["LIQ_OLOR"])
        paired_diffs.append(cli_clin_idx - sup_clin_idx)

    obs_mean_diff = sum(paired_diffs) / len(paired_diffs)
    null_diffs = []
    for _ in range(1000):
        s_flip = sum(d * (1 if random.random() < 0.5 else -1) for d in paired_diffs) / len(paired_diffs)
        null_diffs.append(s_flip)
    mu_null = sum(null_diffs) / len(null_diffs)
    sd_null = math.sqrt(sum((x - mu_null) ** 2 for x in null_diffs) / len(null_diffs))
    z_paired = (obs_mean_diff - mu_null) / (sd_null if sd_null > 0 else 1.0)

    slot_shift_summary = {}
    for sk in slot_keys:
        ms = 100.0 * sum(supply_rates[sk]) / len(supply_rates[sk])
        mc = 100.0 * sum(clinical_rates[sk]) / len(clinical_rates[sk])
        slot_shift_summary[sk] = {
            "supply_HAZC_mean_pct": round(ms, 2),
            "clinical_BPS_mean_pct": round(mc, 2),
            "delta_pct": round(mc - ms, 2),
            "ratio_clinical_over_supply": round(mc / ms, 3) if ms > 0 else 0.0,
        }

    out = {
        "attack": 134,
        "phase": 145,
        "discovery": 151,
        "title": "Complete Multi-Folio Cross-Section Canonical Stem Dictionary & Within-Stem Supply-to-Clinical Inflectional Transformation Law",
        "overview": {
            "n_multi_folio_stems": len(multi_folio_stems),
            "total_tokens_covered": sum(len(stem_tokens[s]) for s in multi_folio_stems),
            "semantic_class_breakdown": dict(class_counts),
            "n_shared_bridge_stems_ge3": len(shared_bridge_stems),
            "within_stem_supply_to_clinical_shift_test": {
                "n_paired_stems": len(shared_bridge_stems),
                "observed_mean_clinical_minus_supply_index": round(obs_mean_diff, 4),
                "null_mean": round(mu_null, 4),
                "null_sd": round(sd_null, 4),
                "z_score": round(z_paired, 2),
                "slot_shift_summary": slot_shift_summary,
            },
        },
        "top200_canonical_stem_dictionary": stem_entries[:200],
        "top50_pan_medical_rare_hub_stems": [
            e for e in stem_entries
            if e["semantic_class"] == "CLASS_2_PAN_MEDICAL_CROSS_SECTION_HUB" and 4 <= e["df_folios"] <= 25
        ][:50],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 134] Saved {OUT_JSON}")
    print(f"Total multi-folio canonical stems: {len(multi_folio_stems)} covering {out['overview']['total_tokens_covered']} tokens")
    print("Semantic Class Breakdown:", json.dumps(dict(class_counts), indent=2))
    print("Within-Stem Supply -> Clinical Shift Test:", json.dumps(out["overview"]["within_stem_supply_to_clinical_shift_test"], indent=2))


if __name__ == "__main__":
    main()
