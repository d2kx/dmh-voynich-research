#!/usr/bin/env python3
"""
Attack 175: The Complete Plumed Bench-Gallows ({cthh}, {ckhh}, {cphh}, {cfhh}) Allographic
Reduction Proof and the Rare Non-Standard EVA Weirdo-Glyph (@132;..@252;) Structural Atlas.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack175_plumed_gallows_and_weirdo_glyph_atlas.json"


def parse_corpus():
    standard_vocab = Counter()
    plumed_occurrences = []
    weirdo_occurrences = []
    total_tokens = 0
    total_label_tokens = 0
    total_prose_tokens = 0

    cur_folio = None
    cur_meta = {}

    with open(ZL_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_f = re.match(r"^<(f\d+[rv]\d*)>\s*(?:<!\s*(.*?)\s*>)?", line)
            if m_f and "." not in line.split(">")[0]:
                cur_folio = m_f.group(1)
                meta_str = m_f.group(2) or ""
                cur_meta = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str))
                continue

            m_l = re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$", line)
            if not m_l:
                continue
            fol, lno, ltype, body = m_l.group(1), int(m_l.group(2)), m_l.group(3), m_l.group(4)
            is_para_start_line = "<%>" in body
            is_para_end_line = "<$>" in body
            body_clean = re.sub(r"<![^>]*>", "", body)
            body_clean = re.sub(r"<[^>]*>", " ", body_clean)
            # Replace [a:b] with a
            body_clean = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", body_clean)

            raw_toks = [t.strip() for t in re.split(r"[.\s,]+", body_clean) if t.strip()]
            is_label = any(x in ltype for x in ("L", "R", "C"))

            for idx, rt in enumerate(raw_toks):
                total_tokens += 1
                if is_label:
                    total_label_tokens += 1
                else:
                    total_prose_tokens += 1

                # Check for plumed gallows {cthh}, {ckhh}, {cphh}, {cfhh}
                m_plumed = re.findall(r"\{(c[tkpf]hh\d*)\}", rt)
                if m_plumed:
                    # Reduced form: replace {cthh...} with cth, {ckhh...} with ckh, etc.
                    reduced_cth = re.sub(r"\{(c[tkpf]h)h\d*\}", r"\1", rt)
                    reduced_cth = re.sub(r"\{([^}]*)\}", r"\1", reduced_cth)
                    reduced_cth = re.sub(r"[^a-zA-Z0-9]", "", reduced_cth)

                    reduced_ch = re.sub(r"\{c[tkpf]hh\d*\}", "ch", rt)
                    reduced_ch = re.sub(r"\{([^}]*)\}", r"\1", reduced_ch)
                    reduced_ch = re.sub(r"[^a-zA-Z0-9]", "", reduced_ch)

                    plumed_occurrences.append({
                        "folio": fol,
                        "lno": lno,
                        "ltype": ltype,
                        "section": cur_meta.get("I", "?"),
                        "lang": cur_meta.get("L", "?"),
                        "hand": cur_meta.get("H", "?"),
                        "raw_token": rt,
                        "plumed_types": m_plumed,
                        "reduced_single_loop": reduced_cth,
                        "reduced_ch": reduced_ch,
                        "is_line_initial": (idx == 0),
                        "is_line_final": (idx == len(raw_toks) - 1),
                        "is_para_start_line": is_para_start_line,
                        "is_label": is_label,
                    })

                # Check for @NNN; weirdo glyphs
                m_weirdo = re.findall(r"(@\d+;)", rt)
                if m_weirdo:
                    weirdo_occurrences.append({
                        "folio": fol,
                        "lno": lno,
                        "ltype": ltype,
                        "section": cur_meta.get("I", "?"),
                        "lang": cur_meta.get("L", "?"),
                        "hand": cur_meta.get("H", "?"),
                        "raw_token": rt,
                        "weirdo_codes": m_weirdo,
                        "is_standalone_single_glyph": (rt in m_weirdo),
                        "is_word_initial": rt.startswith(m_weirdo[0]),
                        "is_word_final": rt.endswith(m_weirdo[-1]),
                        "is_line_initial": (idx == 0),
                        "is_line_final": (idx == len(raw_toks) - 1),
                        "is_label": is_label,
                    })

                # Standard token (without plumed or weirdo)
                if not m_plumed and not m_weirdo:
                    st = re.sub(r"\{([^}]*)\}", r"\1", rt)
                    st = re.sub(r"[^a-zA-Z0-9]", "", st)
                    if st:
                        standard_vocab[st] += 1

    return standard_vocab, plumed_occurrences, weirdo_occurrences, total_tokens, total_label_tokens, total_prose_tokens


def canonical_stem(w: str) -> str:
    s = w
    for p in ("qo", "ch", "sh", "cth", "ckh", "cph", "cfh", "ok", "ot", "op", "of", "yk", "yt", "da", "sa", "so", "ol", "or", "al", "ar", "o", "y", "d", "s"):
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ("aiin", "oiin", "eiin", "chedy", "shedy", "edy", "eey", "ody", "oldy", "aldy", "am", "om", "aim", "ol", "or", "al", "ar", "dy", "ey", "hy", "ky", "ly", "ry", "y", "m", "n", "l", "r"):
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s if len(s) >= 2 else w


def main():
    standard_vocab, plumed, weirdos, tot_toks, tot_lbl_toks, tot_prose_toks = parse_corpus()
    standard_stems = Counter()
    for w, c in standard_vocab.items():
        standard_stems[canonical_stem(w)] += c

    # 1. Plumed Bench-Gallows Analysis
    plumed_by_type = Counter(pt for p in plumed for pt in p["plumed_types"])
    plumed_by_sec = Counter(p["section"] for p in plumed)
    plumed_by_lang = Counter(p["lang"] for p in plumed)
    plumed_by_hand = Counter(p["hand"] for p in plumed)

    exact_word_collapse_single = 0
    exact_word_collapse_either = 0
    canonical_stem_collapse = 0
    collapse_examples = []

    for p in plumed:
        w1 = p["reduced_single_loop"]
        w2 = p["reduced_ch"]
        c1 = standard_vocab.get(w1, 0)
        c2 = standard_vocab.get(w2, 0)
        sc1 = standard_stems.get(canonical_stem(w1), 0)
        if c1 > 0:
            exact_word_collapse_single += 1
        if c1 > 0 or c2 > 0:
            exact_word_collapse_either += 1
        if sc1 > 0:
            canonical_stem_collapse += 1
        collapse_examples.append({
            "folio_line": f"{p['folio']}.{p['lno']}",
            "section": p["section"],
            "hand": p["hand"],
            "raw_token": p["raw_token"],
            "reduced_single_loop": w1,
            "standard_exact_count_single_loop": c1,
            "reduced_ch": w2,
            "standard_exact_count_ch": c2,
            "canonical_stem": canonical_stem(w1),
            "standard_stem_count": sc1,
        })

    # Sort collapse examples by standard_exact_count_single_loop desc
    collapse_examples_sorted = sorted(collapse_examples, key=lambda x: (x["standard_exact_count_single_loop"], x["standard_exact_count_ch"]), reverse=True)

    # 2. Rare Non-Standard (@NNN;) Weirdo-Glyph Atlas
    weirdo_code_counts = Counter(wc for w in weirdos for wc in w["weirdo_codes"])
    weirdo_in_labels = sum(1 for w in weirdos if w["is_label"])
    weirdo_standalone = sum(1 for w in weirdos if w["is_standalone_single_glyph"])
    weirdo_word_initial = sum(1 for w in weirdos if not w["is_standalone_single_glyph"] and w["is_word_initial"])
    weirdo_word_final = sum(1 for w in weirdos if not w["is_standalone_single_glyph"] and w["is_word_final"])
    weirdo_word_medial = sum(1 for w in weirdos if not w["is_standalone_single_glyph"] and not w["is_word_initial"] and not w["is_word_final"])

    # Label enrichment ratio for weirdo glyphs vs baseline corpus label rate
    corpus_label_rate = tot_lbl_toks / max(1, tot_toks)
    weirdo_label_rate = weirdo_in_labels / max(1, len(weirdos))
    weirdo_label_enrichment = weirdo_label_rate / max(1e-9, corpus_label_rate)

    # Functional Allograph Substitution Decoder for embedded @NNN; tokens
    candidate_subs = ["o", "y", "d", "s", "r", "l", "m", "n", "k", "t", "p", "f", "ch", "sh", "e", "a", "i", "aiin", "dy", "ey"]
    embedded_weirdo_resolved = 0
    embedded_weirdo_total = 0
    code_best_subs = defaultdict(Counter)
    weirdo_decoded_examples = []

    for w in weirdos:
        if w["is_standalone_single_glyph"]:
            continue
        embedded_weirdo_total += 1
        rt = w["raw_token"]
        # Strip braces if any
        rt_clean = re.sub(r"\{([^}]*)\}", r"\1", rt)
        codes = w["weirdo_codes"]
        best_word = None
        best_sub = None
        best_freq = 0
        for sub in candidate_subs:
            cand = rt_clean
            for c in codes:
                cand = cand.replace(c, sub)
            cand = re.sub(r"[^a-zA-Z0-9]", "", cand)
            freq = standard_vocab.get(cand, 0)
            if freq > best_freq:
                best_freq = freq
                best_word = cand
                best_sub = sub
        if best_freq > 0:
            embedded_weirdo_resolved += 1
            for c in codes:
                code_best_subs[c][best_sub] += 1
        weirdo_decoded_examples.append({
            "folio_line": f"{w['folio']}.{w['lno']}",
            "ltype": w["ltype"],
            "raw_token": rt,
            "weirdo_codes": codes,
            "best_allograph_sub": best_sub,
            "resolved_standard_word": best_word,
            "standard_word_corpus_freq": best_freq,
        })

    top_weirdo_table = []
    for code, cnt in weirdo_code_counts.most_common(20):
        # Find where it occurs
        occ = [w for w in weirdos if code in w["weirdo_codes"]]
        n_standalone = sum(1 for w in occ if w["is_standalone_single_glyph"])
        n_init = sum(1 for w in occ if not w["is_standalone_single_glyph"] and w["is_word_initial"])
        n_final = sum(1 for w in occ if not w["is_standalone_single_glyph"] and w["is_word_final"])
        n_med = len(occ) - n_standalone - n_init - n_final
        top_subs = code_best_subs[code].most_common(3)
        top_weirdo_table.append({
            "code": code,
            "count": cnt,
            "standalone_count": n_standalone,
            "word_initial_count": n_init,
            "word_final_count": n_final,
            "word_medial_count": n_med,
            "top_allograph_substitutions": [{"sub": s, "matches": m} for s, m in top_subs],
            "sample_folios": sorted(set(w["folio"] for w in occ))[:6],
        })

    out = {
        "attack": "Attack 175: Plumed Bench-Gallows Allographic Reduction Proof & Rare Weirdo-Glyph (@NNN;) Structural Atlas",
        "plumed_gallows_analysis": {
            "total_plumed_tokens": len(plumed),
            "counts_by_type": dict(plumed_by_type),
            "counts_by_section": dict(plumed_by_sec),
            "counts_by_language": dict(plumed_by_lang),
            "counts_by_hand": dict(plumed_by_hand),
            "para_start_line_pct": round(100.0 * sum(1 for p in plumed if p["is_para_start_line"]) / max(1, len(plumed)), 2),
            "exact_word_collapse_single_loop_count": exact_word_collapse_single,
            "exact_word_collapse_single_loop_pct": round(100.0 * exact_word_collapse_single / max(1, len(plumed)), 2),
            "exact_word_collapse_single_or_ch_count": exact_word_collapse_either,
            "exact_word_collapse_single_or_ch_pct": round(100.0 * exact_word_collapse_either / max(1, len(plumed)), 2),
            "canonical_stem_collapse_count": canonical_stem_collapse,
            "canonical_stem_collapse_pct": round(100.0 * canonical_stem_collapse / max(1, len(plumed)), 2),
            "top_collapsed_examples": collapse_examples_sorted[:25],
        },
        "weirdo_glyph_atlas": {
            "total_weirdo_tokens": len(weirdos),
            "distinct_weirdo_codes": len(weirdo_code_counts),
            "in_labels_or_keys_count": weirdo_in_labels,
            "in_labels_or_keys_pct": round(100.0 * weirdo_label_rate, 2),
            "corpus_baseline_label_pct": round(100.0 * corpus_label_rate, 2),
            "label_enrichment_ratio": round(weirdo_label_enrichment, 2),
            "standalone_single_glyph_count": weirdo_standalone,
            "standalone_single_glyph_pct": round(100.0 * weirdo_standalone / max(1, len(weirdos)), 2),
            "embedded_word_initial_count": weirdo_word_initial,
            "embedded_word_final_count": weirdo_word_final,
            "embedded_word_medial_count": weirdo_word_medial,
            "embedded_weirdo_total": embedded_weirdo_total,
            "embedded_weirdo_resolved_to_attested_word": embedded_weirdo_resolved,
            "embedded_weirdo_resolved_pct": round(100.0 * embedded_weirdo_resolved / max(1, embedded_weirdo_total), 2),
            "top_20_weirdo_codes": top_weirdo_table,
            "sample_decoded_embedded_tokens": [x for x in weirdo_decoded_examples if x["standard_word_corpus_freq"] > 0][:30],
        },
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== Attack 175 Summary ===")
    print(f"Plumed Gallows (n={len(plumed)}): Exact Single-Loop Collapse={exact_word_collapse_single}/{len(plumed)} ({out['plumed_gallows_analysis']['exact_word_collapse_single_loop_pct']}%), Single-or-ch Collapse={exact_word_collapse_either}/{len(plumed)} ({out['plumed_gallows_analysis']['exact_word_collapse_single_or_ch_pct']}%), Canonical Stem Collapse={canonical_stem_collapse}/{len(plumed)} ({out['plumed_gallows_analysis']['canonical_stem_collapse_pct']}%)")
    print(f"Weirdo Glyphs (@NNN;, n={len(weirdos)}, {len(weirdo_code_counts)} distinct codes): In Labels/Keys={weirdo_in_labels}/{len(weirdos)} ({out['weirdo_glyph_atlas']['in_labels_or_keys_pct']}% vs {out['weirdo_glyph_atlas']['corpus_baseline_label_pct']}% baseline, {weirdo_label_enrichment:.2f}x); Standalone={weirdo_standalone} ({out['weirdo_glyph_atlas']['standalone_single_glyph_pct']}%); Embedded Resolved to Standard Word={embedded_weirdo_resolved}/{embedded_weirdo_total} ({out['weirdo_glyph_atlas']['embedded_weirdo_resolved_pct']}%)")


if __name__ == "__main__":
    main()
