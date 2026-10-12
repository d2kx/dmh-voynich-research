#!/usr/bin/env python3
"""
Attack 161 (Phase 172 / Discovery 178):
The 14-Folio Astronomical Star-Wheel & Solar/Lunar Sector Atlas (f67r1–f70r2).

Analyzes all 14 Astronomical folios (`$I=A`: f67r1, f67r2, f67v1, f67v2, f68r1, f68r2,
f68r3, f68v1, f68v2, f68v3, f69r, f69v, f70r1, f70r2):
  1. Separates Radial Star/Sector Labels (`@Ls`, `@L0`, `@Lf`, `@Ro`) from Circular Ring &
     Paragraph Prose (`@Cc`, `@Cr`, `@P0`, `@Ri`) and tests the Radial `o-` Nominal Surge vs.
     Circular Ring Prose (`1,000`-trial permutation test).
  2. Maps each of the 14 Astronomical wheels (visual architecture, star/spoke counts, top
     emblem labels, and `doaro` Pleiades crib on `f68r3`).
  3. Quantifies the Cross-Section Lexical Routing of the 14 Astronomical wheels into the
     Zodiac (`Z`), Herbal (`H`), Pharmaceutical (`P`), Balneological (`B`), and Starred
     Master Recipes (`S`).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack161_astronomical_wheels_and_lunar_mansions.json"

ASTRO_FOLIOS_META = {
    "f67r1": {"visual_type": "12-Point Red/Blue Sun Face & Star-Count Sectors", "pdf_page": 122},
    "f67r2": {"visual_type": "8-Point Star & 12 Lunar Phase Disks with Corner Inscriptions", "pdf_page": 122},
    "f67v1": {"visual_type": "4-Quadrant Moon & Star Sector Wheel", "pdf_page": 124},
    "f67v2": {"visual_type": "8-Spoke Squared Sun & Cardinal Emblem Diagram", "pdf_page": 123},
    "f68r1": {"visual_type": "Blazing Crimson Sun Face & 36-Star Ring", "pdf_page": 125},
    "f68r2": {"visual_type": "Divided Half-Shaded Moon Face & Star Ring", "pdf_page": 125},
    "f68r3": {"visual_type": "4-Quadrant Crescent Moon Astrolabe & 7-Star Pleiades (`doaro`)", "pdf_page": 126},
    "f68v1": {"visual_type": "16-Point Indigo/White Sun Ray & Star-Wedge Wheel", "pdf_page": 125},
    "f68v2": {"visual_type": "6-Petal Indigo Flower-Star & 12-Sector Star Wheel", "pdf_page": 125},
    "f68v3": {"visual_type": "8-Arm Spiral Galaxy / Pinwheel Star-Nebula Wheel", "pdf_page": 125},
    "f69r":  {"visual_type": "16-Spoke Droplet/Channel Wheel & Concentric Rings", "pdf_page": 127},
    "f69v":  {"visual_type": "28-Spoke Lunar Mansion Star-Tip Wheel", "pdf_page": 128},
    "f70r1": {"visual_type": "Concentric 3-Ring Star & Spoke Wheel", "pdf_page": 129},
    "f70r2": {"visual_type": "Outer/Inner Concentric Astronomical Text Rings", "pdf_page": 129},
}


def clean_eva_token(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t


def parse_corpus():
    folio_sec = {}
    cur_folio = None
    cur_sec = "U"

    astro_radial_tokens = []
    astro_ring_prose_tokens = []
    folio_data = defaultdict(lambda: {"radial": [], "ring_prose": [], "all": []})
    section_vocab = defaultdict(Counter)

    loc_re = re.compile(r"^<f([0-9]+[rv][0-9]*|Ros)\.([^>]+)>\s+(.*)$")
    meta_i_re = re.compile(r"\$I=([A-Z])")

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("<f") and ">" in line and "." not in line.split(">")[0]:
            cur_folio = line.split(">")[0][1:]
            m_i = meta_i_re.search(line)
            cur_sec = m_i.group(1) if m_i else "U"
            folio_sec[cur_folio] = cur_sec
            continue

        m = loc_re.match(line)
        if not m:
            continue
        folio = "f" + m.group(1)
        loc_tag = m.group(2)
        body = m.group(3)
        sec = folio_sec.get(folio, cur_sec)

        raw_toks = re.split(r"[.\s,]+", body)
        toks = [clean_eva_token(t) for t in raw_toks]
        toks = [t for t in toks if len(t) >= 2]

        for t in toks:
            section_vocab[sec][t] += 1

        if folio in ASTRO_FOLIOS_META:
            # Radial star/sector labels vs circular ring/paragraph prose
            is_radial = any(tag in loc_tag for tag in ("@L", "&L", "@Ro", "&Ro", "@R", "&R"))
            for t in toks:
                folio_data[folio]["all"].append(t)
                if is_radial:
                    astro_radial_tokens.append(t)
                    folio_data[folio]["radial"].append(t)
                else:
                    astro_ring_prose_tokens.append(t)
                    folio_data[folio]["ring_prose"].append(t)

    return astro_radial_tokens, astro_ring_prose_tokens, folio_data, section_vocab


def profile_tokens(toks):
    n = max(len(toks), 1)
    return {
        "tokens": len(toks),
        "unique_types": len(set(toks)),
        "o_prefix_rate": round(sum(1 for t in toks if t.startswith("o")) / n, 4),
        "qo_prefix_rate": round(sum(1 for t in toks if t.startswith("qo")) / n, 4),
        "d_s_prefix_rate": round(sum(1 for t in toks if t.startswith(("d", "s"))) / n, 4),
        "y_suffix_rate": round(sum(1 for t in toks if t.endswith("y")) / n, 4),
        "al_ar_ol_or_rate": round(sum(1 for t in toks if t.endswith(("al", "ar", "ol", "or"))) / n, 4),
        "top_words": [w for w, _ in Counter(toks).most_common(10)],
    }


def main():
    radial, ring_prose, folio_data, section_vocab = parse_corpus()
    rad_prof = profile_tokens(radial)
    ring_prof = profile_tokens(ring_prose)

    # Permutation test on radial o- nominal surge vs ring/prose
    combined = radial + ring_prose
    n_rad = len(radial)
    obs_diff = rad_prof["o_prefix_rate"] - ring_prof["o_prefix_rate"]
    rng = random.Random(161)
    null_diffs = []
    for _ in range(1000):
        shuf = combined[:]
        rng.shuffle(shuf)
        r_s = shuf[:n_rad]
        p_s = shuf[n_rad:]
        d = (sum(1 for t in r_s if t.startswith("o")) / len(r_s)) - (
            sum(1 for t in p_s if t.startswith("o")) / len(p_s)
        )
        null_diffs.append(d)
    mu = sum(null_diffs) / len(null_diffs)
    sd = math.sqrt(sum((x - mu) ** 2 for x in null_diffs) / len(null_diffs)) or 1e-9
    z_o_shift = round((obs_diff - mu) / sd, 2)

    # Cross-section routing of all Astronomical tokens
    all_astro = radial + ring_prose
    routing = {}
    for sec_code, sec_name in [
        ("Z", "Zodiac"),
        ("H", "Herbal"),
        ("P", "Pharmaceutical"),
        ("B", "Balneological"),
        ("S", "Starred_Recipes"),
        ("C", "Cosmological_Rosettes"),
    ]:
        v = section_vocab[sec_code]
        matched_toks = sum(1 for t in all_astro if t in v)
        shared_types = sorted(set(t for t in all_astro if t in v), key=lambda x: -Counter(all_astro)[x])
        routing[sec_name] = {
            "token_match_rate": round(matched_toks / max(len(all_astro), 1), 4),
            "matched_tokens": matched_toks,
            "shared_types_count": len(shared_types),
            "top_shared_words": shared_types[:12],
        }

    wheels_table = []
    for f_id, meta in ASTRO_FOLIOS_META.items():
        fd = folio_data[f_id]
        all_t = fd["all"]
        rad_t = fd["radial"]
        ring_t = fd["ring_prose"]
        n_all = max(len(all_t), 1)
        wheels_table.append({
            "folio": f_id,
            "pdf_page": meta["pdf_page"],
            "visual_type": meta["visual_type"],
            "total_tokens": len(all_t),
            "radial_tokens": len(rad_t),
            "ring_prose_tokens": len(ring_t),
            "o_prefix_rate": round(sum(1 for t in all_t if t.startswith("o")) / n_all, 4),
            "match_rate_in_herbal": round(sum(1 for t in all_t if t in section_vocab["H"]) / n_all, 4),
            "match_rate_in_recipes": round(sum(1 for t in all_t if t in section_vocab["S"]) / n_all, 4),
            "top_radial_labels": [w for w, _ in Counter(rad_t).most_common(6)],
            "top_ring_words": [w for w, _ in Counter(ring_t).most_common(6)],
        })

    out = {
        "attack": 161,
        "phase": 172,
        "discovery": 178,
        "title": "14-Folio Astronomical Star-Wheel & Solar/Lunar Sector Atlas (f67r1-f70r2)",
        "summary": {
            "total_astro_folios": len(ASTRO_FOLIOS_META),
            "total_astro_tokens": len(all_astro),
            "radial_label_tokens": len(radial),
            "ring_prose_tokens": len(ring_prose),
            "radial_o_prefix_rate": rad_prof["o_prefix_rate"],
            "ring_o_prefix_rate": ring_prof["o_prefix_rate"],
            "radial_o_surge_z": z_o_shift,
            "herbal_token_match_rate": routing["Herbal"]["token_match_rate"],
            "recipes_token_match_rate": routing["Starred_Recipes"]["token_match_rate"],
        },
        "radial_profile": rad_prof,
        "ring_prose_profile": ring_prof,
        "cross_section_routing": routing,
        "wheels": wheels_table,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"[Attack 161] Astro tokens={len(all_astro)} (radial={len(radial)}, ring/prose={len(ring_prose)}), "
        f"radial o-={rad_prof['o_prefix_rate']*100:.1f}% vs ring o-={ring_prof['o_prefix_rate']*100:.1f}% "
        f"(z={z_o_shift:+.2f}), Herbal match={routing['Herbal']['token_match_rate']*100:.1f}%, "
        f"Recipes match={routing['Starred_Recipes']['token_match_rate']*100:.1f}%"
    )


if __name__ == "__main__":
    main()
