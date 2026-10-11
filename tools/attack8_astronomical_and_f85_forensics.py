#!/usr/bin/env python3
"""
Phase 19 / Attack 8: Visual & Textual Forensics of the Astronomical Wheel Keys
(f67r1-f70r2) & the Four-Seasons Cosmological Foldout (f85r1-f86v6, Reverse of
the 9-Rosettes).

1. Parses all 14 Astronomical folios (f67r1..f70r2) and all 6 panels of the
   f85-f86 Cosmological Foldout (f85r1, f85r2, f86v4, f86v3, f86v5, f86v6).
2. Runs a 5,000-trial within-diagram permutation test on all ordered Astronomical
   star/spoke label sequences (@Ls, @La, @L0) to test clockwise step-mutation
   (shared Core Root, shared 3/4-char prefix, Levenshtein edit distance).
3. Extracts all single-character / key-like sequences and circular ring formulas
   across f67r1-f70r2 and f85r2 / f86v4.
4. Maps all rare (global prose count <= 5) figure labels from the Astronomical
   wheels (f67r1-f70r2) and Four-Seasons/Four-Moons diagrams (f85r2, f86v4) into
   the rest of the manuscript, and maps rare diagram labels ingested into the
   prose of f85r1-f86v6.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack8_astronomical_and_f85_forensics.json"

ASTRO_FOLIOS = [
    "f67r1", "f67r2", "f67v1", "f67v2",
    "f68r1", "f68r2", "f68r3", "f68v1", "f68v2", "f68v3",
    "f69r", "f69v", "f70r1", "f70r2",
]

F85_86_FOLIOS = [
    "f85r1", "f85r2", "f86v4", "f86v3", "f86v5", "f86v6",
]


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[@&!?\*\(\)<>\[\]\'\"]", "", t)
    return t.strip()


def canonicalize(w: str) -> str:
    if not w:
        return ""
    s = w
    if len(s) > 2 and s[0] in ("q", "y") and s[1] in ("o", "e", "a"):
        s = s[1:]
    s = s.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    if s.endswith("m") and len(s) > 2:
        s = s[:-1] + "r"
    return s


SUFFIX_PAT = re.compile(
    r"(aiin|ain|iin|in|edy|eedy|ody|dy|eey|ey|ary|ory|ry|aly|oly|ly|am|om|al|ol|ar|or|y|r|l|s|d)$"
)


def core_root_of(w: str) -> str:
    s = canonicalize(w)
    if len(s) > 2 and s.startswith("o") and not s.startswith(("ol", "or")):
        s = s[1:]
    m = SUFFIX_PAT.search(s)
    if m and len(s) - len(m.group(1)) >= 1:
        return s[: -len(m.group(1))]
    return s


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        return levenshtein(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            ins = prev[j + 1] + 1
            dele = curr[j] + 1
            sub = prev[j] + (0 if ca == cb else 1)
            curr.append(min(ins, dele, sub))
        prev = curr
    return prev[-1]


def parse_zl_corpus(zl_path: Path):
    text = zl_path.read_text(encoding="utf-8", errors="ignore")
    folios = {}
    current_folio = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m_page = re.match(r"^<(f[\w]+)>\s*(?:<!\s*(.*?)\s*>)?", line)
        if m_page and "." not in m_page.group(1):
            current_folio = m_page.group(1)
            meta = {}
            if m_page.group(2):
                for kv in re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", m_page.group(2)):
                    meta[kv[0]] = kv[1]
            folios[current_folio] = {"meta": meta, "lines": []}
            continue

        m_loc = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m_loc or not current_folio:
            continue
        loc_header = m_loc.group(1)
        body = m_loc.group(2)
        parts = loc_header.split(",")
        loc_id = parts[0]
        unit_type = parts[1] if len(parts) > 1 else ""

        comments = re.findall(r"<!([^>]*)>", body)
        body_no_comments = re.sub(r"<!([^>]*)>", "", body)
        body_no_comments = body_no_comments.replace("<%>", "").replace("<$>", "").replace("<->", " . ")

        raw_toks = [t for t in re.split(r"[\.\s,]+", body_no_comments) if t]
        words = [clean_tok(t) for t in raw_toks]
        words = [w for w in words if w and not w.startswith("@") and not w.startswith("H=")]

        folios[current_folio]["lines"].append(
            {
                "loc": loc_id,
                "unit": unit_type,
                "comments": comments,
                "words": words,
            }
        )
    return folios


def main():
    folios = parse_zl_corpus(ZL_PATH)

    # 1. Global canonical prose occurrences and figure label catalog
    prose_occurrences_by_canon = defaultdict(list)
    labels_by_canon = defaultdict(list)

    for fol, fdata in folios.items():
        sec = fdata["meta"].get("I", "?")
        for lobj in fdata["lines"]:
            unit = lobj["unit"]
            words = lobj["words"]
            if not words:
                continue
            is_label = "@L" in unit or "&L" in unit
            if is_label:
                w = words[0]
                c = canonicalize(w)
                labels_by_canon[c].append(
                    {"folio": fol, "section": sec, "loc": lobj["loc"], "unit": unit, "word": w}
                )
            else:
                for w_i, w in enumerate(words):
                    c = canonicalize(w)
                    prose_occurrences_by_canon[c].append(
                        {"folio": fol, "section": sec, "loc": lobj["loc"], "unit": unit, "word_pos": w_i + 1, "word": w}
                    )

    # 2. Parse Astronomical Folios (f67r1-f70r2): Rings, Spokes, and Star Label Sequences
    astro_summary = []
    astro_label_sequences = {}

    for fol in ASTRO_FOLIOS:
        if fol not in folios:
            continue
        fdata = folios[fol]
        rings_and_spokes = []
        star_labels = []
        single_char_lines = []

        for lobj in fdata["lines"]:
            unit = lobj["unit"]
            words = lobj["words"]
            if not words:
                continue
            is_label = "@L" in unit or "&L" in unit
            if is_label:
                w = words[0]
                star_labels.append(
                    {
                        "loc": lobj["loc"],
                        "unit": unit,
                        "word": w,
                        "canon": canonicalize(w),
                        "root": core_root_of(w),
                        "prose_count": len(prose_occurrences_by_canon[canonicalize(w)]),
                    }
                )
            else:
                single_ratio = sum(1 for w in words if len(w) == 1) / len(words)
                if single_ratio >= 0.25 and len(words) >= 4:
                    single_char_lines.append(
                        {
                            "loc": lobj["loc"],
                            "unit": unit,
                            "num_tokens": len(words),
                            "single_char_ratio": round(single_ratio, 3),
                            "text": " . ".join(words),
                        }
                    )
                if any(tag in unit for tag in ("C", "R", "S")):
                    rings_and_spokes.append(
                        {
                            "loc": lobj["loc"],
                            "unit": unit,
                            "num_words": len(words),
                            "sample": " . ".join(words[:12]),
                        }
                    )

        if len(star_labels) >= 4:
            astro_label_sequences[fol] = star_labels

        astro_summary.append(
            {
                "folio": fol,
                "meta": fdata["meta"],
                "num_star_labels": len(star_labels),
                "num_ring_spoke_lines": len(rings_and_spokes),
                "single_char_key_lines": single_char_lines,
                "star_labels_preview": [f"{s['loc']}({s['unit']}):{s['word']}" for s in star_labels[:12]],
            }
        )

    # 3. 5,000-Trial Within-Diagram Permutation Test on Astronomical Star/Spoke Label Sequences
    def eval_adj_metrics(seqs_dict):
        total_pairs = 0
        same_root = 0
        same_pre3 = 0
        same_suf2 = 0
        total_lev = 0
        adj_root_matches = []
        for fol, seq in seqs_dict.items():
            for i in range(len(seq) - 1):
                a, b = seq[i], seq[i + 1]
                wa, wb = a["word"], b["word"]
                ra, rb = a["root"], b["root"]
                total_pairs += 1
                if ra == rb and len(ra) >= 1:
                    same_root += 1
                    adj_root_matches.append(
                        {"folio": fol, "loc_a": a["loc"], "word_a": wa, "loc_b": b["loc"], "word_b": wb, "shared_root": ra}
                    )
                if len(wa) >= 3 and len(wb) >= 3 and wa[:3] == wb[:3]:
                    same_pre3 += 1
                if len(wa) >= 2 and len(wb) >= 2 and wa[-2:] == wb[-2:]:
                    same_suf2 += 1
                total_lev += levenshtein(wa, wb)
        return {
            "total_pairs": total_pairs,
            "same_root": same_root,
            "same_pre3": same_pre3,
            "same_suf2": same_suf2,
            "mean_lev": total_lev / max(total_pairs, 1),
            "adj_root_matches": adj_root_matches,
        }

    obs_astro = eval_adj_metrics(astro_label_sequences)
    rng = random.Random(42)
    n_trials = 5000
    null_roots, null_pre3, null_suf2, null_lev = [], [], [], []
    for _ in range(n_trials):
        perm_dict = {}
        for fol, seq in astro_label_sequences.items():
            s_copy = list(seq)
            rng.shuffle(s_copy)
            perm_dict[fol] = s_copy
        m = eval_adj_metrics(perm_dict)
        null_roots.append(m["same_root"])
        null_pre3.append(m["same_pre3"])
        null_suf2.append(m["same_suf2"])
        null_lev.append(m["mean_lev"])

    def z_and_p(obs_val, arr, lower_tail=False):
        mu = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - mu) ** 2 for x in arr) / len(arr)) or 1e-9
        z = (obs_val - mu) / sd
        if lower_tail:
            p = sum(1 for x in arr if x <= obs_val) / len(arr)
        else:
            p = sum(1 for x in arr if x >= obs_val) / len(arr)
        return round(mu, 3), round(sd, 3), round(z, 3), round(p, 5)

    r_mu, r_sd, r_z, r_p = z_and_p(obs_astro["same_root"], null_roots)
    p3_mu, p3_sd, p3_z, p3_p = z_and_p(obs_astro["same_pre3"], null_pre3)
    s2_mu, s2_sd, s2_z, s2_p = z_and_p(obs_astro["same_suf2"], null_suf2)
    lv_mu, lv_sd, lv_z, lv_p = z_and_p(obs_astro["mean_lev"], null_lev, lower_tail=True)

    astro_step_mutation_test = {
        "num_folios_with_label_sequences": len(astro_label_sequences),
        "total_adjacent_label_pairs": obs_astro["total_pairs"],
        "shared_core_root": {
            "observed": obs_astro["same_root"],
            "null_mean": r_mu,
            "null_sd": r_sd,
            "z_score": r_z,
            "p_value": r_p,
        },
        "shared_3char_prefix": {
            "observed": obs_astro["same_pre3"],
            "null_mean": p3_mu,
            "null_sd": p3_sd,
            "z_score": p3_z,
            "p_value": p3_p,
        },
        "shared_2char_suffix": {
            "observed": obs_astro["same_suf2"],
            "null_mean": s2_mu,
            "null_sd": s2_sd,
            "z_score": s2_z,
            "p_value": s2_p,
        },
        "mean_levenshtein_distance": {
            "observed": round(obs_astro["mean_lev"], 4),
            "null_mean": lv_mu,
            "null_sd": lv_sd,
            "z_score": lv_z,
            "p_value": lv_p,
        },
        "adjacent_shared_root_pairs": obs_astro["adj_root_matches"],
    }

    # 4. Ultra-Rare Astronomical Label Concordances (global prose count <= 3)
    astro_rare_concordances = []
    for fol in ASTRO_FOLIOS:
        if fol not in folios:
            continue
        for lobj in folios[fol]["lines"]:
            unit = lobj["unit"]
            if "@L" not in unit and "&L" not in unit:
                continue
            if not lobj["words"]:
                continue
            w = lobj["words"][0]
            c = canonicalize(w)
            if len(c) < 3:
                continue
            p_hits = prose_occurrences_by_canon[c]
            if 1 <= len(p_hits) <= 3:
                astro_rare_concordances.append(
                    {
                        "astro_folio": fol,
                        "astro_loc": lobj["loc"],
                        "astro_unit": unit,
                        "label_word": w,
                        "canon": c,
                        "global_prose_count": len(p_hits),
                        "prose_matches": p_hits,
                    }
                )

    # 5. Analyze Four-Seasons / Four-Winds Cosmological Foldout (f85r1-f86v6)
    f85_86_summary = []
    f85_86_rare_label_concordances = []

    for fol in F85_86_FOLIOS:
        if fol not in folios:
            continue
        fdata = folios[fol]
        labels = []
        rings = []
        prose_rare_hits = []

        for lobj in fdata["lines"]:
            unit = lobj["unit"]
            words = lobj["words"]
            if not words:
                continue
            is_label = "@L" in unit or "&L" in unit
            if is_label:
                w = words[0]
                c = canonicalize(w)
                p_hits = prose_occurrences_by_canon[c]
                labels.append(
                    {
                        "loc": lobj["loc"],
                        "unit": unit,
                        "word": w,
                        "canon": c,
                        "global_prose_count": len(p_hits),
                        "prose_matches": p_hits[:5],
                    }
                )
            else:
                if "C" in unit or "R" in unit:
                    rings.append(
                        {
                            "loc": lobj["loc"],
                            "unit": unit,
                            "num_words": len(words),
                            "text": " . ".join(words),
                        }
                    )
                for w_i, w in enumerate(words):
                    c = canonicalize(w)
                    if len(c) < 3:
                        continue
                    p_cnt = len(prose_occurrences_by_canon[c])
                    if p_cnt <= 5 and c in labels_by_canon:
                        lbls = labels_by_canon[c]
                        hit_obj = {
                            "panel": fol,
                            "loc": lobj["loc"],
                            "unit": unit,
                            "word_pos": w_i + 1,
                            "word": w,
                            "canon": c,
                            "global_prose_count": p_cnt,
                            "matched_labels": lbls,
                        }
                        prose_rare_hits.append(hit_obj)
                        f85_86_rare_label_concordances.append(hit_obj)

        f85_86_summary.append(
            {
                "panel": fol,
                "meta": fdata["meta"],
                "num_lines": len(fdata["lines"]),
                "total_words": sum(len(l["words"]) for l in fdata["lines"]),
                "labels": labels,
                "circular_rings": rings,
                "rare_diagram_label_hits": prose_rare_hits,
            }
        )

    out = {
        "astronomical_step_mutation_permutation_test": astro_step_mutation_test,
        "astronomical_folios_summary": astro_summary,
        "astronomical_ultra_rare_label_concordances": astro_rare_concordances,
        "f85_f86_cosmological_foldout_summary": f85_86_summary,
        "f85_f86_rare_diagram_label_concordances": f85_86_rare_label_concordances,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("\n--- Astronomical Step-Mutation Permutation Test (5,000 trials) ---")
    print(json.dumps({k: v for k, v in astro_step_mutation_test.items() if k != "adjacent_shared_root_pairs"}, indent=2))
    print(f"Adjacent shared root pairs ({len(obs_astro['adj_root_matches'])}):")
    for m in obs_astro["adj_root_matches"]:
        print(f"  {m['folio']}: <{m['loc_a']}> {m['word_a']} -> <{m['loc_b']}> {m['word_b']} (root='{m['shared_root']}')")

    print(f"\n--- Single-Char / Key Lines in Astronomical Section ---")
    for a in astro_summary:
        for sc in a["single_char_key_lines"]:
            print(f"  {a['folio']} <{sc['loc']},{sc['unit']}> ({sc['num_tokens']} toks, {sc['single_char_ratio']*100:.1f}% 1-char): {sc['text']}")

    print(f"\n--- Ultra-Rare Astronomical Label Concordances (Prose Count <= 3): {len(astro_rare_concordances)} ---")
    for u in astro_rare_concordances[:25]:
        m_str = ", ".join(f"{p['loc']}({p['section']}):{p['word']}" for p in u["prose_matches"])
        print(f"  <{u['astro_loc']},{u['astro_unit']}> '{u['label_word']}' (cnt={u['global_prose_count']}) <-> {m_str}")

    print(f"\n--- Four-Seasons / Cosmological Foldout (f85r1-f86v6) Summary ---")
    for p in f85_86_summary:
        print(f"  Panel {p['panel']} ({p['total_words']} words, {len(p['labels'])} labels, {len(p['circular_rings'])} rings, {len(p['rare_diagram_label_hits'])} rare label hits)")
        for lbl in p["labels"]:
            m_str = ", ".join(f"{pm['loc']}({pm['section']}):{pm['word']}" for pm in lbl["prose_matches"][:3])
            print(f"    Label <{lbl['loc']},{lbl['unit']}> '{lbl['word']}' (prose_cnt={lbl['global_prose_count']}) -> {m_str}")
        for r in p["circular_rings"]:
            print(f"    Ring <{r['loc']},{r['unit']}> ({r['num_words']}w): {r['text'][:90]}...")
        for h in p["rare_diagram_label_hits"]:
            l_str = ", ".join(f"{l['loc']}({l['unit']}):{l['word']}" for l in h["matched_labels"])
            print(f"    Rare Hit <{h['loc']}> w#{h['word_pos']} '{h['word']}' (cnt={h['global_prose_count']}) <-> {l_str}")


if __name__ == "__main__":
    main()
