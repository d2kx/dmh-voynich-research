#!/usr/bin/env python3
"""
Phase 40 / Attack 29: Herbal-to-Pharmaceutical & Herbal-to-Starred-Recipe
Exact Plant-Identity & Line-1 Topical Headword Citation Graph.

Tests two foundational hypotheses across all 129 Herbal folios ($I=H):
1. The Line-1 Topical Headword Law (1,000-trial stratified permutation test):
   - In medieval herbals, the opening word(s) of Paragraph 1 (<fNr.1,@P0>) name or
     characterize the plant on that page.
   - We test whether the canonical stem / Core Root of a Herbal page's opening words
     (Line 1 tokens 1..3) recurs inside the REMAINDER of that same Herbal page (Lines 2+)
     significantly more often than in random Herbal pages of the same Currier language (A vs B).
2. The Herbal-to-Pharmaceutical (@Lf/@Lc) & Herbal-to-Recipe ($I=P, $I=S) Plant Citation Graph:
   - Identifies each Herbal folio's signature rare stems (1 <= herbal_df <= 3) and Line-1
     headwords, and traces exact canonical citations into:
     (a) Pharmaceutical plant/jar labels (@Lf/@Lc on f88r-f102v2)
     (b) Pharmaceutical recipe prose ($I=P)
     (c) Starred Recipe paragraphs ($I=S, Quire 20 f103r-f116r)
   - Cross-checks visual botanical features (from data/attack19_herbal_visual_pigment_radical_concordance.json)
     across linked Herbal -> Pharmaceutical pairs.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
PIGMENT_JSON = ROOT / "data" / "attack19_herbal_visual_pigment_radical_concordance.json"
OUT_JSON = ROOT / "data" / "attack29_herbal_to_recipe_plant_identity_graph.json"


def normalize_eva(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    return w


def canonical_4rule(w: str) -> str:
    if not w:
        return ""
    s = w
    if s.startswith("qo") and len(s) > 2:
        s = s[2:]
    elif s.startswith("q") and len(s) > 1:
        s = s[1:]
    s = s.replace("ckh", "kh").replace("cth", "th").replace("cph", "ph").replace("cfh", "fh")
    s = re.sub(r"i{2,}", "i", s)
    s = re.sub(r"e{2,}", "e", s)
    if len(s) > 1 and s.startswith("p"):
        s = "t" + s[1:]
    elif len(s) > 1 and s.startswith("f"):
        s = "k" + s[1:]
    return s


PREFIXES = ["qok", "qot", "qo", "ok", "ot", "ol", "or", "ar", "al", "op", "of", "yk", "yt", "ch", "sh", "d", "s", "y", "o", "k", "t", "p", "f"]
SUFFIXES = ["aiin", "oiin", "iiin", "iin", "in", "edy", "eedy", "dy", "ey", "eey", "ol", "or", "ar", "al", "am", "om", "an", "y", "l", "r", "m", "n", "g"]


def extract_core_root(w: str) -> str:
    s = canonical_4rule(w)
    if len(s) <= 2:
        return s
    for p in sorted(PREFIXES, key=len, reverse=True):
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for sfx in sorted(SUFFIXES, key=len, reverse=True):
        if s.endswith(sfx) and len(s) - len(sfx) >= 1:
            s = s[:-len(sfx)]
            break
    return s


def parse_zl():
    folios = {}
    current_folio = None
    meta = {}
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
                    current_folio = m_f.group(1)
                    meta = dict(meta_re.findall(raw))
                    folios[current_folio] = {
                        "folio": current_folio,
                        "section": meta.get("I", ""),
                        "language": meta.get("L", "A"),
                        "hand": meta.get("H", ""),
                        "quire": meta.get("Q", ""),
                        "lines": [],
                    }
                continue
            m = line_re.match(raw)
            if m and current_folio:
                f_id, loc_id, loc_type, body = m.groups()
                body_clean = re.sub(r"<!.*?>", "", body)
                raw_tokens = re.split(r"[.\s,]+", body_clean)
                tokens = [normalize_eva(t) for t in raw_tokens]
                tokens = [t for t in tokens if t]
                folios[current_folio]["lines"].append({
                    "loc_id": loc_id,
                    "loc_type": loc_type,
                    "tokens": tokens,
                    "has_para_start": "<%>" in body or loc_type.startswith("@P"),
                })
    return folios


def main():
    random.seed(42)
    folios = parse_zl()

    herbal_folios = [f_id for f_id, fd in folios.items() if fd["section"] == "H"]
    pharma_folios = [f_id for f_id, fd in folios.items() if fd["section"] == "P"]
    recipe_folios = [f_id for f_id, fd in folios.items() if fd["section"] == "S"]

    # Document frequency of canonical stems across Herbal folios and across all folios
    herbal_df = Counter()
    global_df = Counter()
    folio_canon_counts = {}

    for f_id, fd in folios.items():
        c_counter = Counter()
        for ln in fd["lines"]:
            for t in ln["tokens"]:
                c = canonical_4rule(t)
                if len(c) >= 3:
                    c_counter[c] += 1
        folio_canon_counts[f_id] = c_counter
        for c in c_counter:
            global_df[c] += 1
            if fd["section"] == "H":
                herbal_df[c] += 1

    # 1. Test the Line-1 Topical Headword Law across all 129 Herbal folios
    # Extract Line-1 tokens (first 3 tokens of line 1) and Body tokens (Lines 2+)
    # Both at exact canonical stem (herbal_df <= 25) AND gallows-stripped / Core-Root level
    def strip_top_gallows(c: str) -> str:
        for g in ("kch", "tch", "kh", "th", "ph", "fh", "k", "t", "p", "f"):
            if c.startswith(g) and len(c) - len(g) >= 3:
                return c[len(g):]
            if (c.startswith("o" + g) or c.startswith("y" + g)) and len(c) - len(g) - 1 >= 3:
                return c[0] + c[1 + len(g):]
        return c

    herbal_gstrip_df = Counter()
    for f_id in herbal_folios:
        seen_g = set()
        for ln in folios[f_id]["lines"]:
            for t in ln["tokens"]:
                g = strip_top_gallows(canonical_4rule(t))
                if len(g) >= 3:
                    seen_g.add(g)
        for g in seen_g:
            herbal_gstrip_df[g] += 1

    herbal_line1_stems = {}
    herbal_body_stem_sets = {}
    herbal_line1_gstrips = {}
    herbal_body_gstrip_sets = {}
    herbal_lang = {}

    # Also test Paragraph-Header Parallelism (Paragraph 1 Line 1 vs Paragraph 2+ Line 1 on same Herbal page)
    multi_para_folios = []
    para1_roots_by_folio = {}
    para2plus_roots_by_folio = {}

    for f_id in herbal_folios:
        fd = folios[f_id]
        prose_lines = [ln for ln in fd["lines"] if "P" in ln["loc_type"] and ln["tokens"]]
        if len(prose_lines) < 2:
            continue
        l1_toks = prose_lines[0]["tokens"][:3]
        l1_canon = [canonical_4rule(t) for t in l1_toks if len(canonical_4rule(t)) >= 3 and herbal_df[canonical_4rule(t)] <= 25]
        l1_gstrip = [
            strip_top_gallows(canonical_4rule(t))
            for t in l1_toks
            if len(strip_top_gallows(canonical_4rule(t))) >= 3 and herbal_gstrip_df[strip_top_gallows(canonical_4rule(t))] <= 30
        ]
        body_canon = set()
        body_gstrip = set()
        for ln in prose_lines[1:]:
            for t in ln["tokens"]:
                c = canonical_4rule(t)
                if len(c) >= 3:
                    body_canon.add(c)
                g = strip_top_gallows(c)
                if len(g) >= 3:
                    body_gstrip.add(g)
        herbal_line1_stems[f_id] = l1_canon
        herbal_body_stem_sets[f_id] = body_canon
        herbal_line1_gstrips[f_id] = l1_gstrip
        herbal_body_gstrip_sets[f_id] = body_gstrip
        herbal_lang[f_id] = fd["language"] or "A"

        # Multi-paragraph header extraction
        para_starts = [ln for ln in prose_lines if ln["has_para_start"]]
        if len(para_starts) >= 2:
            p1_r = set(extract_core_root(t) for t in para_starts[0]["tokens"][:4] if len(extract_core_root(t)) >= 2)
            p2_r = set(
                extract_core_root(t)
                for ln in para_starts[1:]
                for t in ln["tokens"][:4]
                if len(extract_core_root(t)) >= 2
            )
            if p1_r and p2_r:
                multi_para_folios.append(f_id)
                para1_roots_by_folio[f_id] = p1_r
                para2plus_roots_by_folio[f_id] = p2_r

    valid_herbal = list(herbal_line1_stems.keys())

    def score_line1_recurrence(l1_map, body_map):
        hits = 0
        fol_with_hit = 0
        for f_id in valid_herbal:
            bset = body_map[f_id]
            m = sum(1 for c in l1_map[f_id] if c in bset)
            hits += m
            if m > 0:
                fol_with_hit += 1
        return hits, fol_with_hit

    obs_l1_hits, obs_l1_folios = score_line1_recurrence(herbal_line1_stems, herbal_body_stem_sets)
    obs_g_hits, obs_g_folios = score_line1_recurrence(herbal_line1_gstrips, herbal_body_gstrip_sets)

    # Score multi-paragraph header root sharing
    obs_para_header_hits = sum(
        len(para1_roots_by_folio[f] & para2plus_roots_by_folio[f]) for f in multi_para_folios
    )

    # Stratified permutation by Currier Language (A vs B)
    lang_buckets = defaultdict(list)
    for f_id in valid_herbal:
        lang_buckets[herbal_lang[f_id]].append(f_id)

    mp_buckets = defaultdict(list)
    for f_id in multi_para_folios:
        mp_buckets[herbal_lang[f_id]].append(f_id)

    null_l1_hits = []
    null_g_hits = []
    null_para_hits = []
    for _ in range(1000):
        perm_body_map = {}
        perm_g_map = {}
        for lg, flist in lang_buckets.items():
            shuffled = flist[:]
            random.shuffle(shuffled)
            for f_orig, f_shuf in zip(flist, shuffled):
                perm_body_map[f_orig] = herbal_body_stem_sets[f_shuf]
                perm_g_map[f_orig] = herbal_body_gstrip_sets[f_shuf]
        nh, _ = score_line1_recurrence(herbal_line1_stems, perm_body_map)
        ng, _ = score_line1_recurrence(herbal_line1_gstrips, perm_g_map)
        null_l1_hits.append(nh)
        null_g_hits.append(ng)

        p_hits = 0
        for lg, flist in mp_buckets.items():
            shuffled = flist[:]
            random.shuffle(shuffled)
            for f_orig, f_shuf in zip(flist, shuffled):
                p_hits += len(para1_roots_by_folio[f_orig] & para2plus_roots_by_folio[f_shuf])
        null_para_hits.append(p_hits)

    mean_nl1 = sum(null_l1_hits) / len(null_l1_hits)
    std_nl1 = math.sqrt(sum((x - mean_nl1) ** 2 for x in null_l1_hits) / len(null_l1_hits)) or 1.0
    z_l1 = (obs_l1_hits - mean_nl1) / std_nl1
    p_l1 = sum(1 for x in null_l1_hits if x >= obs_l1_hits) / len(null_l1_hits)

    mean_ng = sum(null_g_hits) / len(null_g_hits)
    std_ng = math.sqrt(sum((x - mean_ng) ** 2 for x in null_g_hits) / len(null_g_hits)) or 1.0
    z_g = (obs_g_hits - mean_ng) / std_ng
    p_g = sum(1 for x in null_g_hits if x >= obs_g_hits) / len(null_g_hits)

    mean_np = sum(null_para_hits) / len(null_para_hits)
    std_np = math.sqrt(sum((x - mean_np) ** 2 for x in null_para_hits) / len(null_para_hits)) or 1.0
    z_para = (obs_para_header_hits - mean_np) / std_np
    p_para = sum(1 for x in null_para_hits if x >= obs_para_header_hits) / len(null_para_hits)

    # Collect concrete examples where a Herbal folio's Line-1 Headword recurs in its own body
    self_echo_headwords = []
    for f_id in valid_herbal:
        fd = folios[f_id]
        prose_lines = [ln for ln in fd["lines"] if "P" in ln["loc_type"] and ln["tokens"]]
        l1_raw = prose_lines[0]["tokens"][:3]
        for raw_w in l1_raw:
            c = canonical_4rule(raw_w)
            if len(c) >= 3 and herbal_df[c] <= 25 and c in herbal_body_stem_sets[f_id]:
                body_occurrences = sum(
                    1 for ln in prose_lines[1:] for t in ln["tokens"] if canonical_4rule(t) == c
                )
                self_echo_headwords.append({
                    "folio": f_id,
                    "language": herbal_lang[f_id],
                    "line1_word": raw_w,
                    "canonical_stem": c,
                    "herbal_df": herbal_df[c],
                    "same_page_body_occurrences": body_occurrences,
                })

    # 2. Build the Herbal -> Pharmaceutical (@Lf/@Lc + Prose) & Starred Recipe ($I=S) Plant Citation Graph
    # Collect Pharmaceutical labels and prose index
    pharma_label_index = defaultdict(list)
    pharma_prose_index = defaultdict(list)
    for f_id in pharma_folios:
        for ln in folios[f_id]["lines"]:
            lt = ln["loc_type"]
            for t in ln["tokens"]:
                c = canonical_4rule(t)
                if len(c) < 3:
                    continue
                if "L" in lt:
                    pharma_label_index[c].append({"folio": f_id, "loc_id": ln["loc_id"], "loc_type": lt, "token": t})
                elif "P" in lt:
                    pharma_prose_index[c].append({"folio": f_id, "loc_id": ln["loc_id"], "token": t})

    # Collect Starred Recipe ($I=S) paragraph index
    recipe_para_index = defaultdict(list)
    for f_id in recipe_folios:
        p_idx = 0
        for ln in folios[f_id]["lines"]:
            if ln["has_para_start"]:
                p_idx += 1
            for t in ln["tokens"]:
                c = canonical_4rule(t)
                if len(c) >= 3:
                    recipe_para_index[c].append({"folio": f_id, "para": f"P{p_idx}", "loc_id": ln["loc_id"], "token": t})

    # Load pigment data if available
    pigment_by_folio = {}
    if PIGMENT_JSON.exists():
        pdata = json.loads(PIGMENT_JSON.read_text(encoding="utf-8"))
        for row in pdata.get("folio_profiles", []):
            pigment_by_folio[row["folio"]] = row

    # For each Herbal folio, compile its Line-1 Headword + Signature Rare Stems (1 <= herbal_df <= 2)
    # and check where they are cited in Pharmaceutical labels, Pharmaceutical prose, and Starred Recipes
    herbal_plant_cards = []
    high_confidence_citations = []

    for f_id in herbal_folios:
        fd = folios[f_id]
        prose_lines = [ln for ln in fd["lines"] if "P" in ln["loc_type"] and ln["tokens"]]
        l1_words = prose_lines[0]["tokens"][:3] if prose_lines else []
        l1_canons = [canonical_4rule(w) for w in l1_words if len(canonical_4rule(w)) >= 3]

        # Signature rare stems on this Herbal folio (1 <= herbal_df <= 2, length >= 4)
        sig_stems = [
            c for c, cnt in folio_canon_counts[f_id].items()
            if 1 <= herbal_df[c] <= 2 and len(c) >= 4
        ]

        # Check citations of Line-1 headwords (if herbal_df <= 10) and signature rare stems
        candidate_stems = []
        for w, c in zip(l1_words, l1_canons):
            if 1 <= herbal_df[c] <= 10:
                candidate_stems.append((c, f"Line-1 Headword ({w})", herbal_df[c]))
        for c in sig_stems:
            if c not in [x[0] for x in candidate_stems]:
                candidate_stems.append((c, "Signature Rare Stem", herbal_df[c]))

        pharma_lbl_hits = []
        pharma_prs_hits = []
        recipe_hits = []

        for c, role, hdf in candidate_stems:
            if c in pharma_label_index:
                for h in pharma_label_index[c]:
                    entry = {"stem": c, "role": role, "herbal_df": hdf, **h}
                    pharma_lbl_hits.append(entry)
                    high_confidence_citations.append({
                        "herbal_folio": f_id,
                        "herbal_language": fd["language"],
                        "stem": c,
                        "role": role,
                        "herbal_df": hdf,
                        "target_type": f"Pharma Label ({h['loc_type']})",
                        "target_folio": h["folio"],
                        "target_loc": h["loc_id"],
                        "target_token": h["token"],
                    })
            if c in pharma_prose_index:
                for h in pharma_prose_index[c][:3]:
                    pharma_prs_hits.append({"stem": c, "role": role, "herbal_df": hdf, **h})
            if c in recipe_para_index:
                for h in recipe_para_index[c][:3]:
                    recipe_hits.append({"stem": c, "role": role, "herbal_df": hdf, **h})

        herbal_plant_cards.append({
            "folio": f_id,
            "language": fd["language"],
            "hand": fd["hand"],
            "line1_opening_words": l1_words,
            "line1_canonical_stems": l1_canons,
            "signature_rare_stem_count": len(sig_stems),
            "pharma_label_citations": pharma_lbl_hits,
            "pharma_prose_citations": pharma_prs_hits[:8],
            "starred_recipe_citations": recipe_hits[:8],
        })

    folios_with_pharma_label_link = sum(1 for c in herbal_plant_cards if c["pharma_label_citations"])
    folios_with_pharma_prose_link = sum(1 for c in herbal_plant_cards if c["pharma_prose_citations"])
    folios_with_recipe_link = sum(1 for c in herbal_plant_cards if c["starred_recipe_citations"])
    folios_with_any_formulary_link = sum(
        1 for c in herbal_plant_cards
        if c["pharma_label_citations"] or c["pharma_prose_citations"] or c["starred_recipe_citations"]
    )

    result = {
        "phase": "Phase 40 / Attack 29",
        "title": "Herbal-to-Pharmaceutical & Herbal-to-Starred-Recipe Exact Plant-Identity & Line-1 Topical Headword Citation Graph",
        "line1_topical_headword_law": {
            "evaluated_herbal_folios": len(valid_herbal),
            "observed_same_folio_body_hits": obs_l1_hits,
            "observed_folios_with_line1_self_echo": obs_l1_folios,
            "null_stratified_mean": round(mean_nl1, 3),
            "null_stratified_std": round(std_nl1, 3),
            "enrichment_ratio": round(obs_l1_hits / max(mean_nl1, 1e-6), 2),
            "z_score": round(z_l1, 2),
            "p_value": round(p_l1, 4),
            "gallows_stripped_observed_hits": obs_g_hits,
            "gallows_stripped_folios_with_hit": obs_g_folios,
            "gallows_stripped_null_mean": round(mean_ng, 3),
            "gallows_stripped_null_std": round(std_ng, 3),
            "gallows_stripped_z_score": round(z_g, 2),
            "gallows_stripped_p_value": round(p_g, 4),
            "multi_paragraph_folios_count": len(multi_para_folios),
            "multi_paragraph_header_shared_roots": obs_para_header_hits,
            "multi_paragraph_null_mean": round(mean_np, 3),
            "multi_paragraph_null_std": round(std_np, 3),
            "multi_paragraph_z_score": round(z_para, 2),
            "multi_paragraph_p_value": round(p_para, 4),
            "self_echo_examples": self_echo_headwords[:30],
        },
        "herbal_to_formulary_citation_summary": {
            "total_herbal_folios": len(herbal_folios),
            "herbal_folios_linked_to_pharma_labels": folios_with_pharma_label_link,
            "herbal_folios_linked_to_pharma_prose": folios_with_pharma_prose_link,
            "herbal_folios_linked_to_starred_recipes": folios_with_recipe_link,
            "herbal_folios_linked_to_any_formulary": folios_with_any_formulary_link,
            "formulary_coverage_rate": round(folios_with_any_formulary_link / max(len(herbal_folios), 1), 4),
            "total_pharma_label_citations": len(high_confidence_citations),
        },
        "high_confidence_herbal_to_pharma_label_citations": high_confidence_citations[:50],
        "sample_herbal_plant_cards": [c for c in herbal_plant_cards if c["pharma_label_citations"]][:30],
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Line-1 Topical Headword Law:", json.dumps(result["line1_topical_headword_law"], indent=2))
    print("Herbal to Formulary Summary:", json.dumps(result["herbal_to_formulary_citation_summary"], indent=2))


if __name__ == "__main__":
    main()
