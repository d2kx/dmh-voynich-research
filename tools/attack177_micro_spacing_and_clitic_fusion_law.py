#!/usr/bin/env python3
"""
Attack 177: Uncertain vs. Certain Paleographic Word Spaces (A,B Micro-Spaces vs. A.B Standard Spaces)
& The Clitic-Host Lexical Fusion Law Across All 5 Scribe Hands ($H=1..5).

Tests across the entire ZL3b-n.txt corpus:
1. Exact count and distribution of narrow micro-spaces (`,`) vs. standard wide spaces (`.`).
2. The Lexical Fusion Law: P(AB is an attested single word in corpus | A,B) vs. P(AB is an attested word | A.B).
3. Proclitic / Enclitic morphological decomposition of A,B pairs (1-2 char prefixal A or suffixal B).
4. Scribe Hand ($H=1..5), Currier Language ($L=A/B), Section ($I), and Locus Type (@P, @L, @C/@R) stratification.
5. Normalized horizontal line position (left margin vs. interior vs. right margin / drawing intrusion <->).
6. Cross-transcriber fusion check against IT2a-n.txt and RF1b-er.txt.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[@!?\*\[\]<>]", "", t)
    return t.strip()


def load_transcriber_lines(path: Path):
    """Returns dict mapping locus_id (e.g. 'f1r.1') -> raw text body."""
    loci = {}
    if not path.exists():
        return loci
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m = re.match(r"^<([^>]+)>\s+(.*)$", raw)
        if not m:
            continue
        loc_header, body = m.group(1), m.group(2)
        # Normalise locus id to folio.line (strip @P0;H etc.)
        parts = loc_header.split(";")[0]
        parts = parts.split(",")[0]
        loc_id = re.sub(r"@.*$", "", parts)
        loci[loc_id] = body
    return loci


def main():
    zl_path = Path("data/ZL3b-n.txt")
    it_loci = load_transcriber_lines(Path("data/IT2a-n.txt"))
    rf_loci = load_transcriber_lines(Path("data/RF1b-er.txt"))

    folio_meta = {}
    cur_folio = None

    # First pass: collect all clean words and their frequencies across standard (`.`) boundaries
    word_counts = Counter()
    lines_data = []

    for raw in zl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m_page = re.match(r"^<f([0-9]+[rv][0-9]*)>\s*<!([^>]+)>", raw)
        if m_page:
            cur_folio = "f" + m_page.group(1)
            meta_str = m_page.group(2)
            meta = {}
            for kv in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str):
                meta[kv[0]] = kv[1]
            folio_meta[cur_folio] = meta
            continue

        m_line = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,@>]+)(?:[@,]([^>]+))?>\s+(.*)$", raw)
        if not m_line:
            continue
        folio = m_line.group(1)
        line_no = m_line.group(2)
        loc_tag = m_line.group(3) or ""
        body = m_line.group(4)

        has_intrusion = "<->" in body
        # Remove inline comments <! ... > but keep <-> temporarily or replace with space marker
        body_no_comments = re.sub(r"<![^>]*>", "", body)
        body_no_markers = re.sub(r"<[%$~+=\-\/!]+>", ".", body_no_comments)

        # Extract sequence of tokens and the separator (`.` or `,`) between them
        # Split into alternating [tok, sep, tok, sep, ...]
        parts = re.split(r"([.,]+)", body_no_markers.strip("., "))
        tokens = []
        seps = []
        for idx, p in enumerate(parts):
            if idx % 2 == 0:
                w = clean_tok(p)
                tokens.append(w)
            else:
                # If `,` is in the separator and not `.`, it's a comma micro-space
                sep_type = "," if ("," in p and "." not in p) else "."
                seps.append(sep_type)

        # Filter valid adjacent pairs where both tokens are non-empty alphabetic EVA
        valid_tokens = [w for w in tokens if w and re.match(r"^[a-z]+$", w)]
        for w in valid_tokens:
            word_counts[w] += 1

        lines_data.append({
            "folio": folio,
            "line_no": line_no,
            "loc_id": f"{folio}.{line_no}",
            "loc_tag": loc_tag,
            "has_intrusion": has_intrusion,
            "tokens": tokens,
            "seps": seps,
            "meta": folio_meta.get(folio, {}),
        })

    # Attested vocabulary (occurring >= 1 time and >= 2 times)
    vocab_all = set(word_counts.keys())
    vocab_ge2 = {w for w, c in word_counts.items() if c >= 2}
    vocab_ge5 = {w for w, c in word_counts.items() if c >= 5}

    comma_pairs = []
    dot_pairs = []

    by_hand = defaultdict(lambda: {"comma": 0, "dot": 0, "comma_fused_all": 0, "dot_fused_all": 0})
    by_section = defaultdict(lambda: {"comma": 0, "dot": 0})
    by_lang = defaultdict(lambda: {"comma": 0, "dot": 0})
    by_locus_type = defaultdict(lambda: {"comma": 0, "dot": 0})

    comma_norm_pos = []
    dot_norm_pos = []
    intrusion_line_comma = 0
    intrusion_line_dot = 0
    normal_line_comma = 0
    normal_line_dot = 0

    known_proclitics = {
        "o", "y", "s", "d", "r", "l", "q", "k", "t", "p", "f",
        "qo", "ol", "or", "ar", "al", "ok", "ot", "op", "of",
        "ch", "sh", "cth", "ckh", "cph", "cfh", "yk", "yt", "da", "sa", "so", "do", "po", "fo", "ko", "to"
    }
    known_enclitics = {
        "y", "dy", "ey", "edy", "aiin", "iin", "in", "n", "m", "am", "om",
        "ol", "or", "ar", "al", "s", "r", "l", "d", "g", "ky", "ty", "py", "fy", "chy", "shy"
    }

    for ld in lines_data:
        toks = ld["tokens"]
        seps = ld["seps"]
        n_seps = len(seps)
        if n_seps == 0:
            continue
        meta = ld["meta"]
        hand = meta.get("H", "U")
        sec = meta.get("I", "U")
        lang = meta.get("L", "U")
        ltag = ld["loc_tag"]
        if ltag.startswith("P"):
            ltype = "Prose (@P)"
        elif ltag.startswith("L"):
            ltype = "Label (@L)"
        elif ltag.startswith("C") or ltag.startswith("R"):
            ltype = "Ring/Radius (@C/@R)"
        else:
            ltype = "Other"

        for i, sep in enumerate(seps):
            if i >= len(toks) - 1:
                break
            a, b = toks[i], toks[i + 1]
            if not (a and b and re.match(r"^[a-z]+$", a) and re.match(r"^[a-z]+$", b)):
                continue
            ab = a + b
            fused_all = ab in vocab_all
            fused_ge2 = ab in vocab_ge2
            fused_ge5 = ab in vocab_ge5
            norm_pos = i / max(1, n_seps - 1) if n_seps > 1 else 0.5

            rec = {
                "folio": ld["folio"],
                "loc_id": ld["loc_id"],
                "a": a,
                "b": b,
                "ab": ab,
                "ab_freq": word_counts[ab],
                "len_a": len(a),
                "len_b": len(b),
                "fused_all": fused_all,
                "fused_ge2": fused_ge2,
                "fused_ge5": fused_ge5,
                "a_is_proclitic": a in known_proclitics,
                "b_is_enclitic": b in known_enclitics,
                "norm_pos": norm_pos,
                "hand": hand,
                "sec": sec,
                "lang": lang,
                "ltype": ltype,
            }

            if sep == ",":
                comma_pairs.append(rec)
                by_hand[hand]["comma"] += 1
                if fused_all:
                    by_hand[hand]["comma_fused_all"] += 1
                by_section[sec]["comma"] += 1
                by_lang[lang]["comma"] += 1
                by_locus_type[ltype]["comma"] += 1
                comma_norm_pos.append(norm_pos)
                if ld["has_intrusion"]:
                    intrusion_line_comma += 1
                else:
                    normal_line_comma += 1
            else:
                dot_pairs.append(rec)
                by_hand[hand]["dot"] += 1
                if fused_all:
                    by_hand[hand]["dot_fused_all"] += 1
                by_section[sec]["dot"] += 1
                by_lang[lang]["dot"] += 1
                by_locus_type[ltype]["dot"] += 1
                dot_norm_pos.append(norm_pos)
                if ld["has_intrusion"]:
                    intrusion_line_dot += 1
                else:
                    normal_line_dot += 1

    n_comma = len(comma_pairs)
    n_dot = len(dot_pairs)
    total_pairs = n_comma + n_dot

    # 1. Lexical Fusion Rates
    c_fused_all = sum(1 for r in comma_pairs if r["fused_all"])
    d_fused_all = sum(1 for r in dot_pairs if r["fused_all"])
    p_c_all = c_fused_all / n_comma
    p_d_all = d_fused_all / n_dot

    c_fused_ge2 = sum(1 for r in comma_pairs if r["fused_ge2"])
    d_fused_ge2 = sum(1 for r in dot_pairs if r["fused_ge2"])
    p_c_ge2 = c_fused_ge2 / n_comma
    p_d_ge2 = d_fused_ge2 / n_dot

    c_fused_ge5 = sum(1 for r in comma_pairs if r["fused_ge5"])
    d_fused_ge5 = sum(1 for r in dot_pairs if r["fused_ge5"])
    p_c_ge5 = c_fused_ge5 / n_comma
    p_d_ge5 = d_fused_ge5 / n_dot

    # Two-proportion z-score for fused_all and fused_ge2
    def two_prop_z(k1, n1, k2, n2):
        p1, p2 = k1 / n1, k2 / n2
        p_pool = (k1 + k2) / (n1 + n2)
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
        return (p1 - p2) / se if se > 0 else 0.0

    z_fused_all = two_prop_z(c_fused_all, n_comma, d_fused_all, n_dot)
    z_fused_ge2 = two_prop_z(c_fused_ge2, n_comma, d_fused_ge2, n_dot)
    z_fused_ge5 = two_prop_z(c_fused_ge5, n_comma, d_fused_ge5, n_dot)

    # 2. Length & Clitic structure
    mean_len_a_comma = sum(r["len_a"] for r in comma_pairs) / n_comma
    mean_len_b_comma = sum(r["len_b"] for r in comma_pairs) / n_comma
    mean_len_a_dot = sum(r["len_a"] for r in dot_pairs) / n_dot
    mean_len_b_dot = sum(r["len_b"] for r in dot_pairs) / n_dot

    c_short_either = sum(1 for r in comma_pairs if r["len_a"] <= 2 or r["len_b"] <= 2)
    d_short_either = sum(1 for r in dot_pairs if r["len_a"] <= 2 or r["len_b"] <= 2)
    z_short_either = two_prop_z(c_short_either, n_comma, d_short_either, n_dot)

    c_clitic_match = sum(1 for r in comma_pairs if r["a_is_proclitic"] or r["b_is_enclitic"])
    d_clitic_match = sum(1 for r in dot_pairs if r["a_is_proclitic"] or r["b_is_enclitic"])
    z_clitic_match = two_prop_z(c_clitic_match, n_comma, d_clitic_match, n_dot)

    # 3. Cross-transcriber check on comma_pairs: how often does IT2a-n or RF1b-er write `ab` as a single word (no `.` or `,`)?
    it_checked = 0
    it_fused_single_word = 0
    rf_checked = 0
    rf_fused_single_word = 0

    for r in comma_pairs:
        lid = r["loc_id"]
        ab = r["ab"]
        if lid in it_loci:
            it_body = it_loci[lid]
            it_words = [clean_tok(x) for x in re.split(r"[.,\s<>]+", it_body) if clean_tok(x)]
            it_checked += 1
            if ab in it_words:
                it_fused_single_word += 1
        if lid in rf_loci:
            rf_body = rf_loci[lid]
            rf_words = [clean_tok(x) for x in re.split(r"[.,\s<>]+", rf_body) if clean_tok(x)]
            rf_checked += 1
            if ab in rf_words:
                rf_fused_single_word += 1

    # Compare against dot_pairs sample for IT/RF single-word fusion
    dot_it_checked = 0
    dot_it_fused = 0
    for r in dot_pairs[::10]:  # 10% systematic subsample of dot_pairs
        lid = r["loc_id"]
        ab = r["ab"]
        if lid in it_loci:
            it_body = it_loci[lid]
            it_words = [clean_tok(x) for x in re.split(r"[.,\s<>]+", it_body) if clean_tok(x)]
            dot_it_checked += 1
            if ab in it_words:
                dot_it_fused += 1

    z_it_fusion = two_prop_z(it_fused_single_word, it_checked, dot_it_fused, dot_it_checked)

    # Top comma-separated pairs
    comma_pair_counts = Counter((r["a"], r["b"]) for r in comma_pairs)
    top_comma_pairs = []
    for (a, b), cnt in comma_pair_counts.most_common(35):
        ab = a + b
        top_comma_pairs.append({
            "pair": f"{a},{b}",
            "fused_word": ab,
            "comma_count": cnt,
            "fused_word_corpus_freq": word_counts[ab],
            "is_attested_word": ab in vocab_all,
            "a_is_proclitic": a in known_proclitics,
            "b_is_enclitic": b in known_enclitics,
        })

    # Hand summary
    hand_summary = {}
    for h in sorted(by_hand.keys()):
        c = by_hand[h]["comma"]
        d = by_hand[h]["dot"]
        tot = c + d
        hand_summary[h] = {
            "comma_spaces": c,
            "dot_spaces": d,
            "total_spaces": tot,
            "comma_rate_pct": round(100.0 * c / tot, 2) if tot else 0.0,
            "comma_fusion_rate_pct": round(100.0 * by_hand[h]["comma_fused_all"] / c, 2) if c else 0.0,
            "dot_fusion_rate_pct": round(100.0 * by_hand[h]["dot_fused_all"] / d, 2) if d else 0.0,
        }

    locus_summary = {}
    for lt, d in by_locus_type.items():
        tot = d["comma"] + d["dot"]
        locus_summary[lt] = {
            "comma": d["comma"],
            "dot": d["dot"],
            "total": tot,
            "comma_rate_pct": round(100.0 * d["comma"] / tot, 2) if tot else 0.0,
        }

    out = {
        "summary": {
            "total_adjacent_word_boundaries": total_pairs,
            "comma_micro_spaces": n_comma,
            "standard_dot_spaces": n_dot,
            "overall_comma_rate_pct": round(100.0 * n_comma / total_pairs, 2),
            "lexical_fusion_all_vocab": {
                "comma_fused_count": c_fused_all,
                "comma_fusion_rate_pct": round(100.0 * p_c_all, 2),
                "dot_fused_count": d_fused_all,
                "dot_fusion_rate_pct": round(100.0 * p_d_all, 2),
                "enrichment_ratio": round(p_c_all / p_d_all, 2),
                "z_score": round(z_fused_all, 2),
            },
            "lexical_fusion_freq_ge2": {
                "comma_fused_count": c_fused_ge2,
                "comma_fusion_rate_pct": round(100.0 * p_c_ge2, 2),
                "dot_fused_count": d_fused_ge2,
                "dot_fusion_rate_pct": round(100.0 * p_d_ge2, 2),
                "enrichment_ratio": round(p_c_ge2 / p_d_ge2, 2),
                "z_score": round(z_fused_ge2, 2),
            },
            "lexical_fusion_freq_ge5": {
                "comma_fused_count": c_fused_ge5,
                "comma_fusion_rate_pct": round(100.0 * p_c_ge5, 2),
                "dot_fused_count": d_fused_ge5,
                "dot_fusion_rate_pct": round(100.0 * p_d_ge5, 2),
                "enrichment_ratio": round(p_c_ge5 / p_d_ge5, 2),
                "z_score": round(z_fused_ge5, 2),
            },
            "morphological_clitic_structure": {
                "mean_len_a_comma": round(mean_len_a_comma, 2),
                "mean_len_b_comma": round(mean_len_b_comma, 2),
                "mean_len_a_dot": round(mean_len_a_dot, 2),
                "mean_len_b_dot": round(mean_len_b_dot, 2),
                "short_1to2char_member_comma_pct": round(100.0 * c_short_either / n_comma, 2),
                "short_1to2char_member_dot_pct": round(100.0 * d_short_either / n_dot, 2),
                "z_short_member": round(z_short_either, 2),
                "known_clitic_member_comma_pct": round(100.0 * c_clitic_match / n_comma, 2),
                "known_clitic_member_dot_pct": round(100.0 * d_clitic_match / n_dot, 2),
                "z_clitic_member": round(z_clitic_match, 2),
            },
            "cross_transcriber_single_word_fusion": {
                "it_checked_comma_pairs": it_checked,
                "it_fused_as_single_word": it_fused_single_word,
                "it_comma_single_word_pct": round(100.0 * it_fused_single_word / it_checked, 2) if it_checked else 0.0,
                "it_dot_single_word_pct": round(100.0 * dot_it_fused / dot_it_checked, 2) if dot_it_checked else 0.0,
                "it_enrichment_ratio": round((it_fused_single_word / it_checked) / (dot_it_fused / dot_it_checked), 2) if dot_it_fused else 0.0,
                "z_it_fusion": round(z_it_fusion, 2),
                "rf_checked_comma_pairs": rf_checked,
                "rf_fused_as_single_word": rf_fused_single_word,
                "rf_comma_single_word_pct": round(100.0 * rf_fused_single_word / rf_checked, 2) if rf_checked else 0.0,
            },
            "line_position_and_intrusions": {
                "mean_norm_pos_comma": round(sum(comma_norm_pos) / len(comma_norm_pos), 4),
                "mean_norm_pos_dot": round(sum(dot_norm_pos) / len(dot_norm_pos), 4),
                "intrusion_line_comma_rate_pct": round(100.0 * intrusion_line_comma / (intrusion_line_comma + intrusion_line_dot), 2),
                "normal_line_comma_rate_pct": round(100.0 * normal_line_comma / (normal_line_comma + normal_line_dot), 2),
            },
        },
        "by_scribe_hand": hand_summary,
        "by_locus_type": locus_summary,
        "top_35_comma_micro_spaced_pairs": top_comma_pairs,
    }

    out_path = Path("data/attack177_micro_spacing_and_clitic_fusion_law.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out["summary"], indent=2))
    print("\nBy Scribe Hand:")
    print(json.dumps(hand_summary, indent=2))
    print("\nTop 15 Comma Pairs:")
    for item in top_comma_pairs[:15]:
        print(" ", item)


if __name__ == "__main__":
    main()
