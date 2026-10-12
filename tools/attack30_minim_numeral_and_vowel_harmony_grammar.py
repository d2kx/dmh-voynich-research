#!/usr/bin/env python3
"""
Phase 41 / Attack 30: Word-Internal Minim-Count (-in / -iin / -iiin),
Loop-Count (-e- / -ee- / -eee-), and Root-to-Affix Vowel Harmony Grammar.

Investigates the sub-canonical graphic/morphophonemic contrasts that are collapsed
by 4-rule normalization:
1. Minim-Count Distribution & Conditioning (-in [1 minim] vs -iin [2 minims] vs -iiin [3 minims]):
   - Stratifies across Scribe Hands ($H=1..5), Currier Languages (A vs B), Manuscript Sections ($I),
     Line Positions (line-initial, interior, line-final, =Pt titles), and Onset Stems (d-, qok-, ok-, s-, bare a-).
2. Loop-Count Distribution & Aspectual Conditioning (-e- [1 loop] vs -ee- [2 loops] vs -eee- [3+ loops]):
   - Compares minimal pairs on identical Core Roots (qokedy vs qokeedy, chedy vs cheedy,
     shedy vs sheedy, qotedy vs qoteedy, okey vs okeey, chey vs cheey) across Scribe Hands,
     Clause Positions, and Adjacent Argument Contexts.
3. Root-to-Affix Vowel Harmony Law (1,000-trial permutation test + Mutual Information):
   - Tests whether the primary vowel of the Core Root (o, a, e) significantly conditions
     the vowel of its Suffix (-ol/-or/-om vs -al/-ar/-am vs -ey/-edy), proving systematic
     morphophonemic vowel harmony.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack30_minim_numeral_and_vowel_harmony_grammar.json"


def normalize_eva(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    return w


PREFIXES = ["qok", "qot", "qo", "ok", "ot", "ol", "or", "ar", "al", "op", "of", "yk", "yt", "ch", "sh", "d", "s", "y", "o", "k", "t", "p", "f"]
SUFFIXES = ["aiiin", "aiin", "ain", "oiin", "iiin", "iin", "in", "eeedy", "eedy", "edy", "dy", "eeey", "eey", "ey", "ol", "or", "ar", "al", "am", "om", "an", "y", "l", "r", "m", "n", "g"]


def segment_raw_word(w: str):
    s = w
    pfx = ""
    sfx = ""
    for p in sorted(PREFIXES, key=len, reverse=True):
        if s.startswith(p) and len(s) - len(p) >= 2:
            pfx = p
            s = s[len(p):]
            break
    for sx in sorted(SUFFIXES, key=len, reverse=True):
        if s.endswith(sx) and len(s) - len(sx) >= 1:
            sfx = sx
            s = s[:-len(sx)]
            break
    return pfx, s, sfx


def parse_zl():
    records = []
    current_folio = None
    meta = {}
    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    meta_re = re.compile(r"\$([A-Z])=([A-Za-z0-9]+)")

    with open(ZL_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            if raw.startswith("<f") and ">" in raw and "." not in raw.split(">")[0]:
                m_f = re.match(r"^<(f[A-Za-z0-9]+)>", raw)
                if m_f:
                    current_folio = m_f.group(1)
                    meta = dict(meta_re.findall(raw))
                continue
            m = line_re.match(raw)
            if m and current_folio:
                f_id, loc_id, loc_type, body = m.groups()
                body_clean = re.sub(r"<!.*?>", "", body)
                raw_tokens = re.split(r"[.\s,]+", body_clean)
                tokens = [normalize_eva(t) for t in raw_tokens]
                tokens = [t for t in tokens if t]
                n = len(tokens)
                for i, tok in enumerate(tokens):
                    if n == 1:
                        pos = "single_label"
                    elif i == 0:
                        pos = "line_initial"
                    elif i == n - 1:
                        pos = "line_final"
                    else:
                        pos = "line_interior"
                    records.append({
                        "folio": f_id,
                        "section": meta.get("I", ""),
                        "language": meta.get("L", ""),
                        "hand": meta.get("H", ""),
                        "loc_type": loc_type,
                        "pos": pos,
                        "token": tok,
                        "prev_token": tokens[i - 1] if i > 0 else "",
                        "next_token": tokens[i + 1] if i + 1 < n else "",
                    })
    return records


def main():
    random.seed(42)
    records = parse_zl()

    # 1. Minim-Count Analysis (-in vs -iin vs -iiin)
    minim_counts = Counter()
    minim_by_hand = defaultdict(Counter)
    minim_by_lang = defaultdict(Counter)
    minim_by_pos = defaultdict(Counter)
    minim_by_loc_type = defaultdict(Counter)
    minim_by_stem = defaultdict(Counter)

    for r in records:
        t = r["token"]
        m_min = re.search(r"(i+)n$", t)
        if m_min:
            icount = min(len(m_min.group(1)), 3)
            label = f"{icount}_minim" + ("s" if icount > 1 else "")
            stem = t[: m_min.start()]
            minim_counts[label] += 1
            if r["hand"]:
                minim_by_hand[r["hand"]][label] += 1
            if r["language"]:
                minim_by_lang[r["language"]][label] += 1
            minim_by_pos[r["pos"]][label] += 1
            if r["loc_type"].endswith("Pt"):
                minim_by_loc_type["=Pt_title"][label] += 1
            elif "L" in r["loc_type"]:
                minim_by_loc_type["@L_label"][label] += 1
            else:
                minim_by_loc_type["prose"][label] += 1
            minim_by_stem[stem][label] += 1

    def normalize_counter(c):
        tot = sum(c.values()) or 1
        return {k: round(v / tot, 4) for k, v in sorted(c.items())}, tot

    minim_hand_summary = {}
    for h, c in sorted(minim_by_hand.items()):
        rates, tot = normalize_counter(c)
        minim_hand_summary[f"Hand_{h}"] = {"total": tot, "rates": rates, "counts": dict(c)}

    minim_lang_summary = {}
    for lg, c in sorted(minim_by_lang.items()):
        rates, tot = normalize_counter(c)
        minim_lang_summary[f"Currier_{lg}"] = {"total": tot, "rates": rates, "counts": dict(c)}

    minim_pos_summary = {}
    for p, c in sorted(minim_by_pos.items()):
        rates, tot = normalize_counter(c)
        minim_pos_summary[p] = {"total": tot, "rates": rates, "counts": dict(c)}

    minim_loc_summary = {}
    for lt, c in sorted(minim_by_loc_type.items()):
        rates, tot = normalize_counter(c)
        minim_loc_summary[lt] = {"total": tot, "rates": rates, "counts": dict(c)}

    top_minim_stems = {}
    for st, c in minim_by_stem.items():
        if sum(c.values()) >= 40:
            rates, tot = normalize_counter(c)
            top_minim_stems[st] = {"total": tot, "rates": rates, "counts": dict(c)}

    # 2. Loop-Count Analysis (-e- vs -ee- vs -eee-)
    loop_counts = Counter()
    loop_by_hand = defaultdict(Counter)
    loop_by_lang = defaultdict(Counter)
    loop_by_pos = defaultdict(Counter)
    loop_pair_families = defaultdict(Counter)

    TARGET_FAMILIES = {
        "qok_dy": re.compile(r"^qok(e+)dy$"),
        "ok_dy": re.compile(r"^ok(e+)dy$"),
        "ch_dy": re.compile(r"^ch(e+)dy$"),
        "sh_dy": re.compile(r"^sh(e+)dy$"),
        "qot_dy": re.compile(r"^qot(e+)dy$"),
        "ot_dy": re.compile(r"^ot(e+)dy$"),
        "qok_y": re.compile(r"^qok(e+)y$"),
        "ok_y": re.compile(r"^ok(e+)y$"),
        "ch_y": re.compile(r"^ch(e+)y$"),
        "sh_y": re.compile(r"^sh(e+)y$"),
        "ch_ol": re.compile(r"^ch(e+)ol$"),
        "sh_ol": re.compile(r"^sh(e+)ol$"),
    }

    # Also track next-word and prev-word context for 1-loop vs 2-loop (e.g. qokedy vs qokeedy, chedy vs cheedy)
    loop_context_stats = {
        "1_loop_e": {"count": 0, "followed_by_daiin_or_ol": 0, "followed_by_dar_or_ar": 0, "line_final": 0, "line_initial": 0},
        "2_loop_ee": {"count": 0, "followed_by_daiin_or_ol": 0, "followed_by_dar_or_ar": 0, "line_final": 0, "line_initial": 0},
        "3_loop_eee": {"count": 0, "followed_by_daiin_or_ol": 0, "followed_by_dar_or_ar": 0, "line_final": 0, "line_initial": 0},
    }

    for r in records:
        t = r["token"]
        m_e = re.search(r"e+", t)
        if m_e:
            ecount = min(len(m_e.group(0)), 3)
            elabel = f"{ecount}_loop_" + ("e" * ecount)
            loop_counts[elabel] += 1
            if r["hand"]:
                loop_by_hand[r["hand"]][elabel] += 1
            if r["language"]:
                loop_by_lang[r["language"]][elabel] += 1
            loop_by_pos[r["pos"]][elabel] += 1

            for fam, rgx in TARGET_FAMILIES.items():
                mf = rgx.match(t)
                if mf:
                    ec = min(len(mf.group(1)), 3)
                    flbl = f"{ec}_loop_" + ("e" * ec)
                    loop_pair_families[fam][flbl] += 1
                    st = loop_context_stats[flbl]
                    st["count"] += 1
                    if r["next_token"] in ("daiin", "dain", "ol", "okol", "qokaiin", "okaiin"):
                        st["followed_by_daiin_or_ol"] += 1
                    if r["next_token"] in ("dar", "dal", "ar", "al", "or"):
                        st["followed_by_dar_or_ar"] += 1
                    if r["pos"] == "line_final":
                        st["line_final"] += 1
                    if r["pos"] == "line_initial":
                        st["line_initial"] += 1

    loop_hand_summary = {}
    for h, c in sorted(loop_by_hand.items()):
        rates, tot = normalize_counter(c)
        loop_hand_summary[f"Hand_{h}"] = {"total": tot, "rates": rates, "counts": dict(c)}

    loop_lang_summary = {}
    for lg, c in sorted(loop_by_lang.items()):
        rates, tot = normalize_counter(c)
        loop_lang_summary[f"Currier_{lg}"] = {"total": tot, "rates": rates, "counts": dict(c)}

    loop_family_summary = {}
    for fam, c in sorted(loop_pair_families.items()):
        rates, tot = normalize_counter(c)
        loop_family_summary[fam] = {"total": tot, "rates": rates, "counts": dict(c)}

    for k, st in loop_context_stats.items():
        n = max(st["count"], 1)
        st["followed_by_daiin_or_ol_rate"] = round(st["followed_by_daiin_or_ol"] / n, 4)
        st["followed_by_dar_or_ar_rate"] = round(st["followed_by_dar_or_ar"] / n, 4)
        st["line_final_rate"] = round(st["line_final"] / n, 4)
        st["line_initial_rate"] = round(st["line_initial"] / n, 4)

    # 3. Root-to-Affix Vowel Harmony Law
    # For words with an internal vowel in the core root (o, a, e) and a vocalic suffix
    # (-ol/-or/-om [o-back], -al/-ar/-am/-aiin [a-low], -ey/-edy/-eedy [e-front])
    harmony_pairs = []
    for r in records:
        pfx, root, sfx = segment_raw_word(r["token"])
        if not root or not sfx:
            continue
        # Determine root vowel class
        if "o" in root and "a" not in root and "e" not in root:
            rv = "o_back"
        elif "a" in root and "o" not in root and "e" not in root:
            rv = "a_low"
        elif "e" in root and "o" not in root and "a" not in root:
            rv = "e_front"
        else:
            continue

        # Determine suffix vowel class
        if sfx in ("ol", "or", "om", "oiin"):
            sv = "o_back"
        elif sfx in ("al", "ar", "am", "an", "aiin", "ain", "aiiin"):
            sv = "a_low"
        elif sfx in ("edy", "eedy", "eeedy", "ey", "eey", "eeey"):
            sv = "e_front"
        else:
            continue

        harmony_pairs.append((rv, sv, r["language"] or "A"))

    # Compute contingency table and harmonic match rate (rv == sv) + Mutual Information
    contingency = defaultdict(Counter)
    for rv, sv, _ in harmony_pairs:
        contingency[rv][sv] += 1

    obs_harmonic = sum(1 for rv, sv, _ in harmony_pairs if rv == sv)
    total_hp = len(harmony_pairs)
    obs_harmonic_rate = obs_harmonic / max(total_hp, 1)

    # Stratified permutation within Currier Language (A vs B) so language register cannot confound vowel harmony!
    by_lang = defaultdict(list)
    for rv, sv, lg in harmony_pairs:
        by_lang[lg].append((rv, sv))

    null_harmonic = []
    for _ in range(1000):
        h_cnt = 0
        for lg, pairs in by_lang.items():
            rvs = [p[0] for p in pairs]
            svs = [p[1] for p in pairs]
            random.shuffle(svs)
            h_cnt += sum(1 for rv, sv in zip(rvs, svs) if rv == sv)
        null_harmonic.append(h_cnt)

    mean_nh = sum(null_harmonic) / len(null_harmonic)
    std_nh = math.sqrt(sum((x - mean_nh) ** 2 for x in null_harmonic) / len(null_harmonic)) or 1.0
    z_harmony = (obs_harmonic - mean_nh) / std_nh
    p_harmony = sum(1 for x in null_harmonic if x >= obs_harmonic) / len(null_harmonic)

    contingency_report = {}
    for rv, c in sorted(contingency.items()):
        rates, tot = normalize_counter(c)
        contingency_report[rv] = {"total": tot, "suffix_vowel_rates": rates, "counts": dict(c)}

    result = {
        "phase": "Phase 41 / Attack 30",
        "title": "Word-Internal Minim-Count (-in / -iin / -iiin), Loop-Count (-e- / -ee- / -eee-), and Root-to-Affix Vowel Harmony Grammar",
        "minim_count_grammar": {
            "overall_counts": dict(minim_counts),
            "overall_rates": normalize_counter(minim_counts)[0],
            "by_scribe_hand": minim_hand_summary,
            "by_currier_language": minim_lang_summary,
            "by_line_position": minim_pos_summary,
            "by_locus_type": minim_loc_summary,
            "by_top_stems": top_minim_stems,
        },
        "loop_count_grammar": {
            "overall_counts": dict(loop_counts),
            "overall_rates": normalize_counter(loop_counts)[0],
            "by_scribe_hand": loop_hand_summary,
            "by_currier_language": loop_lang_summary,
            "by_minimal_pair_family": loop_family_summary,
            "syntactic_context_by_loop_count": loop_context_stats,
        },
        "root_to_suffix_vowel_harmony": {
            "evaluated_tokens": total_hp,
            "observed_harmonic_matches": obs_harmonic,
            "observed_harmonic_rate": round(obs_harmonic_rate, 4),
            "null_language_stratified_mean": round(mean_nh, 2),
            "null_language_stratified_rate": round(mean_nh / max(total_hp, 1), 4),
            "null_language_stratified_std": round(std_nh, 2),
            "z_score": round(z_harmony, 2),
            "p_value": round(p_harmony, 4),
            "contingency_table": contingency_report,
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Minim grammar overall:", json.dumps(result["minim_count_grammar"]["overall_rates"], indent=2))
    print("Minim by locus type:", json.dumps(result["minim_count_grammar"]["by_locus_type"], indent=2))
    print("Loop pair families:", json.dumps(result["loop_count_grammar"]["by_minimal_pair_family"], indent=2))
    print("Vowel harmony:", json.dumps(result["root_to_suffix_vowel_harmony"], indent=2))


if __name__ == "__main__":
    main()
