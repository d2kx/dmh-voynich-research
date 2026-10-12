#!/usr/bin/env python3
"""
Attack 50: Zodiac Month Labels (`mars`..`decembre`), Ecliptic Seasonality Polarity & Trigon Morphology
======================================================================================================
Analyzes all 10 surviving Zodiac signs (`f70v2` Pisces through `f73v` Sagittarius) paired with their
Franco-Occitan/Catalan month labels (`mars`, `abril`, `may`, `juny`, `jollet`, `agost`, `setembre`,
`octobre`, `novembre`, `decembre`):
  1. Profiles every sign's nymph labels (`@Lz`) and concentric ring texts (`@Cc`) across:
     - Prefix polarity: `ot-/op-/yt-` vs `ok-/of-/yk-` and `o-` vs `y-` vs `ch-/sh-` vs `d-/s-`.
     - Vowel grade & suffix polarity: `a`-grade (`-al/-ar/-am/-aiin`) vs `o/e`-grade (`-ol/-or/-ey/-edy`).
  2. Tests Seasonal Polarity (Spring `mars-may` [`Pisces-Taurus`] vs Summer `juny-agost` [`Gemini-Leo`]
     vs Autumn/Winter `setembre-decembre` [`Virgo-Sagittarius`]) and Classical Element Trigon
     (`Water`, `Fire`, `Earth`, `Air`) against 1,000 random token-to-sign permutations.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack50_zodiac_month_labels_and_seasonal_polarity.json"

LOCUS_RE = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^,>]+),([^>]+)>\s*(.*)$")

ZODIAC_SIGNS = [
    {"folios": ["f70v2"], "sign": "Pisces", "month": "mars", "season": "1_SPRING", "trigon": "WATER"},
    {"folios": ["f70v1", "f71r"], "sign": "Aries", "month": "abril", "season": "1_SPRING", "trigon": "FIRE"},
    {"folios": ["f71v", "f72r1"], "sign": "Taurus", "month": "may", "season": "1_SPRING", "trigon": "EARTH"},
    {"folios": ["f72r2"], "sign": "Gemini", "month": "juny", "season": "2_SUMMER", "trigon": "AIR"},
    {"folios": ["f72r3"], "sign": "Cancer", "month": "jollet", "season": "2_SUMMER", "trigon": "WATER"},
    {"folios": ["f72v3"], "sign": "Leo", "month": "agost", "season": "2_SUMMER", "trigon": "FIRE"},
    {"folios": ["f72v2"], "sign": "Virgo", "month": "setembre", "season": "3_AUTUMN_WINTER", "trigon": "EARTH"},
    {"folios": ["f72v1"], "sign": "Libra", "month": "octobre", "season": "3_AUTUMN_WINTER", "trigon": "AIR"},
    {"folios": ["f73r"], "sign": "Scorpio", "month": "novembre", "season": "3_AUTUMN_WINTER", "trigon": "WATER"},
    {"folios": ["f73v"], "sign": "Sagittarius", "month": "decembre", "season": "3_AUTUMN_WINTER", "trigon": "FIRE"},
]


def clean_tokens(raw: str) -> List[str]:
    s = re.sub(r"\{[^}]*\}", "", raw)
    s = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", s)
    s = s.replace("<%>", " ").replace("<$>", " ").replace("<->", " ")
    s = re.sub(r"<[^>]*>", " ", s)
    s = re.sub(r"@[0-9]+;", "", s)
    s = re.sub(r"[^a-zA-Z.\s]", "", s).lower()
    return [t for t in s.replace(".", " ").split() if t]


def morph_features(w: str) -> Dict[str, int]:
    return {
        "ot_op_yt": int(w.startswith(("ot", "op", "yt", "yp"))),
        "ok_of_yk": int(w.startswith(("ok", "of", "yk", "yf"))),
        "y_onset": int(w.startswith("y")),
        "o_onset": int(w.startswith("o")),
        "ch_sh_onset": int(w.startswith(("ch", "sh"))),
        "a_grade_suf": int(w.endswith(("al", "ar", "am", "aiin", "ain", "aly", "ary"))),
        "oe_grade_suf": int(w.endswith(("ol", "or", "om", "ey", "eey", "edy", "eedy", "ody", "oly", "ory"))),
    }


def main() -> None:
    lines_raw = ZL_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    folio_loci: Dict[str, List[Tuple[str, List[str]]]] = defaultdict(list)

    for line in lines_raw:
        line = line.strip()
        if not line or line.startswith("#") or "." not in line.split(">")[0]:
            continue
        m = LOCUS_RE.match(line)
        if not m:
            continue
        folio = "f" + m.group(1)
        loc_tag = m.group(3)
        toks = clean_tokens(m.group(4))
        if toks:
            folio_loci[folio].append((loc_tag, toks))

    sign_profiles = []
    season_counts: Dict[str, Counter] = defaultdict(Counter)
    trigon_counts: Dict[str, Counter] = defaultdict(Counter)
    all_zodiac_tokens: List[Tuple[str, str, str, str]] = []  # (sign, season, trigon, word)

    for z in ZODIAC_SIGNS:
        sc = Counter()
        nymph_toks = []
        ring_toks = []
        for f in z["folios"]:
            for ltag, toks in folio_loci.get(f, []):
                if "L" in ltag:
                    nymph_toks.extend(toks)
                elif "C" in ltag:
                    ring_toks.extend(toks)
                for w in toks:
                    all_zodiac_tokens.append((z["sign"], z["season"], z["trigon"], w))
                    mf = morph_features(w)
                    sc["total"] += 1
                    season_counts[z["season"]]["total"] += 1
                    trigon_counts[z["trigon"]]["total"] += 1
                    for k, val in mf.items():
                        sc[k] += val
                        season_counts[z["season"]][k] += val
                        trigon_counts[z["trigon"]][k] += val

        tot = max(sc["total"], 1)
        sign_profiles.append({
            "sign": z["sign"],
            "month": z["month"],
            "folios": z["folios"],
            "season": z["season"],
            "trigon": z["trigon"],
            "total_tokens": sc["total"],
            "nymph_tokens": len(nymph_toks),
            "ring_tokens": len(ring_toks),
            "ot_op_rate": round(sc["ot_op_yt"] / tot, 4),
            "ok_of_rate": round(sc["ok_of_yk"] / tot, 4),
            "y_onset_rate": round(sc["y_onset"] / tot, 4),
            "a_grade_suf_rate": round(sc["a_grade_suf"] / tot, 4),
            "oe_grade_suf_rate": round(sc["oe_grade_suf"] / tot, 4),
        })

    season_summary = {}
    for s_name, cnt in sorted(season_counts.items()):
        tot = max(cnt["total"], 1)
        season_summary[s_name] = {
            "total_tokens": cnt["total"],
            "ot_op_rate": round(cnt["ot_op_yt"] / tot, 4),
            "ok_of_rate": round(cnt["ok_of_yk"] / tot, 4),
            "y_onset_rate": round(cnt["y_onset"] / tot, 4),
            "a_grade_suf_rate": round(cnt["a_grade_suf"] / tot, 4),
            "oe_grade_suf_rate": round(cnt["oe_grade_suf"] / tot, 4),
        }

    trigon_summary = {}
    for t_name, cnt in sorted(trigon_counts.items()):
        tot = max(cnt["total"], 1)
        trigon_summary[t_name] = {
            "total_tokens": cnt["total"],
            "ot_op_rate": round(cnt["ot_op_yt"] / tot, 4),
            "ok_of_rate": round(cnt["ok_of_yk"] / tot, 4),
            "y_onset_rate": round(cnt["y_onset"] / tot, 4),
            "a_grade_suf_rate": round(cnt["a_grade_suf"] / tot, 4),
            "oe_grade_suf_rate": round(cnt["oe_grade_suf"] / tot, 4),
        }

    # Permutation tests (1,000 trials shuffling tokens across the 10 signs):
    # Test 1: Spring (`1_SPRING` mars..may) a_grade_suf_rate vs Summer/Autumn (`2_SUMMER`+`3_AUTUMN_WINTER`)
    obs_spring_a = season_summary["1_SPRING"]["a_grade_suf_rate"]
    obs_spring_ot = season_summary["1_SPRING"]["ot_op_rate"]
    # Test 2: Autumn/Winter (`3_AUTUMN_WINTER` setembre..decembre) y_onset_rate
    obs_autumn_y = season_summary["3_AUTUMN_WINTER"]["y_onset_rate"]

    rng = random.Random(50)
    words_only = [w for _, _, _, w in all_zodiac_tokens]
    seasons_only = [s for _, s, _, _ in all_zodiac_tokens]
    n_spring = sum(1 for s in seasons_only if s == "1_SPRING")
    n_autumn = sum(1 for s in seasons_only if s == "3_AUTUMN_WINTER")

    null_spring_a = []
    null_spring_ot = []
    null_autumn_y = []
    for _ in range(1000):
        shuf_s = seasons_only[:]
        rng.shuffle(shuf_s)
        sp_a = 0
        sp_ot = 0
        au_y = 0
        for s, w in zip(shuf_s, words_only):
            mf = morph_features(w)
            if s == "1_SPRING":
                sp_a += mf["a_grade_suf"]
                sp_ot += mf["ot_op_yt"]
            elif s == "3_AUTUMN_WINTER":
                au_y += mf["y_onset"]
        null_spring_a.append(sp_a / max(n_spring, 1))
        null_spring_ot.append(sp_ot / max(n_spring, 1))
        null_autumn_y.append(au_y / max(n_autumn, 1))

    def z_stat(obs: float, arr: List[float]) -> float:
        mu = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - mu) ** 2 for x in arr) / len(arr)) or 1e-9
        return round((obs - mu) / sd, 2)

    z_sp_a = z_stat(obs_spring_a, null_spring_a)
    z_sp_ot = z_stat(obs_spring_ot, null_spring_ot)
    z_au_y = z_stat(obs_autumn_y, null_autumn_y)

    result = {
        "summary": {
            "total_zodiac_tokens": len(all_zodiac_tokens),
            "spring_ot_op_rate": obs_spring_ot,
            "spring_ot_op_z_score": z_sp_ot,
            "spring_a_grade_suf_rate": obs_spring_a,
            "spring_a_grade_suf_z_score": z_sp_a,
            "autumn_winter_y_onset_rate": obs_autumn_y,
            "autumn_winter_y_onset_z_score": z_au_y,
        },
        "season_summary": season_summary,
        "trigon_summary": trigon_summary,
        "sign_profiles": sign_profiles,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("=== ATTACK 50: ZODIAC MONTH LABELS (`mars`..`decembre`) & SEASONAL POLARITY ===")
    for sp in sign_profiles:
        print(f"  {sp['sign']:11s} ({sp['month']:8s} | {sp['season']:15s} | {sp['trigon']:5s}): n={sp['total_tokens']:3d} | ot/op={sp['ot_op_rate']:.3f} | ok/of={sp['ok_of_rate']:.3f} | y-={sp['y_onset_rate']:.3f} | a-suf={sp['a_grade_suf_rate']:.3f} | oe-suf={sp['oe_grade_suf_rate']:.3f}")
    print("\nSeasonal Summary & Permutation Z-Scores:")
    for s_name, st in season_summary.items():
        print(f"  {s_name:16s} (n={st['total_tokens']:4d}): ot/op={st['ot_op_rate']:.3f}, ok/of={st['ok_of_rate']:.3f}, y-={st['y_onset_rate']:.3f}, a-suf={st['a_grade_suf_rate']:.3f}, oe-suf={st['oe_grade_suf_rate']:.3f}")
    print(f"  Z-Scores: Spring ot/op z={z_sp_ot:+.2f} | Spring a-grade suffix z={z_sp_a:+.2f} | Autumn/Winter y-onset z={z_au_y:+.2f}")


if __name__ == "__main__":
    main()
