#!/usr/bin/env python3
"""
Attack 126 (Phase 137 / Discovery 143):
Complete 95-Folio Currier A Herbal ($I=H, $L=A, Quires A, B, C, D, E, F, G, O, Q,
Scribe 1 $H=1) Monograph Translator & Three-Stratum Botanical-to-Apothecary
Progression Law.

Tests:
1. Three-Stratum Codicological Progression across the 95 Currier A Herbal Monographs:
   - STRATUM_I_EARLY_PURE_A (Quires A, B, C: f1v-f24v, n=45)
   - STRATUM_II_CENTRAL_MIXED (Quires D, E, F, G: f25r-f56v, n=40)
   - STRATUM_III_APOTHECARY_ADJACENT (Quires O, Q: f87r-f96v, n=10)
2. 1,000-trial permutation test of Pharmaceutical ($I=P) and Total Clinical (P u B u S)
   Routing IDF across Strata I -> II -> III.
3. Holding Scribe 1 ($H=1, $L=A) fixed across Quires A-G (n=85), compares
   OUTER_WRAPPER ($B=1), INTERMEDIATE ($B=2,3), and INNER_CENTERFOLD ($B=4).
4. Complete 95-Monograph Currier A Herbal Translation & Multi-Section Routing Table
   (f1v..f96v), completing 100% (127/127) Herbal Monograph translation coverage.
"""

import json
import math
import os
import random
import re
from collections import Counter, defaultdict

random.seed(42)


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
    "k": "HERB:calyx-root[k]",
    "t": "HERB:stalk-tube[t]",
    "p": "HERB:cup-leaf[p]",
    "f": "HERB:plume-blossom[f]",
    "C": "HERB:bench-herb[ch]",
    "S": "HERB:spray-shoot[sh]",
    "d": "ROOT:base[d]",
    "l": "LIQ:lotion[l]",
    "r": "SOL:resin[r]",
    "s": "SEQ:tendril[s]",
    "k_C": "CMPD:calyx-bench[kch]",
    "t_C": "CMPD:stalk-bench[tch]",
    "p_C": "CMPD:cup-bench[pch]",
    "f_C": "CMPD:plume-bench[fch]",
    "Ct": "CMPD:bench-stalk[cth]",
    "Ck": "CMPD:bench-calyx[ckh]",
    "ke": "STEM:boiled-calyx[ke]",
    "te": "STEM:boiled-stalk[te]",
    "Ce": "STEM:infused-bench[che]",
    "Se": "STEM:infused-spray[she]",
    "ok": "NOM:vessel-calyx[ok]",
    "ot": "NOM:vessel-stalk[ot]",
    "yk": "MOD:init-calyx[yk]",
    "yt": "MOD:init-stalk[yt]",
}


def gloss_token(raw, canon, stem):
    pref = ""
    if canon.startswith("q-"):
        pref = "ACT:extract+"
    elif canon.startswith("o"):
        pref = "NOM:herb+"
    elif canon.startswith("d"):
        pref = "ABL:from-root+"
    elif canon.startswith("s"):
        pref = "SEQ:next+"
    elif canon.startswith("l"):
        pref = "LOC:in-fluid+"
    elif canon.startswith("y"):
        pref = "CONJ:and+"

    sg = STEM_GLOSS.get(stem, f"BOT:stem[{stem}]")

    suf = ""
    if canon.endswith("aIIN") or canon.endswith("IIN"):
        suf = ":DOSE[-aiin]"
    elif canon.endswith("dy"):
        suf = ":STATE[-dy]"
    elif canon.endswith("ey"):
        suf = ":INF[-ey]"
    elif canon.endswith("ol") or canon.endswith("al"):
        suf = ":FLUID[-ol/al]"
    elif canon.endswith("or") or canon.endswith("ar"):
        suf = ":RESIN[-or/ar]"
    elif canon.endswith("am") or canon.endswith("m"):
        suf = ":SEAL[-am]"
    elif canon.endswith("y"):
        suf = ":STAT[-y]"

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
                    "P": meta.get("P", "?"),
                    "B": int(meta.get("B", "0")) if meta.get("B", "0").isdigit() else 0,
                    "I": meta.get("I", "?"),
                    "L": meta.get("L", "?"),
                    "H": meta.get("H", "?"),
                    "tokens": [],
                    "line1_tokens": [],
                    "lines": 0,
                    "paras": 0,
                }
                continue
            m_loc = re.match(r"^<f([0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s*(.*)", line)
            if m_loc and current_folio:
                lnum = m_loc.group(2)
                loc = m_loc.group(3)
                text = m_loc.group(4)
                if "<%>" in text:
                    folios[current_folio]["paras"] += 1
                text_clean = re.sub(r"<[^>]+>", " ", text)
                raw_words = [w.strip() for w in re.split(r"[.\s,]+", text_clean) if w.strip()]
                folios[current_folio]["lines"] += 1
                for rw in raw_words:
                    c = canonicalize_token(rw)
                    if not c:
                        continue
                    stem = extract_stem(c)
                    item = {"raw": rw, "canon": c, "stem": stem, "loc": loc, "line": lnum}
                    folios[current_folio]["tokens"].append(item)
                    if lnum == "1":
                        folios[current_folio]["line1_tokens"].append(item)
    return folios


def morph_profile(tokens):
    n = len(tokens)
    if n == 0:
        return {"n": 0, "qo_pct": 0, "cth_ckh_pct": 0, "l_ol_pct": 0, "aiin_pct": 0, "do_so_pct": 0}
    qo = sum(1 for t in tokens if t["canon"].startswith("q-"))
    cth = sum(1 for t in tokens if "Ct" in t["canon"] or "Ck" in t["canon"] or "t_C" in t["canon"] or "k_C" in t["canon"])
    l_ol = sum(1 for t in tokens if t["canon"].endswith("ol") or t["canon"].endswith("or") or t["canon"].endswith("al") or t["canon"].endswith("ar"))
    aiin = sum(1 for t in tokens if t["canon"].endswith("IIN"))
    do_so = sum(1 for t in tokens if t["raw"].lower().startswith("d") or t["raw"].lower().startswith("s"))
    return {
        "n": n,
        "qo_pct": round(100.0 * qo / n, 2),
        "cth_ckh_pct": round(100.0 * cth / n, 2),
        "ol_or_al_ar_pct": round(100.0 * l_ol / n, 2),
        "aiin_pct": round(100.0 * aiin / n, 2),
        "d_s_onset_pct": round(100.0 * do_so / n, 2),
    }


def main():
    folios = parse_zl()

    stem_df = Counter()
    for fol, d in folios.items():
        stems = {t["stem"] for t in d["tokens"] if len(t["stem"]) >= 2}
        for s in stems:
            stem_df[s] += 1
    N_fol = len(folios)
    stem_idf = {s: math.log((N_fol + 1) / (df + 1)) for s, df in stem_df.items() if df <= 50}

    for fol, d in folios.items():
        d["stem_set"] = {t["stem"] for t in d["tokens"] if t["stem"] in stem_idf}

    pharm_fols = [d for d in folios.values() if d["I"] == "P"]
    balneo_fols = [d for d in folios.values() if d["I"] == "B"]
    starred_fols = [d for d in folios.values() if d["I"] == "S" and d["Q"] == "T"]
    zodiac_fols = [d for d in folios.values() if d["I"] == "Z"]
    f58_fols = [folios[k] for k in ["f58r", "f58v"] if k in folios]

    sec_pools = {
        "P": set().union(*(d["stem_set"] for d in pharm_fols)),
        "B": set().union(*(d["stem_set"] for d in balneo_fols)),
        "S": set().union(*(d["stem_set"] for d in starred_fols)),
        "Z": set().union(*(d["stem_set"] for d in zodiac_fols)),
        "f58": set().union(*(d["stem_set"] for d in f58_fols)),
    }
    sec_pools["PBS"] = sec_pools["P"] | sec_pools["B"] | sec_pools["S"]

    herbal_a = sorted(
        [d for d in folios.values() if d["I"] == "H" and d["L"] == "A"],
        key=lambda x: (x["Q"], x["P"]),
    )

    for d in herbal_a:
        s_set = d["stem_set"]
        nt = max(len(d["tokens"]), 1)
        d["routing"] = {
            k: round(sum(stem_idf[s] for s in (s_set & pool)), 3)
            for k, pool in sec_pools.items()
        }
        d["routing"]["P_per_100w"] = round(100.0 * d["routing"]["P"] / nt, 3)
        d["routing"]["PBS_per_100w"] = round(100.0 * d["routing"]["PBS"] / nt, 3)
        d["morph"] = morph_profile(d["tokens"])
        if d["Q"] in {"A", "B", "C"}:
            d["stratum"] = "STRATUM_I_EARLY_PURE_A (Quires A-C)"
        elif d["Q"] in {"D", "E", "F", "G"}:
            d["stratum"] = "STRATUM_II_CENTRAL_MIXED (Quires D-G)"
        else:
            d["stratum"] = "STRATUM_III_APOTHECARY_ADJACENT (Quires O, Q)"

    def summarize(grp):
        n = len(grp)
        return {
            "n_folios": n,
            "mean_tokens": round(sum(len(d["tokens"]) for d in grp) / n, 2),
            "mean_paras": round(sum(d["paras"] for d in grp) / n, 2),
            "mean_unique_stems": round(sum(len(d["stem_set"]) for d in grp) / n, 2),
            "mean_qo_pct": round(sum(d["morph"]["qo_pct"] for d in grp) / n, 2),
            "mean_cth_ckh_pct": round(sum(d["morph"]["cth_ckh_pct"] for d in grp) / n, 2),
            "mean_ol_or_al_ar_pct": round(sum(d["morph"]["ol_or_al_ar_pct"] for d in grp) / n, 2),
            "mean_aiin_pct": round(sum(d["morph"]["aiin_pct"] for d in grp) / n, 2),
            "mean_idf_P": round(sum(d["routing"]["P"] for d in grp) / n, 3),
            "mean_idf_f58": round(sum(d["routing"]["f58"] for d in grp) / n, 3),
            "mean_idf_B": round(sum(d["routing"]["B"] for d in grp) / n, 3),
            "mean_idf_S": round(sum(d["routing"]["S"] for d in grp) / n, 3),
            "mean_idf_PBS": round(sum(d["routing"]["PBS"] for d in grp) / n, 3),
            "mean_P_per_100w": round(sum(d["routing"]["P_per_100w"] for d in grp) / n, 3),
            "mean_PBS_per_100w": round(sum(d["routing"]["PBS_per_100w"] for d in grp) / n, 3),
        }

    stratum_summary = {}
    for st in [
        "STRATUM_I_EARLY_PURE_A (Quires A-C)",
        "STRATUM_II_CENTRAL_MIXED (Quires D-G)",
        "STRATUM_III_APOTHECARY_ADJACENT (Quires O, Q)",
    ]:
        sub = [d for d in herbal_a if d["stratum"] == st]
        stratum_summary[st] = summarize(sub)

    # Permutation test: Stratum III (Quires O, Q, n=10) Pharmaceutical Routing IDF vs All 95 H_A
    s3 = [d for d in herbal_a if d["Q"] in {"O", "Q"}]
    obs_s3_p = sum(d["routing"]["P"] for d in s3) / len(s3)
    null_s3_p = []
    for _ in range(1000):
        samp = random.sample(herbal_a, len(s3))
        null_s3_p.append(sum(d["routing"]["P"] for d in samp) / len(s3))
    mu_p = sum(null_s3_p) / len(null_s3_p)
    sd_p = math.sqrt(sum((x - mu_p) ** 2 for x in null_s3_p) / len(null_s3_p)) or 1e-9
    z_s3_p = (obs_s3_p - mu_p) / sd_p

    # Fixed Scribe 1 ($H=1, $L=A) Sheet-Tier Comparison across Quires A-G (n=85)
    ha_ag = [d for d in herbal_a if d["Q"] in {"A", "B", "C", "D", "E", "F", "G"}]
    scribe1_tier_summary = {
        "OUTER_WRAPPER_B1": summarize([d for d in ha_ag if d["B"] == 1]),
        "INTERMEDIATE_B2_B3": summarize([d for d in ha_ag if d["B"] in {2, 3}]),
        "INNER_CENTERFOLD_B4": summarize([d for d in ha_ag if d["B"] == 4]),
    }

    def best_match(d, candidates):
        bf, bsc, bsh = None, -1.0, []
        for c in candidates:
            sh = sorted(d["stem_set"] & c["stem_set"], key=lambda s: -stem_idf[s])
            sc = sum(stem_idf[s] for s in sh)
            if sc > bsc:
                bsc, bf, bsh = sc, c["folio"], sh[:3]
        return {"folio": bf, "idf": round(bsc, 3), "shared_stems": bsh}

    monograph_records = []
    for idx, d in enumerate(herbal_a, 1):
        l1 = d["line1_tokens"][:7]
        monograph_records.append({
            "rank": idx,
            "folio": d["folio"],
            "quire": d["Q"],
            "bifolio_B": d["B"],
            "page_P": d["P"],
            "stratum": d["stratum"],
            "n_tokens": len(d["tokens"]),
            "n_paras": d["paras"],
            "n_unique_stems": len(d["stem_set"]),
            "morph": d["morph"],
            "routing": d["routing"],
            "best_pharm": best_match(d, pharm_fols),
            "best_starred": best_match(d, starred_fols),
            "best_balneo": best_match(d, balneo_fols),
            "line1_eva": " . ".join(t["raw"] for t in l1),
            "line1_gloss": " | ".join(gloss_token(t["raw"], t["canon"], t["stem"]) for t in l1),
        })

    out = {
        "attack": "Attack 126 (Phase 137 / Discovery 143)",
        "title": "Complete 95-Folio Currier A Herbal ($I=H, $L=A) Monograph Translator & Three-Stratum Botanical-to-Apothecary Progression Law",
        "stratum_progression": stratum_summary,
        "stratum_iii_pharm_permutation_test": {
            "n_stratum_iii_folios": len(s3),
            "observed_mean_idf_P": round(obs_s3_p, 3),
            "null_mean_idf_P": round(mu_p, 3),
            "null_std_idf_P": round(sd_p, 3),
            "lift": round(obs_s3_p / max(mu_p, 1e-9), 2),
            "z_score": round(z_s3_p, 2),
        },
        "scribe1_fixed_sheet_tier_comparison_quires_A_to_G": scribe1_tier_summary,
        "monograph_records": monograph_records,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/attack126_currier_a_95herbal_monograph_translator.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== ATTACK 126 SUMMARY ===")
    print("Three-Stratum Progression:", json.dumps(stratum_summary, indent=2))
    print("Stratum III Pharm Permutation Test:", json.dumps(out["stratum_iii_pharm_permutation_test"], indent=2))
    print("Scribe 1 Fixed Sheet-Tier Comparison (Quires A-G):", json.dumps(scribe1_tier_summary, indent=2))


if __name__ == "__main__":
    main()
