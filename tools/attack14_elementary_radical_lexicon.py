#!/usr/bin/env python3
"""
Attack 14 (Phase 25 / Discovery 31):
Visual, Domain & Syntactic Grounding of the Top 50 Elementary Radicals (`90.5%` Token Coverage).

Builds the First Empirical Radical Lexicon Table of the Voynich Manuscript by cross-tabulating
the Top 50 elementary radicals (`k`, `t`, `ch`, `d`, `sh`, `ol`, `che`, `tch`, `s`, `ke`, `cth`,
`cho`, `kch`, `she`, `ar`, `al`, `or`, `tol`, `kol`, `tar`, `tal`, `dar`, `dal`, `teo`, `air`, `dai`, etc.)
against:
1. Diagram Object Type (`@Lc` Apothecary Jars, `@Lf` Botanical Plant Parts, `@Lz` Barreled vs. Unbarreled
   Zodiac Nymphs, `@Ln` Biological Nymphs, `@Lt` Biological Tubes/Pools, `@Ls` Astronomical Stars,
   `@L0` 9-Rosettes Cosmological Map).
2. Astrological Elemental Trigon (`Water: Pisces/Cancer/Scorpio`, `Earth: Taurus/Virgo`,
   `Fire: Aries/Leo/Sagittarius`, `Air: Gemini/Libra`).
3. Manuscript Section Enrichment (`$I=H` Herbal A vs B, `$I=P` Pharma, `$I=Z` Zodiac, `$I=A` Astro,
   `$I=C` Cosmo, `$I=B` Bio, `$I=S` Starred Recipes).
4. Syntactic Slot & Inflectional Profile (`q-` Proclitic Rate, `o-` Nominal Classifier Rate,
   `y-` Initial Rate, Dominant Suffix, Pre-Crib `w-1` vs Post-Crib `w+1` Enrichment,
   and Compound Slot 1 Onset vs Slot 2 Coda Polarity).
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
ATTACK12_JSON = ROOT / "data" / "attack12_core_root_radical_decomposition.json"
OUT_PATH = ROOT / "data" / "attack14_elementary_radical_lexicon.json"

SUFFIX_PAT = re.compile(
    r"(aiin|ain|iin|in|edy|eedy|ody|dy|eey|ey|ary|ory|ry|aly|oly|ly|am|om|al|ol|ar|or|y|r|l|s|d)$"
)

ZODIAC_TRIGON = {
    "f70v2": "Water",   # Pisces (Barreled)
    "f70v1": "Fire",    # Aries I (Barreled)
    "f71r":  "Fire",    # Aries II (Barreled)
    "f71v":  "Earth",   # Taurus I (Barreled)
    "f72r1": "Earth",   # Taurus II (Barreled)
    "f72r2": "Air",     # Gemini (Unbarreled)
    "f72r3": "Water",   # Cancer (Unbarreled)
    "f72v3": "Fire",    # Leo (Unbarreled)
    "f72v2": "Earth",   # Virgo (Unbarreled)
    "f72v1": "Air",     # Libra (Unbarreled)
    "f73r":  "Water",   # Scorpio (Unbarreled)
    "f73v":  "Fire",    # Sagittarius (Unbarreled)
}

ZODIAC_BARRELED = {"f70v2", "f70v1", "f71r", "f71v", "f72r1"}


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"@\d+;", "", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t.strip()


def stage1_gallows(w: str) -> str:
    return w.replace("p", "t").replace("f", "k")


def stage2_vowels(w: str) -> str:
    s = stage1_gallows(w)
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    return s


def extract_core_root_and_envelope(w: str):
    s0 = w
    has_pf = ("p" in s0) or ("f" in s0)
    s2 = stage2_vowels(s0)
    s3 = s2
    has_q = False
    has_y = False
    has_o = False
    has_m = False

    if len(s3) > 2 and s3[0] == "q" and s3[1] in ("o", "e", "a"):
        has_q = True
        s3 = s3[1:]
    elif len(s3) > 2 and s3[0] == "y" and s3[1] in ("o", "e", "a", "t", "k", "c", "s"):
        has_y = True
        s3 = s3[1:]

    if s3.endswith("m") and len(s3) > 2:
        has_m = True
        s3 = s3[:-1] + "r"

    s4 = s3
    if len(s4) > 2 and s4.startswith("o") and not s4.startswith(("ol", "or")):
        has_o = True
        s4 = s4[1:]

    m_suf = SUFFIX_PAT.search(s4)
    if m_suf and len(s4) - len(m_suf.group(1)) >= 1:
        suf = m_suf.group(1)
        core = s4[:-len(suf)]
    else:
        suf = "0"
        core = s4

    return {
        "orig": w,
        "core": core,
        "suff": suf,
        "has_pf": has_pf,
        "has_q": has_q,
        "has_y": has_y,
        "has_o": has_o,
        "has_m": has_m,
    }


def tokenize_eva_glyphs(s: str):
    units = []
    i = 0
    n = len(s)
    while i < n:
        if i + 3 <= n and s[i:i+3] in ("cth", "ckh", "cph", "cfh"):
            units.append(s[i:i+3])
            i += 3
        elif i + 2 <= n and s[i:i+2] in ("ch", "sh", "ai", "oi", "ei", "eo"):
            units.append(s[i:i+2])
            i += 2
        else:
            units.append(s[i])
            i += 1
    return units


def parse_zl():
    text = ZL_PATH.read_text(encoding="utf-8", errors="ignore")
    records = []
    current_folio = None
    cur_meta = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m_page = re.match(r"^<(f[\w]+)>\s*(?:<!\s*(.*?)\s*>)?", line)
        if m_page and "." not in m_page.group(1):
            current_folio = m_page.group(1)
            cur_meta = {}
            if m_page.group(2):
                for kv in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", m_page.group(2)):
                    cur_meta[kv[0]] = kv[1]
            continue

        m_loc = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m_loc or not current_folio:
            continue
        loc_header = m_loc.group(1)
        body = m_loc.group(2)
        parts = loc_header.split(",")
        loc_id = parts[0]
        unit_type = parts[1] if len(parts) > 1 else ""

        body_no_comments = re.sub(r"<!([^>]*)>", "", body)
        body_no_comments = body_no_comments.replace("<%>", "").replace("<$>", "")

        segments = body_no_comments.split("<->")
        words = []
        for seg in segments:
            seg_toks = [clean_tok(t) for t in re.split(r"[\.\s,]+", seg) if t]
            seg_toks = [w for w in seg_toks if w]
            words.extend(seg_toks)

        if not words:
            continue

        is_label = ("@L" in unit_type) or ("&L" in unit_type) or unit_type.startswith("L")
        records.append({
            "folio": current_folio,
            "loc_id": loc_id,
            "unit_type": unit_type,
            "lang": cur_meta.get("L", "Unknown"),
            "hand": cur_meta.get("H", "Unknown"),
            "illus": cur_meta.get("I", "Unknown"),
            "is_label": is_label,
            "words": words,
        })

    return records


def label_object_category(folio: str, unit_type: str, illus: str) -> str:
    if folio in ("fRos", "f85v2"):
        return "Rosettes_Map_Label"
    if folio in ZODIAC_TRIGON:
        if folio in ZODIAC_BARRELED:
            return "Zodiac_Barreled_Nymph"
        return "Zodiac_Free_Nymph"
    if folio.startswith(("f67", "f68", "f69", "f70r")):
        return "Astro_Star_Spoke"
    if "Lc" in unit_type:
        return "Pharma_Apothecary_Jar"
    if "Lf" in unit_type or illus == "P":
        return "Pharma_Botanical_Plant"
    if "Lt" in unit_type:
        return "Bio_Tube_Vessel"
    if "Ln" in unit_type or illus == "B":
        return "Bio_Bathing_Nymph"
    return f"Other_Label_{illus}"


def section_bucket(folio: str, illus: str, lang: str) -> str:
    if folio in ("fRos", "f85v2") or illus == "C":
        return "Cosmological_Rosettes"
    if illus == "H":
        return f"Herbal_{lang}"
    if illus == "P":
        return "Pharmaceutical"
    if illus == "Z":
        return "Zodiac"
    if illus == "A":
        return "Astronomical"
    if illus == "B":
        return "Biological_Balneological"
    if illus == "S" or folio.startswith(("f103", "f104", "f105", "f106", "f107", "f108", "f111", "f112", "f113", "f114", "f115", "f116")):
        return "Starred_Recipes"
    return f"Section_{illus}"


def main():
    records = parse_zl()

    # Build the exact same radical segmenter as Attack 12
    root_token_counts = Counter()
    for r in records:
        for w in r["words"]:
            m = extract_core_root_and_envelope(w)
            root_token_counts[m["core"]] += 1

    sub_counts = Counter()
    for rt, cnt in root_token_counts.items():
        if len(rt) <= 4:
            sub_counts[rt] += cnt
        for split in range(1, len(rt)):
            p1, p2 = rt[:split], rt[split:]
            if 1 <= len(p1) <= 4 and 1 <= len(p2) <= 4:
                sub_counts[p1] += 1
                sub_counts[p2] += 1

    radical_scores = {}
    for cand, sc in sub_counts.items():
        g = tokenize_eva_glyphs(cand)
        if 1 <= len(g) <= 3:
            stand_cnt = root_token_counts.get(cand, 0)
            if len(g) <= 2 and (stand_cnt >= 5 or sc >= 15):
                radical_scores[cand] = stand_cnt + 5 * sc
            elif len(g) == 3 and (stand_cnt >= 20 or sc >= 40):
                radical_scores[cand] = stand_cnt + 3 * sc

    atomic_glyphs = [
        "k", "t", "p", "f", "ch", "sh", "cth", "ckh", "cph", "cfh",
        "d", "s", "l", "r", "m", "n", "g",
        "o", "a", "e", "i", "y", "ai", "oi", "ei", "eo"
    ]
    for ag in atomic_glyphs:
        if ag not in radical_scores:
            radical_scores[ag] = max(root_token_counts.get(ag, 1), 1)

    total_rad_mass = sum(radical_scores.values())
    rad_logp = {r: math.log(v / total_rad_mass) for r, v in radical_scores.items()}

    def segment_root(rt: str):
        n = len(rt)
        if n <= 1:
            return [rt]
        glyphs = tokenize_eva_glyphs(rt)
        if len(glyphs) == 1:
            return [rt]
        force_split = len(glyphs) >= 3 and root_token_counts[rt] <= 200
        seg_penalty = 4.2
        dp = [(-1e18, []) for _ in range(n + 1)]
        dp[0] = (0.0, [])
        for i in range(1, n + 1):
            for j in range(max(0, i - 5), i):
                piece = rt[j:i]
                if force_split and j == 0 and i == n:
                    continue
                if piece in rad_logp:
                    score = dp[j][0] + rad_logp[piece] - (seg_penalty if j > 0 else 0.0)
                    if score > dp[i][0]:
                        dp[i] = (score, dp[j][1] + [piece])
                elif i - j == 1:
                    score = dp[j][0] - 12.0 - (seg_penalty if j > 0 else 0.0)
                    if score > dp[i][0]:
                        dp[i] = (score, dp[j][1] + [piece])
        return dp[n][1] if dp[n][1] else [rt]

    # Cache segmentation for every unique root
    root_to_rads = {rt: segment_root(rt) for rt in root_token_counts}

    # Collect comprehensive stats per elementary radical
    rad_total_tokens = Counter()
    rad_prose_tokens = Counter()
    rad_label_tokens = Counter()
    rad_standalone_tokens = Counter()
    rad_slot1_tokens = Counter()
    rad_slot2_tokens = Counter()
    rad_q_tokens = Counter()
    rad_o_tokens = Counter()
    rad_y_tokens = Counter()
    rad_pf_tokens = Counter()
    rad_m_tokens = Counter()
    rad_suffix_counts = defaultdict(Counter)
    rad_section_counts = defaultdict(Counter)
    rad_label_obj_counts = defaultdict(Counter)
    rad_trigon_counts = defaultdict(Counter)

    section_total_rad_tokens = Counter()
    label_obj_total_rad_tokens = Counter()
    trigon_total_rad_tokens = Counter()
    total_rad_instances = 0
    total_label_rad_instances = 0

    for r in records:
        sec_b = section_bucket(r["folio"], r["illus"], r["lang"])
        l_obj = label_object_category(r["folio"], r["unit_type"], r["illus"]) if r["is_label"] else None
        trig = ZODIAC_TRIGON.get(r["folio"]) if r["is_label"] else None

        for w in r["words"]:
            m = extract_core_root_and_envelope(w)
            rt = m["core"]
            rads = root_to_rads[rt]
            for idx, rad in enumerate(rads):
                total_rad_instances += 1
                rad_total_tokens[rad] += 1
                section_total_rad_tokens[sec_b] += 1
                rad_section_counts[rad][sec_b] += 1
                rad_suffix_counts[rad][m["suff"]] += 1

                if len(rads) == 1:
                    rad_standalone_tokens[rad] += 1
                elif idx == 0:
                    rad_slot1_tokens[rad] += 1
                else:
                    rad_slot2_tokens[rad] += 1

                if m["has_q"]:
                    rad_q_tokens[rad] += 1
                if m["has_o"]:
                    rad_o_tokens[rad] += 1
                if m["has_y"]:
                    rad_y_tokens[rad] += 1
                if m["has_pf"]:
                    rad_pf_tokens[rad] += 1
                if m["has_m"]:
                    rad_m_tokens[rad] += 1

                if r["is_label"]:
                    total_label_rad_instances += 1
                    rad_label_tokens[rad] += 1
                    label_obj_total_rad_tokens[l_obj] += 1
                    rad_label_obj_counts[rad][l_obj] += 1
                    if trig:
                        trigon_total_rad_tokens[trig] += 1
                        rad_trigon_counts[rad][trig] += 1
                else:
                    rad_prose_tokens[rad] += 1

    # Select Top 60 radicals (covering all Top 50 by token frequency + key multi-letter radicals like tol, kol, tar, tal, dar, dal, teo, air)
    top_rads = [r for r, _ in rad_total_tokens.most_common(50)]
    extra_key_rads = ["tol", "kol", "tar", "tal", "dar", "dal", "teo", "keo", "air", "dai", "tai", "kai", "sal", "sar", "kar", "kal"]
    for er in extra_key_rads:
        if er not in top_rads and rad_total_tokens[er] > 0:
            top_rads.append(er)

    lexicon_entries = []
    for rank_idx, rad in enumerate(top_rads, 1):
        tot = rad_total_tokens[rad]
        lbl = rad_label_tokens[rad]
        p_global = tot / total_rad_instances
        p_label_global = lbl / max(total_label_rad_instances, 1)

        # Compute enrichment across Manuscript Sections
        sec_enrichments = {}
        for sec_b, sec_tot in section_total_rad_tokens.items():
            c_sec = rad_section_counts[rad][sec_b]
            p_sec = c_sec / max(sec_tot, 1)
            enr = p_sec / max(p_global, 1e-9)
            sec_enrichments[sec_b] = {"count": c_sec, "enrichment": round(enr, 2)}

        best_sec = max(sec_enrichments.items(), key=lambda x: x[1]["enrichment"])

        # Compute enrichment across Diagram Object Categories
        obj_enrichments = {}
        for l_obj, obj_tot in label_obj_total_rad_tokens.items():
            c_obj = rad_label_obj_counts[rad][l_obj]
            if c_obj > 0:
                p_obj = c_obj / max(obj_tot, 1)
                enr = p_obj / max(p_global, 1e-9)
                obj_enrichments[l_obj] = {"count": c_obj, "enrichment": round(enr, 2)}

        best_obj = max(obj_enrichments.items(), key=lambda x: x[1]["enrichment"]) if obj_enrichments else ("None", {"count": 0, "enrichment": 0.0})

        # Compute enrichment across Zodiac Elemental Trigons
        trig_enrichments = {}
        for trig_b, trig_tot in trigon_total_rad_tokens.items():
            c_tr = rad_trigon_counts[rad][trig_b]
            if c_tr > 0:
                p_tr = c_tr / max(trig_tot, 1)
                enr = p_tr / max(p_global, 1e-9)
                trig_enrichments[trig_b] = {"count": c_tr, "enrichment": round(enr, 2)}

        # Syntactic / Morphological Role Classification
        q_rate = rad_q_tokens[rad] / tot
        o_rate = rad_o_tokens[rad] / tot
        y_rate = rad_y_tokens[rad] / tot
        lbl_rate = lbl / tot
        stand_rate = rad_standalone_tokens[rad] / tot
        s1_rate = rad_slot1_tokens[rad] / max(rad_slot1_tokens[rad] + rad_slot2_tokens[rad], 1)

        top_suffs = [
            {"suffix": s, "count": c, "rate": round(c / tot, 3)}
            for s, c in rad_suffix_counts[rad].most_common(3)
        ]
        dom_suff = top_suffs[0]["suffix"] if top_suffs else "0"
        edy_rate = (rad_suffix_counts[rad]["edy"] + rad_suffix_counts[rad]["eedy"] + rad_suffix_counts[rad]["dy"]) / tot

        # Infer functional / semantic archetype from quantitative profile
        if q_rate >= 0.25 and edy_rate >= 0.25:
            functional_class = "Verbal_Process_Root (High q- & -edy/-dy)"
        elif edy_rate >= 0.35:
            functional_class = "State_Action_Verb_Root (High -edy/-dy)"
        elif lbl_rate >= 0.045 and o_rate >= 0.30:
            functional_class = f"Concrete_Diagram_Noun_Radical ({best_obj[0]})"
        elif s1_rate >= 0.68 and stand_rate < 0.60:
            functional_class = "Compound_Onset_Classifier_Radical (Slot 1)"
        elif s1_rate <= 0.35 and stand_rate < 0.60:
            functional_class = "Compound_Coda_Specifier_Radical (Slot 2)"
        elif o_rate >= 0.28:
            functional_class = "Nominal_Ingredient_Container_Radical (High o-)"
        else:
            functional_class = "General_Core_Radical"

        lexicon_entries.append({
            "rank": rank_idx,
            "radical": rad,
            "total_tokens": tot,
            "prose_tokens": rad_prose_tokens[rad],
            "label_tokens": lbl,
            "label_enrichment_vs_global": round(p_label_global / max(p_global, 1e-9), 2),
            "standalone_rate": round(stand_rate, 3),
            "compound_slot1_onset_share": round(s1_rate, 3),
            "q_proclitic_rate": round(q_rate, 3),
            "o_nominal_rate": round(o_rate, 3),
            "y_initial_rate": round(y_rate, 3),
            "edy_dy_verbal_rate": round(edy_rate, 3),
            "top_3_suffixes": top_suffs,
            "peak_section": {"section": best_sec[0], **best_sec[1]},
            "peak_diagram_object": {"object_type": best_obj[0], **best_obj[1]},
            "diagram_object_breakdown": obj_enrichments,
            "zodiac_trigon_breakdown": trig_enrichments,
            "inferred_functional_class": functional_class,
        })

    # Group radicals by Diagram Object Specialization (which radicals most strongly enrich in each Diagram Object category?)
    object_specialists = {}
    for l_obj in label_obj_total_rad_tokens:
        specs = []
        for entry in lexicon_entries:
            info = entry["diagram_object_breakdown"].get(l_obj)
            if info and info["count"] >= 3 and info["enrichment"] >= 1.5:
                specs.append({
                    "radical": entry["radical"],
                    "label_count": info["count"],
                    "enrichment": info["enrichment"],
                    "total_tokens": entry["total_tokens"],
                    "o_rate": entry["o_nominal_rate"],
                    "q_rate": entry["q_proclitic_rate"],
                })
        specs.sort(key=lambda x: (-x["enrichment"], -x["label_count"]))
        object_specialists[l_obj] = specs[:12]

    output = {
        "summary": {
            "total_radical_token_instances": total_rad_instances,
            "total_label_radical_instances": total_label_rad_instances,
            "num_radicals_in_lexicon_table": len(lexicon_entries),
            "section_totals": dict(section_total_rad_tokens),
            "diagram_object_totals": dict(label_obj_total_rad_tokens),
            "zodiac_trigon_totals": dict(trigon_total_rad_tokens),
        },
        "diagram_object_specialist_radicals": object_specialists,
        "empirical_radical_lexicon_table": lexicon_entries,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved {OUT_PATH} with {len(lexicon_entries)} lexicon entries.")


if __name__ == "__main__":
    main()
