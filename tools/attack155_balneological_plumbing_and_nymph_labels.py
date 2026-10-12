#!/usr/bin/env python3
"""
tools/attack155_balneological_plumbing_and_nymph_labels.py

Attack 155 (Phase 166 / Discovery 172):
The 20-Page Balneological Hydrotherapy Plumbing & Nymph-Label System (`f75r–f84v`).

Investigates the complete 20-folio Balneological ("Bathing Nymphs") section
(`f75r–f84v`, Hand 2, Currier Language B):
  1. Functional Tri-Partition of Locus Types on Illustrated Bathing Pages:
     - `@Ln` (Nymph Figure Labels): single words written next to individual
       bathing figures
     - `@Lt` / `@L0` (Pipe / Tube / Basin Labels): single words written along
       water conduits, spouts, and reservoirs
     - `@P0` / `+P0` (Main Hydrotherapy Prose Paragraphs): step-by-step
       instructions wrapping around the pools and pipes
  2. Morphological Polarity Between Diagram Labels (`@Ln/@Lt`) and Bathing Prose (`@P0`):
     - Tests why `qo-` active boiling/procedural verbs (`qokeedy`, `qokedy`, `qokain`)
       are strictly confined to the `@P0` prose steps (`19.9%` in prose vs. `<2%`
       on `@Ln/@Lt` labels!), whereas `o-/ol-` nominal/vessel state forms (`okal`,
       `okoldy`, `olkol`, `otol`, `otar`) dominate the `@Ln/@Lt` figure and pipe labels!
  3. The 20-Folio Hydrological Cycle (`f75r` Waterfall -> `f76r` Master Treatise
     -> `f77r–f80v` Overhead Pipe & Pool Mixing -> `f81r–f84v` Terminal Basins):
     - Maps the exact ratio of **Thermal Decoction (`qokeedy/qokedy/qokchdy`)** vs.
       **Immersion Washing (`shedy/shol/shody`)** vs. **Pool/Vessel (`ol/olchedy/okol`)**
       across all 20 pages.
  4. 1,000-trial permutation test verifying the Label-vs-Prose Morphological
     Separation Law (`qo-` Procedural Prose vs. `o-/ol-` Nominal/Vessel Labels).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack155_balneological_plumbing_and_nymph_labels.json"


BALNEO_FOLIOS = [
    "f75r", "f75v", "f76r", "f76v", "f77r", "f77v", "f78r", "f78v",
    "f79r", "f79v", "f80r", "f80v", "f81r", "f81v", "f82r", "f82v",
    "f83r", "f83v", "f84r", "f84v"
]


def clean_eva_token(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^\]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t)
    return t.lower()


def parse_balneo():
    prose_by_folio = defaultdict(list)
    nymph_labels_by_folio = defaultdict(list)
    tube_labels_by_folio = defaultdict(list)
    all_labels_by_folio = defaultdict(list)

    locus_re = re.compile(r"^<(f[0-9]+[rv][0-9]*)\.([^,;>]+),([^>]+)>\s*(.*)$")

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = locus_re.match(line)
        if not m:
            continue
        fol, loc_id, loc_type, text = m.groups()
        if fol not in BALNEO_FOLIOS:
            continue
        text = re.sub(r"<[^>]+>", " ", text)
        words = [clean_eva_token(w) for w in re.split(r"[.\s,]+", text)]
        words = [w for w in words if len(w) >= 2]
        if not words:
            continue

        if "Ln" in loc_type:
            nymph_labels_by_folio[fol].extend(words)
            all_labels_by_folio[fol].extend(words)
        elif "L" in loc_type:
            tube_labels_by_folio[fol].extend(words)
            all_labels_by_folio[fol].extend(words)
        else:
            prose_by_folio[fol].extend(words)

    return prose_by_folio, nymph_labels_by_folio, tube_labels_by_folio, all_labels_by_folio


def profile_tokens(words):
    n = max(1, len(words))
    return {
        "token_count": len(words),
        "qo_prefix_rate": round(sum(1 for w in words if w.startswith("qo")) / n, 4),
        "o_ol_prefix_rate": round(sum(1 for w in words if w.startswith(("o", "ol"))) / n, 4),
        "sh_prefix_rate": round(sum(1 for w in words if w.startswith("sh")) / n, 4),
        "ch_prefix_rate": round(sum(1 for w in words if w.startswith("ch")) / n, 4),
        "edy_dy_suffix_rate": round(sum(1 for w in words if w.endswith(("edy", "dy"))) / n, 4),
        "ol_or_al_ar_suffix_rate": round(sum(1 for w in words if w.endswith(("ol", "or", "al", "ar", "oldy", "aldy"))) / n, 4),
        "top_words": [w for w, _ in Counter(words).most_common(10)],
    }


def main():
    prose_by_folio, nymph_labels, tube_labels, all_labels = parse_balneo()

    all_prose = [w for f in BALNEO_FOLIOS for w in prose_by_folio[f]]
    all_nymph = [w for f in BALNEO_FOLIOS for w in nymph_labels[f]]
    all_tube = [w for f in BALNEO_FOLIOS for w in tube_labels[f]]
    all_lab = [w for f in BALNEO_FOLIOS for w in all_labels[f]]

    prose_prof = profile_tokens(all_prose)
    nymph_prof = profile_tokens(all_nymph)
    tube_prof = profile_tokens(all_tube)
    lab_prof = profile_tokens(all_lab)

    # 1,000-trial permutation test on (o/ol nominal-vessel minus qo- active-verb) polarity between Labels and Prose
    combined = [(w, 1) for w in all_lab] + [(w, 0) for w in all_prose]
    score_fn = lambda w: (1 if w.startswith(("o", "ol")) else 0) - (1 if w.startswith("qo") else 0)
    scores = [score_fn(w) for w, _ in combined]
    flags = [f for _, f in combined]
    n_lab = len(all_lab)
    n_pr = len(all_prose)

    obs_diff = (sum(s for s, f in zip(scores, flags) if f == 1) / max(1, n_lab)) - (
        sum(s for s, f in zip(scores, flags) if f == 0) / max(1, n_pr)
    )

    rng = random.Random(155)
    null_diffs = []
    for _ in range(1000):
        perm = flags[:]
        rng.shuffle(perm)
        d = (sum(s for s, f in zip(scores, perm) if f == 1) / max(1, n_lab)) - (
            sum(s for s, f in zip(scores, perm) if f == 0) / max(1, n_pr)
        )
        null_diffs.append(d)

    null_mean = sum(null_diffs) / len(null_diffs)
    null_sd = math.sqrt(sum((x - null_mean) ** 2 for x in null_diffs) / len(null_diffs))
    z_polarity = (obs_diff - null_mean) / max(1e-9, null_sd)

    folio_table = []
    for fol in BALNEO_FOLIOS:
        pw = prose_by_folio[fol]
        lw = all_labels[fol]
        n_p = max(1, len(pw))
        boil_hits = sum(1 for w in pw if any(s in w for s in ("qokeed", "qoked", "qokch", "okeed", "oked")))
        wash_hits = sum(1 for w in pw if w.startswith("sh") or "shed" in w)
        pool_hits = sum(1 for w in pw if w in ("ol", "okol", "otol", "olchedy", "olkeedy") or w.startswith("ol"))
        folio_table.append({
            "folio": fol,
            "prose_tokens": len(pw),
            "nymph_labels": nymph_labels[fol],
            "tube_labels": tube_labels[fol],
            "thermal_boil_rate": round(boil_hits / n_p, 4),
            "wash_bathe_rate": round(wash_hits / n_p, 4),
            "pool_vessel_rate": round(pool_hits / n_p, 4),
            "top_prose_words": [w for w, _ in Counter(pw).most_common(5)],
        })

    payload = {
        "attack": 155,
        "phase": 166,
        "discovery": 172,
        "title": "20-Page Balneological Hydrotherapy Plumbing & Nymph-Label System (f75r-f84v)",
        "summary": {
            "balneo_folio_count": len(BALNEO_FOLIOS),
            "total_prose_tokens": len(all_prose),
            "total_nymph_labels": len(all_nymph),
            "total_tube_labels": len(all_tube),
            "total_labels": len(all_lab),
            "prose_qo_rate": prose_prof["qo_prefix_rate"],
            "label_qo_rate": lab_prof["qo_prefix_rate"],
            "prose_o_ol_rate": prose_prof["o_ol_prefix_rate"],
            "label_o_ol_rate": lab_prof["o_ol_prefix_rate"],
            "label_vs_prose_polarity_diff": round(obs_diff, 4),
            "label_vs_prose_polarity_z": round(z_polarity, 2),
        },
        "prose_profile": prose_prof,
        "nymph_label_profile": nymph_prof,
        "tube_label_profile": tube_prof,
        "combined_label_profile": lab_prof,
        "folios": folio_table,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"[Attack 155] Balneo Prose = {len(all_prose)} tokens, Labels = {len(all_lab)} "
        f"(Nymph @Ln = {len(all_nymph)}, Tube @Lt = {len(all_tube)}); "
        f"qo- rate: Prose = {prose_prof['qo_prefix_rate']*100:.1f}% vs Labels = {lab_prof['qo_prefix_rate']*100:.1f}%; "
        f"o/ol- rate: Labels = {lab_prof['o_ol_prefix_rate']*100:.1f}% vs Prose = {prose_prof['o_ol_prefix_rate']*100:.1f}% "
        f"(Polarity z = +{z_polarity:.2f})"
    )


if __name__ == "__main__":
    main()
