#!/usr/bin/env python3
"""
tools/attack158_rosettes_9sphere_and_cosmological_wheels.py

Attack 158 (Phase 169 / Discovery 175):
The Quire 14 Cosmological Foldout & 9-Sphere Rosettes Map (`f85r1–f86v6` + `fRos`):
  1. Complete locus-by-locus analysis of the Quire 14 Cosmological & Rosettes complex:
     - `f85r1`: Pure-text Opening Cosmological Treatise
     - `f85r2`: The Four-Seasons / Four-Winds Solar Wheel
     - `f86v4`: The Four-Moons Lunar Wheel
     - `f86v3`, `f86v5`, `f86v6`: Exegetical Cosmological & Four-Spouts Prose Treatises
     - `fRos` (`f85v2–f86r2`): The 9-Sphere Rosettes Foldout Map (Ring Inscriptions,
       Causeway/Wall Labels, and Margin/Corner Prose)
  2. Functional Division Between Diagram Rings/Labels (`f85r2, f86v4, fRos` `@C/@R/@L`)
     and Accompanying Prose Treatises (`f85r1, f86v3, f86v5, f86v6` `@P`):
     - Tests the Nominal `o-` Diagram Label vs. Active `qo-` Treatise Prose shift
       across Quire 14 (`1,000`-trial permutation test).
  3. Cross-Section Routing from the 9-Sphere Rosettes Map (`fRos`) to the 5 Major
     Codex Domains (`Astronomical/Zodiac`, `Herbal`, `Balneological`, `Pharmaceutical`,
     `Starred Recipes`).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack158_rosettes_9sphere_and_cosmological_wheels.json"

QUIRE14_FOLIOS = ["f85r1", "f85r2", "f86v4", "f86v3", "f86v5", "f86v6", "fRos"]


def clean_eva_token(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^\]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t)
    return t.lower()


def parse_quire14_and_domains():
    q14_by_folio = defaultdict(list)
    q14_diagram_loci = []
    q14_prose_loci = []
    domain_tokens = defaultdict(set)

    header_re = re.compile(r"^<(f[0-9A-Za-z]+)>\s*<!\s*([^>]+)>")
    locus_re = re.compile(r"^<(f[0-9A-Za-z]+)\.([^,;>]+),([^>]+)>\s*(.*)$")

    folio_sec = {}
    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m_head = header_re.match(line)
        if m_head and "$" in line:
            fol, meta_str = m_head.groups()
            sec = re.search(r"\$I=([A-Z])", meta_str)
            folio_sec[fol] = sec.group(1) if sec else "?"
            continue

        m_loc = locus_re.match(line)
        if not m_loc:
            continue
        fol, loc_id, loc_type, text = m_loc.groups()
        clean_text = re.sub(r"<[^>]+>", " ", text)
        words = [clean_eva_token(w) for w in re.split(r"[.\s,]+", clean_text)]
        words = [w for w in words if len(w) >= 2]
        if not words:
            continue

        if fol in QUIRE14_FOLIOS:
            q14_by_folio[fol].extend(words)
            if any(k in loc_type for k in ("L", "C", "R")) or fol in ("f85r2", "f86v4"):
                q14_diagram_loci.extend(words)
            else:
                q14_prose_loci.extend(words)
        else:
            sec = folio_sec.get(fol, "?")
            domain_tokens[sec].update(words)

    return q14_by_folio, q14_diagram_loci, q14_prose_loci, domain_tokens


def profile_words(words):
    n = max(1, len(words))
    return {
        "tokens": len(words),
        "o_prefix_rate": round(sum(1 for w in words if w.startswith("o")) / n, 4),
        "qo_prefix_rate": round(sum(1 for w in words if w.startswith("qo")) / n, 4),
        "edy_dy_rate": round(sum(1 for w in words if w.endswith(("edy", "dy"))) / n, 4),
        "ol_or_al_ar_rate": round(sum(1 for w in words if w.endswith(("ol", "or", "al", "ar"))) / n, 4),
        "top_words": [w for w, _ in Counter(words).most_common(8)],
    }


def main():
    q14_by_folio, diag_words, prose_words, domain_tokens = parse_quire14_and_domains()

    diag_prof = profile_words(diag_words)
    prose_prof = profile_words(prose_words)

    # 1,000-trial permutation test on (o- minus qo-) polarity between Quire 14 Diagrams and Prose
    combined = [(w, 1) for w in diag_words] + [(w, 0) for w in prose_words]
    scores = [(1 if w.startswith("o") else 0) - (1 if w.startswith("qo") else 0) for w, _ in combined]
    flags = [f for _, f in combined]
    n_d = len(diag_words)
    n_p = len(prose_words)

    obs_diff = (sum(s for s, f in zip(scores, flags) if f == 1) / max(1, n_d)) - (
        sum(s for s, f in zip(scores, flags) if f == 0) / max(1, n_p)
    )
    rng = random.Random(158)
    null_diffs = []
    for _ in range(1000):
        perm = flags[:]
        rng.shuffle(perm)
        d = (sum(s for s, f in zip(scores, perm) if f == 1) / max(1, n_d)) - (
            sum(s for s, f in zip(scores, perm) if f == 0) / max(1, n_p)
        )
        null_diffs.append(d)

    null_mean = sum(null_diffs) / len(null_diffs)
    null_sd = math.sqrt(sum((x - null_mean) ** 2 for x in null_diffs) / len(null_diffs))
    z_pol = (obs_diff - null_mean) / max(1e-9, null_sd)

    # Measure fRos vocabulary overlap with each major section (H, P, B, S, Z/A)
    fros_words = q14_by_folio["fRos"]
    fros_types = set(fros_words)
    domain_overlap = {}
    for sec, label in [("H", "Herbal"), ("P", "Pharmaceutical"), ("B", "Balneological"), ("S", "Starred_Recipes"), ("Z", "Zodiac"), ("A", "Astronomical")]:
        sec_set = domain_tokens.get(sec, set())
        matched_tokens = sum(1 for w in fros_words if w in sec_set)
        matched_types = len(fros_types & sec_set)
        domain_overlap[label] = {
            "token_coverage_rate": round(matched_tokens / max(1, len(fros_words)), 4),
            "shared_types": matched_types,
        }

    folio_profiles = {f: profile_words(q14_by_folio[f]) for f in QUIRE14_FOLIOS}

    payload = {
        "attack": 158,
        "phase": 169,
        "discovery": 175,
        "title": "Quire 14 Cosmological Wheels (f85r2, f86v4) & 9-Sphere Rosettes Map (fRos) Routing Architecture",
        "summary": {
            "total_quire14_tokens": sum(len(v) for v in q14_by_folio.values()),
            "diagram_tokens": n_d,
            "prose_treatise_tokens": n_p,
            "diagram_o_rate": diag_prof["o_prefix_rate"],
            "prose_o_rate": prose_prof["o_prefix_rate"],
            "diagram_qo_rate": diag_prof["qo_prefix_rate"],
            "prose_qo_rate": prose_prof["qo_prefix_rate"],
            "polarity_z_score": round(z_pol, 2),
        },
        "diagram_profile": diag_prof,
        "prose_treatise_profile": prose_prof,
        "fros_domain_routing": domain_overlap,
        "folio_profiles": folio_profiles,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"[Attack 158] Quire 14 Total = {payload['summary']['total_quire14_tokens']} tokens "
        f"(Diagrams = {n_d}, Prose = {n_p}); "
        f"Diagram o- = {diag_prof['o_prefix_rate']*100:.1f}% vs Prose = {prose_prof['o_prefix_rate']*100:.1f}%, "
        f"Prose qo- = {prose_prof['qo_prefix_rate']*100:.1f}% vs Diagram = {diag_prof['qo_prefix_rate']*100:.1f}% "
        f"(Polarity z = +{z_pol:.2f}); "
        f"fRos token match in Starred Recipes = {domain_overlap['Starred_Recipes']['token_coverage_rate']*100:.1f}%, "
        f"Herbal = {domain_overlap['Herbal']['token_coverage_rate']*100:.1f}%"
    )


if __name__ == "__main__":
    main()
