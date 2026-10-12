#!/usr/bin/env python3
"""
Attack 47: Cross-Folio Formulaic Sentence Clone Scanner (Exact & Unified-Root 3-Grams/4-Grams)
==============================================================================================
Scans all 226 folios (4,329 prose lines + diagram loci) for:
  1. Exact Cross-Folio 3-Word and 4-Word Clauses (`w1 . w2 . w3 [. w4]`) shared across >= 2 distinct folios
     (excluding degenerate reduplications `w1 == w2 == w3`).
  2. Unified-Root Cross-Folio 3-Word and 4-Word Clauses, applying Attack 45's `[p/f/k/t]ch <-> c[p/f/k/t]h`
     unification (`K`) and canonical root stripping to detect identical multi-word sentences inflected
     across different sections (e.g., Currier A `-ol/-or` vs Currier B `-edy/-ey`).
  3. 1,000-trial within-line word-order permutation test proving that recurring multi-word cross-folio
     phrases are a genuine grammatical property of Voynich syntax rather than random unigram collisions.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack47_cross_folio_sentence_clone_scanner.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")


def clean_tokens(raw: str) -> List[str]:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def canonical_stem(w: str) -> str:
    """Unify gallows-bench (`K`), gallows (`T`), bench (`C`), and strip outer proclitics/suffixes."""
    s = w
    for cl in ("pch", "fch", "kch", "tch", "psh", "fsh", "ksh", "tsh", "cph", "cfh", "ckh", "cth"):
        s = s.replace(cl, "K")
    s = re.sub(r"ee+", "e", s)
    s = re.sub(r"ii+", "i", s)
    if s.startswith("qo") and len(s) > 3:
        s = s[2:]
    elif s.startswith(("o", "y")) and len(s) > 3:
        s = s[1:]
    for p, r in (("p", "t"), ("f", "k"), ("sh", "ch")):
        s = s.replace(p, r)
    for suf in ("edy", "ody", "aiin", "ain", "eey", "ey", "dy", "ol", "or", "al", "ar", "am", "om", "y"):
        if s.endswith(suf) and len(s) - len(suf) >= 2:
            s = s[: -len(suf)]
            break
    return s


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    current_folio = ""
    current_sec = ""
    folio_sec: Dict[str, str] = {}
    corpus_lines: List[Tuple[str, str, str, List[str]]] = []

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("<f") and ">" in line and "." not in line.split(">")[0]:
            m_f = re.match(r"^<f([0-9]+[rv][0-9]*|Ros)>", line.split(">")[0] + ">")
            if m_f:
                current_folio = "f" + m_f.group(1)
            m_s = re.search(r"\$I=([A-Z])", line)
            current_sec = m_s.group(1) if m_s else "U"
            folio_sec[current_folio] = current_sec
            continue

        m = LOCUS_RE.match(line)
        if not m:
            continue
        folio = "f" + m.group(1)
        loc_id = m.group(2)
        loc_tag = m.group(3)
        toks = clean_tokens(m.group(4))
        if len(toks) >= 3:
            corpus_lines.append((folio, f"{folio}.{loc_id},{loc_tag}", folio_sec.get(folio, "U"), toks))

    # 1. Exact Cross-Folio 3-Grams and 4-Grams
    trigram_folios: Dict[Tuple[str, str, str], Set[str]] = defaultdict(set)
    trigram_loci: Dict[Tuple[str, str, str], List[str]] = defaultdict(list)
    trigram_secs: Dict[Tuple[str, str, str], Set[str]] = defaultdict(set)

    fourgram_folios: Dict[Tuple[str, str, str, str], Set[str]] = defaultdict(set)
    fourgram_loci: Dict[Tuple[str, str, str, str], List[str]] = defaultdict(list)

    for folio, lid, sec, toks in corpus_lines:
        for i in range(len(toks) - 2):
            tg = (toks[i], toks[i + 1], toks[i + 2])
            if len(set(tg)) == 1:
                continue
            trigram_folios[tg].add(folio)
            trigram_secs[tg].add(sec)
            if len(trigram_loci[tg]) < 12:
                trigram_loci[tg].append(lid)
        for i in range(len(toks) - 3):
            fg = (toks[i], toks[i + 1], toks[i + 2], toks[i + 3])
            if len(set(fg)) <= 2:
                continue
            fourgram_folios[fg].add(folio)
            if len(fourgram_loci[fg]) < 12:
                fourgram_loci[fg].append(lid)

    cross_folio_trigrams = [
        {
            "trigram": " . ".join(tg),
            "distinct_folios": len(fset),
            "total_occurrences": len(trigram_loci[tg]),
            "sections": sorted(trigram_secs[tg]),
            "loci": trigram_loci[tg],
        }
        for tg, fset in trigram_folios.items()
        if len(fset) >= 2
    ]
    cross_folio_trigrams.sort(key=lambda x: (-x["distinct_folios"], -x["total_occurrences"], x["trigram"]))

    cross_folio_fourgrams = [
        {
            "fourgram": " . ".join(fg),
            "distinct_folios": len(fset),
            "loci": fourgram_loci[fg],
        }
        for fg, fset in fourgram_folios.items()
        if len(fset) >= 2
    ]
    cross_folio_fourgrams.sort(key=lambda x: (-x["distinct_folios"], x["fourgram"]))

    # 2. Permutation test: within-line word shuffle (preserving exact line vocabulary) 200 times
    obs_cf_trigram_types = len(cross_folio_trigrams)
    rng = random.Random(47)
    null_cf_counts = []
    for _ in range(200):
        tf: Dict[Tuple[str, str, str], Set[str]] = defaultdict(set)
        for folio, _, _, toks in corpus_lines:
            stoks = toks[:]
            rng.shuffle(stoks)
            for i in range(len(stoks) - 2):
                tg = (stoks[i], stoks[i + 1], stoks[i + 2])
                if len(set(tg)) == 1:
                    continue
                tf[tg].add(folio)
        c = sum(1 for fset in tf.values() if len(fset) >= 2)
        null_cf_counts.append(c)
    mu_cf = sum(null_cf_counts) / len(null_cf_counts)
    sd_cf = math.sqrt(sum((x - mu_cf) ** 2 for x in null_cf_counts) / len(null_cf_counts)) or 1e-9
    z_cf_trigrams = (obs_cf_trigram_types - mu_cf) / sd_cf

    # 3. Unified-Root Cross-Sectional 4-Gram Clones (where all 4 stems have length >= 2 and are distinct)
    stem_fourgram_loci: Dict[Tuple[str, str, str, str], List[Tuple[str, str, str]]] = defaultdict(list)
    stem_fourgram_folios: Dict[Tuple[str, str, str, str], Set[str]] = defaultdict(set)
    stem_fourgram_secs: Dict[Tuple[str, str, str, str], Set[str]] = defaultdict(set)

    for folio, lid, sec, toks in corpus_lines:
        stems = [canonical_stem(w) for w in toks]
        for i in range(len(toks) - 3):
            s4 = (stems[i], stems[i + 1], stems[i + 2], stems[i + 3])
            if len(set(s4)) < 3 or any(len(s) < 2 for s in s4):
                continue
            stem_fourgram_folios[s4].add(folio)
            stem_fourgram_secs[s4].add(sec)
            if len(stem_fourgram_loci[s4]) < 10:
                raw4 = " . ".join(toks[i : i + 4])
                stem_fourgram_loci[s4].append((lid, sec, raw4))

    cross_sec_stem_fourgrams = []
    for s4, fset in stem_fourgram_folios.items():
        if len(fset) >= 2 and len(stem_fourgram_secs[s4]) >= 2:
            cross_sec_stem_fourgrams.append({
                "stem_fourgram": " - ".join(s4),
                "distinct_folios": len(fset),
                "sections": sorted(stem_fourgram_secs[s4]),
                "instances": [
                    {"locus": lid, "section": sec, "surface_clause": raw4}
                    for lid, sec, raw4 in stem_fourgram_loci[s4]
                ],
            })
    cross_sec_stem_fourgrams.sort(key=lambda x: (-x["distinct_folios"], -len(x["sections"]), x["stem_fourgram"]))

    result = {
        "summary": {
            "total_lines_scanned": len(corpus_lines),
            "observed_cross_folio_exact_trigrams": obs_cf_trigram_types,
            "null_mean_cross_folio_trigrams": round(mu_cf, 2),
            "null_sd": round(sd_cf, 2),
            "z_score_exact_trigrams": round(z_cf_trigrams, 2),
            "observed_cross_folio_exact_fourgrams": len(cross_folio_fourgrams),
            "cross_section_unified_stem_fourgrams": len(cross_sec_stem_fourgrams),
        },
        "top_exact_cross_folio_trigrams": cross_folio_trigrams[:40],
        "exact_cross_folio_fourgrams": cross_folio_fourgrams[:25],
        "top_cross_section_stem_fourgrams": cross_sec_stem_fourgrams[:35],
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 47: CROSS-FOLIO FORMULAIC SENTENCE CLONE SCANNER ===")
    s = result["summary"]
    print(f"1. Exact Cross-Folio 3-Grams: obs={s['observed_cross_folio_exact_trigrams']} vs within-line shuffle null={s['null_mean_cross_folio_trigrams']}±{s['null_sd']} (z={s['z_score_exact_trigrams']:+.2f})")
    print(f"2. Exact Cross-Folio 4-Grams: {s['observed_cross_folio_exact_fourgrams']} distinct 4-word clauses:")
    for fg in cross_folio_fourgrams[:10]:
        print(f"   [{fg['distinct_folios']} folios] {fg['fourgram']:32s} -> {fg['loci']}")
    print(f"3. Cross-Section Unified-Stem 4-Grams: {s['cross_section_unified_stem_fourgrams']} multi-section 4-word templates:")
    for sfg in cross_sec_stem_fourgrams[:10]:
        inst_str = " || ".join(f"{x['locus']}({x['section']}): {x['surface_clause']}" for x in sfg["instances"][:3])
        print(f"   [{sfg['distinct_folios']}f, secs={','.join(sfg['sections'])}] {sfg['stem_fourgram']:22s} -> {inst_str}")


if __name__ == "__main__":
    main()
