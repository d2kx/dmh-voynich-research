#!/usr/bin/env python3
"""
Attack 146 (Phase 157 / Discovery 163):
Unified Structural & Lexical Compiler Test of the Six Master Index / Margin-Keyed Folios
of the Voynich Manuscript (f1r, f49v, f58r, f58v, f66r, f76r).

Tests whether the 6 Master Index & Margin-Keyed Folios (f1r, f49v, f58r, f58v, f66r, f76r)
form a statistically distinct functional class of Cross-Sectional Lexical Compilers compared
to the remaining 220 folios of the manuscript across:
  1. Prose Length & Unique Open-Class Stem Richness (2 <= df <= 45)
  2. Illustrated Diagram-Label (@Lf/@Lc/@Ln/@Lt/@Lz) Stem Compilation Density
  3. Multi-Section Hub Stem Count (stems bridging >= 3 manuscript sections)
  4. Global Cross-Section Routing IDF (tested via 1,000 random 6-folio draws and
     token-normalized per-100-word comparisons).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "folio_index.json"
EVA_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack146_six_master_index_folios_unified_compiler_test.json"

MASTER_SIX = [
    ("f1r", "Quire A $B=1 ($I=T, $L=A, $H=1): Opening Master Preface with =Pt Right-Justified Rubrics"),
    ("f49v", "Quire G $B=1 ($I=H, $L=A, $H=1): 26-Glyph + Arabic Numeral 1..5 Vertical Margin Key"),
    ("f58r", "Quire H $B=2 ($I=T, $L=B, $H=3): Unillustrated Starred Botanical-Apothecary Master Index I"),
    ("f58v", "Quire H $B=2 ($I=T, $L=B, $H=3): Unillustrated Starred Botanical-Apothecary Master Index II"),
    ("f66r", "Quire H $B=1 ($I=T, $L=B, $H=5): 15-Word + 34-Key Dual Left-Margin Clinical Treatise"),
    ("f76r", "Quire M $B=2 ($I=T, $L=B, $H=2): Unillustrated 9-Key Balneological Master Treatise"),
]

PURE_CLOSED = {"ai", "da", "ol", "or", "al", "ar", "ch", "sh", "qo", "dy", "ey", "in", "ii", "am", "y", "l", "r", "s", "d", "o", "k", "t", "p", "f"}


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def canon_stem(w: str) -> str:
    s = w.replace("f", "p").replace("t", "k")
    if s.startswith("q") and len(s) > 2:
        s = s[1:]
    for p in ["ch", "sh", "da", "sa", "ol", "al", "or", "ar", "ok", "op", "yk", "yp", "d", "s", "y", "o", "l"]:
        if s.startswith(p) and len(s) - len(p) >= 2:
            s = s[len(p):]
            break
    for suf in ["aiin", "oiin", "iin", "eedy", "edy", "ody", "ady", "dy", "ey", "oy", "ol", "al", "or", "ar", "am", "om", "an", "in", "y", "l", "r", "m", "n", "s"]:
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[:-len(suf)]
            break
    return s


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    folios_meta = folio_index["folios"]

    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s+(.*)$")

    folio_prose_tokens = defaultdict(list)
    folio_prose_stems = defaultdict(list)
    stem_folios = defaultdict(set)
    stem_sections = defaultdict(set)
    diagram_label_stems = set()

    master_set = {f for f, _ in MASTER_SIX}

    for raw_line in EVA_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = line_re.match(raw_line)
        if not m:
            continue
        fol, line_id, loc, body = m.groups()
        if ";" in line_id:
            continue
        f_key = f"f{fol}"
        meta = folios_meta.get(f_key, {})
        sec = meta.get("section_code", "H")
        loc_clean = loc.lstrip("+*=@~")

        body_clean = re.sub(r"<![^>]*>", "", body)
        body_clean = re.sub(r"<[^>]*>", " ", body_clean)
        words = [clean_tok(t) for t in re.split(r"[.\s,]+", body_clean)]
        words = [w for w in words if w]
        if not words:
            continue

        for w in words:
            st = canon_stem(w)
            stem_folios[st].add(f_key)
            stem_sections[st].add(sec)
            if loc_clean in ("Lf", "Lc", "Ln", "Lt", "Lz") and f_key not in master_set:
                diagram_label_stems.add(st)

        if loc_clean.startswith("P") or loc in ("=Pt", "+Pr", "+Pc") or (f_key == "f66r" and loc_clean == "L0" and int(re.sub(r"[^0-9]", "", line_id) or 0) <= 15):
            for w in words:
                st = canon_stem(w)
                folio_prose_tokens[f_key].append(w)
                folio_prose_stems[f_key].append(st)

    n_folios = len(folios_meta)
    open_idf = {
        st: math.log(1.0 + n_folios / len(fs))
        for st, fs in stem_folios.items()
        if st not in PURE_CLOSED and 2 <= len(fs) <= 45 and len(st) >= 2
    }
    hub3_stems = {st for st in open_idf if len(stem_sections[st]) >= 3}

    # Compute folio metrics across all folios with >= 20 prose tokens
    folio_metrics = {}
    for f_key in sorted(folios_meta.keys()):
        toks = folio_prose_tokens[f_key]
        stems = folio_prose_stems[f_key]
        if not toks:
            continue
        n_t = len(toks)
        open_set = {s for s in stems if s in open_idf}
        lbl_set = open_set & diagram_label_stems
        hub_set = open_set & hub3_stems
        tot_idf = sum(open_idf[s] for s in open_set)
        hub_idf = sum(open_idf[s] for s in hub_set)
        lbl_idf = sum(open_idf[s] for s in lbl_set)
        folio_metrics[f_key] = {
            "folio": f_key,
            "section": folios_meta[f_key].get("section_code", "H"),
            "lang": folios_meta[f_key].get("currier_lang", "A"),
            "hand": str(folios_meta[f_key].get("hand", "1")),
            "prose_tokens": n_t,
            "unique_open_stems": len(open_set),
            "open_stems_per_100tok": round(100.0 * len(open_set) / n_t, 2),
            "diagram_label_stem_matches": len(lbl_set),
            "diagram_label_idf": round(lbl_idf, 3),
            "multi_section_hub_stems": len(hub_set),
            "multi_section_hub_idf": round(hub_idf, 3),
            "total_open_stem_idf": round(tot_idf, 3),
        }

    master_profiles = []
    for f_key, desc in MASTER_SIX:
        m = dict(folio_metrics[f_key])
        m["role_description"] = desc
        master_profiles.append(m)

    other_folios = [f for f in folio_metrics if f not in master_set]

    def mean_metric(flist, key):
        return sum(folio_metrics[f][key] for f in flist) / len(flist)

    # Permutation tests (1,000 random 6-folio draws from all folios with prose)
    all_prose_folios = list(folio_metrics.keys())
    rng = random.Random(146)

    def perm_test_6folios(metric_key):
        obs = mean_metric([f for f, _ in MASTER_SIX], metric_key)
        other_mean = mean_metric(other_folios, metric_key)
        null_vals = []
        for _ in range(1000):
            samp = rng.sample(all_prose_folios, 6)
            null_vals.append(mean_metric(samp, metric_key))
        mu = sum(null_vals) / len(null_vals)
        sd = math.sqrt(sum((x - mu) ** 2 for x in null_vals) / len(null_vals))
        z = (obs - mu) / (sd if sd > 0 else 1.0)
        return {
            "master_six_mean": round(obs, 3),
            "other_folios_mean": round(other_mean, 3),
            "lift_ratio": round(obs / other_mean, 2) if other_mean > 0 else 0.0,
            "null_mean": round(mu, 3),
            "null_sd": round(sd, 3),
            "z_score": round(z, 2),
        }

    test_tokens = perm_test_6folios("prose_tokens")
    test_open_stems = perm_test_6folios("unique_open_stems")
    test_label_matches = perm_test_6folios("diagram_label_stem_matches")
    test_label_idf = perm_test_6folios("diagram_label_idf")
    test_hub_idf = perm_test_6folios("multi_section_hub_idf")

    # Union of open stems across the 6 Master Index Folios:
    # What % of all Diagram-Label Open Stems and Multi-Section Hub Stems in the codex are covered by just these 6 pages?
    union_master_open = set()
    for f, _ in MASTER_SIX:
        union_master_open.update(s for s in folio_prose_stems[f] if s in open_idf)

    union_lbl_hits = union_master_open & diagram_label_stems
    union_hub_hits = union_master_open & hub3_stems

    # Pairwise Jaccard and Exclusive Stem Partition across the 6 Master Index Folios
    master_open_sets = {
        f: {s for s in folio_prose_stems[f] if s in open_idf} for f, _ in MASTER_SIX
    }
    stem_master_df = Counter()
    for f, sset in master_open_sets.items():
        for s in sset:
            stem_master_df[s] += 1
    exclusive_to_one_master = sum(1 for s, c in stem_master_df.items() if c == 1)

    pairwise_jaccards = []
    m_keys = [f for f, _ in MASTER_SIX]
    for i in range(len(m_keys)):
        for j in range(i + 1, len(m_keys)):
            fa, fb = m_keys[i], m_keys[j]
            sa, sb = master_open_sets[fa], master_open_sets[fb]
            inter = sa & sb
            uni = sa | sb
            jacc = len(inter) / len(uni) if uni else 0.0
            pairwise_jaccards.append({
                "pair": f"{fa} <-> {fb}",
                "shared_open_stems": len(inter),
                "jaccard": round(jacc, 4),
                "shared_examples": sorted(inter, key=lambda x: -open_idf[x])[:6],
            })
    mean_pairwise_jaccard = sum(p["jaccard"] for p in pairwise_jaccards) / len(pairwise_jaccards)

    # Also add exclusive stem count and top stems to each master profile
    for p in master_profiles:
        fk = p["folio"]
        sset = master_open_sets[fk]
        excl = [s for s in sset if stem_master_df[s] == 1]
        p["exclusive_among_6_masters"] = len(excl)
        p["exclusive_pct_of_folio_open"] = round(100.0 * len(excl) / max(len(sset), 1), 2)
        p["top_idf_open_stems"] = [
            {"stem": s, "idf": round(open_idf[s], 3), "in_diagram_labels": (s in diagram_label_stems)}
            for s in sorted(sset, key=lambda x: -open_idf[x])[:8]
        ]

    out = {
        "attack": 146,
        "phase": 157,
        "discovery": 163,
        "title": "Unified Compiler Test of the Six Master Index & Margin-Keyed Folios (f1r, f49v, f58r, f58v, f66r, f76r)",
        "overview": {
            "n_master_index_folios": 6,
            "n_other_prose_folios": len(other_folios),
            "total_codex_open_stems": len(open_idf),
            "total_codex_diagram_label_open_stems": len(diagram_label_stems),
            "total_codex_multi_section_hub_stems": len(hub3_stems),
            "union_unique_open_stems_across_6_folios": len(union_master_open),
            "union_open_stem_coverage_pct": round(100.0 * len(union_master_open) / max(len(open_idf), 1), 2),
            "union_diagram_label_stem_hits": len(union_lbl_hits),
            "union_diagram_label_coverage_pct": round(100.0 * len(union_lbl_hits) / max(len(diagram_label_stems), 1), 2),
            "union_multi_section_hub_stem_hits": len(union_hub_hits),
            "union_multi_section_hub_coverage_pct": round(100.0 * len(union_hub_hits) / max(len(hub3_stems), 1), 2),
            "exclusive_to_single_master_index_folio": exclusive_to_one_master,
            "exclusive_partition_pct": round(100.0 * exclusive_to_one_master / max(len(union_master_open), 1), 2),
            "mean_pairwise_jaccard_between_6_masters": round(mean_pairwise_jaccard, 4),
            "permutation_tests_master6_vs_codex": {
                "prose_tokens_per_folio": test_tokens,
                "unique_open_stems_per_folio": test_open_stems,
                "diagram_label_stem_matches_per_folio": test_label_matches,
                "diagram_label_idf_per_folio": test_label_idf,
                "multi_section_hub_idf_per_folio": test_hub_idf,
            },
        },
        "six_master_index_folio_profiles": master_profiles,
        "pairwise_jaccard_matrix": pairwise_jaccards,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 146] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))
    for p in master_profiles:
        print(
            f"  {p['folio']} ({p['section']}, H{p['hand']}, {p['prose_tokens']}w): "
            f"open_stems={p['unique_open_stems']} (excl={p['exclusive_among_6_masters']}, {p['exclusive_pct_of_folio_open']}%), "
            f"lbl_matches={p['diagram_label_stem_matches']} (IDF={p['diagram_label_idf']}), hub_idf={p['multi_section_hub_idf']}"
        )


if __name__ == "__main__":
    main()
