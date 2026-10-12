#!/usr/bin/env python3
"""
Phase 44 / Attack 33: Quire 20 (f103r-f116r) Marginal Star Fill, Central-Dot,
Point-Count, and Tail-Geometry Rubrication Concordance.

Parses every '# ... star ...' comment in data/ZL3b-n.txt across Quire 20 (f103r-f116v)
and tests:
1. Exact Distribution of Star Fill Types (DARK_SOLID, LIGHT_DOTTED, LIGHT_PLAIN),
   Tail Presence (TAILED vs UNTAILED), and Point Counts (6, 7, 8, 9 points) across
   the 22 folios and 6 Preparation Chapters of Quire 20.
2. Strict Alternation / Dyadic & Triadic Cadence Law (1,000-trial permutation test):
   - Tests whether LIGHT_DOTTED and LIGHT_PLAIN stars alternate in strict 1:1 dyads
     (LIGHT_DOTTED <-> LIGHT_PLAIN) significantly above random ordering within folios.
3. Grammatical & Lexical Contrast Between Paired Star Types (DARK_SOLID vs LIGHT_DOTTED
   vs LIGHT_PLAIN, and TAILED vs UNTAILED):
   - Compares paragraph length, p-/f- top-gallows opener rate, -edy/-dy verbal rate,
     -aiin unit-measure rate, -am/-om finished-product closer rate, and procedural genre.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack33_quire20_star_color_and_tail_concordance.json"


def normalize_eva(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    return w


def parse_star_comment(comment: str):
    c = comment.lower()
    if "dark" in c:
        fill = "DARK_SOLID"
    elif "dotted" in c or "dot" in c:
        fill = "LIGHT_DOTTED"
    else:
        fill = "LIGHT_PLAIN"

    has_tail = "tail" in c and "no tail" not in c
    m_pts = re.search(r"([0-9]+)\s*points", c)
    points = int(m_pts.group(1)) if m_pts else 0
    return {
        "raw_comment": comment,
        "fill_type": fill,
        "has_tail": has_tail,
        "points": points,
    }


def parse_quire20_with_stars():
    starred_units = []
    current_folio = None
    meta = {}
    pending_star = None
    current_unit = None

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    meta_re = re.compile(r"\$([A-Z])=([A-Za-z0-9]+)")

    with open(ZL_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            if raw.startswith("#"):
                if "star" in raw.lower() and ("points" in raw.lower() or "dark" in raw.lower() or "light" in raw.lower()):
                    pending_star = parse_star_comment(raw.lstrip("# ").strip())
                continue
            if raw.startswith("<f") and ">" in raw and "." not in raw.split(">")[0]:
                m_f = re.match(r"^<(f[A-Za-z0-9]+)>", raw)
                if m_f:
                    if current_unit and current_unit["tokens"]:
                        starred_units.append(current_unit)
                        current_unit = None
                    current_folio = m_f.group(1)
                    meta = dict(meta_re.findall(raw))
                    pending_star = None
                continue
            m = line_re.match(raw)
            if m and current_folio and meta.get("Q") == "T":
                f_id, loc_id, loc_type, body = m.groups()
                if "P" not in loc_type:
                    continue
                is_para_start = "<%>" in body or loc_type.startswith("@P") or loc_type.startswith("*P")
                is_para_end = "<$>" in body
                body_clean = re.sub(r"<!.*?>", "", body)
                raw_tokens = re.split(r"[.\s,]+", body_clean)
                tokens = [normalize_eva(t) for t in raw_tokens]
                tokens = [t for t in tokens if t]
                if not tokens:
                    continue

                if is_para_start or current_unit is None:
                    if current_unit and current_unit["tokens"]:
                        starred_units.append(current_unit)
                        current_unit = None
                    star_info = pending_star or {
                        "raw_comment": "unmarked",
                        "fill_type": "UNMARKED",
                        "has_tail": False,
                        "points": 0,
                    }
                    pending_star = None
                    current_unit = {
                        "folio": f_id,
                        "start_loc": loc_id,
                        "star": star_info,
                        "mid_paragraph_stars": [],
                        "tokens": list(tokens),
                        "line_count": 1,
                    }
                else:
                    if pending_star is not None:
                        current_unit["mid_paragraph_stars"].append({
                            "loc_id": loc_id,
                            "loc_type": loc_type,
                            "is_closing_line": is_para_end,
                            **pending_star,
                        })
                        # If this star comment sits on the <$> closing line, keep it in pending_star
                        # so the immediately following <%> opener inherits its marginal star!
                        if not is_para_end:
                            pending_star = None
                    current_unit["tokens"].extend(tokens)
                    current_unit["line_count"] += 1

                if is_para_end and current_unit:
                    starred_units.append(current_unit)
                    current_unit = None

    if current_unit and current_unit["tokens"]:
        starred_units.append(current_unit)

    return starred_units


def profile_units(units):
    n_u = max(len(units), 1)
    all_toks = [t for u in units for t in u["tokens"]]
    n_t = max(len(all_toks), 1)
    openers = [u["tokens"][0] for u in units if u["tokens"]]
    closers = [u["tokens"][-1] for u in units if u["tokens"]]

    return {
        "paragraph_count": len(units),
        "mean_words_per_paragraph": round(len(all_toks) / n_u, 2),
        "mean_lines_per_paragraph": round(sum(u["line_count"] for u in units) / n_u, 2),
        "opener_p_f_top_gallows_rate": round(sum(1 for w in openers if w.startswith(("p", "f"))) / max(len(openers), 1), 4),
        "opener_k_t_gallows_rate": round(sum(1 for w in openers if w.startswith(("k", "t"))) / max(len(openers), 1), 4),
        "opener_qok_qot_rate": round(sum(1 for w in openers if w.startswith(("qok", "qot", "qo"))) / max(len(openers), 1), 4),
        "opener_d_s_deictic_rate": round(sum(1 for w in openers if w.startswith(("d", "s"))) / max(len(openers), 1), 4),
        "closer_am_om_product_rate": round(sum(1 for w in closers if w.endswith(("am", "om", "an"))) / max(len(closers), 1), 4),
        "body_edy_dy_verbal_rate": round(sum(1 for t in all_toks if t.endswith(("edy", "eedy", "dy"))) / n_t, 4),
        "body_aiin_unit_rate": round(sum(1 for t in all_toks if t.endswith(("aiin", "iin", "in"))) / n_t, 4),
        "body_sh_decoction_rate": round(sum(1 for t in all_toks if "sh" in t) / n_t, 4),
        "body_ch_mixture_rate": round(sum(1 for t in all_toks if "ch" in t) / n_t, 4),
        "body_k_vessel_rate": round(sum(1 for t in all_toks if "k" in t) / n_t, 4),
        "body_t_conduit_rate": round(sum(1 for t in all_toks if "t" in t) / n_t, 4),
    }


def main():
    random.seed(42)
    units = parse_quire20_with_stars()

    fill_counts = Counter(u["star"]["fill_type"] for u in units)
    tail_counts = Counter("TAILED" if u["star"]["has_tail"] else "UNTAILED" for u in units if u["star"]["fill_type"] != "UNMARKED")
    point_counts = Counter(u["star"]["points"] for u in units if u["star"]["points"] > 0)

    # Folio-by-folio star breakdown
    folios_order = []
    for u in units:
        if u["folio"] not in folios_order:
            folios_order.append(u["folio"])

    folio_star_table = []
    for f_id in folios_order:
        f_units = [u for u in units if u["folio"] == f_id]
        fc = Counter(u["star"]["fill_type"] for u in f_units)
        tc = Counter("TAILED" if u["star"]["has_tail"] else "UNTAILED" for u in f_units if u["star"]["fill_type"] != "UNMARKED")
        pc = Counter(u["star"]["points"] for u in f_units if u["star"]["points"] > 0)
        seq = [u["star"]["fill_type"] for u in f_units]
        folio_star_table.append({
            "folio": f_id,
            "paragraph_count": len(f_units),
            "fill_counts": dict(fc),
            "tail_counts": dict(tc),
            "point_counts": {str(k): v for k, v in sorted(pc.items())},
            "star_sequence": seq,
        })

    # Test strict alternation (F_i != F_{i+1}) on folios where LIGHT_DOTTED and LIGHT_PLAIN co-occur
    # vs random permutation within each folio!
    dyad_folios = [
        f_id for f_id in folios_order
        if sum(1 for u in units if u["folio"] == f_id and u["star"]["fill_type"] == "LIGHT_DOTTED") >= 2
        and sum(1 for u in units if u["folio"] == f_id and u["star"]["fill_type"] == "LIGHT_PLAIN") >= 2
    ]

    def score_alternation(seq_by_folio):
        alt_hits = 0
        total_adj = 0
        for f_id, seq in seq_by_folio.items():
            filtered = [s for s in seq if s in ("LIGHT_DOTTED", "LIGHT_PLAIN")]
            for i in range(len(filtered) - 1):
                total_adj += 1
                if filtered[i] != filtered[i + 1]:
                    alt_hits += 1
        return alt_hits, total_adj

    obs_seqs = {
        f_id: [u["star"]["fill_type"] for u in units if u["folio"] == f_id]
        for f_id in dyad_folios
    }
    obs_alt, total_adj = score_alternation(obs_seqs)

    null_alts = []
    for _ in range(1000):
        perm_seqs = {}
        for f_id, seq in obs_seqs.items():
            filtered = [s for s in seq if s in ("LIGHT_DOTTED", "LIGHT_PLAIN")]
            random.shuffle(filtered)
            perm_seqs[f_id] = filtered
        na, _ = score_alternation(perm_seqs)
        null_alts.append(na)

    mean_na = sum(null_alts) / len(null_alts)
    std_na = math.sqrt(sum((x - mean_na) ** 2 for x in null_alts) / len(null_alts)) or 1.0
    z_alt = (obs_alt - mean_na) / std_na
    p_alt = sum(1 for x in null_alts if x >= obs_alt) / len(null_alts)

    # Profile by Fill Type and Tail Presence
    by_fill_profiles = {}
    for ft in ("DARK_SOLID", "LIGHT_DOTTED", "LIGHT_PLAIN", "UNMARKED"):
        sub = [u for u in units if u["star"]["fill_type"] == ft]
        if sub:
            by_fill_profiles[ft] = profile_units(sub)

    by_tail_profiles = {
        "TAILED": profile_units([u for u in units if u["star"]["fill_type"] != "UNMARKED" and u["star"]["has_tail"]]),
        "UNTAILED": profile_units([u for u in units if u["star"]["fill_type"] != "UNMARKED" and not u["star"]["has_tail"]]),
    }

    # Check mid-paragraph stars (stars placed on the final/continuation line of a paragraph!)
    mid_para_stars = []
    for u in units:
        for ms in u["mid_paragraph_stars"]:
            mid_para_stars.append({
                "folio": u["folio"],
                "para_start_loc": u["start_loc"],
                "para_opening_star": u["star"]["fill_type"],
                **ms,
            })

    result = {
        "phase": "Phase 44 / Attack 33",
        "title": "Quire 20 (f103r-f116r) Marginal Star Fill, Central-Dot, Point-Count, and Tail-Geometry Rubrication Concordance",
        "overall_star_counts": {
            "total_paragraphs": len(units),
            "fill_type_counts": dict(fill_counts),
            "tail_counts": dict(tail_counts),
            "point_counts": {str(k): v for k, v in sorted(point_counts.items())},
            "mid_paragraph_extra_stars_count": len(mid_para_stars),
        },
        "dyadic_dotted_plain_alternation_law": {
            "evaluated_dyad_folios": dyad_folios,
            "adjacent_dotted_plain_pairs": total_adj,
            "observed_alternating_pairs": obs_alt,
            "observed_alternation_rate": round(obs_alt / max(total_adj, 1), 4),
            "null_within_folio_mean": round(mean_na, 2),
            "null_within_folio_rate": round(mean_na / max(total_adj, 1), 4),
            "null_within_folio_std": round(std_na, 2),
            "z_score": round(z_alt, 2),
            "p_value": round(p_alt, 4),
        },
        "grammatical_profile_by_fill_type": by_fill_profiles,
        "grammatical_profile_by_tail_geometry": by_tail_profiles,
        "mid_paragraph_extra_stars": mid_para_stars,
        "folio_star_table": folio_star_table,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Overall star counts:", json.dumps(result["overall_star_counts"], indent=2))
    print("Dyadic alternation law:", json.dumps(result["dyadic_dotted_plain_alternation_law"], indent=2))
    print("Profile by fill type:", json.dumps(result["grammatical_profile_by_fill_type"], indent=2))
    print("Profile by tail geometry:", json.dumps(result["grammatical_profile_by_tail_geometry"], indent=2))


if __name__ == "__main__":
    main()
