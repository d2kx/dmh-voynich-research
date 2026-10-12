#!/usr/bin/env python3
r"""
Attack 113 (Discovery 130): The Five-Section (`Z, H, P, B, S`) Dual-Branch Therapeutic
Routing Matrix & Exact Word-for-Word Inflectional Paradigm Table

Tests & Builds:
1. Maps all open-class canonical stems (excluding Top-45 Canonical Stems, `len >= 3`, `2 <= df <= 95`)
   across all FIVE medical/calendrical sections of the Voynich Manuscript:
   - `Z`: `12` Zodiac Medallions (`f70v2–f73v`),
   - `H`: `128` Herbal Specimen Monographs,
   - `P`: `16` Pharmaceutical Jar/Root Formularies (`f88r–f102v2`),
   - `B`: `19` Balneological Hydrotherapy Folios (`f75r–f84v`),
   - `S`: `292` Starred Clinical Recipes (`f103r–f116r`, `f58r/v`).
2. Classifies every `H ∩ P` Apothecary-Compiled Botanical Stem (`314` stems) into three therapeutic
   routing classes:
   - **Dual-Branch Therapeutic Stems (`H ∩ P ∩ B ∩ S`)**: Botanicals used in BOTH Oral/Decoction
     Starred Recipes (`$I=S`) AND Balneological Immersion Baths (`$I=B`),
   - **Decoction-Only Stems (`(H ∩ P ∩ S) \ B`)**: Botanicals routed exclusively to Starred Recipes (`$I=S`),
   - **Hydrotherapy-Only Stems (`(H ∩ P ∩ B) \ S`)**: Botanicals routed exclusively to Immersion Baths (`$I=B`),
   and compares the morphological & radical (`ch/sh/k/t/ke/te/kch/tch/cth`) profiles of these 3 classes!
3. Constructs the **Complete Word-for-Word Five-Section Inflectional Paradigm Table (`cs -> Z_surface | H_surface | P_label | P_prose | B_surface | S_surface`)**
   for all Pan-Medical Open-Class Stems attested simultaneously across `Z ∩ H ∩ P ∩ B ∩ S` (and `H ∩ P ∩ B ∩ S`),
   demonstrating how the exact same botanical stem is systematically inflected across all 5 sections.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack113_five_section_dual_branch_therapeutic_matrix.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    out = []
    for c in s.replace(".", " ").replace(",", " ").split():
        w = re.sub(r"[^a-zA-Z]", "", c).lower()
        if w:
            out.append(w)
    return out


def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = "o" + s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = s.replace("cph", "cth").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = s.replace("sh", "ch")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    if s.endswith("edy") and len(s) > 4:
        s = s[:-3] + "dy"
    elif s.endswith("ody") and len(s) > 4:
        s = s[:-3] + "dy"
    return s


def classify_radical_family(stem: str) -> str:
    if any(r in stem for r in ("kch", "tch", "ckh", "cth")):
        return "COMPOUND_GALLOWS_BENCH (kch/tch/ckh/cth)"
    if "ke" in stem or "te" in stem:
        return "EXTENDED_GALLOWS (ke/te)"
    if "che" in stem:
        return "EXTENDED_BENCH (che)"
    if "ch" in stem:
        return "SIMPLEX_BENCH (ch)"
    if "k" in stem or "t" in stem:
        return "SIMPLEX_GALLOWS (k/t)"
    return "VOCALIC_LIQUID_OTHER"


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}

    folio_meta = {}
    folio_all_tokens = defaultdict(list)
    sec_tokens = defaultdict(list)
    sec_label_tokens = defaultdict(list)
    sec_prose_tokens = defaultdict(list)

    all_word_counts = Counter()

    for raw_line in raw_lines:
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        mf = FOLIO_META_RE.match(raw_s)
        if mf:
            cur_folio = "f" + mf.group(1)
            meta_str = mf.group(2)
            cur_meta = {}
            for kv in meta_str.split():
                if "=" in kv:
                    k, v = kv.lstrip("$").split("=", 1)
                    cur_meta[k] = v
            folio_meta[cur_folio] = cur_meta
            continue
        ml = LOCUS_RE.match(raw_s)
        if ml and cur_folio:
            lnum, ltype, text = ml.group(2), ml.group(3), ml.group(4)
            toks = clean_tokens(text)
            if not toks:
                continue
            for w in toks:
                all_word_counts[w] += 1
            folio_all_tokens[cur_folio].extend(toks)
            sec = cur_meta.get("I", "U")
            ltype_clean = ltype.lstrip("@+*=")
            sec_tokens[sec].extend(toks)
            if ltype_clean.startswith("L"):
                sec_label_tokens[sec].extend(toks)
            elif ltype_clean.startswith("P"):
                sec_prose_tokens[sec].extend(toks)

    canon_counts = Counter()
    for w, c in all_word_counts.items():
        cs = canonical_stem(w)
        if len(cs) >= 3:
            canon_counts[cs] += c
    closed_stems = {cs for cs, _ in canon_counts.most_common(45)}

    stem_doc_freq = Counter()
    all_folios_list = sorted(folio_all_tokens.keys())
    for f in all_folios_list:
        for st in {canonical_stem(w) for w in folio_all_tokens[f]}:
            stem_doc_freq[st] += 1

    n_docs = len(all_folios_list)
    stem_idf = {}
    for st, df in stem_doc_freq.items():
        if st not in closed_stems and len(st) >= 3 and 2 <= df <= 95:
            stem_idf[st] = math.log((n_docs + 1.0) / (df + 1.0))

    # Build surface form counters per section & canonical stem
    sec_stem_surfaces = defaultdict(lambda: defaultdict(Counter))
    for sec in ("Z", "H", "P", "B", "S"):
        for w in sec_tokens[sec]:
            cs = canonical_stem(w)
            if cs in stem_idf:
                sec_stem_surfaces[sec][cs][w] += 1

    p_lbl_surfaces = defaultdict(Counter)
    p_prs_surfaces = defaultdict(Counter)
    for w in sec_label_tokens["P"]:
        cs = canonical_stem(w)
        if cs in stem_idf:
            p_lbl_surfaces[cs][w] += 1
    for w in sec_prose_tokens["P"]:
        cs = canonical_stem(w)
        if cs in stem_idf:
            p_prs_surfaces[cs][w] += 1

    z_set = set(sec_stem_surfaces["Z"].keys())
    h_set = set(sec_stem_surfaces["H"].keys())
    p_set = set(sec_stem_surfaces["P"].keys())
    b_set = set(sec_stem_surfaces["B"].keys())
    s_set = set(sec_stem_surfaces["S"].keys())

    hp_set = h_set & p_set
    dual_branch_set = hp_set & b_set & s_set
    decoction_only_set = (hp_set & s_set) - b_set
    hydro_only_set = (hp_set & b_set) - s_set
    pan5_set = z_set & h_set & p_set & b_set & s_set

    def profile_stem_class(st_set):
        fams = Counter(classify_radical_family(st) for st in st_set)
        n = len(st_set) or 1
        # Collect all tokens of these stems in S and B and H and P
        h_toks = [w for w in sec_tokens["H"] if canonical_stem(w) in st_set]
        p_toks = [w for w in sec_tokens["P"] if canonical_stem(w) in st_set]
        b_toks = [w for w in sec_tokens["B"] if canonical_stem(w) in st_set]
        s_toks = [w for w in sec_tokens["S"] if canonical_stem(w) in st_set]
        return {
            "stem_count": len(st_set),
            "mean_idf": round(sum(stem_idf[st] for st in st_set) / n, 3),
            "radical_family_pct": {k: round(100.0 * v / n, 2) for k, v in fams.most_common()},
            "herbal_tokens": len(h_toks),
            "pharm_tokens": len(p_toks),
            "balneo_tokens": len(b_toks),
            "starred_tokens": len(s_toks),
            "s_qo_active_pct": round(100.0 * sum(1 for w in s_toks if w.startswith("qo")) / (len(s_toks) or 1), 2),
            "s_aiin_dose_pct": round(100.0 * sum(1 for w in s_toks if w.endswith(("aiin", "iin", "ain"))) / (len(s_toks) or 1), 2),
            "b_l_ol_applicative_pct": round(100.0 * sum(1 for w in b_toks if w.startswith(("l", "ol", "qol"))) / (len(b_toks) or 1), 2),
        }

    routing_classes = {
        "ALL_HP_APOTHECARY_STEMS": len(hp_set),
        "PAN_5SECTION_STEMS_ZHPBS": profile_stem_class(pan5_set),
        "DUAL_BRANCH_STEMS_HPBS": profile_stem_class(dual_branch_set),
        "DECOCTION_ONLY_STEMS_HPS_NOT_B": profile_stem_class(decoction_only_set),
        "HYDROTHERAPY_ONLY_STEMS_HPB_NOT_S": profile_stem_class(hydro_only_set),
    }

    # Build the Complete Word-for-Word 5-Section Inflectional Paradigm Table for all Pan-5-Section Stems (Z ∩ H ∩ P ∩ B ∩ S)
    def top_forms_str(counter_obj, limit=3):
        if not counter_obj:
            return "-"
        return ", ".join(f"{w}({c})" for w, c in counter_obj.most_common(limit))

    pan5_paradigms = []
    for cs in sorted(pan5_set, key=lambda x: -stem_idf[x]):
        pan5_paradigms.append({
            "canonical_stem": cs,
            "idf": round(stem_idf[cs], 3),
            "doc_freq": stem_doc_freq[cs],
            "radical_family": classify_radical_family(cs),
            "stage1_zodiac_Z": top_forms_str(sec_stem_surfaces["Z"][cs]),
            "stage2_herbal_H": top_forms_str(sec_stem_surfaces["H"][cs]),
            "stage3a_pharm_label_Lf": top_forms_str(p_lbl_surfaces[cs]),
            "stage3b_pharm_prose_P": top_forms_str(p_prs_surfaces[cs]),
            "branchB_balneo_bath_B": top_forms_str(sec_stem_surfaces["B"][cs]),
            "branchA_starred_recipe_S": top_forms_str(sec_stem_surfaces["S"][cs]),
        })

    # Also build paradigms for Dual-Branch Stems that have an explicit @Lf Pharmaceutical Root/Leaf Label!
    label_anchored_dual_paradigms = []
    for cs in sorted(dual_branch_set, key=lambda x: (-len(p_lbl_surfaces[x]), -stem_idf[x])):
        if p_lbl_surfaces[cs]:
            label_anchored_dual_paradigms.append({
                "canonical_stem": cs,
                "idf": round(stem_idf[cs], 3),
                "doc_freq": stem_doc_freq[cs],
                "stage1_zodiac_Z": top_forms_str(sec_stem_surfaces["Z"][cs]),
                "stage2_herbal_H": top_forms_str(sec_stem_surfaces["H"][cs]),
                "stage3a_pharm_label_Lf": top_forms_str(p_lbl_surfaces[cs]),
                "stage3b_pharm_prose_P": top_forms_str(p_prs_surfaces[cs]),
                "branchB_balneo_bath_B": top_forms_str(sec_stem_surfaces["B"][cs]),
                "branchA_starred_recipe_S": top_forms_str(sec_stem_surfaces["S"][cs]),
            })

    summary = {
        "attack_id": 113,
        "discovery_id": 130,
        "title": "The Five-Section (Z, H, P, B, S) Dual-Branch Therapeutic Routing Matrix & Exact Word-for-Word Inflectional Paradigm Table",
        "section_open_stem_counts": {
            "Z_zodiac": len(z_set),
            "H_herbal": len(h_set),
            "P_pharm": len(p_set),
            "B_balneo": len(b_set),
            "S_starred": len(s_set),
            "HP_apothecary_compiled": len(hp_set),
            "HPBS_dual_branch": len(dual_branch_set),
            "ZHPBS_pan_5section": len(pan5_set),
        },
        "therapeutic_routing_classes": routing_classes,
        "pan_5section_inflectional_paradigms": pan5_paradigms,
        "pharm_label_anchored_dual_branch_paradigms": label_anchored_dual_paradigms,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Attack 113] Saved -> {OUT_JSON}")
    print("  Open-Stem Counts:", summary["section_open_stem_counts"])
    for k, v in routing_classes.items():
        if isinstance(v, dict):
            print(f"    {k:34s}: n={v['stem_count']:3d} stems (IDF={v['mean_idf']:.2f}) | B l-/ol-={v['b_l_ol_applicative_pct']:5.2f}% | S qo-={v['s_qo_active_pct']:5.2f}% | S -aiin={v['s_aiin_dose_pct']:5.2f}% | Top Radicals={list(v['radical_family_pct'].items())[:2]}")
    print("  Top 10 Pan-5-Section (Z ∩ H ∩ P ∩ B ∩ S) Word-for-Word Inflectional Paradigms:")
    for p in pan5_paradigms[:10]:
        print(f"    [{p['canonical_stem']:8s}] (IDF={p['idf']:.2f}): Z={p['stage1_zodiac_Z']} | H={p['stage2_herbal_H']} | P_lbl={p['stage3a_pharm_label_Lf']} | P_prs={p['stage3b_pharm_prose_P']} | B={p['branchB_balneo_bath_B']} | S={p['branchA_starred_recipe_S']}")


if __name__ == "__main__":
    main()
