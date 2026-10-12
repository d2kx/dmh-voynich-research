#!/usr/bin/env python3
"""
Attack 110 (Discovery 127): The Balneological (`Quire M`, `f75r–f84v`, `$I=B`)
Hydrotherapy-to-Zodiac & Herbal-Infusion Network

Tests:
1. Extracts open-class canonical stems (excluding Top-45 Canonical Stems, `len >= 3`, `2 <= df <= 95`)
   across all `20` Balneological folios (`f75r–f84v`, `$I=B, $Q=M, $H=2`, grouped into their `5` physical
   bifolios `$B=1..5: f75/f84, f76/f83, f77/f82, f78/f81, f79/f80`).
2. Measures the **Herbal Infusion Selectivity** of the `20` Balneological folios across all `128`
   Herbal Monographs (`32` Currier B vs. `96` Currier A):
   - What percentage of the `20` Balneological folios select a **Currier B Herbal Monograph (`$L=B`)**
     as their `#1` highest-IDF botanical partner (vs. the `25.00%` Herbal-B folio baseline)?
   - Runs a 1,000-trial permutation test on the mean `#1` Botanical Partner IDF of the `20` Balneological folios.
3. Reconstructs **Three-Stage Herbal-to-Bath Chains (`Herbal $I=H -> Pharmaceutical $I=P -> Balneological Bath $I=B`)**
   and **Four-Stage Astro-Balneological Tetrads (`Zodiac Nymph Medallion $I=Z -> Herbal $I=H -> Pharm $I=P -> Bath $I=B`)**,
   testing significance with a 200-trial within-section multiset permutation test.
4. Profiles the **Morphological Transformation across Shared Hydrotherapy Stems (`H -> P -> B -> S`)**
   and across the `5` nested physical bifolios (`$B=1` outer sheet `f75/f84` to `$B=5` centerfold `f79/f80`).
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
OUT_JSON = DATA_DIR / "attack110_balneological_to_zodiac_and_herbal_infusion_network.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

ZODIAC_META = {
    "f70v2": ("Pisces", "March", "SPRING"),
    "f70v1": ("Aries (Dark)", "April", "SPRING"),
    "f71r":  ("Aries (Light)", "April", "SPRING"),
    "f71v":  ("Taurus (Light)", "May", "SPRING"),
    "f72r1": ("Taurus (Dark)", "May", "SPRING"),
    "f72r2": ("Gemini", "June", "SUMMER"),
    "f72r3": ("Cancer", "July", "SUMMER"),
    "f72v3": ("Leo", "August", "SUMMER"),
    "f72v2": ("Virgo", "September", "AUTUMN"),
    "f72v1": ("Libra", "October", "AUTUMN"),
    "f73r":  ("Scorpio", "November", "AUTUMN"),
    "f73v":  ("Sagittarius", "December", "WINTER"),
}


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

    b_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "B"], key=lambda x: (int(re.findall(r"\d+", x)[0]), x))
    z_folios = sorted(ZODIAC_META.keys())
    h_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "H" and len(folio_prose_tokens[f]) >= 15])
    p_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "P" and len(folio_all_tokens[f]) >= 15])

    b_stems = {bf: {canonical_stem(w) for w in folio_all_tokens[bf] if canonical_stem(w) in stem_idf} for bf in b_folios}
    b_lbl_stems = {bf: {canonical_stem(w) for w in folio_label_tokens[bf] if canonical_stem(w) in stem_idf} for bf in b_folios}
    z_stems = {zf: {canonical_stem(w) for w in folio_all_tokens[zf] if canonical_stem(w) in stem_idf} for zf in z_folios}
    h_stems = {hf: {canonical_stem(w) for w in folio_prose_tokens[hf] if canonical_stem(w) in stem_idf} for hf in h_folios}
    p_stems = {pf: {canonical_stem(w) for w in folio_all_tokens[pf] if canonical_stem(w) in stem_idf} for pf in p_folios}
    p_lbl_stems = {pf: {canonical_stem(w) for w in folio_label_tokens[pf] if canonical_stem(w) in stem_idf} for pf in p_folios}

    # 1. Balneological Folio-by-Folio Top Herbal, Top Pharm, and Top Zodiac Correspondences
    balneo_profiles = []
    hb_top1_count = 0
    for bf in b_folios:
        bst = b_stems[bf]
        # Top Herbal
        h_scores = []
        for hf in h_folios:
            inter = bst & h_stems[hf]
            if inter:
                h_scores.append((hf, folio_meta[hf].get("L", "U"), folio_meta[hf].get("Q", "U"), round(sum(stem_idf[s] for s in inter), 3), sorted(inter, key=lambda x: -stem_idf[x])))
        h_scores.sort(key=lambda x: -x[3])
        if h_scores and h_scores[0][1] == "B":
            hb_top1_count += 1

        # Top Pharm
        p_scores = []
        for pf in p_folios:
            inter = bst & p_stems[pf]
            if inter:
                lbl_hits = sorted(inter & p_lbl_stems[pf])
                p_scores.append((pf, round(sum(stem_idf[s] for s in inter), 3), sorted(inter, key=lambda x: -stem_idf[x]), lbl_hits))
        p_scores.sort(key=lambda x: -x[1])

        # Top Zodiac
        z_scores = []
        for zf in z_folios:
            inter = bst & z_stems[zf]
            if inter:
                z_scores.append((zf, ZODIAC_META[zf][0], ZODIAC_META[zf][1], round(sum(stem_idf[s] for s in inter), 3), sorted(inter, key=lambda x: -stem_idf[x])))
        z_scores.sort(key=lambda x: -x[3])

        balneo_profiles.append({
            "balneo_folio": bf,
            "bifolio": folio_meta[bf].get("B", "U"),
            "tokens": len(folio_all_tokens[bf]),
            "nymph_labels": len(folio_label_tokens[bf]),
            "open_stems": len(bst),
            "top_herbal": {
                "folio": h_scores[0][0],
                "lang": h_scores[0][1],
                "quire": h_scores[0][2],
                "idf": h_scores[0][3],
                "stems": h_scores[0][4],
            } if h_scores else None,
            "second_herbal": {
                "folio": h_scores[1][0],
                "lang": h_scores[1][1],
                "idf": h_scores[1][3],
                "stems": h_scores[1][4],
            } if len(h_scores) > 1 else None,
            "top_pharm": {
                "folio": p_scores[0][0],
                "idf": p_scores[0][1],
                "stems": p_scores[0][2],
                "label_hits": p_scores[0][3],
            } if p_scores else None,
            "top_zodiac": {
                "folio": z_scores[0][0],
                "sign": z_scores[0][1],
                "month": z_scores[0][2],
                "idf": z_scores[0][3],
                "stems": z_scores[0][4],
            } if z_scores else None,
        })

    # 2. Three-Stage (H ∩ P ∩ B) and Four-Stage (Z ∩ H ∩ P ∩ B) Hydrotherapy Chains
    hpb_triads_3plus = []
    zhpb_tetrads_2plus = []
    for bf in b_folios:
        bst = b_stems[bf]
        for hf in h_folios:
            hb = bst & h_stems[hf]
            if len(hb) < 2:
                continue
            for pf in p_folios:
                hpb = hb & p_stems[pf]
                if len(hpb) >= 3:
                    lbl_hits = sorted(hpb & (p_lbl_stems[pf] | b_lbl_stems[bf]))
                    sc = sum(stem_idf[s] for s in hpb)
                    hpb_triads_3plus.append({
                        "herbal_folio": hf,
                        "herbal_lang": folio_meta[hf].get("L", "U"),
                        "pharm_folio": pf,
                        "balneo_folio": bf,
                        "balneo_bifolio": folio_meta[bf].get("B", "U"),
                        "shared_count": len(hpb),
                        "shared_stems": sorted(hpb, key=lambda x: -stem_idf[x]),
                        "label_anchored_stems": lbl_hits,
                        "idf_score": round(sc, 3),
                    })
                if len(hpb) >= 2:
                    for zf in z_folios:
                        zhpb = hpb & z_stems[zf]
                        if len(zhpb) >= 2:
                            zhpb_tetrads_2plus.append({
                                "zodiac_folio": zf,
                                "zodiac_sign": ZODIAC_META[zf][0],
                                "herbal_folio": hf,
                                "herbal_lang": folio_meta[hf].get("L", "U"),
                                "pharm_folio": pf,
                                "balneo_folio": bf,
                                "shared_4stage_count": len(zhpb),
                                "shared_4stage_stems": sorted(zhpb, key=lambda x: -stem_idf[x]),
                                "hpb_shared_stems": sorted(hpb, key=lambda x: -stem_idf[x]),
                                "idf_4stage": round(sum(stem_idf[s] for s in zhpb), 3),
                            })

    hpb_triads_3plus.sort(key=lambda x: (-x["shared_count"], -x["idf_score"]))
    zhpb_tetrads_2plus.sort(key=lambda x: (-x["shared_4stage_count"], -x["idf_4stage"]))

    # 3. 200-Trial Within-Section Multiset Permutation Test for H∩P∩B (>=3 stems) and Z∩H∩P∩B (>=2 stems)
    rng = random.Random(2026110)
    z_pool = [st for zf in z_folios for st in z_stems[zf]]
    h_pool = [st for hf in h_folios for st in h_stems[hf]]
    p_pool = [st for pf in p_folios for st in p_stems[pf]]
    b_pool = [st for bf in b_folios for st in b_stems[bf]]

    z_sizes = [len(z_stems[zf]) for zf in z_folios]
    h_sizes = [len(h_stems[hf]) for hf in h_folios]
    p_sizes = [len(p_stems[pf]) for pf in p_folios]
    b_sizes = [len(b_stems[bf]) for bf in b_folios]

    obs_hpb3 = len(hpb_triads_3plus)
    obs_zhpb2 = len(zhpb_tetrads_2plus)
    null_hpb3 = []
    null_zhpb2 = []

    for _ in range(200):
        rng.shuffle(z_pool)
        rng.shuffle(h_pool)
        rng.shuffle(p_pool)
        rng.shuffle(b_pool)

        idx = 0
        sim_z = []
        for sz in z_sizes:
            sim_z.append(set(z_pool[idx:idx + sz]))
            idx += sz

        idx = 0
        sim_h = []
        for sz in h_sizes:
            sim_h.append(set(h_pool[idx:idx + sz]))
            idx += sz

        idx = 0
        sim_p = []
        for sz in p_sizes:
            sim_p.append(set(p_pool[idx:idx + sz]))
            idx += sz

        idx = 0
        sim_b = []
        for sz in b_sizes:
            sim_b.append(set(b_pool[idx:idx + sz]))
            idx += sz

        c_hpb3 = 0
        c_zhpb2 = 0
        for bst in sim_b:
            for hst in sim_h:
                hb = bst & hst
                if len(hb) < 2:
                    continue
                for pst in sim_p:
                    hpb = hb & pst
                    if len(hpb) >= 3:
                        c_hpb3 += 1
                    if len(hpb) >= 2:
                        for zst in sim_z:
                            if len(hpb & zst) >= 2:
                                c_zhpb2 += 1
        null_hpb3.append(c_hpb3)
        null_zhpb2.append(c_zhpb2)

    def calc_z(obs, arr):
        m = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - m) ** 2 for x in arr) / len(arr)) or 1e-9
        return round(m, 2), round(sd, 2), round((obs - m) / sd, 2)

    m_hpb3, sd_hpb3, z_hpb3 = calc_z(obs_hpb3, null_hpb3)
    m_zhpb2, sd_zhpb2, z_zhpb2 = calc_z(obs_zhpb2, null_zhpb2)

    # 4. Morphological Transformation across Shared Hydrotherapy Stems (H -> P -> B)
    shared_hpb_stems = {st for t in hpb_triads_3plus for st in t["shared_stems"]}

    def profile_shared(word_list):
        matched = [w for w in word_list if canonical_stem(w) in shared_hpb_stems]
        n = len(matched) or 1
        return {
            "matched_tokens": len(matched),
            "o_nominal_pct": round(100.0 * sum(1 for w in matched if w.startswith("o") and not w.startswith("qo")) / n, 2),
            "qo_active_pct": round(100.0 * sum(1 for w in matched if w.startswith("qo")) / n, 2),
            "l_ol_applicative_pct": round(100.0 * sum(1 for w in matched if w.startswith(("l", "ol", "qol"))) / n, 2),
            "edy_process_pct": round(100.0 * sum(1 for w in matched if w.endswith(("edy", "eedy"))) / n, 2),
            "dy_state_pct": round(100.0 * sum(1 for w in matched if w.endswith("dy") and not w.endswith(("edy", "eedy"))) / n, 2),
            "aiin_measure_pct": round(100.0 * sum(1 for w in matched if w.endswith(("aiin", "iin", "ain"))) / n, 2),
            "ol_or_al_ar_liquid_pct": round(100.0 * sum(1 for w in matched if w.endswith(("ol", "or", "al", "ar"))) / n, 2),
        }

    h_all_w = [w for hf in h_folios for w in folio_prose_tokens[hf]]
    p_all_w = [w for pf in p_folios for w in folio_all_tokens[pf]]
    b_lbl_w = [w for bf in b_folios for w in folio_label_tokens[bf]]
    b_prs_w = [w for bf in b_folios for w in folio_prose_tokens[bf]]

    hydro_transformation = {
        "shared_hpb_stems_count": len(shared_hpb_stems),
        "STAGE_1_HERBAL_PROSE": profile_shared(h_all_w),
        "STAGE_2_PHARM_FORMULARY": profile_shared(p_all_w),
        "STAGE_3A_BALNEO_NYMPH_LABELS": profile_shared(b_lbl_w),
        "STAGE_3B_BALNEO_POOL_PROSE": profile_shared(b_prs_w),
    }

    hb_folio_share = round(100.0 * sum(1 for hf in h_folios if folio_meta[hf].get("L") == "B") / len(h_folios), 2)
    hb_top1_pct = round(100.0 * hb_top1_count / len(b_folios), 2)

    summary = {
        "attack_id": 110,
        "discovery_id": 127,
        "title": "The Balneological (Quire M, f75r-f84v) Hydrotherapy-to-Zodiac & Herbal-Infusion Network",
        "herbal_b_selectivity": {
            "balneo_folios_count": len(b_folios),
            "herbal_b_top1_matches": hb_top1_count,
            "herbal_b_top1_pct": hb_top1_pct,
            "herbal_b_folio_baseline_pct": hb_folio_share,
            "enrichment_ratio": round(hb_top1_pct / (hb_folio_share or 1e-9), 2),
        },
        "permutation_tests": {
            "hpb_3plus_triads_obs": obs_hpb3,
            "hpb_3plus_triads_null_mean": m_hpb3,
            "hpb_3plus_triads_null_std": sd_hpb3,
            "hpb_3plus_triads_z": z_hpb3,
            "zhpb_2plus_tetrads_obs": obs_zhpb2,
            "zhpb_2plus_tetrads_null_mean": m_zhpb2,
            "zhpb_2plus_tetrads_null_std": sd_zhpb2,
            "zhpb_2plus_tetrads_z": z_zhpb2,
        },
        "hydrotherapy_morphological_transformation": hydro_transformation,
        "balneological_20folio_atlas": balneo_profiles,
        "top_20_hpb_3stage_triads": hpb_triads_3plus[:20],
        "top_20_zhpb_4stage_tetrads": zhpb_tetrads_2plus[:20],
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Attack 110] Saved -> {OUT_JSON}")
    print(f"  Herbal-B #1 Partner Selectivity across 20 Balneological Folios: {hb_top1_count}/20 = {hb_top1_pct}% vs {hb_folio_share}% baseline ({hb_top1_pct/hb_folio_share:.2f}x enrichment)")
    print(f"  3-Stage (H ∩ P ∩ B >= 3 stems) Triads : {obs_hpb3} (null={m_hpb3}+/-{sd_hpb3}, z={z_hpb3:+.2f})")
    print(f"  4-Stage (Z ∩ H ∩ P ∩ B >= 2 stems) Tetrads: {obs_zhpb2} (null={m_zhpb2}+/-{sd_zhpb2}, z={z_zhpb2:+.2f})")
    for k, v in hydro_transformation.items():
        if isinstance(v, dict):
            print(f"    {k:30s}: n={v['matched_tokens']:4d} | o-={v['o_nominal_pct']:5.2f}% | qo-={v['qo_active_pct']:5.2f}% | l-/ol-={v['l_ol_applicative_pct']:5.2f}% | -edy={v['edy_process_pct']:5.2f}% | -ol/-or={v['ol_or_al_ar_liquid_pct']:5.2f}%")


if __name__ == "__main__":
    main()
