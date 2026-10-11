#!/usr/bin/env python3
"""
Attack 12 (Phase 23 / Discovery 29):
Radical & Syllabic Decomposition of the Core Roots:
Minimum Description Length (MDL) Morpheme Discovery, Commuting Radical Grids,
and Empirical Verification Against Paleographic Micro-Spaces (',') in ZL3b-n.txt.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack12_core_root_radical_decomposition.json"

SUFFIX_PAT = re.compile(
    r"(aiin|ain|iin|in|edy|eedy|ody|dy|eey|ey|ary|ory|ry|aly|oly|ly|am|om|al|ol|ar|or|y|r|l|s|d)$"
)


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"@\d+;", "", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t.strip()


def clean_tok_keep_comma(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"@\d+;", "", t)
    t = re.sub(r"[^a-zA-Z,]", "", t).lower()
    return t.strip(",")


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
    """
    Exact Stage-4 Core Root & Envelope extractor from Attack 7.
    Returns dict with pref, core, suff, stage2_norm, env_sig.
    """
    s0 = w
    env_parts = []
    if "p" in s0 or "f" in s0:
        env_parts.append("G:p/f->t/k")
    s1 = stage1_gallows(s0)
    s2 = stage2_vowels(s0)
    if s2 != s1:
        env_parts.append("V:ee/ii")

    s3 = s2
    pref = ""
    if len(s3) > 2 and s3[0] == "q" and s3[1] in ("o", "e", "a"):
        env_parts.append("P:q-")
        pref += "q"
        s3 = s3[1:]
    elif len(s3) > 2 and s3[0] == "y" and s3[1] in ("o", "e", "a", "t", "k", "c", "s"):
        env_parts.append("P:y-")
        pref += "y"
        s3 = s3[1:]

    if s3.endswith("m") and len(s3) > 2:
        env_parts.append("M:-m->-r")
        s3 = s3[:-1] + "r"

    s4 = s3
    if len(s4) > 2 and s4.startswith("o") and not s4.startswith(("ol", "or")):
        env_parts.append("N:o-")
        pref += "o"
        s4 = s4[1:]

    m_suf = SUFFIX_PAT.search(s4)
    if m_suf and len(s4) - len(m_suf.group(1)) >= 1:
        suf = m_suf.group(1)
        core = s4[:-len(suf)]
        env_parts.append(f"S:-{suf}")
    else:
        suf = ""
        core = s4
        env_parts.append("S:0")

    return {
        "orig": w,
        "s2": s2,
        "pref": pref,
        "core": core,
        "suff": suf,
        "env_sig": "|".join(env_parts) if env_parts else "BARE",
    }


def tokenize_eva_glyphs(s: str):
    """
    Tokenize a canonical Core Root string into atomic EVA glyph units:
    Benched gallows (cth, ckh, cph, cfh), plumed/sh-ch ligatures (ch, sh),
    diphthong (ai, oi, ei, eo), or single EVA characters.
    """
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
    comma_tokens = []
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

        for rp in re.split(r"[\.\s]+", body_no_comments.replace("<->", " ")):
            if "," in rp:
                ck = clean_tok_keep_comma(rp)
                if "," in ck and len(ck.replace(",", "")) >= 3:
                    comma_tokens.append({
                        "folio": current_folio,
                        "loc_id": loc_id,
                        "unit_type": unit_type,
                        "raw_comma": ck,
                    })

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

    return records, comma_tokens


def main():
    records, comma_tokens = parse_zl()
    print(f"Loaded {len(records)} lines and {len(comma_tokens)} intra-word comma tokens.")

    root_token_counts = Counter()
    root_prose_counts = Counter()
    root_label_counts = Counter()
    root_examples = defaultdict(list)
    total_tokens = 0
    total_prose_tokens = 0

    for r in records:
        for w in r["words"]:
            total_tokens += 1
            m = extract_core_root_and_envelope(w)
            rt = m["core"]
            root_token_counts[rt] += 1
            if r["is_label"]:
                root_label_counts[rt] += 1
            else:
                total_prose_tokens += 1
                root_prose_counts[rt] += 1
            if len(root_examples[rt]) < 5:
                root_examples[rt].append(f"{w} ({r['loc_id']})")

    unique_roots = sorted(root_token_counts.keys(), key=lambda x: (-root_token_counts[x], x))
    print(
        f"Total tokens: {total_tokens} (Prose: {total_prose_tokens}), "
        f"Unique Alpha Core Roots: {len(unique_roots)} (Prose Core Roots: {len(root_prose_counts)})"
    )

    # 2. Cumulative token coverage by Core Root rank
    cum = 0
    coverage_milestones = {}
    for idx, rt in enumerate(unique_roots, 1):
        cum += root_token_counts[rt]
        frac = cum / total_tokens
        for target in [0.50, 0.70, 0.80, 0.85, 0.90, 0.95, 0.98, 1.00]:
            key = f"{int(target*100)}%"
            if key not in coverage_milestones and frac >= target - 1e-9:
                coverage_milestones[key] = {
                    "num_roots": idx,
                    "fraction_of_types": round(idx / len(unique_roots), 4),
                    "tokens_covered": cum,
                    "fraction_of_tokens": round(frac, 4),
                }

    # 3. Build natural elementary radical inventory from standalone Core Roots + compound boundary productivity
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

    def segment_root(rt: str, force_split: bool = False):
        n = len(rt)
        if n <= 1:
            return [rt]
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

    # 4. Segment all unique Core Roots
    root_segmentations = {}
    radical_usage_types = Counter()
    radical_usage_tokens = Counter()
    slot1_radicals = Counter()
    slot2_radicals = Counter()
    slot3_radicals = Counter()
    num_segments_dist_types = Counter()
    num_segments_dist_tokens = Counter()
    bigram_transitions = Counter()

    for rt in unique_roots:
        cnt = root_token_counts[rt]
        glyphs = tokenize_eva_glyphs(rt)
        if len(glyphs) == 1:
            segs = [rt]
        else:
            segs = segment_root(rt, force_split=(len(glyphs) >= 3 and cnt <= 200))
        root_segmentations[rt] = segs
        k = len(segs)
        num_segments_dist_types[k] += 1
        num_segments_dist_tokens[k] += cnt
        for s_idx, rad in enumerate(segs):
            radical_usage_types[rad] += 1
            radical_usage_tokens[rad] += cnt
            if len(segs) >= 2:
                if s_idx == 0:
                    slot1_radicals[rad] += 1
                elif s_idx == 1:
                    slot2_radicals[rad] += 1
                else:
                    slot3_radicals[rad] += 1
        for a, b in zip(segs, segs[1:]):
            bigram_transitions[(a, b)] += 1

    # 5. Compute MDL (Minimum Description Length) & Radical Inventory Compression
    sorted_radicals_by_types = radical_usage_types.most_common()
    sorted_radicals_by_tokens = radical_usage_tokens.most_common()

    total_rad_token_instances = sum(radical_usage_tokens.values())
    total_rad_type_instances = sum(radical_usage_types.values())

    rad_coverage_curve = {}
    cum_tok = 0
    cum_typ = 0
    for r_idx, (rad, t_cnt) in enumerate(sorted_radicals_by_tokens, 1):
        cum_tok += t_cnt
        cum_typ += radical_usage_types[rad]
        frac_tok = cum_tok / total_rad_token_instances
        frac_typ = cum_typ / total_rad_type_instances
        if r_idx in (15, 25, 35, 50, 75, 100, 150) or r_idx == len(sorted_radicals_by_tokens):
            rad_coverage_curve[f"top_{r_idx}_radicals"] = {
                "num_radicals": r_idx,
                "token_radical_coverage": round(frac_tok, 4),
                "type_radical_coverage": round(frac_typ, 4),
            }

    H_unseg = -sum((c / total_tokens) * math.log2(c / total_tokens) for c in root_token_counts.values())
    H_rad = -sum((c / total_rad_token_instances) * math.log2(c / total_rad_token_instances) for c in radical_usage_tokens.values())
    mean_rads_per_token = total_rad_token_instances / total_tokens
    mean_rads_per_type = total_rad_type_instances / len(unique_roots)

    unseg_lexicon_chars = sum(len(rt) for rt in unique_roots)
    unseg_lexicon_bits = unseg_lexicon_chars * math.log2(26)
    seg_lexicon_rad_bits = sum(len(r) for r in radical_usage_types) * math.log2(26)
    seg_pointer_bits = sum(
        -cnt * math.log2(cnt / total_rad_type_instances)
        for cnt in radical_usage_types.values()
    )
    seg_total_lexicon_bits = seg_lexicon_rad_bits + seg_pointer_bits
    mdl_compression_ratio = unseg_lexicon_bits / seg_total_lexicon_bits

    print(f"Total unique elementary radicals used across all {len(unique_roots)} roots: {len(radical_usage_types)}")
    print(f"Unsegmented Lexicon Bits: {unseg_lexicon_bits:.1f} vs Segmented MDL Bits: {seg_total_lexicon_bits:.1f} ({mdl_compression_ratio:.2f}x compression)")

    # 6. EMPIRICAL GROUND-TRUTH TEST: Paleographic Micro-Spaces (',') in ZL3b-n.txt
    comma_boundary_stats = Counter()
    comma_root_internal_hits = 0
    comma_root_internal_total = 0
    comma_root_random_expected = 0.0
    verified_comma_examples = []

    for ct in comma_tokens:
        raw_c = ct["raw_comma"]
        parts = [p for p in raw_c.split(",") if p]
        if len(parts) != 2:
            continue
        left_raw, right_raw = parts
        left_s2 = stage2_vowels(left_raw)
        right_s2 = stage2_vowels(right_raw)
        joined_s2 = left_s2 + right_s2
        comma_pos = len(left_s2)

        m = extract_core_root_and_envelope(left_raw + right_raw)
        pref_len = len(m["pref"])
        root_len = len(m["core"])
        root_start = pref_len
        root_end = pref_len + root_len

        segs = segment_root(m["core"], force_split=True) if len(m["core"]) >= 2 else [m["core"]]
        internal_boundaries = set()
        acc = root_start
        for s in segs[:-1]:
            acc += len(s)
            internal_boundaries.add(acc)

        if comma_pos == root_start and pref_len > 0:
            btype = "Prefix | Root boundary"
            comma_boundary_stats[btype] += 1
        elif comma_pos == root_end and len(m["suff"]) > 0:
            btype = "Root | Suffix boundary"
            comma_boundary_stats[btype] += 1
        elif root_start < comma_pos < root_end:
            comma_root_internal_total += 1
            possible_internal_positions = max(root_len - 1, 1)
            comma_root_random_expected += len(internal_boundaries) / possible_internal_positions
            if comma_pos in internal_boundaries:
                btype = "Internal Radical | Radical boundary (R1 | R2)"
                comma_boundary_stats[btype] += 1
                comma_root_internal_hits += 1
            else:
                btype = "Unaligned internal position"
                comma_boundary_stats[btype] += 1
        else:
            btype = "Affix-internal boundary"
            comma_boundary_stats[btype] += 1

        if btype in ("Prefix | Root boundary", "Root | Suffix boundary", "Internal Radical | Radical boundary (R1 | R2)"):
            if len(verified_comma_examples) < 60:
                verified_comma_examples.append({
                    "folio_loc": f"<{ct['loc_id']},{ct['unit_type']}>",
                    "raw_comma": raw_c,
                    "joined_s2": joined_s2,
                    "morph_parse": f"[{m['pref'] or 'bare'}|{'+'.join(segs)}|-{m['suff'] or '0'}]",
                    "boundary_type": btype,
                })

    total_comma_evaluated = sum(comma_boundary_stats.values())
    aligned_comma_total = (
        comma_boundary_stats["Prefix | Root boundary"]
        + comma_boundary_stats["Root | Suffix boundary"]
        + comma_boundary_stats["Internal Radical | Radical boundary (R1 | R2)"]
    )
    print(f"Comma micro-space alignment: {aligned_comma_total}/{total_comma_evaluated} ({aligned_comma_total/max(total_comma_evaluated,1)*100:.2f}%)")
    if comma_root_internal_total > 0:
        p_hit = comma_root_internal_hits / comma_root_internal_total
        p_exp = comma_root_random_expected / comma_root_internal_total
        z_comma = (comma_root_internal_hits - comma_root_random_expected) / max(
            math.sqrt(comma_root_internal_total * p_exp * (1 - p_exp)), 1e-6
        )
        print(
            f"Root-internal comma alignment with R1|R2: {comma_root_internal_hits}/{comma_root_internal_total} "
            f"({p_hit*100:.2f}% vs {p_exp*100:.2f}% random, {p_hit/max(p_exp,1e-6):.2f}x, z={z_comma:+.2f})"
        )
    else:
        p_hit, p_exp, z_comma = 0.0, 0.0, 0.0

    # 7. Commuting Radical Grids (Slot 1 Onset Radical x Slot 2 Coda Radical)
    top_s1 = [r for r, _ in slot1_radicals.most_common(15)]
    top_s2 = [r for r, _ in slot2_radicals.most_common(15)]
    commuting_grid = []
    for r1 in top_s1:
        row = {"slot1_radical": r1, "total_types": slot1_radicals[r1], "combinations": {}}
        for r2 in top_s2:
            comp = r1 + r2
            if comp in root_token_counts:
                row["combinations"][r2] = {
                    "compound_root": comp,
                    "token_count": root_token_counts[comp],
                    "example": root_examples[comp][0] if root_examples[comp] else comp,
                }
        commuting_grid.append(row)

    # 8. Decompose Confirmed Diagram Cribs into Elementary Radicals
    key_crib_words = [
        ("otar.am / otaram", "otaram", "f70v2.22 / f107r.11", "Pisces 20° (Water)"),
        ("otar,al / otaral", "otaral", "f70v2.23 / f107r.13", "Pisces 21° (Water)"),
        ("otalar", "otalar", "f70v2.24 / f107r.16", "Pisces 22° (Water)"),
        ("airal", "airal", "f72r3.21 / f107r.15", "Cancer 19° (Water)"),
        ("ykolairol", "ykolairol", "f72r3.13 / f113r.2", "Cancer 12° (Water)"),
        ("oteeosy", "oteeosy", "f73r.13 / f113r.3", "Scorpio 12° (Water)"),
        ("opaiinam / otaiinam", "otaiinam", "f72v2.18 / f107r.16", "Virgo 17° (Earth)"),
        ("okolar", "okolar", "f70v1.11 / f107r.19", "Aries 10° (Fire)"),
        ("oly", "oly", "f71r.11 / f107r.18", "Aries 25° (Fire)"),
        ("otaldy", "otaldy", "f72v3.7 / f107r.17", "Leo 6° (Fire)"),
        ("otedar", "otedar", "f85v2.7 / f106v.14", "Rosettes / Recipe"),
        ("daraldy", "daraldy", "f85v2.19 / f84r.34", "Rosettes / Bio"),
        ("daldar", "daldar", "f85v2.15 / f43v.10", "Rosettes / Herbal"),
        ("otolaiin / otol,daiin", "otoldaiin", "f85v2.6 / f89v1.13", "Rosettes / Pharma"),
        ("yteoldy / yteeoldy", "yteoldy", "f99r.45 / f101r.3", "Apothecary Jar"),
        ("oteolair", "oteolair", "f99r.16 / f111r.12", "Pharma Root / Recipe"),
        ("opcheedey / otchedey", "otchedey", "f89v2.14 / f111r.12", "Pharma Root / Recipe"),
        ("otar . arody / par . arody", "arody", "f88v.4 / f105r.6", "2-Word Botanical Crib"),
    ]

    decomposed_cribs = []
    for label_str, target_w, loci_str, domain_str in key_crib_words:
        m = extract_core_root_and_envelope(target_w)
        rt = m["core"]
        segs = segment_root(rt, force_split=(len(tokenize_eva_glyphs(rt)) >= 2))
        decomposed_cribs.append({
            "crib": label_str,
            "target_word": target_w,
            "loci": loci_str,
            "domain": domain_str,
            "prefix": m["pref"] or "bare",
            "core_root": rt,
            "radicals": segs,
            "suffix": m["suff"] or "0",
            "formula": f"[{m['pref'] or 'bare'} | {' + '.join(segs)} | -{m['suff'] or '0'}]",
        })

    output = {
        "summary": {
            "total_tokens": total_tokens,
            "total_prose_tokens": total_prose_tokens,
            "unique_alpha_core_roots_all": len(unique_roots),
            "unique_alpha_core_roots_prose": len(root_prose_counts),
            "unique_elementary_radicals": len(radical_usage_types),
            "mean_radicals_per_token": round(mean_rads_per_token, 4),
            "mean_radicals_per_root_type": round(mean_rads_per_type, 4),
            "unsegmented_root_entropy_bits": round(H_unseg, 4),
            "elementary_radical_entropy_bits": round(H_rad, 4),
            "unsegmented_lexicon_bits": round(unseg_lexicon_bits, 1),
            "segmented_mdl_lexicon_bits": round(seg_total_lexicon_bits, 1),
            "mdl_lexicon_compression_ratio": round(mdl_compression_ratio, 3),
        },
        "core_root_coverage_milestones": coverage_milestones,
        "radical_coverage_curve": rad_coverage_curve,
        "num_radicals_per_root_distribution": {
            "by_root_types": {str(k): v for k, v in sorted(num_segments_dist_types.items())},
            "by_token_occurrences": {str(k): v for k, v in sorted(num_segments_dist_tokens.items())},
        },
        "top_50_elementary_radicals_by_tokens": [
            {
                "rank": idx,
                "radical": rad,
                "token_occurrences": t_cnt,
                "root_type_productivity": radical_usage_types[rad],
                "standalone_root_tokens": root_token_counts.get(rad, 0),
                "slot1_onset_types": slot1_radicals.get(rad, 0),
                "slot2_coda_types": slot2_radicals.get(rad, 0),
            }
            for idx, (rad, t_cnt) in enumerate(sorted_radicals_by_tokens[:50], 1)
        ],
        "top_40_elementary_radicals_by_type_productivity": [
            {
                "rank": idx,
                "radical": rad,
                "root_type_productivity": typ_cnt,
                "token_occurrences": radical_usage_tokens[rad],
                "standalone_root_tokens": root_token_counts.get(rad, 0),
                "slot1_onset_types": slot1_radicals.get(rad, 0),
                "slot2_coda_types": slot2_radicals.get(rad, 0),
            }
            for idx, (rad, typ_cnt) in enumerate(sorted_radicals_by_types[:40], 1)
        ],
        "top_40_radical_bigrams_R1_R2": [
            {
                "r1": a,
                "r2": b,
                "compound": a + b,
                "type_count": cnt,
                "standalone_compound_tokens": root_token_counts.get(a + b, 0),
                "examples": root_examples.get(a + b, [])[:3],
            }
            for (a, b), cnt in bigram_transitions.most_common(40)
        ],
        "commuting_radical_grid": commuting_grid,
        "paleographic_comma_microspace_verification": {
            "total_two_part_comma_tokens": total_comma_evaluated,
            "boundary_type_counts": dict(comma_boundary_stats),
            "overall_morpheme_or_radical_boundary_rate": round(
                aligned_comma_total / max(total_comma_evaluated, 1), 4
            ),
            "root_internal_comma_tokens": comma_root_internal_total,
            "root_internal_R1_R2_exact_hits": comma_root_internal_hits,
            "root_internal_random_expected": round(comma_root_random_expected, 2),
            "root_internal_hit_rate": round(p_hit, 4),
            "root_internal_expected_rate": round(p_exp, 4),
            "root_internal_enrichment_ratio": round(p_hit / max(p_exp, 1e-6), 3),
            "root_internal_z_score": round(z_comma, 2),
            "verified_examples": verified_comma_examples,
        },
        "decomposed_diagram_cribs": decomposed_cribs,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
