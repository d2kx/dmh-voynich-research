#!/usr/bin/env python3
"""
Attack 178: The `f57v` Four-Ring Character-Cycle Key Wheel (`o l d r v x k m [f/p] t r y c`),
the `f68r1-3` Pleiades/Lunar Triad, & the Complete Taxonomy of All Circular Ring (`@C`)
and Radial Spoke (`@R`) Loci in the Codex.
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


def canonical_stem(w: str) -> str:
    if not w:
        return ""
    s = w
    for p in ("qok", "qot", "qo", "ch", "sh", "cth", "ckh", "cph", "cfh", "ok", "ot", "op", "of", "yk", "yt", "da", "sa"):
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    for suf in ("aiin", "oiin", "eiin", "iin", "edy", "eey", "ody", "ey", "dy", "ol", "or", "ar", "al", "am", "om", "an", "in", "y", "r", "l", "s", "d"):
        if s.endswith(suf) and len(s) > len(suf) + 1:
            s = s[:-len(suf)]
            break
    return "s_" + s


def autocorr_periodicity(seq):
    """Find best repeating period k (8 <= k <= max(9, len(seq)//2)) by exact match rate."""
    n = len(seq)
    if n < 16:
        return None, 0.0, {}
    best_k = None
    best_rate = 0.0
    period_scores = {}
    for k in range(8, n // 2 + 1):
        matches = sum(1 for i in range(n - k) if seq[i] == seq[i + k])
        total = n - k
        rate = matches / total if total > 0 else 0.0
        period_scores[k] = round(100.0 * rate, 2)
        if rate > best_rate:
            best_rate = rate
            best_k = k
    return best_k, round(100.0 * best_rate, 2), period_scores


def main():
    zl_path = Path("data/ZL3b-n.txt")
    f57v_loci = []
    all_ring_loci = []
    all_radial_loci = []
    f68r_loci = defaultdict(list)
    folio_tokens = defaultdict(list)

    for raw in zl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m_line = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,@>]+)(?:[@,]([^>]+))?>\s+(.*)$", raw)
        if not m_line:
            continue
        folio = m_line.group(1)
        line_no = m_line.group(2)
        loc_tag_raw = m_line.group(3) or ""
        loc_tag = loc_tag_raw.lstrip("@+=*").split(";")[0]
        body = m_line.group(4)

        body_clean = re.sub(r"<![^>]*>", "", body)
        body_clean = re.sub(r"<[^>]*>", " ", body_clean)
        toks = [clean_tok(x) for x in re.split(r"[.,\s]+", body_clean) if clean_tok(x)]
        alpha_toks = [t for t in toks if re.match(r"^[a-z]+$", t)]
        folio_tokens[folio].extend(alpha_toks)

        rec = {
            "folio": folio,
            "line_no": line_no,
            "loc_id": f"{folio}.{line_no}",
            "loc_tag": loc_tag,
            "n_tokens": len(alpha_toks),
            "mean_token_len": round(sum(len(t) for t in alpha_toks) / len(alpha_toks), 2) if alpha_toks else 0.0,
            "single_char_rate_pct": round(100.0 * sum(1 for t in alpha_toks if len(t) == 1) / len(alpha_toks), 2) if alpha_toks else 0.0,
            "edy_rate_pct": round(100.0 * sum(1 for t in alpha_toks if t.endswith("edy")) / len(alpha_toks), 2) if alpha_toks else 0.0,
            "tokens": alpha_toks,
            "raw_body": body_clean.strip(),
        }

        if folio == "f57v":
            f57v_loci.append(rec)
        if folio in ("f68r1", "f68r2", "f68r3"):
            f68r_loci[folio].append(rec)
        if loc_tag.startswith("C"):
            all_ring_loci.append(rec)
        elif loc_tag.startswith("R"):
            all_radial_loci.append(rec)

    # Analyze f57v 4 concentric rings in detail
    f57v_ring_analysis = []
    for r in f57v_loci:
        toks = r["tokens"]
        best_k, best_rate, pscores = autocorr_periodicity(toks)
        f57v_ring_analysis.append({
            "loc_id": r["loc_id"],
            "loc_tag": r["loc_tag"],
            "n_tokens": r["n_tokens"],
            "mean_token_len": r["mean_token_len"],
            "single_char_rate_pct": r["single_char_rate_pct"],
            "best_token_period_k": best_k,
            "best_token_period_match_pct": best_rate,
            "full_string": " ".join(toks),
        })

    # Exact 4-quadrant alignment of f57v.3 (Ring 2 from outside)
    # Sequence:
    # Q1 (12 chars, missing final 'c'): o l d r v x k m f t r y
    # Q2 (13 chars):                     o l d r v x k m f t r y c
    # Q3 (13 chars):                     o l d r v x k m p t r y c
    # Q4 (13 chars):                     o l d r v x k m p t r y c
    q1 = ["o", "l", "d", "r", "v", "x", "k", "m", "f", "t", "r", "y", "-"]
    q2 = ["o", "l", "d", "r", "v", "x", "k", "m", "f", "t", "r", "y", "c"]
    q3 = ["o", "l", "d", "r", "v", "x", "k", "m", "p", "t", "r", "y", "c"]
    q4 = ["o", "l", "d", "r", "v", "x", "k", "m", "p", "t", "r", "y", "c"]

    slot_alignment = []
    exact_slot_matches = 0
    allograph_slot_matches = 0
    total_slot_comparisons = 0
    quads = [q1, q2, q3, q4]
    for slot_idx in range(13):
        vals = [q[slot_idx] for q in quads]
        present_vals = [v for v in vals if v != "-"]
        # Pairwise comparisons among present quadrants in this slot
        for i in range(len(present_vals)):
            for j in range(i + 1, len(present_vals)):
                total_slot_comparisons += 1
                v1, v2 = present_vals[i], present_vals[j]
                if v1 == v2:
                    exact_slot_matches += 1
                    allograph_slot_matches += 1
                elif {v1, v2} == {"f", "p"}:
                    allograph_slot_matches += 1
        slot_alignment.append({
            "slot": slot_idx + 1,
            "Q1": q1[slot_idx],
            "Q2": q2[slot_idx],
            "Q3": q3[slot_idx],
            "Q4": q4[slot_idx],
            "note": "f <-> p gallows allograph swap!" if slot_idx == 8 else ("omitted at Q1 seam" if slot_idx == 12 else "100% identical"),
        })

    # Classify all @C ring loci across the manuscript into 3 structural types
    type1_char_cipher_rings = []
    type2_nominal_catalog_rings = []
    type3_continuous_prose_rings = []

    for r in all_ring_loci:
        if r["single_char_rate_pct"] >= 50.0:
            rtype = "Type I: Repeating Single-Glyph Key Ring"
            type1_char_cipher_rings.append(r["loc_id"])
        elif r["n_tokens"] >= 8 and (r["mean_token_len"] >= 4.7 or any(w in r["tokens"] for w in ("daiin", "chedy", "shedy", "qokedy", "qokeedy", "chol", "chor", "oteey", "okeey"))):
            rtype = "Type III: Continuous Circular Prose Ring"
            type3_continuous_prose_rings.append(r["loc_id"])
        else:
            rtype = "Type II: Nominal Catalog / Sector Ring"
            type2_nominal_catalog_rings.append(r["loc_id"])
        r["ring_class"] = rtype

    # Classify all @R radial spoke loci
    radial_single_label = [r["loc_id"] for r in all_radial_loci if r["n_tokens"] <= 2]
    radial_multi_token = [r["loc_id"] for r in all_radial_loci if r["n_tokens"] >= 3]

    # Summarize f68r1, f68r2, f68r3 (3-panel foldout sheet)
    f68r_summary = {}
    for fol in ("f68r1", "f68r2", "f68r3"):
        loci = f68r_loci[fol]
        prose_toks = [t for l in loci if l["loc_tag"].startswith("P") for t in l["tokens"]]
        ring_toks = [t for l in loci if l["loc_tag"].startswith("C") or l["loc_tag"].startswith("R") for t in l["tokens"]]
        label_toks = [t for l in loci if l["loc_tag"].startswith("L") for t in l["tokens"]]
        f68r_summary[fol] = {
            "total_loci": len(loci),
            "prose_tokens": len(prose_toks),
            "ring_or_radial_tokens": len(ring_toks),
            "star_and_moon_label_tokens": len(label_toks),
            "sample_labels": label_toks[:15],
        }

    # Check vocabulary overlap between f57v and its facing/conjoined Quire H Index folios (f58r, f58v, f66r)
    f57v_words = {t for t in folio_tokens["f57v"] if len(t) >= 2}
    f57v_stems = {canonical_stem(t) for t in f57v_words}
    f58_words = {t for t in (folio_tokens["f58r"] + folio_tokens["f58v"]) if len(t) >= 2}
    f58_stems = {canonical_stem(t) for t in f58_words}
    shared_f57v_f58_words = sorted(f57v_words & f58_words)
    shared_f57v_f58_stems = sorted(f57v_stems & f58_stems)

    out = {
        "summary": {
            "total_circular_ring_loci_at_C": len(all_ring_loci),
            "total_radial_spoke_loci_at_R": len(all_radial_loci),
            "type1_single_glyph_key_rings_count": len(type1_char_cipher_rings),
            "type1_single_glyph_key_rings_list": type1_char_cipher_rings,
            "type2_nominal_catalog_rings_count": len(type2_nominal_catalog_rings),
            "type3_continuous_prose_rings_count": len(type3_continuous_prose_rings),
            "radial_single_label_spokes_count": len(radial_single_label),
            "radial_multi_token_spokes_count": len(radial_multi_token),
            "f57v_ring2_f57v3_exact_slot_identity_pct": round(100.0 * exact_slot_matches / total_slot_comparisons, 2),
            "f57v_ring2_f57v3_allographic_fp_slot_identity_pct": round(100.0 * allograph_slot_matches / total_slot_comparisons, 2),
            "f57v_f58_shared_multi_char_words": shared_f57v_f58_words,
            "f57v_f58_shared_stems_count": len(shared_f57v_f58_stems),
            "f57v_f58_stem_overlap_pct": round(100.0 * len(shared_f57v_f58_stems) / len(f57v_stems), 2) if f57v_stems else 0.0,
        },
        "f57v_ring3_13glyph_4quadrant_table": slot_alignment,
        "f57v_ring_analysis": f57v_ring_analysis,
        "f68r_three_panel_foldout_summary": f68r_summary,
        "ring_taxonomy": {
            "Type_I_Single_Glyph_Key_Rings": type1_char_cipher_rings,
            "Type_II_Nominal_Catalog_Rings": type2_nominal_catalog_rings,
            "Type_III_Continuous_Prose_Rings": type3_continuous_prose_rings,
        },
    }

    out_path = Path("data/attack178_f57v_four_ring_key_and_astro_wheel_taxonomy.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out["summary"], indent=2))
    print("\nf57v.3 13-Glyph 4-Quadrant Alignment Table:")
    for row in slot_alignment:
        print(f"  Slot {row['slot']:2d}: Q1={row['Q1']} | Q2={row['Q2']} | Q3={row['Q3']} | Q4={row['Q4']}  ({row['note']})")
    print("\nf68r1-3 Summary:")
    print(json.dumps(f68r_summary, indent=2))


if __name__ == "__main__":
    main()
