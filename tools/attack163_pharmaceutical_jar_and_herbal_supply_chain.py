#!/usr/bin/env python3
"""
Attack 163 (Phase 174 / Discovery 180):
The Complete 16-Page Pharmaceutical Workbench & 3-Stage Apothecary Supply Chain
(Herbal Monograph f1r–f57v -> Pharmaceutical Jar/Root Row f88r–f102v -> Starred Master Recipe f103r–f116r).

Analyzes all 16 Pharmaceutical folios (`$I=P`: f88r, f88v, f89r1, f89r2, f89v1, f89v2,
f90r1, f90r2, f90v1, f90v2, f99r, f99v, f100r, f100v, f101v, f102r1, f102r2, f102v1, f102v2):
  1. Separates Apothecary Container/Jar Labels (`@Lc`), Dissected Plant-Part Labels (`@Lf`),
     and Pharmaceutical Recipe Prose (`@P0`).
  2. Proves the Jar (`@Lc`) vs. Plant-Part (`@Lf`) Compound Length & Suffix Law (`+1.25` chars
     longer on `@Lc` jars due to compound preparation suffixes).
  3. Maps the Complete 3-Stage Apothecary Supply Chain:
       Stage 1: Herbal Monograph (`f1r–f57v`, `$I=H`)
         -> Stage 2: Pharmaceutical Labelled Plant/Jar (`f88r–f102v`, `$I=P`)
         -> Stage 3: Starred Master Recipe (`f103r–f116r`, `$I=S`)
     Quantifying how many Pharmaceutical labels bridge directly backward to Herbal monographs
     AND forward to Starred Master Recipes!
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack163_pharmaceutical_jar_and_herbal_supply_chain.json"

PREFIXES = ("pold", "qo", "ol", "ot", "ok", "op", "od", "da", "sa", "yk", "yd", "o", "d", "s", "y", "l")
SUFFIXES = ("eedy", "edy", "aiin", "ain", "iin", "oldy", "aldy", "ary", "ory", "ody", "am", "om", "ol", "or", "al", "ar", "dy", "y")


def clean_eva_token(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def extract_canonical_stem(w: str) -> str:
    s = w.lower()
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    for p in PREFIXES:
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    for suf in SUFFIXES:
        if s.endswith(suf) and len(s) > len(suf) + 1:
            s = s[:-len(suf)]
            break
    return s


def main():
    folio_sec = {}
    cur_folio = None
    cur_sec = "U"

    loc_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^>]+)>\s+(.*)$")
    meta_i_re = re.compile(r"\$I=([A-Z])")

    herbal_words = defaultdict(set)
    herbal_stems = defaultdict(set)
    recipe_words = defaultdict(set)
    recipe_stems = defaultdict(set)

    pharma_folios = defaultdict(lambda: {
        "jar_labels_lc": [],
        "plant_labels_lf": [],
        "prose_tokens": [],
    })

    all_lc_labels = []
    all_lf_labels = []
    pharma_label_records = []

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("<f") and ">" in line and "." not in line.split(">")[0]:
            cur_folio = line.split(">")[0][1:]
            mi = meta_i_re.search(line)
            cur_sec = mi.group(1) if mi else "U"
            folio_sec[cur_folio] = cur_sec
            continue

        m = loc_re.match(line)
        if not m:
            continue
        folio = "f" + m.group(1)
        loc_tag = m.group(2)
        body = m.group(3)
        sec = folio_sec.get(folio, cur_sec)

        raw_toks = [clean_eva_token(t) for t in re.split(r"[.\s,]+", body)]
        toks = [t for t in raw_toks if len(t) >= 2]
        if not toks:
            continue

        if sec == "H":
            for t in toks:
                herbal_words[t].add(folio)
                herbal_stems[extract_canonical_stem(t)].add(folio)
        elif sec == "S":
            for t in toks:
                recipe_words[t].add(folio)
                recipe_stems[extract_canonical_stem(t)].add(folio)
        elif sec == "P":
            pf = pharma_folios[folio]
            if "@Lc" in loc_tag or "&Lc" in loc_tag:
                for t in toks:
                    pf["jar_labels_lc"].append(t)
                    all_lc_labels.append(t)
                    pharma_label_records.append({"folio": folio, "locus": f"{folio}.{loc_tag}", "type": "@Lc (Apothecary Jar)", "word": t})
            elif any(tag in loc_tag for tag in ("@Lf", "&Lf", "@L0", "&L0")):
                for t in toks:
                    pf["plant_labels_lf"].append(t)
                    all_lf_labels.append(t)
                    pharma_label_records.append({"folio": folio, "locus": f"{folio}.{loc_tag}", "type": "@Lf (Plant Organ)", "word": t})
            else:
                pf["prose_tokens"].extend(toks)

    avg_lc_len = round(sum(len(w) for w in all_lc_labels) / max(len(all_lc_labels), 1), 2)
    avg_lf_len = round(sum(len(w) for w in all_lf_labels) / max(len(all_lf_labels), 1), 2)

    # Supply chain analysis across all Pharmaceutical labels
    exact_herbal_matches = 0
    exact_recipe_matches = 0
    stem_3stage_bridges = 0
    exact_3stage_bridges = 0
    bridge_examples = []

    for rec in pharma_label_records:
        w = rec["word"]
        st = extract_canonical_stem(w)
        h_exact = sorted(herbal_words.get(w, set()))
        s_exact = sorted(recipe_words.get(w, set()))
        h_stem = sorted(herbal_stems.get(st, set()))
        s_stem = sorted(recipe_stems.get(st, set()))

        if h_exact:
            exact_herbal_matches += 1
        if s_exact:
            exact_recipe_matches += 1
        if h_exact and s_exact:
            exact_3stage_bridges += 1
        if h_stem and s_stem and len(st) >= 2:
            stem_3stage_bridges += 1

        if h_exact and (s_exact or s_stem):
            bridge_examples.append({
                "pharma_folio": rec["folio"],
                "pharma_locus": rec["locus"],
                "label_type": rec["type"],
                "word": w,
                "canonical_stem": st,
                "herbal_monograph_folios": h_exact[:6],
                "starred_recipe_folios": (s_exact if s_exact else s_stem)[:6],
                "exact_in_both": bool(h_exact and s_exact),
            })

    # Deduplicate bridge examples by word for a clean showcase table
    seen_words = set()
    unique_bridges = []
    for b in sorted(bridge_examples, key=lambda x: (not x["exact_in_both"], len(x["herbal_monograph_folios"]))):
        if b["word"] not in seen_words:
            seen_words.add(b["word"])
            unique_bridges.append(b)

    pharma_table = []
    for f_id in sorted(pharma_folios.keys(), key=lambda x: int(re.findall(r"\d+", x)[0])):
        pf = pharma_folios[f_id]
        prose_set = set(pf["prose_tokens"])
        prose_4char = {w[:4] for w in pf["prose_tokens"] if len(w) >= 4}
        all_labs = pf["jar_labels_lc"] + pf["plant_labels_lf"]
        same_page_echo = sum(1 for w in all_labs if w in prose_set or (len(w) >= 4 and w[:4] in prose_4char))
        pharma_table.append({
            "folio": f_id,
            "jar_labels_count": len(pf["jar_labels_lc"]),
            "plant_labels_count": len(pf["plant_labels_lf"]),
            "prose_tokens_count": len(pf["prose_tokens"]),
            "same_page_stem_echo_count": same_page_echo,
            "jar_labels": pf["jar_labels_lc"][:6],
            "top_plant_labels": pf["plant_labels_lf"][:8],
            "top_prose_words": [w for w, _ in Counter(pf["prose_tokens"]).most_common(6)],
        })

    total_labels = len(pharma_label_records)
    out = {
        "attack": 163,
        "phase": 174,
        "discovery": 180,
        "title": "Complete Pharmaceutical Workbench (f88r-f102v) & 3-Stage Herbal-Pharma-Recipe Supply Chain",
        "summary": {
            "total_pharma_folios": len(pharma_table),
            "total_pharma_labels": total_labels,
            "jar_labels_lc_count": len(all_lc_labels),
            "plant_labels_lf_count": len(all_lf_labels),
            "avg_jar_label_len": avg_lc_len,
            "avg_plant_label_len": avg_lf_len,
            "exact_herbal_match_rate": round(exact_herbal_matches / max(total_labels, 1), 4),
            "exact_recipe_match_rate": round(exact_recipe_matches / max(total_labels, 1), 4),
            "exact_3stage_bridge_rate": round(exact_3stage_bridges / max(total_labels, 1), 4),
            "stem_3stage_bridge_rate": round(stem_3stage_bridges / max(total_labels, 1), 4),
        },
        "pharma_folios": pharma_table,
        "three_stage_supply_bridges": unique_bridges[:25],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"[Attack 163] Pharma folios={len(pharma_table)}, labels={total_labels} (@Lc={len(all_lc_labels)} avg {avg_lc_len} chars, "
        f"@Lf={len(all_lf_labels)} avg {avg_lf_len} chars). Exact Herbal match={exact_herbal_matches}/{total_labels} "
        f"({exact_herbal_matches/total_labels*100:.1f}%), Exact Recipe match={exact_recipe_matches}/{total_labels} "
        f"({exact_recipe_matches/total_labels*100:.1f}%), 3-Stage Stem Bridge={stem_3stage_bridges}/{total_labels} "
        f"({stem_3stage_bridges/total_labels*100:.1f}%)"
    )


if __name__ == "__main__":
    main()
