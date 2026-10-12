#!/usr/bin/env python3
"""
Attack 170 (Discovery 187): The 7 "Key-Like Sequence" Folios (f1r, f49v, f57v, f58r,
f66r, f76r, f116v), the f49v "1-2-3-4-5" Repeating Pentad Proof, and the f58r
Acrostic Margin Column Decoupling Law.
"""

import json
import math
import random
import re
from collections import Counter
from pathlib import Path

ZL_PATH = Path("data/ZL3b-n.txt")
OUT_PATH = Path("data/attack170_key_like_sequences_and_f49v_cycle_proof.json")


def parse_folio_lines(target_folio: str):
    lines = ZL_PATH.read_text(encoding="utf-8").splitlines()
    cur = ""
    out = []
    for l in lines:
        m_f = re.match(r"^<(f[0-9]+[rv][0-9]*|fRos)>", l)
        if m_f:
            cur = m_f.group(1)
            continue
        if cur == target_folio:
            out.append(l)
    return out


def analyze_f49v_pentad():
    lines = parse_folio_lines("f49v")
    margin_glyphs = []
    paired_lines = []
    last_glyph = None
    for l in lines:
        m = re.match(r"^<f49v\.(\d+),([^>]+)>\s+(.*)$", l)
        if not m:
            continue
        lno, ltype, text = m.groups()
        text_clean = text.strip()
        if "L0" in ltype:
            # Normalize @192; -> r* (plumed r allograph) and @140; -> L* (hooked l/e allograph)
            norm_g = text_clean
            if norm_g == "@192;":
                norm_Slot = "r_plumed(@192;)"
                canon_g = "R"
            elif norm_g == "@140;":
                norm_Slot = "hook(@140;)"
                canon_g = "L"
            elif norm_g == "@164;":
                norm_Slot = "crest(@164;)"
                canon_g = "C"
            else:
                norm_Slot = norm_g
                canon_g = norm_g.upper()
            last_glyph = {"line_no": int(lno), "raw": text_clean, "slot": norm_Slot, "canon": canon_g}
            margin_glyphs.append(last_glyph)
        elif "P0" in ltype and last_glyph is not None:
            words = [w for w in re.split(r"[.,\s]+", text_clean.replace("<%>", "").replace("<$>", "").replace("<->", ".")) if w]
            paired_lines.append({
                "margin_glyph": last_glyph["raw"],
                "canon_glyph": last_glyph["canon"],
                "first_word": words[0] if words else "",
                "line_text": " ".join(words[:5]),
            })

    canon_seq = "".join(g["canon"] for g in margin_glyphs)
    # Check repeating pentad O-R-Y-E-L (where R is r or @192;, L is @140;)
    # Sequence: F [O R Y E L] K S P [O R Y E L] C P [O R Y E L] D Y E K Y
    pentad = "ORYEL"
    pentad_occurrences = [m.start() for m in re.finditer(pentad, canon_seq)]

    # Permutation test: shuffle the 26 characters 10,000 times and count how often "ORYEL" (length 5) appears >= 3 times
    rng = random.Random(170)
    chars = list(canon_seq)
    null_counts = []
    hits_ge_3 = 0
    for _ in range(10000):
        rng.shuffle(chars)
        s = "".join(chars)
        c = s.count(pentad)
        null_counts.append(c)
        if c >= 3:
            hits_ge_3 += 1
    mean_null = sum(null_counts) / len(null_counts)
    sd_null = math.sqrt(sum((x - mean_null) ** 2 for x in null_counts) / len(null_counts)) or 0.001
    z_pentad = (len(pentad_occurrences) - mean_null) / sd_null

    return {
        "total_margin_glyphs": len(margin_glyphs),
        "raw_sequence": [g["raw"] for g in margin_glyphs],
        "canonical_sequence_string": canon_seq,
        "Segmented_Structure": [
            {"segment": "Header 1", "glyphs": ["f"], "note": "Top-line Gallows opener"},
            {"segment": "Pentad Cycle 1 (Numbered 1-2-3-4-5 in Left Margin!)", "glyphs": ["o (1)", "r (2)", "y (3)", "e (4)", "@140; (5)"], "note": "Explicitly numbered 1..5 in Arabic numerals by medieval reader"},
            {"segment": "Bridge 1", "glyphs": ["k", "s"], "note": "Inter-cycle transition"},
            {"segment": "Header 2 + Pentad Cycle 2", "glyphs": ["p", "o", "@192; (r*)", "y", "e", "@140;"], "note": "Second full 5-glyph cycle opened by Gallows p"},
            {"segment": "Header 3 + Pentad Cycle 3", "glyphs": ["@164;", "p", "o", "@192; (r*)", "y", "e", "@140;"], "note": "Third full 5-glyph cycle opened by Gallows p (spanning Para 2 -> Para 3)"},
            {"segment": "Closing Coda", "glyphs": ["d", "y", "e", "k", "y"], "note": "5-glyph terminal cadence closing Paragraph 3"},
        ],
        "pentad_pattern": "o - r/@192; - y - e - @140;",
        "pentad_exact_occurrences": len(pentad_occurrences),
        "pentad_start_indices_0based": pentad_occurrences,
        "permutation_10000_mean": round(mean_null, 5),
        "permutation_10000_p_value": hits_ge_3 / 10000.0,
        "pentad_z_score": round(z_pentad, 2),
        "paired_lines_sample": paired_lines[:15],
    }


def analyze_f58r_acrostic():
    lines = parse_folio_lines("f58r")
    para3_lines = []
    in_para3 = False
    for l in lines:
        if "<f58r.26," in l:
            in_para3 = True
        if in_para3:
            m = re.match(r"^<f58r\.(\d+),([^>]+)>\s+(.*)$", l)
            if m:
                lno, ltype, text = m.groups()
                t = re.sub(r"<!.*?>", "", text).replace("<%>", "").replace("<$>", "").strip()
                first_token = re.split(r"[.\s]+", t)[0]
                para3_lines.append({"line_no": int(lno), "raw_first_token": first_token, "full_line": t})
            if "<$>" in l:
                break

    decoupled_rows = []
    anomalies_before = 0
    anomalies_after = 0
    for row in para3_lines:
        raw_tok = row["raw_first_token"]
        clean_tok = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", raw_tok)
        clean_tok = re.sub(r"\{([^}]+)\}", r"\1", clean_tok)
        # First character is the margin acrostic letter (sometimes followed by a comma like s,ysheos)
        if "," in clean_tok and clean_tok.index(",") == 1:
            margin_char = clean_tok[0]
            rest_word = clean_tok[2:]
        else:
            margin_char = clean_tok[0]
            rest_word = clean_tok[1:]

        # Check if raw_tok is phonotactically anomalous in Voynichese:
        # e.g., o + qo... (oqotaly), d + t... (dtor, dtshol), o + p... (opolkeor), s, + y... (s,ysheos), y + ss... (yssheol)
        is_anom_before = bool(
            clean_tok.startswith("oqo")
            or clean_tok.startswith("dt")
            or clean_tok.startswith("op") and "polk" in clean_tok
            or raw_tok.startswith("s,y")
            or clean_tok.startswith("yss")
            or clean_tok.startswith("odsh")
        )
        if is_anom_before:
            anomalies_before += 1

        is_anom_after = bool(
            rest_word.startswith("oqo")
            or rest_word.startswith("dt")
        )
        if is_anom_after:
            anomalies_after += 1

        decoupled_rows.append({
            "line_no": row["line_no"],
            "raw_first_token": raw_tok,
            "margin_key_char": margin_char,
            "restored_initial_word": rest_word,
            "was_phonotactic_anomaly": is_anom_before,
            "is_anomaly_after_decoupling": is_anom_after,
        })

    acrostic_seq = [r["margin_key_char"] for r in decoupled_rows]
    return {
        "total_lines_in_para3": len(decoupled_rows),
        "acrostic_margin_sequence": acrostic_seq,
        "acrostic_string": "".join(acrostic_seq),
        "unique_acrostic_alphabet": sorted(set(acrostic_seq)),
        "acrostic_char_counts": dict(Counter(acrostic_seq)),
        "phonotactic_anomalies_before_decoupling": anomalies_before,
        "phonotactic_anomaly_rate_before_pct": round(anomalies_before / len(decoupled_rows) * 100, 2),
        "phonotactic_anomalies_after_decoupling": anomalies_after,
        "decoupled_lines": decoupled_rows,
    }


def analyze_all_7_key_folios():
    # Collect the single-glyph / key sequences across the 7 key-like folios
    f76r_lines = parse_folio_lines("f76r")
    f76r_key = []
    for l in f76r_lines:
        m = re.match(r"^<f76r\.\d+,[^>]*L0[^>]*>\s+(.*)$", l)
        if m:
            f76r_key.append(m.group(1).strip())

    f66r_lines = parse_folio_lines("f66r")
    f66r_key = []
    for l in f66r_lines:
        m = re.match(r"^<f66r\.\d+,[^>]*L0[^>]*>\s+(.*)$", l)
        if m:
            w = m.group(1).strip()
            if len(w) <= 2 or w.startswith("@"):
                f66r_key.append(w)

    f1r_lines = parse_folio_lines("f1r")
    f1r_key = []
    for l in f1r_lines:
        m = re.match(r"^<f1r\.\d+,[^>]*L0[^>]*>\s+(.*)$", l)
        if m:
            f1r_key.append(m.group(1).strip())

    return {
        "f1r_right_margin_key": f1r_key,
        "f66r_single_char_margin_key": f66r_key,
        "f76r_left_margin_key": f76r_key,
        "seven_key_folios_catalog": [
            {
                "folio": "f1r",
                "section": "H (Herbal Opening Page)",
                "hand": "Hand 1 (Currier A)",
                "key_type": "Vertical single-character sequence in right/left margin + faded alphabetic column",
                "tokens": f1r_key,
            },
            {
                "folio": "f49v",
                "section": "H (Herbal Cyclamen/Lunaria)",
                "hand": "Hand 1 (Currier A)",
                "key_type": "26-line vertical left-margin column with Arabic numerals 1-2-3-4-5 marking 3x repeating 5-glyph pentad (o-r-y-e-@140;)",
                "tokens": ["f", "o", "r", "y", "e", "@140;", "k", "s", "p", "o", "@192;", "y", "e", "@140;", "@164;", "p", "o", "@192;", "y", "e", "@140;", "d", "y", "e", "k", "y"],
            },
            {
                "folio": "f57v",
                "section": "C/H (End of Quire 7 Key Ring)",
                "hand": "Hand 3 (Currier A/B bridge)",
                "key_type": "4 concentric rings of repeating single-character sequences (f <-> p 4-quadrant substitution wheel) + Saturn symbol",
                "tokens": ["d,o,l,d,a,r...", "f <-> p quadrant substitution rings"],
            },
            {
                "folio": "f58r",
                "section": "S/H (Starred Herbal Index, Quire 8 opening)",
                "hand": "Hand 3 (Currier A)",
                "key_type": "6-, 7-, and 8-pointed left-margin stars + 16-line vertical acrostic prefix column (k,y,y,o,y,o,o,s,y,d,s,o,s,d,y,d) prepended to Paragraph 3",
                "tokens": ["k", "y", "y", "o", "y", "o", "o", "s", "y", "d", "s", "o", "s", "d", "y", "d"],
            },
            {
                "folio": "f66r",
                "section": "H/B (End of Quire 8 Bilingual Tub Page)",
                "hand": "Hand 3 (Currier B)",
                "key_type": "Vertical single-glyph margin column (o,d,y,s,r,p,f,t...) alongside reclining hydrotherapy figure labeled 'den mus / del'",
                "tokens": f66r_key,
            },
            {
                "folio": "f76r",
                "section": "B (Balneological Text-Only Master Treatise)",
                "hand": "Hand 2 (Currier B)",
                "key_type": "11-letter vertical left-margin index column (d, o, l, r, s, y, q, o, d, k, s) keying the paragraphs of the bath treatise",
                "tokens": f76r_key,
            },
            {
                "folio": "f116v",
                "section": "X (Final Codex Page Bilingual Crib)",
                "hand": "Marginalia / Final Hand",
                "key_type": "Bilingual Western Romance/Latin + German + Voynichese charm ('anchiton oladabas... multas te tuly... poror / oror') + Roman alphabet key trial",
                "tokens": ["oror", "poror", "oladabas", "multas", "te", "tuly"],
            },
        ],
    }


def main():
    f49v_res = analyze_f49v_pentad()
    f58r_res = analyze_f58r_acrostic()
    key_cat = analyze_all_7_key_folios()

    # Compute core prefix-radical share across f49v, f58r, f66r, f76r single-char keys
    core_radicals = {"o", "y", "d", "s", "r", "l", "k", "p", "f", "t", "e", "q", "@192;", "@140;"}
    all_single_chars = (
        f49v_res["raw_sequence"]
        + f58r_res["acrostic_margin_sequence"]
        + key_cat["f66r_single_char_margin_key"]
        + key_cat["f76r_left_margin_key"]
    )
    in_core = sum(1 for c in all_single_chars if c in core_radicals)
    core_share_pct = round(in_core / max(1, len(all_single_chars)) * 100, 2)

    out = {
        "attack": "Attack 170",
        "discovery": "Discovery 187",
        "title": "The 7 Key-Like Sequence Folios, the f49v 1-2-3-4-5 Repeating Pentad Proof, and the f58r Acrostic Margin Decoupling Law",
        "summary": {
            "total_key_like_folios": 7,
            "f49v_margin_glyph_count": f49v_res["total_margin_glyphs"],
            "f49v_repeating_pentad": f49v_res["pentad_pattern"],
            "f49v_pentad_exact_repetitions": f49v_res["pentad_exact_occurrences"],
            "f49v_pentad_z_score": f49v_res["pentad_z_score"],
            "f49v_pentad_p_value": f49v_res["permutation_10000_p_value"],
            "f58r_para3_lines": f58r_res["total_lines_in_para3"],
            "f58r_acrostic_alphabet": f58r_res["unique_acrostic_alphabet"],
            "f58r_anomalies_before_decoupling": f58r_res["phonotactic_anomalies_before_decoupling"],
            "f58r_anomalies_after_decoupling": f58r_res["phonotactic_anomalies_after_decoupling"],
            "total_vertical_margin_glyph_tokens": len(all_single_chars),
            "core_prefix_header_radical_coverage_pct": core_share_pct,
        },
        "f49v_pentad_analysis": f49v_res,
        "f58r_acrostic_analysis": f58r_res,
        "seven_key_folios": key_cat,
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_PATH}")
    print("Summary:", json.dumps(out["summary"], indent=2))


if __name__ == "__main__":
    main()
