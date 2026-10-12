#!/usr/bin/env python3
"""
Phase 42 / Attack 31: Quire 20 (f103r-f116r) Starred Recipe Formulary Compiler,
Opening-Header-to-Body Operator Concordance, and Adjacent-Recipe Genre Clustering.

Analyzes all starred recipe paragraphs in Section $I=S (Quire 20, f103r-f116r) in data/ZL3b-n.txt:
1. Classifies every starred recipe paragraph into one of 4 Dominant Procedural Genres
   based on its body operator counts (excluding opening word w_1):
   - THERMAL_DECOCTION (sh / she stems: shedy, sheedy, shey, shol, shor)
   - MECHANICAL_MIXTURE (ch / che stems: chedy, cheedy, chey, chol, chor)
   - VESSEL_INFUSION (k / ke stems: qokeedy, qokedy, qokeey, okeedy, okedy)
   - CONDUIT_DISTILLATION (t / te stems: qoteedy, qotedy, otedy, oteedy,tedy)
2. Opening Header (w_1) -> Recipe Body Genre Concordance (1,000-trial permutation test):
   - Tests whether the root consonant of the paragraph-opening header word w_1 (<%>w_1)
     predicts the dominant procedural operator class of the remainder of the paragraph (w_2..w_n).
3. Adjacent-Recipe Genre Clustering (1,000-trial permutation test):
   - Tests whether consecutive starred recipes (P_i, P_{i+1}) on the same folio share the
     same procedural genre significantly above random recipe ordering.
4. Closing Product Terminus (-am/-om/-dam at <$>) Profile across the 24 pages of Quire 20.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack31_starred_recipe_formulary_compiler.json"


def normalize_eva(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    return w


def classify_operator_token(w: str) -> str:
    if not w:
        return ""
    # Check specific procedural operator families
    if w.startswith(("sh", "qosh", "osh", "ysh", "dsh", "lsh")) or "shed" in w or "shey" in w:
        return "THERMAL_DECOCTION_sh"
    if w.startswith(("ch", "qoch", "och", "ych", "dch", "lch")) or "ched" in w or "chey" in w:
        return "MECHANICAL_MIXTURE_ch"
    if w.startswith(("qok", "ok", "yk", "lk", "k", "f", "of", "qof")) or "ked" in w or "keey" in w:
        return "VESSEL_INFUSION_k"
    if w.startswith(("qot", "ot", "yt", "lt", "t", "p", "op", "qop")) or "ted" in w or "teey" in w:
        return "CONDUIT_DISTILLATION_t"
    return ""


def parse_quire20_recipes():
    recipes = []
    current_folio = None
    meta = {}
    current_para = None

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    meta_re = re.compile(r"\$([A-Z])=([A-Za-z0-9]+)")

    with open(ZL_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            if raw.startswith("<f") and ">" in raw and "." not in raw.split(">")[0]:
                m_f = re.match(r"^<(f[A-Za-z0-9]+)>", raw)
                if m_f:
                    if current_para and current_para["tokens"]:
                        recipes.append(current_para)
                        current_para = None
                    current_folio = m_f.group(1)
                    meta = dict(meta_re.findall(raw))
                continue
            m = line_re.match(raw)
            if m and current_folio and meta.get("I") == "S":
                f_id, loc_id, loc_type, body = m.groups()
                if "P" not in loc_type:
                    continue
                is_start = "<%>" in body or loc_type.startswith("@P") or loc_type.startswith("*P")
                is_end = "<$>" in body
                body_clean = re.sub(r"<!.*?>", "", body)
                raw_tokens = re.split(r"[.\s,]+", body_clean)
                tokens = [normalize_eva(t) for t in raw_tokens]
                tokens = [t for t in tokens if t]
                if not tokens:
                    continue

                if is_start or current_para is None:
                    if current_para and current_para["tokens"]:
                        recipes.append(current_para)
                    current_para = {
                        "folio": f_id,
                        "hand": meta.get("H", ""),
                        "language": meta.get("L", "B"),
                        "start_loc": loc_id,
                        "tokens": list(tokens),
                        "line_count": 1,
                    }
                else:
                    current_para["tokens"].extend(tokens)
                    current_para["line_count"] += 1

                if is_end and current_para:
                    recipes.append(current_para)
                    current_para = None

    if current_para and current_para["tokens"]:
        recipes.append(current_para)

    return recipes


def main():
    random.seed(42)
    recipes = parse_quire20_recipes()

    # Number paragraphs per folio
    folio_para_counters = Counter()
    compiled_recipes = []
    genre_counts = Counter()

    header_body_pairs = []
    closing_am_by_genre = defaultdict(lambda: {"total": 0, "am_om_closers": 0})

    for r in recipes:
        f_id = r["folio"]
        folio_para_counters[f_id] += 1
        p_id = f"{f_id}:P{folio_para_counters[f_id]}"
        toks = r["tokens"]
        w1 = toks[0]
        w_last = toks[-1]
        body_toks = toks[1:] if len(toks) > 1 else toks

        # Count operators in body_toks
        op_counts = Counter()
        for bt in body_toks:
            cl = classify_operator_token(bt)
            if cl:
                op_counts[cl] += 1

        if op_counts:
            # Normalize by corpus baseline operator share so the largest raw class doesn't trivially win every time,
            # AND also record raw dominant class
            raw_dom = op_counts.most_common(1)[0][0]
        else:
            raw_dom = "VESSEL_INFUSION_k"

        # Also compute relative enrichment genre (normalized against Quire 20 mean share of each operator class)
        compiled_recipes.append({
            "recipe_id": p_id,
            "folio": f_id,
            "hand": r["hand"],
            "line_count": r["line_count"],
            "word_count": len(toks),
            "opening_word": w1,
            "opening_class": classify_operator_token(w1) or "NOMINAL_OTHER",
            "closing_word": w_last,
            "closes_with_am_om": w_last.endswith(("am", "om", "an")),
            "closes_with_dy_y": w_last.endswith("y"),
            "aiin_unit_count": sum(1 for t in toks if t.endswith(("aiin", "iin", "in"))),
            "dar_dal_count": sum(1 for t in toks if t in ("dar", "dal", "dair", "dam")),
            "op_counts": dict(op_counts),
            "raw_dominant_genre": raw_dom,
        })

    # Compute corpus-wide operator totals across Quire 20 to define relative-enrichment dominant genre
    global_op_totals = Counter()
    for cr in compiled_recipes:
        for k, v in cr["op_counts"].items():
            global_op_totals[k] += v
    tot_ops = sum(global_op_totals.values()) or 1
    op_shares = {k: v / tot_ops for k, v in global_op_totals.items()}

    for cr in compiled_recipes:
        opc = cr["op_counts"]
        tot_r = sum(opc.values()) or 1
        best_genre = max(
            op_shares.keys(),
            key=lambda g: (opc.get(g, 0) / tot_r) / max(op_shares[g], 1e-6),
        )
        cr["enriched_genre"] = best_genre
        genre_counts[best_genre] += 1
        closing_am_by_genre[best_genre]["total"] += 1
        if cr["closes_with_am_om"]:
            closing_am_by_genre[best_genre]["am_om_closers"] += 1
        if cr["opening_class"] != "NOMINAL_OTHER":
            header_body_pairs.append((cr["opening_class"], best_genre, cr["hand"]))

    # 1. Test Opening Header (w_1) -> Body Genre Concordance (1,000 permutations)
    obs_hb_match = sum(1 for h_cl, b_cl, _ in header_body_pairs if h_cl == b_cl)
    null_hb = []
    b_list = [b_cl for _, b_cl, _ in header_body_pairs]
    h_list = [h_cl for h_cl, _, _ in header_body_pairs]
    for _ in range(1000):
        shuf_b = b_list[:]
        random.shuffle(shuf_b)
        null_hb.append(sum(1 for h_cl, b_cl in zip(h_list, shuf_b) if h_cl == b_cl))

    mean_hb = sum(null_hb) / len(null_hb)
    std_hb = math.sqrt(sum((x - mean_hb) ** 2 for x in null_hb) / len(null_hb)) or 1.0
    z_hb = (obs_hb_match - mean_hb) / std_hb
    p_hb = sum(1 for x in null_hb if x >= obs_hb_match) / len(null_hb)

    # 2. Test Adjacent-Recipe Genre Clustering on the same folio (P_i, P_{i+1})
    adj_pairs = []
    for i in range(len(compiled_recipes) - 1):
        if compiled_recipes[i]["folio"] == compiled_recipes[i + 1]["folio"]:
            adj_pairs.append((compiled_recipes[i]["enriched_genre"], compiled_recipes[i + 1]["enriched_genre"]))

    obs_adj_same = sum(1 for g1, g2 in adj_pairs if g1 == g2)

    # Permute recipe order across Quire 20 (stratified by Scribe Hand)
    by_hand_recipes = defaultdict(list)
    for idx, cr in enumerate(compiled_recipes):
        by_hand_recipes[cr["hand"]].append(idx)

    null_adj = []
    for _ in range(1000):
        perm_genres = [None] * len(compiled_recipes)
        for h, idxs in by_hand_recipes.items():
            g_vals = [compiled_recipes[i]["enriched_genre"] for i in idxs]
            random.shuffle(g_vals)
            for i, gv in zip(idxs, g_vals):
                perm_genres[i] = gv
        cnt = 0
        for i in range(len(compiled_recipes) - 1):
            if compiled_recipes[i]["folio"] == compiled_recipes[i + 1]["folio"]:
                if perm_genres[i] == perm_genres[i + 1]:
                    cnt += 1
        null_adj.append(cnt)

    mean_adj = sum(null_adj) / len(null_adj)
    std_adj = math.sqrt(sum((x - mean_adj) ** 2 for x in null_adj) / len(null_adj)) or 1.0
    z_adj = (obs_adj_same - mean_adj) / std_adj
    p_adj = sum(1 for x in null_adj if x >= obs_adj_same) / len(null_adj)

    # 3. Folio-by-folio Quire 20 summary
    folio_summaries = []
    folios_order = []
    for cr in compiled_recipes:
        if cr["folio"] not in folios_order:
            folios_order.append(cr["folio"])

    for f_id in folios_order:
        f_recs = [cr for cr in compiled_recipes if cr["folio"] == f_id]
        g_dist = Counter(cr["enriched_genre"] for cr in f_recs)
        folio_summaries.append({
            "folio": f_id,
            "hand": f_recs[0]["hand"],
            "recipe_count": len(f_recs),
            "total_words": sum(cr["word_count"] for cr in f_recs),
            "am_om_closer_count": sum(1 for cr in f_recs if cr["closes_with_am_om"]),
            "dominant_folio_genre": g_dist.most_common(1)[0][0],
            "genre_counts": dict(g_dist),
        })

    closing_summary = {}
    for g, d in sorted(closing_am_by_genre.items()):
        closing_summary[g] = {
            "recipe_count": d["total"],
            "am_om_closer_count": d["am_om_closers"],
            "am_om_closer_rate": round(d["am_om_closers"] / max(d["total"], 1), 4),
        }

    result = {
        "phase": "Phase 42 / Attack 31",
        "title": "Quire 20 (f103r-f116r) Starred Recipe Formulary Compiler, Opening-Header-to-Body Operator Concordance & Genre Clustering",
        "overall_quire20_counts": {
            "total_folios": len(folios_order),
            "total_starred_recipes": len(compiled_recipes),
            "total_recipe_words": sum(cr["word_count"] for cr in compiled_recipes),
            "global_operator_shares": {k: round(v, 4) for k, v in op_shares.items()},
            "enriched_genre_distribution": dict(genre_counts),
        },
        "opening_header_to_body_concordance": {
            "evaluated_recipes_with_operator_header": len(header_body_pairs),
            "observed_matches": obs_hb_match,
            "observed_match_rate": round(obs_hb_match / max(len(header_body_pairs), 1), 4),
            "null_mean": round(mean_hb, 2),
            "null_std": round(std_hb, 2),
            "z_score": round(z_hb, 2),
            "p_value": round(p_hb, 4),
        },
        "adjacent_recipe_genre_clustering": {
            "adjacent_same_folio_pairs": len(adj_pairs),
            "observed_same_genre_pairs": obs_adj_same,
            "observed_same_genre_rate": round(obs_adj_same / max(len(adj_pairs), 1), 4),
            "null_hand_stratified_mean": round(mean_adj, 2),
            "null_hand_stratified_std": round(std_adj, 2),
            "z_score": round(z_adj, 2),
            "p_value": round(p_adj, 4),
        },
        "closing_am_om_by_genre": closing_summary,
        "folio_summaries": folio_summaries,
        "sample_compiled_recipes": compiled_recipes[:40],
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Overall Quire 20:", json.dumps(result["overall_quire20_counts"], indent=2))
    print("Header -> Body Concordance:", json.dumps(result["opening_header_to_body_concordance"], indent=2))
    print("Adjacent Genre Clustering:", json.dumps(result["adjacent_recipe_genre_clustering"], indent=2))
    print("Closing -am/-om by genre:", json.dumps(result["closing_am_om_by_genre"], indent=2))


if __name__ == "__main__":
    main()
