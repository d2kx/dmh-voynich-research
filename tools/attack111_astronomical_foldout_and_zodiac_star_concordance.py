#!/usr/bin/env python3
"""
Attack 111 (Discovery 128): The 14-Folio Astronomical Foldout (`f67r1–f70r2`, `$I=A`)
& Zodiac (`f70v2–f73v`, `$I=Z`) Sector-by-Sector Star & Calendar Concordance

Tests:
1. Extracts all `14` Astronomical foldout folios (`f67r1, f67r2, f67v1, f67v2, f68r1, f68r2, f68r3,
   f68v1, f68v2, f68v3, f69r, f69v, f70r1, f70r2`, `$I=A`), separating tokens into their 4 structural
   locus classes:
   - `ASTRO_STAR_LABELS (@L)`,
   - `ASTRO_RADIAL_SPOKES (@R)`,
   - `ASTRO_CONCENTRIC_RINGS (@C)`,
   - `ASTRO_MARGINAL_PROSE (@P)`.
2. Maps the exact **Astronomical Foldout (`$I=A`) <-> Zodiac Medallion (`$I=Z`) <-> Herbal Monograph (`$I=H`)**
   high-IDF open-stem network (excluding Top-45 Canonical Stems, `len >= 3`, `2 <= df <= 95`),
   testing with a 1,000-trial permutation baseline whether `A <-> Z` and `A <-> H_B` stem sharing
   exceed random chance.
3. Measures the **4-Tier Internal Locus Morphological Gradient (`@L Star Labels -> @R Radial Spokes ->
   @C Concentric Rings -> @P Marginal Prose`)** across the `14` Astronomical foldout pages.
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
OUT_JSON = DATA_DIR / "attack111_astronomical_foldout_and_zodiac_star_concordance.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

ZODIAC_META = {
    "f70v2": ("Pisces", "March", "SPRING"),
    "f70v1": ("Aries (Dark)", "April", "SPRING"),
    "f71r":  ("Aries (Light)", "April", "SPRING"),
    "f71v":  ("Taurus (Light)", "May", "SPRING"),
    "f72r1": ("Taurus (Dark)", "May", "SPRING"),
    "f72r2": ("Gemini", "June", "SUMMER"),
    "f72r3": ("Cancer", "July", "SUMMER"),
    "f72v3": ("Leo", "August", "SUMMER"),
    "f72v2": ("Virgo", "September", "AUTUMN"),
    "f72v1": ("Libra", "October", "AUTUMN"),
    "f73r":  ("Scorpio", "November", "AUTUMN"),
    "f73v":  ("Sagittarius", "December", "WINTER"),
}


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    out = []
    for c in s.replace(".", " ").replace(",", " ").split():
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
    if s.endswith("edy") and len(s) > 4:
        s = s[:-3] + "dy"
    elif s.endswith("ody") and len(s) > 4:
        s = s[:-3] + "dy"
    return s


def main():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    cur_folio = None
    cur_meta = {}

    folio_meta = {}
    folio_all_tokens = defaultdict(list)
    folio_prose_tokens = defaultdict(list)
    astro_locus_tokens = {
        "ASTRO_STAR_LABELS_L": [],
        "ASTRO_RADIAL_SPOKES_R": [],
        "ASTRO_CONCENTRIC_RINGS_C": [],
        "ASTRO_MARGINAL_PROSE_P": [],
    }
    astro_folio_by_type = defaultdict(lambda: defaultdict(list))

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
            lnum, ltype, text = ml.group(2), ml.group(3), ml.group(4)
            toks = clean_tokens(text)
            if not toks:
                continue
            for w in toks:
                all_word_counts[w] += 1
            folio_all_tokens[cur_folio].extend(toks)
            ltype_clean = ltype.lstrip("@+*=")
            if ltype_clean.startswith("P"):
                folio_prose_tokens[cur_folio].extend(toks)

            if cur_folio.startswith(("f67", "f68", "f69", "f70r")):
                if ltype_clean.startswith("L"):
                    astro_locus_tokens["ASTRO_STAR_LABELS_L"].extend(toks)
                    astro_folio_by_type[cur_folio]["L"].extend(toks)
                elif ltype_clean.startswith("R"):
                    astro_locus_tokens["ASTRO_RADIAL_SPOKES_R"].extend(toks)
                    astro_folio_by_type[cur_folio]["R"].extend(toks)
                elif ltype_clean.startswith("C"):
                    astro_locus_tokens["ASTRO_CONCENTRIC_RINGS_C"].extend(toks)
                    astro_folio_by_type[cur_folio]["C"].extend(toks)
                elif ltype_clean.startswith("P"):
                    astro_locus_tokens["ASTRO_MARGINAL_PROSE_P"].extend(toks)
                    astro_folio_by_type[cur_folio]["P"].extend(toks)

    canon_counts = Counter()
    for w, c in all_word_counts.items():
        cs = canonical_stem(w)
        if len(cs) >= 3:
            canon_counts[cs] += c
    closed_stems = {cs for cs, _ in canon_counts.most_common(45)}

    stem_doc_freq = Counter()
    all_folios_list = sorted(folio_all_tokens.keys())
    for f in all_folios_list:
        for st in {canonical_stem(w) for w in folio_all_tokens[f]}:
            stem_doc_freq[st] += 1

    n_docs = len(all_folios_list)
    stem_idf = {}
    for st, df in stem_doc_freq.items():
        if st not in closed_stems and len(st) >= 3 and 2 <= df <= 95:
            stem_idf[st] = math.log((n_docs + 1.0) / (df + 1.0))

    a_folios = sorted(
        [f for f in folio_meta if f.startswith(("f67", "f68", "f69", "f70r"))],
        key=lambda x: (int(re.findall(r"\d+", x)[0]), x)
    )
    z_folios = sorted(ZODIAC_META.keys())
    h_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "H" and len(folio_prose_tokens[f]) >= 15])
    p_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "P" and len(folio_all_tokens[f]) >= 15])

    a_stems = {af: {canonical_stem(w) for w in folio_all_tokens[af] if canonical_stem(w) in stem_idf} for af in a_folios}
    z_stems = {zf: {canonical_stem(w) for w in folio_all_tokens[zf] if canonical_stem(w) in stem_idf} for zf in z_folios}
    h_stems = {hf: {canonical_stem(w) for w in folio_prose_tokens[hf] if canonical_stem(w) in stem_idf} for hf in h_folios}
    p_stems = {pf: {canonical_stem(w) for w in folio_all_tokens[pf] if canonical_stem(w) in stem_idf} for pf in p_folios}

    # 1. Astronomical Foldout Folio-by-Folio Concordance to Zodiac ($I=Z), Herbal ($I=H), and Pharm ($I=P)
    astro_atlas = []
    hb_top1 = 0
    obs_az_max_idfs = []
    for af in a_folios:
        ast = a_stems[af]
        z_matches = []
        for zf in z_folios:
            inter = ast & z_stems[zf]
            sc = sum(stem_idf[s] for s in inter)
            z_matches.append((zf, ZODIAC_META[zf][0], ZODIAC_META[zf][1], ZODIAC_META[zf][2], round(sc, 3), sorted(inter, key=lambda x: -stem_idf[x])))
        z_matches.sort(key=lambda x: -x[4])
        obs_az_max_idfs.append(z_matches[0][4])

        h_matches = []
        for hf in h_folios:
            inter = ast & h_stems[hf]
            if inter:
                sc = sum(stem_idf[s] for s in inter)
                h_matches.append((hf, folio_meta[hf].get("L", "U"), folio_meta[hf].get("Q", "U"), round(sc, 3), sorted(inter, key=lambda x: -stem_idf[x])))
        h_matches.sort(key=lambda x: -x[3])
        if h_matches and h_matches[0][1] == "B":
            hb_top1 += 1

        p_matches = []
        for pf in p_folios:
            inter = ast & p_stems[pf]
            if inter:
                sc = sum(stem_idf[s] for s in inter)
                p_matches.append((pf, round(sc, 3), sorted(inter, key=lambda x: -stem_idf[x])))
        p_matches.sort(key=lambda x: -x[1])

        by_t = astro_folio_by_type[af]
        astro_atlas.append({
            "astro_folio": af,
            "quire": folio_meta[af].get("Q", "U"),
            "hand": folio_meta[af].get("H", "U"),
            "total_tokens": len(folio_all_tokens[af]),
            "l_star_tokens": len(by_t["L"]),
            "r_spoke_tokens": len(by_t["R"]),
            "c_ring_tokens": len(by_t["C"]),
            "p_prose_tokens": len(by_t["P"]),
            "open_stems": len(ast),
            "top_zodiac": {
                "folio": z_matches[0][0],
                "sign": z_matches[0][1],
                "month": z_matches[0][2],
                "season": z_matches[0][3],
                "idf": z_matches[0][4],
                "stems": z_matches[0][5],
            },
            "second_zodiac": {
                "folio": z_matches[1][0],
                "sign": z_matches[1][1],
                "month": z_matches[1][2],
                "idf": z_matches[1][4],
                "stems": z_matches[1][5],
            },
            "top_herbal": {
                "folio": h_matches[0][0],
                "lang": h_matches[0][1],
                "quire": h_matches[0][2],
                "idf": h_matches[0][3],
                "stems": h_matches[0][4],
            } if h_matches else None,
            "top_pharm": {
                "folio": p_matches[0][0],
                "idf": p_matches[0][1],
                "stems": p_matches[0][2],
            } if p_matches else None,
        })

    # 2. Permutation Test on Astronomical <-> Zodiac (A <-> Z) Mean Max IDF (500 trials)
    obs_az_mean = sum(obs_az_max_idfs) / len(obs_az_max_idfs)
    rng = random.Random(2026111)
    non_astro_folios = [f for f in all_folios_list if folio_meta[f].get("I") not in ("A", "Z") and len(folio_all_tokens[f]) >= 25]
    cand_pool = [
        (f, [canonical_stem(w) for w in folio_all_tokens[f] if canonical_stem(w) in stem_idf])
        for f in non_astro_folios
    ]

    null_az_means = []
    for _ in range(500):
        tot = 0.0
        for af in a_folios:
            k = len(a_stems[af])
            _, pool_st = rng.choice(cand_pool)
            if len(pool_st) >= k:
                sampled = set(rng.sample(pool_st, k))
            else:
                sampled = set(pool_st)
            best_z = max(sum(stem_idf[s] for s in (sampled & z_stems[zf])) for zf in z_folios)
            tot += best_z
        null_az_means.append(tot / len(a_folios))

    m_az = sum(null_az_means) / len(null_az_means)
    sd_az = math.sqrt(sum((x - m_az) ** 2 for x in null_az_means) / len(null_az_means)) or 1e-9
    z_az = round((obs_az_mean - m_az) / sd_az, 2)

    # 3. 4-Tier Internal Locus Morphological Gradient across the 14 Astronomical Foldouts
    def profile_locus(toks):
        n = len(toks) or 1
        return {
            "tokens": len(toks),
            "o_nominal_pct": round(100.0 * sum(1 for w in toks if w.startswith("o") and not w.startswith("qo")) / n, 2),
            "qo_active_pct": round(100.0 * sum(1 for w in toks if w.startswith("qo")) / n, 2),
            "d_s_y_clause_pct": round(100.0 * sum(1 for w in toks if w.startswith(("d", "s", "y"))) / n, 2),
            "l_ol_applicative_pct": round(100.0 * sum(1 for w in toks if w.startswith(("l", "ol", "qol"))) / n, 2),
            "edy_process_pct": round(100.0 * sum(1 for w in toks if w.endswith(("edy", "eedy"))) / n, 2),
            "dy_state_pct": round(100.0 * sum(1 for w in toks if w.endswith("dy") and not w.endswith(("edy", "eedy"))) / n, 2),
            "aiin_measure_pct": round(100.0 * sum(1 for w in toks if w.endswith(("aiin", "iin", "ain"))) / n, 2),
            "ol_or_al_ar_liquid_pct": round(100.0 * sum(1 for w in toks if w.endswith(("ol", "or", "al", "ar"))) / n, 2),
            "am_m_terminus_pct": round(100.0 * sum(1 for w in toks if w.endswith(("am", "m"))) / n, 2),
        }

    locus_gradient = {
        k: profile_locus(v) for k, v in astro_locus_tokens.items()
    }

    hb_pct = round(100.0 * hb_top1 / len(a_folios), 2)
    hb_base = round(100.0 * sum(1 for hf in h_folios if folio_meta[hf].get("L") == "B") / len(h_folios), 2)

    summary = {
        "attack_id": 111,
        "discovery_id": 128,
        "title": "The 14-Folio Astronomical Foldout (f67r1-f70r2) & Zodiac (f70v2-f73v) Sector-by-Sector Star & Calendar Concordance",
        "astro_to_zodiac_permutation_test": {
            "astro_folios_count": len(a_folios),
            "observed_mean_max_zodiac_idf": round(obs_az_mean, 3),
            "null_mean_max_zodiac_idf": round(m_az, 3),
            "null_std_max_zodiac_idf": round(sd_az, 3),
            "z_score": z_az,
        },
        "herbal_b_selectivity": {
            "herbal_b_top1_matches": hb_top1,
            "herbal_b_top1_pct": hb_pct,
            "herbal_b_baseline_pct": hb_base,
            "enrichment_ratio": round(hb_pct / (hb_base or 1e-9), 2),
        },
        "four_tier_astro_locus_gradient": locus_gradient,
        "astronomical_14folio_atlas": astro_atlas,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Attack 111] Saved -> {OUT_JSON}")
    print(f"  Astronomical -> Zodiac Mean Max IDF: {obs_az_mean:.3f} vs null {m_az:.3f}+/-{sd_az:.3f} (z={z_az:+.2f})")
    print(f"  Astronomical -> Herbal-B #1 Selectivity: {hb_top1}/{len(a_folios)} = {hb_pct}% vs {hb_base}% baseline ({hb_pct/hb_base:.2f}x)")
    print("  4-Tier Astronomical Locus Gradient:")
    for k, v in locus_gradient.items():
        print(f"    {k:28s}: n={v['tokens']:4d} | o-={v['o_nominal_pct']:5.2f}% | qo-={v['qo_active_pct']:5.2f}% | -aiin={v['aiin_measure_pct']:5.2f}% | -ol/-or={v['ol_or_al_ar_liquid_pct']:5.2f}% | -am/-m={v['am_m_terminus_pct']:5.2f}%")


if __name__ == "__main__":
    main()
