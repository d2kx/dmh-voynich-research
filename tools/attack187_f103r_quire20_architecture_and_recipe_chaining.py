#!/usr/bin/env python3
"""
Attack 187 (Discovery 204): Quire 20 (f103r-f116r) Opening Architecture, the f103r
Alternating Red/White Star Sequence & Bottom-Left Arabic '20' Quire Mark, Within-Page
Vertical Recipe Trajectory, and Consecutive Recipe Stem Chaining Across All Starred Recipes.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

random.seed(187)


def canonical_stem(word: str) -> str:
    w = word.lower().strip()
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return ""
    if w.startswith("qo") and len(w) > 3:
        w = w[2:]
    elif w.startswith(("o", "y", "d", "s")) and len(w) > 3:
        w = w[1:]
    w = w.replace("ee", "e").replace("ii", "i")
    for suf in ("aiin", "oiin", "eiin", "chedy", "shedy", "edy", "eey", "ody", "ady", "iin", "ain", "al", "ar", "or", "ol", "am", "om", "ey", "dy", "y"):
        if w.endswith(suf) and len(w) > len(suf) + 1:
            w = w[: -len(suf)]
            break
    w = w.replace("f", "p").replace("k", "t")
    return w


def parse_zl_recipes(path: Path):
    folios = defaultdict(lambda: {"meta": {}, "recipes": []})
    cur_folio = None
    cur_recipe = None
    line_re = re.compile(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    meta_re = re.compile(r"^<([^>]+)>\s*<!\s*(.*)\s*>$")

    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        m_meta = meta_re.match(raw)
        if m_meta:
            cur_folio = m_meta.group(1)
            meta_str = m_meta.group(2)
            for kv in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str):
                folios[cur_folio]["meta"][kv[0]] = kv[1]
            continue
        m_line = line_re.match(raw)
        if m_line:
            f_id, l_num, loc, txt = m_line.groups()
            cur_folio = f_id
            is_start = "<%>" in txt or loc.startswith("@P")
            txt_clean = re.sub(r"<!.*?>", "", txt)
            txt_clean = re.sub(r"<[^>]+>", " ", txt_clean)
            txt_clean = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", txt_clean)
            txt_clean = re.sub(r"[^a-zA-Z0-9.\s]", "", txt_clean)
            words = [w.strip() for w in re.split(r"[.\s]+", txt_clean) if w.strip() and not w.strip().isdigit()]
            if not words:
                continue
            if "P" in loc:
                if is_start or cur_recipe is None or cur_recipe["folio"] != f_id:
                    cur_recipe = {
                        "folio": f_id,
                        "start_line": f"{f_id}.{l_num}",
                        "lines": [],
                        "words": [],
                    }
                    folios[f_id]["recipes"].append(cur_recipe)
                cur_recipe["lines"].append({"line_id": f"{f_id}.{l_num}", "loc": loc, "words": words})
                cur_recipe["words"].extend(words)
    return folios


def recipe_profile(recipes):
    n_rec = len(recipes)
    if n_rec == 0:
        return {}
    words = [w for r in recipes for w in r["words"]]
    n_w = len(words)
    first_words = [r["words"][0] for r in recipes if r["words"]]
    last_words = [r["words"][-1] for r in recipes if r["words"]]
    pf_start = sum(1 for w in first_words if w.startswith(("p", "f", "op", "of"))) / len(first_words)
    tk_start = sum(1 for w in first_words if w.startswith(("t", "k", "ot", "ok"))) / len(first_words)
    ds_start = sum(1 for w in first_words if w.startswith(("d", "s"))) / len(first_words)
    qo_rate = sum(1 for w in words if w.startswith("qo")) / n_w
    edy_rate = sum(1 for w in words if w.endswith(("edy", "eey"))) / n_w
    aiin_rate = sum(1 for w in words if w.endswith(("aiin", "iin", "ain"))) / n_w
    am_end_rate = sum(1 for w in last_words if w.endswith(("am", "om", "aim", "y", "dy"))) / len(last_words)
    return {
        "n_recipes": n_rec,
        "total_words": n_w,
        "mean_words_per_recipe": round(n_w / n_rec, 2),
        "mean_lines_per_recipe": round(sum(len(r["lines"]) for r in recipes) / n_rec, 2),
        "pf_gallows_init_rate": round(pf_start, 4),
        "tk_gallows_init_rate": round(tk_start, 4),
        "ds_particle_init_rate": round(ds_start, 4),
        "qo_rate": round(qo_rate, 4),
        "edy_rate": round(edy_rate, 4),
        "aiin_rate": round(aiin_rate, 4),
        "terminal_close_rate": round(am_end_rate, 4),
    }


def main():
    zl_path = Path("data/ZL3b-n.txt")
    folios = parse_zl_recipes(zl_path)

    # Filter Quire 20 ($I=S: f103r..f116r)
    q20_folios = sorted(
        [fid for fid, fdata in folios.items() if fdata["meta"].get("I") == "S" and fdata["recipes"]],
        key=lambda x: (int(re.findall(r"\d+", x)[0]), x[-1]),
    )

    all_q20_recipes = []
    top_recipes = []
    mid_recipes = []
    bot_recipes = []

    for fid in q20_folios:
        recs = folios[fid]["recipes"]
        for idx, r in enumerate(recs):
            r["folio_recipe_idx"] = idx + 1
            r["global_idx"] = len(all_q20_recipes) + 1
            r["word_set"] = set(r["words"])
            r["stem_set"] = set(canonical_stem(w) for w in r["words"] if len(canonical_stem(w)) >= 2)
            all_q20_recipes.append(r)
            if idx == 0:
                top_recipes.append(r)
            elif idx == len(recs) - 1:
                bot_recipes.append(r)
            else:
                mid_recipes.append(r)

    # 1. f103r Grand Opening Forensics (18 recipes, Red vs White-Outline Alternating Stars)
    f103r_recs = folios["f103r"]["recipes"]
    f103r_odd_red = [r for i, r in enumerate(f103r_recs) if (i + 1) % 2 == 1]
    f103r_even_white = [r for i, r in enumerate(f103r_recs) if (i + 1) % 2 == 0]

    f103r_recipe_list = []
    for i, r in enumerate(f103r_recs):
        star_type = "Solid_Red" if (i + 1) % 2 == 1 else "Outlined_White"
        f103r_recipe_list.append({
            "recipe_num": i + 1,
            "star_visual_type": star_type,
            "start_line": r["start_line"],
            "n_lines": len(r["lines"]),
            "n_words": len(r["words"]),
            "first_word": r["words"][0],
            "last_word": r["words"][-1],
            "qo_count": sum(1 for w in r["words"] if w.startswith("qo")),
            "edy_count": sum(1 for w in r["words"] if w.endswith(("edy", "eey"))),
        })

    # 2. Consecutive Recipe Chaining (R_i -> R_{i+1} on the same page vs random recipe pairs across Quire 20)
    adj_exact_jacc = []
    adj_stem_jacc = []
    adj_shared_exact_counts = []
    adj_shared_stem_counts = []

    for fid in q20_folios:
        recs = folios[fid]["recipes"]
        for i in range(len(recs) - 1):
            r1, r2 = recs[i], recs[i + 1]
            u_w = len(r1["word_set"] | r2["word_set"]) or 1
            i_w = len(r1["word_set"] & r2["word_set"])
            u_s = len(r1["stem_set"] | r2["stem_set"]) or 1
            i_s = len(r1["stem_set"] & r2["stem_set"])
            adj_exact_jacc.append(i_w / u_w)
            adj_stem_jacc.append(i_s / u_s)
            adj_shared_exact_counts.append(i_w)
            adj_shared_stem_counts.append(i_s)

    obs_exact_jacc = sum(adj_exact_jacc) / len(adj_exact_jacc)
    obs_stem_jacc = sum(adj_stem_jacc) / len(adj_stem_jacc)
    obs_shared_exact = sum(adj_shared_exact_counts) / len(adj_shared_exact_counts)
    obs_shared_stem = sum(adj_shared_stem_counts) / len(adj_shared_stem_counts)

    # 2,000-trial permutation test shuffling recipes across Quire 20
    null_exact_jacc = []
    null_stem_jacc = []
    null_shared_exact = []
    null_shared_stem = []

    for _ in range(2000):
        shuf = all_q20_recipes[:]
        random.shuffle(shuf)
        it = iter(shuf)
        ej, sj, ec, sc = [], [], [], []
        for fid in q20_folios:
            n_r = len(folios[fid]["recipes"])
            page_r = [next(it) for _ in range(n_r)]
            for i in range(n_r - 1):
                r1, r2 = page_r[i], page_r[i + 1]
                u_w = len(r1["word_set"] | r2["word_set"]) or 1
                i_w = len(r1["word_set"] & r2["word_set"])
                u_s = len(r1["stem_set"] | r2["stem_set"]) or 1
                i_s = len(r1["stem_set"] & r2["stem_set"])
                ej.append(i_w / u_w)
                sj.append(i_s / u_s)
                ec.append(i_w)
                sc.append(i_s)
        null_exact_jacc.append(sum(ej) / len(ej))
        null_stem_jacc.append(sum(sj) / len(sj))
        null_shared_exact.append(sum(ec) / len(ec))
        null_shared_stem.append(sum(sc) / len(sc))

    def z_calc(obs, arr):
        m = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - m) ** 2 for x in arr) / len(arr)) or 1e-9
        return round(m, 4), round(obs / max(m, 1e-9), 2), round((obs - m) / sd, 2)

    null_ej_m, ej_lift, z_ej = z_calc(obs_exact_jacc, null_exact_jacc)
    null_sj_m, sj_lift, z_sj = z_calc(obs_stem_jacc, null_stem_jacc)
    null_ec_m, ec_lift, z_ec = z_calc(obs_shared_exact, null_shared_exact)
    null_sc_m, sc_lift, z_sc = z_calc(obs_shared_stem, null_shared_stem)

    # 3. Odd vs Even Recipe Alternation across all Quire 20 folios
    all_odd_recs = [r for fid in q20_folios for i, r in enumerate(folios[fid]["recipes"]) if (i + 1) % 2 == 1]
    all_even_recs = [r for fid in q20_folios for i, r in enumerate(folios[fid]["recipes"]) if (i + 1) % 2 == 0]

    out = {
        "attack": "Attack 187",
        "discovery": "Discovery 204",
        "title": "Quire 20 (f103r-f116r) Opening Architecture, f103r Alternating Red/White Star Sequence, Vertical Page Trajectory, and Consecutive Recipe Chaining",
        "quire20_overview": {
            "n_folios": len(q20_folios),
            "n_recipes": len(all_q20_recipes),
            "total_words": sum(len(r["words"]) for r in all_q20_recipes),
            "overall_profile": recipe_profile(all_q20_recipes),
        },
        "f103r_opening_forensics": {
            "bottom_left_quire_numeral": "20 (Hindu-Arabic numeral inscribed at lower-left corner of f103r)",
            "star_color_pattern": "Strict 18-star Red / Outlined-White alternation (Odd = Solid Red, Even = Outlined White)",
            "odd_red_star_profile": recipe_profile(f103r_odd_red),
            "even_white_star_profile": recipe_profile(f103r_even_white),
            "recipes": f103r_recipe_list,
        },
        "within_page_vertical_trajectory": {
            "top_first_recipes": recipe_profile(top_recipes),
            "middle_recipes": recipe_profile(mid_recipes),
            "bottom_final_recipes": recipe_profile(bot_recipes),
            "odd_numbered_recipes_global": recipe_profile(all_odd_recs),
            "even_numbered_recipes_global": recipe_profile(all_even_recs),
        },
        "consecutive_recipe_chaining": {
            "n_adjacent_pairs": len(adj_exact_jacc),
            "obs_exact_jaccard": round(obs_exact_jacc, 4),
            "null_exact_jaccard": null_ej_m,
            "exact_jaccard_lift": ej_lift,
            "z_exact_jaccard": z_ej,
            "obs_stem_jaccard": round(obs_stem_jacc, 4),
            "null_stem_jaccard": null_sj_m,
            "stem_jaccard_lift": sj_lift,
            "z_stem_jaccard": z_sj,
            "obs_mean_shared_exact_words": round(obs_shared_exact, 3),
            "null_mean_shared_exact_words": null_ec_m,
            "shared_exact_lift": ec_lift,
            "z_shared_exact": z_ec,
            "obs_mean_shared_stems": round(obs_shared_stem, 3),
            "null_mean_shared_stems": null_sc_m,
            "shared_stem_lift": sc_lift,
            "z_shared_stem": z_sc,
        },
    }

    out_path = Path("data/attack187_f103r_quire20_architecture_and_recipe_chaining.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print(f"Consecutive Recipe Exact Jaccard: {obs_exact_jacc:.4f} vs null {null_ej_m:.4f} ({ej_lift}x, z={z_ej})")
    print(f"Consecutive Recipe Stem Jaccard: {obs_stem_jacc:.4f} vs null {null_sj_m:.4f} ({sj_lift}x, z={z_sj})")
    print(f"Consecutive Recipe Shared Exact Words: {obs_shared_exact:.3f} vs null {null_ec_m:.3f} (z={z_ec})")
    print(f"Consecutive Recipe Shared Stems: {obs_shared_stem:.3f} vs null {null_sc_m:.3f} (z={z_sc})")


if __name__ == "__main__":
    main()
