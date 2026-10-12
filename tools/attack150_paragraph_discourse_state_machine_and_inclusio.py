#!/usr/bin/env python3
"""
Attack 150 (Phase 161 / Discovery 167):
The 3-Act Paragraph Discourse State Machine, Contiguous Multi-Line Stem Execution
Chains (L_t -> L_{t+1} -> L_{t+2}), and Frame-Ring Closure (Inclusio: Line 1 <-> Line m).

Tests:
1. Across all multi-line paragraphs with >= 3 lines in ZL3b-n.txt:
   - Maps every token into the 8-Case/Voice Inflectional Paradigm across the
     3-Act Paragraph State Machine:
     * Act I   (Line 1: Opening Header / Botanical-Recipe Setup)
     * Act II  (Lines 2..m-1: Chained Interior Processing Body)
     * Act III (Line m: Final Dosing & Terminal Closure)
2. Contiguous Multi-Line Stem Execution Chains (runs of k >= 3 consecutive lines
   L_t, L_{t+1}, ..., L_{t+k-1} inside a paragraph where the EXACT SAME canonical
   stem S recurs on every single line of the run):
   - Tested against 1,000 Within-(Section $I, Language $L) Line-Shuffle Permutations
     and 1,000 Strict Within-Paragraph Line-Order Shuffles (inside paragraphs >= 4 lines).
3. Paragraph Frame-Ring Closure (Inclusio: Line 1 <-> Line m in paragraphs >= 3 lines):
   - Measures the rate at which a canonical stem S introduced in Line 1 recurs in
     the final Line m of the same paragraph (tested vs. 1,000 Within-Section Line Shuffles).
   - Evaluates the Directional Morphological Transformation of the EXACT SAME STEM S
     from Line 1 (w_first) to Line m (w_last) across all Inclusio pairs, tested via
     discordant sign-flip z-scores.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
FOLIO_INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack150_paragraph_discourse_state_machine_and_inclusio.json"

PREFIX_RE = re.compile(r"^(qol|qo|ch|sh|da|ct|ck|cp|cf|op|ot|ok|of|ol|or|al|ar|yk|yt|yp|yf|d|s|y|l|r|q|o)")
SUFFIX_RE = re.compile(r"(aiin|oiin|eiin|iin|ain|edy|ody|eey|ey|dy|am|om|im|in|al|ol|ar|or|el|y|r|l|m|n|s|g)$")

CASE_SLOTS = [
    "C1_CIT_BARE",
    "C2_NOM_O",
    "C3_DEIC_DS",
    "C4_ACT_QO",
    "C5_PROC_EDY",
    "C6_APPL_L",
    "C7_LIQ_CONT",
    "C8_QUANT_TERM",
]


def normalize_token(tok: str) -> str:
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", tok)
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"<[^>]*>", "", t)
    t = t.replace("?", "").replace("!", "").replace("*", "").replace("%", "").replace("$", "")
    t = t.replace(",", "").replace("'", "").strip().lower()
    t = re.sub(r"c([tkpf])h", r"c\1h", t)
    t = re.sub(r"i{2,}", "ii", t)
    t = re.sub(r"e{2,}", "ee", t)
    return t


def extract_prefix_stem_suffix(word: str) -> Tuple[str, str, str]:
    w = word
    pref = ""
    suff = ""
    if len(w) >= 4:
        m = PREFIX_RE.match(w)
        if m and len(w) - len(m.group(1)) >= 2:
            pref = m.group(1)
            w = w[len(pref):]
    if len(w) >= 3:
        m2 = SUFFIX_RE.search(w)
        if m2 and len(w) - len(m2.group(1)) >= 2:
            suff = m2.group(1)
            w = w[: -len(suff)]
    return pref, w, suff


def assign_case_slot(word: str, pref: str, suff: str) -> str:
    if pref in {"l", "ol", "qol"} or word.startswith(("qol", "ol")):
        return "C6_APPL_L"
    if pref == "qo" or word.startswith("qo"):
        return "C4_ACT_QO"
    if suff in {"aiin", "oiin", "eiin", "iin", "ain", "in", "n", "am", "om", "im", "m"}:
        return "C8_QUANT_TERM"
    if suff in {"edy", "ody", "eey", "ey", "dy"} or word.endswith("edy"):
        return "C5_PROC_EDY"
    if pref in {"d", "s", "da"} or word.startswith(("da", "d", "s")):
        return "C3_DEIC_DS"
    if suff in {"ol", "or", "al", "ar", "el", "l", "r"} or pref in {"or", "al", "ar", "r"}:
        return "C7_LIQ_CONT"
    if pref in {"o", "y", "ot", "ok", "op", "of", "yk", "yt", "yp", "yf"} or suff == "y":
        return "C2_NOM_O"
    return "C1_CIT_BARE"


def has_top_gallows(word: str) -> bool:
    return any(g in word[:3] for g in ("p", "f", "cp", "cf", "op", "of"))


def parse_paragraphs(zl_path: Path, folio_meta: Dict[str, dict]) -> List[dict]:
    text = zl_path.read_text(encoding="utf-8", errors="ignore")
    loc_re = re.compile(r"^<([^>]+)>\s+(.*)$")

    paragraphs = []
    cur_para = None
    cur_folio = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = loc_re.match(line)
        if not m:
            continue
        loc, body = m.group(1), m.group(2)
        if ";" in loc:
            continue
        parts = loc.split(",")
        f_line = parts[0]
        locus_tag = parts[1] if len(parts) > 1 else "@P0"
        if not (locus_tag.startswith("@P") or locus_tag.startswith("+P") or locus_tag.startswith("*P")):
            continue

        folio = f_line.split(".")[0]
        fmeta = folio_meta.get(folio, {})
        sec = fmeta.get("section_code", fmeta.get("section", "H"))
        lang = fmeta.get("currier_language", "A")
        hand = str(fmeta.get("hand", "1"))

        has_para_start = "<%>" in body or locus_tag.startswith("@P") or locus_tag.startswith("*P")
        has_para_end = "<$>" in body

        clean_body = re.sub(r"<[^>]*>", " ", body)
        raw_toks = [t for t in re.split(r"[.\s]+", clean_body) if t]
        toks = []
        for rt in raw_toks:
            nt = normalize_token(rt)
            if len(nt) >= 2:
                pref, stem, suff = extract_prefix_stem_suffix(nt)
                if len(stem) >= 2:
                    cslot = assign_case_slot(nt, pref, suff)
                    toks.append({
                        "word": nt,
                        "pref": pref,
                        "stem": stem,
                        "suff": suff,
                        "case": cslot,
                        "top_pf": has_top_gallows(nt),
                    })
        if len(toks) < 2:
            continue

        if cur_para is None or folio != cur_folio or has_para_start:
            if cur_para and len(cur_para["lines"]) >= 1:
                paragraphs.append(cur_para)
            cur_para = {
                "folio": folio,
                "section": sec,
                "lang": lang,
                "hand": hand,
                "para_index": len([p for p in paragraphs if p["folio"] == folio]) + 1,
                "lines": [],
            }
            cur_folio = folio

        cur_para["lines"].append({
            "loc": f_line,
            "tokens": toks,
            "stem_set": {t["stem"] for t in toks},
        })

        if has_para_end:
            if len(cur_para["lines"]) >= 1:
                paragraphs.append(cur_para)
            cur_para = None

    if cur_para and len(cur_para["lines"]) >= 1:
        paragraphs.append(cur_para)

    return paragraphs


def count_3line_triplets(stem_sets: List[Set[str]]) -> int:
    """Counts (t, stem) where stem is in L_t & L_{t+1} & L_{t+2}."""
    cnt = 0
    for i in range(len(stem_sets) - 2):
        cnt += len(stem_sets[i] & stem_sets[i + 1] & stem_sets[i + 2])
    return cnt


def main() -> None:
    index_raw = json.loads(FOLIO_INDEX_PATH.read_text(encoding="utf-8"))
    folio_meta = index_raw.get("folios", index_raw)

    paragraphs = parse_paragraphs(ZL_PATH, folio_meta)
    paras_ge3 = [p for p in paragraphs if len(p["lines"]) >= 3]
    paras_ge4 = [p for p in paragraphs if len(p["lines"]) >= 4]

    # 1. The 3-Act Paragraph State Machine across all paragraphs with >= 3 lines
    act_case_counts = {
        "ACT1_LINE1_HEADER": Counter(),
        "ACT2_INTERIOR_BODY": Counter(),
        "ACT3_FINAL_CLOSURE": Counter(),
    }
    act_top_pf_counts = Counter()
    act_totals = Counter()

    for p in paras_ge3:
        lns = p["lines"]
        m = len(lns)
        for idx, ln in enumerate(lns):
            if idx == 0:
                act = "ACT1_LINE1_HEADER"
            elif idx == m - 1:
                act = "ACT3_FINAL_CLOSURE"
            else:
                act = "ACT2_INTERIOR_BODY"
            for t in ln["tokens"]:
                act_case_counts[act][t["case"]] += 1
                act_totals[act] += 1
                if t["top_pf"]:
                    act_top_pf_counts[act] += 1

    three_act_profiles = {}
    for act in ["ACT1_LINE1_HEADER", "ACT2_INTERIOR_BODY", "ACT3_FINAL_CLOSURE"]:
        tot = act_totals[act]
        cc = act_case_counts[act]
        three_act_profiles[act] = {
            "total_tokens": tot,
            "top_gallows_pf_pct": round(100.0 * act_top_pf_counts[act] / max(tot, 1), 2),
            "active_process_voice_pct": round(
                100.0 * (cc["C4_ACT_QO"] + cc["C5_PROC_EDY"] + cc["C6_APPL_L"]) / max(tot, 1), 2
            ),
            "case_pct": {cs: round(100.0 * cc[cs] / max(tot, 1), 2) for cs in CASE_SLOTS},
        }

    # 2. Contiguous 3-Line Stem Execution Chains (L_t -> L_{t+1} -> L_{t+2}) & Max Run Lengths
    obs_3line_triplets = 0
    paras_with_3line_chain = 0
    max_chain_examples = []

    for p in paras_ge3:
        ssets = [ln["stem_set"] for ln in p["lines"]]
        c3 = count_3line_triplets(ssets)
        obs_3line_triplets += c3
        if c3 > 0:
            paras_with_3line_chain += 1

        # Find longest contiguous run of a single stem in this paragraph
        all_p_stems = set().union(*ssets)
        for s in all_p_stems:
            cur_run = 0
            best_run = 0
            best_start = 0
            cur_start = 0
            for idx, ss in enumerate(ssets):
                if s in ss:
                    if cur_run == 0:
                        cur_start = idx
                    cur_run += 1
                    if cur_run > best_run:
                        best_run = cur_run
                        best_start = cur_start
                else:
                    cur_run = 0
            if best_run >= 4:
                chain_forms = []
                for idx in range(best_start, best_start + best_run):
                    ln = p["lines"][idx]
                    forms = [t["word"] for t in ln["tokens"] if t["stem"] == s]
                    chain_forms.append(f"{ln['loc']}:{'/'.join(forms)}")
                max_chain_examples.append({
                    "folio": p["folio"],
                    "section": p["section"],
                    "lang": p["lang"],
                    "stem": s,
                    "contiguous_lines": best_run,
                    "para_total_lines": len(ssets),
                    "line_by_line_forms": chain_forms,
                })

    max_chain_examples.sort(key=lambda x: (-x["contiguous_lines"], -len(x["stem"])))

    # Permutation Test for 3-Line Stem Triplets & Position-Stratified Inclusio (Line 1 <-> Line m):
    bucket_ssets = defaultdict(list)
    bucket_shapes = defaultdict(list)
    bucket_first_lines = defaultdict(list)
    bucket_last_lines = defaultdict(list)
    for p in paras_ge3:
        key = (p["section"], p["lang"])
        bucket_shapes[key].append(len(p["lines"]))
        bucket_first_lines[key].append(p["lines"][0]["stem_set"])
        bucket_last_lines[key].append(p["lines"][-1]["stem_set"])
        for ln in p["lines"]:
            bucket_ssets[key].append(ln["stem_set"])

    rng = random.Random(150)
    null_sec_3line = []
    null_sec_inclusio_links = []
    null_sec_inclusio_paras = []

    for _ in range(1000):
        sim_3l = 0
        sim_inc_links = 0
        sim_inc_paras = 0
        for key, shapes in bucket_shapes.items():
            pool = list(bucket_ssets[key])
            rng.shuffle(pool)
            idx = 0
            for sz in shapes:
                sub = pool[idx : idx + sz]
                sim_3l += count_3line_triplets(sub)
                idx += sz

            # Position-stratified shuffle: pair Line 1 of paragraph i with Line m of random paragraph j in same (Section, Lang)
            f_pool = list(bucket_first_lines[key])
            l_pool = list(bucket_last_lines[key])
            rng.shuffle(l_pool)
            for s1, sm in zip(f_pool, l_pool):
                inc = len(s1 & sm)
                sim_inc_links += inc
                if inc > 0:
                    sim_inc_paras += 1

        null_sec_3line.append(sim_3l)
        null_sec_inclusio_links.append(sim_inc_links)
        null_sec_inclusio_paras.append(sim_inc_paras)

    def stats_z(obs, arr):
        mu = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - mu) ** 2 for x in arr) / len(arr))
        z = (obs - mu) / (sd if sd > 0 else 1.0)
        return {
            "observed": obs,
            "null_mean": round(mu, 2),
            "null_sd": round(sd, 2),
            "lift_ratio": round(obs / max(mu, 1e-6), 3),
            "z_score": round(z, 2),
        }

    # (B) Strict Within-Paragraph Line-Order Shuffle inside paragraphs >= 4 lines (1,000 trials)
    obs_ge4_3line = sum(count_3line_triplets([ln["stem_set"] for ln in p["lines"]]) for p in paras_ge4)
    null_wp_3line = []
    for _ in range(1000):
        sim = 0
        for p in paras_ge4:
            sub = [ln["stem_set"] for ln in p["lines"]]
            rng.shuffle(sub)
            sim += count_3line_triplets(sub)
        null_wp_3line.append(sim)

    # 3. Paragraph Frame-Ring Closure (Inclusio: Line 1 <-> Line m in paragraphs >= 3 lines)
    obs_inclusio_paras = 0
    obs_inclusio_stem_links = 0
    inclusio_token_pairs = []
    inclusio_examples = []

    for p in paras_ge3:
        l_first = p["lines"][0]
        l_last = p["lines"][-1]
        shared_stems = l_first["stem_set"] & l_last["stem_set"]
        if shared_stems:
            obs_inclusio_paras += 1
            obs_inclusio_stem_links += len(shared_stems)
        for ta in l_first["tokens"]:
            for tb in l_last["tokens"]:
                if ta["stem"] == tb["stem"]:
                    inclusio_token_pairs.append((ta, tb, p))
                    if ta["word"] != tb["word"] and len(inclusio_examples) < 30:
                        inclusio_examples.append({
                            "folio": p["folio"],
                            "section": p["section"],
                            "lang": p["lang"],
                            "para_lines": len(p["lines"]),
                            "stem": ta["stem"],
                            "line1_loc": l_first["loc"],
                            "line1_word": ta["word"],
                            "line1_case": ta["case"],
                            "linem_loc": l_last["loc"],
                            "linem_word": tb["word"],
                            "linem_case": tb["case"],
                        })

    # Directional Morphological Transformation across Inclusio Cognate Pairs (w_first != w_last)
    cognate_inclusio = [(ta, tb) for ta, tb, _ in inclusio_token_pairs if ta["word"] != tb["word"]]
    n_cog_inc = len(cognate_inclusio)

    def feat_map(t: dict) -> Dict[str, bool]:
        return {
            "top_gallows_pf": t["top_pf"],
            "C1_CIT_BARE": t["case"] == "C1_CIT_BARE",
            "C2_NOM_O": t["case"] == "C2_NOM_O",
            "C3_DEIC_DS": t["case"] == "C3_DEIC_DS",
            "C4_ACT_QO": t["case"] == "C4_ACT_QO",
            "C5_PROC_EDY": t["case"] == "C5_PROC_EDY",
            "C6_APPL_L": t["case"] == "C6_APPL_L",
            "C7_LIQ_CONT": t["case"] == "C7_LIQ_CONT",
            "C8_QUANT_TERM": t["case"] == "C8_QUANT_TERM",
            "active_or_terminal_C4_C5_C6_C8": t["case"] in {"C4_ACT_QO", "C5_PROC_EDY", "C6_APPL_L", "C8_QUANT_TERM"},
        }

    inclusio_morph_shift = {}
    fkeys = [
        "top_gallows_pf",
        "C1_CIT_BARE",
        "C2_NOM_O",
        "C3_DEIC_DS",
        "C4_ACT_QO",
        "C5_PROC_EDY",
        "C6_APPL_L",
        "C7_LIQ_CONT",
        "C8_QUANT_TERM",
        "active_or_terminal_C4_C5_C6_C8",
    ]
    f_pairs = [(feat_map(ta), feat_map(tb)) for ta, tb in cognate_inclusio]
    for fk in fkeys:
        c1 = sum(1 for fa, _ in f_pairs if fa[fk])
        cm = sum(1 for _, fb in f_pairs if fb[fk])
        n01 = sum(1 for fa, fb in f_pairs if (not fa[fk]) and fb[fk])
        n10 = sum(1 for fa, fb in f_pairs if fa[fk] and (not fb[fk]))
        disc = n01 + n10
        z_f = (n01 - n10) / math.sqrt(disc) if disc > 0 else 0.0
        inclusio_morph_shift[fk] = {
            "line1_count": c1,
            "line1_pct": round(100.0 * c1 / max(n_cog_inc, 1), 2),
            "linem_count": cm,
            "linem_pct": round(100.0 * cm / max(n_cog_inc, 1), 2),
            "delta_line1_to_linem_pct": round(100.0 * (cm - c1) / max(n_cog_inc, 1), 2),
            "discordant_gain_0to1": n01,
            "discordant_loss_1to0": n10,
            "sign_flip_z": round(z_f, 2),
        }

    out = {
        "attack": 150,
        "phase": 161,
        "discovery": 167,
        "title": "The 3-Act Paragraph Discourse State Machine, Contiguous Multi-Line Stem Execution Chains, and Frame-Ring Closure (Inclusio)",
        "overview": {
            "paragraphs_ge3_lines": len(paras_ge3),
            "paragraphs_ge4_lines": len(paras_ge4),
            "paragraphs_with_3line_contiguous_stem_chain": paras_with_3line_chain,
            "paragraphs_with_3line_chain_pct": round(100.0 * paras_with_3line_chain / max(len(paras_ge3), 1), 2),
            "contiguous_3line_stem_triplets_within_section_test": stats_z(obs_3line_triplets, null_sec_3line),
            "contiguous_3line_stem_triplets_strict_within_para_test": stats_z(obs_ge4_3line, null_wp_3line),
            "paragraphs_with_inclusio_line1_to_linem": obs_inclusio_paras,
            "paragraphs_with_inclusio_pct": round(100.0 * obs_inclusio_paras / max(len(paras_ge3), 1), 2),
            "inclusio_paragraphs_within_section_test": stats_z(obs_inclusio_paras, null_sec_inclusio_paras),
            "inclusio_shared_stems_within_section_test": stats_z(obs_inclusio_stem_links, null_sec_inclusio_links),
            "total_inclusio_token_pairs": len(inclusio_token_pairs),
            "cognate_inclusio_token_pairs_w1_ne_wm": n_cog_inc,
            "cognate_share_of_inclusio_pairs_pct": round(100.0 * n_cog_inc / max(len(inclusio_token_pairs), 1), 2),
        },
        "three_act_paragraph_state_machine": three_act_profiles,
        "inclusio_line1_to_linem_morphological_shift": inclusio_morph_shift,
        "longest_contiguous_stem_chains": max_chain_examples[:20],
        "sample_inclusio_frame_pairs": inclusio_examples[:20],
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Attack 150] Saved {OUT_JSON}")
    print("Overview:", json.dumps(out["overview"], indent=2))
    print("3-Act State Machine:", json.dumps(three_act_profiles, indent=2))
    print("Inclusio Morph Shift:", json.dumps(inclusio_morph_shift, indent=2))


if __name__ == "__main__":
    main()
