#!/usr/bin/env python3
"""
Phase 20 / Attack 9: Syntactic Context & Frame Grammar Around Known Diagram Nouns
(Separating Functional Operators [Verbs/Prepositions] from Concrete Diagram Ingredients/Vessels/Stars)

Tests:
1. In-Situ Prose Inflectional Transformation of Diagram Cribs (Diagram Citation Form vs. Prose Contextual Form):
   - How often does a rare diagram label (rarity <= 25 / <= 10) acquire `q-` (qo-), `y-`, or retain bare `o-`
     when embedded in running prose, stratified by Semantic Crib Class (`Pharma`, `Zodiac`, `Astro`, `Rosettes`, `Bio`)?
2. Flanking Syntactic Frame Analysis (`[w-2, w-1, CRIB, w+1, w+2]`):
   - Using the Attack 7 Five-Stage Positional & Inflectional FST (`prefix + core_root + suffix`),
     what Core Roots (`d`, `ch`, `k`, `t`, `sh`, `ke`, `te`, `l`, `che`, `r`, etc.) and Suffixes (`-dy`, `-in`, `-ol`, `-ar`, `-al`, `-y`)
     immediately precede (`w-1`) and follow (`w+1`) rare diagram cribs?
   - 2,000-trial within-section permutation tests comparing `w-1` and `w+1` around Rare Diagram Cribs
     against random non-crib prose positions in the exact same section (`$I`) and Currier language (`$L`).
3. Semantic Class Frame Differentiation (`Pharma` vs. `Zodiac` vs. `Astro` vs. `Rosettes` vs. `Bio`):
   - Do Pharmaceutical ingredient/jar cribs select systematically different preceding/following operator roots
     and line/paragraph positions than Zodiac/Astronomical timing cribs or 9-Rosettes cosmological cribs?
4. Catalog of Exact Recurring `[Operator + CRIB]` and `[CRIB + Operator]` Formulaic Collocations
   and high-density multi-crib syntactic clauses for visual scan verification.
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

# Import our Attack 7 FST stripper and canonical normalizer
from attack7_positional_envelope_fst import (
    stage3_positional_proclitic_margin,
    extract_core_root_and_envelope,
)


def canonicalize_4rule(w: str) -> str:
    return stage3_positional_proclitic_margin(w)


def decompose_token(w: str) -> dict:
    pos_sig, env_sig, core_root = extract_core_root_and_envelope(w, "MEDIAL")
    proclitic = "q" if "P:q-" in env_sig else ("y" if "P:y-" in env_sig else "")
    o_prefix = "o" if "N:o-" in env_sig else ""
    suf = "0"
    for part in env_sig.split("|"):
        if part.startswith("S:"):
            suf = part[2:]
    return {
        "pos_sig": pos_sig,
        "env_sig": env_sig,
        "core_root": core_root,
        "proclitic": proclitic,
        "o_prefix": o_prefix,
        "suffix": suf,
    }

ZL_PATH = os.path.join("data", "ZL3b-n.txt")
INDEX_PATH = os.path.join("data", "folio_index.json")
OUT_JSON = os.path.join("data", "attack9_syntactic_context_frames.json")


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("-", "").strip()
    return t


def classify_semantic_domain(folio: str, sec: str, tag: str) -> str:
    if tag.startswith(("@Lc", "&Lc")):
        return "Pharma_Jar"
    if tag.startswith(("@Lf", "&Lf", "@Lp", "&Lp")):
        return "Pharma_Botanical"
    if tag.startswith(("@Lz", "&Lz")):
        return "Zodiac"
    if tag.startswith(("@Ls", "&Ls", "@La", "&La", "@Lt", "&Lt")):
        return "Astro"
    if tag.startswith(("@Ln", "&Ln")):
        return "Bio_Nymph"
    if tag.startswith(("@L0", "&L0")):
        if folio == "fRos" or folio.startswith(("f85", "f86")) or sec == "Cosmological":
            return "Rosettes_Cosmo"
        if sec == "Astronomical" or folio.startswith(("f67", "f68", "f69", "f70r")):
            return "Astro"
        return "Rosettes_Cosmo"
    return "Other_Label"


def parse_manuscript():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        folio_index = json.load(f)["folios"]

    # Parse ZL3b-n.txt into figure labels and prose paragraphs/lines
    label_entries = []  # dicts of {folio, loc, tag, domain, surface, canon, decomp}
    prose_paragraphs = []  # list of dicts: {folio, sec, lang, hand, p_idx, lines: [[tok_dicts]]}

    cur_folio = None
    cur_sec = "?"
    cur_lang = "?"
    cur_hand = "?"
    cur_para_lines = []
    p_idx_by_folio = Counter()

    line_re = re.compile(r"^<([^.]+)\.([^,>]+),([^>]+)>\s+(.*)$")

    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line or raw_line.startswith("#"):
                continue
            m_f = re.match(r"^<f?([^>]+)>\s*<!(.*)$", raw_line)
            if m_f and "." not in m_f.group(1):
                # Flush previous folio paragraph
                if cur_para_lines and cur_folio:
                    p_idx_by_folio[cur_folio] += 1
                    prose_paragraphs.append({
                        "folio": cur_folio,
                        "sec": cur_sec,
                        "lang": cur_lang,
                        "hand": cur_hand,
                        "p_idx": p_idx_by_folio[cur_folio],
                        "lines": cur_para_lines,
                    })
                    cur_para_lines = []
                cur_folio = "f" + m_f.group(1) if not m_f.group(1).startswith("f") else m_f.group(1)
                meta = folio_index.get(cur_folio, {})
                cur_sec = meta.get("section", "?")
                cur_lang = meta.get("currier_language", "?")
                cur_hand = str(meta.get("hand", "?"))
                continue

            m = line_re.match(raw_line)
            if not m:
                continue
            folio, loc_num, tag, rest = m.group(1), m.group(2), m.group(3), m.group(4)
            meta = folio_index.get(folio, {})
            sec = meta.get("section", cur_sec if folio == cur_folio else "?")
            lang = meta.get("currier_language", cur_lang if folio == cur_folio else "?")
            hand = str(meta.get("hand", cur_hand if folio == cur_folio else "?"))

            has_para_start = "<%>" in rest
            has_para_end = "<$>" in rest

            # Strip inline comments <! ... >
            rest_clean = re.sub(r"<!([^>]*)>", "", rest)
            rest_clean = rest_clean.replace("<%>", "").replace("<$>", "").replace("<->", " ")
            raw_toks = [clean_tok(t) for t in rest_clean.split(".") if clean_tok(t)]
            if not raw_toks:
                continue

            is_label = tag.startswith("@L") or tag.startswith("&L")
            is_ring_text = tag.startswith("@C") or tag.startswith("@R") or tag.startswith("&C") or tag.startswith("&R")
            if is_label:
                domain = classify_semantic_domain(folio, sec, tag)
                for w_i, tok in enumerate(raw_toks):
                    canon = canonicalize_4rule(tok)
                    if len(canon) < 2:
                        continue
                    decomp = decompose_token(tok)
                    label_entries.append({
                        "folio": folio,
                        "loc": f"{folio}.{loc_num}",
                        "tag": tag,
                        "domain": domain,
                        "surface": tok,
                        "canon": canon,
                        "decomp": decomp,
                    })
            elif not is_ring_text:
                if has_para_start and cur_para_lines:
                    p_idx_by_folio[folio] += 1
                    prose_paragraphs.append({
                        "folio": folio,
                        "sec": sec,
                        "lang": lang,
                        "hand": hand,
                        "p_idx": p_idx_by_folio[folio],
                        "lines": cur_para_lines,
                    })
                    cur_para_lines = []

                line_objs = []
                for w_i, tok in enumerate(raw_toks):
                    canon = canonicalize_4rule(tok)
                    decomp = decompose_token(tok)
                    line_objs.append({
                        "folio": folio,
                        "loc": f"{folio}.{loc_num}",
                        "tag": tag,
                        "surface": tok,
                        "canon": canon,
                        "decomp": decomp,
                        "w_idx": w_i,
                        "line_len": len(raw_toks),
                    })
                cur_para_lines.append(line_objs)

                if has_para_end and cur_para_lines:
                    p_idx_by_folio[folio] += 1
                    prose_paragraphs.append({
                        "folio": folio,
                        "sec": sec,
                        "lang": lang,
                        "hand": hand,
                        "p_idx": p_idx_by_folio[folio],
                        "lines": cur_para_lines,
                    })
                    cur_para_lines = []

    if cur_para_lines and cur_folio:
        p_idx_by_folio[cur_folio] += 1
        prose_paragraphs.append({
            "folio": cur_folio,
            "sec": cur_sec,
            "lang": cur_lang,
            "hand": cur_hand,
            "p_idx": p_idx_by_folio[cur_folio],
            "lines": cur_para_lines,
        })

    return label_entries, prose_paragraphs


def main():
    random.seed(42)
    label_entries, prose_paragraphs = parse_manuscript()

    # Build global prose canonical frequency & map each canonical form to its diagram domains
    global_prose_canon_counts = Counter()
    all_prose_tokens_flat = []

    for p in prose_paragraphs:
        n_lines = len(p["lines"])
        p_tokens = []
        for l_idx, line in enumerate(p["lines"]):
            for t in line:
                t["l_idx"] = l_idx
                t["n_lines"] = n_lines
                t["sec"] = p["sec"]
                t["lang"] = p["lang"]
                t["hand"] = p["hand"]
                t["p_idx"] = p["p_idx"]
                global_prose_canon_counts[t["canon"]] += 1
                p_tokens.append(t)
        p["flat_tokens"] = p_tokens
        all_prose_tokens_flat.extend(p_tokens)

    # Group diagram labels by canonical form
    canon_to_labels = defaultdict(list)
    for lbl in label_entries:
        canon_to_labels[lbl["canon"]].append(lbl)

    # Identify priority semantic domain for each canonical diagram label
    # Priority order if a canon appears in multiple diagram domains:
    # Pharma_Jar > Pharma_Botanical > Zodiac > Astro > Rosettes_Cosmo > Bio_Nymph > Herbal
    domain_priority = [
        "Pharma_Jar",
        "Pharma_Botanical",
        "Zodiac",
        "Astro",
        "Rosettes_Cosmo",
        "Bio_Nymph",
        "Herbal",
    ]

    canon_to_primary_domain = {}
    canon_to_all_domains = {}
    for canon, lbls in canon_to_labels.items():
        doms = sorted(set(l["domain"] for l in lbls))
        canon_to_all_domains[canon] = doms
        chosen = doms[0]
        for dp in domain_priority:
            if dp in doms:
                chosen = dp
                break
        canon_to_primary_domain[canon] = chosen

    # Combine Pharma_Jar + Pharma_Botanical into a unified "Pharma_All" view as well as keeping them split
    print(f"Total label tokens: {len(label_entries)} ({len(canon_to_labels)} unique canons)")
    print(f"Total prose paragraphs: {len(prose_paragraphs)} ({len(all_prose_tokens_flat)} prose tokens)")

    # =========================================================================
    # PART 1: Diagram Citation Form vs. In-Situ Prose Contextual Form
    # =========================================================================
    # For rare diagram labels (1 <= global_prose_count <= 25 and len(canon) >= 3):
    # Compare their prefix/suffix profile inside diagrams vs. when cited in running prose!
    rare_canons_25 = {
        c for c, lbls in canon_to_labels.items()
        if 1 <= global_prose_canon_counts[c] <= 25 and len(c) >= 3
    }
    rare_canons_10 = {
        c for c, lbls in canon_to_labels.items()
        if 1 <= global_prose_canon_counts[c] <= 10 and len(c) >= 3
    }

    diagram_vs_prose_inflection = {}
    domains_to_track = ["ALL_RARE_25", "ALL_RARE_10", "Pharma_All", "Pharma_Jar", "Pharma_Botanical", "Zodiac", "Astro", "Rosettes_Cosmo", "Bio_Nymph"]

    for dom in domains_to_track:
        diagram_vs_prose_inflection[dom] = {
            "diagram_count": 0,
            "prose_count": 0,
            "diagram_prefix": Counter(),
            "prose_prefix": Counter(),
            "diagram_suffix": Counter(),
            "prose_suffix": Counter(),
            "prose_line_pos": Counter(),   # line_initial, line_medial, line_final
            "prose_para_pos": Counter(),   # para_line1, para_medial, para_last_line
        }

    for lbl in label_entries:
        c = lbl["canon"]
        if c not in rare_canons_25:
            continue
        dom = canon_to_primary_domain[c]
        buckets = ["ALL_RARE_25"]
        if c in rare_canons_10:
            buckets.append("ALL_RARE_10")
        if dom in diagram_vs_prose_inflection:
            buckets.append(dom)
        if dom in ("Pharma_Jar", "Pharma_Botanical"):
            buckets.append("Pharma_All")

        d = lbl["decomp"]
        pfx = "q-" if d["proclitic"] == "q" else ("y-" if d["proclitic"] == "y" else ("o-" if d["o_prefix"] == "o" else "bare"))
        sfx = d["suffix"]
        for b in buckets:
            diagram_vs_prose_inflection[b]["diagram_count"] += 1
            diagram_vs_prose_inflection[b]["diagram_prefix"][pfx] += 1
            diagram_vs_prose_inflection[b]["diagram_suffix"][sfx] += 1

    # Now scan all prose paragraphs for rare crib occurrences and record both in-situ inflection and flanking frames
    crib_instances = []  # detailed records of every rare crib occurrence in prose

    for p in prose_paragraphs:
        toks = p["flat_tokens"]
        n_toks = len(toks)
        for i, t in enumerate(toks):
            c = t["canon"]
            if c not in rare_canons_25:
                continue
            # Exclude same-folio matches so we only measure true cross-folio prose usage
            lbl_folios = {l["folio"] for l in canon_to_labels[c]}
            if t["folio"] in lbl_folios:
                continue

            dom = canon_to_primary_domain[c]
            buckets = ["ALL_RARE_25"]
            if c in rare_canons_10:
                buckets.append("ALL_RARE_10")
            if dom in diagram_vs_prose_inflection:
                buckets.append(dom)
            if dom in ("Pharma_Jar", "Pharma_Botanical"):
                buckets.append("Pharma_All")

            d = t["decomp"]
            pfx = "q-" if d["proclitic"] == "q" else ("y-" if d["proclitic"] == "y" else ("o-" if d["o_prefix"] == "o" else "bare"))
            sfx = d["suffix"]

            if t["w_idx"] == 0:
                lpos = "line_initial"
            elif t["w_idx"] == t["line_len"] - 1:
                lpos = "line_final"
            else:
                lpos = "line_medial"

            if t["l_idx"] == 0:
                ppos = "para_line1"
            elif t["l_idx"] == t["n_lines"] - 1:
                ppos = "para_last_line"
            else:
                ppos = "para_medial"

            for b in buckets:
                diagram_vs_prose_inflection[b]["prose_count"] += 1
                diagram_vs_prose_inflection[b]["prose_prefix"][pfx] += 1
                diagram_vs_prose_inflection[b]["prose_suffix"][sfx] += 1
                diagram_vs_prose_inflection[b]["prose_line_pos"][lpos] += 1
                diagram_vs_prose_inflection[b]["prose_para_pos"][ppos] += 1

            w_minus_2 = toks[i - 2] if i >= 2 else None
            w_minus_1 = toks[i - 1] if i >= 1 else None
            w_plus_1 = toks[i + 1] if i + 1 < n_toks else None
            w_plus_2 = toks[i + 2] if i + 2 < n_toks else None

            crib_instances.append({
                "folio": t["folio"],
                "loc": t["loc"],
                "sec": t["sec"],
                "lang": t["lang"],
                "p_idx": t["p_idx"],
                "l_idx": t["l_idx"],
                "w_idx": t["w_idx"],
                "line_len": t["line_len"],
                "line_pos": lpos,
                "para_pos": ppos,
                "surface": t["surface"],
                "canon": c,
                "global_prose_count": global_prose_canon_counts[c],
                "domain": dom,
                "all_domains": canon_to_all_domains[c],
                "label_loci": [f"{l['loc']}({l['surface']})" for l in canon_to_labels[c][:4]],
                "crib_prefix": pfx,
                "crib_root": d["core_root"],
                "crib_suffix": sfx,
                "w_minus_2": {
                    "surface": w_minus_2["surface"],
                    "root": w_minus_2["decomp"]["core_root"],
                    "prefix": "q-" if w_minus_2["decomp"]["proclitic"] == "q" else ("y-" if w_minus_2["decomp"]["proclitic"] == "y" else ("o-" if w_minus_2["decomp"]["o_prefix"] == "o" else "bare")),
                    "suffix": w_minus_2["decomp"]["suffix"],
                } if w_minus_2 else None,
                "w_minus_1": {
                    "surface": w_minus_1["surface"],
                    "root": w_minus_1["decomp"]["core_root"],
                    "prefix": "q-" if w_minus_1["decomp"]["proclitic"] == "q" else ("y-" if w_minus_1["decomp"]["proclitic"] == "y" else ("o-" if w_minus_1["decomp"]["o_prefix"] == "o" else "bare")),
                    "suffix": w_minus_1["decomp"]["suffix"],
                    "same_line": (w_minus_1["l_idx"] == t["l_idx"]),
                } if w_minus_1 else None,
                "w_plus_1": {
                    "surface": w_plus_1["surface"],
                    "root": w_plus_1["decomp"]["core_root"],
                    "prefix": "q-" if w_plus_1["decomp"]["proclitic"] == "q" else ("y-" if w_plus_1["decomp"]["proclitic"] == "y" else ("o-" if w_plus_1["decomp"]["o_prefix"] == "o" else "bare")),
                    "suffix": w_plus_1["decomp"]["suffix"],
                    "same_line": (w_plus_1["l_idx"] == t["l_idx"]),
                } if w_plus_1 else None,
                "w_plus_2": {
                    "surface": w_plus_2["surface"],
                    "root": w_plus_2["decomp"]["core_root"],
                    "prefix": "q-" if w_plus_2["decomp"]["proclitic"] == "q" else ("y-" if w_plus_2["decomp"]["proclitic"] == "y" else ("o-" if w_plus_2["decomp"]["o_prefix"] == "o" else "bare")),
                    "suffix": w_plus_2["decomp"]["suffix"],
                } if w_plus_2 else None,
            })

    # Convert counters in diagram_vs_prose_inflection to percentages + counts
    inflection_summary = {}
    for dom, stats in diagram_vs_prose_inflection.items():
        dc = stats["diagram_count"]
        pc = stats["prose_count"]
        if dc == 0 and pc == 0:
            continue
        inflection_summary[dom] = {
            "diagram_count": dc,
            "prose_count": pc,
            "diagram_prefix_pct": {k: round(100.0 * v / dc, 2) for k, v in stats["diagram_prefix"].most_common()} if dc else {},
            "prose_prefix_pct": {k: round(100.0 * v / pc, 2) for k, v in stats["prose_prefix"].most_common()} if pc else {},
            "diagram_suffix_pct": {k: round(100.0 * v / dc, 2) for k, v in stats["diagram_suffix"].most_common(6)} if dc else {},
            "prose_suffix_pct": {k: round(100.0 * v / pc, 2) for k, v in stats["prose_suffix"].most_common(6)} if pc else {},
            "prose_line_pos_pct": {k: round(100.0 * v / pc, 2) for k, v in stats["prose_line_pos"].most_common()} if pc else {},
            "prose_para_pos_pct": {k: round(100.0 * v / pc, 2) for k, v in stats["prose_para_pos"].most_common()} if pc else {},
        }

    # Baseline line_pos and para_pos across all 36,281 prose tokens
    base_line_pos = Counter()
    base_para_pos = Counter()
    for t in all_prose_tokens_flat:
        if t["w_idx"] == 0:
            base_line_pos["line_initial"] += 1
        elif t["w_idx"] == t["line_len"] - 1:
            base_line_pos["line_final"] += 1
        else:
            base_line_pos["line_medial"] += 1

        if t["l_idx"] == 0:
            base_para_pos["para_line1"] += 1
        elif t["l_idx"] == t["n_lines"] - 1:
            base_para_pos["para_last_line"] += 1
        else:
            base_para_pos["para_medial"] += 1

    n_all = len(all_prose_tokens_flat)
    baseline_geometry = {
        "total_prose_tokens": n_all,
        "line_pos_pct": {k: round(100.0 * v / n_all, 2) for k, v in base_line_pos.most_common()},
        "para_pos_pct": {k: round(100.0 * v / n_all, 2) for k, v in base_para_pos.most_common()},
    }

    # =========================================================================
    # PART 2: Flanking Frame Analysis (`w-1` and `w+1`) by Semantic Crib Domain
    # =========================================================================
    # Compute global prose root, prefix, and suffix frequencies per (sec, lang) bucket
    # so we can compute exact Stratified Expected Counts and Enrichment Ratios!
    bucket_root_counts_w_minus_1 = defaultdict(Counter)
    bucket_sfx_counts_w_minus_1 = defaultdict(Counter)
    bucket_pfx_counts_w_minus_1 = defaultdict(Counter)
    bucket_totals_w_minus_1 = Counter()

    bucket_root_counts_w_plus_1 = defaultdict(Counter)
    bucket_sfx_counts_w_plus_1 = defaultdict(Counter)
    bucket_pfx_counts_w_plus_1 = defaultdict(Counter)
    bucket_totals_w_plus_1 = Counter()

    for p in prose_paragraphs:
        b_key = (p["sec"], p["lang"])
        toks = p["flat_tokens"]
        for i in range(len(toks)):
            if i >= 1:
                wm1 = toks[i - 1]["decomp"]
                pfx = "q-" if wm1["proclitic"] == "q" else ("y-" if wm1["proclitic"] == "y" else ("o-" if wm1["o_prefix"] == "o" else "bare"))
                bucket_root_counts_w_minus_1[b_key][wm1["core_root"]] += 1
                bucket_sfx_counts_w_minus_1[b_key][wm1["suffix"]] += 1
                bucket_pfx_counts_w_minus_1[b_key][pfx] += 1
                bucket_totals_w_minus_1[b_key] += 1
            if i + 1 < len(toks):
                wp1 = toks[i + 1]["decomp"]
                pfx = "q-" if wp1["proclitic"] == "q" else ("y-" if wp1["proclitic"] == "y" else ("o-" if wp1["o_prefix"] == "o" else "bare"))
                bucket_root_counts_w_plus_1[b_key][wp1["core_root"]] += 1
                bucket_sfx_counts_w_plus_1[b_key][wp1["suffix"]] += 1
                bucket_pfx_counts_w_plus_1[b_key][pfx] += 1
                bucket_totals_w_plus_1[b_key] += 1

    def analyze_flanking_for_domain(filter_fn, min_obs=5):
        subset = [ci for ci in crib_instances if filter_fn(ci)]
        wm1_roots = Counter()
        wm1_sfx = Counter()
        wm1_pfx = Counter()
        wm1_buckets = Counter()

        wp1_roots = Counter()
        wp1_sfx = Counter()
        wp1_pfx = Counter()
        wp1_buckets = Counter()

        for ci in subset:
            b_key = (ci["sec"], ci["lang"])
            if ci["w_minus_1"] is not None:
                wm1_roots[ci["w_minus_1"]["root"]] += 1
                wm1_sfx[ci["w_minus_1"]["suffix"]] += 1
                wm1_pfx[ci["w_minus_1"]["prefix"]] += 1
                wm1_buckets[b_key] += 1
            if ci["w_plus_1"] is not None:
                wp1_roots[ci["w_plus_1"]["root"]] += 1
                wp1_sfx[ci["w_plus_1"]["suffix"]] += 1
                wp1_pfx[ci["w_plus_1"]["prefix"]] += 1
                wp1_buckets[b_key] += 1

        def compute_enrichments(obs_counter, bucket_dist, bucket_tot, sample_buckets, min_c):
            results = []
            tot_n = sum(sample_buckets.values())
            if tot_n == 0:
                return results
            for feat, obs in obs_counter.most_common():
                if obs < min_c:
                    continue
                exp = 0.0
                for b_k, b_n in sample_buckets.items():
                    if bucket_tot[b_k] > 0:
                        exp += b_n * (bucket_dist[b_k][feat] / bucket_tot[b_k])
                if exp <= 0:
                    continue
                ratio = obs / exp
                z = (obs - exp) / math.sqrt(exp)
                results.append({
                    "feature": feat,
                    "observed": obs,
                    "expected": round(exp, 2),
                    "pct": round(100.0 * obs / tot_n, 2),
                    "enrichment_ratio": round(ratio, 3),
                    "z_score": round(z, 2),
                })
            results.sort(key=lambda x: x["z_score"], reverse=True)
            return results

        return {
            "instance_count": len(subset),
            "w_minus_1_total": sum(wm1_buckets.values()),
            "w_plus_1_total": sum(wp1_buckets.values()),
            "w_minus_1_top_roots": compute_enrichments(wm1_roots, bucket_root_counts_w_minus_1, bucket_totals_w_minus_1, wm1_buckets, min_obs)[:15],
            "w_minus_1_suffixes": compute_enrichments(wm1_sfx, bucket_sfx_counts_w_minus_1, bucket_totals_w_minus_1, wm1_buckets, min_obs),
            "w_minus_1_prefixes": compute_enrichments(wm1_pfx, bucket_pfx_counts_w_minus_1, bucket_totals_w_minus_1, wm1_buckets, min_obs),
            "w_plus_1_top_roots": compute_enrichments(wp1_roots, bucket_root_counts_w_plus_1, bucket_totals_w_plus_1, wp1_buckets, min_obs)[:15],
            "w_plus_1_suffixes": compute_enrichments(wp1_sfx, bucket_sfx_counts_w_plus_1, bucket_totals_w_plus_1, wp1_buckets, min_obs),
            "w_plus_1_prefixes": compute_enrichments(wp1_pfx, bucket_pfx_counts_w_plus_1, bucket_totals_w_plus_1, wp1_buckets, min_obs),
        }

    flanking_by_domain = {
        "ALL_RARE_25": analyze_flanking_for_domain(lambda x: True, min_obs=10),
        "ALL_RARE_10": analyze_flanking_for_domain(lambda x: x["global_prose_count"] <= 10, min_obs=6),
        "Pharma_All": analyze_flanking_for_domain(lambda x: x["domain"] in ("Pharma_Jar", "Pharma_Botanical"), min_obs=5),
        "Pharma_Jar": analyze_flanking_for_domain(lambda x: x["domain"] == "Pharma_Jar", min_obs=3),
        "Pharma_Botanical": analyze_flanking_for_domain(lambda x: x["domain"] == "Pharma_Botanical", min_obs=5),
        "Zodiac": analyze_flanking_for_domain(lambda x: x["domain"] == "Zodiac", min_obs=5),
        "Astro": analyze_flanking_for_domain(lambda x: x["domain"] == "Astro", min_obs=4),
        "Rosettes_Cosmo": analyze_flanking_for_domain(lambda x: x["domain"] == "Rosettes_Cosmo", min_obs=4),
        "Bio_Nymph": analyze_flanking_for_domain(lambda x: x["domain"] == "Bio_Nymph", min_obs=4),
    }

    # =========================================================================
    # PART 3: Recurring Exact Collocation Formulas (`[Operator + CRIB]` & `[CRIB + Operator]`)
    # =========================================================================
    # Look for recurring templates where a short functional root (`d`, `ch`, `k`, `t`, `sh`, `ke`, `te`, `l`, `che`, `r`)
    # precedes or follows a rare diagram crib (`global_prose_count <= 15`)
    top_operator_roots = {"d", "ch", "k", "t", "sh", "ke", "te", "l", "che", "a", "r", "kch", "tch", "pch", "s"}

    operator_before_crib = Counter()
    operator_after_crib = Counter()
    sandwich_frames = []

    for ci in crib_instances:
        if ci["global_prose_count"] > 15:
            continue
        wm1 = ci["w_minus_1"]
        wp1 = ci["w_plus_1"]
        if wm1 and wm1["same_line"] and wm1["root"] in top_operator_roots:
            pat = f"[{wm1['prefix']}{wm1['root']}{wm1['suffix']}] + <{ci['domain']}:{ci['canon']}>"
            operator_before_crib[pat] += 1
        if wp1 and wp1["same_line"] and wp1["root"] in top_operator_roots:
            pat = f"<{ci['domain']}:{ci['canon']}> + [{wp1['prefix']}{wp1['root']}{wp1['suffix']}]"
            operator_after_crib[pat] += 1

        if wm1 and wp1 and wm1["same_line"] and wp1["same_line"] and ci["global_prose_count"] <= 6:
            sandwich_frames.append({
                "folio": ci["folio"],
                "loc": ci["loc"],
                "sec": ci["sec"],
                "domain": ci["domain"],
                "global_prose_count": ci["global_prose_count"],
                "label_loci": ci["label_loci"],
                "clause_surface": f"{wm1['surface']} . {ci['surface']} . {wp1['surface']}",
                "clause_segmented": (
                    f"[{wm1['prefix']}{wm1['root']}{wm1['suffix']}]  "
                    f"<{ci['crib_prefix']}|{ci['crib_root']}|{ci['crib_suffix']} ({ci['domain']})>  "
                    f"[{wp1['prefix']}{wp1['root']}{wp1['suffix']}]"
                ),
                "w_minus_1": wm1,
                "crib_surface": ci["surface"],
                "crib_canon": ci["canon"],
                "w_plus_1": wp1,
            })

    # Sort sandwich frames by rarity of the crib (ascending)
    sandwich_frames.sort(key=lambda x: (x["global_prose_count"], -len(x["crib_canon"])))

    # =========================================================================
    # PART 4: Operator Root Selectional Preference Matrix (Which Operator Roots Prefer Which Crib Class?)
    # =========================================================================
    # For the top 10 Operator Roots (`d`, `ch`, `k`, `t`, `sh`, `ke`, `te`, `l`, `che`, `r`),
    # compute their distribution in `w-1` and `w+1` across the 4 major Crib Super-Classes:
    # `Pharma_All`, `Zodiac`, `Astro`, `Rosettes_Cosmo`
    super_domains = ["Pharma_All", "Zodiac", "Astro", "Rosettes_Cosmo", "Bio_Nymph"]
    operator_selection_matrix = {}
    for op in ["d", "ch", "k", "t", "sh", "ke", "te", "l", "che", "r"]:
        operator_selection_matrix[op] = {"w_minus_1_pct_by_domain": {}, "w_plus_1_pct_by_domain": {}}
        for sdom in super_domains:
            sub = [
                ci for ci in crib_instances
                if (ci["domain"] in ("Pharma_Jar", "Pharma_Botanical") if sdom == "Pharma_All" else ci["domain"] == sdom)
            ]
            wm1_n = sum(1 for ci in sub if ci["w_minus_1"] is not None)
            wp1_n = sum(1 for ci in sub if ci["w_plus_1"] is not None)
            wm1_op = sum(1 for ci in sub if ci["w_minus_1"] is not None and ci["w_minus_1"]["root"] == op)
            wp1_op = sum(1 for ci in sub if ci["w_plus_1"] is not None and ci["w_plus_1"]["root"] == op)
            operator_selection_matrix[op]["w_minus_1_pct_by_domain"][sdom] = round(100.0 * wm1_op / wm1_n, 2) if wm1_n else 0.0
            operator_selection_matrix[op]["w_plus_1_pct_by_domain"][sdom] = round(100.0 * wp1_op / wp1_n, 2) if wp1_n else 0.0

    output = {
        "summary": {
            "total_label_tokens": len(label_entries),
            "unique_label_canons": len(canon_to_labels),
            "rare_canons_25": len(rare_canons_25),
            "rare_canons_10": len(rare_canons_10),
            "cross_folio_rare_25_prose_instances": len(crib_instances),
        },
        "baseline_prose_geometry": baseline_geometry,
        "diagram_vs_prose_inflection": inflection_summary,
        "flanking_frames_by_domain": flanking_by_domain,
        "operator_selection_matrix": operator_selection_matrix,
        "top_operator_before_crib_formulas": [
            {"formula": k, "count": v} for k, v in operator_before_crib.most_common(25)
        ],
        "top_operator_after_crib_formulas": [
            {"formula": k, "count": v} for k, v in operator_after_crib.most_common(25)
        ],
        "top_ultra_rare_sandwich_clauses": sandwich_frames[:40],
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved Attack 9 analysis to {OUT_JSON}")
    print("\n--- BASELINE PROSE GEOMETRY ---")
    print(json.dumps(baseline_geometry, indent=2))
    print("\n--- DIAGRAM VS PROSE INFLECTION BY SEMANTIC CLASS ---")
    for dom in ["ALL_RARE_25", "ALL_RARE_10", "Pharma_Jar", "Pharma_Botanical", "Zodiac", "Astro", "Rosettes_Cosmo", "Bio_Nymph"]:
        if dom in inflection_summary:
            s = inflection_summary[dom]
            print(f"[{dom}] (diag={s['diagram_count']}, prose={s['prose_count']})")
            print(f"   Diag Prefix : {s['diagram_prefix_pct']}")
            print(f"   Prose Prefix: {s['prose_prefix_pct']}")
            print(f"   Prose LinePos: {s['prose_line_pos_pct']}")
            print(f"   Prose ParaPos: {s['prose_para_pos_pct']}")

    print("\n--- OPERATOR SELECTION MATRIX (w-1 and w+1 % by Semantic Class) ---")
    for op, mat in operator_selection_matrix.items():
        print(f"Root '{op}': w-1={mat['w_minus_1_pct_by_domain']} | w+1={mat['w_plus_1_pct_by_domain']}")

    print("\n--- TOP 15 ULTRA-RARE SANDWICH CLAUSES (global_prose_count <= 6) ---")
    for sf in sandwich_frames[:15]:
        print(f"  {sf['loc']} ({sf['sec']}, cnt={sf['global_prose_count']}): {sf['clause_surface']}  ==>  {sf['clause_segmented']}  [from {sf['label_loci']}]")


if __name__ == "__main__":
    main()
