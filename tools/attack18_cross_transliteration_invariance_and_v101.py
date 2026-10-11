#!/usr/bin/env python3
"""
Phase 29 / Attack 18: Cross-Transliteration Paleographic Invariance (ZL3b-n, IT2a-n,
RF1b-er) & Glen Claston v101 (GC2a-n) Sub-Glyph Allography Decoder.

Tests:
1. Inter-Transcriber Agreement & Stage-3 FST Variance Absorption across ZL3b-n, IT2a-n,
   and RF1b-er:
   - What percentage of raw EVA spelling disagreements between Zandbergen-Landini (ZL)
     and Takahashi (IT) are automatically resolved by our Stage-3 Positional FST and
     Core Root extractor?
2. Inter-Transcriber Word-Space Split Verification:
   - When IT2a-n splits a token (`w1 . w2`) that ZL3b-n writes as a single unbroken word
     (`w1w2`, without even a comma `,`), what percentage of those splits fall on an
     exact `[Prefix | R_1 + R_2 | -Suffix]` boundary predicted by our Attack 12 Viterbi
     radical segmenter?
3. Glen Claston v101 (`GC2a-n.txt`) Sub-Glyph Disambiguation:
   - Aligns EVA tokens (`ZL3b-n.txt`) 1-to-1 with Glen Claston v101 (`GC2a-n.txt`).
   - Maps how single EVA letters/suffixes split into multiple v101 paleographic glyphs,
     testing whether v101 sub-glyphs encode:
     (a) Positional allography (Initial vs. Medial vs. Final),
     (b) Scribe Hand / Currier Language (A vs. B), or
     (c) Distinct lexical/radical contrasts blurred by EVA!
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from attack7_positional_envelope_fst import (
    stage3_positional_proclitic_margin,
    extract_core_root_and_envelope,
)
from attack16_radical_clause_translation_edition import (
    build_viterbi_root_segmenter,
    parse_all_lines,
)

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
IT_PATH = ROOT / "data" / "IT2a-n.txt"
RF_PATH = ROOT / "data" / "RF1b-er.txt"
GC_PATH = ROOT / "data" / "GC2a-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack18_cross_transliteration_invariance_and_v101.json"


def clean_ivar_line(body: str, keep_case: bool = False) -> list[str]:
    text = re.sub(r"<!([^>]*)>", "", body)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\{[^}]*\}", "", text)
    text = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", text)
    text = re.sub(r"@\d+;", "", text)
    toks = []
    for raw_t in re.split(r"[.\s]+", text):
        t = raw_t.replace("[", "").replace("]", "").replace("!", "").replace("?", "").replace("*", "").strip(".,-<> ")
        if not keep_case:
            t = t.lower()
        if t:
            toks.append(t)
    return toks


def parse_ivtff_lines(path: Path, keep_case: bool = False) -> dict[str, list[str]]:
    out = {}
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        m = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$", raw)
        if not m:
            continue
        folio, lnum, tag, body = m.groups()
        if "P" not in tag and "L" not in tag:
            continue
        loc = f"{folio}.{lnum}"
        toks = clean_ivar_line(body, keep_case=keep_case)
        if toks:
            out[loc] = toks
    return out


def main():
    print("Running Phase 29 / Attack 18: Cross-Transliteration Paleographic Invariance & v101 Analysis...")
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    all_lines = parse_all_lines()
    root_decomp_map, segment_root_fn = build_viterbi_root_segmenter(all_lines)

    zl_lines = parse_ivtff_lines(ZL_PATH, keep_case=False)
    it_lines = parse_ivtff_lines(IT_PATH, keep_case=False)
    rf_lines = parse_ivtff_lines(RF_PATH, keep_case=False)
    gc_lines = parse_ivtff_lines(GC_PATH, keep_case=True)

    print(f"Loaded lines: ZL={len(zl_lines)}, IT={len(it_lines)}, RF={len(rf_lines)}, GC(v101)={len(gc_lines)}")

    # 1. Align ZL vs IT on exact same-length lines to measure token-by-token agreement & FST absorption
    shared_zl_it_locs = sorted(set(zl_lines.keys()) & set(it_lines.keys()))
    aligned_pairs = 0
    exact_raw_matches = 0
    disagreements = 0
    resolved_by_stage3 = 0
    resolved_by_core_root = 0
    disagreement_examples = Counter()
    resolved_examples = Counter()

    # Also check 1-to-2 word-boundary splits where ZL has 1 unbroken word (no comma) and IT has 2 words!
    it_split_events = []
    it_split_hits_morpheme_or_radical = 0

    for loc in shared_zl_it_locs:
        z_toks = [t.replace(",", "") for t in zl_lines[loc] if t.replace(",", "")]
        z_raw_toks = zl_lines[loc]
        i_toks = [t.replace(",", "") for t in it_lines[loc] if t.replace(",", "")]

        if len(z_toks) == len(i_toks):
            for z_w, i_w in zip(z_toks, i_toks):
                if not z_w.isalpha() or not i_w.isalpha():
                    continue
                aligned_pairs += 1
                if z_w == i_w:
                    exact_raw_matches += 1
                else:
                    disagreements += 1
                    c_z = stage3_positional_proclitic_margin(z_w)
                    c_i = stage3_positional_proclitic_margin(i_w)
                    _, _, rt_z = extract_core_root_and_envelope(z_w, "MEDIAL")
                    _, _, rt_i = extract_core_root_and_envelope(i_w, "MEDIAL")
                    if c_z == c_i:
                        resolved_by_stage3 += 1
                        resolved_examples[f"{z_w} <-> {i_w} => {c_z}"] += 1
                    if rt_z == rt_i:
                        resolved_by_core_root += 1
                    else:
                        disagreement_examples[f"{z_w} (rt={rt_z}) vs {i_w} (rt={rt_i})"] += 1

        # Detect exact 1-word (ZL, no comma) <-> 2-word (IT) splits
        if len(i_toks) == len(z_raw_toks) + 1:
            # Find where i_toks[k] + i_toks[k+1] == z_raw_toks[k]
            for k in range(len(z_raw_toks)):
                zw = z_raw_toks[k]
                if "," in zw or not zw.isalpha():
                    continue
                if k + 1 < len(i_toks) and (i_toks[k] + i_toks[k + 1]) == zw:
                    p1, p2 = i_toks[k], i_toks[k + 1]
                    split_idx = len(p1)
                    # Determine predicted boundaries of zw using Attack 12 / Attack 7
                    _, env_sig, rt = extract_core_root_and_envelope(zw, "MEDIAL")
                    rads = root_decomp_map.get(rt, segment_root_fn(rt)) if rt else [zw]
                    # Map prefix, radical boundaries, and suffix onto character indices of zw
                    # Approximate by finding rt inside stage1/2 or matching prefix/suffix length
                    pref_str = [x[2:] for x in env_sig.split("|") if x.startswith("P:")][0] if "P:" in env_sig else "0"
                    suff_str = [x[2:] for x in env_sig.split("|") if x.startswith("S:")][0] if "S:" in env_sig else "0"

                    # Check if p1 is a known prefix/proclitic, or p2 is a known suffix, or p1 & p2 are valid radicals/words
                    boundary_type = "OTHER"
                    if p1 in ("q", "qo", "o", "d", "s", "y", "l", "ch", "sh", "cth", "ckh", "ol", "or", "ar", "al", "dar", "dal", "ok", "ot", "qok", "qot"):
                        boundary_type = "PREFIX_OR_RADICAL1_SPLIT"
                    elif p2 in ("aiin", "ain", "iin", "in", "edy", "ody", "dy", "ey", "eey", "ol", "al", "or", "ar", "am", "y", "s", "d", "r", "l", "chy", "shy", "chey", "shey", "chedy", "shedy", "daiin", "dain", "dar", "dal"):
                        boundary_type = "RADICAL2_OR_SUFFIX_SPLIT"
                    elif p1 in root_decomp_map or p2 in root_decomp_map:
                        boundary_type = "COMPOUND_ROOT_SPLIT"

                    if boundary_type != "OTHER":
                        it_split_hits_morpheme_or_radical += 1

                    it_split_events.append({
                        "loc": loc,
                        "zl_unbroken": zw,
                        "it_split": f"{p1} . {p2}",
                        "boundary_type": boundary_type,
                        "core_root": rt,
                        "radicals": rads,
                    })
                    break

    # 2. Align ZL (EVA) vs GC (Glen Claston v101) to decode v101 Sub-Glyph Allography!
    shared_zl_gc_locs = sorted(set(zl_lines.keys()) & set(gc_lines.keys()))
    eva_to_v101_pairs = []
    for loc in shared_zl_gc_locs:
        folio = loc.split(".")[0]
        meta = folio_index.get(folio, {})
        lang = meta.get("currier_language", "?")
        hand = str(meta.get("hand", "?"))
        z_toks = [t.replace(",", "") for t in zl_lines[loc] if t.replace(",", "")]
        g_toks = [t.replace(",", "") for t in gc_lines[loc] if t.replace(",", "")]
        if len(z_toks) == len(g_toks):
            for idx, (zw, gw) in enumerate(zip(z_toks, g_toks)):
                if zw.isalpha():
                    eva_to_v101_pairs.append((zw, gw, idx == 0, idx == len(z_toks) - 1, lang, hand, loc))

    print(f"Aligned {len(eva_to_v101_pairs)} exact 1-to-1 (EVA, v101) token pairs.")

    # Analyze key EVA morphemes/glyphs and their v101 realizations:
    v101_for_eva_token = defaultdict(Counter)
    eva_for_v101_token = defaultdict(Counter)
    v101_onset_for_eva_y_init = Counter()
    v101_coda_for_eva_y_final = Counter()
    v101_coda_for_eva_aiin = defaultdict(Counter)
    v101_coda_for_eva_edy = defaultdict(Counter)
    v101_d_by_internal_context = defaultdict(Counter)
    v101_d_by_section = defaultdict(Counter)
    v101_sh_by_following_vowel = defaultdict(Counter)
    v101_sh_by_section = defaultdict(Counter)
    v101_ee_by_context = defaultdict(Counter)

    for zw, gw, is_init, is_fin, lang, hand, loc in eva_to_v101_pairs:
        folio = loc.split(".")[0]
        sec = folio_index.get(folio, {}).get("section", "?")
        lang_true = folio_index.get(folio, {}).get("language", lang)
        v101_for_eva_token[zw][gw] += 1
        eva_for_v101_token[gw][zw] += 1

        if zw.startswith("y") and len(zw) > 1 and gw:
            v101_onset_for_eva_y_init[gw[0]] += 1
        if zw.endswith("y") and len(zw) > 1 and gw:
            v101_coda_for_eva_y_final[gw[-1]] += 1
        if zw.endswith("aiin") and len(gw) >= 2:
            v101_coda_for_eva_aiin[lang_true][gw[-2:]] += 1
        if zw.endswith("edy") and len(gw) >= 3:
            v101_coda_for_eva_edy[f"Hand_{hand}_{sec}"][gw[-3:]] += 1

        # Check EVA `d` -> v101 `8` vs `7` across internal phonetic context!
        if "d" in zw and ("8" in gw or "7" in gw):
            d_glyph = "7" if "7" in gw else "8"
            v101_d_by_section[sec][d_glyph] += 1
            if zw.startswith("d"):
                v101_d_by_internal_context["1_word_initial_d-"][d_glyph] += 1
            elif "ed" in zw:
                v101_d_by_internal_context["2_post_e_(-ed-)"][d_glyph] += 1
            elif "od" in zw:
                v101_d_by_internal_context["3_post_o_(-od-)"][d_glyph] += 1
            elif "chd" in zw or "shd" in zw:
                v101_d_by_internal_context["4_post_ch/sh_(-chd-)"][d_glyph] += 1
            elif "ld" in zw or "rd" in zw:
                v101_d_by_internal_context["5_post_liquid_(-ld/-rd-)"][d_glyph] += 1
            elif "al" in zw or "ai" in zw:
                v101_d_by_internal_context["6_post_a_(-ad-)"][d_glyph] += 1

        # Check EVA `sh` -> v101 `2`, `3`, `5`, `6`, `7` across following vowel (`she`, `sho`, `sha`, `shy`)
        if zw.startswith("sh") and gw and gw[0] in ("2", "3", "5", "6"):
            sh_glyph = gw[0]
            v101_sh_by_section[sec][sh_glyph] += 1
            if zw.startswith("she"):
                v101_sh_by_following_vowel["she-"][sh_glyph] += 1
            elif zw.startswith("sho"):
                v101_sh_by_following_vowel["sho-"][sh_glyph] += 1
            elif zw.startswith("sha"):
                v101_sh_by_following_vowel["sha-"][sh_glyph] += 1
            elif zw.startswith("shy"):
                v101_sh_by_following_vowel["shy-"][sh_glyph] += 1

        # Check EVA `ee` -> v101 `C` vs `cc`
        if "ee" in zw and "eee" not in zw:
            if "C" in gw:
                v101_ee_by_context[sec]["C_ligature"] += 1
            elif "cc" in gw:
                v101_ee_by_context[sec]["cc_double"] += 1

    # Find Top EVA words that split into 2+ distinct high-frequency v101 words!
    eva_homograph_splits = []
    for zw, g_cnts in v101_for_eva_token.items():
        tot = sum(g_cnts.values())
        if tot < 30:
            continue
        top_g = g_cnts.most_common(4)
        if len(top_g) >= 2 and top_g[1][1] >= 10:
            eva_homograph_splits.append({
                "eva_word": zw,
                "total_aligned": tot,
                "v101_variants": [{"v101": g, "count": c, "pct": round(100.0 * c / tot, 1)} for g, c in top_g],
            })
    eva_homograph_splits.sort(key=lambda x: -x["v101_variants"][1]["count"])

    # Conversely, find Top v101 words that EVA splits into 2+ distinct words!
    v101_merged_in_gc = []
    for gw, z_cnts in eva_for_v101_token.items():
        tot = sum(z_cnts.values())
        if tot < 30:
            continue
        top_z = z_cnts.most_common(4)
        if len(top_z) >= 2 and top_z[1][1] >= 10:
            v101_merged_in_gc.append({
                "v101_word": gw,
                "total_aligned": tot,
                "eva_variants": [{"eva": z, "count": c, "pct": round(100.0 * c / tot, 1)} for z, c in top_z],
            })
    v101_merged_in_gc.sort(key=lambda x: -x["eva_variants"][1]["count"])

    out = {
        "summary": {
            "zl_it_aligned_tokens": aligned_pairs,
            "zl_it_exact_raw_agreement_pct": round(100.0 * exact_raw_matches / max(aligned_pairs, 1), 2),
            "zl_it_disagreements": disagreements,
            "disagreements_resolved_by_stage3_fst": resolved_by_stage3,
            "disagreements_resolved_by_stage3_pct": round(100.0 * resolved_by_stage3 / max(disagreements, 1), 2),
            "disagreements_resolved_by_core_root": resolved_by_core_root,
            "disagreements_resolved_by_core_root_pct": round(100.0 * resolved_by_core_root / max(disagreements, 1), 2),
            "it_word_splits_of_zl_unbroken_words": len(it_split_events),
            "it_word_splits_hitting_morpheme_or_radical_boundary": it_split_hits_morpheme_or_radical,
            "it_word_splits_morpheme_or_radical_pct": round(100.0 * it_split_hits_morpheme_or_radical / max(len(it_split_events), 1), 2),
            "zl_gc_v101_aligned_tokens": len(eva_to_v101_pairs),
        },
        "top_zl_it_disagreements_resolved_by_fst": [
            {"pair": k, "count": v} for k, v in resolved_examples.most_common(25)
        ],
        "it_word_split_examples": it_split_events[:35],
        "v101_subglyph_analysis": {
            "eva_y_initial_to_v101_onset": v101_onset_for_eva_y_init.most_common(8),
            "eva_y_final_to_v101_coda": v101_coda_for_eva_y_final.most_common(8),
            "eva_aiin_to_v101_by_currier_lang": {k: v.most_common(6) for k, v in v101_coda_for_eva_aiin.items()},
            "eva_edy_to_v101_by_hand_sec": {k: v.most_common(5) for k, v in sorted(v101_coda_for_eva_edy.items())},
            "eva_d_8_vs_7_by_internal_context": {k: dict(v) for k, v in sorted(v101_d_by_internal_context.items())},
            "eva_d_8_vs_7_by_section": {k: dict(v) for k, v in sorted(v101_d_by_section.items())},
            "eva_sh_2356_by_following_vowel": {k: dict(v) for k, v in sorted(v101_sh_by_following_vowel.items())},
            "eva_ee_C_vs_cc_by_section": {k: dict(v) for k, v in sorted(v101_ee_by_context.items())},
            "eva_homograph_splits_in_v101": eva_homograph_splits[:25],
            "v101_words_split_by_eva": v101_merged_in_gc[:25],
        },
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("\n--- Summary of Cross-Transliteration Invariance (ZL vs IT vs GC v101) ---")
    for k, v in out["summary"].items():
        print(f"  {k}: {v}")

    print("\n--- v101 `8` vs `7` (for EVA `d`) by Internal Phonetic Context ---")
    for k, v in sorted(v101_d_by_internal_context.items()):
        tot = sum(v.values())
        p7 = 100.0 * v.get("7", 0) / max(tot, 1)
        print(f"  {k:28s}: 8={v.get('8',0):4d}  7={v.get('7',0):4d}  (7% = {p7:5.1f}%)")

    print("\n--- v101 `2/3/5/6` (for EVA `sh`) by Following Vowel ---")
    for k, v in sorted(v101_sh_by_following_vowel.items()):
        print(f"  {k:10s}: {dict(v)}")

    print("\n--- v101 `C` (Ligature) vs `cc` (Double Stroke) for EVA `ee` by Section ---")
    for k, v in sorted(v101_ee_by_context.items()):
        tot = sum(v.values())
        pc = 100.0 * v.get("C_ligature", 0) / max(tot, 1)
        print(f"  {k:28s}: C={v.get('C_ligature',0):4d}  cc={v.get('cc_double',0):4d}  (C_lig% = {pc:5.1f}%)")


if __name__ == "__main__":
    main()
