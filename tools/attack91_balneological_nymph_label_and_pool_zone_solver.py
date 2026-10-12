#!/usr/bin/env python3
"""
Attack 91 (Phase 102 / Discovery 108): Balneological (`Quire M`, `f75r–f84v`) Nymph-Label
(`@Ln / @Lb`) & Vertical Hydraulic Flow Zone (`P_TOP` Inflow -> `P_MID` Pipe/Mixing ->
`P_BOT` Lower Pool) Grammar Solver

Tests across all `20` folios of Quire M (`$I=B, $L=B, $H=2`, `f75r–f84v`):
1. **Nymph & Pipe Labels (`@Ln / @Lb`, `n = 113` tokens) vs. Biological Prose (`@P`, `n = 6,800+` tokens)**:
   - Quantifies the exact morphological transformation between `@Ln` Nymph Labels and `@P` Biological Prose:
     * `PFX_O_NOM` (`o-`) vs. `PFX_QO_ACT` (`qo-`) vs. `PFX_L_APPL` (`l-/ol-/qol-`)
     * `T_CLASS` (`t/p`, `otedy, otol, otar`) vs. `K_CLASS` (`k/f`, `qokedy, qokeedy, olkedy`)
   - Measures what fraction of `@Ln` Nymph Labels (`exact, q-proclitic, or canonical stem`) recur
     directly in the prose of the **same Biological folio** and **same Bifolio Sheet (`$B in 1..5`)**.
2. **Vertical Hydraulic Flow Gradient (`P_TOP` Upper Canopy/Inflow -> `P_MID` Pipe/Stream -> `P_BOT` Lower Pool)**:
   - Segments all multi-paragraph Biological folios into `P_TOP` (first paragraph at top of folio),
     `P_MID` (interior paragraphs), and `P_BOT` (final paragraph at bottom of folio alongside the lower pool).
   - Evaluates a 500-trial within-folio permutation test on the vertical gradient from `P_TOP -> P_MID -> P_BOT`
     across `qo-` active operators, `l-/ol-/qol-` liquid applicatives, `K_CLASS` vs. `T_CLASS`,
     `-edy/-dy` vs. `-ol/-al` liquid codas, and `-am/-m` colophon closers!
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
OUT_JSON = DATA_DIR / "attack91_balneological_nymph_label_and_pool_zone_solver.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str):
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def canonical_form(w: str) -> str:
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
    return s


def para_profile(words: list) -> dict:
    n = max(len(words), 1)
    return {
        "n_words": len(words),
        "top_pf_init": 1.0 if (words and any(g in words[0][:3] for g in ("p", "f"))) else 0.0,
        "am_colophon": 1.0 if (words and words[-1].endswith(("am", "om", "em", "im", "m"))) else 0.0,
        "qo_rate": sum(1 for w in words if w.startswith("q")) / n,
        "l_appl_rate": sum(1 for w in words if w.startswith(("l", "ol", "qol", "dal")) and len(w) > 3) / n,
        "o_nom_rate": sum(1 for w in words if w.startswith("o") and len(w) > 2) / n,
        "s_y_init_rate": sum(1 for w in words if w.startswith(("s", "y"))) / n,
        "k_class_rate": sum(1 for w in words if any(g in w for g in ("k", "f"))) / n,
        "t_class_rate": sum(1 for w in words if any(g in w for g in ("t", "p"))) / n,
        "ch_sh_bench_rate": sum(1 for w in words if ("ch" in w or "sh" in w) and not any(g in w for g in ("k", "t", "p", "f"))) / n,
        "dy_rate": sum(1 for w in words if w.endswith("dy")) / n,
        "y_bare_rate": sum(1 for w in words if w.endswith("y") and not w.endswith("dy")) / n,
        "in_meas_rate": sum(1 for w in words if w.endswith(("aiin", "ain", "oiin", "in"))) / n,
        "liq_l_rate": sum(1 for w in words if w.endswith(("ol", "al"))) / n,
        "liq_r_rate": sum(1 for w in words if w.endswith(("or", "ar"))) / n,
    }


def main():
    bio_folios = {}
    cur_folio = None
    cur_sec = None
    cur_para = []

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        raw_s = raw_line.strip()
        if not raw_s or raw_s.startswith("#"):
            continue
        if raw_s.startswith("<f") and ">" in raw_s and "." not in raw_s.split(">")[0]:
            if cur_folio and cur_sec == "B" and cur_para:
                bio_folios[cur_folio]["paras"].append(list(cur_para))
                cur_para = []
            cur_folio = raw_s.split(">")[0][1:]
            tags = dict(re.findall(r"\$([A-Z])=([0-9A-Za-z]+)", raw_s))
            cur_sec = tags.get("I", "U")
            if cur_sec == "B":
                bio_folios[cur_folio] = {
                    "folio": cur_folio,
                    "Q": tags.get("Q", "U"),
                    "B": tags.get("B", "U"),
                    "L": tags.get("L", "U"),
                    "H": tags.get("H", "U"),
                    "labels": [],
                    "paras": [],
                    "all_prose": [],
                }
            continue
        m = LOCUS_RE.match(raw_s)
        if m and cur_folio is not None and cur_sec == "B":
            lnum, ltype_raw, raw_text = m.group(2), m.group(3), m.group(4)
            lt = ltype_raw.lstrip("@+*=")
            toks = clean_tokens(raw_text)
            if not toks:
                continue
            if lt.startswith("L"):
                for w in toks:
                    if len(w) >= 2:
                        bio_folios[cur_folio]["labels"].append((lnum, ltype_raw, w))
            elif lt.startswith("P"):
                if ("<%>" in raw_text or ltype_raw.startswith(("@", "*"))) and cur_para:
                    bio_folios[cur_folio]["paras"].append(list(cur_para))
                    cur_para = []
                cur_para.extend(toks)
                bio_folios[cur_folio]["all_prose"].extend(toks)
                if "<$>" in raw_text and cur_para:
                    bio_folios[cur_folio]["paras"].append(list(cur_para))
                    cur_para = []

    if cur_folio and cur_sec == "B" and cur_para:
        bio_folios[cur_folio]["paras"].append(list(cur_para))

    # 1. Nymph Label (@Ln/@Lb) vs Biological Prose (@P) Comparison & Same-Page / Same-Bifolio Match
    all_nymph_labels = [w for fd in bio_folios.values() for _, _, w in fd["labels"]]
    all_bio_prose = [w for fd in bio_folios.values() for w in fd["all_prose"]]

    bifolia_prose = defaultdict(set)
    bifolia_canon = defaultdict(set)
    for fd in bio_folios.values():
        fd["prose_set"] = set(fd["all_prose"])
        fd["canon_set"] = {canonical_form(w) for w in fd["all_prose"]}
        bifolia_prose[fd["B"]].update(fd["prose_set"])
        bifolia_canon[fd["B"]].update(fd["canon_set"])

    same_page_exact_q = 0
    same_page_canon = 0
    same_bifolio_canon = 0
    same_section_canon = 0
    all_bio_canon = {canonical_form(w) for w in all_bio_prose}

    nymph_bridges = []
    for fname, fd in sorted(bio_folios.items()):
        for lnum, ltype_raw, w_lbl in fd["labels"]:
            q_form = "q" + w_lbl if w_lbl.startswith("o") else "qo" + w_lbl
            cw = canonical_form(w_lbl)
            if cw in all_bio_canon:
                same_section_canon += 1
            if cw in bifolia_canon[fd["B"]]:
                same_bifolio_canon += 1
            if w_lbl in fd["prose_set"] or q_form in fd["prose_set"]:
                same_page_exact_q += 1
                same_page_canon += 1
                matches = sorted({pw for pw in fd["all_prose"] if pw in (w_lbl, q_form) or canonical_form(pw) == cw})
                nymph_bridges.append({
                    "folio": fname,
                    "bifolio": fd["B"],
                    "locus": f"<{fname}.{lnum},{ltype_raw}>",
                    "nymph_label": w_lbl,
                    "match_type": "EXACT_OR_Q_PROCLITIC",
                    "same_page_prose_forms": matches[:5],
                })
            elif cw in fd["canon_set"]:
                same_page_canon += 1
                matches = sorted({pw for pw in fd["all_prose"] if canonical_form(pw) == cw})
                nymph_bridges.append({
                    "folio": fname,
                    "bifolio": fd["B"],
                    "locus": f"<{fname}.{lnum},{ltype_raw}>",
                    "nymph_label": w_lbl,
                    "match_type": "CANONICAL_STEM",
                    "same_page_prose_forms": matches[:5],
                })

    n_lbl = max(len(all_nymph_labels), 1)

    # 2. Vertical Hydraulic Flow Gradient across Multi-Paragraph Biological Folios (P_TOP -> P_MID -> P_BOT)
    zone_paras = defaultdict(list)
    multi_para_folios = []
    for fname, fd in sorted(bio_folios.items()):
        valid_p = [p for p in fd["paras"] if len(p) >= 15]
        if len(valid_p) < 2:
            continue
        multi_para_folios.append(valid_p)
        for i, p in enumerate(valid_p):
            pf = para_profile(p)
            pf["folio"] = fname
            if i == 0:
                zone_paras["P_TOP_INFLOW"].append(pf)
            elif i == len(valid_p) - 1:
                zone_paras["P_BOT_POOL"].append(pf)
            else:
                zone_paras["P_MID_PIPE_STREAM"].append(pf)

    keys_avg = (
        "n_words", "top_pf_init", "am_colophon", "qo_rate", "l_appl_rate", "o_nom_rate",
        "s_y_init_rate", "k_class_rate", "t_class_rate", "ch_sh_bench_rate",
        "dy_rate", "y_bare_rate", "in_meas_rate", "liq_l_rate", "liq_r_rate"
    )
    zone_summary = {}
    for zn in ("P_TOP_INFLOW", "P_MID_PIPE_STREAM", "P_BOT_POOL"):
        plist = zone_paras[zn]
        m = max(len(plist), 1)
        zone_summary[zn] = {k: round(sum(p[k] for p in plist) / m, 4) for k in keys_avg}
        zone_summary[zn]["n_paragraphs"] = len(plist)

    # Top enriched words in P_TOP_INFLOW vs P_BOT_POOL
    top_words_p_top = Counter(w for p in multi_para_folios for w in p[0])
    top_words_p_bot = Counter(w for p in multi_para_folios for w in p[-1])
    nt = sum(top_words_p_top.values())
    nb = sum(top_words_p_bot.values())

    p_top_characteristic = []
    p_bot_characteristic = []
    for w in set(top_words_p_top.keys()) | set(top_words_p_bot.keys()):
        ct = top_words_p_top[w]
        cb = top_words_p_bot[w]
        if ct + cb < 8:
            continue
        rt = (ct + 0.5) / nt
        rb = (cb + 0.5) / nb
        if rt / rb >= 1.5:
            p_top_characteristic.append({"word": w, "p_top_count": ct, "p_bot_count": cb, "lift": round(rt / rb, 2)})
        elif rb / rt >= 1.5:
            p_bot_characteristic.append({"word": w, "p_bot_count": cb, "p_top_count": ct, "lift": round(rb / rt, 2)})

    p_top_characteristic.sort(key=lambda x: -x["lift"])
    p_bot_characteristic.sort(key=lambda x: -x["lift"])

    # Within-Folio Permutation Test (500 trials) for P_TOP vs P_BOT drop in qo_rate and dy_rate
    obs_qo_drop = zone_summary["P_TOP_INFLOW"]["qo_rate"] - zone_summary["P_BOT_POOL"]["qo_rate"]
    obs_dy_drop = zone_summary["P_TOP_INFLOW"]["dy_rate"] - zone_summary["P_BOT_POOL"]["dy_rate"]
    rng = random.Random(91)
    null_qo_drops = []
    null_dy_drops = []
    for _ in range(500):
        t_qos, b_qos, t_dys, b_dys = [], [], [], []
        for p_list in multi_para_folios:
            sh_p = list(p_list)
            rng.shuffle(sh_p)
            pf_t = para_profile(sh_p[0])
            pf_b = para_profile(sh_p[-1])
            t_qos.append(pf_t["qo_rate"])
            b_qos.append(pf_b["qo_rate"])
            t_dys.append(pf_t["dy_rate"])
            b_dys.append(pf_b["dy_rate"])
        null_qo_drops.append(sum(t_qos) / len(t_qos) - sum(b_qos) / len(b_qos))
        null_dy_drops.append(sum(t_dys) / len(t_dys) - sum(b_dys) / len(b_dys))

    def calc_z(obs, nulls):
        m = sum(nulls) / len(nulls)
        sd = math.sqrt(sum((x - m) ** 2 for x in nulls) / len(nulls)) or 1e-9
        return round((obs - m) / sd, 2)

    z_qo_drop = calc_z(obs_qo_drop, null_qo_drops)
    z_dy_drop = calc_z(obs_dy_drop, null_dy_drops)

    out = {
        "nymph_label_vs_prose_summary": {
            "n_nymph_labels": len(all_nymph_labels),
            "n_bio_prose_tokens": len(all_bio_prose),
            "nymph_label_profile": para_profile(all_nymph_labels),
            "bio_prose_profile": para_profile(all_bio_prose),
            "same_page_exact_or_q_pct": round(100.0 * same_page_exact_q / n_lbl, 2),
            "same_page_canonical_pct": round(100.0 * same_page_canon / n_lbl, 2),
            "same_bifolio_canonical_pct": round(100.0 * same_bifolio_canon / n_lbl, 2),
            "same_section_canonical_pct": round(100.0 * same_section_canon / n_lbl, 2),
        },
        "vertical_hydraulic_flow_zones": zone_summary,
        "vertical_gradient_permutation_test": {
            "obs_qo_drop_top_minus_bot": round(obs_qo_drop, 4),
            "z_score_qo_drop": z_qo_drop,
            "obs_dy_drop_top_minus_bot": round(obs_dy_drop, 4),
            "z_score_dy_drop": z_dy_drop,
        },
        "p_top_inflow_characteristic_words": p_top_characteristic[:12],
        "p_bot_pool_characteristic_words": p_bot_characteristic[:12],
        "same_page_nymph_to_prose_bridges": nymph_bridges[:25],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Nymph Label vs Prose Summary:")
    for k, v in out["nymph_label_vs_prose_summary"].items():
        if not isinstance(v, dict):
            print(f"  {k}: {v}")
    print("  Nymph Label Profile:", out["nymph_label_vs_prose_summary"]["nymph_label_profile"])
    print("  Bio Prose Profile:  ", out["nymph_label_vs_prose_summary"]["bio_prose_profile"])
    print("Vertical Hydraulic Flow Zones:")
    for zn, row in zone_summary.items():
        print(
            f"  {zn:18s} (n={row['n_paragraphs']:2d}): words={row['n_words']:5.1f}, "
            f"topPF={row['top_pf_init']:.3f}, amCol={row['am_colophon']:.3f}, "
            f"qo={row['qo_rate']:.4f}, l_appl={row['l_appl_rate']:.4f}, "
            f"k={row['k_class_rate']:.4f}, t={row['t_class_rate']:.4f}, "
            f"dy={row['dy_rate']:.4f}, liqL={row['liq_l_rate']:.4f}, liqR={row['liq_r_rate']:.4f}"
        )
    print("Top P_TOP Inflow Words:", p_top_characteristic[:6])
    print("Top P_BOT Pool Words:  ", p_bot_characteristic[:6])
    print("Top Same-Page Nymph -> Prose Bridges:")
    for b in nymph_bridges[:8]:
        print(" ", b)


if __name__ == "__main__":
    main()
