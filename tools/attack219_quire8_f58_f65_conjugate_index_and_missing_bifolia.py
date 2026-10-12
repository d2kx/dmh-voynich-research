#!/usr/bin/env python3
"""
Attack 219 (Discovery 236): Quire 8 (f57r-f66v) 100% Visual & Bifolium Architecture,
Scribe 3's 10-Paragraph Starred Herbal Index (f58r-f58v) for the 10-Leaf Quire (with 6 Missing Leaves f59-f64),
and Conjugate/Facing Coupling across f58r/v <-> f65r/v <-> f66r/v.
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

def normalize_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = w.replace("<->", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    w = re.sub(r"[^a-zA-Z0-9']", "", w)
    return w.strip().lower()

def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = re.sub(r"^p", "t", s)
    s = re.sub(r"^f", "k", s)
    s = re.sub(r"^cph", "cth", s)
    s = re.sub(r"^cfh", "ckh", s)
    s = s.replace("iin", "N").replace("in", "n")
    for suf in ["edy", "ody", "ey", "dy", "y", "aN", "oN", "eN", "N", "ar", "or", "al", "ol", "am", "om", "an", "on"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s

def parse_zl(zl_path: str):
    folio_words = defaultdict(list)
    folio_paras = defaultdict(list)
    folio_meta = {}
    current_folio = None
    current_para = None

    with open(zl_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_fol = re.match(r"^<(f[a-zA-Z0-9]+)>\s*(.*)$", line)
            if m_fol:
                current_folio = m_fol.group(1)
                hdr = m_fol.group(2)
                meta = {}
                for k, v in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", hdr):
                    meta[k] = v
                folio_meta[current_folio] = meta
                current_para = None
                continue
            m_loc = re.match(r"^<(f[a-zA-Z0-9]+)\.([^>]+)>\s+(.*)$", line)
            if not m_loc:
                continue
            fol, loc, body = m_loc.group(1), m_loc.group(2), m_loc.group(3)
            clean_body = re.sub(r"<[^>]*>", " ", body)
            tokens = [normalize_word(t) for t in re.split(r"[.\s,]+", clean_body)]
            tokens = [t for t in tokens if t]
            if not tokens:
                continue
            folio_words[fol].extend(tokens)
            if "P" in loc:
                if "<%>" in body or current_para is None:
                    if current_para is not None:
                        folio_paras[fol].append(current_para)
                    current_para = {"loc": f"{fol}.{loc}", "words": list(tokens)}
                else:
                    current_para["words"].extend(tokens)
                if "<$>" in body and current_para is not None:
                    folio_paras[fol].append(current_para)
                    current_para = None
    for fol in list(folio_words.keys()):
        if current_para and current_para["loc"].startswith(fol + "."):
            folio_paras[fol].append(current_para)
            current_para = None
    return folio_words, folio_paras, folio_meta

def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)

def token_coverage(target_words, source_stems: set) -> float:
    if not target_words:
        return 0.0
    return sum(1 for w in target_words if canonical_stem(w) in source_stems) / len(target_words)

def main():
    zl_path = os.path.join("data", "ZL3b-n.txt")
    folio_words, folio_paras, folio_meta = parse_zl(zl_path)

    q8_folios = ["f57r", "f57v", "f58r", "f58v", "f65r", "f65v", "f66r", "f66v"]
    pages_files = [p for p in os.listdir("pages") if p.endswith(".png")]

    # 1. Quire 8 8/8 Visual & Codicological Profile
    q8_profiles = {}
    for fol in q8_folios:
        words = folio_words[fol]
        stems = [canonical_stem(w) for w in words]
        paras = folio_paras[fol]
        pngs = sorted([p for p in pages_files if p.startswith(fol + "_")])
        q8_profiles[fol] = {
            "rendered": len(pngs) > 0,
            "files": pngs,
            "meta": folio_meta.get(fol, {}),
            "words": len(words),
            "unique_stems": len(set(stems)),
            "paragraphs": len(paras),
            "para_openers": [p["words"][0] for p in paras if p["words"]],
            "q_pct": round(100.0 * sum(1 for w in words if w.startswith("q")) / max(1, len(words)), 2),
            "edy_pct": round(100.0 * sum(1 for w in words if w.endswith("edy")) / max(1, len(words)), 2),
            "aiin_pct": round(100.0 * sum(1 for w in words if w.endswith("aiin")) / max(1, len(words)), 2),
            "o_initial_pct": round(100.0 * sum(1 for w in words if w.startswith("o")) / max(1, len(words)), 2),
            "top_words": Counter(words).most_common(8)
        }

    # 2. Bifolium Architecture of Quire 8:
    # Original 5 bifolia (10 leaves: f57..f66):
    # Bifolium #1 (outer): f57r/v ($H=5/$H=1) <-> f66r/v ($H=5)
    # Bifolium #2 (inner surviving): f58r/v ($H=3, Starred Index) <-> f65r/v ($H=3, Herbal)
    # Bifolia #3, #4, #5 (missing 6 leaves: f59, f60, f61, f62, f63, f64)
    f58_words = folio_words["f58r"] + folio_words["f58v"]
    f58_stems = set(canonical_stem(w) for w in f58_words)
    s58r = set(canonical_stem(w) for w in folio_words["f58r"])
    s58v = set(canonical_stem(w) for w in folio_words["f58v"])
    s65r = set(canonical_stem(w) for w in folio_words["f65r"])
    s65v = set(canonical_stem(w) for w in folio_words["f65v"])
    s66r = set(canonical_stem(w) for w in folio_words["f66r"])
    s66v = set(canonical_stem(w) for w in folio_words["f66v"])
    s57r = set(canonical_stem(w) for w in folio_words["f57r"])
    s57v = set(canonical_stem(w) for w in folio_words["f57v"])

    f58_index_analysis = {
        "f58r_words": len(folio_words["f58r"]),
        "f58v_words": len(folio_words["f58v"]),
        "total_f58_words": len(f58_words),
        "f58r_starred_paragraphs": len(folio_paras["f58r"]),
        "f58v_starred_paragraphs": len(folio_paras["f58v"]),
        "total_f58_starred_paragraphs": len(folio_paras["f58r"]) + len(folio_paras["f58v"]),
        "original_quire8_leaves_count": 10,
        "surviving_quire8_leaves_count": 4,
        "missing_quire8_leaves_count": 6,
        "f58r_to_f58v_token_cov_pct": round(100.0 * token_coverage(folio_words["f58v"], s58r), 2),
        "f58v_to_f58r_token_cov_pct": round(100.0 * token_coverage(folio_words["f58r"], s58v), 2),
        "f58r_f58v_stem_jaccard": round(jaccard(s58r, s58v), 4),
        "f58_covers_conjugate_f65v_token_pct": round(100.0 * token_coverage(folio_words["f65v"], f58_stems), 2),
        "f58_covers_conjugate_f65r_v_token_pct": round(100.0 * token_coverage(folio_words["f65r"] + folio_words["f65v"], f58_stems), 2),
        "f58_covers_f66r_token_pct": round(100.0 * token_coverage(folio_words["f66r"], f58_stems), 2),
        "f58_covers_f66v_token_pct": round(100.0 * token_coverage(folio_words["f66v"], f58_stems), 2),
        "f58_covers_f57r_token_pct": round(100.0 * token_coverage(folio_words["f57r"], f58_stems), 2),
        "f58_covers_f57v_token_pct": round(100.0 * token_coverage(folio_words["f57v"], f58_stems), 2),
    }

    # 3. Controlled Within-Scribe ($H=3) Cross-Language ($L=A on f58r-v vs $L=B in Quire 20) Experiment
    q20_folios = [fol for fol, m in folio_meta.items() if m.get("I") == "S" and fol not in ("f58r", "f58v")]
    q20_words = [w for fol in q20_folios for w in folio_words[fol]]
    q20_word_set = set(q20_words)
    q20_stems = set(canonical_stem(w) for w in q20_words)
    herbal_b_folios = [fol for fol, m in folio_meta.items() if m.get("I") == "H" and m.get("L") == "B" and fol not in ("f58r", "f58v")]
    herbal_a_folios = [fol for fol, m in folio_meta.items() if m.get("I") == "H" and m.get("L") == "A"]
    hb_words = [w for fol in herbal_b_folios for w in folio_words[fol]]
    ha_words = [w for fol in herbal_a_folios for w in folio_words[fol]]
    ha_h3_folios = [fol for fol, m in folio_meta.items() if m.get("H") == "3" and fol not in ("f58r", "f58v")]

    raw_f58_in_q20_pct = round(100.0 * sum(1 for w in f58_words if w in q20_word_set) / len(f58_words), 2)
    stem_f58_in_q20_pct = round(100.0 * token_coverage(f58_words, q20_stems), 2)

    cross_section_routing = {
        "f58_raw_word_covered_by_quire20_pct": raw_f58_in_q20_pct,
        "f58_canonical_stem_covered_by_quire20_pct": stem_f58_in_q20_pct,
        "canonical_normalization_lift_ratio": round(stem_f58_in_q20_pct / max(0.01, raw_f58_in_q20_pct), 2),
        "f58_seeds_quire20_token_pct": round(100.0 * token_coverage(q20_words, f58_stems), 2),
        "f58_seeds_herbal_b_token_pct": round(100.0 * token_coverage(hb_words, f58_stems), 2),
        "f58_seeds_herbal_a_token_pct": round(100.0 * token_coverage(ha_words, f58_stems), 2),
        "f58_mean_jaccard_with_quire20_pages": round(
            sum(jaccard(f58_stems, set(canonical_stem(w) for w in folio_words[fol])) for fol in q20_folios) / len(q20_folios),
            4
        ),
        "f58_mean_jaccard_with_herbal_b_pages": round(
            sum(jaccard(f58_stems, set(canonical_stem(w) for w in folio_words[fol])) for fol in herbal_b_folios) / len(herbal_b_folios),
            4
        ),
        "f58_mean_jaccard_with_herbal_a_pages": round(
            sum(jaccard(f58_stems, set(canonical_stem(w) for w in folio_words[fol])) for fol in herbal_a_folios) / len(herbal_a_folios),
            4
        ),
    }

    # 4. f65v (Daisy-Button + Blue-Calyx Conjugate Herbal) Bridge Analysis:
    # How f65v (44 words) bridges Bifolium #2 (f58r/v) and facing Bifolium #1 (f66r/v)
    f65v_words = folio_words["f65v"]
    f65v_bridge = {
        "f65v_words_count": len(f65v_words),
        "f65v_words_list": f65v_words,
        "covered_by_conjugate_f58r_v_pct": round(100.0 * token_coverage(f65v_words, f58_stems), 2),
        "covered_by_facing_f66r_pct": round(100.0 * token_coverage(f65v_words, s66r), 2),
        "covered_by_f66r_v_pct": round(100.0 * token_coverage(f65v_words, s66r | s66v), 2),
        "covered_by_quire8_rest_pct": round(100.0 * token_coverage(f65v_words, f58_stems | s66r | s66v | s57r | s57v | s65r), 2),
        "covered_by_quire20_pct": round(100.0 * token_coverage(f65v_words, q20_stems), 2),
        "shared_exact_words_with_f58": sorted(list(set(f65v_words) & set(f58_words))),
        "shared_exact_words_with_facing_f66r": sorted(list(set(f65v_words) & set(folio_words["f66r"])))
    }

    out = {
        "attack": 219,
        "discovery": 236,
        "title": "Quire 8 (f57r-f66v) 100% Visual & Bifolium Architecture, Scribe 3's 10-Paragraph Starred Herbal Index (f58r-f58v), and f65v Conjugate/Facing Bridge",
        "quire8_visual_and_folio_profiles": q8_profiles,
        "f58_starred_herbal_index_analysis": f58_index_analysis,
        "f58_cross_section_routing": cross_section_routing,
        "f65v_conjugate_and_facing_bridge": f65v_bridge
    }

    out_path = os.path.join("data", "attack219_quire8_f58_f65_conjugate_index_and_missing_bifolia.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")
    for fol, p in q8_profiles.items():
        print(f"  {fol}: rendered={p['rendered']}, $H={p['meta'].get('H')}, $L={p['meta'].get('L')}, $I={p['meta'].get('I')}, {p['words']}w, {p['paragraphs']} paras, q={p['q_pct']}%, edy={p['edy_pct']}%, o={p['o_initial_pct']}%")
    print(f"f58r<->f58v: {f58_index_analysis['f58r_starred_paragraphs']}+{f58_index_analysis['f58v_starred_paragraphs']}={f58_index_analysis['total_f58_starred_paragraphs']} starred paras (matching 10 original Quire 8 leaves!); Jaccard={f58_index_analysis['f58r_f58v_stem_jaccard']}, cov={f58_index_analysis['f58r_to_f58v_token_cov_pct']}% / {f58_index_analysis['f58v_to_f58r_token_cov_pct']}%")
    print(f"f58 covers conjugate f65v: {f58_index_analysis['f58_covers_conjugate_f65v_token_pct']}%, covers f66r: {f58_index_analysis['f58_covers_f66r_token_pct']}%, covers f57v: {f58_index_analysis['f58_covers_f57v_token_pct']}%")
    print(f"f58 <-> Quire 20: raw word cov = {cross_section_routing['f58_raw_word_covered_by_quire20_pct']}%, canonical stem cov = {cross_section_routing['f58_canonical_stem_covered_by_quire20_pct']}% ({cross_section_routing['canonical_normalization_lift_ratio']}x lift), f58 seeds Q20 = {cross_section_routing['f58_seeds_quire20_token_pct']}%, seeds Herbal-B = {cross_section_routing['f58_seeds_herbal_b_token_pct']}% vs Herbal-A = {cross_section_routing['f58_seeds_herbal_a_token_pct']}%")
    print(f"f65v (44w): covered by conjugate f58={f65v_bridge['covered_by_conjugate_f58r_v_pct']}%, by facing f66r={f65v_bridge['covered_by_facing_f66r_pct']}%, by Quire 8 rest={f65v_bridge['covered_by_quire8_rest_pct']}%, by Quire 20={f65v_bridge['covered_by_quire20_pct']}%")

if __name__ == "__main__":
    main()
