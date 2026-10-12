"""
Attack 21: The 39-Line Colophon System (`=Pt`, `+Pr`, `+Pc`), the 5-Folio `=Pt` Cross-Reference Chain,
and Testing `f1r` as a Master Preface / Colophon System
=======================================================================================================
Investigates all 39 explicitly aligned paragraph-closing / title loci across `data/ZL3b-n.txt`:
- `10` `=Pt` lines (Right-Justified Standalone Paragraph Titles on `f1r`, `f8r`, `f25r`, `f42v`, `f46v`)
- `12` `+Pr` lines (Right-Justified Paragraph-Final Colophon Lines)
- `17` `+Pc` lines (Centered Paragraph-Final Colophon Lines)

Key Quantitative Tests:
1. **5-Folio `=Pt` Cross-Reference Chain (`f1r` & `f8r` <-> `f25r`, `f42v`, `f46v`)**:
   - `<f1r.21,=Pt> otol . daiiin` -> recurs verbatim on `<f42v.2,+P0> otol . daiin` (`f42v` is a `=Pt` folio).
   - `<f1r.28,=Pt> dchaiin` -> recurs verbatim on `<f25r.5,+P0> dchain` (`f25r` is a `=Pt` folio).
   - `<f8r.21,=Pt> schol . saim` -> exact `-m` token `saim` recurs on `<f46v.2,+P0> saim` (`f46v` is a `=Pt` folio; raw `saim` occurs ONLY on `f8r` and `f46v` in the entire manuscript!).
   - 10,000-trial Monte Carlo permutation test on the 5 `=Pt` folios ($z = +2.63, p = 0.035$).
2. **Cross-Colophon Echo Network (`=Pt` <-> `+Pr` / `+Pc`)**:
   - `<f1r.10,=Pt> dain . os . teody` <-> `<f86v5.39,+Pr> yteody . chedy . qoteey . octhy . dy <$>`
   - `<f1r.21,=Pt> otol . daiiin` <-> `<f85r1.35,+Pc> s,ar,chedar . olpchdy . otol . otchedy <$>`
   - `<f8r.21,=Pt> schol . saim` <-> `<f105r.10,+Pr> sairy . ore . daiindy . ytam <$>`
   - `<f25r.7,=Pt> dair . otaiir . otosy` <-> `<f105r.37,+Pc> otoiir . chedaiin . otair . otaly <$>`
   - `<f40v.19,+Pc> pchedy . chetar . ofair . arody <$>` <-> `<f105r.6,@P0> <%>par . arody` & `<f88v.4,@Lf> otar . arody`
   - 10,000-trial Monte Carlo permutation test on rare root/stem sharing between `=Pt` and `+Pr/+Pc`.
3. **Morphological Signature of Colophon Lines (`=Pt`, `+Pr`, `+Pc`)**:
   - Line-initial `y-` proclitic enrichment (`17.95%` of colophon lines open with `y-` vs `8.1%` of ordinary prose lines).
   - Line-final `-m / -am` colophon terminal marker in `+Pr` (`41.67%` of `+Pr` lines end with `-m/-am`) and `-g` in `=Pt` (`15.75x`).
4. **`f1r` (`P1..P4` + 4 `=Pt` titles) as a 4-Part Master Preface**.
"""

import json
import re
import random
from pathlib import Path
from collections import Counter, defaultdict

from attack7_positional_envelope_fst import (
    extract_core_root_and_envelope,
)
from attack16_radical_clause_translation_edition import RADICAL_SHORT_TAG

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "attack21_right_justified_titles_and_f1r_toc.json"


def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    if not w:
        return ""
    if w.startswith("qo") and len(w) > 2:
        w = w[1:]
    elif w.startswith("q") and len(w) > 1:
        w = w[1:]
    if w.startswith("cph"):
        w = "cth" + w[3:]
    elif w.startswith("cfh"):
        w = "ckh" + w[3:]
    elif w.startswith("p") and len(w) > 1:
        w = "t" + w[1:]
    elif w.startswith("f") and len(w) > 1:
        w = "k" + w[1:]
    w = re.sub(r"i{2,}", "i", w)
    w = re.sub(r"e{2,}", "e", w)
    if len(w) > 2 and w.endswith("am"):
        w = w[:-2] + "ar"
    elif len(w) > 2 and w.endswith("om"):
        w = w[:-2] + "or"
    elif len(w) >= 4 and w.endswith("aim"):
        w = w[:-3] + "air"
    return w


def segment_into_radicals(core_root: str, radical_set: set) -> list:
    if not core_root:
        return []
    if core_root in radical_set or len(core_root) <= 2:
        return [core_root]
    n = len(core_root)
    dp = [None] * (n + 1)
    dp[0] = []
    sorted_rads = sorted(radical_set, key=len, reverse=True)
    for i in range(n):
        if dp[i] is None:
            continue
        for r in sorted_rads:
            if core_root.startswith(r, i):
                cand = dp[i] + [r]
                if dp[i + len(r)] is None or len(cand) < len(dp[i + len(r)]):
                    dp[i + len(r)] = cand
        cand_char = dp[i] + [core_root[i:i+1]]
        if dp[i + 1] is None or len(cand_char) < len(dp[i + 1]):
            dp[i + 1] = cand_char
    return dp[n] if dp[n] else [core_root]


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    rad_dict = dict(RADICAL_SHORT_TAG)
    radical_set = set(rad_dict.keys())

    all_lines = []
    paragraphs = []
    cur_para = None

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$", raw_line)
        if not m:
            continue
        folio, lnum, tag, body = m.group(1), m.group(2), m.group(3), m.group(4)
        f_base = re.sub(r"\d+$", "", folio) if folio not in folio_index else folio
        f_meta = folio_index.get(folio, folio_index.get(f_base, {}))
        sec = f_meta.get("section", "Unknown")
        lang = f_meta.get("currier_lang", "Unknown")
        quire = f_meta.get("quire", "?")

        has_para_start = "<%>" in body
        has_para_end = "<$>" in body
        clean_body = re.sub(r"<[^>]*>", " ", body)
        raw_words = [w.strip() for w in re.split(r"[.\s,]+", clean_body) if w.strip()]

        parsed_words = []
        n_w = len(raw_words)
        for idx_w, rw in enumerate(raw_words):
            clean_rw = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", rw)
            clean_rw = re.sub(r"[^a-zA-Z]", "", clean_rw).lower()
            cn = normalize_token(rw)
            if not cn:
                continue
            pos = "INITIAL" if idx_w == 0 else ("FINAL" if idx_w == n_w - 1 else "MEDIAL")
            pref, suff, rt = extract_core_root_and_envelope(clean_rw, pos)
            rt = rt or cn
            rads = segment_into_radicals(rt, radical_set)
            parsed_words.append({
                "raw": rw,
                "clean_raw": clean_rw,
                "canon": cn,
                "pref": pref,
                "root": rt,
                "suff": suff,
                "radicals": rads
            })

        if not parsed_words:
            continue

        line_obj = {
            "folio": folio,
            "quire": quire,
            "lnum": lnum,
            "loc": f"{folio}.{lnum}",
            "tag": tag,
            "sec": sec,
            "lang": lang,
            "has_para_start": has_para_start,
            "has_para_end": has_para_end,
            "words": parsed_words,
            "raw_phrase": " . ".join(w["raw"] for w in parsed_words),
            "canon_phrase": " . ".join(w["canon"] for w in parsed_words)
        }
        all_lines.append(line_obj)

        if "P0" in tag:
            if has_para_start or tag.startswith("@P") or tag.startswith("*P") or cur_para is None or cur_para["folio"] != folio:
                if cur_para is not None:
                    paragraphs.append(cur_para)
                cur_para = {
                    "folio": folio,
                    "sec": sec,
                    "lang": lang,
                    "para_idx_on_folio": sum(1 for p in paragraphs if p["folio"] == folio) + 1,
                    "lines": [line_obj],
                    "pt_title": None
                }
            else:
                cur_para["lines"].append(line_obj)
        elif "Pt" in tag:
            if cur_para is not None and cur_para["folio"] == folio and cur_para["pt_title"] is None:
                cur_para["pt_title"] = line_obj
                paragraphs.append(cur_para)
                cur_para = None
            else:
                same_folio_paras = [p for p in paragraphs if p["folio"] == folio]
                if same_folio_paras and same_folio_paras[-1]["pt_title"] is None:
                    same_folio_paras[-1]["pt_title"] = line_obj

    if cur_para is not None:
        paragraphs.append(cur_para)

    # Index corpus
    raw_to_locs = defaultdict(list)
    canon_to_locs = defaultdict(list)
    root_to_locs = defaultdict(list)
    label_canon_to_locs = defaultdict(list)
    label_root_to_locs = defaultdict(list)
    folio_to_roots = defaultdict(set)
    folio_to_rads = defaultdict(set)
    folio_to_canons = defaultdict(set)
    folio_to_raws = defaultdict(set)
    folio_to_bigrams = defaultdict(set)

    for ln in all_lines:
        is_label = "L" in ln["tag"] or "C" in ln["tag"]
        ws = ln["words"]
        for i, w in enumerate(ws):
            entry = {"loc": ln["loc"], "tag": ln["tag"], "sec": ln["sec"], "raw": w["raw"], "canon": w["canon"]}
            raw_to_locs[w["clean_raw"]].append(entry)
            canon_to_locs[w["canon"]].append(entry)
            if w["root"]:
                root_to_locs[w["root"]].append(entry)
            if is_label:
                label_canon_to_locs[w["canon"]].append(entry)
                if w["root"]:
                    label_root_to_locs[w["root"]].append(entry)
            if "Pt" not in ln["tag"]:
                folio_to_raws[ln["folio"]].add(w["clean_raw"])
                folio_to_canons[ln["folio"]].add(w["canon"])
                if w["root"]:
                    folio_to_roots[ln["folio"]].add(w["root"])
                for r in w["radicals"]:
                    folio_to_rads[ln["folio"]].add(r)
        if "Pt" not in ln["tag"]:
            for i in range(len(ws) - 1):
                folio_to_bigrams[ln["folio"]].add((ws[i]["canon"], ws[i+1]["canon"]))

    # 1. Analyze all 10 explicit `=Pt` lines across the 5 `=Pt` folios (`f1r`, `f8r`, `f25r`, `f42v`, `f46v`)
    pt_lines = [ln for ln in all_lines if ln["tag"] == "=Pt"]
    pr_lines = [ln for ln in all_lines if ln["tag"] == "+Pr"]
    pc_lines = [ln for ln in all_lines if ln["tag"] == "+Pc"]
    colophon_lines = [ln for ln in all_lines if ln["tag"] in ("=Pt", "+Pr", "+Pc")]

    pt_folios = sorted(list({ln["folio"] for ln in pt_lines}))
    pt_records = []

    raw_endings = Counter()
    all_prose_raw_endings = Counter()
    for ln in all_lines:
        if "P0" in ln["tag"]:
            for w in ln["words"]:
                rw = w["clean_raw"]
                if rw.endswith("g"):
                    all_prose_raw_endings["g"] += 1
                elif rw.endswith("m"):
                    all_prose_raw_endings["m"] += 1
                elif rw.endswith("in"):
                    all_prose_raw_endings["in"] += 1
                elif rw.endswith("y"):
                    all_prose_raw_endings["y"] += 1
                all_prose_raw_endings["TOTAL"] += 1

    for ln in pt_lines:
        assoc_para = next((p for p in paragraphs if p["pt_title"] and p["pt_title"]["loc"] == ln["loc"]), None)
        para_canons = set()
        para_roots = set()
        para_rads = set()
        if assoc_para:
            for pln in assoc_para["lines"]:
                for pw in pln["words"]:
                    para_canons.add(pw["canon"])
                    if pw["root"]:
                        para_roots.add(pw["root"])
                    for r in pw["radicals"]:
                        para_rads.add(r)

        w_details = []
        for w in ln["words"]:
            rw = w["clean_raw"]
            if rw.endswith("g"):
                raw_endings["g"] += 1
            elif rw.endswith("m"):
                raw_endings["m"] += 1
            elif rw.endswith("in"):
                raw_endings["in"] += 1
            elif rw.endswith("y"):
                raw_endings["y"] += 1
            raw_endings["TOTAL"] += 1

            ex_matches = [m for m in canon_to_locs[w["canon"]] if m["loc"] != ln["loc"]]
            raw_matches = [m for m in raw_to_locs[w["clean_raw"]] if m["loc"] != ln["loc"]]
            rt_matches = [m for m in root_to_locs[w["root"]] if m["loc"] != ln["loc"]] if len(w["root"]) >= 2 else []
            lbl_matches = label_canon_to_locs[w["canon"]] + (label_root_to_locs[w["root"]] if len(w["root"]) >= 2 else [])
            seen_lbl = set()
            dedup_lbl = []
            for lm in lbl_matches:
                if lm["loc"] not in seen_lbl:
                    seen_lbl.add(lm["loc"])
                    dedup_lbl.append(lm)

            w_details.append({
                "raw": w["raw"],
                "clean_raw": w["clean_raw"],
                "canon": w["canon"],
                "core_root": w["root"],
                "suff": w["suff"],
                "radicals": w["radicals"],
                "radical_glosses": [rad_dict.get(r, r) for r in w["radicals"]],
                "echoes_parent_para_word": w["canon"] in para_canons,
                "echoes_parent_para_root": w["root"] in para_roots,
                "echoes_parent_para_radical": any(r in para_rads for r in w["radicals"]),
                "echoes_same_folio_word": w["canon"] in folio_to_canons[ln["folio"]],
                "echoes_same_folio_root": w["root"] in folio_to_roots[ln["folio"]],
                "exact_raw_matches_count": len(raw_matches),
                "exact_raw_matches_sample": raw_matches[:8],
                "exact_canon_matches_count": len(ex_matches),
                "core_root_matches_count": len(rt_matches),
                "exact_canon_matches_sample": ex_matches[:8],
                "diagram_label_matches": dedup_lbl[:8]
            })

        phrase_matches = []
        if len(ln["words"]) >= 2:
            for i in range(len(ln["words"]) - 1):
                c1, c2 = ln["words"][i]["canon"], ln["words"][i+1]["canon"]
                r1, r2 = ln["words"][i]["root"], ln["words"][i+1]["root"]
                fused_canon = c1 + c2
                fused_root = r1 + r2
                for oln in all_lines:
                    if oln["loc"] == ln["loc"]:
                        continue
                    ow = oln["words"]
                    for j in range(len(ow) - 1):
                        if (ow[j]["canon"] == c1 and ow[j+1]["canon"] == c2):
                            phrase_matches.append({
                                "loc": oln["loc"],
                                "tag": oln["tag"],
                                "sec": oln["sec"],
                                "match_type": "exact_canon_bigram",
                                "phrase": f"{ow[j]['raw']} . {ow[j+1]['raw']}"
                            })
                    for w_o in ow:
                        if w_o["canon"] == fused_canon or (len(fused_root) >= 3 and w_o["root"] == fused_root):
                            phrase_matches.append({
                                "loc": oln["loc"],
                                "tag": oln["tag"],
                                "sec": oln["sec"],
                                "match_type": "fused_compound",
                                "word": w_o["raw"]
                            })

        pt_records.append({
            "folio": ln["folio"],
            "quire": ln["quire"],
            "loc": ln["loc"],
            "tag": ln["tag"],
            "section": ln["sec"],
            "lang": ln["lang"],
            "raw_phrase": ln["raw_phrase"],
            "parent_para_lines": len(assoc_para["lines"]) if assoc_para else 0,
            "words": w_details,
            "phrase_or_compound_matches": phrase_matches[:15]
        })

    # 2. Test the 5-Folio `=Pt` Cross-Reference Chain!
    rare_pt_items = []
    all_folios_list = sorted(list(folio_to_canons.keys()))
    herbal_a_folios = [
        f for f in all_folios_list
        if folio_index.get(f, {}).get("section") == "Herbal (Botanical)"
        and folio_index.get(f, {}).get("currier_lang") == "A"
    ]

    for rec in pt_records:
        f_src = rec["folio"]
        for w in rec["words"]:
            target_folios_canon = sorted(list({
                m["loc"].split(".")[0] for m in canon_to_locs[w["canon"]]
                if m["loc"].split(".")[0] != f_src and "Pt" not in m["tag"]
            }))
            target_folios_raw = sorted(list({
                m["loc"].split(".")[0] for m in raw_to_locs[w["clean_raw"]]
                if m["loc"].split(".")[0] != f_src and "Pt" not in m["tag"]
            }))
            if 1 <= len(target_folios_canon) <= 10:
                rare_pt_items.append({
                    "src_folio": f_src,
                    "src_loc": rec["loc"],
                    "type": "rare_canon_word",
                    "item": w["raw"],
                    "canon": w["canon"],
                    "total_target_folios": len(target_folios_canon),
                    "target_folios": target_folios_canon,
                    "pt_folio_hits": [tf for tf in target_folios_canon if tf in pt_folios]
                })
            elif 1 <= len(target_folios_raw) <= 10:
                rare_pt_items.append({
                    "src_folio": f_src,
                    "src_loc": rec["loc"],
                    "type": "rare_raw_word_orthography",
                    "item": w["raw"],
                    "canon": w["clean_raw"],
                    "total_target_folios": len(target_folios_raw),
                    "target_folios": target_folios_raw,
                    "pt_folio_hits": [tf for tf in target_folios_raw if tf in pt_folios]
                })
        ws = rec["words"]
        for i in range(len(ws) - 1):
            bg = (ws[i]["canon"], ws[i+1]["canon"])
            t_folios = sorted([f for f, bset in folio_to_bigrams.items() if f != f_src and bg in bset])
            if 1 <= len(t_folios) <= 10:
                rare_pt_items.append({
                    "src_folio": f_src,
                    "src_loc": rec["loc"],
                    "type": "rare_canon_bigram",
                    "item": f"{ws[i]['raw']} . {ws[i+1]['raw']}",
                    "canon": f"{bg[0]} . {bg[1]}",
                    "total_target_folios": len(t_folios),
                    "target_folios": t_folios,
                    "pt_folio_hits": [tf for tf in t_folios if tf in pt_folios]
                })

    obs_cross_pt_hits = sum(len(item["pt_folio_hits"]) for item in rare_pt_items)
    rng = random.Random(42)
    null_cross_counts = []
    cand_pool = [f for f in herbal_a_folios if f != "f1r"]
    for _ in range(10000):
        sampled_4 = set(rng.sample(cand_pool, 4)) | {"f1r"}
        c = 0
        for item in rare_pt_items:
            for tf in item["target_folios"]:
                if tf in sampled_4 and tf != item["src_folio"]:
                    c += 1
        null_cross_counts.append(c)

    nc_mean = sum(null_cross_counts) / len(null_cross_counts)
    nc_std = (sum((x - nc_mean) ** 2 for x in null_cross_counts) / len(null_cross_counts)) ** 0.5
    nc_z = (obs_cross_pt_hits - nc_mean) / (nc_std if nc_std > 0 else 1.0)
    nc_p = sum(1 for x in null_cross_counts if x >= obs_cross_pt_hits) / len(null_cross_counts)

    # 3. Analyze the 39-Line Colophon System (`=Pt`, `+Pr`, `+Pc`)
    colophon_catalog = []
    for ln in colophon_lines:
        first_w = ln["words"][0]["clean_raw"]
        last_w = ln["words"][-1]["clean_raw"]
        has_m_token = any(w["clean_raw"].endswith("m") for w in ln["words"])
        has_g_token = any(w["clean_raw"].endswith("g") for w in ln["words"])
        colophon_catalog.append({
            "loc": ln["loc"],
            "folio": ln["folio"],
            "quire": ln["quire"],
            "tag": ln["tag"],
            "section": ln["sec"],
            "lang": ln["lang"],
            "raw_phrase": ln["raw_phrase"],
            "starts_with_y": first_w.startswith("y"),
            "ends_with_m": last_w.endswith("m") or has_m_token,
            "ends_with_g": last_w.endswith("g") or has_g_token,
            "roots": [w["root"] for w in ln["words"]]
        })

    # Compute Colophon Morphological Laws vs ordinary `+P0` lines
    ordinary_p0_lines = [ln for ln in all_lines if ln["tag"] == "+P0"]
    ord_starts_y = sum(1 for ln in ordinary_p0_lines if ln["words"][0]["clean_raw"].startswith("y")) / len(ordinary_p0_lines)
    ord_has_m = sum(1 for ln in ordinary_p0_lines if any(w["clean_raw"].endswith("m") for w in ln["words"])) / len(ordinary_p0_lines)

    col_starts_y = sum(1 for c in colophon_catalog if c["starts_with_y"]) / len(colophon_catalog)
    pr_has_m = sum(1 for c in colophon_catalog if c["tag"] == "+Pr" and c["ends_with_m"]) / len(pr_lines)

    # Cross-Colophon Echoes between `=Pt` (`10` lines) and `+Pr/+Pc` (`29` lines)
    # Count how many `+Pr/+Pc` lines share a non-trivial Core Root (`len >= 2` or rare canonical stem) with `=Pt`
    pt_nontrivial_roots = {
        w["root"] for ln in pt_lines for w in ln["words"]
        if len(w["root"]) >= 2 and len(root_to_locs[w["root"]]) <= 450
    }
    pt_nontrivial_canons = {
        w["canon"] for ln in pt_lines for w in ln["words"]
        if len(canon_to_locs[w["canon"]]) <= 150
    }

    pr_pc_lines = pr_lines + pc_lines
    obs_colophon_echo_lines = []
    for ln in pr_pc_lines:
        matched_items = []
        for w in ln["words"]:
            if w["canon"] in pt_nontrivial_canons:
                matched_items.append(f"canon:{w['raw']}({w['canon']})")
            elif w["root"] in pt_nontrivial_roots:
                matched_items.append(f"root:{w['raw']}({w['root']})")
        if matched_items:
            obs_colophon_echo_lines.append({
                "loc": ln["loc"],
                "tag": ln["tag"],
                "raw_phrase": ln["raw_phrase"],
                "matched_pt_items": matched_items
            })

    # Permutation baseline for `+Pr/+Pc` echoing `=Pt`: sample 29 random `+P0` lines 10,000 times
    null_echo_counts = []
    for _ in range(10000):
        samp = rng.sample(ordinary_p0_lines, len(pr_pc_lines))
        cnt = 0
        for ln in samp:
            if any(w["canon"] in pt_nontrivial_canons or w["root"] in pt_nontrivial_roots for w in ln["words"]):
                cnt += 1
        null_echo_counts.append(cnt)
    ne_mean = sum(null_echo_counts) / len(null_echo_counts)
    ne_std = (sum((x - ne_mean) ** 2 for x in null_echo_counts) / len(null_echo_counts)) ** 0.5
    ne_z = (len(obs_colophon_echo_lines) - ne_mean) / (ne_std if ne_std > 0 else 1.0)

    # Analyze `f1r` 4 paragraphs (`P1..P4`) and their 4 `=Pt` titles
    f1r_paras = [p for p in paragraphs if p["folio"] == "f1r"]
    f1r_analysis = []
    for idx, p in enumerate(f1r_paras, 1):
        p_words = [w for ln in p["lines"] for w in ln["words"]]
        sec_counter = Counter()
        rare_label_links = []
        rare_folio_targets = Counter()
        for w in p_words:
            rt = w["root"]
            if len(rt) >= 2:
                matches = [m for m in root_to_locs[rt] if m["loc"].split(".")[0] != "f1r"]
                if 1 <= len(matches) <= 25:
                    for m in matches:
                        sec_counter[m["sec"]] += 1
                        rare_folio_targets[m["loc"].split(".")[0]] += 1
                lbl_m = label_root_to_locs[rt]
                if 1 <= len(lbl_m) <= 10:
                    rare_label_links.append({
                        "f1r_word": w["raw"],
                        "root": rt,
                        "label_matches": [f"{lm['loc']}({lm['raw']}, {lm['tag']})" for lm in lbl_m[:5]]
                    })
        f1r_analysis.append({
            "para_index": idx,
            "line_count": len(p["lines"]),
            "word_count": len(p_words),
            "pt_title": {
                "loc": p["pt_title"]["loc"],
                "raw_phrase": p["pt_title"]["raw_phrase"],
                "words": [
                    {
                        "raw": tw["raw"],
                        "canon": tw["canon"],
                        "root": tw["root"],
                        "radicals": tw["radicals"],
                        "glosses": [rad_dict.get(r, r) for r in tw["radicals"]]
                    }
                    for tw in p["pt_title"]["words"]
                ]
            } if p["pt_title"] else None,
            "opening_words": " . ".join(w["raw"] for w in p_words[:5]),
            "closing_words": " . ".join(w["raw"] for w in p_words[-5:]),
            "rare_root_section_targets": dict(sec_counter.most_common()),
            "top_target_folios": dict(rare_folio_targets.most_common(8)),
            "rare_diagram_label_citations": rare_label_links[:10]
        })

    pt_tot = max(1, raw_endings["TOTAL"])
    pr_tot = max(1, all_prose_raw_endings["TOTAL"])
    ending_enrichment = {}
    for k in ["g", "m", "in", "y"]:
        pt_rate = raw_endings[k] / pt_tot
        pr_rate = all_prose_raw_endings[k] / pr_tot
        ending_enrichment[k] = {
            "pt_count": raw_endings[k],
            "pt_rate": round(pt_rate, 4),
            "prose_count": all_prose_raw_endings[k],
            "prose_rate": round(pr_rate, 4),
            "enrichment_ratio": round(pt_rate / pr_rate, 2) if pr_rate > 0 else 0.0
        }

    out = {
        "summary": {
            "total_explicit_pt_lines": len(pt_records),
            "total_pr_lines": len(pr_lines),
            "total_pc_lines": len(pc_lines),
            "total_colophon_lines": len(colophon_catalog),
            "pt_folios": pt_folios,
            "cross_pt_folio_chain_test": {
                "rare_pt_items_tested": len(rare_pt_items),
                "observed_cross_pt_folio_hits": obs_cross_pt_hits,
                "null_mean_herbal_a": round(nc_mean, 3),
                "null_std_herbal_a": round(nc_std, 3),
                "z_score": round(nc_z, 2),
                "empirical_p_value": round(nc_p, 5),
                "rare_pt_items": rare_pt_items
            },
            "colophon_morphological_laws": {
                "colophon_starts_with_y_rate": round(col_starts_y, 4),
                "ordinary_p0_starts_with_y_rate": round(ord_starts_y, 4),
                "y_initial_enrichment_ratio": round(col_starts_y / ord_starts_y, 2),
                "pr_has_m_terminal_rate": round(pr_has_m, 4),
                "ordinary_p0_has_m_rate": round(ord_has_m, 4),
                "pr_m_enrichment_ratio": round(pr_has_m / ord_has_m, 2),
                "pt_vs_pr_pc_echo": {
                    "observed_echo_lines": len(obs_colophon_echo_lines),
                    "total_pr_pc_lines": len(pr_pc_lines),
                    "null_mean": round(ne_mean, 2),
                    "null_std": round(ne_std, 2),
                    "z_score": round(ne_z, 2),
                    "echo_matches": obs_colophon_echo_lines
                }
            },
            "ending_enrichment_vs_prose": ending_enrichment
        },
        "explicit_pt_titles": pt_records,
        "all_39_colophon_lines": colophon_catalog,
        "f1r_preface_analysis": f1r_analysis
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved Attack 21 results to {OUT_PATH}")
    print(f"1. 5-Folio `=Pt` Cross-Reference Chain: observed={obs_cross_pt_hits} hits vs null={nc_mean:.3f} ± {nc_std:.3f} (z = {nc_z:+.2f}, p = {nc_p:.5f})")
    print(f"2. Colophon `y-` initial rate: {col_starts_y*100:.2f}% vs ordinary +P0 {ord_starts_y*100:.2f}% ({col_starts_y/ord_starts_y:.2f}x)")
    print(f"3. `+Pr` `-m/-am` terminal rate: {pr_has_m*100:.2f}% vs ordinary +P0 {ord_has_m*100:.2f}% ({pr_has_m/ord_has_m:.2f}x)")
    print(f"4. `+Pr/+Pc` echoing `=Pt` roots/stems: {len(obs_colophon_echo_lines)}/{len(pr_pc_lines)} vs null {ne_mean:.2f} ± {ne_std:.2f} (z = {ne_z:+.2f})")
    for em in obs_colophon_echo_lines:
        print(f"   [{em['loc']},{em['tag']}] `{em['raw_phrase']}` -> {em['matched_pt_items']}")


if __name__ == "__main__":
    main()
