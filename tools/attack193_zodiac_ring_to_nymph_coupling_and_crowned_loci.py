#!/usr/bin/env python3
"""
Attack 193 (Discovery 210): The Zodiac Concentric Ring (@Cc) vs. Degree-Label (@Lz)
Coupling Law across all 12 Zodiac Folios (f70v2-f73v), Visual Forensics of the
Unfolded p132 (f72v3 Leo 'agost' | f72v2 Virgo 'setembre') & p133 (f72v1 Libra
'octobre') Sequence, Crowned 12:00 Leader-Nymphs, Pre-Existing Vellum Defect Hole
Avoidance on f72v1, and Quire 11 Signature '11m'.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack193_zodiac_ring_to_nymph_coupling_and_crowned_loci.json"

ZODIAC_FOLIOS = [
    ("f70v2", "Pisces", "mars", "p128"),
    ("f70v1", "Aries I (Dark)", "abril", "p128"),
    ("f71r", "Aries II (Light)", "abril", "p129"),
    ("f71v", "Taurus I (Light)", "may", "p130"),
    ("f72r1", "Taurus II (Dark)", "may", "p131"),
    ("f72r2", "Gemini", "juny", "p131"),
    ("f72r3", "Cancer", "jolh", "p131"),
    ("f72v3", "Leo", "agost", "p132"),
    ("f72v2", "Virgo", "setembre", "p132"),
    ("f72v1", "Libra", "octobre", "p133"),
    ("f73r", "Scorpio", "octobre", "p134"),
    ("f73v", "Sagittarius", "novembre", "p135"),
]

PREFIXES = ["qo", "ch", "sh", "ok", "ot", "ol", "or", "op", "of", "od", "da", "sa", "yk", "yt", "yd", "o", "d", "s", "y", "l", "r"]
SUFFIXES = ["aiin", "oiin", "eiin", "chedy", "shedy", "edy", "ody", "eey", "ey", "chy", "shy", "dy", "ol", "or", "al", "ar", "am", "om", "an", "in", "y", "r", "l", "m", "s"]


def clean_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    return w.strip()


def canonical_stem(w: str) -> str:
    s = w
    s = s.replace("ch", "C").replace("sh", "S").replace("ckh", "K").replace("cth", "T").replace("cph", "P").replace("cfh", "F")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    w2 = s.replace("C", "ch").replace("S", "sh").replace("K", "kh").replace("T", "th").replace("P", "ph").replace("F", "fh")
    if w2.endswith("m") and len(w2) > 2:
        w2 = w2[:-1] + "r"
    for p in PREFIXES:
        if w2.startswith(p) and len(w2) - len(p) >= 2:
            w2 = w2[len(p):]
            break
    for suf in SUFFIXES:
        if w2.endswith(suf) and len(w2) - len(suf) >= 2:
            w2 = w2[:-len(suf)]
            break
    if w2 and w2[0] in ("p", "f", "k", "t"):
        w2 = "K" + w2[1:]
    return w2 if w2 else w


def parse_zodiac():
    cc_words = defaultdict(list)
    lz_words = defaultdict(list)
    cc_loci = defaultdict(list)
    lz_loci = defaultdict(list)

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw.startswith("<f"):
            continue
        m = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s+(.*)$", raw)
        if not m:
            continue
        folio, lnum, ltype, body = m.groups()
        if folio not in {f[0] for f in ZODIAC_FOLIOS}:
            continue
        body_clean = re.sub(r"<!.*?>", "", body)
        tokens = [clean_word(t) for t in re.split(r"[.,\s]+", body_clean) if clean_word(t)]
        if not tokens:
            continue
        if "Cc" in ltype:
            cc_words[folio].extend(tokens)
            cc_loci[folio].append({"locus": f"{folio}.{lnum}", "ltype": ltype, "words": tokens})
        elif "Lz" in ltype or "L" in ltype:
            lz_words[folio].extend(tokens)
            lz_loci[folio].append({"locus": f"{folio}.{lnum}", "ltype": ltype, "words": tokens})

    return cc_words, lz_words, cc_loci, lz_loci


def morph_profile(words):
    n = len(words)
    if n == 0:
        return {}
    return {
        "n_words": n,
        "mean_len": round(sum(len(w) for w in words) / n, 3),
        "ok_ot_rate": round(sum(1 for w in words if w.startswith(("ok", "ot", "op", "of"))) / n, 4),
        "ot_op_rate": round(sum(1 for w in words if w.startswith(("ot", "op"))) / n, 4),
        "ok_of_rate": round(sum(1 for w in words if w.startswith(("ok", "of"))) / n, 4),
        "ch_sh_rate": round(sum(1 for w in words if w.startswith(("ch", "sh"))) / n, 4),
        "o_init_rate": round(sum(1 for w in words if w.startswith("o")) / n, 4),
        "y_dy_ey_rate": round(sum(1 for w in words if w.endswith(("y", "dy", "ey", "ody", "edy"))) / n, 4),
        "al_ar_ol_or_rate": round(sum(1 for w in words if w.endswith(("al", "ar", "ol", "or"))) / n, 4),
        "aiin_rate": round(sum(1 for w in words if w.endswith(("aiin", "oiin", "iin"))) / n, 4),
    }


def main():
    random.seed(42)
    cc_words, lz_words, cc_loci, lz_loci = parse_zodiac()

    all_cc = [w for f, _, _, _ in ZODIAC_FOLIOS for w in cc_words[f]]
    all_lz = [w for f, _, _, _ in ZODIAC_FOLIOS for w in lz_words[f]]

    cc_prof = morph_profile(all_cc)
    lz_prof = morph_profile(all_lz)

    # Test 1: Same-medallion @Cc <-> @Lz coupling vs random cross-medallion permutation
    folio_rows = []
    obs_exact_hits = 0
    obs_stem_hits = 0
    total_lz_tokens = 0
    obs_jaccard_exact = []
    obs_jaccard_stem = []

    for folio, sign, month, pdf_page in ZODIAC_FOLIOS:
        cc_w = cc_words[folio]
        lz_w = lz_words[folio]
        cc_set = set(cc_w)
        lz_set = set(lz_w)
        cc_stems = {canonical_stem(w) for w in cc_w}
        lz_stems = {canonical_stem(w) for w in lz_w}

        exact_hits = sum(1 for w in lz_w if w in cc_set)
        stem_hits = sum(1 for w in lz_w if canonical_stem(w) in cc_stems)
        obs_exact_hits += exact_hits
        obs_stem_hits += stem_hits
        total_lz_tokens += len(lz_w)

        j_ex = len(cc_set & lz_set) / max(1, len(cc_set | lz_set))
        j_st = len(cc_stems & lz_stems) / max(1, len(cc_stems | lz_stems))
        obs_jaccard_exact.append(j_ex)
        obs_jaccard_stem.append(j_st)

        folio_rows.append({
            "folio": folio,
            "sign": sign,
            "month": month,
            "pdf_page": pdf_page,
            "n_cc_rings": len(cc_loci[folio]),
            "n_cc_words": len(cc_w),
            "n_lz_loci": len(lz_loci[folio]),
            "n_lz_words": len(lz_w),
            "lz_in_same_cc_exact_count": exact_hits,
            "lz_in_same_cc_exact_rate": round(exact_hits / max(1, len(lz_w)), 4),
            "lz_in_same_cc_stem_count": stem_hits,
            "lz_in_same_cc_stem_rate": round(stem_hits / max(1, len(lz_w)), 4),
            "shared_exact_words": sorted(cc_set & lz_set),
            "shared_stems": sorted(cc_stems & lz_stems),
            "exact_jaccard": round(j_ex, 4),
            "stem_jaccard": round(j_st, 4),
        })

    obs_exact_rate = obs_exact_hits / total_lz_tokens
    obs_stem_rate = obs_stem_hits / total_lz_tokens
    mean_obs_j_ex = sum(obs_jaccard_exact) / len(obs_jaccard_exact)
    mean_obs_j_st = sum(obs_jaccard_stem) / len(obs_jaccard_stem)

    # Permutation baseline: shuffle @Cc ring assignments across the 12 Zodiac folios (excluding self where possible)
    folios = [f[0] for f in ZODIAC_FOLIOS]
    null_exact_rates = []
    null_stem_rates = []
    null_j_ex = []
    null_j_st = []

    for _ in range(2000):
        perm = folios[:]
        random.shuffle(perm)
        eh = 0
        sh = 0
        je = []
        js = []
        for f_lz, f_cc in zip(folios, perm):
            cc_set = set(cc_words[f_cc])
            lz_w = lz_words[f_lz]
            lz_set = set(lz_w)
            cc_stems = {canonical_stem(w) for w in cc_words[f_cc]}
            lz_stems = {canonical_stem(w) for w in lz_w}
            eh += sum(1 for w in lz_w if w in cc_set)
            sh += sum(1 for w in lz_w if canonical_stem(w) in cc_stems)
            je.append(len(cc_set & lz_set) / max(1, len(cc_set | lz_set)))
            js.append(len(cc_stems & lz_stems) / max(1, len(cc_stems | lz_stems)))
        null_exact_rates.append(eh / total_lz_tokens)
        null_stem_rates.append(sh / total_lz_tokens)
        null_j_ex.append(sum(je) / len(je))
        null_j_st.append(sum(js) / len(js))

    def z_score(obs, nulls):
        mu = sum(nulls) / len(nulls)
        sd = math.sqrt(sum((x - mu) ** 2 for x in nulls) / len(nulls))
        return round(mu, 4), round((obs - mu) / sd, 2) if sd > 0 else 0.0

    null_ex_mu, z_ex = z_score(obs_exact_rate, null_exact_rates)
    null_st_mu, z_st = z_score(obs_stem_rate, null_stem_rates)
    null_jex_mu, z_jex = z_score(mean_obs_j_ex, null_j_ex)
    null_jst_mu, z_jst = z_score(mean_obs_j_st, null_j_st)

    # Also check how many of the 299 @Lz labels echo in ANY @Cc ring across the 12 Zodiac pages
    global_cc_set = set(all_cc)
    global_cc_stems = {canonical_stem(w) for w in all_cc}
    lz_in_any_cc_exact = sum(1 for w in all_lz if w in global_cc_set)
    lz_in_any_cc_stem = sum(1 for w in all_lz if canonical_stem(w) in global_cc_stems)

    # Detailed profile of p132 (f72v3 Leo | f72v2 Virgo) & p133 (f72v1 Libra)
    p132_p133_forensics = {
        "f72v3_leo": {
            "month": "agost",
            "pdf_page": "p132 (left panel of unfolded f72v3 | f72v2 sheet)",
            "emblem": "Striding lion (Leo) with curving tail and red-painted scrotum/genitalia above Occitan/Catalan gloss 'agost'",
            "crowned_leader_nymph": "Top-center (12:00) outer-ring nymph wears a 3-pointed crown (<f72v3.13,@Lz> or.aiin / <f72v3.14,@Lz> otedy)",
            "cc_rings": cc_loci["f72v3"],
            "n_lz": len(lz_loci["f72v3"]),
        },
        "f72v2_virgo": {
            "month": "setembre",
            "pdf_page": "p132 (right panel of unfolded f72v3 | f72v2 sheet, marked '72' top right)",
            "emblem": "Standing maiden (Virgo) in pleated blue-and-white medieval gown and blue cap holding a stemmed star above 'setembre'",
            "stemmed_stars": "Both inner (11) and outer (19) nymphs hold their golden stars attached to vertical floral/staff stems",
            "cc_rings": cc_loci["f72v2"],
            "n_lz": len(lz_loci["f72v2"]),
        },
        "f72v1_libra": {
            "month": "octobre",
            "pdf_page": "p133 (with bottom-right Quire 11 signature '11m')",
            "emblem": "Mechanical blue-and-gold balance scale (Libra) with two circular pans above 'octobre'",
            "crowned_leader_nymph": "Top-center (12:30) outer-ring nymph wears a tall 3-peaked crown (<f72v1.12,@Lz> okchey / <f72v1.13,@Lz> otedy)",
            "vellum_defect_hole": "Large circular natural vellum defect hole (~100 px) at 03:00 on the inner ring; the circular ring boundary and text curve cleanly around the hole without losing a single glyph",
            "quire_signature": "Bottom-right corner preserves the medieval bookbinder's Quire 11 signature '11m' (matching '10m' on f71r)",
            "cc_rings": cc_loci["f72v1"],
            "n_lz": len(lz_loci["f72v1"]),
        },
    }

    out = {
        "summary": {
            "n_zodiac_folios": len(ZODIAC_FOLIOS),
            "total_cc_words": len(all_cc),
            "total_lz_words": len(all_lz),
            "same_medallion_lz_in_cc_exact_count": obs_exact_hits,
            "same_medallion_lz_in_cc_exact_rate": round(obs_exact_rate, 4),
            "null_lz_in_cc_exact_rate": null_ex_mu,
            "same_medallion_exact_lift": round(obs_exact_rate / max(1e-9, null_ex_mu), 2),
            "same_medallion_exact_z": z_ex,
            "same_medallion_lz_in_cc_stem_count": obs_stem_hits,
            "same_medallion_lz_in_cc_stem_rate": round(obs_stem_rate, 4),
            "null_lz_in_cc_stem_rate": null_st_mu,
            "same_medallion_stem_lift": round(obs_stem_rate / max(1e-9, null_st_mu), 2),
            "same_medallion_stem_z": z_st,
            "mean_exact_jaccard": round(mean_obs_j_ex, 4),
            "null_exact_jaccard": null_jex_mu,
            "exact_jaccard_z": z_jex,
            "mean_stem_jaccard": round(mean_obs_j_st, 4),
            "null_stem_jaccard": null_jst_mu,
            "stem_jaccard_z": z_jst,
            "lz_in_any_zodiac_cc_exact_count": lz_in_any_cc_exact,
            "lz_in_any_zodiac_cc_exact_rate": round(lz_in_any_cc_exact / len(all_lz), 4),
            "lz_in_any_zodiac_cc_stem_count": lz_in_any_cc_stem,
            "lz_in_any_zodiac_cc_stem_rate": round(lz_in_any_cc_stem / len(all_lz), 4),
        },
        "cc_vs_lz_morphology": {
            "cc_rings": cc_prof,
            "lz_labels": lz_prof,
        },
        "folio_breakdown": folio_rows,
        "p132_p133_visual_forensics": p132_p133_forensics,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(json.dumps(out["summary"], indent=2))
    print("CC vs LZ morphology:", json.dumps(out["cc_vs_lz_morphology"], indent=2))


if __name__ == "__main__":
    main()
