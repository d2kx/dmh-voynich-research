"""
Attack 62: Complete 6-Level Hierarchical Entropy Decomposition of the Voynich Vocabulary.

Decomposes the entire unigram word entropy H(Word) = 10.7699 bits (across 36,229 tokens and
8,510 unique word types in `ZL3b-n.txt`) through a 6-level morphological and paleographic cascade:

  Level 1: Macro-Class (`OPEN_GALLOWS_BENCH` [75.99%] vs `CLOSED_FUNCTIONAL` [23.74%] vs `RESIDUAL` [0.27%])
  Level 2: Dual-Matrix Cell (`[Prefix_8 x Core_6 x Coda_8]` + `[Onset_7 x Coda_8]` = 419 attested cells)
  Level 3: Internal Stem Nucleus (`V_nuc` in `[ZERO_V, E1, E2, O_VOW, EO_DIPH, A_VOW, OTHER_V]`)
  Level 4: Exact Prefix & Coda Allograph (`l/ol/qol/al`, `-in/-iin/-iiin`, `-y/-dy/-ey/-edy`, `-am/-om/-m`)
  Level 5: Core Allograph & Secondary Radical (`k vs f`, `t vs p`, `SEQ kch vs PED ckh`, + compound secondary radical)
  Level 6: Residual Idiosyncratic / Hapax Surface Noise

Tests how much of the 10.7699-bit word entropy of the Voynich Manuscript is explained at each level,
and characterizes the exact residual entropy H(Word | L1..L5).
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack62_subcell_allography_entropy_decomposition.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")
KCH_COMPLEX = ("kch", "fch", "ksh", "fsh", "ckh", "cfh")
TCH_COMPLEX = ("tch", "pch", "tsh", "psh", "cth", "cph")


def shannon_entropy(counts: Counter) -> float:
    tot = sum(counts.values())
    if tot == 0:
        return 0.0
    return -sum((c / tot) * math.log2(c / tot) for c in counts.values() if c > 0)


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def classify_pre(pre: str) -> str:
    if pre == "":
        return "ZERO"
    if pre.startswith("qo"):
        return "QO"
    if pre.startswith("ol") or pre.startswith("qol") or pre.startswith("l") or pre.startswith("al"):
        return "L_APPL"
    if pre.startswith("o"):
        return "O_VOW"
    if pre.startswith("y"):
        return "Y"
    if pre.startswith("d"):
        return "D"
    if pre.startswith("s"):
        return "S"
    return "R_OTHER"


def parse_post_details(post: str):
    coda_coarse = "AM_OTHER"
    coda_exact = "BARE"
    nuc_str = post
    for suf_pat, c_label in [
        ("dy", "DY"),
        ("aiin", "AIIN"), ("iiin", "AIIN"), ("iin", "AIIN"), ("ain", "AIIN"), ("in", "AIIN"),
        ("y", "Y"),
        ("ol", "OL"), ("or", "OR"), ("al", "AL"), ("ar", "AR"),
        ("am", "AM_OTHER"), ("om", "AM_OTHER"), ("m", "AM_OTHER"),
        ("s", "AM_OTHER"), ("d", "AM_OTHER"), ("l", "OL"), ("r", "OR"),
    ]:
        if post.endswith(suf_pat):
            coda_coarse = c_label
            coda_exact = suf_pat
            nuc_str = post[:-len(suf_pat)]
            if suf_pat in ("aiin", "ain"):
                nuc_str = post[:-len(suf_pat)] + "a"
            elif suf_pat in ("ol", "or"):
                nuc_str = post[:-2] + "o"
            elif suf_pat in ("al", "ar"):
                nuc_str = post[:-2] + "a"
            elif suf_pat in ("am", "om"):
                nuc_str = post[:-1]
            break

    if nuc_str == "":
        v_nuc = "ZERO_V"
    elif nuc_str in ("ee", "eee"):
        v_nuc = "E2"
    elif nuc_str == "e":
        v_nuc = "E1"
    elif nuc_str in ("eo", "eeo"):
        v_nuc = "EO_DIPH"
    elif nuc_str in ("o", "oo"):
        v_nuc = "O_VOW"
    elif nuc_str in ("a", "ea", "oa"):
        v_nuc = "A_VOW"
    else:
        v_nuc = "OTHER_V"

    # Secondary consonant/radical inside nuc_str (if any consonants remain in nuc_str)
    sec_rad = re.sub(r"[aeio]+", "V", nuc_str)
    return v_nuc, coda_coarse, coda_exact, sec_rad


def hierarchical_keys(w: str):
    # Check Open Class
    for pat in KCH_COMPLEX:
        idx = w.find(pat)
        if idx != -1:
            pre_s = w[:idx]
            post_s = w[idx + len(pat):]
            pre_c = classify_pre(pre_s)
            v_nuc, coda_c, coda_ex, sec_rad = parse_post_details(post_s)
            l1 = "OPEN"
            l2 = f"{l1}:{pre_c}:KCH_CKH:{coda_c}"
            l3 = f"{l2}:{v_nuc}"
            l4 = f"{l3}:{pre_s[:3]}:{coda_ex}"
            l5 = f"{l4}:{pat}:{sec_rad}"
            return l1, l2, l3, l4, l5

    for pat in TCH_COMPLEX:
        idx = w.find(pat)
        if idx != -1:
            pre_s = w[:idx]
            post_s = w[idx + len(pat):]
            pre_c = classify_pre(pre_s)
            v_nuc, coda_c, coda_ex, sec_rad = parse_post_details(post_s)
            l1 = "OPEN"
            l2 = f"{l1}:{pre_c}:TCH_CTH:{coda_c}"
            l3 = f"{l2}:{v_nuc}"
            l4 = f"{l3}:{pre_s[:3]}:{coda_ex}"
            l5 = f"{l4}:{pat}:{sec_rad}"
            return l1, l2, l3, l4, l5

    for pat, cname in (("ch", "CH"), ("sh", "SH")):
        idx = w.find(pat)
        if idx != -1:
            pre_s = w[:idx]
            post_s = w[idx + 2:]
            pre_c = classify_pre(pre_s)
            v_nuc, coda_c, coda_ex, sec_rad = parse_post_details(post_s)
            l1 = "OPEN"
            l2 = f"{l1}:{pre_c}:{cname}:{coda_c}"
            l3 = f"{l2}:{v_nuc}"
            l4 = f"{l3}:{pre_s[:3]}:{coda_ex}"
            l5 = f"{l4}:{pat}:{sec_rad}"
            return l1, l2, l3, l4, l5

    for i, ch in enumerate(w):
        if ch in ("k", "f", "t", "p"):
            cname = "K_F" if ch in ("k", "f") else "T_P"
            pre_s = w[:i]
            post_s = w[i + 1:]
            pre_c = classify_pre(pre_s)
            v_nuc, coda_c, coda_ex, sec_rad = parse_post_details(post_s)
            l1 = "OPEN"
            l2 = f"{l1}:{pre_c}:{cname}:{coda_c}"
            l3 = f"{l2}:{v_nuc}"
            l4 = f"{l3}:{pre_s[:3]}:{coda_ex}"
            l5 = f"{l4}:{ch}:{sec_rad}"
            return l1, l2, l3, l4, l5

    # Closed Class
    for p, lbl in [
        ("qo", "QO_PRO"), ("o", "O_VOW"), ("a", "O_VOW"), ("e", "O_VOW"), ("i", "O_VOW"),
        ("y", "Y_CONJ"), ("d", "D_DEIC"), ("s", "S_SIB"), ("l", "L_APPL"), ("r", "R_PORT")
    ]:
        if w.startswith(p):
            post_s = w[len(p):]
            v_nuc, coda_c, coda_ex, sec_rad = parse_post_details(post_s)
            l1 = "CLOSED"
            l2 = f"{l1}:{lbl}:{coda_c}"
            l3 = f"{l2}:{v_nuc}"
            l4 = f"{l3}:{p}:{coda_ex}"
            l5 = f"{l4}:{sec_rad}"
            return l1, l2, l3, l4, l5

    return "RESIDUAL", "RESIDUAL", "RESIDUAL", "RESIDUAL", f"RESIDUAL:{w[:2]}"


def main():
    word_counts = Counter()
    level_counts = [Counter() for _ in range(5)]
    l5_word_buckets = defaultdict(Counter)

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#"):
            continue
        m = LOCUS_RE.match(raw_line)
        if not m:
            continue
        toks = clean_tokens(m.group(4))
        for w in toks:
            word_counts[w] += 1
            keys = hierarchical_keys(w)
            for idx, k in enumerate(keys):
                level_counts[idx][k] += 1
            l5_word_buckets[keys[4]][w] += 1

    tot = sum(word_counts.values())
    h_total = shannon_entropy(word_counts)

    cascade = []
    prev_h = 0.0
    level_names = [
        "Level 1: Macro-Class (Open Gallows/Bench vs Closed Functional)",
        "Level 2: Dual-Matrix Cell ([Prefix x Core x Coda] / [Onset x Coda])",
        "Level 3: + Internal Stem Nucleus (ZERO_V, E1, E2, O_VOW, EO_DIPH, A_VOW)",
        "Level 4: + Exact Prefix Sub-Form & Minim/Coda Allograph (-in/-iin/-iiin, l-/ol-/qol-)",
        "Level 5: + Core Allograph (k/f, t/p, SEQ/PED) & Secondary Radical Skeleton",
    ]

    for idx, name in enumerate(level_names):
        h_val = shannon_entropy(level_counts[idx])
        gain = h_val - prev_h
        pct = 100.0 * h_val / h_total
        cascade.append({
            "level": idx + 1,
            "description": name,
            "attested_states": len(level_counts[idx]),
            "cumulative_entropy_bits": round(h_val, 4),
            "incremental_gain_bits": round(gain, 4),
            "cumulative_pct_of_word_entropy": round(pct, 2),
            "remaining_residual_bits": round(h_total - h_val, 4),
        })
        prev_h = h_val

    h_res = h_total - prev_h
    cascade.append({
        "level": 6,
        "description": "Level 6: Residual Surface Variation (Exact Vowel/Minim Spelling inside L5)",
        "attested_states": len(word_counts),
        "cumulative_entropy_bits": round(h_total, 4),
        "incremental_gain_bits": round(h_res, 4),
        "cumulative_pct_of_word_entropy": 100.0,
        "remaining_residual_bits": 0.0,
    })

    # Inspect top L5 buckets that still have >1 surface word to see what Level 6 is!
    multi_word_l5 = []
    for k5, wc in l5_word_buckets.items():
        if len(wc) > 1 and sum(wc.values()) >= 50:
            multi_word_l5.append({
                "l5_state": k5,
                "total_tokens": sum(wc.values()),
                "unique_words": len(wc),
                "within_bucket_entropy_bits": round(shannon_entropy(wc), 3),
                "top_words": dict(wc.most_common(5)),
            })
    multi_word_l5.sort(key=lambda d: d["total_tokens"], reverse=True)

    print("=== ATTACK 62: COMPLETE 6-LEVEL HIERARCHICAL ENTROPY DECOMPOSITION ===")
    print(f"Total Corpus: {tot:,} tokens, {len(word_counts):,} unique word types | H(Word) = {h_total:.4f} bits\n")
    for row in cascade:
        print(
            f"  L{row['level']} ({row['attested_states']:4d} states): Cumul H = {row['cumulative_entropy_bits']:7.4f} bits "
            f"(+{row['incremental_gain_bits']:6.4f} bits) -> {row['cumulative_pct_of_word_entropy']:6.2f}% explained "
            f"[Residual = {row['remaining_residual_bits']:.4f} bits] | {row['description']}"
        )
    print("\nTop L5 States with Residual Surface Allography (what remains in Level 6):")
    for b in multi_word_l5[:10]:
        print(f"  {b['l5_state']:38s} (n={b['total_tokens']:3d}, H={b['within_bucket_entropy_bits']:.2f}b): {b['top_words']}")

    out = {
        "total_tokens": tot,
        "unique_word_types": len(word_counts),
        "total_unigram_word_entropy_bits": round(h_total, 4),
        "six_level_cascade": cascade,
        "top_multiword_l5_buckets": multi_word_l5[:20],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved -> {OUT_JSON}")


if __name__ == "__main__":
    main()
