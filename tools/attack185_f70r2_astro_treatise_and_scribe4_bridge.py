#!/usr/bin/env python3
"""
Attack 185 (Discovery 202): The Unfolded f69v-f70r1-f70r2 (p127) 3-Wheel Astronomical
Trifecta, f70r2's Unique 16-Line Continuous Astro-Treatise Block (154 Words), and
Scribe 4 ($H=4) Cross-Section Invariance (Astronomical $I=A/C vs. Herbal $I=H on f96r).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

random.seed(185)


def canonical_stem(word: str) -> str:
    w = word.lower().strip()
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return ""
    if w.startswith("qo") and len(w) > 3:
        w = w[2:]
    elif w.startswith(("ch", "sh")) and len(w) > 4:
        pass
    elif w.startswith(("o", "y", "d", "s")) and len(w) > 3:
        w = w[1:]
    w = w.replace("ee", "e").replace("ii", "i")
    for suf in ("aiin", "oiin", "eiin", "chedy", "shedy", "edy", "eey", "ody", "ady", "iin", "ain", "al", "ar", "or", "ol", "am", "om", "ey", "dy", "y"):
        if w.endswith(suf) and len(w) > len(suf) + 1:
            w = w[: -len(suf)]
            break
    w = w.replace("f", "p").replace("k", "t")
    return w


def parse_zl(path: Path):
    folios = defaultdict(lambda: {"meta": {}, "lines": []})
    cur_folio = None
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
            txt_clean = re.sub(r"<!.*?>", "", txt)
            has_intrusion = "<->" in txt_clean
            txt_clean = re.sub(r"<[^>]+>", " ", txt_clean)
            txt_clean = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", txt_clean)
            txt_clean = re.sub(r"[^a-zA-Z0-9.\s]", "", txt_clean)
            words = [w.strip() for w in re.split(r"[.\s]+", txt_clean) if w.strip() and not w.strip().isdigit()]
            if words:
                folios[f_id]["lines"].append({
                    "line_id": f"{f_id}.{l_num}",
                    "loc": loc,
                    "words": words,
                    "has_intrusion": has_intrusion,
                })
    return folios


def morph_profile(words):
    n = len(words)
    if n == 0:
        return {}
    qo = sum(1 for w in words if w.startswith("qo")) / n
    chsh = sum(1 for w in words if w.startswith(("ch", "sh"))) / n
    o_init = sum(1 for w in words if w.startswith("o") and not w.startswith(("ok", "ot"))) / n
    ok_ot = sum(1 for w in words if w.startswith(("ok", "ot"))) / n
    y_init = sum(1 for w in words if w.startswith("y")) / n
    edy = sum(1 for w in words if w.endswith(("edy", "eey"))) / n
    ody_ady = sum(1 for w in words if w.endswith(("ody", "ady"))) / n
    dy = sum(1 for w in words if w.endswith("dy") and not w.endswith(("edy", "ody", "ady"))) / n
    aiin = sum(1 for w in words if w.endswith(("aiin", "iin", "ain"))) / n
    al_ar_or_ol = sum(1 for w in words if w.endswith(("al", "ar", "or", "ol"))) / n
    cth_ckh = sum(1 for w in words if "cth" in w or "ckh" in w or "cph" in w or "cfh" in w) / n
    mean_len = sum(len(w) for w in words) / n
    return {
        "n_words": n,
        "n_types": len(set(words)),
        "ttr": round(len(set(words)) / n, 4),
        "mean_word_len": round(mean_len, 3),
        "qo_rate": round(qo, 4),
        "chsh_rate": round(chsh, 4),
        "o_init_rate": round(o_init, 4),
        "ok_ot_rate": round(ok_ot, 4),
        "y_init_rate": round(y_init, 4),
        "edy_rate": round(edy, 4),
        "ody_ady_rate": round(ody_ady, 4),
        "dy_bare_rate": round(dy, 4),
        "aiin_rate": round(aiin, 4),
        "liquid_suf_rate": round(al_ar_or_ol, 4),
        "cth_ckh_rate": round(cth_ckh, 4),
    }


def main():
    zl_path = Path("data/ZL3b-n.txt")
    folios = parse_zl(zl_path)

    # 1. Analyze the unfolded p127 3-wheel trifecta: f69v, f70r1, f70r2
    trifecta_ids = ["f69v", "f70r1", "f70r2"]
    trifecta_breakdown = {}
    f70r2_prose_words = []
    f70r2_ring_words = []
    trifecta_all_wheel_words = []

    for fid in trifecta_ids:
        lines = folios[fid]["lines"]
        ring_w = [w for l in lines if "C" in l["loc"] for w in l["words"]]
        spoke_w = [w for l in lines if "R" in l["loc"] for w in l["words"]]
        label_w = [w for l in lines if "L" in l["loc"] for w in l["words"]]
        prose_w = [w for l in lines if "P" in l["loc"] for w in l["words"]]
        all_w = [w for l in lines for w in l["words"]]

        if fid == "f70r2":
            f70r2_prose_words = prose_w
            f70r2_ring_words = ring_w + spoke_w + label_w
        trifecta_all_wheel_words.extend(ring_w + spoke_w + label_w)

        trifecta_breakdown[fid] = {
            "total_words": len(all_w),
            "ring_words": len(ring_w),
            "spoke_words": len(spoke_w),
            "label_words": len(label_w),
            "prose_words": len(prose_w),
            "ring_profile": morph_profile(ring_w),
            "prose_profile": morph_profile(prose_w) if prose_w else None,
            "sample_lines": [
                {"line_id": l["line_id"], "loc": l["loc"], "text": ".".join(l["words"])}
                for l in lines[:8]
            ],
        }

    # Test lexical & stem coupling between f70r2's 16-line continuous prose treatise (@P0, 154 words)
    # and the wheel rings/labels on the same unfolded sheet (f69v + f70r1 + f70r2 wheels)
    prose_set = set(f70r2_prose_words)
    prose_stems = set(canonical_stem(w) for w in f70r2_prose_words if canonical_stem(w))

    wheel_words = trifecta_all_wheel_words
    wheel_set = set(wheel_words)
    wheel_stems = set(canonical_stem(w) for w in wheel_words if canonical_stem(w))

    exact_cov_in_prose = sum(1 for w in f70r2_prose_words if w in wheel_set) / len(f70r2_prose_words)
    stem_cov_in_prose = sum(1 for w in f70r2_prose_words if canonical_stem(w) in wheel_stems) / len(f70r2_prose_words)

    # Compare against 2,000 random 154-word slices from Currier B prose paragraphs outside Quire 10
    other_b_prose = [
        w
        for fid, fdata in folios.items()
        if fdata["meta"].get("L") == "B" and fid not in trifecta_ids and fdata["meta"].get("Q") != "J"
        for l in fdata["lines"]
        if "P" in l["loc"]
        for w in l["words"]
    ]

    n_prose = len(f70r2_prose_words)
    null_exact = []
    null_stem = []
    for _ in range(2000):
        start = random.randint(0, len(other_b_prose) - n_prose)
        sample = other_b_prose[start : start + n_prose]
        null_exact.append(sum(1 for w in sample if w in wheel_set) / n_prose)
        null_stem.append(sum(1 for w in sample if canonical_stem(w) in wheel_stems) / n_prose)

    mean_exact = sum(null_exact) / len(null_exact)
    sd_exact = math.sqrt(sum((x - mean_exact) ** 2 for x in null_exact) / len(null_exact)) or 1e-9
    z_exact = (exact_cov_in_prose - mean_exact) / sd_exact

    mean_stem = sum(null_stem) / len(null_stem)
    sd_stem = math.sqrt(sum((x - mean_stem) ** 2 for x in null_stem) / len(null_stem)) or 1e-9
    z_stem = (stem_cov_in_prose - mean_stem) / sd_stem

    shared_exact_words = sorted(prose_set & wheel_set)
    shared_stems = sorted(prose_stems & wheel_stems)

    # 2. Analyze Scribe 4 ($H=4) across Astronomical/Cosmological ($I=A,C,Z) vs Herbal ($I=H: f96r/v, f93r/v, f94r/v, f95r/v)
    scribe_groups = defaultdict(list)
    for fid, fdata in folios.items():
        h = fdata["meta"].get("H", "?")
        sec = fdata["meta"].get("I", "?")
        lang = fdata["meta"].get("L", "?")
        words = [w for l in fdata["lines"] for w in l["words"]]
        scribe_groups[(h, sec, lang)].extend(words)

    scribe4_astro_words = scribe_groups.get(("4", "A", "B"), []) + scribe_groups.get(("4", "A", "?"), []) + scribe_groups.get(("4", "C", "B"), []) + scribe_groups.get(("4", "Z", "?"), [])
    # Wait: let's inspect all ($H, $I, $L) combinations present in ZL3b-n.txt!
    all_h4_folios = {}
    for fid, fdata in folios.items():
        if fdata["meta"].get("H") == "4":
            w_list = [w for l in fdata["lines"] for w in l["words"]]
            all_h4_folios[fid] = {
                "meta": fdata["meta"],
                "n_words": len(w_list),
                "profile": morph_profile(w_list),
            }

    # Also inspect f96r and f90r1/f90r2 specifically
    f96r_words = [w for l in folios["f96r"]["lines"] for w in l["words"]]
    f96r_intrusions = [l for l in folios["f96r"]["lines"] if l["has_intrusion"]]
    f90r1_words = [w for l in folios["f90r1"]["lines"] for w in l["words"]]
    f90r2_words = [w for l in folios["f90r2"]["lines"] for w in l["words"]]

    # Compare Scribe 4 vs Scribes 1, 2, 3, 5 signature features (-ody/-ady, ok-/ot- prefix rate, mean word length)
    scribe_profiles = {}
    for h_id in ["1", "2", "3", "4", "5"]:
        h_words = [
            w
            for fid, fdata in folios.items()
            if fdata["meta"].get("H") == h_id
            for l in fdata["lines"]
            for w in l["words"]
        ]
        scribe_profiles[f"Scribe_{h_id}"] = morph_profile(h_words)

    # Check Scribe 4's distinctive -ody/-ady and ok-/ot- enrichment vs all other scribes
    h4_words = [w for fid, fdata in folios.items() if fdata["meta"].get("H") == "4" for l in fdata["lines"] for w in l["words"]]
    non_h4_words = [w for fid, fdata in folios.items() if fdata["meta"].get("H") in ("1", "2", "3", "5") for l in fdata["lines"] for w in l["words"]]

    h4_prof = morph_profile(h4_words)
    non_h4_prof = morph_profile(non_h4_words)

    ody_lift = h4_prof["ody_ady_rate"] / max(non_h4_prof["ody_ady_rate"], 1e-9)
    ok_ot_lift = h4_prof["ok_ot_rate"] / max(non_h4_prof["ok_ot_rate"], 1e-9)

    out = {
        "attack": "Attack 185",
        "discovery": "Discovery 202",
        "title": "Unfolded f69v-f70r1-f70r2 3-Wheel Astronomical Trifecta, f70r2's 16-Line Astro-Treatise Block, and Scribe 4 Signature",
        "trifecta_p127": {
            "folios": trifecta_breakdown,
            "f70r2_prose_to_trifecta_wheels_coupling": {
                "f70r2_prose_words": len(f70r2_prose_words),
                "trifecta_wheel_words": len(wheel_words),
                "exact_token_coverage_in_f70r2_prose": round(exact_cov_in_prose, 4),
                "null_exact_coverage_mean": round(mean_exact, 4),
                "exact_lift": round(exact_cov_in_prose / max(mean_exact, 1e-9), 2),
                "z_exact": round(z_exact, 2),
                "stem_coverage_in_f70r2_prose": round(stem_cov_in_prose, 4),
                "null_stem_coverage_mean": round(mean_stem, 4),
                "stem_lift": round(stem_cov_in_prose / max(mean_stem, 1e-9), 2),
                "z_stem": round(z_stem, 2),
                "shared_exact_types": len(shared_exact_words),
                "shared_exact_list": shared_exact_words,
                "shared_stem_types": len(shared_stems),
                "shared_stem_list": shared_stems,
            },
        },
        "scribe_4_forensics": {
            "scribe_profiles_all_5_hands": scribe_profiles,
            "scribe_4_vs_other_scribes": {
                "h4_ody_ady_rate": h4_prof["ody_ady_rate"],
                "other_ody_ady_rate": non_h4_prof["ody_ady_rate"],
                "ody_ady_lift": round(ody_lift, 2),
                "h4_ok_ot_rate": h4_prof["ok_ot_rate"],
                "other_ok_ot_rate": non_h4_prof["ok_ot_rate"],
                "ok_ot_lift": round(ok_ot_lift, 2),
            },
            "scribe_4_folios": all_h4_folios,
        },
        "herbal_foldout_and_gap_forensics": {
            "f90r1_profile": morph_profile(f90r1_words),
            "f90r2_profile": morph_profile(f90r2_words),
            "f96r_profile": morph_profile(f96r_words),
            "f96r_meta": folios["f96r"]["meta"],
            "f96r_intrusion_lines": [
                {"line_id": l["line_id"], "text": ".".join(l["words"])}
                for l in f96r_intrusions
            ],
        },
    }

    out_path = Path("data/attack185_f70r2_astro_treatise_and_scribe4_bridge.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print("f70r2 prose -> trifecta wheels exact cov:", round(exact_cov_in_prose, 4), "vs null", round(mean_exact, 4), f"(lift {exact_cov_in_prose/mean_exact:.2f}x, z={z_exact:.2f})")
    print("f70r2 prose -> trifecta wheels stem cov:", round(stem_cov_in_prose, 4), "vs null", round(mean_stem, 4), f"(lift {stem_cov_in_prose/mean_stem:.2f}x, z={z_stem:.2f})")
    print("Scribe 4 -ody/-ady lift:", round(ody_lift, 2), "x; ok-/ot- lift:", round(ok_ot_lift, 2), "x")


if __name__ == "__main__":
    main()
