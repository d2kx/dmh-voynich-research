#!/usr/bin/env python3
"""
Attack 194 (Discovery 211): Balneological f80r (11-Nymph Gallery) & f82r (Dual-Arc
Fountain, 'otol.daiin' Horizontal Jet & 'olaradag' Green-Pool Nymph), Cross-Bath
Shared Nymph Network across all 12 Labeled Balneological Folios, and the Global
'-g / -adag' Rare Label-Suffix Family across all 226 Folios.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack194_balneo_f80r_f82r_and_rare_velar_suffixes.json"

PREFIXES = ["qo", "ch", "sh", "ok", "ot", "ol", "or", "op", "of", "od", "da", "sa", "yk", "yt", "yd", "o", "d", "s", "y", "l", "r"]
SUFFIXES = ["aiin", "oiin", "eiin", "chedy", "shedy", "edy", "ody", "eey", "ey", "chy", "shy", "dy", "ol", "or", "al", "ar", "am", "om", "an", "in", "y", "r", "l", "m", "s"]


def clean_word(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    return w.strip()


def canonical_stem(w: str) -> str:
    s = w
    s = s.replace("ch", "C").replace("sh", "S").replace("ckh", "K").replace("cth", "T").replace("cph", "P").replace("cfh", "F")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    w2 = s.replace("C", "ch").replace("S", "sh").replace("K", "kh").replace("T", "th").replace("P", "ph").replace("F", "fh")
    if w2.endswith(("m", "g")) and len(w2) > 2:
        w2 = w2[:-1] + "r"
    if w2.endswith("adag") and len(w2) > 4:
        w2 = w2[:-4]
    for p in PREFIXES:
        if w2.startswith(p) and len(w2) - len(p) >= 2:
            w2 = w2[len(p):]
            break
    for suf in SUFFIXES:
        if w2.endswith(suf) and len(w2) - len(suf) >= 2:
            w2 = w2[:-len(suf)]
            break
    if w2 and w2[0] in ("p", "f", "k", "t"):
        w2 = "K" + w2[1:]
    return w2 if w2 else w


def main():
    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folio_meta = index_data.get("folios", {})

    all_tokens = []
    balneo_labels = defaultdict(list)
    balneo_prose = defaultdict(list)

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw.startswith("<f"):
            continue
        m = re.match(r"^<(f[0-9]+[rv][0-9]*)\.([^,>]+),([^>]+)>\s+(.*)$", raw)
        if not m:
            continue
        folio, lnum, ltype, body = m.groups()
        sec = folio_meta.get(folio, {}).get("section", "?")
        body_clean = re.sub(r"<!.*?>", "", body)
        tokens = [clean_word(t) for t in re.split(r"[.,\s]+", body_clean) if clean_word(t)]
        if not tokens:
            continue
        is_label = any(tag in ltype for tag in ("L", "R")) and "P" not in ltype
        for idx, tok in enumerate(tokens):
            all_tokens.append({
                "folio": folio,
                "locus": f"{folio}.{lnum}",
                "ltype": ltype,
                "sec": sec,
                "is_label": is_label,
                "is_line_final": idx == len(tokens) - 1,
                "word": tok,
                "stem": canonical_stem(tok),
            })
        if sec in ("B", "Biological") or folio.startswith(("f75", "f76", "f77", "f78", "f79", "f80", "f81", "f82", "f83", "f84")):
            if is_label:
                balneo_labels[folio].append({
                    "locus": f"{folio}.{lnum}",
                    "ltype": ltype,
                    "words": tokens,
                    "full_label": ".".join(tokens),
                    "stem": canonical_stem(tokens[0]),
                })
            elif "P" in ltype:
                balneo_prose[folio].extend(tokens)

    # 1. Audit all words containing EVA 'g' or ending in '-g' / '-adag'
    g_tokens = [t for t in all_tokens if "g" in t["word"]]
    g_end_tokens = [t for t in all_tokens if t["word"].endswith("g")]
    adag_tokens = [t for t in all_tokens if t["word"].endswith("adag") or "adag" in t["word"]]

    total_label_tokens = sum(1 for t in all_tokens if t["is_label"])
    total_prose_tokens = sum(1 for t in all_tokens if not t["is_label"])

    g_in_labels = sum(1 for t in g_tokens if t["is_label"])
    g_in_prose = sum(1 for t in g_tokens if not t["is_label"])

    g_label_rate = g_in_labels / max(1, total_label_tokens)
    g_prose_rate = g_in_prose / max(1, total_prose_tokens)
    g_label_lift = g_label_rate / max(1e-9, g_prose_rate)

    # Z-score for g enrichment in labels
    p_pool = len(g_tokens) / len(all_tokens)
    se_g = math.sqrt(p_pool * (1 - p_pool) * (1 / total_label_tokens + 1 / total_prose_tokens))
    z_g_label = (g_label_rate - g_prose_rate) / se_g if se_g > 0 else 0.0

    g_line_final_rate = sum(1 for t in g_tokens if t["is_line_final"]) / max(1, len(g_tokens))

    # 2. Detailed f80r & f82r label-to-prose concordance
    all_balneo_prose_words = {w for f in balneo_prose for w in balneo_prose[f]}
    all_balneo_prose_stems = {canonical_stem(w) for w in all_balneo_prose_words}

    def analyze_balneo_folio(folio, organ_descriptions):
        prose_w = set(balneo_prose[folio])
        prose_st = {canonical_stem(w) for w in prose_w}
        rows = []
        for idx, item in enumerate(balneo_labels[folio]):
            w0 = item["words"][0]
            st = item["stem"]
            rows.append({
                "locus": item["locus"],
                "ltype": item["ltype"],
                "label": item["full_label"],
                "stem": st,
                "position": organ_descriptions[idx] if idx < len(organ_descriptions) else "Bath nymph / stream",
                "in_same_folio_prose_exact": w0 in prose_w,
                "in_same_folio_prose_stem": st in prose_st,
                "in_balneo_prose_exact": w0 in all_balneo_prose_words,
                "in_balneo_prose_stem": st in all_balneo_prose_stems,
            })
        return {
            "folio": folio,
            "n_labels": len(rows),
            "n_prose_words": len(balneo_prose[folio]),
            "same_folio_exact_hits": sum(1 for r in rows if r["in_same_folio_prose_exact"]),
            "same_folio_stem_hits": sum(1 for r in rows if r["in_same_folio_prose_stem"]),
            "balneo_prose_stem_hits": sum(1 for r in rows if r["in_balneo_prose_stem"]),
            "labels": rows,
        }

    f80r_desc = [
        "Upper gallery Nymph #1 (far left, arms raised)",
        "Upper gallery Nymph #2 (hands on waist)",
        "Upper gallery Nymph #3 (stepping right)",
        "Upper gallery Nymph #4 (standing center-left)",
        "Upper gallery Nymph #5 (standing inside tiered blue pedestal basin!)",
        "Upper gallery Nymph #6 (seated/kneeling beside blue basin)",
        "Upper gallery Nymph #7 (embracing Nymph #8 below folio '80')",
        "Upper gallery Nymph #8 (embracing Nymph #7 above right pipe)",
        "Sinuous right-margin water conduit below '80' feeding spouted pitcher",
    ]

    f82r_desc = [
        "Middle-left nymph in blue goblet firing horizontal multi-stream water jet",
        "Lower-left shower plume above Nymph #1 in green scalloped pool",
        "Bottom-left Nymph #1 standing in cup at left edge of green pool",
        "Bottom Nymph #2 standing under left vertical shower plume",
        "Bottom Nymph #3 standing center-left in green pool",
        "Bottom Nymph #4 (crowned/braided) beside right vertical geyser plume (-adag suffix!)",
        "Bottom-right Nymph #5 standing in blue cup at right of green pool",
        "Lower-left submerged Nymph #6 in green pool scallop",
        "Lower-left submerged Nymph #7 (wearing conical cap) in green pool",
        "Lower-center submerged Nymph #8 (crowned) in green pool",
        "Lower-center submerged Nymph #9 in green pool",
        "Lower-right submerged Nymph #10 in green pool",
        "Lower-right submerged Nymph #11 at right scallop of green pool",
    ]

    f80r_profile = analyze_balneo_folio("f80r", f80r_desc)
    f82r_profile = analyze_balneo_folio("f82r", f82r_desc)

    # 3. Cross-bath shared label & stem network across all 12 labeled Balneological folios
    label_to_folios = defaultdict(list)
    stem_to_folios = defaultdict(list)
    for f, items in balneo_labels.items():
        for it in items:
            label_to_folios[it["full_label"]].append(f"{it['locus']} ({it['ltype']})")
            stem_to_folios[it["stem"]].append(f"{it['locus']} ({it['full_label']})")

    shared_exact_labels = {
        k: v for k, v in sorted(label_to_folios.items(), key=lambda x: -len(x[1])) if len(v) >= 2
    }
    shared_label_stems = {
        k: v for k, v in sorted(stem_to_folios.items(), key=lambda x: -len(x[1])) if len(v) >= 3
    }

    out = {
        "summary": {
            "total_g_tokens": len(g_tokens),
            "total_g_end_tokens": len(g_end_tokens),
            "total_adag_tokens": len(adag_tokens),
            "g_in_labels": g_in_labels,
            "g_in_prose": g_in_prose,
            "g_label_rate": round(g_label_rate, 5),
            "g_prose_rate": round(g_prose_rate, 5),
            "g_label_enrichment_lift": round(g_label_lift, 2),
            "g_label_enrichment_z": round(z_g_label, 2),
            "g_line_or_label_final_rate": round(g_line_final_rate, 4),
            "f80r_same_folio_stem_echo_rate": round(f80r_profile["same_folio_stem_hits"] / max(1, f80r_profile["n_labels"]), 4),
            "f80r_balneo_stem_echo_rate": round(f80r_profile["balneo_prose_stem_hits"] / max(1, f80r_profile["n_labels"]), 4),
            "f82r_same_folio_stem_echo_rate": round(f82r_profile["same_folio_stem_hits"] / max(1, f82r_profile["n_labels"]), 4),
            "f82r_balneo_stem_echo_rate": round(f82r_profile["balneo_prose_stem_hits"] / max(1, f82r_profile["n_labels"]), 4),
            "n_shared_exact_balneo_labels": len(shared_exact_labels),
        },
        "adag_cross_section_bridge": adag_tokens,
        "all_g_tokens": g_tokens,
        "f80r_profile": f80r_profile,
        "f82r_profile": f82r_profile,
        "shared_exact_balneo_labels": shared_exact_labels,
        "shared_balneo_label_stems": shared_label_stems,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(json.dumps(out["summary"], indent=2))
    print("adag bridge:", json.dumps(adag_tokens, indent=2))
    print("Shared exact balneo labels:", json.dumps(shared_exact_labels, indent=2))


if __name__ == "__main__":
    main()
