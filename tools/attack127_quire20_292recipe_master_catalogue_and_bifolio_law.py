#!/usr/bin/env python3
"""
Attack 127 (Phase 138 / Discovery 144):
Complete 292-Recipe Quire 20 (f103r-f116r, $I=S) Starred Clinical Recipe Master
Catalogue, 6-Bifolio ($B=1..6) Nested Compounding Law & 23-Folio Progression.

Tests:
1. Complete extraction and morphological/stoichiometric profiling of all ~292
   starred clinical recipes (<%>) across the 23 folios of Quire T (f103r-f116r).
2. Six-Bifolio ($B=1..6) Nested Compounding Law across Quire T:
   compares OUTER_SHELL ($B=1,2: f103,f104,f115,f116), MID_SHELL ($B=3,4: f105,f106,f113,f114),
   and INNER_CENTERFOLD_CORE ($B=5,6: f107,f108,f111,f112), with a 1,000-trial
   permutation test of Multi-Section Clinical Hub IDF and Recipe Length.
3. Four-Regimen Classification of all 292 Starred Recipes:
   - INTENSIVE_BOILED_DECOCTION (high qo- + -edy/-eedy)
   - AQUEOUS_LOTION_INFUSION (high l-/ol- + -ol/-al)
   - STOICHIOMETRIC_MULTI_COMPOUND (>= 8 measured -aiin doses)
   - SIMPLE_SPECIFIC_RECIPE (concise 1-3 line specific prescription)
4. Complete 23-Folio Summary & 292-Recipe Master Clinical Catalogue.
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
    "k": "HERB:calyx[k]",
    "t": "HERB:stalk[t]",
    "p": "HERB:cup[p]",
    "f": "HERB:plume[f]",
    "C": "ACT:mix-bench[ch]",
    "S": "ACT:infuse-spray[sh]",
    "d": "BASE:portion[d]",
    "l": "LIQ:lotion[l]",
    "r": "RESIN:measure[r]",
    "s": "SEQ:next[s]",
    "ke": "BOIL:calyx[ke]",
    "te": "BOIL:stalk[te]",
    "kEE": "STEEP:calyx[kee]",
    "tEE": "STEEP:stalk[tee]",
    "Ce": "MIX:bench[che]",
    "Se": "INFUSE:spray[she]",
    "CEE": "DECOCT:bench[chee]",
    "SEE": "DECOCT:spray[shee]",
    "lk": "BATH:lotion-calyx[lk]",
    "lt": "BATH:lotion-stalk[lt]",
    "ok": "VESSEL:calyx[ok]",
    "ot": "VESSEL:stalk[ot]",
}


def gloss_token(raw, canon, stem):
    pref = ""
    if canon.startswith("q-"):
        pref = "IMP:boil+"
    elif canon.startswith("o"):
        pref = "NOM:vessel+"
    elif canon.startswith("l"):
        pref = "BATH:in-liquid+"
    elif canon.startswith("d"):
        pref = "ABL:from-part+"
    elif canon.startswith("s"):
        pref = "SEQ:then-add+"
    elif canon.startswith("y"):
        pref = "CONJ:and+"

    sg = STEM_GLOSS.get(stem, f"INGR[{stem}]")

    suf = ""
    if canon.endswith("aIIN") or canon.endswith("IIN"):
        suf = ":DOSE[-aiin]"
    elif canon.endswith("EEdy"):
        suf = ":SIMMER[-eedy]"
    elif canon.endswith("edy"):
        suf = ":BOIL[-edy]"
    elif canon.endswith("dy"):
        suf = ":DONE[-dy]"
    elif canon.endswith("ey"):
        suf = ":COOKED[-ey]"
    elif canon.endswith("ol") or canon.endswith("al"):
        suf = ":FLUID[-ol/al]"
    elif canon.endswith("or") or canon.endswith("ar"):
        suf = ":EXTRACT[-or/ar]"
    elif canon.endswith("am") or canon.endswith("m"):
        suf = ":FINISH[-am]"
    elif canon.endswith("y"):
        suf = ":STATE[-y]"

    return f"{raw} <{pref}{sg}{suf}>"


def parse_zl():
    path = os.path.join("data", "ZL3b-n.txt")
    folios = {}
    current_folio = None
    current_recipe = None
    recipes = []

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
                current_recipe = None
                folios[fol] = {
                    "folio": fol,
                    "Q": meta.get("Q", "?"),
                    "P": meta.get("P", "?"),
                    "B": int(meta.get("B", "0")) if meta.get("B", "0").isdigit() else 0,
                    "I": meta.get("I", "?"),
                    "L": meta.get("L", "?"),
                    "H": meta.get("H", "?"),
                    "tokens": [],
                    "recipes": [],
                }
                continue
            m_loc = re.match(r"^<f([0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s*(.*)", line)
            if m_loc and current_folio:
                lnum = m_loc.group(2)
                loc = m_loc.group(3)
                text = m_loc.group(4)
                is_new_para = "<%>" in text
                text_clean = re.sub(r"<[^>]+>", " ", text)
                raw_words = [w.strip() for w in re.split(r"[.\s,]+", text_clean) if w.strip()]
                tok_list = []
                for rw in raw_words:
                    c = canonicalize_token(rw)
                    if not c:
                        continue
                    stem = extract_stem(c)
                    item = {"raw": rw, "canon": c, "stem": stem, "loc": loc, "line": lnum}
                    folios[current_folio]["tokens"].append(item)
                    tok_list.append(item)

                if folios[current_folio]["Q"] == "T" and folios[current_folio]["I"] == "S" and tok_list:
                    if is_new_para or current_recipe is None:
                        current_recipe = {
                            "folio": current_folio,
                            "B": folios[current_folio]["B"],
                            "P": folios[current_folio]["P"],
                            "start_line": lnum,
                            "n_lines": 0,
                            "tokens": [],
                        }
                        recipes.append(current_recipe)
                        folios[current_folio]["recipes"].append(current_recipe)
                    current_recipe["n_lines"] += 1
                    current_recipe["tokens"].extend(tok_list)
    return folios, recipes


def main():
    folios, recipes = parse_zl()

    stem_df = Counter()
    for fol, d in folios.items():
        stems = {t["stem"] for t in d["tokens"] if len(t["stem"]) >= 2}
        for s in stems:
            stem_df[s] += 1
    N_fol = len(folios)
    stem_idf = {s: math.log((N_fol + 1) / (df + 1)) for s, df in stem_df.items() if df <= 50}

    for fol, d in folios.items():
        d["stem_set"] = {t["stem"] for t in d["tokens"] if t["stem"] in stem_idf}

    herbal_fols = [d for d in folios.values() if d["I"] == "H"]
    pharm_fols = [d for d in folios.values() if d["I"] == "P"]
    balneo_fols = [d for d in folios.values() if d["I"] == "B"]
    zodiac_fols = [d for d in folios.values() if d["I"] == "Z"]

    sec_pools = {
        "H": set().union(*(d["stem_set"] for d in herbal_fols)),
        "P": set().union(*(d["stem_set"] for d in pharm_fols)),
        "B": set().union(*(d["stem_set"] for d in balneo_fols)),
        "Z": set().union(*(d["stem_set"] for d in zodiac_fols)),
    }
    sec_pools["HPB"] = sec_pools["H"] | sec_pools["P"] | sec_pools["B"]

    def best_match(s_set, candidates):
        bf, bsc, bsh = None, -1.0, []
        for c in candidates:
            sh = sorted(s_set & c["stem_set"], key=lambda s: -stem_idf[s])
            sc = sum(stem_idf[s] for s in sh)
            if sc > bsc:
                bsc, bf, bsh = sc, f"{c['folio']}(L={c['L']})", sh[:3]
        return {"folio": bf, "idf": round(bsc, 3), "shared_stems": bsh}

    regimen_counts = Counter()
    recipe_records = []
    for idx, r in enumerate(recipes, 1):
        toks = r["tokens"]
        n = len(toks)
        s_set = {t["stem"] for t in toks if t["stem"] in stem_idf}
        r["stem_set"] = s_set

        qo_cnt = sum(1 for t in toks if t["canon"].startswith("q-"))
        edy_cnt = sum(1 for t in toks if t["canon"].endswith("edy") or t["canon"].endswith("EEdy"))
        eedy_cnt = sum(1 for t in toks if "EE" in t["canon"] and (t["canon"].endswith("EEdy") or t["canon"].endswith("EEy")))
        l_ol_cnt = sum(1 for t in toks if t["canon"].startswith("l") or t["canon"].startswith("ol") or t["canon"].endswith("ol") or t["canon"].endswith("al"))
        aiin_cnt = sum(1 for t in toks if t["canon"].endswith("IIN"))

        n_verbs = sum(1 for t in toks if t["canon"].startswith("q-") or t["canon"].endswith("edy") or t["canon"].endswith("EEdy"))
        n_doses = sum(1 for t in toks if t["canon"].endswith("IIN") or t["canon"].endswith("ol") or t["canon"].endswith("or") or t["canon"].endswith("al") or t["canon"].endswith("ar"))

        qo_pct = round(100.0 * qo_cnt / n, 2)
        edy_pct = round(100.0 * edy_cnt / n, 2)
        eedy_pct = round(100.0 * eedy_cnt / n, 2)
        l_ol_pct = round(100.0 * l_ol_cnt / n, 2)
        aiin_pct = round(100.0 * aiin_cnt / n, 2)

        if n <= 24:
            regimen = "SIMPLE_SPECIFIC_RECIPE"
        elif aiin_cnt >= 8 or n >= 55:
            regimen = "STOICHIOMETRIC_MULTI_COMPOUND"
        elif l_ol_pct >= 24.0:
            regimen = "AQUEOUS_LOTION_INFUSION"
        else:
            regimen = "INTENSIVE_BOILED_DECOCTION"
        regimen_counts[regimen] += 1

        hpb_idf = round(sum(stem_idf[s] for s in (s_set & sec_pools["HPB"])), 3)
        r["hpb_idf"] = hpb_idf
        r["morph"] = {
            "qo_pct": qo_pct,
            "edy_pct": edy_pct,
            "eedy_pct": eedy_pct,
            "l_ol_pct": l_ol_pct,
            "aiin_pct": aiin_pct,
            "n_verbs": n_verbs,
            "n_doses": n_doses,
            "verb_dose_ratio": round(n_verbs / max(n_doses, 1), 3),
        }

        m_h = best_match(s_set, herbal_fols)
        m_p = best_match(s_set, pharm_fols)
        m_b = best_match(s_set, balneo_fols)

        recipe_records.append({
            "recipe_id": f"R_{idx:03d}",
            "locus": f"<{r['folio']}.{r['start_line']}>",
            "folio": r["folio"],
            "bifolio_B": r["B"],
            "n_lines": r["n_lines"],
            "n_tokens": n,
            "n_unique_stems": len(s_set),
            "regimen_class": regimen,
            "hpb_idf": hpb_idf,
            "morph": r["morph"],
            "best_herbal": m_h,
            "best_pharm": m_p,
            "best_balneo": m_b,
            "opening_eva": " . ".join(t["raw"] for t in toks[:7]),
            "opening_gloss": " | ".join(gloss_token(t["raw"], t["canon"], t["stem"]) for t in toks[:6]),
        })

    # Group by Bifolio $B = 1..6 and Shell Tier
    by_b = defaultdict(list)
    for rec in recipe_records:
        by_b[rec["bifolio_B"]].append(rec)

    def summarize_recipes(rlist):
        nr = len(rlist)
        if nr == 0:
            return {}
        return {
            "n_recipes": nr,
            "mean_tokens": round(sum(x["n_tokens"] for x in rlist) / nr, 2),
            "mean_unique_stems": round(sum(x["n_unique_stems"] for x in rlist) / nr, 2),
            "mean_hpb_idf": round(sum(x["hpb_idf"] for x in rlist) / nr, 3),
            "mean_qo_pct": round(sum(x["morph"]["qo_pct"] for x in rlist) / nr, 2),
            "mean_edy_pct": round(sum(x["morph"]["edy_pct"] for x in rlist) / nr, 2),
            "mean_eedy_pct": round(sum(x["morph"]["eedy_pct"] for x in rlist) / nr, 2),
            "mean_l_ol_pct": round(sum(x["morph"]["l_ol_pct"] for x in rlist) / nr, 2),
            "mean_aiin_pct": round(sum(x["morph"]["aiin_pct"] for x in rlist) / nr, 2),
            "mean_verb_dose_ratio": round(sum(x["morph"]["verb_dose_ratio"] for x in rlist) / nr, 3),
        }

    bifolio_summary = {f"B={b}": summarize_recipes(by_b[b]) for b in sorted(by_b.keys())}
    shell_summary = {
        "OUTER_SHELL_B1_B2 (f103,f104,f115,f116)": summarize_recipes(by_b[1] + by_b[2]),
        "MID_SHELL_B3_B4 (f105,f106,f113,f114)": summarize_recipes(by_b[3] + by_b[4]),
        "INNER_CORE_B5_B6 (f107,f108,f111,f112)": summarize_recipes(by_b[5] + by_b[6]),
    }

    # Permutation Test 1: B=6 Innermost Centerfold (f108/f111, n=35) Recipe Length & HPB IDF
    b6_recs = by_b[6]
    obs_b6_len = sum(x["n_tokens"] for x in b6_recs) / len(b6_recs)
    obs_b6_idf = sum(x["hpb_idf"] for x in b6_recs) / len(b6_recs)
    null_b6_len, null_b6_idf = [], []
    for _ in range(1000):
        samp = random.sample(recipe_records, len(b6_recs))
        null_b6_len.append(sum(x["n_tokens"] for x in samp) / len(b6_recs))
        null_b6_idf.append(sum(x["hpb_idf"] for x in samp) / len(b6_recs))
    mu_len = sum(null_b6_len) / 1000.0
    sd_len = math.sqrt(sum((x - mu_len) ** 2 for x in null_b6_len) / 1000.0) or 1e-9
    z_b6_len = (obs_b6_len - mu_len) / sd_len
    mu_idf = sum(null_b6_idf) / 1000.0
    sd_idf = math.sqrt(sum((x - mu_idf) ** 2 for x in null_b6_idf) / 1000.0) or 1e-9
    z_b6_idf = (obs_b6_idf - mu_idf) / sd_idf

    # Permutation Test 2: Mid-Shell B=3,4 (f105,f106,f113,f114, n=106) Measured -aiin Dosing Rate
    mid_recs = by_b[3] + by_b[4]
    obs_mid_aiin = sum(x["morph"]["aiin_pct"] for x in mid_recs) / len(mid_recs)
    null_mid_aiin = []
    for _ in range(1000):
        samp = random.sample(recipe_records, len(mid_recs))
        null_mid_aiin.append(sum(x["morph"]["aiin_pct"] for x in samp) / len(mid_recs))
    mu_aiin = sum(null_mid_aiin) / 1000.0
    sd_aiin = math.sqrt(sum((x - mu_aiin) ** 2 for x in null_mid_aiin) / 1000.0) or 1e-9
    z_mid_aiin = (obs_mid_aiin - mu_aiin) / sd_aiin

    perm_tests = {
        "b6_centerfold_recipe_length": {
            "n_b6_recipes": len(b6_recs),
            "observed_mean_tokens": round(obs_b6_len, 2),
            "rest_of_quire20_mean_tokens": round(sum(x["n_tokens"] for x in recipe_records if x["bifolio_B"] != 6) / (len(recipe_records) - len(b6_recs)), 2),
            "lift_over_rest": round(obs_b6_len / (sum(x["n_tokens"] for x in recipe_records if x["bifolio_B"] != 6) / (len(recipe_records) - len(b6_recs))), 2),
            "null_mean": round(mu_len, 2),
            "null_std": round(sd_len, 2),
            "z_score": round(z_b6_len, 2),
        },
        "b6_centerfold_hpb_idf": {
            "observed_mean_hpb_idf": round(obs_b6_idf, 3),
            "null_mean": round(mu_idf, 3),
            "null_std": round(sd_idf, 3),
            "z_score": round(z_b6_idf, 2),
        },
        "mid_shell_b3_b4_aiin_dosing_surge": {
            "n_mid_recipes": len(mid_recs),
            "observed_mean_aiin_pct": round(obs_mid_aiin, 2),
            "null_mean_aiin_pct": round(mu_aiin, 2),
            "null_std_aiin_pct": round(sd_aiin, 2),
            "z_score": round(z_mid_aiin, 2),
        },
    }

    # Folio-by-folio summary across all 23 Quire T Starred Recipe folios
    qt_fols = sorted(
        [d for d in folios.values() if d["Q"] == "T" and d["I"] == "S"],
        key=lambda x: x["P"],
    )
    folio_summary = []
    for d in qt_fols:
        f_recs = [x for x in recipe_records if x["folio"] == d["folio"]]
        folio_summary.append({
            "folio": d["folio"],
            "bifolio_B": d["B"],
            "page_P": d["P"],
            "n_recipes": len(f_recs),
            "n_tokens": len(d["tokens"]),
            "mean_recipe_tokens": round(len(d["tokens"]) / max(len(f_recs), 1), 2),
            "mean_recipe_hpb_idf": round(sum(x["hpb_idf"] for x in f_recs) / max(len(f_recs), 1), 3),
            "best_herbal": best_match(d["stem_set"], herbal_fols)["folio"],
            "best_pharm": best_match(d["stem_set"], pharm_fols)["folio"],
            "best_balneo": best_match(d["stem_set"], balneo_fols)["folio"],
        })

    out = {
        "attack": "Attack 127 (Phase 138 / Discovery 144)",
        "title": "Complete 285-Recipe Quire 20 (f103r-f116r) Starred Clinical Recipe Master Catalogue & 6-Bifolio Nested Compounding Law",
        "total_recipes": len(recipe_records),
        "regimen_class_distribution": dict(regimen_counts),
        "permutation_tests": perm_tests,
        "bifolio_summary": bifolio_summary,
        "shell_tier_summary": shell_summary,
        "folio_summary_23": folio_summary,
        "recipe_catalogue": recipe_records,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/attack127_quire20_292recipe_master_catalogue_and_bifolio_law.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== ATTACK 127 SUMMARY ===")
    print(f"Total Quire 20 Starred Recipes: {len(recipe_records)}")
    print("Regimen Classes:", dict(regimen_counts))
    print("Permutation Tests:", json.dumps(perm_tests, indent=2))
    print("Shell Tier Summary:", json.dumps(shell_summary, indent=2))
    print("Bifolio Summary:", json.dumps(bifolio_summary, indent=2))


if __name__ == "__main__":
    main()
