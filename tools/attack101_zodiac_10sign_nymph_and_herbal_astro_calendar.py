#!/usr/bin/env python3
"""
Attack 101 (Discovery 118): The 12-Medallion Zodiac (`f70v2–f73v`) Astro-Botanical Calendar —
Light-vs.-Dark Split-Medallion Polarity (`Aries f70v1/f71r` & `Taurus f71v/f72r1`),
Consecutive Zodiac Wheel Continuity, and Zodiac-to-Herbal Monograph Correspondences

Tests:
1. Parses all `12` Zodiac medallions (`f70v2 Pisces`, `f70v1 Aries-Dark`, `f71r Aries-Light`,
   `f71v Taurus-Light`, `f72r1 Taurus-Dark`, `f72r2 Gemini`, `f72r3 Cancer`, `f72v3 Leo`,
   `f72v2 Virgo`, `f72v1 Libra`, `f73r Scorpio`, `f73v Sagittarius`), separating `@Lz/@Ls`
   nymph/star labels from `@Cc/@Ce` circular ring tokens.
2. Tests **Split-Sign Pair Coherence & Light/Dark Polarity (`Aries f70v1<->f71r` and `Taurus f71v<->f72r1`)**:
   - Do the two halves of the same split Zodiac sign (`Aries-Dark <-> Aries-Light` and `Taurus-Light <-> Taurus-Dark`)
     share higher canonical stem Jaccard than non-paired medallions?
   - What is the morphological difference between the `Dark-Half` (`f70v1, f72r1`) and `Light-Half` (`f71r, f71v`)
     medallions (`o-` vs. `y-/d-` vs. `-dy` vs. `-ar/-al`)?
3. Tests **Calendar-Wheel Adjacency Continuity**:
   - Does the astronomical calendar order (`Pisces -> Aries -> Taurus -> Gemini -> Cancer -> Leo -> Virgo -> Libra -> Scorpio -> Sagittarius`)
     exhibit higher adjacent-medallion canonical stem Jaccard than random permutations of the 12 medallions?
4. Reconstructs the **12-Medallion Astro-Botanical Herbal Correspondence Table (`Zodiac Medallion <-> Herbal Monograph $I=H`)**:
   - For each of the `12` Zodiac medallions, identifies the top-matching Herbal Monograph folios (`$I=H`)
     by IDF-weighted open-class canonical stem overlap and tests significance via 500-trial permutation.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ZL_PATH = DATA_DIR / "ZL3b-n.txt"
OUT_JSON = DATA_DIR / "attack101_zodiac_10sign_nymph_and_herbal_astro_calendar.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

ZODIAC_ORDER = [
    ("f70v2", "01_PISCES_MAR", "FULL_30"),
    ("f70v1", "02A_ARIES_DARK_APR1", "SPLIT_DARK_15"),
    ("f71r", "02B_ARIES_LIGHT_APR2", "SPLIT_LIGHT_15"),
    ("f71v", "03A_TAURUS_LIGHT_MAY1", "SPLIT_LIGHT_15"),
    ("f72r1", "03B_TAURUS_DARK_MAY2", "SPLIT_DARK_15"),
    ("f72r2", "04_GEMINI_JUN", "FULL_30"),
    ("f72r3", "05_CANCER_JUL", "FULL_30"),
    ("f72v3", "06_LEO_AUG", "FULL_30"),
    ("f72v2", "07_VIRGO_SEP", "FULL_30"),
    ("f72v1", "08_LIBRA_OCT", "FULL_30"),
    ("f73r", "09_SCORPIO_NOV", "FULL_30"),
    ("f73v", "10_SAGITTARIUS_DEC", "FULL_30"),
]


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    out = []
    for c in s.replace(".", " ").split():
        w = re.sub(r"[^a-zA-Z]", "", c).lower()
        if w:
            out.append(w)
    return out


def canonical_stem(w: str) -> str:
    s = w
    if s.startswith("qo") and len(s) > 3:
        s = "o" + s[2:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = s.replace("cph", "cth").replace("cfh", "ckh")
    s = s.replace("p", "t").replace("f", "k")
    s = s.replace("sh", "ch")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    if s.endswith("edy") and len(s) >= 4:
        s = s[:-3] + "dy"
    elif s.endswith("ody") and len(s) >= 4:
        s = s[:-3] + "dy"
    return s


def jaccard(s1: set, s2: set) -> float:
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}
    folio_meta = {}
    folio_all_tokens = defaultdict(list)
    folio_label_tokens = defaultdict(list)
    folio_ring_tokens = defaultdict(list)
    all_word_counts = Counter()

    for raw_line in raw_lines:
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        mf = FOLIO_META_RE.match(raw_s)
        if mf:
            cur_folio = "f" + mf.group(1)
            meta_str = mf.group(2)
            cur_meta = {}
            for kv in meta_str.split():
                if "=" in kv:
                    k, v = kv.lstrip("$").split("=", 1)
                    cur_meta[k] = v
            folio_meta[cur_folio] = cur_meta
            continue
        ml = LOCUS_RE.match(raw_s)
        if ml and cur_folio:
            ltype, text = ml.group(3), ml.group(4)
            toks = clean_tokens(text)
            if not toks:
                continue
            for w in toks:
                all_word_counts[w] += 1
            folio_all_tokens[cur_folio].extend(toks)
            lt = ltype.lstrip("@+*=")
            if lt.startswith("L"):
                folio_label_tokens[cur_folio].extend(toks)
            elif lt.startswith(("C", "R")):
                folio_ring_tokens[cur_folio].extend(toks)

    canon_counts = Counter()
    for w, c in all_word_counts.items():
        cs = canonical_stem(w)
        if len(cs) >= 3:
            canon_counts[cs] += c
    top35_closed = {cs for cs, _ in canon_counts.most_common(35)}

    def get_open_stems(tokens):
        return {canonical_stem(w) for w in tokens if len(w) >= 3 and canonical_stem(w) not in top35_closed}

    def get_all_stems(tokens):
        return {canonical_stem(w) for w in tokens if len(w) >= 2}

    # 1. Profile all 12 Zodiac Medallions
    medallion_profiles = []
    medallion_stems = {}
    medallion_open_stems = {}

    for f, sign_name, mtype in ZODIAC_ORDER:
        toks = folio_all_tokens[f]
        ltoks = folio_label_tokens[f]
        rtoks = folio_ring_tokens[f]
        n = len(toks) or 1
        st = get_all_stems(toks)
        ost = get_open_stems(toks)
        medallion_stems[f] = st
        medallion_open_stems[f] = ost

        o_pct = 100.0 * sum(1 for w in toks if w.startswith("o") and not w.startswith("qo")) / n
        y_pct = 100.0 * sum(1 for w in toks if w.startswith("y")) / n
        d_pct = 100.0 * sum(1 for w in toks if w.startswith("d")) / n
        dy_pct = 100.0 * sum(1 for w in toks if w.endswith("dy")) / n
        ar_al_pct = 100.0 * sum(1 for w in toks if w.endswith(("ar", "al", "or", "ol"))) / n
        aiin_pct = 100.0 * sum(1 for w in toks if w.endswith(("aiin", "ain", "iin"))) / n

        medallion_profiles.append({
            "folio": f,
            "zodiac_sign": sign_name,
            "medallion_type": mtype,
            "total_tokens": len(toks),
            "nymph_label_tokens": len(ltoks),
            "ring_tokens": len(rtoks),
            "distinct_stems": len(st),
            "o_onset_pct": round(o_pct, 2),
            "y_onset_pct": round(y_pct, 2),
            "d_onset_pct": round(d_pct, 2),
            "dy_coda_pct": round(dy_pct, 2),
            "liquid_coda_pct": round(ar_al_pct, 2),
            "aiin_coda_pct": round(aiin_pct, 2),
        })

    # 2. Test Split-Sign Pair Coherence (Aries f70v1<->f71r and Taurus f71v<->f72r1) & Calendar Wheel Adjacency
    zod_folios = [f for f, _, _ in ZODIAC_ORDER]
    aries_jaccard = jaccard(medallion_stems["f70v1"], medallion_stems["f71r"])
    taurus_jaccard = jaccard(medallion_stems["f71v"], medallion_stems["f72r1"])
    split_pair_mean = 0.5 * (aries_jaccard + taurus_jaccard)

    adj_jaccards = [jaccard(medallion_stems[zod_folios[i]], medallion_stems[zod_folios[i + 1]]) for i in range(len(zod_folios) - 1)]
    obs_adj_mean = sum(adj_jaccards) / len(adj_jaccards)

    all_non_adj = []
    for i in range(len(zod_folios)):
        for j in range(i + 2, len(zod_folios)):
            all_non_adj.append(jaccard(medallion_stems[zod_folios[i]], medallion_stems[zod_folios[j]]))
    non_adj_mean = sum(all_non_adj) / len(all_non_adj)

    rng = random.Random(101)
    null_adj_means = []
    for _ in range(1000):
        perm = list(zod_folios)
        rng.shuffle(perm)
        null_adj_means.append(sum(jaccard(medallion_stems[perm[i]], medallion_stems[perm[i + 1]]) for i in range(len(perm) - 1)) / (len(perm) - 1))
    null_adj_mu = sum(null_adj_means) / len(null_adj_means)
    null_adj_sd = math.sqrt(sum((x - null_adj_mu) ** 2 for x in null_adj_means) / len(null_adj_means)) or 1e-9
    z_calendar_adj = (obs_adj_mean - null_adj_mu) / null_adj_sd

    # Compare Dark Split Medallions (f70v1, f72r1) vs Light Split Medallions (f71r, f71v)
    dark_toks = folio_all_tokens["f70v1"] + folio_all_tokens["f72r1"]
    light_toks = folio_all_tokens["f71r"] + folio_all_tokens["f71v"]
    nd, nl = len(dark_toks) or 1, len(light_toks) or 1
    split_light_dark_contrast = {
        "dark_medallions_f70v1_f72r1": {
            "n_tokens": len(dark_toks),
            "o_onset_pct": round(100.0 * sum(1 for w in dark_toks if w.startswith("o")) / nd, 2),
            "y_onset_pct": round(100.0 * sum(1 for w in dark_toks if w.startswith("y")) / nd, 2),
            "ch_sh_onset_pct": round(100.0 * sum(1 for w in dark_toks if w.startswith(("ch", "sh"))) / nd, 2),
            "dy_coda_pct": round(100.0 * sum(1 for w in dark_toks if w.endswith("dy")) / nd, 2),
            "aiin_coda_pct": round(100.0 * sum(1 for w in dark_toks if w.endswith(("aiin", "ain", "iin"))) / nd, 2),
        },
        "light_medallions_f71r_f71v": {
            "n_tokens": len(light_toks),
            "o_onset_pct": round(100.0 * sum(1 for w in light_toks if w.startswith("o")) / nl, 2),
            "y_onset_pct": round(100.0 * sum(1 for w in light_toks if w.startswith("y")) / nl, 2),
            "ch_sh_onset_pct": round(100.0 * sum(1 for w in light_toks if w.startswith(("ch", "sh"))) / nl, 2),
            "dy_coda_pct": round(100.0 * sum(1 for w in light_toks if w.endswith("dy")) / nl, 2),
            "aiin_coda_pct": round(100.0 * sum(1 for w in light_toks if w.endswith(("aiin", "ain", "iin"))) / nl, 2),
        },
    }

    # 3. Astro-Botanical Correspondence Table: Match each of the 12 Zodiac Medallions to Top Herbal Monographs ($I=H)
    h_folios = {}
    for f, meta in folio_meta.items():
        if meta.get("I") == "H" and len(folio_all_tokens[f]) >= 30:
            h_folios[f] = {
                "folio": f,
                "lang": meta.get("L", "U"),
                "open_stems": get_open_stems(folio_all_tokens[f]),
                "tokens": folio_all_tokens[f],
            }

    all_doc_sets = list(medallion_open_stems.values()) + [u["open_stems"] for u in h_folios.values()]
    n_docs = len(all_doc_sets)
    df = Counter(cs for s in all_doc_sets for cs in s)
    idf = {cs: math.log((n_docs + 1.0) / (c + 0.5)) for cs, c in df.items()}

    astro_botanical_table = []
    obs_max_idfs = []
    for f, sign_name, mtype in ZODIAC_ORDER:
        zst = medallion_open_stems[f]
        ztoks = folio_all_tokens[f]
        lbl_stems = get_open_stems(folio_label_tokens[f])
        scored_h = []
        for hf, hrec in h_folios.items():
            inter = zst & hrec["open_stems"]
            if not inter:
                continue
            sc = sum(idf[cs] for cs in inter)
            lbl_inter = sorted(inter & lbl_stems)
            scored_h.append((sc, len(inter), hf, hrec["lang"], sorted(inter, key=lambda x: -idf[x]), lbl_inter))
        scored_h.sort(reverse=True)
        best = scored_h[0]
        obs_max_idfs.append(best[0])
        # Build concrete surface pairs for top 5 shared stems
        surf_pairs = []
        for cs in best[4][:5]:
            zw = [w for w in ztoks if canonical_stem(w) == cs][0]
            hw = [w for w in h_folios[best[2]]["tokens"] if canonical_stem(w) == cs][0]
            surf_pairs.append(f"{cs}: Z({zw}{'*Lz' if cs in lbl_stems else ''}) <-> H({hw})")
        astro_botanical_table.append({
            "zodiac_folio": f,
            "zodiac_sign": sign_name,
            "top_herbal_folio": best[2],
            "herbal_lang": best[3],
            "runner_up_herbal_folios": [f"{x[2]}({round(x[0],1)})" for x in scored_h[1:4]],
            "shared_open_stems_count": best[1],
            "nymph_label_anchored_count": len(best[5]),
            "idf_overlap_score": round(best[0], 2),
            "shared_stems_with_surface_forms": surf_pairs,
        })

    obs_mean_max_idf = sum(obs_max_idfs) / len(obs_max_idfs)

    # Permutation Null Test (300 trials): shuffle open-class stems across Zodiac medallions and Herbal folios
    z_pool = [cs for s in medallion_open_stems.values() for cs in s]
    h_pool = [cs for u in h_folios.values() for cs in u["open_stems"]]
    null_max_idf_means = []
    for _ in range(300):
        rng.shuffle(z_pool)
        rng.shuffle(h_pool)
        idx = 0
        sim_z = []
        for s in medallion_open_stems.values():
            k = len(s)
            sim_z.append(set(z_pool[idx:idx + k]))
            idx += k
        idx = 0
        sim_h = []
        for u in h_folios.values():
            k = len(u["open_stems"])
            sim_h.append(set(h_pool[idx:idx + k]))
            idx += k
        max_scores = []
        for zs in sim_z:
            best_sc = max((sum(idf[cs] for cs in (zs & hs)) for hs in sim_h), default=0.0)
            max_scores.append(best_sc)
        null_max_idf_means.append(sum(max_scores) / len(max_scores))

    null_idf_mu = sum(null_max_idf_means) / len(null_max_idf_means)
    null_idf_sd = math.sqrt(sum((x - null_idf_mu) ** 2 for x in null_max_idf_means) / len(null_max_idf_means)) or 1e-9
    z_astro_botanical = (obs_mean_max_idf - null_idf_mu) / null_idf_sd

    out = {
        "calendar_wheel_continuity": {
            "aries_split_pair_f70v1_f71r_jaccard": round(aries_jaccard, 4),
            "taurus_split_pair_f71v_f72r1_jaccard": round(taurus_jaccard, 4),
            "split_pair_mean_jaccard": round(split_pair_mean, 4),
            "calendar_adjacent_11pairs_mean_jaccard": round(obs_adj_mean, 4),
            "non_adjacent_pairs_mean_jaccard": round(non_adj_mean, 4),
            "adjacent_vs_non_adjacent_lift_pct": round(100.0 * (obs_adj_mean - non_adj_mean) / (non_adj_mean or 1e-9), 2),
            "null_permuted_wheel_mean_jaccard": round(null_adj_mu, 4),
            "null_permuted_wheel_std": round(null_adj_sd, 4),
            "z_calendar_adjacency": round(z_calendar_adj, 2),
        },
        "split_medallion_light_vs_dark_contrast": split_light_dark_contrast,
        "astro_botanical_validation": {
            "observed_mean_max_idf_across_12_medallions": round(obs_mean_max_idf, 3),
            "null_mean_max_idf": round(null_idf_mu, 3),
            "null_std_max_idf": round(null_idf_sd, 3),
            "z_score": round(z_astro_botanical, 2),
        },
        "twelve_medallion_profiles": medallion_profiles,
        "twelve_medallion_astro_botanical_correspondences": astro_botanical_table,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Calendar Wheel Continuity:", json.dumps(out["calendar_wheel_continuity"], indent=2))
    print("Split Light vs Dark Contrast:", json.dumps(split_light_dark_contrast, indent=2))
    print("Astro-Botanical Validation:", json.dumps(out["astro_botanical_validation"], indent=2))
    for row in astro_botanical_table[:6]:
        print(f"  {row['zodiac_folio']} ({row['zodiac_sign']}) -> {row['top_herbal_folio']} ({row['herbal_lang']}, IDF={row['idf_overlap_score']}, shared={row['shared_open_stems_count']}): {row['shared_stems_with_surface_forms'][:3]}")


if __name__ == "__main__":
    main()
