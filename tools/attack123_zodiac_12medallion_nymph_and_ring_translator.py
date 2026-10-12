#!/usr/bin/env python3
"""
Attack 123 (Phase 134 / Discovery 140):
Complete 12-Medallion Zodiac (f70v2-f73v) Star-Nymph Label (@Lz/@Ln) &
Concentric Ring (@Cc/@R) Word-for-Word Astro-Medical Translator.

Tests:
1. Complete decomposition of all 12 Zodiac Medallions (Pisces f70v2 -> Sagittarius f73v)
   into Concentric Ring Inscriptions (@Cc/@R/@C) vs. Individual Star-Nymph Labels (@Lz/@Ln/@L0).
2. Morphological Polarity Law between Zodiac Star-Nymph Labels (@Lz) and
   Concentric Ring Prose (@Cc): token length, o-/y- seasonal onset polarity,
   -y/-dy state suffixes, -al/-ar/-ol/-or fluid/resin suffixes, and -am/-m ring closure.
3. Cross-Section Label Concordance Permutation Test (1,000 trials):
   tests whether Zodiac Star-Nymph Labels (@Lz) share significantly higher
   open-class stem IDF with Balneological Nymph Labels ($I=B @Ln) and
   Pharmaceutical Botanical Labels ($I=P @Lf) than random corpus label/token draws.
4. Complete 12-Medallion Astro-Medical Translation Table: for each sign, decodes
   Central/Inner/Outer Ring texts, resolves every Star-Nymph Label to its #1
   Herbal Monograph ($I=H), Pharmaceutical Register ($I=P), Balneological Bath ($I=B),
   and Starred Recipe ($I=S).
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

random.seed(42)

ZODIAC_ORDER = [
    ("f70v2", "Pisces (March)", "SPRING_WET"),
    ("f70v1", "Aries I - Dark Stars (April I)", "SPRING_WARM"),
    ("f71r", "Aries II - Light Stars (April II)", "SPRING_WARM"),
    ("f71v", "Taurus I - Dark Stars (May I)", "SPRING_TEMPERATE"),
    ("f72r1", "Taurus II - Light Stars (May II)", "SPRING_TEMPERATE"),
    ("f72r2", "Gemini (June)", "SUMMER_HOT"),
    ("f72r3", "Cancer (July)", "SUMMER_MOIST"),
    ("f72v3", "Leo (August)", "SUMMER_DRY"),
    ("f72v2", "Virgo (September)", "AUTUMN_EARTHY"),
    ("f72v1", "Libra (October)", "AUTUMN_EQUINOX"),
    ("f73r", "Scorpio (November)", "AUTUMN_MARS"),
    ("f73v", "Sagittarius (December)", "WINTER_JUPITER"),
]


def canonicalize_token(w):
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[@&]\d+;", "", w)
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w:
        return ""
    w = re.sub(r"^qo", "q-", w)
    w = re.sub(r"ch", "C", w)
    w = re.sub(r"sh", "S", w)
    w = re.sub(r"([ptkf])C", r"\1_C", w)
    w = re.sub(r"([ptkf])S", r"\1_S", w)
    w = re.sub(r"i{2,}n", "IIN", w)
    w = re.sub(r"e{2,}", "EE", w)
    return w


def extract_stem(canon):
    if not canon:
        return ""
    s = canon
    for p in ["q-", "d-o-", "s-o-", "l-o-", "o-l-", "o-", "y-", "d-", "s-", "l-", "r-"]:
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    for suf in ["aIIN", "IIN", "EEdy", "edy", "dy", "ey", "ol", "or", "al", "ar", "am", "y", "l", "r", "m", "n"]:
        if s.endswith(suf) and len(s) > len(suf) + 1:
            s = s[:-len(suf)]
            break
    return s


STEM_GLOSS = {
    "k": "HERB:calyx/heat-root[k]",
    "t": "HERB:tube/stalk-herb[t]",
    "p": "HERB:cup/pitcher-leaf[p]",
    "f": "HERB:plumed-foliage[f]",
    "C": "HERB:ch-bench-herb[ch]",
    "S": "HERB:sh-plume-herb[sh]",
    "d": "ROOT:ground/foot-base[d]",
    "l": "LIQ:wash/lotion-fluid[l]",
    "r": "SOL:sharp-resin/seed[r]",
    "s": "SEQ:shoot/tendril[s]",
    "k_C": "CMPD:calyx-bench[kch]",
    "t_C": "CMPD:stalk-bench[tch]",
    "p_C": "CMPD:cup-bench[pch]",
    "f_C": "CMPD:plume-bench[fch]",
    "k_S": "CMPD:calyx-spray[ksh]",
    "t_S": "CMPD:stalk-spray[tsh]",
    "p_S": "CMPD:cup-spray[psh]",
    "ke": "STEM:boiled-calyx[ke]",
    "te": "STEM:boiled-stalk[te]",
    "pe": "STEM:boiled-cup[pe]",
    "fe": "STEM:boiled-plume[fe]",
    "Ce": "STEM:infused-bench[che]",
    "Se": "STEM:infused-spray[she]",
    "ok": "NOM:vessel-calyx[ok]",
    "ot": "NOM:vessel-stalk[ot]",
    "op": "NOM:vessel-cup[op]",
    "of": "NOM:vessel-plume[of]",
    "yk": "AUTUMN:init-calyx[yk]",
    "yt": "AUTUMN:init-stalk[yt]",
    "yp": "AUTUMN:init-cup[yp]",
    "yf": "AUTUMN:init-plume[yf]",
}


def gloss_zodiac_token(raw, canon, stem):
    pref = ""
    if canon.startswith("o"):
        pref = "SPRING-NOM[o-]+"
    elif canon.startswith("y"):
        pref = "AUTUMN-INIT[y-]+"
    elif canon.startswith("q-"):
        pref = "ACT-EXTRACT[qo-]+"
    elif canon.startswith("d"):
        pref = "BASE[d-]+"
    elif canon.startswith("s"):
        pref = "SHOOT[s-]+"
    elif canon.startswith("l"):
        pref = "BATH[l-]+"

    sg = STEM_GLOSS.get(stem, f"DECAN-HERB[{stem}]")

    suf = ""
    if canon.endswith("aIIN") or canon.endswith("IIN"):
        suf = ":DEGREE-DOSE[-aiin]"
    elif canon.endswith("EEdy") or canon.endswith("edy"):
        suf = ":PROCESS[-edy]"
    elif canon.endswith("dy"):
        suf = ":STEEPED-NYMPH[-dy]"
    elif canon.endswith("ey"):
        suf = ":COOKED[-ey]"
    elif canon.endswith("ol") or canon.endswith("al"):
        suf = ":FLUID-BALM[-ol/al]"
    elif canon.endswith("or") or canon.endswith("ar"):
        suf = ":ESSENCE-RESIN[-or/ar]"
    elif canon.endswith("am") or canon.endswith("m"):
        suf = ":RING-SEAL[-am]"
    elif canon.endswith("y"):
        suf = ":STAR-STATE[-y]"

    return f"{raw} <{pref}{sg}{suf}>"


def parse_zl():
    path = os.path.join("data", "ZL3b-n.txt")
    folios = {}
    current_folio = None
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m_meta = re.match(r"^<f([0-9]+[rv][0-9]*)>\s*<!\s*(.*?)\s*>", line)
            if m_meta:
                fol = "f" + m_meta.group(1)
                meta_str = m_meta.group(2)
                meta = {}
                for kv in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str):
                    meta[kv[0]] = kv[1]
                current_folio = fol
                folios[fol] = {
                    "folio": fol,
                    "Q": meta.get("Q", "?"),
                    "I": meta.get("I", "?"),
                    "L": meta.get("L", "?"),
                    "H": meta.get("H", "?"),
                    "tokens": [],
                    "loci": [],
                }
                continue
            m_loc = re.match(r"^<f([0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s*(.*)", line)
            if m_loc and current_folio:
                lnum = m_loc.group(2)
                loc = m_loc.group(3)
                text = m_loc.group(4)
                text_clean = re.sub(r"<[^>]+>", " ", text)
                raw_words = [w.strip() for w in re.split(r"[.\s,]+", text_clean) if w.strip()]
                loc_clean = loc.lstrip("@+=*~&")
                tok_list = []
                for rw in raw_words:
                    c = canonicalize_token(rw)
                    if not c:
                        continue
                    stem = extract_stem(c)
                    item = {"raw": rw, "canon": c, "stem": stem, "loc": loc, "loc_clean": loc_clean, "line": lnum}
                    folios[current_folio]["tokens"].append(item)
                    tok_list.append(item)
                if tok_list:
                    folios[current_folio]["loci"].append({
                        "line": lnum,
                        "loc": loc,
                        "loc_clean": loc_clean,
                        "tokens": tok_list,
                    })
    return folios


def morph_stats(tokens):
    n = len(tokens)
    if n == 0:
        return {}
    return {
        "n_tokens": n,
        "mean_len_chars": round(sum(len(t["raw"]) for t in tokens) / n, 2),
        "o_onset_pct": round(100.0 * sum(1 for t in tokens if t["raw"].lower().startswith("o")) / n, 2),
        "y_onset_pct": round(100.0 * sum(1 for t in tokens if t["raw"].lower().startswith("y")) / n, 2),
        "qo_onset_pct": round(100.0 * sum(1 for t in tokens if t["canon"].startswith("q-")) / n, 2),
        "y_dy_coda_pct": round(100.0 * sum(1 for t in tokens if t["canon"].endswith("y") or t["canon"].endswith("dy")) / n, 2),
        "fluid_resin_ol_or_al_ar_pct": round(
            100.0 * sum(1 for t in tokens if any(t["canon"].endswith(s) for s in ["ol", "or", "al", "ar"])) / n, 2
        ),
        "ring_seal_am_m_pct": round(
            100.0 * sum(1 for t in tokens if t["canon"].endswith("am") or t["canon"].endswith("m")) / n, 2
        ),
        "aiin_coda_pct": round(100.0 * sum(1 for t in tokens if t["canon"].endswith("IIN")) / n, 2),
    }


def main():
    folios = parse_zl()

    # Global stem IDF (df <= 55)
    stem_df = Counter()
    all_attested_stems = set()
    for fol, d in folios.items():
        if d["I"] != "Z":
            for t in d["tokens"]:
                if t["stem"]:
                    all_attested_stems.add(t["stem"])
        stems = {t["stem"] for t in d["tokens"] if len(t["stem"]) >= 2}
        for s in stems:
            stem_df[s] += 1
    N_fol = len(folios)
    stem_idf = {s: math.log((N_fol + 1) / (df + 1)) for s, df in stem_df.items() if df <= 55}

    for fol, d in folios.items():
        d["stem_set"] = {t["stem"] for t in d["tokens"] if t["stem"] in stem_idf}
        d["all_stems"] = {t["stem"] for t in d["tokens"] if t["stem"]}

    herbal_fols = [d for d in folios.values() if d["I"] == "H"]
    pharm_fols = [d for d in folios.values() if d["I"] == "P"]
    balneo_fols = [d for d in folios.values() if d["I"] == "B"]
    starred_fols = [d for d in folios.values() if d["I"] == "S" and d["Q"] == "T"]

    herbal_stem_pool = set().union(*(d["all_stems"] for d in herbal_fols))
    pharm_stem_pool = set().union(*(d["all_stems"] for d in pharm_fols))
    balneo_stem_pool = set().union(*(d["all_stems"] for d in balneo_fols))
    starred_stem_pool = set().union(*(d["all_stems"] for d in starred_fols))

    # Extract Balneological @Ln and Pharmaceutical @Lf label stem sets
    balneo_ln_stems = {
        t["stem"]
        for d in balneo_fols
        for t in d["tokens"]
        if t["loc_clean"].startswith("Ln") and t["stem"] in stem_idf
    }
    pharm_lf_stems = {
        t["stem"]
        for d in pharm_fols
        for t in d["tokens"]
        if t["loc_clean"].startswith("Lf") and t["stem"] in stem_idf
    }
    clinical_label_stems = balneo_ln_stems | pharm_lf_stems

    # Resolve any Zodiac token via 1-to-3-stem decomposition
    def resolve_stem(canon, stem):
        if stem in all_attested_stems:
            return {"status": "DIRECT_STEM", "parts": [stem]}
        stripped = re.sub(r"^[oydslr]+", "", stem)
        if len(stripped) >= 1 and stripped in all_attested_stems:
            return {"status": "PREFIX_STRIPPED", "parts": [stripped]}
        for i in range(1, len(stem)):
            p1, p2 = stem[:i], stem[i:]
            if p1 in all_attested_stems and p2 in all_attested_stems:
                return {"status": "COMPOUND_2STEM", "parts": [p1, p2]}
        for i in range(1, len(stem) - 1):
            for j in range(i + 1, len(stem)):
                p1, p2, p3 = stem[:i], stem[i:j], stem[j:]
                if p1 in all_attested_stems and p2 in all_attested_stems and p3 in all_attested_stems:
                    return {"status": "COMPOUND_3STEM", "parts": [p1, p2, p3]}
        return {"status": "UNRESOLVED", "parts": [stem]}

    all_ring_tokens = []
    all_nymph_tokens = []
    medallion_records = []

    res_counts = Counter()
    in_herbal_count = 0
    in_pharm_count = 0
    in_balneo_count = 0
    in_starred_count = 0

    for fol, sign_name, humor in ZODIAC_ORDER:
        d = folios[fol]
        ring_loci = []
        nymph_loci = []
        f_ring_toks = []
        f_nymph_toks = []

        for loc_entry in d["loci"]:
            lc = loc_entry["loc_clean"]
            if lc.startswith("L"):
                nymph_loci.append(loc_entry)
                f_nymph_toks.extend(loc_entry["tokens"])
                all_nymph_tokens.extend(loc_entry["tokens"])
            else:
                ring_loci.append(loc_entry)
                f_ring_toks.extend(loc_entry["tokens"])
                all_ring_tokens.extend(loc_entry["tokens"])

        # Resolve nymph labels on this medallion
        decoded_nymphs = []
        for t in f_nymph_toks:
            res = resolve_stem(t["canon"], t["stem"])
            res_counts[res["status"]] += 1
            parts = set(res["parts"])
            in_h = bool(parts & herbal_stem_pool)
            in_p = bool(parts & pharm_stem_pool)
            in_b = bool(parts & balneo_stem_pool)
            in_s = bool(parts & starred_stem_pool)
            if in_h:
                in_herbal_count += 1
            if in_p:
                in_pharm_count += 1
            if in_b:
                in_balneo_count += 1
            if in_s:
                in_starred_count += 1

            # Find top Herbal Monograph for this nymph label
            best_h = None
            best_h_score = -1.0
            for hf in herbal_fols:
                ov = parts & hf["all_stems"]
                sc = sum(stem_idf.get(x, 1.0) for x in ov)
                if sc > best_h_score and ov:
                    best_h_score = sc
                    best_h = f"{hf['folio']}($L={hf['L']})"

            decoded_nymphs.append({
                "line": t["line"],
                "loc": t["loc"],
                "raw": t["raw"],
                "canon": t["canon"],
                "stem": t["stem"],
                "resolution": res["status"],
                "parts": res["parts"],
                "gloss": gloss_zodiac_token(t["raw"], t["canon"], t["stem"]),
                "top_herbal": best_h or "H-general",
                "in_sections": "".join([
                    "H" if in_h else "",
                    "P" if in_p else "",
                    "B" if in_b else "",
                    "S" if in_s else "",
                ]),
            })

        # Decode ring loci
        decoded_rings = []
        for rl in ring_loci:
            rtoks = rl["tokens"]
            last_raw = rtoks[-1]["raw"] if rtoks else ""
            last_canon = rtoks[-1]["canon"] if rtoks else ""
            has_am_seal = last_canon.endswith("am") or last_canon.endswith("m") or last_canon.endswith("y")
            decoded_rings.append({
                "line": rl["line"],
                "loc": rl["loc"],
                "n_tokens": len(rtoks),
                "terminal_token": last_raw,
                "has_terminal_seal": has_am_seal,
                "eva_preview": " . ".join(x["raw"] for x in rtoks[:10]),
                "gloss_preview": " | ".join(gloss_zodiac_token(x["raw"], x["canon"], x["stem"]) for x in rtoks[:6]),
            })

        # Medallion-level best cross-section matches
        def best_medallion_match(candidates):
            bf, bsc, bsh = None, -1.0, []
            for c in candidates:
                sh = sorted(d["stem_set"] & c["stem_set"], key=lambda s: -stem_idf[s])
                sc = sum(stem_idf[s] for s in sh)
                if sc > bsc:
                    bsc, bf, bsh = sc, f"{c['folio']}(L={c['L']})", sh[:4]
            return {"folio": bf, "idf": round(bsc, 3), "shared_stems": bsh}

        medallion_records.append({
            "folio": fol,
            "sign": sign_name,
            "humoral_quality": humor,
            "n_ring_loci": len(ring_loci),
            "n_ring_tokens": len(f_ring_toks),
            "n_nymph_labels": len(f_nymph_toks),
            "nymph_morph": morph_stats(f_nymph_toks),
            "ring_morph": morph_stats(f_ring_toks),
            "best_herbal": best_medallion_match(herbal_fols),
            "best_pharm": best_medallion_match(pharm_fols),
            "best_balneo": best_medallion_match(balneo_fols),
            "best_starred": best_medallion_match(starred_fols),
            "rings": decoded_rings,
            "nymph_labels": decoded_nymphs,
        })

    # Permutation Test: Zodiac Nymph Label Stem Set vs. Clinical Label Stem Set (Balneo @Ln + Pharm @Lf)
    zodiac_nymph_stems = {t["stem"] for t in all_nymph_tokens if t["stem"] in stem_idf}
    obs_shared_label_stems = zodiac_nymph_stems & clinical_label_stems
    obs_label_idf = sum(stem_idf[s] for s in obs_shared_label_stems)

    all_idf_pool = list(stem_idf.keys())
    k_zn = len(zodiac_nymph_stems)
    null_idfs = []
    for _ in range(1000):
        samp = set(random.sample(all_idf_pool, k_zn))
        null_idfs.append(sum(stem_idf[s] for s in (samp & clinical_label_stems)))
    mu_l = sum(null_idfs) / len(null_idfs)
    sd_l = math.sqrt(sum((x - mu_l) ** 2 for x in null_idfs) / len(null_idfs)) or 1e-9
    z_label_concordance = (obs_label_idf - mu_l) / sd_l

    total_nymph = len(all_nymph_tokens)
    resolved_nymph = total_nymph - res_counts["UNRESOLVED"]

    out = {
        "attack": "Attack 123 (Phase 134 / Discovery 140)",
        "title": "Complete 12-Medallion Zodiac (f70v2-f73v) Star-Nymph Label & Concentric Ring Astro-Medical Translator",
        "global_summary": {
            "n_medallions": len(medallion_records),
            "total_nymph_star_labels": total_nymph,
            "total_ring_tokens": len(all_ring_tokens),
            "nymph_label_resolved_count": resolved_nymph,
            "nymph_label_resolved_pct": round(100.0 * resolved_nymph / max(total_nymph, 1), 2),
            "resolution_breakdown": dict(res_counts),
            "nymph_in_herbal_pct": round(100.0 * in_herbal_count / max(total_nymph, 1), 2),
            "nymph_in_pharm_pct": round(100.0 * in_pharm_count / max(total_nymph, 1), 2),
            "nymph_in_balneo_pct": round(100.0 * in_balneo_count / max(total_nymph, 1), 2),
            "nymph_in_starred_pct": round(100.0 * in_starred_count / max(total_nymph, 1), 2),
            "nymph_morph_global": morph_stats(all_nymph_tokens),
            "ring_morph_global": morph_stats(all_ring_tokens),
        },
        "zodiac_nymph_to_clinical_label_permutation_test": {
            "n_zodiac_nymph_rare_stems": k_zn,
            "n_clinical_ln_lf_rare_stems": len(clinical_label_stems),
            "shared_rare_stems_count": len(obs_shared_label_stems),
            "observed_shared_idf": round(obs_label_idf, 3),
            "null_mean_idf": round(mu_l, 3),
            "null_std_idf": round(sd_l, 3),
            "lift": round(obs_label_idf / max(mu_l, 1e-9), 2),
            "z_score": round(z_label_concordance, 2),
        },
        "medallion_records": medallion_records,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/attack123_zodiac_12medallion_nymph_and_ring_translator.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== ATTACK 123 SUMMARY ===")
    print("Global Summary:", json.dumps(out["global_summary"], indent=2))
    print("Permutation Test (Zodiac @Lz vs Balneo @Ln + Pharm @Lf):", json.dumps(out["zodiac_nymph_to_clinical_label_permutation_test"], indent=2))
    for m in medallion_records:
        print(f"  {m['folio']} {m['sign']}: rings={m['n_ring_loci']}({m['n_ring_tokens']}w), nymphs={m['n_nymph_labels']}, o%={m['nymph_morph'].get('o_onset_pct')}, y%={m['nymph_morph'].get('y_onset_pct')}, H={m['best_herbal']['folio']}, P={m['best_pharm']['folio']}, B={m['best_balneo']['folio']}, S={m['best_starred']['folio']}")


if __name__ == "__main__":
    main()
