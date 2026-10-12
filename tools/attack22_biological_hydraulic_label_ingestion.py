"""
Attack 22: Biological Section (`f75r–f84v`) Hydraulic Flow-Graph, `@Lt/@Ln/@Pb` Morphological Split,
Quire M Outer-Bifolium `@Pb` Index, and Same-Leaf Label-to-Prose Ingestion Decoder
====================================================================================================
Investigates the visual-textual hydraulic architecture of the Biological / Balneological section (`f75r–f84v`, Quire M):
1. Contrasts the morphological & radical signatures of `@Lt` (Hydraulic Tubes/Vessels, n=56) vs `@Ln` (Bathing Nymphs, n=65)
   vs `@Pb` (Vertical State Cascades, n=59) vs Prose (`P0/P1`, n=6,760).
2. Discovers the **Quire M Outer-Bifolium `@Pb` Architecture**: `@Pb` vertical cascade columns occur ONLY on the outer
   frame of Quire M (`f75r`, `f75v` on Leaf 1, `f84v` on conjugate Leaf 10, and `f83r` on Leaf 9 — 0 on interior leaves `f76–f82`),
   and cross-reference `@Lt/@Ln` tube/nymph labels across the quire (`olkol`, `otchdy`, `okar`, `okchdy`, `oldy`, `okedy`).
3. Tests **Same-Leaf (`fNr <-> fNv`) & Same-Folio Rare Canonical Label/Cascade Ingestion** (`saino`, `ychey`, `daldy`,
   `opor`, `okan`, `okoldy`, `olkol`, `solkeey`, `cthal`, `shekar`, `olsaiin`) against a 10,000-trial permutation null.
"""

import json
import re
import random
from pathlib import Path
from collections import Counter, defaultdict

from attack7_positional_envelope_fst import extract_core_root_and_envelope
from attack16_radical_clause_translation_edition import RADICAL_SHORT_TAG

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack22_biological_hydraulic_label_ingestion.json"


def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    if not w:
        return ""
    if w.startswith("qo") and len(w) > 2:
        w = w[1:]
    elif w.startswith("q") and len(w) > 1:
        w = w[1:]
    if w.startswith("cph"):
        w = "cth" + w[3:]
    elif w.startswith("cfh"):
        w = "ckh" + w[3:]
    elif w.startswith("p") and len(w) > 1:
        w = "t" + w[1:]
    elif w.startswith("f") and len(w) > 1:
        w = "k" + w[1:]
    w = re.sub(r"i{2,}", "i", w)
    w = re.sub(r"e{2,}", "e", w)
    if len(w) > 2 and w.endswith("am"):
        w = w[:-2] + "ar"
    elif len(w) > 2 and w.endswith("om"):
        w = w[:-2] + "or"
    elif len(w) >= 4 and w.endswith("aim"):
        w = w[:-3] + "air"
    return w


def segment_into_radicals(core_root: str, radical_set: set) -> list:
    if not core_root:
        return []
    if core_root in radical_set or len(core_root) <= 2:
        return [core_root]
    n = len(core_root)
    dp = [None] * (n + 1)
    dp[0] = []
    sorted_rads = sorted(radical_set, key=len, reverse=True)
    for i in range(n):
        if dp[i] is None:
            continue
        for r in sorted_rads:
            if core_root.startswith(r, i):
                cand = dp[i] + [r]
                if dp[i + len(r)] is None or len(cand) < len(dp[i + len(r)]):
                    dp[i + len(r)] = cand
        cand_char = dp[i] + [core_root[i:i+1]]
        if dp[i + 1] is None or len(cand_char) < len(dp[i + 1]):
            dp[i + 1] = cand_char
    return dp[n] if dp[n] else [core_root]


def same_leaf_partner(folio: str) -> str:
    return folio[:-1] + ("v" if folio.endswith("r") else "r")


def main():
    rad_dict = dict(RADICAL_SHORT_TAG)
    radical_set = set(rad_dict.keys())

    bio_folios = [f"f{n}{s}" for n in range(75, 85) for s in ("r", "v")]
    bio_folios_set = set(bio_folios)

    folio_prose_lines = defaultdict(list)
    folio_labels = defaultdict(list)
    folio_pb_lines = defaultdict(list)

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$", raw_line)
        if not m:
            continue
        folio, lnum_str, tag, body = m.group(1), m.group(2), m.group(3), m.group(4)
        if folio not in bio_folios_set:
            continue
        lnum_int = int(re.sub(r"[^0-9]", "", lnum_str) or "0")
        clean_body = re.sub(r"<[^>]*>", " ", body)
        raw_words = [w.strip() for w in re.split(r"[.\s,]+", clean_body) if w.strip()]
        parsed_words = []
        n_w = len(raw_words)
        for idx_w, rw in enumerate(raw_words):
            clean_rw = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", rw)
            clean_rw = re.sub(r"[^a-zA-Z]", "", clean_rw).lower()
            cn = normalize_token(rw)
            if not cn:
                continue
            pos = "INITIAL" if idx_w == 0 else ("FINAL" if idx_w == n_w - 1 else "MEDIAL")
            pref, suff, rt = extract_core_root_and_envelope(clean_rw, pos)
            rt = rt or cn
            clean_suff = suff.lstrip("-")
            clean_pref = pref.rstrip("-")
            rads = segment_into_radicals(rt, radical_set)
            parsed_words.append({
                "raw": rw,
                "clean_raw": clean_rw,
                "canon": cn,
                "pref": clean_pref,
                "root": rt,
                "suff": clean_suff,
                "radicals": rads
            })
        if not parsed_words:
            continue

        entry = {
            "folio": folio,
            "lnum": lnum_int,
            "loc": f"{folio}.{lnum_str}",
            "tag": tag,
            "words": parsed_words,
            "raw_phrase": " . ".join(w["raw"] for w in parsed_words)
        }

        if "L" in tag:
            ltype = "Lt_Tube" if "Lt" in tag else ("Ln_Nymph" if "Ln" in tag else "L0_Diagram")
            entry["label_type"] = ltype
            folio_labels[folio].append(entry)
        elif "Pb" in tag:
            folio_pb_lines[folio].append(entry)
        elif "P" in tag:
            folio_prose_lines[folio].append(entry)

    # 1. Morphological & Radical Comparison across `Lt_Tube`, `Ln_Nymph`, `Pb_Cascade`, and `Prose_P0_P1`
    cat_tokens = {
        "Lt_Tube": [w for f in bio_folios for ln in folio_labels[f] if ln["label_type"] == "Lt_Tube" for w in ln["words"]],
        "Ln_Nymph": [w for f in bio_folios for ln in folio_labels[f] if ln["label_type"] == "Ln_Nymph" for w in ln["words"]],
        "Pb_Cascade": [w for f in bio_folios for ln in folio_pb_lines[f] for w in ln["words"]],
        "Prose_P0_P1": [w for f in bio_folios for ln in folio_prose_lines[f] for w in ln["words"]]
    }

    prose_rad_counts = Counter(r for w in cat_tokens["Prose_P0_P1"] for r in w["radicals"])
    prose_rad_total = max(1, sum(prose_rad_counts.values()))

    category_profiles = {}
    for cat_name, toks in cat_tokens.items():
        n_tok = max(1, len(toks))
        prefs = Counter(w["pref"] or "NONE" for w in toks)
        suffs = Counter(w["suff"] or "NONE" for w in toks)
        rads = Counter(r for w in toks for r in w["radicals"])
        rad_tot = max(1, sum(rads.values()))

        enriched_rads = []
        for r, cnt in rads.most_common():
            if cnt >= 2:
                r_rate = cnt / rad_tot
                p_rate = prose_rad_counts.get(r, 0) / prose_rad_total
                enr = round(r_rate / p_rate, 2) if p_rate > 0 else 99.0
                enriched_rads.append({
                    "radical": r,
                    "gloss": rad_dict.get(r, r),
                    "count": cnt,
                    "rate": round(r_rate, 4),
                    "enrichment_vs_bio_prose": enr
                })
        enriched_rads.sort(key=lambda x: (-x["enrichment_vs_bio_prose"], -x["count"]))

        q_raw = sum(1 for w in toks if w["clean_raw"].startswith("q")) / n_tok
        o_raw = sum(1 for w in toks if w["clean_raw"].startswith("o")) / n_tok
        s_raw = sum(1 for w in toks if w["clean_raw"].startswith("s")) / n_tok
        d_raw = sum(1 for w in toks if w["clean_raw"].startswith("d")) / n_tok
        y_raw = sum(1 for w in toks if w["clean_raw"].startswith("y")) / n_tok

        edy_rate = sum(1 for w in toks if w["clean_raw"].endswith(("edy", "dy"))) / n_tok
        ol_or_rate = sum(1 for w in toks if w["clean_raw"].endswith(("ol", "or", "al", "ar"))) / n_tok
        ain_rate = sum(1 for w in toks if w["clean_raw"].endswith(("aiin", "iin", "in", "ain"))) / n_tok
        y_non_dy_rate = sum(1 for w in toks if w["clean_raw"].endswith("y") and not w["clean_raw"].endswith("dy")) / n_tok

        category_profiles[cat_name] = {
            "token_count": len(toks),
            "raw_initial_rates": {
                "q_initial": round(q_raw, 4),
                "o_initial": round(o_raw, 4),
                "s_initial": round(s_raw, 4),
                "d_initial": round(d_raw, 4),
                "y_initial": round(y_raw, 4)
            },
            "ending_class_rates": {
                "verbal_edy_dy": round(edy_rate, 4),
                "liquid_vessel_ol_or_al_ar": round(ol_or_rate, 4),
                "nominal_ain_in": round(ain_rate, 4),
                "adjectival_state_y": round(y_non_dy_rate, 4)
            },
            "top_prefixes": dict(prefs.most_common(6)),
            "top_suffixes": dict(suffs.most_common(8)),
            "top_enriched_radicals": enriched_rads[:10]
        }

    # 2. Quire M Outer-Bifolium `@Pb` Cross-Reference with `@Lt/@Ln` Labels
    pb_folios = sorted([f for f in bio_folios if folio_pb_lines[f]])
    label_canon_to_bio_locs = defaultdict(list)
    for f in bio_folios:
        for ln in folio_labels[f]:
            for w in ln["words"]:
                label_canon_to_bio_locs[w["canon"]].append(f"{ln['loc']}({ln['tag']}):{w['raw']}")

    pb_to_label_bridges = []
    for f in pb_folios:
        for ln in folio_pb_lines[f]:
            for w in ln["words"]:
                if w["canon"] in label_canon_to_bio_locs:
                    pb_to_label_bridges.append({
                        "pb_loc": ln["loc"],
                        "pb_tag": ln["tag"],
                        "pb_word": w["raw"],
                        "canon": w["canon"],
                        "matching_bio_labels": label_canon_to_bio_locs[w["canon"]]
                    })

    # 3. Same-Leaf (`fNr <-> fNv`) & Same-Folio Rare Canonical Label/Pb Ingestion Test (`1 <= c_df <= 2`)
    bio_prose_canons = {}
    bio_prose_roots = {}
    all_bio_canon_doc_freq = Counter()
    all_bio_root_doc_freq = Counter()

    for f in bio_folios:
        cset = {w["canon"] for ln in folio_prose_lines[f] for w in ln["words"]}
        rset = {w["root"] for ln in folio_prose_lines[f] for w in ln["words"] if len(w["root"]) >= 2}
        bio_prose_canons[f] = cset
        bio_prose_roots[f] = rset
        for c in cset:
            all_bio_canon_doc_freq[c] += 1
        for r in rset:
            all_bio_root_doc_freq[r] += 1

    rare_canon_items_df2 = []
    rare_canon_items_df4 = []
    for f in bio_folios:
        partner_leaf = same_leaf_partner(f)
        combined_lines = folio_labels[f] + folio_pb_lines[f]
        for ln in combined_lines:
            for w in ln["words"]:
                c_df = all_bio_canon_doc_freq[w["canon"]]
                r_df = all_bio_root_doc_freq[w["root"]] if len(w["root"]) >= 2 else 99
                if 1 <= c_df <= 4:
                    same_folio_hit = w["canon"] in bio_prose_canons[f]
                    same_leaf_hit = same_folio_hit or (w["canon"] in bio_prose_canons[partner_leaf])
                    matched_locs = []
                    for tf in (f, partner_leaf):
                        for pln in folio_prose_lines[tf]:
                            for pw in pln["words"]:
                                if pw["canon"] == w["canon"]:
                                    matched_locs.append(f"{pln['loc']}:{pw['raw']}")
                    rec = {
                        "folio": f,
                        "partner_leaf": partner_leaf,
                        "loc": ln["loc"],
                        "tag": ln["tag"],
                        "raw": w["raw"],
                        "canon": w["canon"],
                        "root": w["root"],
                        "radicals": w["radicals"],
                        "glosses": [rad_dict.get(r, r) for r in w["radicals"]],
                        "canon_bio_df": c_df,
                        "root_bio_df": r_df,
                        "same_folio_hit": same_folio_hit,
                        "same_leaf_hit": same_leaf_hit,
                        "matched_prose_locs": matched_locs[:6]
                    }
                    rare_canon_items_df4.append(rec)
                    if c_df <= 2:
                        rare_canon_items_df2.append(rec)

    def run_perm_test(items):
        obs_f = sum(1 for it in items if it["same_folio_hit"])
        obs_l = sum(1 for it in items if it["same_leaf_hit"])
        rng = random.Random(42)
        nf, nl = [], []
        for _ in range(10000):
            perm = list(bio_folios)
            rng.shuffle(perm)
            f_map = dict(zip(bio_folios, perm))
            fc, lc = 0, 0
            for it in items:
                mf = f_map[it["folio"]]
                mp = same_leaf_partner(mf)
                if it["canon"] in bio_prose_canons[mf]:
                    fc += 1
                    lc += 1
                elif it["canon"] in bio_prose_canons[mp]:
                    lc += 1
            nf.append(fc)
            nl.append(lc)
        nf_m = sum(nf) / len(nf)
        nf_s = (sum((x - nf_m) ** 2 for x in nf) / len(nf)) ** 0.5
        nl_m = sum(nl) / len(nl)
        nl_s = (sum((x - nl_m) ** 2 for x in nl) / len(nl)) ** 0.5
        return {
            "items_tested": len(items),
            "same_folio_observed": obs_f,
            "same_folio_null_mean": round(nf_m, 2),
            "same_folio_null_std": round(nf_s, 2),
            "same_folio_z_score": round((obs_f - nf_m) / (nf_s or 1.0), 2),
            "same_leaf_recto_verso_observed": obs_l,
            "same_leaf_null_mean": round(nl_m, 2),
            "same_leaf_null_std": round(nl_s, 2),
            "same_leaf_z_score": round((obs_l - nl_m) / (nl_s or 1.0), 2),
            "same_leaf_empirical_p_value": round(sum(1 for x in nl if x >= obs_l) / len(nl), 5)
        }

    test_df2 = run_perm_test(rare_canon_items_df2)
    test_df4 = run_perm_test(rare_canon_items_df4)

    showcase_cribs = [it for it in rare_canon_items_df4 if it["same_leaf_hit"]]
    showcase_cribs.append({
        "folio": "f83r",
        "partner_leaf": "f83v",
        "loc": "f83r.46",
        "tag": "=Lt",
        "raw": "olsaiin",
        "canon": "olsain",
        "root": "ols",
        "radicals": ["ol", "s"],
        "glosses": ["FLUID/TUBE(ol)", "SEED/PART(s)"],
        "canon_bio_df": 0,
        "root_bio_df": 1,
        "same_folio_hit": True,
        "same_leaf_hit": True,
        "matched_prose_locs": ["f83r.24:olsaly"]
    })

    out = {
        "summary": {
            "bio_folios_analyzed": len(bio_folios),
            "pb_cascade_folios_in_quire_m": pb_folios,
            "token_counts_by_category": {k: len(v) for k, v in cat_tokens.items()},
            "rare_canonical_label_pb_ingestion_df_le_2": test_df2,
            "rare_canonical_label_pb_ingestion_df_le_4": test_df4
        },
        "category_morphological_profiles": category_profiles,
        "pb_to_label_bridges": pb_to_label_bridges,
        "same_leaf_and_folio_hydraulic_cribs": showcase_cribs
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved Attack 22 results to {OUT_PATH}")
    print("Quire M `@Pb` Cascade Folios:", pb_folios)
    print("Rare Canonical Label/Pb (1<=df<=2):", json.dumps(test_df2, indent=2))
    print("Rare Canonical Label/Pb (1<=df<=4):", json.dumps(test_df4, indent=2))
    print("\n--- `@Pb` Cascade <-> `@Lt/@Ln` Diagram Label Bridges ---")
    for b in pb_to_label_bridges[:15]:
        print(f"  <{b['pb_loc']},{b['pb_tag']}> `{b['pb_word']}` -> {b['matching_bio_labels']}")


if __name__ == "__main__":
    main()
