#!/usr/bin/env python3
"""
Attack 131 (Phase 142 / Discovery 148):
The Global 226-Folio Master Citation & Cross-Reference Graph (`G = (V_226, E_IDF)`) —
PageRank Centrality, 4-Tier Codicological Distance Decay, and the Top-25 Master
Hub Folios of the Voynich Manuscript.

Investigates:
1. Complete 226 x 226 rare-stem (`2 <= df <= 15`) IDF weight matrix `W[i, j]`
   across all 25,425 distinct folio pairs in the Voynich Manuscript.
2. Four-Tier Codicological Distance Decay across all 25,425 folio pairs:
   - Tier 1: Same Physical Bifolio Sheet-Mate (`same $Q` and `same $B`)
   - Tier 2: Same Quire, Different Bifolio (`same $Q`, `diff $B`)
   - Tier 3: Same Section (`$I`), Different Quire (`same $I`, `diff $Q`)
   - Tier 4: Cross-Section (`diff $I`)
   Verified via a 1,000-trial node-label permutation test (`z`-score).
3. Power-iteration PageRank Centrality (`alpha = 0.85`), Cross-Section Routing
   IDF Density (per 100 tokens), and 6-Domain Shannon Routing Entropy across
   all 226 folios.
4. Complete ranking of the Top-25 Global PageRank Hub Folios, Top-25 Length-
   Normalized Cross-Section Router Folios, and Top-30 Strongest Inter-Folio
   Citation Edges in the entire codex.
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
OUT_JSON = ROOT / "data" / "attack131_global_226folio_citation_pagerank_graph.json"


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


def parse_corpus():
    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx["folios"]

    folio_tokens = defaultdict(list)
    folio_bifolio = {}

    cur_fol = None
    with open(ZL_PATH, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_page = re.match(r"^<(f[0-9a-zA-Z]+)>\s*<!([^>]+)>", line)
            if m_page:
                cur_fol = m_page.group(1)
                meta_str = m_page.group(2)
                m_b = re.search(r"\$B=([0-9a-zA-Z]+)", meta_str)
                if m_b:
                    folio_bifolio[cur_fol] = m_b.group(1)
                continue
            m_line = re.match(r"^<(f[0-9a-zA-Z]+)\.([^>]+)>\s+(.*)$", line)
            if not m_line:
                continue
            fol, loc_part, text = m_line.groups()
            raw_toks = re.split(r"[.\s,]+", text)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if len(t) >= 2]
            if toks:
                folio_tokens[fol].extend(toks)

    return folio_meta, folio_tokens, folio_bifolio


def main():
    random.seed(42)
    folio_meta, folio_tokens, folio_bifolio = parse_corpus()
    folios = sorted(folio_tokens.keys(), key=lambda f: folio_meta.get(f, {}).get("pdf_pages", [{}])[0].get("pdf1_page", 999) if folio_meta.get(f, {}).get("pdf_pages") else 999)
    n_fols = len(folios)

    folio_stems = {}
    stem_df = defaultdict(set)
    for f in folios:
        sts = {canon_stem(w) for w in folio_tokens[f] if len(canon_stem(w)) >= 2}
        folio_stems[f] = sts
        for s in sts:
            stem_df[s].add(f)

    # Rare stems: 2 <= df <= 15
    stem_idf = {
        s: math.log(n_fols / len(fset))
        for s, fset in stem_df.items()
        if 2 <= len(fset) <= 15 and len(s) >= 2
    }

    # Build 226 x 226 weight matrix W[i][j]
    W = {f: defaultdict(float) for f in folios}
    shared_top = {}

    tier_weights = {
        "TIER1_SAME_BIFOLIO_SHEET": [],
        "TIER2_SAME_QUIRE_DIFF_BIFOLIO": [],
        "TIER3_SAME_SECTION_DIFF_QUIRE": [],
        "TIER4_CROSS_SECTION": [],
    }
    tier_norm_weights = {
        "TIER1_SAME_BIFOLIO_SHEET": [],
        "TIER2_SAME_QUIRE_DIFF_BIFOLIO": [],
        "TIER3_SAME_SECTION_DIFF_QUIRE": [],
        "TIER4_CROSS_SECTION": [],
    }

    all_pairs = []
    top_edges = []

    for i_idx in range(n_fols):
        fi = folios[i_idx]
        mi = folio_meta.get(fi, {})
        qi = mi.get("quire", "?")
        bi = folio_bifolio.get(fi, "?")
        si = mi.get("section_code", "?")
        ni = max(1, len(folio_stems[fi]))

        for j_idx in range(i_idx + 1, n_fols):
            fj = folios[j_idx]
            mj = folio_meta.get(fj, {})
            qj = mj.get("quire", "?")
            bj = folio_bifolio.get(fj, "?")
            sj = mj.get("section_code", "?")
            nj = max(1, len(folio_stems[fj]))

            sh = [s for s in (folio_stems[fi] & folio_stems[fj]) if s in stem_idf]
            w_ij = sum(stem_idf[s] for s in sh)
            w_norm = w_ij / math.sqrt(ni * nj)

            if w_ij > 0:
                W[fi][fj] = w_ij
                W[fj][fi] = w_ij

            if qi == qj and bi == bj and qi != "?":
                tier = "TIER1_SAME_BIFOLIO_SHEET"
            elif qi == qj and qi != "?":
                tier = "TIER2_SAME_QUIRE_DIFF_BIFOLIO"
            elif si == sj and si != "?":
                tier = "TIER3_SAME_SECTION_DIFF_QUIRE"
            else:
                tier = "TIER4_CROSS_SECTION"

            tier_weights[tier].append(w_ij)
            tier_norm_weights[tier].append(w_norm)
            all_pairs.append((i_idx, j_idx, tier, w_ij, w_norm))

            if w_ij >= 12.0:
                top_edges.append({
                    "folio_a": fi,
                    "section_a": si,
                    "quire_a": qi,
                    "folio_b": fj,
                    "section_b": sj,
                    "quire_b": qj,
                    "tier": tier,
                    "idf_weight": round(w_ij, 3),
                    "norm_weight": round(w_norm, 4),
                    "shared_rare_stems": sorted(sh, key=lambda x: -stem_idf[x])[:6],
                })

    top_edges.sort(key=lambda x: -x["idf_weight"])

    # Compute 4-Tier Codicological Distance Summary & Permutation Test
    tier_summary = {}
    for t_key in ["TIER1_SAME_BIFOLIO_SHEET", "TIER2_SAME_QUIRE_DIFF_BIFOLIO", "TIER3_SAME_SECTION_DIFF_QUIRE", "TIER4_CROSS_SECTION"]:
        vals = tier_weights[t_key]
        nvals = tier_norm_weights[t_key]
        tier_summary[t_key] = {
            "n_pairs": len(vals),
            "mean_raw_idf": round(sum(vals) / len(vals), 4) if vals else 0.0,
            "mean_size_normalized_idf": round(sum(nvals) / len(nvals), 5) if nvals else 0.0,
            "nonzero_edge_pct": round(100.0 * sum(1 for v in vals if v > 0) / len(vals), 2) if vals else 0.0,
        }

    # Permutation test: Shuffle folio node positions 1,000 times and measure
    # Tier 1 (Same Bifolio Sheet) mean size-normalized IDF vs null
    obs_t1_norm = tier_summary["TIER1_SAME_BIFOLIO_SHEET"]["mean_size_normalized_idf"]
    obs_t2_norm = tier_summary["TIER2_SAME_QUIRE_DIFF_BIFOLIO"]["mean_size_normalized_idf"]

    # Pre-store matrix of size-normalized weights M_norm[i][j]
    M_norm = [[0.0] * n_fols for _ in range(n_fols)]
    t1_pairs_idx = []
    for i_idx, j_idx, tier, _, w_norm in all_pairs:
        M_norm[i_idx][j_idx] = w_norm
        M_norm[j_idx][i_idx] = w_norm
        if tier == "TIER1_SAME_BIFOLIO_SHEET":
            t1_pairs_idx.append((i_idx, j_idx))

    null_t1_means = []
    idx_list = list(range(n_fols))
    for _ in range(1000):
        perm = list(idx_list)
        random.shuffle(perm)
        s_val = sum(M_norm[perm[i]][perm[j]] for i, j in t1_pairs_idx) / len(t1_pairs_idx)
        null_t1_means.append(s_val)

    mu_t1 = sum(null_t1_means) / len(null_t1_means)
    sd_t1 = math.sqrt(sum((x - mu_t1) ** 2 for x in null_t1_means) / len(null_t1_means))
    z_t1 = (obs_t1_norm - mu_t1) / (sd_t1 if sd_t1 > 0 else 1.0)

    # Power-iteration PageRank on W[i][j] (alpha = 0.85)
    pr = {f: 1.0 / n_fols for f in folios}
    out_strength = {f: sum(W[f].values()) for f in folios}
    alpha = 0.85
    for _ in range(60):
        new_pr = {f: (1.0 - alpha) / n_fols for f in folios}
        dangling_mass = sum(pr[f] for f in folios if out_strength[f] == 0)
        for f in folios:
            new_pr[f] += alpha * dangling_mass / n_fols
        for fi in folios:
            if out_strength[fi] > 0:
                for fj, w_ij in W[fi].items():
                    new_pr[fj] += alpha * pr[fi] * (w_ij / out_strength[fi])
        pr = new_pr

    # Compute folio-level centrality & cross-section routing metrics
    folio_profiles = []
    sec_pagerank_sum = defaultdict(float)
    sec_count = Counter()

    for f in folios:
        meta = folio_meta.get(f, {})
        sec = meta.get("section_code", "?")
        q = meta.get("quire", "?")
        b = folio_bifolio.get(f, "?")
        h = str(meta.get("hand", "?"))
        lg = meta.get("currier_lang", "?")
        n_toks = len(folio_tokens[f])
        n_stems = len(folio_stems[f])

        total_deg_idf = out_strength[f]
        cross_quire_idf = sum(w for fj, w in W[f].items() if folio_meta.get(fj, {}).get("quire") != q)
        cross_sec_idf = sum(w for fj, w in W[f].items() if folio_meta.get(fj, {}).get("section_code") != sec)

        # 6-domain breakdown (H, A, Z, B, P, S)
        dom_weights = {}
        for d_sec in ["H", "A", "Z", "B", "P", "S"]:
            dom_weights[d_sec] = sum(w for fj, w in W[f].items() if folio_meta.get(fj, {}).get("section_code") == d_sec)
        tot_6dom = sum(dom_weights.values())
        entropy_6dom = 0.0
        if tot_6dom > 0:
            for v in dom_weights.values():
                if v > 0:
                    p = v / tot_6dom
                    entropy_6dom -= p * math.log(p, 2)

        top_neighbors = sorted(W[f].items(), key=lambda x: -x[1])[:4]
        sec_pagerank_sum[sec] += pr[f]
        sec_count[sec] += 1

        folio_profiles.append({
            "folio": f,
            "section": sec,
            "quire": q,
            "bifolio": b,
            "hand": h,
            "language": lg,
            "n_tokens": n_toks,
            "n_unique_stems": n_stems,
            "pagerank": round(pr[f], 6),
            "pagerank_lift_vs_uniform": round(pr[f] * n_fols, 3),
            "total_weighted_degree_idf": round(total_deg_idf, 3),
            "cross_quire_idf": round(cross_quire_idf, 3),
            "cross_section_idf": round(cross_sec_idf, 3),
            "cross_section_idf_per_100tok": round(100.0 * cross_sec_idf / max(50, n_toks), 3),
            "six_domain_entropy_bits": round(entropy_6dom, 3),
            "top_neighbors": [
                {"folio": nf, "section": folio_meta.get(nf, {}).get("section_code", "?"), "idf": round(nw, 2)}
                for nf, nw in top_neighbors
            ],
        })

    top25_pagerank = sorted(folio_profiles, key=lambda x: -x["pagerank"])[:25]
    top25_norm_cross_sec = sorted(
        [fp for fp in folio_profiles if fp["n_tokens"] >= 60],
        key=lambda x: -x["cross_section_idf_per_100tok"]
    )[:25]
    top25_entropy_bridges = sorted(
        [fp for fp in folio_profiles if fp["total_weighted_degree_idf"] >= 150.0],
        key=lambda x: -x["six_domain_entropy_bits"]
    )[:25]

    section_pagerank_summary = {
        s: {
            "n_folios": sec_count[s],
            "total_pagerank_share_pct": round(100.0 * sec_pagerank_sum[s], 2),
            "mean_pagerank_lift_per_folio": round((sec_pagerank_sum[s] / sec_count[s]) * n_fols, 3),
        }
        for s in sorted(sec_count.keys())
    }

    out = {
        "attack": 131,
        "phase": 142,
        "discovery": 148,
        "title": "Global 226-Folio Master Citation & Cross-Reference Graph (G = (V_226, E_IDF)) — PageRank Centrality & Top-25 Master Hub Folios",
        "graph_overview": {
            "n_folios": n_fols,
            "n_total_pairs": len(all_pairs),
            "n_rare_informative_stems_2_to_15": len(stem_idf),
            "codicological_4tier_distance_decay": tier_summary,
            "same_bifolio_sheet_permutation_test": {
                "observed_tier1_norm_idf": obs_t1_norm,
                "null_mean": round(mu_t1, 5),
                "null_sd": round(sd_t1, 5),
                "lift_ratio": round(obs_t1_norm / mu_t1, 3) if mu_t1 > 0 else 0.0,
                "z_score": round(z_t1, 2),
            },
            "section_pagerank_summary": section_pagerank_summary,
        },
        "top25_global_pagerank_hubs": top25_pagerank,
        "top25_normalized_cross_section_routers": top25_norm_cross_sec,
        "top25_universal_6domain_entropy_bridges": top25_entropy_bridges,
        "top30_inter_folio_citation_edges": top_edges[:30],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 131] Saved {OUT_JSON}")
    print("4-Tier Codicological Distance Decay:", json.dumps(tier_summary, indent=2))
    print("Same-Bifolio Permutation Test:", json.dumps(out["graph_overview"]["same_bifolio_sheet_permutation_test"], indent=2))
    print("Section PageRank Summary:", json.dumps(section_pagerank_summary, indent=2))
    print("Top 10 Global PageRank Hubs:")
    for r in top25_pagerank[:10]:
        print(f"  {r['folio']} ($I={r['section']}, $Q={r['quire']}, $B={r['bifolio']}, $H={r['hand']}, {r['n_tokens']}w): PR_lift={r['pagerank_lift_vs_uniform']}x, degIDF={r['total_weighted_degree_idf']}, H6={r['six_domain_entropy_bits']}b")
    print("Top 10 Length-Normalized Cross-Section Routers (>=60w):")
    for r in top25_norm_cross_sec[:10]:
        print(f"  {r['folio']} ($I={r['section']}, $Q={r['quire']}, $B={r['bifolio']}, $H={r['hand']}, {r['n_tokens']}w): CrossSec/100w={r['cross_section_idf_per_100tok']}, PR_lift={r['pagerank_lift_vs_uniform']}x")


if __name__ == "__main__":
    main()
