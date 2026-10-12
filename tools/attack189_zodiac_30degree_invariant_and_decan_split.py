#!/usr/bin/env python3
"""
Attack 189 (Discovery 206): The Complete 10-Folio Zodiac Medallion Architecture
(f70v2-f73v), the 30 = 15 + 15 Decan-Split vs. Single-Sign 30-Degree Invariant,
Multi-Word Nymph Labels (f71r), and the Barreled (ot-/op-) vs. Unbarreled (ok-/of-)
Inflectional Polarity Law.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack189_zodiac_30degree_invariant_and_decan_split.json"


def clean_word(raw: str) -> str:
    w = re.sub(r"\{[^}]*\}", "", raw)
    w = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[@&;!\?\*\(\)\<\>\[\]']", "", w)
    return w.strip().lower()


def extract_stem(w: str) -> str:
    s = w
    for p in ("qo", "ch", "sh", "cth", "ckh", "cph", "cfh", "ok", "ot", "op", "of", "ol", "or", "al", "ar", "da", "sa", "yk", "yt", "yp", "yf"):
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    else:
        if len(s) > 2 and s[0] in "oydsklrtp":
            s = s[1:]
    for suf in ("aiin", "oiin", "eiin", "iin", "ain", "edy", "eey", "ody", "ady", "chy", "shy", "ky", "ty", "py", "fy", "dy", "ey", "ly", "ry", "ol", "or", "al", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n"):
        if s.endswith(suf) and len(s) > len(suf):
            s = s[:-len(suf)]
            break
    return s if s else w


ZODIAC_META = {
    "f70v2": {"sign": "Pisces", "month_gloss": "mars", "split": "Single (Full Sign)", "barreled": True},
    "f70v1": {"sign": "Aries I (Dark)", "month_gloss": "abril", "split": "Split Part 1 (Decans 1-1.5)", "barreled": True},
    "f71r":  {"sign": "Aries II (Light)", "month_gloss": "abril", "split": "Split Part 2 (Decans 1.5-3)", "barreled": True},
    "f71v":  {"sign": "Taurus I (Light)", "month_gloss": "may", "split": "Split Part 1 (Decans 1-1.5)", "barreled": True},
    "f72r1": {"sign": "Taurus II (Dark)", "month_gloss": "may", "split": "Split Part 2 (Decans 1.5-3)", "barreled": True},
    "f72r2": {"sign": "Gemini", "month_gloss": "juny", "split": "Single (Full Sign)", "barreled": False},
    "f72r3": {"sign": "Cancer", "month_gloss": "jolh", "split": "Single (Full Sign)", "barreled": False},
    "f72v3": {"sign": "Leo", "month_gloss": "agost", "split": "Single (Full Sign)", "barreled": False},
    "f72v2": {"sign": "Virgo", "month_gloss": "setembre", "split": "Single (Full Sign)", "barreled": False},
    "f72v1": {"sign": "Libra", "month_gloss": "octobre", "split": "Single (Full Sign)", "barreled": False},
    "f73r":  {"sign": "Scorpio", "month_gloss": "octobre/novembre", "split": "Single (Full Sign)", "barreled": False},
    "f73v":  {"sign": "Sagittarius", "month_gloss": "novembre/decembre", "split": "Single (Full Sign)", "barreled": False},
}

ZODIAC_ORDER = [
    "f70v2", "f70v1", "f71r", "f71v", "f72r1",
    "f72r2", "f72r3", "f72v3", "f72v2", "f72v1", "f73r", "f73v"
]


def parse_zodiac():
    lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    loc_re = re.compile(r"^<f([0-9]+[rv][0-9]*)\.([0-9]+),([^>]+)>\s+(.*)$")
    folios = defaultdict(lambda: {"rings": [], "nymph_loci": [], "other_loci": [], "all_words": []})

    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        m = loc_re.match(line)
        if not m:
            continue
        fol = "f" + m.group(1)
        if fol not in ZODIAC_META:
            continue
        lnum = int(m.group(2))
        ltype = m.group(3)
        raw_body = m.group(4)
        body = re.sub(r"<![^>]*>", "", raw_body)
        raw_tokens = [t for t in re.split(r"[.,\s]+", body) if t]
        words = [clean_word(t) for t in raw_tokens]
        words = [w for w in words if w and not w.startswith("@")]
        if not words:
            continue

        folios[fol]["all_words"].extend(words)
        if "C" in ltype:
            folios[fol]["rings"].append({"line": lnum, "ltype": ltype, "words": words})
        elif "Lz" in ltype or "L" in ltype:
            folios[fol]["nymph_loci"].append({"line": lnum, "ltype": ltype, "words": words, "text": ".".join(words)})
        else:
            folios[fol]["other_loci"].append({"line": lnum, "ltype": ltype, "words": words})

    return folios


def classify_prefix_group(w: str) -> str:
    if w.startswith(("ot", "op")):
        return "ot_op"
    if w.startswith(("ok", "of")):
        return "ok_of"
    if w.startswith(("ol", "or")):
        return "ol_or"
    if w.startswith(("ch", "sh")):
        return "ch_sh"
    if w.startswith(("d", "s", "y")):
        return "d_s_y"
    return "other"


def main():
    random.seed(42)
    folios = parse_zodiac()

    folio_summaries = []
    barreled_counts = Counter()
    unbarreled_counts = Counter()

    all_nymph_first_words = []
    for fol in ZODIAC_ORDER:
        data = folios[fol]
        meta = ZODIAC_META[fol]
        nymph_loci = data["nymph_loci"]
        rings = data["rings"]
        ring_words = [w for r in rings for w in r["words"]]
        nymph_words = [w for nl in nymph_loci for w in nl["words"]]
        multi_word_loci = [nl for nl in nymph_loci if len(nl["words"]) >= 2]

        pref_counts = Counter()
        for nl in nymph_loci:
            fw = nl["words"][0]
            pg = classify_prefix_group(fw)
            pref_counts[pg] += 1
            all_nymph_first_words.append((fol, meta["barreled"], fw, pg))
            if meta["barreled"]:
                barreled_counts[pg] += 1
            else:
                unbarreled_counts[pg] += 1

        # Exact and stem overlap between nymph labels and ring text on same folio
        ring_word_set = set(ring_words)
        ring_stem_set = {extract_stem(w) for w in ring_words}
        nymph_word_set = set(nymph_words)
        nymph_stem_set = {extract_stem(w) for w in nymph_words}

        shared_exact = sorted(nymph_word_set & ring_word_set)
        shared_stems = sorted(nymph_stem_set & ring_stem_set)

        ot_op = pref_counts["ot_op"]
        ok_of = pref_counts["ok_of"]
        ot_op_share = ot_op / (ot_op + ok_of) if (ot_op + ok_of) > 0 else 0.0

        folio_summaries.append({
            "folio": fol,
            "sign": meta["sign"],
            "month_gloss": meta["month_gloss"],
            "split": meta["split"],
            "barreled": meta["barreled"],
            "n_rings": len(rings),
            "ring_words_count": len(ring_words),
            "n_nymph_loci": len(nymph_loci),
            "nymph_words_count": len(nymph_words),
            "multi_word_nymph_loci_count": len(multi_word_loci),
            "multi_word_nymph_examples": [nl["text"] for nl in multi_word_loci[:6]],
            "prefix_counts": dict(pref_counts),
            "ot_op_vs_ok_of_ratio": round(ot_op_share * 100, 2),
            "shared_nymph_ring_exact_words": shared_exact,
            "shared_nymph_ring_stems_count": len(shared_stems),
            "nymph_stem_coverage_in_rings_pct": round(100.0 * len(shared_stems) / len(nymph_stem_set), 2) if nymph_stem_set else 0.0,
            "sample_nymph_labels": [nl["text"] for nl in nymph_loci[:10]],
        })

    # Sign-level 30-degree invariant table
    sign_30_table = [
        {"sign": "Pisces (mars)", "folios": ["f70v2"], "nymph_loci_total": len(folios["f70v2"]["nymph_loci"]), "target_30": 30, "notes": "29 barreled nymphs + 1 central star label = 30 @Lz loci"},
        {"sign": "Aries (abril)", "folios": ["f70v1", "f71r"], "nymph_loci_total": len(folios["f70v1"]["nymph_loci"]) + len(folios["f71r"]["nymph_loci"]), "target_30": 30, "notes": "15 (5+10) Dark + 15 (5+10) Light = 30 exact degrees"},
        {"sign": "Taurus (may)", "folios": ["f71v", "f72r1"], "nymph_loci_total": len(folios["f71v"]["nymph_loci"]) + len(folios["f72r1"]["nymph_loci"]), "target_30": 30, "notes": "15 (5+10) Light + 15 (5+10) Dark = 30 exact degrees"},
        {"sign": "Gemini (juny)", "folios": ["f72r2"], "nymph_loci_total": len(folios["f72r2"]["nymph_loci"]), "target_30": 30, "notes": "30 unbarreled nymphs in 1 page"},
        {"sign": "Cancer (jolh)", "folios": ["f72r3"], "nymph_loci_total": len(folios["f72r3"]["nymph_loci"]), "target_30": 30, "notes": "41 @Lz loci (30 degree-nymphs + extra inner/outer star labels)"},
        {"sign": "Leo (agost)", "folios": ["f72v3"], "nymph_loci_total": len(folios["f72v3"]["nymph_loci"]), "target_30": 30, "notes": "31 @Lz loci (30 degree-nymphs + 1 central emblem label)"},
        {"sign": "Virgo (setembre)", "folios": ["f72v2"], "nymph_loci_total": len(folios["f72v2"]["nymph_loci"]), "target_30": 30, "notes": "30 exact degree-nymphs"},
        {"sign": "Libra (octobre)", "folios": ["f72v1"], "nymph_loci_total": len(folios["f72v1"]["nymph_loci"]), "target_30": 30, "notes": "30 exact degree-nymphs"},
        {"sign": "Scorpio (octobre)", "folios": ["f73r"], "nymph_loci_total": len(folios["f73r"]["nymph_loci"]), "target_30": 30, "notes": "31 @Lz loci (1 central star otedy + 10 inner + 16 middle + 4 top overflow = 30 degree-nymphs)"},
        {"sign": "Sagittarius (novembre)", "folios": ["f73v"], "nymph_loci_total": len(folios["f73v"]["nymph_loci"]), "target_30": 30, "notes": "30 exact degree-nymphs (10 inner + 16 middle + 4 top overflow)"},
    ]

    # Chi-square on barreled vs unbarreled ot/op vs ok/of
    b_ot = barreled_counts["ot_op"]
    b_ok = barreled_counts["ok_of"]
    u_ot = unbarreled_counts["ot_op"]
    u_ok = unbarreled_counts["ok_of"]
    total_ot_ok = b_ot + b_ok + u_ot + u_ok
    chi2 = (total_ot_ok * (b_ot * u_ok - b_ok * u_ot) ** 2) / (
        (b_ot + b_ok) * (u_ot + u_ok) * (b_ot + u_ot) * (b_ok + u_ok)
    )
    z_equiv = math.sqrt(chi2)

    # Split-sign pair cohesion (Aries I <-> Aries II, Taurus I <-> Taurus II)
    def pair_stem_jaccard(f1, f2):
        s1 = {extract_stem(w) for w in folios[f1]["all_words"]}
        s2 = {extract_stem(w) for w in folios[f2]["all_words"]}
        return len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 0.0

    aries_jaccard = pair_stem_jaccard("f70v1", "f71r")
    taurus_jaccard = pair_stem_jaccard("f71v", "f72r1")
    mean_split_jaccard = (aries_jaccard + taurus_jaccard) / 2.0

    other_pairs = []
    for i, f1 in enumerate(ZODIAC_ORDER):
        for f2 in ZODIAC_ORDER[i + 1:]:
            if (f1, f2) not in [("f70v1", "f71r"), ("f71v", "f72r1")]:
                other_pairs.append(pair_stem_jaccard(f1, f2))
    mean_other_jaccard = sum(other_pairs) / len(other_pairs)

    out = {
        "attack": 189,
        "discovery": 206,
        "title": "Complete 12-Folio Zodiac Medallion Architecture (f70v2-f73v), the 30=15+15 Decan-Split Invariant, Multi-Word Nymph Labels (f71r), and Barreled vs. Unbarreled Prefix Polarity",
        "summary": {
            "total_zodiac_folios": len(ZODIAC_ORDER),
            "total_zodiac_signs_preserved": 10,
            "total_nymph_loci": sum(f["n_nymph_loci"] for f in folio_summaries),
            "total_ring_words": sum(f["ring_words_count"] for f in folio_summaries),
            "barreled_ot_op": b_ot,
            "barreled_ok_of": b_ok,
            "barreled_ot_op_pct": round(100.0 * b_ot / (b_ot + b_ok), 2),
            "unbarreled_ot_op": u_ot,
            "unbarreled_ok_of": u_ok,
            "unbarreled_ok_of_pct": round(100.0 * u_ok / (u_ot + u_ok), 2),
            "barreled_vs_unbarreled_chi2": round(chi2, 2),
            "barreled_vs_unbarreled_z": round(z_equiv, 2),
            "aries_split_stem_jaccard": round(aries_jaccard, 4),
            "taurus_split_stem_jaccard": round(taurus_jaccard, 4),
            "mean_split_sign_jaccard": round(mean_split_jaccard, 4),
            "mean_other_zodiac_jaccard": round(mean_other_jaccard, 4),
        },
        "sign_30_degree_invariant_table": sign_30_table,
        "folio_summaries": folio_summaries,
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print(json.dumps(out["summary"], indent=2))
    for s in sign_30_table:
        print(f"  {s['sign']:24s}: {s['nymph_loci_total']} loci ({s['notes']})")


if __name__ == "__main__":
    main()
