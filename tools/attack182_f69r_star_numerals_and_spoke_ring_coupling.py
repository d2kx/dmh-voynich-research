#!/usr/bin/env python3
"""
Attack 182 (Discovery 199): Visual & Paleographic Forensics of f69r (22-Spoke 3-Color
Organ-Pipe Wheel & Central Star Numerals), Adjacent-Spoke Alliteration Law, and
Multi-Locus Wheel Architecture (`@C`, `@R`, `@L`, `@P`).

Investigates:
1. Complete paleographic & structural anatomy of `f69r` (`pages/f69r_swirling_spoke_wheel_enh.png`):
   - 4-line introductory header paragraph (`@P0`, `36` words)
   - 17 outer perimeter sector labels (`@Ls / +Ls`, `36` words)
   - 22 radial "organ pipe" spoke inscriptions (`@Ro / +Ro`, `66` words, mean `3.00` words/spoke)
     with 3-color periodic alternation (Blue -> White -> Green) plus 1 cross-hatched start-indicator
     spoke at 02:00 (`f69r.22,@Ro`)
   - 1 inner circular ring (`@Cc`, `9` words) surrounding the 6-pointed star with 6 Arabic numerals
     (`8, 9, 2, 3, 6, 9` / ThP numbering) between the star rays.
2. Same-wheel Spoke (`@R`) <-> Ring/Sector/Para (`@C + @L + @P`) canonical stem and exact word
   coupling across all wheel folios, plus the **Adjacent-Spoke (`S_i` <-> `S_{i+1}`) Prefix &
   Morphological Parallelism Law** tested against 1,000 random spoke permutations.
3. Strict 3-tier structural length & inflection hierarchy on Astronomical wheels:
   Outer/Inner Rings (`@C`: `26.86` words/locus) -> Header Paragraphs (`@P`: `8.85` words/line) ->
   Radial Spokes (`@R`: `2.65` words/spoke) -> Sector/Star Labels (`@L`: `1.47` words/label).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

random.seed(42)


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[\[\]<>@*$?!%'0-9]", "", t)
    return t.strip()


def canonical_stem(w: str) -> str:
    s = w
    s = re.sub(r"ch", "C", s)
    s = re.sub(r"sh", "S", s)
    s = re.sub(r"ii+", "i", s)
    s = re.sub(r"ee+", "e", s)
    for pref in ("qo", "ok", "ot", "op", "of", "ol", "or", "da", "so", "yk", "yt", "yp"):
        if s.startswith(pref) and len(s) - len(pref) >= 2:
            s = s[len(pref):]
            break
    for suf in ("aiin", "oiin", "eiin", "iin", "edy", "eey", "ody", "am", "om", "al", "ar", "ol", "or", "dy", "ey", "in", "y", "m"):
        if s.endswith(suf) and len(s) - len(suf) >= 1:
            s = s[:-len(suf)]
            break
    s = s.replace("C", "ch").replace("S", "sh")
    return s


def main():
    zl_path = Path("data/ZL3b-n.txt")
    line_re = re.compile(r"^<(f(?:Ros|[0-9]+[rv][0-9]*))\.([^,>]+),([^>]+)>\s+(.*)$")
    folio_hdr_re = re.compile(r"^<(f(?:Ros|[0-9]+[rv][0-9]*))>")

    folio_comments = defaultdict(list)
    wheel_loci = defaultdict(lambda: {"C": [], "R": [], "P": [], "L": []})
    f69r_lines = []

    curr_folio = None
    for raw in zl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        mh = folio_hdr_re.match(raw)
        if mh:
            curr_folio = mh.group(1)
            continue
        if raw.startswith("#"):
            if curr_folio:
                folio_comments[curr_folio].append(raw.lstrip("# ").strip())
            continue
        m = line_re.match(raw)
        if not m:
            continue
        folio = m.group(1)
        lno = m.group(2)
        loc_raw = m.group(3).strip()
        loc_clean = loc_raw.lstrip("@+=*")
        body = m.group(4)

        clock_match = re.search(r"<!([^>]+)>", body)
        clock_pos = clock_match.group(1) if clock_match else ""

        body_clean = re.sub(r"<[^>]*>", " ", body)
        words = [clean_tok(w) for w in re.split(r"[.,\s]+", body_clean)]
        words = [w for w in words if w]
        if not words:
            continue

        cat = loc_clean[0] if loc_clean else "P"
        if cat in ("C", "R", "P", "L"):
            wheel_loci[folio][cat].append({
                "lno": lno,
                "loc": loc_raw,
                "loc_clean": loc_clean,
                "clock": clock_pos,
                "words": words,
                "word_count": len(words),
                "text": " ".join(words),
            })
        if folio == "f69r":
            f69r_lines.append({
                "lno": lno,
                "loc": loc_raw,
                "loc_clean": loc_clean,
                "clock": clock_pos,
                "words": words,
                "word_count": len(words),
                "text": " ".join(words),
            })

    # All folios that have @C or @R (18 circular/wheel folios)
    all_wheel_folios = sorted([f for f, d in wheel_loci.items() if d["C"] or d["R"]])
    r_folios = sorted([f for f, d in wheel_loci.items() if d["R"]])

    # 4-Tier Locus Architecture across all 18 Wheel Folios
    tier_stats = {}
    for cat, label in [
        ("C", "Concentric_Rings_@C"),
        ("P", "Header_Paragraph_Lines_@P"),
        ("R", "Radial_Spoke_Lines_@R"),
        ("L", "Sector_and_Star_Labels_@L"),
    ]:
        loci_list = [item for f in all_wheel_folios for item in wheel_loci[f][cat]]
        toks = [w for item in loci_list for w in item["words"]]
        ok_ot_cnt = sum(1 for w in toks if w.startswith(("ok", "ot", "op", "of")))
        qo_cnt = sum(1 for w in toks if w.startswith("qo"))
        aiin_ar_al_cnt = sum(1 for w in toks if w.endswith(("aiin", "iin", "ar", "al", "or", "ol")))
        edy_ey_cnt = sum(1 for w in toks if w.endswith(("edy", "dy", "eey", "ey")))
        tier_stats[cat] = {
            "category": label,
            "loci_count": len(loci_list),
            "total_words": len(toks),
            "unique_types": len(set(toks)),
            "mean_words_per_locus": round(len(toks) / max(1, len(loci_list)), 2),
            "type_token_ratio": round(len(set(toks)) / max(1, len(toks)), 4),
            "ok_ot_op_prefix_pct": round(100.0 * ok_ot_cnt / max(1, len(toks)), 2),
            "qo_prefix_pct": round(100.0 * qo_cnt / max(1, len(toks)), 2),
            "nominal_aiin_ar_al_pct": round(100.0 * aiin_ar_al_cnt / max(1, len(toks)), 2),
            "verbal_edy_ey_pct": round(100.0 * edy_ey_cnt / max(1, len(toks)), 2),
        }

    # Test Spoke (@R) <-> Same-Wheel Non-Spoke (@C + @L + @P) stem & exact coupling across r_folios
    spoke_words_by_folio = {}
    non_spoke_words_by_folio = {}
    for f in r_folios:
        spoke_words_by_folio[f] = [w for item in wheel_loci[f]["R"] for w in item["words"]]
        non_spoke_words_by_folio[f] = [
            w for cat in ("C", "L", "P") for item in wheel_loci[f][cat] for w in item["words"]
        ]

    # Compare @R word length distribution and `ok-/ot-` vs `d-/s-` initial grammar across the 11 radial wheel folios
    # Test within-wheel spoke homogeneity (do spokes on the same wheel share word-count, initial prefix, and suffix profile?)
    all_spokes = [(f, item) for f in r_folios for item in wheel_loci[f]["R"]]

    def spoke_similarity(s1, s2):
        w1, w2 = s1["words"], s2["words"]
        len_diff = abs(len(w1) - len(w2))
        inits1 = {w[0] for w in w1 if w}
        inits2 = {w[0] for w in w2 if w}
        init2_1 = {w[:2] for w in w1 if len(w) >= 2}
        init2_2 = {w[:2] for w in w2 if len(w) >= 2}
        stems1 = {canonical_stem(w) for w in w1 if len(w) >= 2}
        stems2 = {canonical_stem(w) for w in w2 if len(w) >= 2}
        return (
            1 if len_diff <= 1 else 0,
            1 if (init2_1 & init2_2) else 0,
            1 if (stems1 & stems2) else 0,
            len_diff,
        )

    adj_pairs = []
    for f in r_folios:
        sp = wheel_loci[f]["R"]
        if len(sp) >= 2:
            for i in range(len(sp)):
                adj_pairs.append((sp[i], sp[(i + 1) % len(sp)], f))

    obs_len_match = sum(spoke_similarity(a, b)[0] for a, b, _ in adj_pairs) / len(adj_pairs)
    obs_init2_match = sum(spoke_similarity(a, b)[1] for a, b, _ in adj_pairs) / len(adj_pairs)
    obs_stem_match = sum(spoke_similarity(a, b)[2] for a, b, _ in adj_pairs) / len(adj_pairs)
    obs_mean_len_diff = sum(spoke_similarity(a, b)[3] for a, b, _ in adj_pairs) / len(adj_pairs)

    # Compare against 1,000 random cross-wheel spoke pairs
    null_len_match, null_init2_match, null_stem_match, null_mean_len_diff = [], [], [], []
    spoke_only_list = [item for _, item in all_spokes]
    for _ in range(1000):
        shuf = spoke_only_list[:]
        random.shuffle(shuf)
        lm, im, sm, ld = 0, 0, 0, 0
        for i in range(len(adj_pairs)):
            a = shuf[i % len(shuf)]
            b = shuf[(i + 1) % len(shuf)]
            r0, r1, r2, r3 = spoke_similarity(a, b)
            lm += r0
            im += r1
            sm += r2
            ld += r3
        n = len(adj_pairs)
        null_len_match.append(100.0 * lm / n)
        null_init2_match.append(100.0 * im / n)
        null_stem_match.append(100.0 * sm / n)
        null_mean_len_diff.append(ld / n)

    def calc_z(obs, arr):
        m = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - m) ** 2 for x in arr) / len(arr)) or 1e-9
        return round(m, 2), round((obs - m) / sd, 2)

    null_lm_mean, z_lm = calc_z(100.0 * obs_len_match, null_len_match)
    null_im_mean, z_im = calc_z(100.0 * obs_init2_match, null_init2_match)
    null_sm_mean, z_sm = calc_z(100.0 * obs_stem_match, null_stem_match)
    null_ld_mean, z_ld = calc_z(obs_mean_len_diff, null_mean_len_diff)

    # Per-wheel breakdown across all 11 folios with @R spokes
    wheel_breakdown = []
    for f in r_folios:
        rw = spoke_words_by_folio[f]
        nsw = non_spoke_words_by_folio[f]
        ns_set = set(nsw)
        ns_stems = {canonical_stem(w) for w in nsw if len(w) >= 2}
        e_hits = [w for w in rw if w in ns_set]
        s_hits = [w for w in rw if canonical_stem(w) in ns_stems]
        wheel_breakdown.append({
            "folio": f,
            "ring_C_loci": len(wheel_loci[f]["C"]),
            "spoke_R_loci": len(wheel_loci[f]["R"]),
            "label_L_loci": len(wheel_loci[f]["L"]),
            "para_P_loci": len(wheel_loci[f]["P"]),
            "spoke_words": len(rw),
            "non_spoke_words": len(nsw),
            "mean_words_per_spoke": round(len(rw) / max(1, len(wheel_loci[f]["R"])), 2),
            "spoke_exact_match_in_wheel_pct": round(100.0 * len(e_hits) / max(1, len(rw)), 2),
            "spoke_stem_match_in_wheel_pct": round(100.0 * len(s_hits) / max(1, len(rw)), 2),
            "exact_matches_sample": sorted(set(e_hits))[:10],
        })

    out = {
        "attack": 182,
        "discovery": 199,
        "title": "Visual & Paleographic Forensics of f69r, 4-Tier Wheel Locus Hierarchy & Adjacent-Spoke Template Law",
        "f69r_forensics": {
            "comments_in_zl3b": [c for c in folio_comments["f69r"] if c],
            "central_star_arabic_numerals_note": "Six late-medieval Arabic digits (8, 9, 2, 3, 6, 9 / ThP numbering) inscribed in brown ink inside the bays between the 6 points of the central star.",
            "organ_pipe_spoke_colors_note": "22 radial organ-pipe spokes alternating in a 3-color cycle (Blue -> Unpainted/White -> Green), interrupted by 1 cross-hatched index spoke at 02:00 (f69r.22,@Ro: 'dar.doaiin.okal').",
            "header_paragraph_P0": [x for x in f69r_lines if x["loc_clean"].startswith("P")],
            "outer_perimeter_17_sectors_Ls": [x for x in f69r_lines if x["loc_clean"].startswith("L")],
            "radial_organ_pipes_22_Ro": [x for x in f69r_lines if x["loc_clean"].startswith("R")],
            "inner_ring_Cc": [x for x in f69r_lines if x["loc_clean"].startswith("C")],
            "total_lines": len(f69r_lines),
            "total_words": sum(x["word_count"] for x in f69r_lines),
        },
        "four_tier_wheel_locus_hierarchy": tier_stats,
        "adjacent_spoke_template_law": {
            "total_adjacent_spoke_pairs": len(adj_pairs),
            "spoke_length_match_within_1_word_pct": round(100.0 * obs_len_match, 2),
            "null_length_match_pct": null_lm_mean,
            "z_length_match": z_lm,
            "mean_word_count_diff_adjacent": round(obs_mean_len_diff, 2),
            "null_mean_word_count_diff": null_ld_mean,
            "z_word_count_diff": z_ld,
            "shared_initial_bigram_pct": round(100.0 * obs_init2_match, 2),
            "null_initial_bigram_pct": null_im_mean,
            "z_initial_bigram": z_im,
            "shared_canonical_stem_pct": round(100.0 * obs_stem_match, 2),
            "null_canonical_stem_pct": null_sm_mean,
            "z_canonical_stem": z_sm,
        },
        "wheel_breakdown": wheel_breakdown,
    }

    out_path = Path("data/attack182_f69r_star_numerals_and_spoke_ring_coupling.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print("4-Tier Hierarchy:")
    for k, v in tier_stats.items():
        print(f"  {k}: {v['loci_count']} loci, {v['total_words']} words, mean={v['mean_words_per_locus']} w/locus, "
              f"nominal={v['nominal_aiin_ar_al_pct']}%, verbal={v['verbal_edy_ey_pct']}%")
    print("Adjacent-Spoke Template Law:", json.dumps(out["adjacent_spoke_template_law"], indent=2))


if __name__ == "__main__":
    main()
