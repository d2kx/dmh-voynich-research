"""Deep analysis of the f57v 4-ring cipher/key wheel and comparison with f49v, f66r, and f76r margin keys."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_FILE = ROOT / "data" / "ZL3b-n.txt"
OUT_FILE = ROOT / "data" / "cipher_wheel_f57v_analysis.json"


def parse_raw_folio_lines(folio_id: str):
    text = ZL_FILE.read_text(encoding="utf-8", errors="ignore")
    loc_re = re.compile(rf"^<({folio_id})\.([^,>]+),([^>]+)>\s*(.*)$")
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        m = loc_re.match(line)
        if m:
            f_id, loc_id, ltype, body = m.groups()
            body_clean = re.sub(r"<![^>]*>", "", body)
            body_clean = body_clean.replace("<%>", "").replace("<$>", "").strip()
            tokens = [t for t in re.split(r"[.,\s]+", body_clean) if t and t != "-"]
            lines.append({
                "loc": f"{f_id}.{loc_id}",
                "ltype": ltype,
                "tokens": tokens,
            })
    return lines


def segment_words_and_single_chars(tokens):
    """Segment a ring token list into alternating chunks of single characters (len 1 or @code) and multi-char words."""
    segments = []
    cur_type = None
    cur_items = []
    for idx, t in enumerate(tokens):
        is_single = (len(t) == 1) or t.startswith("@") or t in ("sh", "ch", "aiin", "ar", "vs", "vo", "yf") and len(t) <= 2
        # Let's strictly define single-char tokens as len(t)==1 or @code
        strict_single = (len(t) == 1) or t.startswith("@")
        ttype = "CHAR" if strict_single else "WORD"
        if ttype != cur_type:
            if cur_items:
                segments.append({"type": cur_type, "items": cur_items})
            cur_type = ttype
            cur_items = [(idx, t)]
        else:
            cur_items.append((idx, t))
    if cur_items:
        segments.append({"type": cur_type, "items": cur_items})
    return segments


def main():
    f57v_lines = parse_raw_folio_lines("f57v")
    rings = {}
    for l in f57v_lines:
        rings[l["loc"]] = {
            "ltype": l["ltype"],
            "count": len(l["tokens"]),
            "tokens": l["tokens"],
            "segments": segment_words_and_single_chars(l["tokens"]),
        }

    # Align Ring 1 (f57v.2, 54 tokens), Ring 2 (f57v.3, 55 tokens), Ring 3 (f57v.4, 29 tokens), Ring 4 (f57v.5, 33 tokens)
    # by normalized angular position [0..1] around the circle (starting from the 10 o'clock radial line)
    r1 = rings["f57v.2"]["tokens"]
    r2 = rings["f57v.3"]["tokens"]
    r3 = rings["f57v.4"]["tokens"]
    r4 = rings["f57v.5"]["tokens"]

    # Map each token in r1, r2, r3, r4 to angle in degrees (0..360 clockwise from 10 o'clock radial bar)
    radial_table = []
    for i, tok2 in enumerate(r2):
        angle = round(360.0 * i / len(r2), 1)
        idx1 = min(len(r1) - 1, round(i * len(r1) / len(r2)))
        idx3 = min(len(r3) - 1, round(i * len(r3) / len(r2)))
        idx4 = min(len(r4) - 1, round(i * len(r4) / len(r2)))
        radial_table.append({
            "step": i + 1,
            "angle_deg": angle,
            "ring1_word": r1[idx1],
            "ring2_char": tok2,
            "ring3_token": r3[idx3],
            "ring4_token": r4[idx4],
        })

    # Group Ring 1 words by the Ring 2 single character they sit directly above across the 4 quadrants!
    # Ring 2 has 4 quadrants of 14 chars:
    # Q1: indices 0..12 (13 chars: o l d r v x k m f @169;v t r y)
    # Q2: indices 13..26 (14 chars: o l d r v x k m f @169;v t r y c)
    # Q3: indices 27..40 (14 chars: o l d r v x k m p @169;v t r y c)
    # Q4: indices 41..54 (14 chars: o l d r v x k m p @169;v t r y c)
    # Ring 2 has 4 exact quadrants of 17 tokens (4 x 17 = 68):
    quad_slices = [
        ("Q1", 0, 17),
        ("Q2", 17, 34),
        ("Q3", 34, 51),
        ("Q4", 51, 68),
    ]
    slot_names = [
        "o", "l", "d", "r1", "v", "x", "k", "m", "f_or_p",
        "@169;v", "t", "r2", "@170;", "@171;", "y", "I_or_c", "@172;",
    ]
    quadrant_alignment = defaultdict(dict)
    for qname, s_idx, e_idx in quad_slices:
        q_r2 = r2[s_idx:e_idx]
        for pos_idx, ch in enumerate(q_r2):
            global_i = s_idx + pos_idx
            idx1 = min(len(r1) - 1, round(global_i * len(r1) / len(r2)))
            slot_key = f"{pos_idx+1:02d}_{slot_names[pos_idx]}"
            quadrant_alignment[slot_key][qname] = {
                "ring2_char": ch,
                "ring1_token": r1[idx1],
                "ring1_idx": idx1,
            }

    # Also analyze the embedded single-character delimiter pairs in Ring 1 (f57v.2) vs Ring 3 (f57v.4)
    r1_delims = []
    for seg in rings["f57v.2"]["segments"]:
        if seg["type"] == "CHAR":
            avg_idx = sum(i for i, _ in seg["items"]) / len(seg["items"])
            r1_delims.append({
                "chars": " ".join(t for _, t in seg["items"]),
                "indices": [i for i, _ in seg["items"]],
                "angle_deg": round(360.0 * avg_idx / len(r1), 1),
            })
        else:
            r1_delims.append({
                "words": [t for _, t in seg["items"]],
                "count": len(seg["items"]),
                "angle_deg": round(360.0 * (sum(i for i, _ in seg["items"]) / len(seg["items"])) / len(r1), 1),
            })

    r3_delims = []
    for seg in rings["f57v.4"]["segments"]:
        if seg["type"] == "CHAR":
            avg_idx = sum(i for i, _ in seg["items"]) / len(seg["items"])
            r3_delims.append({
                "chars": " ".join(t for _, t in seg["items"]),
                "indices": [i for i, _ in seg["items"]],
                "angle_deg": round(360.0 * avg_idx / len(r3), 1),
            })
        else:
            r3_delims.append({
                "words": [t for _, t in seg["items"]],
                "count": len(seg["items"]),
                "angle_deg": round(360.0 * (sum(i for i, _ in seg["items"]) / len(seg["items"])) / len(r3), 1),
            })

    # Test f49v and f76r: how do the left-margin single characters (*L0) relate to the line (=P0) immediately to their right?
    f49v_lines = parse_raw_folio_lines("f49v")
    f49v_pairs = []
    for idx in range(0, len(f49v_lines) - 1, 2):
        lbl = f49v_lines[idx]
        pline = f49v_lines[idx + 1]
        if lbl["tokens"] and pline["tokens"]:
            mchar = lbl["tokens"][0]
            w1 = pline["tokens"][0]
            w_last = pline["tokens"][-1]
            f49v_pairs.append({
                "line_num": (idx // 2) + 1,
                "margin_char": mchar,
                "first_word": w1,
                "last_word": w_last,
                "line_words": pline["tokens"],
            })

    f76r_lines = parse_raw_folio_lines("f76r")
    f76r_pairs = []
    for idx, l in enumerate(f76r_lines):
        if l["ltype"] == "*L0" and idx + 1 < len(f76r_lines):
            pline = f76r_lines[idx + 1]
            f76r_pairs.append({
                "loc": l["loc"],
                "margin_char": l["tokens"][0] if l["tokens"] else "",
                "first_word": pline["tokens"][0] if pline["tokens"] else "",
                "last_word": pline["tokens"][-1] if pline["tokens"] else "",
                "line_words": pline["tokens"],
            })

    # Compare character inventories across all 4 key folios: f49v, f57v (Ring 2 & Ring 4), f66r, f76r
    f66r_lines = parse_raw_folio_lines("f66r")
    f66r_chars = [l["tokens"][0] for l in f66r_lines if l["ltype"] in ("@L0", "+L0") and l["tokens"] and (len(l["tokens"][0]) <= 2 or l["tokens"][0].startswith("@")) and int(l["loc"].split(".")[1]) >= 16]

    key_inventories = {
        "f49v_hand1_26chars": [p["margin_char"] for p in f49v_pairs],
        "f57v_ring2_hand4_55chars": r2,
        "f57v_ring4_hand4_25chars": [t for t in r4 if len(t) <= 2 or t == "aiin"],
        "f66r_hand5_34chars": f66r_chars,
        "f76r_hand2_9chars": [p["margin_char"] for p in f76r_pairs],
    }

    out = {
        "f57v_ring1_segments": r1_delims,
        "f57v_ring3_segments": r3_delims,
        "f57v_quadrant_slot_alignment": dict(quadrant_alignment),
        "f49v_margin_to_line_pairs": f49v_pairs,
        "f76r_margin_to_line_pairs": f76r_pairs,
        "key_character_inventories": key_inventories,
    }
    OUT_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("=== 1. f57v RING 1 (OUTER) ALTERNATING WORD-CHUNKS & SINGLE-CHAR DELIMITERS ===")
    for s in r1_delims:
        print(" ", s)

    print("\n=== 2. f57v RING 3 (INNER) ALTERNATING WORD-CHUNKS & SINGLE-CHAR DELIMITERS ===")
    for s in r3_delims:
        print(" ", s)

    print("\n=== 3. f57v 4-QUADRANT RADIAL ALIGNMENT (Ring 2 Single Chars <-> Ring 1 Words) ===")
    for slot_k, qdict in sorted(quadrant_alignment.items()):
        row_str = " | ".join(f"{qn}: {v['ring2_char']}->{v['ring1_token']}" for qn, v in qdict.items())
        print(f"  {slot_k:12s}: {row_str}")

    print("\n=== 4. f76r MARGIN KEY (*L0) vs LINE FIRST WORD (=P0) ===")
    for p in f76r_pairs:
        print(f"  {p['loc']} char='{p['margin_char']}' -> first_word='{p['first_word']}' (last='{p['last_word']}')")


if __name__ == "__main__":
    main()
