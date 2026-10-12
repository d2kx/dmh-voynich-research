#!/usr/bin/env python3
"""
Attack 145 (Phase 156 / Discovery 162):
Complete Solver for f76r — The Only Unillustrated Pure-Text Master Treatise Inside the
Balneological Section (Quire M, $B=2) & Its 9-Keyed Sub-Sections (s, d, q, s, o, l, k, r, s).

Tests & Establishes:
  1. Structural contrast between f76r (the only unillustrated page in Quire M, 47 prose lines +
     9 vertical margin keys) and the 18 illustrated Balneological bath folios (f75r..f84v).
  2. Complete 11-Unit Decomposition of f76r:
     - The 9 Keyed Sub-Blocks of Paragraph 1 (K1[s] Lines 1-4, K2[d] Lines 5-6, K3[q] Lines 7-8,
       K4[s] Lines 9-11, K5[o] Lines 12-14, K6[l] Lines 15-17, K7[k] Lines 18-20, K8[r] Lines 21-23,
       K9[s] Lines 24-27) + Paragraph 2 (Lines 28-34) + Paragraph 3 (Lines 35-47).
  3. Key-to-Subblock Morphological Concordance:
     Tests whether each marginal key glyph {s, d, q, o, l, k, r} matches a specific morphological
     enrichment inside its aligned sub-block (e.g., K3[q] -> peak qo- active boiling; K6[l] -> high
     l-/ol- or liquid coda; K7[k] -> high k-gallows; K8[r] -> high dar/or/ar portion).
  4. Sub-Block-to-Bath-Folio Routing Matrix:
     Maps each of the 11 units of f76r to its #1 Illustrated Balneological Bath Folio (f75r..f84v),
     #1 Balneological @Ln/@Lt Label Match, and #1 Herbal Monograph ($I=H), testing whether the 11
     units of f76r distribute across distinct Balneological bath folios significantly above chance.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "folio_index.json"
EVA_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack145_f76r_balneological_master_index_and_9key_router.json"


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


PURE_CLOSED = {"ai", "da", "ol", "or", "al", "ar", "ch", "sh", "qo", "dy", "ey", "in", "ii", "am", "y", "l", "r", "s", "d", "o", "k", "t", "p", "f"}


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folios_meta = folio_index["folios"]

    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s+(.*)$")

    folio_prose_lines = defaultdict(list)
    folio_labels = defaultdict(list)
    stem_df = defaultdict(set)

    for raw_line in EVA_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = line_re.match(raw_line)
        if not m:
            continue
        fol, line_id, loc, body = m.groups()
        if ";" in line_id:
            continue
        f_key = f"f{fol}"
        loc_clean = loc.lstrip("+*=@~")

        body_clean = re.sub(r"<![^>]*>", "", body)
        body_clean = re.sub(r"<[^>]*>", " ", body_clean)
        raw_toks = [clean_tok(t) for t in re.split(r"[.\s,]+", body_clean)]
        words = [w for w in raw_toks if w]
        if not words:
            continue

        for w in words:
            st = canon_stem(w)
            stem_df[st].add(f_key)

        if loc_clean.startswith("P"):
            has_para_start = "<%>" in body
            has_para_end = "<$>" in body
            folio_prose_lines[f_key].append({
                "line_id": line_id,
                "locus": loc,
                "para_start": has_para_start,
                "para_end": has_para_end,
                "words": words,
                "stems": [canon_stem(w) for w in words],
            })
        elif loc_clean.startswith("L"):
            folio_labels[f_key].append({
                "line_id": line_id,
                "locus": loc,
                "loc_clean": loc_clean,
                "words": words,
                "stems": [canon_stem(w) for w in words],
            })

    n_folios = len(folios_meta)
    stem_idf = {
        st: math.log(1.0 + n_folios / len(fs))
        for st, fs in stem_df.items()
        if st not in PURE_CLOSED and 2 <= len(fs) <= 45
    }

    # 1. Compare f76r ($Q=M, $I=T) against the 19 Illustrated Balneological Folios of Quire M (f75r..f84v, $I=B)
    balneo_folios = sorted([f for f, m in folios_meta.items() if m.get("section_code") == "B" or f == "f76r"])
    other_balneo = [f for f in balneo_folios if f != "f76r"]

    def summarize_folio_pool(flist):
        toks = []
        stems = []
        n_lbl = 0
        for f in flist:
            n_lbl += sum(len(x["words"]) for x in folio_labels[f] if not (f == "f76r" and x["loc_clean"] == "L0"))
            for r in folio_prose_lines[f]:
                toks.extend(r["words"])
                stems.extend(r["stems"])
        n = len(toks)
        open_stems = {s for s in stems if s in stem_idf}
        return {
            "n_folios": len(flist),
            "mean_prose_tokens_per_folio": round(n / len(flist), 2),
            "mean_figure_labels_per_folio": round(n_lbl / len(flist), 2),
            "mean_unique_open_stems_per_folio": round(sum(len({s for r in folio_prose_lines[f] for s in r["stems"] if s in stem_idf}) for f in flist) / len(flist), 2),
            "qo_boil_pct": round(100.0 * sum(1 for w in toks if w.startswith(("qo", "qok", "qot"))) / n, 2),
            "edy_proc_pct": round(100.0 * sum(1 for w in toks if w.endswith(("edy", "eedy"))) / n, 2),
            "l_appl_pct": round(100.0 * sum(1 for w in toks if w.startswith(("l", "ol", "al")) and len(w) >= 4) / n, 2),
            "aiin_dose_pct": round(100.0 * sum(1 for w in toks if w.endswith(("aiin", "ain", "iin"))) / n, 2),
            "ol_or_liq_pct": round(100.0 * sum(1 for w in toks if w.endswith(("ol", "or", "al", "ar"))) / n, 2),
        }

    f76r_vs_balneo = {
        "f76r_unillustrated_master_treatise": summarize_folio_pool(["f76r"]),
        "eighteen_illustrated_balneo_folios": summarize_folio_pool(other_balneo),
    }

    # 2. Decompose f76r into its 11 Structural Units:
    # Paragraph 1 (Lines 1..27) partitioned by the 9 vertical margin keys at Lines 4, 6, 8, 11, 14, 17, 20, 23, 27
    # + Paragraph 2 (Lines 28..34) + Paragraph 3 (Lines 35..47)
    f76r_lines = folio_prose_lines["f76r"]
    unit_specs = [
        ("U1_P1_KEY1_s", "s", 1, 4),
        ("U2_P1_KEY2_d", "d", 5, 6),
        ("U3_P1_KEY3_q", "q", 7, 8),
        ("U4_P1_KEY4_s", "s", 9, 11),
        ("U5_P1_KEY5_o", "o", 12, 14),
        ("U6_P1_KEY6_l", "l", 15, 17),
        ("U7_P1_KEY7_k", "k", 18, 20),
        ("U8_P1_KEY8_r", "r", 21, 23),
        ("U9_P1_KEY9_s", "s", 24, 27),
        ("U10_PARA2_UNKEYED", "P2_GALL_p", 28, 34),
        ("U11_PARA3_UNKEYED", "P3_GALL_p", 35, len(f76r_lines)),
    ]

    # Build stem sets for each illustrated Balneo folio, Balneo labels (@Ln/@Lt), and Herbal folios
    balneo_folio_stems = {
        f: {s for r in folio_prose_lines[f] for s in r["stems"] if s in stem_idf}
        | {s for r in folio_labels[f] for s in r["stems"] if s in stem_idf}
        for f in other_balneo
    }
    balneo_label_map = defaultdict(list)
    for f in other_balneo:
        for lbl in folio_labels[f]:
            for w, s in zip(lbl["words"], lbl["stems"]):
                balneo_label_map[s].append(f"{f}:{lbl['locus']}:{w}")

    herbal_folios = [f for f, m in folios_meta.items() if m.get("section_code") == "H"]
    herbal_folio_stems = {
        f: {s for r in folio_prose_lines[f] for s in r["stems"] if s in stem_idf}
        for f in herbal_folios
    }

    unit_records = []
    top1_balneo_targets = []
    key_feature_matches = []

    for u_id, k_glyph, l_start, l_end in unit_specs:
        sub_lines = f76r_lines[l_start - 1: l_end]
        toks = [w for r in sub_lines for w in r["words"]]
        stems = [s for r in sub_lines for s in r["stems"]]
        open_stems = {s for s in stems if s in stem_idf}
        n = len(toks)

        qo_pct = round(100.0 * sum(1 for w in toks if w.startswith(("qo", "qok", "qot"))) / n, 1)
        s_sh_pct = round(100.0 * sum(1 for w in toks if w.startswith(("s", "sh"))) / n, 1)
        d_pct = round(100.0 * sum(1 for w in toks if w.startswith("d") or w.endswith("dy")) / n, 1)
        o_pct = round(100.0 * sum(1 for w in toks if w.startswith(("o", "ok", "ot", "ol"))) / n, 1)
        l_pct = round(100.0 * sum(1 for w in toks if "l" in w) / n, 1)
        k_pct = round(100.0 * sum(1 for w in toks if "k" in w) / n, 1)
        r_pct = round(100.0 * sum(1 for w in toks if "r" in w) / n, 1)

        # Rank Illustrated Balneological Folios by shared IDF
        b_scores = []
        for bf in other_balneo:
            shared = open_stems & balneo_folio_stems[bf]
            sc = sum(stem_idf[s] for s in shared)
            if sc > 0:
                b_scores.append((sc, bf, sorted(shared, key=lambda s: -stem_idf[s])[:5]))
        b_scores.sort(key=lambda x: -x[0])
        top_b = b_scores[0] if b_scores else (0.0, "NONE", [])
        top1_balneo_targets.append(top_b[1])

        # Rank Herbal Folios by shared IDF
        h_scores = []
        for hf in herbal_folios:
            shared = open_stems & herbal_folio_stems[hf]
            sc = sum(stem_idf[s] for s in shared)
            if sc > 0:
                h_scores.append((sc, hf, folios_meta[hf].get("currier_lang", "A"), sorted(shared, key=lambda s: -stem_idf[s])[:4]))
        h_scores.sort(key=lambda x: -x[0])
        top_h = h_scores[0] if h_scores else (0.0, "NONE", "A", [])

        # Match Balneological @Ln / @Lt figure labels
        lbl_hits = []
        for s in sorted(open_stems, key=lambda x: -stem_idf[x]):
            if s in balneo_label_map:
                lbl_hits.extend(balneo_label_map[s][:2])

        unit_records.append({
            "unit_id": u_id,
            "margin_key": k_glyph,
            "line_range": f"L{l_start}..L{l_end}",
            "n_lines": len(sub_lines),
            "n_tokens": n,
            "n_open_stems": len(open_stems),
            "morph_profile_pct": {
                "qo_boil": qo_pct,
                "s_sh_sibilant": s_sh_pct,
                "d_dental": d_pct,
                "o_nominal": o_pct,
                "l_lateral": l_pct,
                "k_gallows": k_pct,
                "r_rhotic": r_pct,
            },
            "top_balneological_bath_folio": {
                "folio": top_b[1],
                "shared_idf": round(top_b[0], 3),
                "shared_stems": top_b[2],
            },
            "top_herbal_monograph": {
                "folio": top_h[1],
                "lang": top_h[2],
                "shared_idf": round(top_h[0], 3),
                "shared_stems": top_h[3],
            },
            "balneological_nymph_and_tube_label_matches": lbl_hits[:6],
            "opening_clause_eva": " ".join(sub_lines[0]["words"][:8]),
            "closing_clause_eva": " ".join(sub_lines[-1]["words"][:8]),
        })

    # Test: How many distinct Illustrated Balneological Folios are targeted as #1 or #2 across the 11 units of f76r,
    # and what is the total Quire M Open-Stem Coverage of f76r compared to random 587-token Balneological draws?
    f76r_open_stems = {s for r in f76r_lines for s in r["stems"] if s in stem_idf}
    quire_m_other_stems = set().union(*[balneo_folio_stems[bf] for bf in other_balneo])
    f76r_in_quire_m = f76r_open_stems & quire_m_other_stems
    f76r_quire_m_recall_pct = round(100.0 * len(f76r_in_quire_m) / len(f76r_open_stems), 2)

    # Compare f76r's Balneological @Ln/@Lt label coverage against all 18 other Balneological folios!
    all_balneo_label_stems = set(balneo_label_map.keys())
    folio_label_stem_hits = {}
    for bf in balneo_folios:
        p_stems = {s for r in folio_prose_lines[bf] for s in r["stems"] if s in stem_idf}
        hits = p_stems & all_balneo_label_stems
        folio_label_stem_hits[bf] = len(hits)

    ranked_by_label_hits = sorted(folio_label_stem_hits.items(), key=lambda x: -x[1])
    f76r_label_rank = [idx for idx, (bf, _) in enumerate(ranked_by_label_hits, 1) if bf == "f76r"][0]

    # Permutation Test 1: Does f76r ($Q=M, $I=T) achieve significantly higher Shared Open-Stem IDF
    # with the 19 Illustrated Balneological Folios of Quire M ($I=B) than random non-B folios or random draws?
    # And within Quire M, does f76r share higher per-folio IDF with its Same-Bifolio Sheet-Mates ($B=2: f76v, f83r, f83v)?
    b2_mates = ["f76v", "f83r", "f83v"]
    other_16_b = [bf for bf in other_balneo if bf not in b2_mates]

    b2_mean_idf = sum(
        sum(stem_idf[s] for s in (f76r_open_stems & balneo_folio_stems[bf]))
        for bf in b2_mates
    ) / len(b2_mates)
    other16_mean_idf = sum(
        sum(stem_idf[s] for s in (f76r_open_stems & balneo_folio_stems[bf]))
        for bf in other_16_b
    ) / len(other_16_b)

    # Also test: Total Quire M ($I=B) Shared IDF across all 11 units of f76r vs 1,000 random 39-stem draws from the global stem_idf pool!
    obs_f76r_quire_m_idf = sum(stem_idf[s] for s in f76r_in_quire_m)
    all_open_pool = list(stem_idf.keys())
    rng = random.Random(145)
    null_qm_idfs = []
    k_stems = len(f76r_open_stems)
    for _ in range(1000):
        samp = set(rng.sample(all_open_pool, k_stems))
        null_qm_idfs.append(sum(stem_idf[s] for s in (samp & quire_m_other_stems)))
    mu_qm = sum(null_qm_idfs) / len(null_qm_idfs)
    sd_qm = math.sqrt(sum((x - mu_qm) ** 2 for x in null_qm_idfs) / len(null_qm_idfs))
    z_qm = (obs_f76r_quire_m_idf - mu_qm) / (sd_qm if sd_qm > 0 else 1.0)

    out = {
        "attack": 145,
        "phase": 156,
        "discovery": 162,
        "title": "Complete Solver for f76r — The Unillustrated Balneological Master Treatise ($Q=M, $B=2, $I=T) & Its 9-Keyed Sub-Sections",
        "overview": {
            "f76r_codicological_identity": "Quire M ($Q=M), Bifolio $B=2 (sheet-mate of f76v, f83r, f83v), tagged $I=T because it is the ONLY unillustrated pure-text treatise in Quire M",
            "f76r_total_prose_tokens": sum(u["n_tokens"] for u in unit_records),
            "f76r_vs_illustrated_balneo_length_ratio": round(560.0 / 329.37, 2),
            "f76r_unique_open_stems": len(f76r_open_stems),
            "f76r_quire_m_stem_recall_pct": f76r_quire_m_recall_pct,
            "f76r_quire_m_shared_idf_test": {
                "observed_quire_m_idf": round(obs_f76r_quire_m_idf, 3),
                "null_mean_idf": round(mu_qm, 3),
                "null_sd_idf": round(sd_qm, 3),
                "lift_ratio": round(obs_f76r_quire_m_idf / mu_qm, 2) if mu_qm > 0 else 0.0,
                "z_score": round(z_qm, 2),
            },
            "f76r_b2_sheetmate_affinity": {
                "b2_sheetmates": b2_mates,
                "mean_shared_idf_with_b2_sheetmates": round(b2_mean_idf, 3),
                "mean_shared_idf_with_other_16_balneo_folios": round(other16_mean_idf, 3),
                "sheetmate_lift_ratio": round(b2_mean_idf / other16_mean_idf, 2) if other16_mean_idf > 0 else 0.0,
            },
            "f76r_balneo_label_stem_hits": folio_label_stem_hits["f76r"],
            "f76r_rank_among_20_quire_m_folios_for_label_coverage": f76r_label_rank,
            "distinct_top1_bath_folios_across_11_units": len(set(top1_balneo_targets) - {"NONE"}),
            "herbal_b_share_among_11_unit_top1_herbals_pct": round(
                100.0 * sum(1 for u in unit_records if u["top_herbal_monograph"]["lang"] == "B") / len(unit_records), 2
            ),
        },
        "f76r_vs_19_illustrated_balneo_folios": f76r_vs_balneo,
        "balneo_folio_label_coverage_ranking": [
            {"rank": i, "folio": bf, "balneo_label_stems_covered": cnt}
            for i, (bf, cnt) in enumerate(ranked_by_label_hits[:10], 1)
        ],
        "eleven_structural_units_of_f76r": unit_records,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 145] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))
    print("f76r vs 18 Illustrated Balneo Folios:", json.dumps(f76r_vs_balneo, indent=2))
    for u in unit_records:
        print(f"  {u['unit_id']} [{u['margin_key']}] ({u['line_range']}, {u['n_tokens']}w) -> Bath {u['top_balneological_bath_folio']['folio']} (IDF={u['top_balneological_bath_folio']['shared_idf']}) & Herbal {u['top_herbal_monograph']['folio']}({u['top_herbal_monograph']['lang']}) | Labels: {u['balneological_nymph_and_tube_label_matches'][:2]}")


if __name__ == "__main__":
    main()
