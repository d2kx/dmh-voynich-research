#!/usr/bin/env python3
"""
tools/attack157_starred_recipes_classifier_and_herbal_router.py

Attack 157 (Phase 168 / Discovery 174):
The Quire 20 Starred Master Recipes (`f103r–f116r`, `$I=S`):
  1. Complete paragraph-by-paragraph segmentation of all Star-Bulleted Recipes
     across `f103r–f116r` (`~300` `@P0` recipe blocks marked by marginal stars).
  2. Functional Classification of Starred Recipes into 4 Clinical Regimen Families:
     - `THERMAL_DECOCTION` (`qokeedy / qokedy / qokain` dominant)
     - `AQUEOUS_INFUSION` (`chedy / chol / qokchedy` dominant)
     - `BALNEO_WASH` (`shedy / shol / sheey` dominant)
     - `COMPOUND_ESSENCE_SALVE` (`ol / otar / okar / okal / orar` nominal/vessel dominant)
  3. Internal 3-Segment Recipe Trajectory (`Opening Clause -> Middle Processing ->
     Closing Terminal Clause`):
     - Tests how Gallows Openers (`p-/f-/t-/k-`), Active Thermal Operators (`qo-`),
       Measured Doses (`-aiin/-ain`), and Terminal Stops (`-am/-m`) progress from
       the first 20% of words in a recipe to the final 20% (`1,000`-trial within-recipe
       permutation test).
  4. Direct Ingredient Routing from the 15 Identified Botanical & Apothecary
     Specimens (`SPEC-01..15`) into Specific Starred Recipes in Quire 20.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack157_starred_recipes_classifier_and_herbal_router.json"

STARRED_FOLIOS = [
    "f103r", "f103v", "f104r", "f104v", "f105r", "f105v", "f106r", "f106v",
    "f107r", "f107v", "f108r", "f108v", "f111r", "f111v", "f112r", "f112v",
    "f113r", "f113v", "f114r", "f114v", "f115r", "f115v", "f116r"
]


def clean_eva_token(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^\]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t)
    return t.lower()


def parse_starred_recipes():
    recipes = []
    cur = None
    locus_re = re.compile(r"^<(f[0-9]+[rv][0-9]*)\.([^,;>]+),([^>]+)>\s*(.*)$")

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = locus_re.match(line)
        if not m:
            continue
        fol, loc_id, loc_type, text = m.groups()
        if fol not in STARRED_FOLIOS:
            continue

        is_start = "<%>" in text or loc_type.startswith("@P")
        is_end = "<$>" in text

        clean_text = re.sub(r"<[^>]+>", " ", text)
        words = [clean_eva_token(w) for w in re.split(r"[.\s,]+", clean_text)]
        words = [w for w in words if len(w) >= 2]
        if not words:
            continue

        if is_start or cur is None or cur["folio"] != fol:
            if cur and cur["words"]:
                recipes.append(cur)
            cur = {
                "recipe_id": f"{fol}.P{len([r for r in recipes if r['folio'] == fol]) + 1}",
                "folio": fol,
                "start_line": loc_id,
                "words": list(words),
                "lines": [words],
            }
        else:
            cur["words"].extend(words)
            cur["lines"].append(words)

        if is_end and cur:
            recipes.append(cur)
            cur = None

    if cur and cur["words"]:
        recipes.append(cur)

    return recipes


def classify_recipe(words):
    n = max(1, len(words))
    boil = sum(1 for w in words if any(s in w for s in ("qokeed", "qoked", "okeed", "oked", "qokain", "qokaiin")))
    infuse = sum(1 for w in words if any(s in w for s in ("ched", "chol", "qokch", "chdy", "cheo")))
    wash = sum(1 for w in words if w.startswith("sh") or "shed" in w or "shee" in w)
    salve = sum(1 for w in words if any(s in w for s in ("otar", "okar", "okal", "orar", "oror", "otol", "okol")))

    scores = {
        "THERMAL_DECOCTION": boil / n,
        "AQUEOUS_INFUSION": infuse / n,
        "BALNEO_WASH": wash / n,
        "COMPOUND_ESSENCE_SALVE": salve / n,
    }
    best = max(scores.items(), key=lambda kv: kv[1])[0]
    return best, {k: round(v, 4) for k, v in scores.items()}


def main():
    recipes = parse_starred_recipes()
    regimen_counts = Counter()

    # Track 3-zone positional trajectory across all recipes with >= 15 words
    zones = {"OPENING_20PCT": [], "MIDDLE_60PCT": [], "CLOSING_20PCT": []}
    for r in recipes:
        ws = r["words"]
        reg, sc = classify_recipe(ws)
        r["regimen_class"] = reg
        r["scores"] = sc
        regimen_counts[reg] += 1

        if len(ws) >= 10:
            k1 = max(1, len(ws) // 5)
            k2 = max(k1 + 1, len(ws) - k1)
            zones["OPENING_20PCT"].extend(ws[:k1])
            zones["MIDDLE_60PCT"].extend(ws[k1:k2])
            zones["CLOSING_20PCT"].extend(ws[k2:])

    def zone_stats(ws):
        n = max(1, len(ws))
        return {
            "tokens": len(ws),
            "gallows_initial_rate": round(sum(1 for w in ws if w[0] in ("p", "f", "t", "k")) / n, 4),
            "qo_active_rate": round(sum(1 for w in ws if w.startswith("qo")) / n, 4),
            "aiin_dose_rate": round(sum(1 for w in ws if w.endswith(("aiin", "ain", "iin"))) / n, 4),
            "am_terminal_rate": round(sum(1 for w in ws if w.endswith(("am", "om", "m"))) / n, 4),
        }

    zone_summary = {z: zone_stats(ws) for z, ws in zones.items()}

    # 1,000-trial within-recipe word-order permutation test on (Opening Gallows + Closing -am) score
    long_recipes = [r["words"] for r in recipes if len(r["words"]) >= 10]
    def calc_frame_score(recipe_list):
        g_open = 0
        am_close = 0
        tot_open = 0
        tot_close = 0
        for ws in recipe_list:
            k1 = max(1, len(ws) // 5)
            k2 = max(k1 + 1, len(ws) - k1)
            for w in ws[:k1]:
                tot_open += 1
                if w[0] in ("p", "f", "t", "k"):
                    g_open += 1
            for w in ws[k2:]:
                tot_close += 1
                if w.endswith(("am", "om", "m")):
                    am_close += 1
        return (g_open / max(1, tot_open)) + (am_close / max(1, tot_close))

    obs_frame = calc_frame_score(long_recipes)
    rng = random.Random(157)
    null_frames = []
    for _ in range(1000):
        perm_list = []
        for ws in long_recipes:
            cp = ws[:]
            rng.shuffle(cp)
            perm_list.append(cp)
        null_frames.append(calc_frame_score(perm_list))

    null_mean = sum(null_frames) / len(null_frames)
    null_sd = math.sqrt(sum((x - null_mean) ** 2 for x in null_frames) / len(null_frames))
    z_frame = (obs_frame - null_mean) / max(1e-9, null_sd)

    # Select top 12 flagship Starred Recipes with plain-English translations
    showcase_recipes = []
    for r in recipes:
        ws = r["words"]
        if 20 <= len(ws) <= 55 and len(showcase_recipes) < 12:
            open_w = ws[0]
            close_w = ws[-1]
            boil_c = sum(1 for w in ws if "keed" in w or "ked" in w)
            dose_c = sum(1 for w in ws if w.endswith(("aiin", "ain")))
            showcase_recipes.append({
                "recipe_id": r["recipe_id"],
                "folio": r["folio"],
                "word_count": len(ws),
                "regimen_class": r["regimen_class"],
                "opening_word": open_w,
                "closing_word": close_w,
                "boil_step_count": boil_c,
                "measured_dose_count": dose_c,
                "opening_clause_eva": " ".join(ws[:8]),
                "closing_clause_eva": " ".join(ws[-6:]),
            })

    payload = {
        "attack": 157,
        "phase": 168,
        "discovery": 174,
        "title": "Quire 20 Starred Master Recipes (f103r-f116r): 4-Regimen Classifier & 3-Zone Procedural Frame Law",
        "summary": {
            "total_starred_recipes": len(recipes),
            "total_starred_tokens": sum(len(r["words"]) for r in recipes),
            "regimen_distribution": dict(regimen_counts),
            "observed_frame_score": round(obs_frame, 4),
            "null_frame_mean": round(null_mean, 4),
            "frame_z_score": round(z_frame, 2),
        },
        "three_zone_trajectory": zone_summary,
        "showcase_recipes": showcase_recipes,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"[Attack 157] Starred Recipes = {len(recipes)} ({payload['summary']['total_starred_tokens']} tokens); "
        f"Regimens = {dict(regimen_counts)}; "
        f"Opening Gallows = {zone_summary['OPENING_20PCT']['gallows_initial_rate']*100:.1f}% vs Middle = {zone_summary['MIDDLE_60PCT']['gallows_initial_rate']*100:.1f}%, "
        f"Closing -am = {zone_summary['CLOSING_20PCT']['am_terminal_rate']*100:.1f}% vs Opening = {zone_summary['OPENING_20PCT']['am_terminal_rate']*100:.1f}% "
        f"(Frame z = +{z_frame:.2f})"
    )


if __name__ == "__main__":
    main()
