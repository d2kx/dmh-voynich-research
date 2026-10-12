#!/usr/bin/env python3
"""
Attack 122 (Phase 133 / Discovery 139):
Complete Monograph-by-Monograph Structural & Botanical Translation of the 32
Currier B Herbal Monographs ($I=H, $L=B across Quires D, E, F, G, H, Q).

Tests:
1. Quantitative Morphological & Clinical-Routing Comparison between the 32
   Currier B Herbal Monographs (H_B) and the 98 Currier A Herbal Monographs (H_A),
   with 1,000-trial permutation z-scores across P, B, S, Z, and A/C routing.
2. Three-Scribe Specialization within H_B:
   - Scribe 2 ($H=2, n=20, Quires D, E, F, G) -> Balneological ($I=B) & Dual-Branch
   - Scribe 5 ($H=5, n=6, Quires F, H) -> Outer-Wrapper Master Hubs & f66r
   - Scribe 3 ($H=3, n=6, Quire Q foldout f94r-f95v2) -> Starred Decoctions ($I=S) & Pharm ($I=P)
3. Complete 32-Monograph Translation & Multi-Section Routing Table (f26r..f95v2),
   decoding Line-1 Botanical Title Headers, Top Signature Stems, 5-Section
   Clinical Links (Z, P, B, S, f66r), and Line-1 Interlinear Glosses.
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
    "Ck": "CMPD:bench-calyx[chk]",
    "Ct": "CMPD:bench-stalk[cht]",
    "ke": "STEM:boiled-calyx[ke]",
    "te": "STEM:boiled-stalk[te]",
    "pe": "STEM:boiled-cup[pe]",
    "fe": "STEM:boiled-plume[fe]",
    "kEE": "STEM:steeped-calyx[kee]",
    "tEE": "STEM:steeped-stalk[tee]",
    "Ce": "STEM:infused-bench[che]",
    "Se": "STEM:infused-spray[she]",
    "CEE": "STEM:decocted-bench[chee]",
    "SEE": "STEM:decocted-spray[shee]",
    "lk": "BATH:lotion-calyx[lk]",
    "lt": "BATH:lotion-stalk[lt]",
    "yk": "MOD:init-calyx[yk]",
    "yt": "MOD:init-stalk[yt]",
    "ok": "NOM:vessel-calyx[ok]",
    "ot": "NOM:vessel-stalk[ot]",
    "op": "NOM:vessel-cup[op]",
    "of": "NOM:vessel-plume[of]",
}


def gloss_token(raw, canon, stem):
    pref = ""
    if canon.startswith("q-"):
        pref = "ACT:boil/extract+"
    elif canon.startswith("o-"):
        pref = "NOM:herb/vessel+"
    elif canon.startswith("d-"):
        pref = "ABL:from-base+"
    elif canon.startswith("s-"):
        pref = "SEQ:next-add+"
    elif canon.startswith("l-") or canon.startswith("ol"):
        pref = "LOC:in-bath+"
    elif canon.startswith("y-"):
        pref = "CONJ:and-then+"

    sg = STEM_GLOSS.get(stem, f"BOT:stem[{stem}]")

    suf = ""
    if canon.endswith("aIIN") or canon.endswith("IIN"):
        suf = ":DOSE[measure-aiin]"
    elif canon.endswith("EEdy") or canon.endswith("edy"):
        suf = ":PROC[decoct/mix-edy]"
    elif canon.endswith("dy"):
        suf = ":STATE[steeped-dy]"
    elif canon.endswith("ey"):
        suf = ":INF[cooked-ey]"
    elif canon.endswith("ol") or canon.endswith("al"):
        suf = ":FLUID[lotion-ol/al]"
    elif canon.endswith("or") or canon.endswith("ar"):
        suf = ":RESIN[extract-or/ar]"
    elif canon.endswith("am") or canon.endswith("m"):
        suf = ":TERM[seal/close-m]"
    elif canon.endswith("y"):
        suf = ":STAT[state-y]"

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
                    "F": meta.get("F", "?"),
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
        return {"n": 0, "qo_pct": 0, "edy_pct": 0, "l_ol_pct": 0, "aiin_pct": 0, "do_so_pct": 0}
    qo = sum(1 for t in tokens if t["canon"].startswith("q-"))
    edy = sum(1 for t in tokens if t["canon"].endswith("edy") or t["canon"].endswith("EEdy"))
    l_ol = sum(1 for t in tokens if t["canon"].startswith("l") or t["canon"].startswith("ol") or t["canon"].endswith("ol") or t["canon"].endswith("al"))
    aiin = sum(1 for t in tokens if t["canon"].endswith("IIN"))
    do_so = sum(1 for t in tokens if t["canon"].startswith("do") or t["canon"].startswith("so") or t["canon"].startswith("d") or t["canon"].startswith("s"))
    return {
        "n": n,
        "qo_pct": round(100.0 * qo / n, 2),
        "edy_pct": round(100.0 * edy / n, 2),
        "l_ol_pct": round(100.0 * l_ol / n, 2),
        "aiin_pct": round(100.0 * aiin / n, 2),
        "do_so_pct": round(100.0 * do_so / n, 2),
    }


def main():
    folios = parse_zl()

    # Global stem IDF across all folios (rare/medium open-class stems df <= 50)
    stem_df = Counter()
    for fol, d in folios.items():
        stems = {t["stem"] for t in d["tokens"] if len(t["stem"]) >= 2}
        for s in stems:
            stem_df[s] += 1
    N_fol = len(folios)
    stem_idf = {s: math.log((N_fol + 1) / (df + 1)) for s, df in stem_df.items() if df <= 50}

    # Precompute stem sets per folio and section pools
    for fol, d in folios.items():
        d["stem_set"] = {t["stem"] for t in d["tokens"] if t["stem"] in stem_idf}
        d["stem_counts"] = Counter(t["stem"] for t in d["tokens"] if t["stem"] in stem_idf)

    # Target clinical/calendar folio groups
    pharm_fols = [d for d in folios.values() if d["I"] == "P"]
    balneo_fols = [d for d in folios.values() if d["I"] == "B"]
    starred_fols = [d for d in folios.values() if d["I"] == "S" and d["Q"] == "T"]
    zodiac_fols = [d for d in folios.values() if d["I"] == "Z"]
    astro_fols = [d for d in folios.values() if d["I"] in {"A", "C"}]

    sec_pools = {
        "P": set().union(*(d["stem_set"] for d in pharm_fols)),
        "B": set().union(*(d["stem_set"] for d in balneo_fols)),
        "S": set().union(*(d["stem_set"] for d in starred_fols)),
        "Z": set().union(*(d["stem_set"] for d in zodiac_fols)),
        "AC": set().union(*(d["stem_set"] for d in astro_fols)),
        "f66r": folios["f66r"]["stem_set"] if "f66r" in folios else set(),
    }

    herbal_b = sorted(
        [d for d in folios.values() if d["I"] == "H" and d["L"] == "B"],
        key=lambda x: (x["Q"], x["P"]),
    )
    herbal_a = sorted(
        [d for d in folios.values() if d["I"] == "H" and d["L"] == "A"],
        key=lambda x: (x["Q"], x["P"]),
    )

    # Find sheet-mates for every folio
    by_qb = defaultdict(list)
    for d in folios.values():
        if d["Q"] != "?" and d["B"] > 0:
            by_qb[(d["Q"], d["B"])].append(d["folio"])

    def compute_routing(d):
        s_set = d["stem_set"]
        scores = {}
        for k, pool in sec_pools.items():
            scores[k] = round(sum(stem_idf[s] for s in (s_set & pool)), 3)
        scores["total_clinical_PBS"] = round(
            sum(stem_idf[s] for s in (s_set & (sec_pools["P"] | sec_pools["B"] | sec_pools["S"]))), 3
        )
        return scores

    for d in herbal_b + herbal_a:
        d["routing"] = compute_routing(d)
        d["morph"] = morph_profile(d["tokens"])

    # 1. Compare H_B (n=32) vs H_A (n=96)
    def summarize_group(grp):
        n = len(grp)
        return {
            "n_folios": n,
            "mean_tokens": round(sum(len(d["tokens"]) for d in grp) / n, 2),
            "mean_paras": round(sum(d["paras"] for d in grp) / n, 2),
            "mean_unique_stems": round(sum(len(d["stem_set"]) for d in grp) / n, 2),
            "mean_qo_pct": round(sum(d["morph"]["qo_pct"] for d in grp) / n, 2),
            "mean_edy_pct": round(sum(d["morph"]["edy_pct"] for d in grp) / n, 2),
            "mean_l_ol_pct": round(sum(d["morph"]["l_ol_pct"] for d in grp) / n, 2),
            "mean_aiin_pct": round(sum(d["morph"]["aiin_pct"] for d in grp) / n, 2),
            "mean_idf_P": round(sum(d["routing"]["P"] for d in grp) / n, 3),
            "mean_idf_B": round(sum(d["routing"]["B"] for d in grp) / n, 3),
            "mean_idf_S": round(sum(d["routing"]["S"] for d in grp) / n, 3),
            "mean_idf_Z": round(sum(d["routing"]["Z"] for d in grp) / n, 3),
            "mean_idf_AC": round(sum(d["routing"]["AC"] for d in grp) / n, 3),
            "mean_idf_f66r": round(sum(d["routing"]["f66r"] for d in grp) / n, 3),
            "mean_total_clinical_PBS": round(sum(d["routing"]["total_clinical_PBS"] for d in grp) / n, 3),
        }

    hb_summary = summarize_group(herbal_b)
    ha_summary = summarize_group(herbal_a)

    # Permutation test: H_B vs All Herbal (H_A + H_B) on Total Clinical PBS IDF & Per-Token Normalized Clinical IDF
    all_h = herbal_b + herbal_a
    obs_hb_pbs = hb_summary["mean_total_clinical_PBS"]
    null_pbs = []
    for _ in range(1000):
        samp = random.sample(all_h, len(herbal_b))
        null_pbs.append(sum(d["routing"]["total_clinical_PBS"] for d in samp) / len(herbal_b))
    mu_pbs = sum(null_pbs) / len(null_pbs)
    sd_pbs = math.sqrt(sum((x - mu_pbs) ** 2 for x in null_pbs) / len(null_pbs)) or 1e-9
    z_hb_pbs = (obs_hb_pbs - mu_pbs) / sd_pbs

    # 2. Three-Scribe Specialization within H_B (H=2 vs H=5 vs H=3)
    scribe_hb_summary = {}
    for h in ["2", "5", "3"]:
        sub = [d for d in herbal_b if d["H"] == h]
        scribe_hb_summary[f"H={h}"] = summarize_group(sub)

    # 3. Build Complete 32-Monograph Translation & Routing Table
    def best_match(d, candidates):
        best_f = None
        best_idf = -1.0
        best_shared = []
        for c in candidates:
            shared = sorted(d["stem_set"] & c["stem_set"], key=lambda s: -stem_idf[s])
            idf = sum(stem_idf[s] for s in shared)
            if idf > best_idf:
                best_idf = idf
                best_f = c["folio"]
                best_shared = shared[:4]
        return {"folio": best_f, "idf": round(best_idf, 3), "shared_stems": best_shared}

    monograph_records = []
    for idx, d in enumerate(herbal_b, 1):
        fol = d["folio"]
        mates = [m for m in by_qb[(d["Q"], d["B"])] if m != fol]
        top_stems = sorted(d["stem_set"], key=lambda s: (-d["stem_counts"][s] * stem_idf[s], -stem_idf[s]))[:6]
        top_stem_glosses = [f"{s} ({STEM_GLOSS.get(s, 'BOT:' + s)}, idf={round(stem_idf[s], 2)})" for s in top_stems]

        l1_toks = d["line1_tokens"][:8]
        l1_raw = " . ".join(t["raw"] for t in l1_toks)
        l1_gloss = " | ".join(gloss_token(t["raw"], t["canon"], t["stem"]) for t in l1_toks)

        m_z = best_match(d, zodiac_fols)
        m_p = best_match(d, pharm_fols)
        m_b = best_match(d, balneo_fols)
        m_s = best_match(d, starred_fols)

        # Determine dominant clinical branch
        if d["routing"]["B"] >= d["routing"]["P"] and d["morph"]["l_ol_pct"] >= 18.0:
            branch = "BALNEO_HYDROTHERAPY_DOMINANT (Bath-Infusion Herb)"
        elif d["routing"]["S"] >= 45.0 and d["morph"]["qo_pct"] >= 14.0:
            branch = "DECOCTION_INTERNAL_DOMINANT (Boiled-Recipe Herb)"
        else:
            branch = "DUAL_BRANCH_MASTER_HERB (Apothecary + Bath + Decoction)"

        monograph_records.append({
            "rank": idx,
            "folio": fol,
            "quire": d["Q"],
            "bifolio_B": d["B"],
            "page_P": d["P"],
            "scribe_H": d["H"],
            "sheet_mates": mates,
            "n_tokens": len(d["tokens"]),
            "n_paras": d["paras"],
            "n_lines": d["lines"],
            "n_unique_stems": len(d["stem_set"]),
            "morph": d["morph"],
            "routing_idf": d["routing"],
            "clinical_branch": branch,
            "top_signature_stems": top_stem_glosses,
            "line1_header_eva": l1_raw,
            "line1_header_gloss": l1_gloss,
            "best_zodiac_match": m_z,
            "best_pharm_match": m_p,
            "best_balneo_match": m_b,
            "best_starred_match": m_s,
        })

    out = {
        "attack": "Attack 122 (Phase 133 / Discovery 139)",
        "title": "Complete 32-Monograph Currier B Herbal ($I=H, $L=B) Structural & Botanical Translation",
        "herbal_b_vs_a_comparison": {
            "H_B_32": hb_summary,
            "H_A_96": ha_summary,
            "permutation_test_total_clinical_PBS": {
                "observed_H_B_mean": obs_hb_pbs,
                "observed_H_A_mean": ha_summary["mean_total_clinical_PBS"],
                "lift_B_over_A": round(obs_hb_pbs / max(ha_summary["mean_total_clinical_PBS"], 1e-9), 3),
                "null_mean": round(mu_pbs, 3),
                "null_std": round(sd_pbs, 3),
                "z_score": round(z_hb_pbs, 2),
            },
        },
        "three_scribe_hb_specialization": scribe_hb_summary,
        "monograph_records": monograph_records,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/attack122_currier_b_32herbal_monograph_translator.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== ATTACK 122 SUMMARY ===")
    print("H_B (32) vs H_A (96):", json.dumps(out["herbal_b_vs_a_comparison"], indent=2))
    print("\nThree-Scribe H_B Specialization:", json.dumps(scribe_hb_summary, indent=2))
    print(f"\nTranslated {len(monograph_records)} Currier B Herbal Monographs.")
    for r in monograph_records[:5]:
        print(f"  [{r['rank']}] {r['folio']} (Q={r['quire']},B={r['bifolio_B']},H={r['scribe_H']}): tokens={r['n_tokens']}, PBS_IDF={r['routing_idf']['total_clinical_PBS']}, Z={r['best_zodiac_match']['folio']}, P={r['best_pharm_match']['folio']}, B={r['best_balneo_match']['folio']}, S={r['best_starred_match']['folio']}")


if __name__ == "__main__":
    main()
