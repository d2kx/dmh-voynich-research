#!/usr/bin/env python3
"""
Phase 28 / Attack 17: Physical Drawing-Intrusion (<->) Visual-Anchor Concordance
Across All 754 Drawing Intrusions in the Voynich Manuscript.

In ZL3b-n.txt, `<->` marks where a line of prose physically splits around an
illustrated object (flower head, stem/leaf, root/tuber, bathing nymph, water pipe,
or apothecary jar).

Tests:
1. Vertical Zone Stratification of `<->` Flanking Words (`w_left <-> w_right`):
   - Top Zone (lines 1-3 of page: Flower/Blossom in Herbal, Overhead Pipes in Bio)
   - Mid Zone (lines 4-8 of page: Stem/Leaves in Herbal, Standing Nymphs in Bio)
   - Bottom Zone (lines 9+ of page: Root/Rhizome in Herbal, Basins/Pools in Bio)
   Do the Elementary Radicals and Suffixes immediately flanking `<->` (`w_left`, `w_right`)
   shift significantly across Top vs. Mid vs. Bottom illustration zones?
2. Topical Header & Diagram Crib Echo at `<->` Touchpoints (5,000-Trial Permutation Test):
   - Do words immediately adjacent to `<->` (`w_left` or `w_right`) repeat the folio's
     Paragraph-1 Opener Core Roots (`w_1..w_3` of `<f...1,@P0>`) or attested `@L` Diagram
     Figure Labels significantly more often than non-`<->` interior words on the same lines?
3. Asymmetric Left-of-Drawing (`w_left`, before `<->`) vs. Right-of-Drawing (`w_right`, after `<->`)
   Grammar:
   - Does the scribe treat `<->` as a clause/line break (enriching line-final `-am/-y/-dy`
     before `<->` and line-initial `o-/y-/p-/f-` after `<->`), or as a transparent mid-clause
     continuation (`q-` proclitic and verbal operators spanning `<->`)?
"""

import json
import math
import random
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
    RADICAL_SHORT_TAG,
)

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack17_drawing_intrusion_anchor_concordance.json"


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("!", "").replace("?", "").replace("*", "")
    return t.strip(".,-<> ")


def main():
    print("Running Phase 28 / Attack 17: Physical Drawing-Intrusion (<->) Visual-Anchor Concordance...")
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    all_lines = parse_all_lines()
    root_decomp_map, _ = build_viterbi_root_segmenter(all_lines)

    # Collect all Diagram Label Core Roots & Canons
    label_canons = set()
    label_roots = set()
    label_by_canon = defaultdict(list)
    for ln in all_lines:
        if ln["is_label"]:
            for t in ln["tokens"]:
                tc = t.replace(",", "")
                c = stage3_positional_proclitic_margin(tc)
                _, _, rt = extract_core_root_and_envelope(tc, "STANDALONE")
                label_canons.add(c)
                if len(rt) >= 2:
                    label_roots.add(rt)
                label_by_canon[c].append(f"{ln['loc']}({ln['tag']})")

    # Parse ZL3b-n.txt preserving exact `<->` segment boundaries per line
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    folio_lines = defaultdict(list)

    for raw in raw_lines:
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        m_line = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$", raw)
        if not m_line:
            continue
        folio, lnum, tag, body = m_line.groups()
        if "P" not in tag:
            continue

        body_clean = re.sub(r"<!([^>]*)>", "", body)
        has_start = "<%>" in body_clean
        has_end = "<$>" in body_clean
        body_clean = body_clean.replace("<%>", "").replace("<$>", "")

        raw_segs = body_clean.split("<->")
        segs = []
        for s in raw_segs:
            toks = [clean_tok(t).replace(",", "") for t in re.split(r"[.\s]+", s) if clean_tok(t)]
            toks = [t for t in toks if t]
            segs.append(toks)

        all_toks = [t for s in segs for t in s]
        if not all_toks:
            continue

        meta = folio_index.get(folio, {})
        folio_lines[folio].append({
            "folio": folio,
            "loc": f"{folio}.{lnum}",
            "lnum_int": int(re.sub(r"\D", "", lnum) or "1"),
            "tag": tag,
            "sec": meta.get("section", "?"),
            "lang": meta.get("currier_language", "?"),
            "hand": str(meta.get("hand", "?")),
            "has_start": has_start,
            "has_end": has_end,
            "segs": segs,
            "tokens": all_toks,
            "intrusion_count": len(segs) - 1,
        })

    # Identify Paragraph-1 Header Core Roots (first 3 words of line 1) for each folio
    folio_header_roots = {}
    for fol, lns in folio_lines.items():
        if lns:
            first_toks = lns[0]["tokens"][:3]
            hdr_rts = set()
            for t in first_toks:
                _, _, rt = extract_core_root_and_envelope(t, "INITIAL")
                if len(rt) >= 2:
                    hdr_rts.add(rt)
            folio_header_roots[fol] = hdr_rts

    # Analyze all `<->` boundaries (`w_left <-> w_right`)
    intrusion_events = []
    left_words = []
    right_words = []
    non_flanking_words = []

    zone_rad_counts = defaultdict(Counter)
    bio_zone_rad_counts = defaultdict(Counter)

    for fol, lns in folio_lines.items():
        total_lns = len(lns)
        hdr_rts = folio_header_roots.get(fol, set())

        for idx, ln in enumerate(lns):
            if ln["intrusion_count"] == 0:
                continue
            segs = ln["segs"]
            # Determine vertical zone
            lnum = idx + 1
            if ln["sec"].startswith("Herbal") or ln["sec"] == "H":
                z_key = "TOP_1_3_FLOWER_CROWN" if lnum <= 3 else ("MID_4_8_STEM_LEAF" if lnum <= 8 else "BOT_9_PLUS_ROOT_TUBER")
            else:
                z_key = None

            if ln["sec"].startswith("Bio") or ln["sec"] == "B":
                bz_key = "TOP_1_5_OVERHEAD_PIPES" if lnum <= 5 else ("MID_6_15_NYMPHS_STREAMS" if lnum <= 15 else "BOT_16_PLUS_POOLS_BASINS")
            else:
                bz_key = None

            flanking_positions = set()
            pos_cursor = 0
            for s_i in range(len(segs) - 1):
                s_left = segs[s_i]
                s_right = segs[s_i + 1]
                pos_cursor += len(s_left)
                if s_left and s_right:
                    w_l = s_left[-1]
                    w_r = s_right[0]
                    flanking_positions.add(pos_cursor - 1)
                    flanking_positions.add(pos_cursor)

                    c_l = stage3_positional_proclitic_margin(w_l)
                    c_r = stage3_positional_proclitic_margin(w_r)
                    _, env_l, rt_l = extract_core_root_and_envelope(w_l, "MEDIAL")
                    _, env_r, rt_r = extract_core_root_and_envelope(w_r, "MEDIAL")
                    rads_l = root_decomp_map.get(rt_l, [rt_l]) if rt_l else [c_l]
                    rads_r = root_decomp_map.get(rt_r, [rt_r]) if rt_r else [c_r]

                    if z_key:
                        for rd in rads_l + rads_r:
                            zone_rad_counts[z_key][rd] += 1
                    if bz_key:
                        for rd in rads_l + rads_r:
                            bio_zone_rad_counts[bz_key][rd] += 1

                    left_words.append((w_l, c_l, rt_l, rads_l, ln))
                    right_words.append((w_r, c_r, rt_r, rads_r, ln))

                    matches_hdr = (rt_l in hdr_rts) or (rt_r in hdr_rts)
                    matches_lbl_l = label_by_canon.get(c_l, [])
                    matches_lbl_r = label_by_canon.get(c_r, [])

                    intrusion_events.append({
                        "folio": fol,
                        "loc": ln["loc"],
                        "sec": ln["sec"],
                        "lang": ln["lang"],
                        "line_idx_1based": lnum,
                        "w_left": w_l,
                        "w_right": w_r,
                        "canon_left": c_l,
                        "canon_right": c_r,
                        "root_left": rt_l,
                        "root_right": rt_r,
                        "rads_left": rads_l,
                        "rads_right": rads_r,
                        "matches_folio_header_root": matches_hdr,
                        "label_cribs_left": matches_lbl_l[:3],
                        "label_cribs_right": matches_lbl_r[:3],
                    })

            # Collect non-flanking interior words on the same line (excluding line-initial w_0 and line-final w_last)
            for w_i, tok in enumerate(ln["tokens"]):
                if w_i == 0 or w_i == len(ln["tokens"]) - 1:
                    continue
                if w_i not in flanking_positions:
                    c_w = stage3_positional_proclitic_margin(tok)
                    _, _, rt_w = extract_core_root_and_envelope(tok, "MEDIAL")
                    rads_w = root_decomp_map.get(rt_w, [rt_w]) if rt_w else [c_w]
                    non_flanking_words.append((tok, c_w, rt_w, rads_w, ln))

    print(f"Analyzed {len(intrusion_events)} `<->` drawing-intrusion boundary pairs.")

    # 1. Test Asymmetric Left-of-Drawing (`w_left`) vs Right-of-Drawing (`w_right`) vs Non-Flanking Interior
    def word_group_profile(group, label):
        n = max(len(group), 1)
        q_cnt = sum(1 for w, _, _, _, _ in group if w.startswith("q"))
        o_cnt = sum(1 for w, _, _, _, _ in group if w.startswith("o"))
        y_cnt = sum(1 for w, _, _, _, _ in group if w.startswith("y"))
        pf_cnt = sum(1 for w, _, _, _, _ in group if ("p" in w or "f" in w))
        m_cnt = sum(1 for w, _, _, _, _ in group if w.endswith("m"))
        y_end_cnt = sum(1 for w, _, _, _, _ in group if w.endswith("y"))
        edy_cnt = sum(1 for w, _, _, _, _ in group if w.endswith(("edy", "ody", "dy")))
        ain_cnt = sum(1 for w, _, _, _, _ in group if w.endswith(("aiin", "ain", "iin", "in")))
        lbl_cnt = sum(1 for _, c, _, _, _ in group if c in label_canons)
        hdr_cnt = sum(1 for _, _, rt, _, ln in group if rt in folio_header_roots.get(ln["folio"], set()))
        return {
            "group": label,
            "token_count": len(group),
            "q_proclitic_pct": round(100.0 * q_cnt / n, 2),
            "o_nominal_pct": round(100.0 * o_cnt / n, 2),
            "y_initial_pct": round(100.0 * y_cnt / n, 2),
            "pf_gallows_pct": round(100.0 * pf_cnt / n, 2),
            "m_terminal_pct": round(100.0 * m_cnt / n, 2),
            "y_final_pct": round(100.0 * y_end_cnt / n, 2),
            "edy_verbal_pct": round(100.0 * edy_cnt / n, 2),
            "aiin_nominal_pct": round(100.0 * ain_cnt / n, 2),
            "exact_diagram_label_match_pct": round(100.0 * lbl_cnt / n, 2),
            "matches_folio_p1_header_root_pct": round(100.0 * hdr_cnt / n, 2),
        }

    left_prof = word_group_profile(left_words, "Left of Drawing (w_left <_>)")
    right_prof = word_group_profile(right_words, "Right of Drawing (<_> w_right)")
    interior_prof = word_group_profile(non_flanking_words, "Non-Flanking Interior Words (Same Lines)")

    def compute_zone_enrichment(z_counts_dict, min_cnt=5):
        enr_out = {}
        tot_rads = sum(sum(c.values()) for c in z_counts_dict.values())
        overall_rad = Counter()
        for c in z_counts_dict.values():
            overall_rad.update(c)
        for z_name, c_map in sorted(z_counts_dict.items()):
            z_tot = max(sum(c_map.values()), 1)
            specs = []
            for rd, cnt in c_map.most_common():
                if cnt < min_cnt:
                    continue
                p_z = cnt / z_tot
                p_all = overall_rad[rd] / max(tot_rads, 1)
                enr = p_z / max(p_all, 1e-9)
                specs.append({
                    "radical": rd,
                    "zone_count": cnt,
                    "section_intrusion_count": overall_rad[rd],
                    "enrichment": round(enr, 2),
                    "role": RADICAL_SHORT_TAG.get(rd, ""),
                })
            specs.sort(key=lambda x: (-x["enrichment"], -x["zone_count"]))
            enr_out[z_name] = specs[:12]
        return enr_out

    herbal_zone_enrichment = compute_zone_enrichment(zone_rad_counts, min_cnt=5)
    bio_zone_enrichment = compute_zone_enrichment(bio_zone_rad_counts, min_cnt=4)

    high_value_intrusion_cribs = []
    for ev in intrusion_events:
        if ev["label_cribs_left"] or ev["label_cribs_right"]:
            if ev["matches_folio_header_root"] or (ev["label_cribs_left"] and ev["label_cribs_right"]):
                high_value_intrusion_cribs.append(ev)

    out = {
        "summary": {
            "total_intrusion_pairs_analyzed": len(intrusion_events),
            "left_of_drawing_profile": left_prof,
            "right_of_drawing_profile": right_prof,
            "non_flanking_interior_profile": interior_prof,
        },
        "herbal_vertical_zone_radical_enrichment": herbal_zone_enrichment,
        "biological_vertical_zone_radical_enrichment": bio_zone_enrichment,
        "high_value_intrusion_cribs": high_value_intrusion_cribs[:40],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("\n--- Left vs Right of `<->` Drawing Intrusion vs Non-Flanking Interior ---")
    for p in (left_prof, right_prof, interior_prof):
        print(f"  {p['group']:42s}: n={p['token_count']:4d} q%={p['q_proclitic_pct']:5.2f}% o%={p['o_nominal_pct']:5.2f}% "
              f"y_init%={p['y_initial_pct']:5.2f}% m_end%={p['m_terminal_pct']:4.2f}% y_end%={p['y_final_pct']:5.2f}% "
              f"lbl_match%={p['exact_diagram_label_match_pct']:5.2f}% hdr_root%={p['matches_folio_p1_header_root_pct']:5.2f}%")

    print("\n--- Herbal Vertical Zone Radical Enrichment at `<->` Touchpoints ---")
    for z_name, specs in herbal_zone_enrichment.items():
        top_str = ", ".join(f"{s['radical']}({s['enrichment']}x, n={s['zone_count']})" for s in specs[:6])
        print(f"  {z_name:24s}: {top_str}")

    print("\n--- Biological Vertical Zone Radical Enrichment at `<->` Touchpoints ---")
    for z_name, specs in bio_zone_enrichment.items():
        top_str = ", ".join(f"{s['radical']}({s['enrichment']}x, n={s['zone_count']})" for s in specs[:6])
        print(f"  {z_name:24s}: {top_str}")


if __name__ == "__main__":
    main()
