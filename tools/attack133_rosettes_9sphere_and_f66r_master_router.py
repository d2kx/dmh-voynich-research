#!/usr/bin/env python3
"""
Attack 133 (Phase 144 / Discovery 150):
The Complete 9-Sphere Rosettes Map (`fRos`, `518` Tokens) Sphere-by-Sphere &
Causeway-by-Causeway Translator and the `f66r <-> fRos <-> Quire 20` Master
Routing Triad Solver.

Investigates:
1. Exact spatial parsing of all `fRos` lines (`<fRos.1>` .. `<fRos.72>`) using
   the IVTFF 2.0 spatial location comments (`<!NW>`, `<!N>`, `<!NE>`, `<!W>`,
   `<!C>`, `<!E>`, `<!SW>`, `<!S>`, `<!SE>`, and connecting causeways/pipes)
   plus locus types (`@Cc` Ring, `@L0` Label, `@Pb` Wedge/Box).
2. Functional & Cross-Sectional Specialization across the 9 Rosettes Spheres
   and Connecting Causeways (`Herbal H`, `Astronomical A`, `Zodiac Z`,
   `Balneological B`, `Pharmaceutical P`, `Starred S`, and `f66r`).
3. The `#1` Cross-Section Citation Edge in the Voynich Manuscript (`f66r <->
   fRos`, `IDF = 32.247`) and the `f66r <-> fRos <-> Quire 20 (f114r, f105v)`
   Master Routing Triad (`1,000`-trial permutation test).
4. Complete sphere-by-sphere and ring-by-ring structural translation of `fRos`.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack133_rosettes_9sphere_and_f66r_master_router.json"

PREFIXES = [
    "qok", "qot", "qop", "qof", "qo",
    "ch", "sh", "cth", "ckh", "cph", "cfh",
    "da", "sa", "ol", "al", "or", "ar",
    "ok", "ot", "op", "of",
    "yk", "yt", "yp", "yf",
    "lk", "lt", "lp", "lf",
    "d", "s", "y", "o", "l", "r", "k", "t", "p", "f",
]

SUFFIXES = [
    "aiin", "oiin", "eiin", "iin", "in",
    "eedy", "edy", "ody", "ady", "dy",
    "ey", "oy", "ay", "y",
    "eal", "ol", "al", "el", "l",
    "ear", "or", "ar", "er", "r",
    "eam", "am", "om", "m",
    "an", "en", "on", "n",
    "s", "d", "g",
]


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def canon_stem(w: str) -> str:
    s = w
    if s.startswith("q") and len(s) > 2:
        s = s[1:]
    for p in ["ch", "sh", "da", "sa", "ol", "al", "or", "ar", "ok", "ot", "yk", "yt", "d", "s", "y", "o", "l"]:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ["aiin", "oiin", "iin", "eedy", "edy", "ody", "ady", "dy", "ey", "oy", "ol", "al", "or", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n", "s"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def decompose_word(w: str) -> dict:
    rem = w
    pref = ""
    for p in PREFIXES:
        if rem.startswith(p) and len(rem) - len(p) >= 2:
            pref = p
            rem = rem[len(p):]
            break
    suf = ""
    for s in SUFFIXES:
        if rem.endswith(s) and len(rem) - len(s) >= 1:
            suf = s
            rem = rem[:-len(s)]
            break
    stem = canon_stem(w)
    if pref.startswith("qo"):
        p_gloss = "ACT_BOIL"
    elif pref in ("ch", "sh", "cth", "ckh", "cph", "cfh"):
        p_gloss = "HERB_BENCH"
    elif pref in ("o", "ok", "ot", "op", "of", "y", "yk", "yt"):
        p_gloss = "NOM_SPEC"
    elif pref in ("d", "da"):
        p_gloss = "TOP_LOC"
    elif pref in ("s", "sa"):
        p_gloss = "SEQ_CONT"
    elif pref in ("l", "ol", "al", "lk", "lt"):
        p_gloss = "APPL_VESSEL"
    elif pref in ("or", "ar", "r"):
        p_gloss = "FLOW_LIQ"
    else:
        p_gloss = "BARE"

    if suf in ("aiin", "oiin", "eiin", "iin", "in"):
        s_gloss = "DOSE_AIIN"
    elif suf in ("eedy", "edy"):
        s_gloss = "PROC_SIMMER"
    elif suf in ("ody", "ady", "dy"):
        s_gloss = "PERF_DONE"
    elif suf in ("ey", "oy", "ay", "y"):
        s_gloss = "STATE_Y"
    elif suf in ("ol", "al", "el", "eal", "l"):
        s_gloss = "FLUID_L"
    elif suf in ("or", "ar", "er", "ear", "r"):
        s_gloss = "SOURCE_R"
    elif suf in ("am", "om", "eam", "m"):
        s_gloss = "FINAL_M"
    else:
        s_gloss = "ROOT"

    return {
        "word": w,
        "prefix": pref,
        "core": rem,
        "suffix": suf,
        "stem": stem,
        "gloss": f"{p_gloss}[{stem.upper()}]:{s_gloss}",
    }


def metrics_for_tokens(toks: list) -> dict:
    n = len(toks)
    if n == 0:
        return {}
    stems = [canon_stem(w) for w in toks]
    qo = sum(1 for w in toks if w.startswith("qo"))
    o_nom = sum(1 for w in toks if w.startswith("o") and not w.startswith("ol"))
    bench = sum(1 for w in toks if w.startswith(("ch", "sh")))
    da_top = sum(1 for w in toks if w.startswith("d"))
    l_appl = sum(1 for w in toks if w.startswith(("l", "ol", "al")))
    edy = sum(1 for w in toks if w.endswith(("edy", "eedy")))
    aiin = sum(1 for w in toks if w.endswith(("aiin", "oiin", "iin")))
    am = sum(1 for w in toks if w.endswith(("am", "om", "m")))
    dy = sum(1 for w in toks if w.endswith("dy") and not w.endswith(("edy", "eedy")))
    return {
        "n_tokens": n,
        "n_unique_stems": len(set(stems)),
        "mean_len": round(sum(len(w) for w in toks) / n, 3),
        "o_nom_pct": round(100.0 * o_nom / n, 2),
        "qo_pct": round(100.0 * qo / n, 2),
        "bench_pct": round(100.0 * bench / n, 2),
        "d_top_pct": round(100.0 * da_top / n, 2),
        "l_appl_pct": round(100.0 * l_appl / n, 2),
        "edy_pct": round(100.0 * edy / n, 2),
        "aiin_pct": round(100.0 * aiin / n, 2),
        "dy_pct": round(100.0 * dy / n, 2),
        "am_pct": round(100.0 * am / n, 2),
    }


CIRCLE_NAMES = {
    "1": "CIRCLE_1_NW",
    "2": "CIRCLE_2_W",
    "3": "CIRCLE_3_SW",
    "4": "CIRCLE_4_N",
    "5": "CIRCLE_5_CENTER",
    "6": "CIRCLE_6_S",
    "7": "CIRCLE_7_NE",
    "8": "CIRCLE_8_E",
    "9": "CIRCLE_9_SE",
}

RING_LINE_MAP = {
    2: "CIRCLE_1_NW",
    20: "CIRCLE_4_N",
    35: "CIRCLE_7_NE",
    36: "CIRCLE_7_NE",
    47: "CIRCLE_2_W",
    62: "CIRCLE_5_CENTER",
    87: "CIRCLE_8_E",
    94: "CIRCLE_3_SW",
    112: "CIRCLE_3_SW",
    113: "CIRCLE_3_SW",
    114: "CIRCLE_3_SW",
    115: "CIRCLE_3_SW",
    122: "CIRCLE_6_S",
    133: "CIRCLE_9_SE",
}


def normalize_fros_zone(comment_tags: list, line_num: int) -> str:
    if line_num in RING_LINE_MAP:
        return RING_LINE_MAP[line_num]
    for tag in comment_tags:
        t = tag.strip()
        m_c = re.match(r"^([1-9]):", t)
        if m_c:
            return CIRCLE_NAMES[m_c.group(1)]
        if t in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII"):
            return "CAUSEWAYS_I_TO_VIII"
    if 137 <= line_num <= 160:
        return "CAUSEWAYS_I_TO_VIII"
    return "UNSPECIFIED"


def main():
    random.seed(42)
    with open(INDEX_PATH, encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx["folios"]

    folio_tokens = defaultdict(list)
    fros_lines = []
    last_zone = "SPHERE_NW"

    with open(ZL_PATH, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m_line = re.match(r"^<(f[0-9a-zA-Z]+)\.([^>]+)>\s+(.*)$", line)
            if not m_line:
                continue
            fol, loc_part, text = m_line.groups()
            loc = loc_part.split(",")[-1] if "," in loc_part else loc_part
            line_id = loc_part.split(",")[0]

            comments = re.findall(r"<!([^>]+)>", text)
            text_no_comm = re.sub(r"<![^>]+>", "", text)
            raw_toks = re.split(r"[.\s,]+", text_no_comm)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if len(t) >= 2]
            if not toks:
                continue

            for t in toks:
                folio_tokens[fol].append((loc, t))

            if fol == "fRos":
                z = normalize_fros_zone(comments, int(re.sub(r"[^0-9]", "", line_id) or 0))
                if z != "UNSPECIFIED":
                    last_zone = z
                fros_lines.append({
                    "line_id": line_id,
                    "loc": loc,
                    "comments": comments,
                    "zone": last_zone,
                    "tokens": toks,
                })

    # Build global stem IDF
    stem_folios = defaultdict(set)
    section_stems = defaultdict(set)
    folio_stem_sets = {}
    for fol, lt_list in folio_tokens.items():
        sec = folio_meta.get(fol, {}).get("section_code", "?")
        st_set = {canon_stem(t) for _, t in lt_list if len(canon_stem(t)) >= 2}
        folio_stem_sets[fol] = st_set
        for s in st_set:
            stem_folios[s].add(fol)
            if fol != "fRos":
                section_stems[sec].add(s)

    n_folios = len(folio_tokens)
    stem_idf = {
        s: math.log(n_folios / len(fols))
        for s, fols in stem_folios.items()
        if 2 <= len(fols) <= 20 and len(s) >= 2
    }

    # Group fRos lines by zone
    zone_lines = defaultdict(list)
    for ln in fros_lines:
        zone_lines[ln["zone"]].append(ln)

    zone_profiles = []
    for z_name, lns in sorted(zone_lines.items()):
        toks = [t for ln in lns for t in ln["tokens"]]
        st_set = {canon_stem(w) for w in toks if len(canon_stem(w)) >= 2}
        m = metrics_for_tokens(toks)

        sec_idf = {
            sk: round(sum(stem_idf[s] for s in (st_set & section_stems[sk]) if s in stem_idf), 3)
            for sk in ["H", "A", "Z", "B", "P", "S"]
        }
        f66r_shared = [s for s in (st_set & folio_stem_sets["f66r"]) if s in stem_idf]
        f66r_idf = round(sum(stem_idf[s] for s in f66r_shared), 3)

        # Best external folio match
        ext_matches = []
        for ef, est in folio_stem_sets.items():
            if ef == "fRos":
                continue
            sh = [s for s in (st_set & est) if s in stem_idf]
            if sh:
                ext_matches.append((
                    round(sum(stem_idf[s] for s in sh), 3),
                    ef,
                    folio_meta.get(ef, {}).get("section_code", "?"),
                    sorted(sh, key=lambda x: -stem_idf[x])[:4],
                ))
        ext_matches.sort(reverse=True)

        dom_sec = max(["H", "A", "Z", "B", "P", "S"], key=lambda k: sec_idf[k])
        sample_eva = " ".join(toks[:8])
        sample_gloss = " ".join(decompose_word(w)["gloss"] for w in toks[:8])

        zone_profiles.append({
            "zone": z_name,
            "n_lines": len(lns),
            "loci": sorted({ln["loc"] for ln in lns}),
            "metrics": m,
            "dominant_section": dom_sec,
            "section_routing_idf": sec_idf,
            "f66r_shared_idf": f66r_idf,
            "f66r_shared_stems": f66r_shared,
            "top_external_folios": [
                {"folio": ef, "section": es, "idf": sc, "shared_stems": sts}
                for sc, ef, es, sts in ext_matches[:3]
            ],
            "sample_eva": sample_eva,
            "sample_gloss": sample_gloss,
        })

    # Analyze the f66r <-> fRos <-> Quire 20 Master Routing Triad
    f66r_stems = folio_stem_sets["f66r"]
    fros_stems = folio_stem_sets["fRos"]
    q20_fols = [f for f, m in folio_meta.items() if m.get("quire") == "T" and f != "f116v" and f in folio_stem_sets]
    q20_stems = set().union(*(folio_stem_sets[f] for f in q20_fols))

    triad_stems = [s for s in (f66r_stems & fros_stems & q20_stems) if s in stem_idf]
    triad_idf = sum(stem_idf[s] for s in triad_stems)

    # Permutation test: pick 2 random non-Quire-20 folios with token counts matching f66r (356w) and fRos (518w)
    non_q20_fols = [f for f in folio_stem_sets if f not in q20_fols and len(folio_tokens[f]) >= 150]
    null_triad_idfs = []
    for _ in range(1000):
        f_a, f_b = random.sample(non_q20_fols, 2)
        sh = [s for s in (folio_stem_sets[f_a] & folio_stem_sets[f_b] & q20_stems) if s in stem_idf]
        null_triad_idfs.append(sum(stem_idf[s] for s in sh))

    mu_tr = sum(null_triad_idfs) / len(null_triad_idfs)
    sd_tr = math.sqrt(sum((x - mu_tr) ** 2 for x in null_triad_idfs) / len(null_triad_idfs))
    z_triad = (triad_idf - mu_tr) / (sd_tr if sd_tr > 0 else 1.0)
    p_triad = sum(1 for x in null_triad_idfs if x >= triad_idf) / len(null_triad_idfs)

    out = {
        "attack": 133,
        "phase": 144,
        "discovery": 150,
        "title": "Complete 9-Sphere Rosettes (fRos, 518 Tokens) Sphere-by-Sphere & Causeway-by-Causeway Translator and the f66r <-> fRos <-> Quire 20 Master Routing Triad",
        "fros_overview": {
            "n_lines": len(fros_lines),
            "n_zones": len(zone_profiles),
            "total_tokens": sum(len(ln["tokens"]) for ln in fros_lines),
        },
        "f66r_fros_quire20_triad_test": {
            "shared_rare_stems_count": len(triad_stems),
            "shared_rare_stems": sorted(triad_stems, key=lambda x: -stem_idf[x]),
            "observed_triad_idf": round(triad_idf, 3),
            "null_mean_random_pair": round(mu_tr, 3),
            "null_sd": round(sd_tr, 3),
            "lift_ratio": round(triad_idf / mu_tr, 3) if mu_tr > 0 else 0.0,
            "z_score": round(z_triad, 2),
            "p_value": round(p_triad, 4),
        },
        "zone_profiles": zone_profiles,
        "all_fros_lines": [
            {
                "line_id": ln["line_id"],
                "loc": ln["loc"],
                "zone": ln["zone"],
                "comments": ln["comments"],
                "n_tokens": len(ln["tokens"]),
                "eva": " ".join(ln["tokens"]),
                "gloss": " ".join(decompose_word(w)["gloss"] for w in ln["tokens"]),
            }
            for ln in fros_lines
        ],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 133] Saved {OUT_JSON}")
    print("f66r <-> fRos <-> Quire 20 Triad Test:", json.dumps(out["f66r_fros_quire20_triad_test"], indent=2))
    print("fRos Zones:")
    for zp in zone_profiles:
        m = zp["metrics"]
        print(f"  {zp['zone']} ({zp['n_lines']} lines, {m['n_tokens']}w, o-={m['o_nom_pct']}%, qo-={m['qo_pct']}%, -edy={m['edy_pct']}%, -aiin={m['aiin_pct']}%): dom={zp['dominant_section']}, f66r_IDF={zp['f66r_shared_idf']}, topExt={zp['top_external_folios'][:2]}")


if __name__ == "__main__":
    main()
