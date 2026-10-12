#!/usr/bin/env python3
"""
Attack 114 (Discovery 131): The Currier A -> Currier B Cross-Dialect Apothecary Compiler
— Proving That the `16` Pharmaceutical Formularies (`$I=P, $L=A`) & `f58r/f58v` Master Index (`$L=A`)
Relay the `96` Currier A Herbal Monographs into the Currier B Clinical Sections (`$I=S, B`)

Tests:
1. Partitions all `1,124` Open-Class Canonical Stems in the Herbal Section (`$I=H`, excluding Top-45
   Canonical Stems, `len >= 3`, `2 <= df <= 95`) into three disjoint pools:
   - `HERBAL_A_EXCLUSIVE (H_A \\ H_B)`: Botanical stems attested ONLY in the `96` Currier A Herbal Monographs,
   - `HERBAL_B_EXCLUSIVE (H_B \\ H_A)`: Botanical stems attested ONLY in the `32` Currier B Herbal Monographs,
   - `HERBAL_AB_SHARED (H_A ∩ H_B)`: Core botanical stems attested in BOTH Currier A and Currier B Herbals.
2. Tests the **Apothecary Relay / Mediated Compilation Law**:
   - Among `HERBAL_A_EXCLUSIVE` stems (`H_A \\ H_B`), compares the rate at which stems **compiled into
     the Currier A Apothecary Formularies (`P ∪ f58`)** reach the **Currier B Clinical Sections (`Quire 20 Starred
     Recipes S_Q20 ∪ Balneological Baths B`)** vs. `HERBAL_A_EXCLUSIVE` stems **not compiled into `P ∪ f58`**,
     computing the exact Relay Odds Ratio, Enrichment Lift, and 1,000-trial permutation z-score!
3. Extracts concrete **Cross-Dialect Surface Rewrite Chains (`Stage 1 H_A [$L=A, $H=1] -> Stage 2 P_A [$L=A, $H=1/4] -> Stage 3 S_B/B_B [$L=B, $H=2/3]`)**,
   demonstrating how Scribe 1's Currier A surface words (`p/f` gallows, `-ody/-dy`, single `e`, unplumed `ch`)
   are systematically rewritten into Scribe 2/3's Currier B clinical words (`t/k` gallows, `qo-`, `-edy/-eedy`, plumed `sh`).
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
OUT_JSON = DATA_DIR / "attack114_currier_a_to_b_apothecary_compiler.json"

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


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}

    folio_meta = {}
    folio_all_tokens = defaultdict(list)
    folio_prose_tokens = defaultdict(list)
    folio_label_tokens = defaultdict(list)

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
            ltype_clean = ltype.lstrip("@+*=")
            if ltype_clean.startswith("L"):
                folio_label_tokens[cur_folio].extend(toks)
            elif ltype_clean.startswith("P"):
                folio_prose_tokens[cur_folio].extend(toks)

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

    ha_folios = [f for f, m in folio_meta.items() if m.get("I") == "H" and m.get("L") == "A"]
    hb_folios = [f for f, m in folio_meta.items() if m.get("I") == "H" and m.get("L") == "B"]
    p_folios = [f for f, m in folio_meta.items() if m.get("I") == "P"]
    f58_folios = ["f58r", "f58v"]
    sq20_folios = [f for f, m in folio_meta.items() if m.get("I") == "S" and f not in ("f58r", "f58v")]
    b_folios = [f for f, m in folio_meta.items() if m.get("I") == "B"]

    def get_stem_surfaces(flist):
        surf = defaultdict(Counter)
        for f in flist:
            for w in folio_all_tokens[f]:
                cs = canonical_stem(w)
                if cs in stem_idf:
                    surf[cs][w] += 1
        return surf

    ha_surf = get_stem_surfaces(ha_folios)
    hb_surf = get_stem_surfaces(hb_folios)
    p_surf = get_stem_surfaces(p_folios)
    f58_surf = get_stem_surfaces(f58_folios)
    apoth_surf = get_stem_surfaces(p_folios + f58_folios)
    sq20_surf = get_stem_surfaces(sq20_folios)
    b_surf = get_stem_surfaces(b_folios)
    clin_b_surf = get_stem_surfaces(sq20_folios + b_folios)

    ha_set = set(ha_surf.keys())
    hb_set = set(hb_surf.keys())
    p_set = set(p_surf.keys())
    f58_set = set(f58_surf.keys())
    apoth_set = p_set | f58_set
    sq20_set = set(sq20_surf.keys())
    b_set = set(b_surf.keys())
    clin_b_set = sq20_set | b_set

    ha_excl = ha_set - hb_set
    hb_excl = hb_set - ha_set
    hab_shared = ha_set & hb_set

    # Test 1: How do the 3 Herbal Stem Pools (HA_excl, HB_excl, HAB_shared) enter Apothecary (P ∪ f58) and Clinical B (S_Q20 ∪ B)?
    def pool_routing_stats(pool_set):
        n = len(pool_set) or 1
        in_p = pool_set & p_set
        in_f58 = pool_set & f58_set
        in_apoth = pool_set & apoth_set
        in_sq20 = pool_set & sq20_set
        in_b = pool_set & b_set
        in_clin_b = pool_set & clin_b_set
        return {
            "total_stems": len(pool_set),
            "in_pharm_P_count": len(in_p),
            "in_pharm_P_pct": round(100.0 * len(in_p) / n, 2),
            "in_f58_index_count": len(in_f58),
            "in_f58_index_pct": round(100.0 * len(in_f58) / n, 2),
            "in_apothecary_P_or_f58_count": len(in_apoth),
            "in_apothecary_P_or_f58_pct": round(100.0 * len(in_apoth) / n, 2),
            "in_quire20_S_count": len(in_sq20),
            "in_quire20_S_pct": round(100.0 * len(in_sq20) / n, 2),
            "in_balneo_B_count": len(in_b),
            "in_balneo_B_pct": round(100.0 * len(in_b) / n, 2),
            "in_clinical_B_S_or_B_count": len(in_clin_b),
            "in_clinical_B_S_or_B_pct": round(100.0 * len(in_clin_b) / n, 2),
        }

    pool_stats = {
        "HERBAL_A_EXCLUSIVE_HA_not_HB": pool_routing_stats(ha_excl),
        "HERBAL_B_EXCLUSIVE_HB_not_HA": pool_routing_stats(hb_excl),
        "HERBAL_AB_SHARED_HA_and_HB": pool_routing_stats(hab_shared),
    }

    # Test 2: The Apothecary Relay Law on HERBAL_A_EXCLUSIVE stems (`H_A \ H_B`)
    # Compare Clinical-B (S_Q20 ∪ B) adoption rate for HA_excl stems compiled into (P ∪ f58) vs NOT compiled into (P ∪ f58)
    ha_excl_in_apoth = ha_excl & apoth_set
    ha_excl_not_apoth = ha_excl - apoth_set

    relayed_to_clin_b = ha_excl_in_apoth & clin_b_set
    unrelayed_to_clin_b = ha_excl_not_apoth & clin_b_set

    rate_relayed = 100.0 * len(relayed_to_clin_b) / (len(ha_excl_in_apoth) or 1)
    rate_unrelayed = 100.0 * len(unrelayed_to_clin_b) / (len(ha_excl_not_apoth) or 1)
    relay_lift_ratio = rate_relayed / (rate_unrelayed or 1e-9)

    # 1,000-trial permutation test for Apothecary Relay Lift on HA_excl
    rng = random.Random(2026114)
    ha_excl_list = sorted(ha_excl)
    k_apoth = len(ha_excl_in_apoth)
    obs_relayed_count = len(relayed_to_clin_b)
    null_relayed_counts = []
    for _ in range(1000):
        sampled = set(rng.sample(ha_excl_list, k_apoth))
        null_relayed_counts.append(len(sampled & clin_b_set))
    m_rel = sum(null_relayed_counts) / len(null_relayed_counts)
    sd_rel = math.sqrt(sum((x - m_rel) ** 2 for x in null_relayed_counts) / len(null_relayed_counts)) or 1e-9
    z_relay = round((obs_relayed_count - m_rel) / sd_rel, 2)

    # Test 3: Concrete Cross-Dialect Surface Rewrite Chains (`H_A [$L=A] -> P/f58 [$L=A] -> S_Q20/B [$L=B]`)
    # Extract stems in `ha_excl_in_apoth & clin_b_set` (and `hab_shared & apoth_set & clin_b_set`) where the surface form changes across dialects!
    def fmt_counter(c, k=3):
        return ", ".join(f"{w}({n})" for w, n in c.most_common(k))

    cross_dialect_rewrites = []
    for cs in sorted((ha_set & apoth_set & clin_b_set), key=lambda x: (- (1 if x in ha_excl else 0), -stem_idf[x])):
        ha_top = ha_surf[cs].most_common(1)[0][0]
        ap_top = apoth_surf[cs].most_common(1)[0][0]
        cb_top = clin_b_surf[cs].most_common(1)[0][0]
        is_distinct_surface = (ha_top != cb_top) or (ap_top != cb_top)
        cross_dialect_rewrites.append({
            "canonical_stem": cs,
            "is_herbal_a_exclusive": cs in ha_excl,
            "idf": round(stem_idf[cs], 3),
            "stage1_herbal_A_forms": fmt_counter(ha_surf[cs]),
            "stage2_apothecary_A_forms": fmt_counter(apoth_surf[cs]),
            "stage3_clinical_B_forms": fmt_counter(clin_b_surf[cs]),
            "surface_shift_observed": is_distinct_surface,
            "example_rewrite_chain": f"{ha_top} (Herbal-A) -> {ap_top} (Pharm/f58-A) -> {cb_top} (Clinical-B)",
        })

    # Measure systematic orthographic shift across all tokens of (ha_set & apoth_set & clin_b_set) in HA vs P/f58 vs Clinical-B
    shared_bridge_stems = ha_set & apoth_set & clin_b_set

    def dialect_orth_profile(flist):
        toks = [w for f in flist for w in folio_all_tokens[f] if canonical_stem(w) in shared_bridge_stems]
        n = len(toks) or 1
        return {
            "tokens": len(toks),
            "qo_proclitic_pct": round(100.0 * sum(1 for w in toks if w.startswith("qo")) / n, 2),
            "o_nominal_pct": round(100.0 * sum(1 for w in toks if w.startswith("o") and not w.startswith("qo")) / n, 2),
            "l_ol_applicative_pct": round(100.0 * sum(1 for w in toks if w.startswith(("l", "ol", "qol"))) / n, 2),
            "sh_plumed_pct": round(100.0 * sum(1 for w in toks if "sh" in w) / n, 2),
            "ee_geminate_pct": round(100.0 * sum(1 for w in toks if "ee" in w) / n, 2),
            "edy_process_pct": round(100.0 * sum(1 for w in toks if w.endswith(("edy", "eedy"))) / n, 2),
            "ody_dy_state_pct": round(100.0 * sum(1 for w in toks if w.endswith("dy") and not w.endswith(("edy", "eedy"))) / n, 2),
            "p_f_gallows_pct": round(100.0 * sum(1 for w in toks if "p" in w or "f" in w) / n, 2),
        }

    orth_shift = {
        "shared_bridge_stems_count": len(shared_bridge_stems),
        "STAGE_1_HERBAL_A_96FOLIOS": dialect_orth_profile(ha_folios),
        "STAGE_2_APOTHECARY_A_P_AND_F58": dialect_orth_profile(p_folios + f58_folios),
        "STAGE_3A_QUIRE20_STARRED_B": dialect_orth_profile(sq20_folios),
        "STAGE_3B_BALNEOLOGICAL_B": dialect_orth_profile(b_folios),
    }

    summary = {
        "attack_id": 114,
        "discovery_id": 131,
        "title": "The Currier A -> Currier B Cross-Dialect Apothecary Compiler (Herbal-A -> Pharm/f58-A -> Starred/Balneo-B)",
        "herbal_stem_pool_routing": pool_stats,
        "herbal_a_exclusive_apothecary_relay_test": {
            "herbal_a_exclusive_total": len(ha_excl),
            "compiled_in_apothecary_count": len(ha_excl_in_apoth),
            "not_compiled_in_apothecary_count": len(ha_excl_not_apoth),
            "relayed_to_clinical_b_count": len(relayed_to_clin_b),
            "relayed_to_clinical_b_pct": round(rate_relayed, 2),
            "unrelayed_to_clinical_b_count": len(unrelayed_to_clin_b),
            "unrelayed_to_clinical_b_pct": round(rate_unrelayed, 2),
            "relay_enrichment_ratio": round(relay_lift_ratio, 3),
            "null_mean_relayed": round(m_rel, 2),
            "null_std_relayed": round(sd_rel, 2),
            "z_score": z_relay,
        },
        "cross_dialect_orthographic_and_inflectional_shift": orth_shift,
        "top_30_cross_dialect_rewrite_chains": [r for r in cross_dialect_rewrites if r["surface_shift_observed"]][:30],
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Attack 114] Saved -> {OUT_JSON}")
    print("  Herbal Stem Pool Routing:")
    for k, v in pool_stats.items():
        print(f"    {k:32s}: n={v['total_stems']:3d} | in P∪f58={v['in_apothecary_P_or_f58_pct']:5.2f}% ({v['in_apothecary_P_or_f58_count']}) | in S_Q20∪B={v['in_clinical_B_S_or_B_pct']:5.2f}% ({v['in_clinical_B_S_or_B_count']})")
    rt = summary["herbal_a_exclusive_apothecary_relay_test"]
    print(f"  Apothecary Relay Test on HERBAL_A_EXCLUSIVE (n={rt['herbal_a_exclusive_total']}):")
    print(f"    Compiled in P∪f58 -> Reaches Clinical-B (S_Q20∪B): {rt['relayed_to_clinical_b_count']}/{rt['compiled_in_apothecary_count']} = {rt['relayed_to_clinical_b_pct']}%")
    print(f"    Not in P∪f58      -> Reaches Clinical-B (S_Q20∪B): {rt['unrelayed_to_clinical_b_count']}/{rt['not_compiled_in_apothecary_count']} = {rt['unrelayed_to_clinical_b_pct']}% (Lift={rt['relay_enrichment_ratio']}x, z={rt['z_score']:+.2f})")
    print("  Cross-Dialect Orthographic & Inflectional Shift on Identical Bridge Stems:")
    for k, v in orth_shift.items():
        if isinstance(v, dict):
            print(f"    {k:32s}: n={v['tokens']:4d} | qo-={v['qo_proclitic_pct']:5.2f}% | sh={v['sh_plumed_pct']:5.2f}% | ee={v['ee_geminate_pct']:5.2f}% | -edy={v['edy_process_pct']:5.2f}% | -ody/-dy={v['ody_dy_state_pct']:5.2f}%")


if __name__ == "__main__":
    main()
