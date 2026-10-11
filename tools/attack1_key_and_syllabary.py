"""
Phase 12 (Attack 1): Reconstructing & Testing the f49v (1..5 = f-o-r-y-e) Generative Tuple,
the f57v 4-Ring Volvelle Alignment (Rings 1, 2, 3, and 4), and the f66r 17-Symbol Key.

Outputs:
- data/attack1_key_and_syllabary.json
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack1_key_and_syllabary.json"


def clean_word(raw: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", raw)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "")
    w = w.replace("'", "").replace(",", "").strip()
    return w


def canonicalize(w: str) -> str:
    if not w:
        return ""
    s = w
    if len(s) > 2 and s[0] in ("q", "y"):
        s = s[1:]
    s = s.replace("cth", "ckh").replace("cph", "ckh").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    if len(s) > 2 and s.endswith("m"):
        s = s[:-1] + "r"
    return s


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    all_words = []
    folio_lines = defaultdict(list)

    for rl in raw_lines:
        if rl.startswith("#") or not rl.strip():
            continue
        if re.match(r"^<(f[0-9]+[rv][0-9]*|fRos)>\s*<!", rl):
            continue
        m = re.match(r"^<([^>]+)>\s+(.*)$", rl)
        if not m:
            continue
        hdr, body = m.group(1), m.group(2)
        loc = hdr.split(",")[0] if "," in hdr else hdr
        ltype = hdr.split(",")[1] if "," in hdr else ""
        folio = loc.split(".")[0]
        body_clean = re.sub(r"<[^>]*>", " ", body)
        toks = [clean_word(t) for t in re.split(r"[.,\s]+", body_clean) if clean_word(t)]
        if not toks:
            continue
        all_words.extend(toks)
        folio_lines[folio].append({
            "loc": loc,
            "loc_type": ltype,
            "raw_body": body,
            "words": toks,
            "canon": [canonicalize(t) for t in toks],
        })

    # 1. Analyze f49v 1..5 Key (`[f/p/k] - o - r - y - e`) as a 5-Slot Generative Tuple
    # On f49v, Arabic numerals 1, 2, 3, 4, 5 are written next to `f, o, r, y, e`,
    # followed by Cycle 2 (`p, o, @192;[r], y, e`), Cycle 3 (`p, o, @192;[r], y, e`), and Cycle 4 (`k, o, @192;[r], o`).
    # Notice that:
    # - Position 1 (`f` -> `p` -> `p` -> `k`) cycles through the Gallows Core consonants (`f, p, k, t`)!
    # - Position 2 (`o` -> `o` -> `o` -> `o`) is invariant Onset Vowel `o`!
    # - Position 3 (`r` -> `@192;` -> `@192;` -> `@192;`) is invariant Liquid `r`!
    # - Position 4 (`y` -> `y` -> `y` -> `o`) is Terminal Suffix `y`!
    # - Position 5 (`e` -> `e` -> `e` -> `@140;`) is Medial Grade Vowel `e`!
    f49v_labels = [l for l in folio_lines["f49v"] if "L" in l["loc_type"]]
    f49v_prose = [l for l in folio_lines["f49v"] if "P" in l["loc_type"]]

    f49v_aligned_rows = []
    for idx in range(max(len(f49v_labels), len(f49v_prose))):
        kl = f49v_labels[idx] if idx < len(f49v_labels) else None
        pl = f49v_prose[idx] if idx < len(f49v_prose) else None
        f49v_aligned_rows.append({
            "row": idx + 1,
            "key_loc": kl["loc"] if kl else None,
            "key_char": kl["words"][0] if (kl and kl["words"]) else None,
            "prose_loc": pl["loc"] if pl else None,
            "prose_first_word": pl["words"][0] if (pl and pl["words"]) else None,
            "prose_last_word": pl["words"][-1] if (pl and pl["words"]) else None,
        })

    # How many words in the entire Voynich corpus are formed purely from the 5 structural classes
    # represented by `1..5 = [Gallows: k/t/p/f/ch/sh] + [Onset: o/a] + [Liquid: r/l] + [Suffix: y/dy/in] + [Grade: e/o]`?
    # Let's also check how many words are formed strictly from the characters `{f, p, k, t, o, r, l, y, e, d, s, q, a, i, n, c, h}`
    char_counts = Counter(c for w in all_words for c in w)
    total_chars = sum(char_counts.values())
    f49v_base_set = set("fpktooryeds")
    f49v_expanded_set = set("fpktooryedsch")  # adding bench ch/sh
    cov_base = sum(char_counts[c] for c in f49v_base_set) / total_chars
    cov_exp = sum(char_counts[c] for c in f49v_expanded_set) / total_chars

    # Check exact words formed solely from `{f, p, k, t, o, r, y, e}` (the 5-tuple of f49v with gallows allographs)
    tuple_char_set = set("fpktorye")
    pure_tuple_words = Counter(w for w in all_words if set(w).issubset(tuple_char_set))
    # Plus with `q` or `d` proclitic/dental (`q, d` + `{f, p, k, t, o, r, y, e}`)
    qd_tuple_char_set = set("qdfpktorye")
    qd_tuple_words = Counter(w for w in all_words if set(w).issubset(qd_tuple_char_set))

    # 2. Complete 4-Ring Radial Alignment of f57v (`<f57v.2>`, `<f57v.3>`, `<f57v.4>`, `<f57v.5>`)
    f57v_rings = {}
    for l in folio_lines["f57v"]:
        f57v_rings[l["loc"]] = l["words"]

    r1 = f57v_rings.get("f57v.2", [])  # 54 tokens
    r2 = f57v_rings.get("f57v.3", [])  # 68 tokens (4 x 17)
    r3 = f57v_rings.get("f57v.4", [])  # 31 tokens
    r4 = f57v_rings.get("f57v.5", [])  # 33 tokens (innermost ring!)

    # Let's segment Ring 4 (`<f57v.5>`, 33 tokens) into alternating word-chunks and single-char delimiters
    # just as we did for Ring 1 and Ring 3!
    def segment_ring(tokens):
        segs = []
        cur_type = None
        cur_items = []
        cur_indices = []
        n = len(tokens)
        for i, t in enumerate(tokens):
             clean_len = len(re.sub(r"@[0-9]+;", "X", t))
             is_single = clean_len == 1
             stype = "DELIMITER" if is_single else "WORDS"
             if stype != cur_type and cur_items:
                 avg_ang = round(360.0 * (sum(cur_indices) / len(cur_indices)) / n, 1)
                 segs.append({
                     "type": cur_type,
                     "items": cur_items,
                     "count": len(cur_items),
                     "start_angle_deg": round(360.0 * cur_indices[0] / n, 1),
                     "center_angle_deg": avg_ang,
                 })
                 cur_items = []
                 cur_indices = []
             cur_type = stype
             cur_items.append(t)
             cur_indices.append(i)
        if cur_items:
            avg_ang = round(360.0 * (sum(cur_indices) / len(cur_indices)) / n, 1)
            segs.append({
                "type": cur_type,
                "items": cur_items,
                "count": len(cur_items),
                "start_angle_deg": round(360.0 * cur_indices[0] / n, 1),
                "center_angle_deg": avg_ang,
            })
        return segs

    r1_segs = segment_ring(r1)
    r3_segs = segment_ring(r3)
    r4_segs = segment_ring(r4)

    # 3. Align the 6 Radial Sectors across ALL 4 RINGS of f57v!
    # Sector boundaries in degrees (from 10 o'clock radial bar = 0 deg):
    # Sector 1: 0° .. 51°
    # Sector 2: 51° .. 78°
    # Sector 3: 78° .. 157°
    # Sector 4: 157° .. 210°
    # Sector 5: 210° .. 292°
    # Sector 6: 292° .. 360°
    sector_bounds = [
        ("Sector_1_10h_to_12h", 0.0, 50.0),
        ("Sector_2_12h_to_1h", 50.0, 78.0),
        ("Sector_3_1h_to_3h15", 78.0, 156.5),
        ("Sector_4_3h15_to_5h", 156.5, 208.5),
        ("Sector_5_5h_to_7h45", 208.5, 290.0),
        ("Sector_6_7h45_to_10h", 290.0, 360.0),
    ]

    def tokens_in_arc(tokens, a0, a1):
        n = len(tokens)
        out = []
        for i, t in enumerate(tokens):
            ang = 360.0 * i / n
            if a0 <= ang < a1:
                out.append(t)
        return out

    six_sectors = []
    for sname, a0, a1 in sector_bounds:
        six_sectors.append({
            "sector": sname,
            "angle_range_deg": [a0, a1],
            "ring1_outer_tokens": tokens_in_arc(r1, a0, a1),
            "ring2_key_tokens": tokens_in_arc(r2, a0, a1),
            "ring3_mid_tokens": tokens_in_arc(r3, a0, a1),
            "ring4_inner_tokens": tokens_in_arc(r4, a0, a1),
        })

    # 4. Compare the 17-Symbol Key of `f57v.3` with the 34-Symbol Margin Key of `f66r` and the `f49v` Key
    f66r_margin_key = [l["words"][0] for l in folio_lines["f66r"] if l["loc_type"] in ("*L0", "+L0", "@L0") and int(l["loc"].split(".")[1]) >= 16]
    f66r_corner_labels = [l for l in folio_lines["f66r"] if int(l["loc"].split(".")[1]) <= 15 or "Lx" in l["loc_type"]]

    # Check if the 34 margin key characters on f66r (`f66r.16..49`) align with the 32 prose lines on f66r (`f66r.50..81`)
    # and the 15 outer-left words (`f66r.1..15`), as verified visually on pages/f66r_top_left_labels_enh.png and pages/f66r_mid_left_labels_enh.png
    f66r_prose = [l for l in folio_lines["f66r"] if "P" in l["loc_type"]]
    f66r_outer_to_key_pairs = [
        {"outer_loc": "f66r.1", "outer_word": "rary", "key_loc": "f66r.16", "key_char": "y", "match_type": "ends_with_y", "prose_loc": "f66r.50 (<%>pdaiin...)"},
        {"outer_loc": "f66r.2", "outer_word": "rals", "key_loc": "f66r.18", "key_char": "s", "match_type": "ends_with_s", "prose_loc": "f66r.52"},
        {"outer_loc": "f66r.3", "outer_word": "qor", "key_loc": "f66r.20", "key_char": "y", "match_type": "none", "prose_loc": "f66r.54"},
        {"outer_loc": "f66r.4", "outer_word": "dary", "key_loc": "f66r.23", "key_char": "f", "match_type": "par2_start_gallows", "prose_loc": "f66r.57 (<%>tocpheey...)"},
        {"outer_loc": "f66r.5", "outer_word": "ykeol", "key_loc": "f66r.25", "key_char": "x", "match_type": "none", "prose_loc": "f66r.59"},
        {"outer_loc": "f66r.6", "outer_word": "saly", "key_loc": "f66r.29", "key_char": "y", "match_type": "ends_with_y", "prose_loc": "f66r.62"},
        {"outer_loc": "f66r.7", "outer_word": "salf", "key_loc": "f66r.30", "key_char": "f", "match_type": "ends_with_f (ultra-rare -f!)", "prose_loc": "f66r.63 (<%>pchof...)"},
        {"outer_loc": "f66r.8", "outer_word": "fary", "key_loc": "f66r.31", "key_char": "f", "match_type": "starts_with_f", "prose_loc": "f66r.64"},
        {"outer_loc": "f66r.9", "outer_word": "qotesy", "key_loc": "f66r.35", "key_char": "s", "match_type": "contains_s", "prose_loc": "f66r.67 (<%>psheody...)"},
        {"outer_loc": "f66r.10", "outer_word": "ykaly", "key_loc": "f66r.37", "key_char": "c", "match_type": "f57v_f_c_@172_seq", "prose_loc": "f66r.69"},
        {"outer_loc": "f66r.11", "outer_word": "doly", "key_loc": "f66r.39", "key_char": "x", "match_type": "par5_start_t_o", "prose_loc": "f66r.70 (<%>todeeey...)"},
        {"outer_loc": "f66r.12", "outer_word": "saiin", "key_loc": "f66r.41", "key_char": "o", "match_type": "none", "prose_loc": "f66r.72"},
        {"outer_loc": "f66r.13", "outer_word": "qokal", "key_loc": "f66r.43", "key_char": "l", "match_type": "ends_with_l", "prose_loc": "f66r.74"},
        {"outer_loc": "f66r.14", "outer_word": "qolsa", "key_loc": "f66r.46", "key_char": "o", "match_type": "contains_o", "prose_loc": "f66r.77"},
        {"outer_loc": "f66r.15", "outer_word": "raral", "key_loc": "f66r.48", "key_char": "p", "match_type": "final_cycle_p_gallows", "prose_loc": "f66r.79 (pchedy)"},
    ]

    results = {
        "f49v_1_to_5_tuple_analysis": {
            "cycle_1_with_arabic_1_to_5": ["f", "o", "r", "y", "e"],
            "cycle_2": ["p", "o", "@192;(r)", "y", "e"],
            "cycle_3": ["p", "o", "@192;(r)", "y", "e"],
            "cycle_4": ["k", "o", "@192;(r)", "o", "@140;"],
            "slot_interpretation": {
                "1_f_p_k": "Slot 3 Core Gallows consonant (f on Line 0 / Cycle 1 -> p in Cycles 2-3 -> k in Cycle 4)",
                "2_o": "Slot 2 Onset nominal vowel (o-)",
                "3_r": "Slot 5a Liquid stem coda (-r)",
                "4_y": "Slot 5b Inflectional suffix (-y)",
                "5_e": "Slot 4 Medial vowel grade (e/ee)",
            },
            "corpus_char_coverage_fpktoryeds_pct": round(100.0 * cov_base, 2),
            "corpus_char_coverage_with_bench_ch_sh_pct": round(100.0 * cov_exp, 2),
            "pure_fpktorye_word_tokens": sum(pure_tuple_words.values()),
            "pure_fpktorye_pct_of_corpus": round(100.0 * sum(pure_tuple_words.values()) / len(all_words), 2),
            "top_20_pure_fpktorye_words": pure_tuple_words.most_common(20),
            "qd_plus_fpktorye_word_tokens": sum(qd_tuple_words.values()),
            "qd_plus_fpktorye_pct_of_corpus": round(100.0 * sum(qd_tuple_words.values()) / len(all_words), 2),
            "top_25_qd_fpktorye_words": qd_tuple_words.most_common(25),
            "f49v_line_by_line_alignment": f49v_aligned_rows,
        },
        "f57v_4ring_volvelle_analysis": {
            "ring_token_counts": {
                "Ring1_f57v.2": len(r1),
                "Ring2_f57v.3": len(r2),
                "Ring3_f57v.4": len(r3),
                "Ring4_f57v.5": len(r4),
            },
            "ring4_segments": r4_segs,
            "six_synchronized_sectors": six_sectors,
        },
        "f66r_key_and_corner_crib": {
            "margin_key_34_chars": f66r_margin_key,
            "outer_to_key_to_prose_alignment": f66r_outer_to_key_pairs,
            "corner_labels_and_lx": f66r_corner_labels,
            "prose_line_count": len(f66r_prose),
        },
    }

    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== 1. f49v (1..5 = f-o-r-y-e) GENERATIVE TUPLE ANALYSIS ===")
    print(f"  Corpus character coverage of {{f,p,k,t,o,r,y,e,d,s}}: {cov_base*100:.2f}% (with c,h: {cov_exp*100:.2f}%)")
    print(f"  Words built ONLY from {{f,p,k,t,o,r,y,e}}: {sum(pure_tuple_words.values())} tokens ({100.0*sum(pure_tuple_words.values())/len(all_words):.2f}% of MS!)")
    print("  Top 15 pure {f,p,k,t,o,r,y,e} words:", pure_tuple_words.most_common(15))
    print(f"  Words built ONLY from {{q,d}} + {{f,p,k,t,o,r,y,e}}: {sum(qd_tuple_words.values())} tokens ({100.0*sum(qd_tuple_words.values())/len(all_words):.2f}% of MS!)")
    print("  Top 15 {q,d}+{f,p,k,t,o,r,y,e} words:", qd_tuple_words.most_common(15))

    print("\n=== 2. f57v RING 4 (INNERMOST RING, 33 TOKENS) SEGMENTS ===")
    for s in r4_segs:
        print(f"  {s}")

    print("\n=== 3. f57v 6 SYNCHRONIZED SECTORS ACROSS ALL 4 RINGS ===")
    for sec in six_sectors:
        print(f"  [{sec['sector']} ({sec['angle_range_deg'][0]}°-{sec['angle_range_deg'][1]}°)]")
        print(f"    R1 (Outer) : {sec['ring1_outer_tokens']}")
        print(f"    R2 (Key)   : {sec['ring2_key_tokens']}")
        print(f"    R3 (Mid)   : {sec['ring3_mid_tokens']}")
        print(f"    R4 (Inner) : {sec['ring4_inner_tokens']}")

    print("\n=== 4. f66r CORNER LABELS & MARGIN KEY ===")
    for cl in f66r_corner_labels:
        print(f"  {cl['loc']} ({cl['loc_type']}): {cl['raw_body']} -> {cl['words']}")
    print("  f66r 34-char margin key:", " ".join(f66r_margin_key))


if __name__ == "__main__":
    main()
