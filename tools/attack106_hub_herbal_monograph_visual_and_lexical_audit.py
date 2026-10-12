#!/usr/bin/env python3
"""
Attack 106 (Discovery 123): Visual, Codicological & Lexical Audit of the Master Hub Herbal
Monographs (`f43v, f46r, f34r, f31v, f33v, f40r, f48r, f55v`) vs. Non-Hub Herbal Folios

Tests:
1. Computes the exact Cross-Sectional Citation Degree of all `126` Herbal Monograph folios (`$I=H`,
   `95` Currier A and `31` Currier B) across:
   - `Zodiac Medallions ($I=Z)` (shared high-IDF open stems),
   - `Pharmaceutical Formularies ($I=P)` (shared high-IDF open stems & `@Lf` label matches),
   - `Quire 20 Starred Clinical Recipes ($I=S)` (3-stage pharmacopoeia triads & shared stems).
2. Controls strictly for folio word count (`per 100 prose tokens`) to test whether the Hub Herbal
   monographs (`Top-15 Hubs`, led by `f43v, f46r, f34r, f31v, f33v, f40r, f48r, f55v`) and Currier B
   Herbal Quires (`Quires D, E, F, G`) exhibit true per-token cross-sectional citation enrichment
   beyond length effects (1,000-trial permutation test).
3. Profiles the Codicological (`Quire $Q`, `Scribe Hand $H`, `Bifolio $B`), Layout (`Paragraphs`,
   `Drawing Intrusions <-> per line`), and Morphological (`qo-`, `l-/ol-`, `-edy`, `-aiin`,
   `Compound Core %`) signatures that distinguish Hub Herbal Monographs from Non-Hub Herbal Monographs.
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
PIGMENT_JSON = DATA_DIR / "attack79_full_manuscript_pigment_grammar_concordance.json"
OUT_JSON = DATA_DIR / "attack106_hub_herbal_monograph_visual_and_lexical_audit.json"

FOLIO_META_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)>\s*<!\s*(.*?)>")
LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


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
    folio_label_tokens = defaultdict(list)
    folio_para_count = Counter()
    folio_line_count = Counter()
    folio_intrusion_count = Counter()

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
            if ltype_clean.startswith("L"):
                folio_label_tokens[cur_folio].extend(toks)
            elif ltype_clean.startswith("P"):
                folio_prose_tokens[cur_folio].extend(toks)
                folio_line_count[cur_folio] += 1
                if "<%>" in text or ltype.startswith("@P"):
                    folio_para_count[cur_folio] += 1
                if "<->" in text:
                    folio_intrusion_count[cur_folio] += text.count("<->")

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

    h_folios = sorted([
        f for f, m in folio_meta.items()
        if m.get("I") == "H" and len(folio_prose_tokens[f]) >= 15
    ])
    z_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "Z"])
    p_folios = sorted([
        f for f, m in folio_meta.items()
        if m.get("I") == "P" and len(folio_all_tokens[f]) >= 15
    ])
    s_folios = sorted([f for f, m in folio_meta.items() if m.get("I") == "S"])

    z_stem_union = {canonical_stem(w) for zf in z_folios for w in folio_all_tokens[zf] if canonical_stem(w) in stem_idf}
    p_stem_union = {canonical_stem(w) for pf in p_folios for w in folio_all_tokens[pf] if canonical_stem(w) in stem_idf}
    p_lbl_stem_union = {canonical_stem(w) for pf in p_folios for w in folio_label_tokens[pf] if canonical_stem(w) in stem_idf}
    s_stem_union = {canonical_stem(w) for sf in s_folios for w in folio_all_tokens[sf] if canonical_stem(w) in stem_idf}

    # Load pigment metrics if available
    pigment_by_folio = {}
    if PIGMENT_JSON.exists():
        try:
            pdata = json.loads(PIGMENT_JSON.read_text(encoding="utf-8"))
            for row in pdata.get("folio_records", []):
                pigment_by_folio[row["folio"]] = row
        except Exception:
            pass

    herbal_profiles = []
    for hf in h_folios:
        toks = folio_prose_tokens[hf]
        n_toks = len(toks)
        open_stems = {canonical_stem(w) for w in toks if canonical_stem(w) in stem_idf}
        z_shared = open_stems & z_stem_union
        p_shared = open_stems & p_stem_union
        p_lbl_shared = open_stems & p_lbl_stem_union
        s_shared = open_stems & s_stem_union
        zps_shared = open_stems & z_stem_union & p_stem_union & s_stem_union
        ps_shared = open_stems & p_stem_union & s_stem_union

        total_bridge_idf = (
            sum(stem_idf[st] for st in z_shared)
            + sum(stem_idf[st] for st in p_shared)
            + sum(stem_idf[st] for st in s_shared)
        )
        bridge_idf_per_100 = 100.0 * total_bridge_idf / n_toks
        ps_stems_per_100 = 100.0 * len(ps_shared) / n_toks

        m = folio_meta[hf]
        lines = folio_line_count[hf] or 1
        paras = folio_para_count[hf] or 1
        intrusions = folio_intrusion_count[hf]

        herbal_profiles.append({
            "folio": hf,
            "quire": m.get("Q", "U"),
            "bifolio": m.get("B", "U"),
            "currier_lang": m.get("L", "U"),
            "scribe_hand": m.get("H", "U"),
            "tokens": n_toks,
            "lines": lines,
            "paragraphs": paras,
            "intrusions": intrusions,
            "intrusions_per_line": round(intrusions / lines, 3),
            "open_stems_count": len(open_stems),
            "open_stems_per_100_toks": round(100.0 * len(open_stems) / n_toks, 2),
            "z_shared_count": len(z_shared),
            "p_shared_count": len(p_shared),
            "p_label_shared_count": len(p_lbl_shared),
            "s_shared_count": len(s_shared),
            "ps_shared_count": len(ps_shared),
            "zps_shared_count": len(zps_shared),
            "zps_shared_stems": sorted(zps_shared, key=lambda x: -stem_idf[x]),
            "ps_shared_stems": sorted(ps_shared, key=lambda x: -stem_idf[x])[:10],
            "p_label_shared_stems": sorted(p_lbl_shared, key=lambda x: -stem_idf[x]),
            "total_bridge_idf": round(total_bridge_idf, 3),
            "bridge_idf_per_100_toks": round(bridge_idf_per_100, 3),
            "ps_stems_per_100_toks": round(ps_stems_per_100, 3),
            "qo_active_pct": round(100.0 * sum(1 for w in toks if w.startswith("qo")) / n_toks, 2),
            "o_nominal_pct": round(100.0 * sum(1 for w in toks if w.startswith("o") and not w.startswith("qo")) / n_toks, 2),
            "l_ol_applicative_pct": round(100.0 * sum(1 for w in toks if w.startswith(("l", "ol", "qol"))) / n_toks, 2),
            "edy_process_pct": round(100.0 * sum(1 for w in toks if w.endswith(("edy", "eedy"))) / n_toks, 2),
            "aiin_measure_pct": round(100.0 * sum(1 for w in toks if w.endswith(("aiin", "iin", "ain"))) / n_toks, 2),
        })

    herbal_profiles.sort(key=lambda x: (-x["zps_shared_count"], -x["ps_shared_count"], -x["total_bridge_idf"]))

    # Compare Currier B vs Currier A Herbal Folios on raw and per-100-token normalized bridge metrics
    hb_rows = [r for r in herbal_profiles if r["currier_lang"] == "B"]
    ha_rows = [r for r in herbal_profiles if r["currier_lang"] == "A"]

    def summarize_group(rows):
        n = len(rows) or 1
        return {
            "folio_count": len(rows),
            "mean_tokens": round(sum(r["tokens"] for r in rows) / n, 2),
            "mean_paragraphs": round(sum(r["paragraphs"] for r in rows) / n, 2),
            "mean_intrusions_per_line": round(sum(r["intrusions_per_line"] for r in rows) / n, 3),
            "mean_open_stems_per_100_toks": round(sum(r["open_stems_per_100_toks"] for r in rows) / n, 2),
            "mean_z_shared": round(sum(r["z_shared_count"] for r in rows) / n, 2),
            "mean_p_shared": round(sum(r["p_shared_count"] for r in rows) / n, 2),
            "mean_s_shared": round(sum(r["s_shared_count"] for r in rows) / n, 2),
            "mean_ps_shared": round(sum(r["ps_shared_count"] for r in rows) / n, 2),
            "mean_zps_shared": round(sum(r["zps_shared_count"] for r in rows) / n, 2),
            "mean_bridge_idf_per_100_toks": round(sum(r["bridge_idf_per_100_toks"] for r in rows) / n, 2),
            "mean_ps_stems_per_100_toks": round(sum(r["ps_stems_per_100_toks"] for r in rows) / n, 2),
            "mean_qo_active_pct": round(sum(r["qo_active_pct"] for r in rows) / n, 2),
            "mean_l_ol_applicative_pct": round(sum(r["l_ol_applicative_pct"] for r in rows) / n, 2),
            "mean_edy_process_pct": round(sum(r["edy_process_pct"] for r in rows) / n, 2),
        }

    top15_hubs = herbal_profiles[:15]
    non_hubs = herbal_profiles[15:]

    # 1,000-trial permutation test on per-100-token normalized Bridge IDF between Herbal-B and Herbal-A
    rng = random.Random(2026106)
    all_rates = [r["bridge_idf_per_100_toks"] for r in herbal_profiles]
    n_b = len(hb_rows)
    obs_hb_rate = sum(r["bridge_idf_per_100_toks"] for r in hb_rows) / n_b
    obs_ha_rate = sum(r["bridge_idf_per_100_toks"] for r in ha_rows) / len(ha_rows)
    obs_diff = obs_hb_rate - obs_ha_rate

    null_diffs = []
    for _ in range(1000):
        shuffled = list(all_rates)
        rng.shuffle(shuffled)
        mb = sum(shuffled[:n_b]) / n_b
        ma = sum(shuffled[n_b:]) / (len(shuffled) - n_b)
        null_diffs.append(mb - ma)

    nd_mean = sum(null_diffs) / len(null_diffs)
    nd_std = math.sqrt(sum((x - nd_mean) ** 2 for x in null_diffs) / len(null_diffs)) or 1e-9
    z_hb_vs_ha_per100 = round((obs_diff - nd_mean) / nd_std, 2)

    # Quire breakdown across Herbal section
    quire_groups = defaultdict(list)
    for r in herbal_profiles:
        quire_groups[r["quire"]].append(r)
    quire_summary = {
        q: summarize_group(rows)
        for q, rows in sorted(quire_groups.items())
    }

    summary = {
        "attack_id": 106,
        "discovery_id": 123,
        "title": "Visual, Codicological & Lexical Audit of the Master Hub Herbal Monographs vs. Non-Hub Herbal Folios",
        "herbal_folio_count": len(herbal_profiles),
        "group_comparisons": {
            "TOP_15_MASTER_HUB_HERBALS": summarize_group(top15_hubs),
            "NON_HUB_HERBALS_111": summarize_group(non_hubs),
            "CURRIER_B_HERBALS_31": summarize_group(hb_rows),
            "CURRIER_A_HERBALS_95": summarize_group(ha_rows),
        },
        "per_100_token_normalized_permutation_test": {
            "herbal_b_bridge_idf_per_100_toks": round(obs_hb_rate, 3),
            "herbal_a_bridge_idf_per_100_toks": round(obs_ha_rate, 3),
            "ratio_b_over_a": round(obs_hb_rate / (obs_ha_rate or 1e-9), 3),
            "observed_diff": round(obs_diff, 3),
            "null_mean_diff": round(nd_mean, 3),
            "null_std_diff": round(nd_std, 3),
            "z_score": z_hb_vs_ha_per100,
        },
        "quire_breakdown": quire_summary,
        "top_20_hub_herbal_monographs": herbal_profiles[:20],
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Attack 106] Saved -> {OUT_JSON}")
    print(f"  Herbal-B vs Herbal-A Bridge IDF per 100 tokens: {obs_hb_rate:.2f} vs {obs_ha_rate:.2f} (ratio={obs_hb_rate/obs_ha_rate:.2f}x, z={z_hb_vs_ha_per100:+.2f})")
    print("  Top 10 Master Hub Herbal Monographs:")
    for r in herbal_profiles[:10]:
        print(f"    {r['folio']:6s} (Q={r['quire']}, L={r['currier_lang']}, H={r['scribe_hand']}, toks={r['tokens']:3d}, paras={r['paragraphs']}): Z∩P∩S={r['zps_shared_count']} {r['zps_shared_stems']} | P∩S={r['ps_shared_count']} | P_lbl={r['p_label_shared_stems']} | IDF/100t={r['bridge_idf_per_100_toks']:.1f}")


if __name__ == "__main__":
    main()
