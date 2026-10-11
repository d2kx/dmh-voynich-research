#!/usr/bin/env python3
"""
Attack 13 (Phase 24 / Discovery 30):
Full-Manuscript Multi-Word Phrase, Compound-Split & Allographic Header Crib Scanner.

Tests four distinct structural mechanisms by which multi-word and compound diagram labels
appear in the prose text of the Voynich Manuscript:
1. Mode 1 (2-Word Phrase Crib): Multi-word label `w1 . w2` (or contiguous label pair `L_i -> L_{i+1}`)
   recurring as an adjacent (`gap=1`) or 1-word-bridged (`gap=2`) bigram in prose under Tier-1
   Canonical or Tier-2 Prefix-Agnostic Allographic equivalence (e.g., `<f88v.4> otar . arody`
   <-> `<f105r.6> <%>par . arody`).
2. Mode 2 (Fused Compound Crib): 2-word/comma-split diagram label `w1 . w2` / `w1 , w2`
   recurring in prose as a single fused compound word `w1w2` (e.g., `<f70v2.22> otar.am` -> `otaram`,
   `<f70v2.23> otar,al` -> `otaral`).
3. Mode 3 (Split Compound Crib): Single-word compound diagram label `W` split across two
   adjacent prose words `w1 . w2` (`stem(w1) + stem(w2) == stem(W)`).
4. Mode 4 (Same-Line Co-Occurrence): Both words of a multi-word label or contiguous label pair
   co-occurring on the exact same prose line (`gap <= 6`).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_PATH = ROOT / "data" / "attack13_multiword_phrase_crib_scanner.json"

SUFFIX_PAT = re.compile(
    r"(aiin|ain|iin|in|edy|eedy|ody|dy|eey|ey|ary|ory|ry|aly|oly|ly|am|om|al|ol|ar|or|y|r|l|s|d)$"
)


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"@\d+;", "", t)
    t = re.sub(r"[^a-zA-Z]", "", t).lower()
    return t.strip()


def canon_tier1(w: str) -> str:
    """Tier 1: Gallows p/f->t/k, vowel grade collapse, qo->o, -m->-r."""
    if not w:
        return ""
    s = w.replace("p", "t").replace("f", "k")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    s = re.sub(r"o+", "o", s)
    s = re.sub(r"a+", "a", s)
    if s.startswith("qo") and len(s) > 2:
        s = "o" + s[2:]
    if s.endswith("m") and len(s) > 2:
        s = s[:-1] + "r"
    return s


def stem_tier2(w: str) -> str:
    """
    Tier 2: Prefix-Agnostic Stem+Suffix Equivalence.
    Strips initial proclitics/classifiers (`qo-`, `q-`, `y-`, `o-`) from Tier 1 so that
    top-line bare gallows (`par`, `far`, `tar`, `kar`) match `o-` diagram nouns (`otar`, `opar`, `okar`, `ofar`).
    """
    s = canon_tier1(w)
    if len(s) > 2 and s[0] in ("q", "y") and s[1] in ("o", "e", "a", "t", "k", "c", "s"):
        s = s[1:]
    if len(s) > 2 and s.startswith("o") and not s.startswith(("ol", "or")):
        s = s[1:]
    return s


def classify_domain(folio: str, unit_type: str, illus: str) -> str:
    if folio in ("fRos", "f85v2"):
        return "Rosettes_Cosmo"
    if folio.startswith(("f70", "f71", "f72", "f73")):
        return "Zodiac"
    if folio.startswith(("f67", "f68", "f69")):
        return "Astronomical"
    if "Lc" in unit_type:
        return "Pharma_Jar"
    if "Lf" in unit_type or illus == "P":
        return "Pharma_Botanical"
    if "Ln" in unit_type or "Lt" in unit_type or illus == "B":
        return "Bio_Nymph_Tube"
    return f"Other_{illus}"


def parse_zl():
    text = ZL_PATH.read_text(encoding="utf-8", errors="ignore")
    lines = []
    current_folio = None
    cur_meta = {}
    in_first_line_of_par = False

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
            in_first_line_of_par = True
            continue

        m_loc = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m_loc or not current_folio:
            continue
        loc_header = m_loc.group(1)
        body = m_loc.group(2)
        parts = loc_header.split(",")
        loc_id = parts[0]
        unit_type = parts[1] if len(parts) > 1 else ""

        has_par_start = "<%>" in body or unit_type.startswith("@P") or unit_type.startswith("@L")
        has_par_end = "<$>" in body
        if has_par_start:
            in_first_line_of_par = True

        body_no_comments = re.sub(r"<!([^>]*)>", "", body)
        body_no_comments = body_no_comments.replace("<%>", "").replace("<$>", "")

        raw_dot_tokens = [t for t in re.split(r"[\.\s]+", body_no_comments.replace("<->", " ")) if t]
        words_joined = [clean_tok(t.replace(",", "")) for t in raw_dot_tokens]
        words_joined = [w for w in words_joined if w]

        words_comma_split = [clean_tok(t) for t in re.split(r"[\.\s,]+", body_no_comments.replace("<->", " ")) if t]
        words_comma_split = [w for w in words_comma_split if w]

        if not words_joined:
            continue

        is_label = ("@L" in unit_type) or ("&L" in unit_type) or unit_type.startswith("L")
        lines.append({
            "folio": current_folio,
            "loc_id": loc_id,
            "unit_type": unit_type,
            "lang": cur_meta.get("L", "Unknown"),
            "hand": cur_meta.get("H", "Unknown"),
            "illus": cur_meta.get("I", "Unknown"),
            "is_label": is_label,
            "has_par_start": "<%>" in body or unit_type.startswith("@P"),
            "has_par_end": has_par_end,
            "is_top_line": in_first_line_of_par,
            "raw_body": body_no_comments.strip(),
            "words": words_joined,
            "words_comma_split": words_comma_split,
        })

        if has_par_end:
            in_first_line_of_par = True
        else:
            in_first_line_of_par = False

    return lines


def main():
    lines = parse_zl()
    label_lines = [l for l in lines if l["is_label"]]
    prose_lines = [l for l in lines if not l["is_label"]]
    print(f"Loaded {len(prose_lines)} prose lines and {len(label_lines)} label lines.")

    prose_t1_counts = Counter()
    prose_t2_counts = Counter()
    total_prose_tokens = 0

    for pl in prose_lines:
        for w in pl["words"]:
            total_prose_tokens += 1
            prose_t1_counts[canon_tier1(w)] += 1
            prose_t2_counts[stem_tier2(w)] += 1

    # 1. Extract all Single-Locus Multi-Word Labels & Contiguous 2-Label Sequences
    multiword_labels = []
    single_word_labels = []

    for ll in label_lines:
        dom = classify_domain(ll["folio"], ll["unit_type"], ll["illus"])
        if len(ll["words"]) == 1:
            w = ll["words"][0]
            if len(w) >= 4:
                single_word_labels.append({
                    "folio": ll["folio"],
                    "loc_id": ll["loc_id"],
                    "unit_type": ll["unit_type"],
                    "domain": dom,
                    "word": w,
                    "t1": canon_tier1(w),
                    "t2": stem_tier2(w),
                    "t1_prose_cnt": prose_t1_counts[canon_tier1(w)],
                    "t2_prose_cnt": prose_t2_counts[stem_tier2(w)],
                })
        variants = [("Dot_MultiWord_Label", ll["words"])]
        if ll["words_comma_split"] != ll["words"] and len(ll["words_comma_split"]) >= 2:
            variants.append(("Comma_MultiWord_Label", ll["words_comma_split"]))
        for stype, wlist in variants:
            if len(wlist) >= 2:
                for i in range(len(wlist) - 1):
                    w1, w2 = wlist[i], wlist[i + 1]
                    if len(w1) < 2 or len(w2) < 2:
                        continue
                    multiword_labels.append({
                        "source_type": stype,
                        "folio": ll["folio"],
                        "loc_id": ll["loc_id"],
                        "unit_type": ll["unit_type"],
                        "domain": dom,
                        "w1": w1,
                        "w2": w2,
                        "t1_pair": (canon_tier1(w1), canon_tier1(w2)),
                        "t2_pair": (stem_tier2(w1), stem_tier2(w2)),
                        "c1_prose": prose_t1_counts[canon_tier1(w1)],
                        "c2_prose": prose_t1_counts[canon_tier1(w2)],
                        "t2_c1_prose": prose_t2_counts[stem_tier2(w1)],
                        "t2_c2_prose": prose_t2_counts[stem_tier2(w2)],
                    })

    contiguous_label_pairs = []
    for idx in range(len(label_lines) - 1):
        l1, l2 = label_lines[idx], label_lines[idx + 1]
        if l1["folio"] != l2["folio"]:
            continue
        w1 = l1["words"][-1]
        w2 = l2["words"][0]
        if len(w1) < 2 or len(w2) < 2:
            continue
        dom = classify_domain(l1["folio"], l1["unit_type"], l1["illus"])
        contiguous_label_pairs.append({
            "source_type": "Contiguous_Adjacent_Labels",
            "folio": l1["folio"],
            "loc_id": f"{l1['loc_id']}->{l2['loc_id']}",
            "unit_type": l1["unit_type"],
            "domain": dom,
            "w1": w1,
            "w2": w2,
            "t1_pair": (canon_tier1(w1), canon_tier1(w2)),
            "t2_pair": (stem_tier2(w1), stem_tier2(w2)),
            "c1_prose": prose_t1_counts[canon_tier1(w1)],
            "c2_prose": prose_t1_counts[canon_tier1(w2)],
            "t2_c1_prose": prose_t2_counts[stem_tier2(w1)],
            "t2_c2_prose": prose_t2_counts[stem_tier2(w2)],
        })

    # Index by Tier 1 and Tier 2 with a joint rarity filter:
    # Require min(t2_c1, t2_c2) <= 35 OR (min(t2_c1, t2_c2) <= 60 and t2_c1 * t2_c2 <= 25000)
    t1_index = defaultdict(list)
    t2_index = defaultdict(list)
    for item in multiword_labels + contiguous_label_pairs:
        c1, c2 = item["t2_c1_prose"], item["t2_c2_prose"]
        if min(c1, c2) <= 35 or (min(c1, c2) <= 60 and (c1 * c2) <= 25000):
            t1_index[item["t1_pair"]].append(item)
            t2_index[item["t2_pair"]].append(item)

    # MODE 1 & MODE 4: Scan prose lines for gap=1 (adjacent), gap=2 (1-word bridged), and gap<=6 (same-line)
    mode1_matches = []
    mode4_same_line_matches = []
    par_opener_matches = []

    for pl in prose_lines:
        wlist = pl["words"]
        n = len(wlist)
        for i in range(n - 1):
            for gap in range(1, min(7, n - i)):
                pw1, pw2 = wlist[i], wlist[i + gap]
                pt1 = (canon_tier1(pw1), canon_tier1(pw2))
                pt2 = (stem_tier2(pw1), stem_tier2(pw2))

                matched_items = []
                match_tier = None
                if pt1 in t1_index:
                    matched_items = t1_index[pt1]
                    match_tier = "Tier1_Canonical_Exact"
                elif pt2 in t2_index:
                    matched_items = t2_index[pt2]
                    match_tier = "Tier2_Allographic_Stem"

                if not matched_items:
                    continue

                matched_items = sorted(
                    matched_items,
                    key=lambda x: (
                        0 if "MultiWord_Label" in x["source_type"] else 1,
                        x["t2_c1_prose"] * x["t2_c2_prose"],
                    ),
                )
                best = matched_items[0]
                if pl["folio"] == best["folio"]:
                    continue

                p1 = max(best["t2_c1_prose"], 1) / total_prose_tokens
                p2 = max(best["t2_c2_prose"], 1) / total_prose_tokens
                info_bits = -math.log2(p1 * p2)

                is_par_start = pl["has_par_start"] and i == 0
                is_line_start = i == 0

                rec = {
                    "prose_folio": pl["folio"],
                    "prose_loc": pl["loc_id"],
                    "prose_sec": pl["illus"],
                    "prose_lang": pl["lang"],
                    "is_par_start": is_par_start,
                    "is_line_start": is_line_start,
                    "word_pos": i,
                    "gap": gap,
                    "prose_words": " . ".join(wlist[i:i + gap + 1]),
                    "prose_line_text": " . ".join(wlist),
                    "match_tier": match_tier,
                    "t2_pair": list(pt2),
                    "label_source_type": best["source_type"],
                    "label_folio": best["folio"],
                    "label_loc": best["loc_id"],
                    "label_domain": best["domain"],
                    "label_words": f"{best['w1']} . {best['w2']}",
                    "t1_counts_in_prose": [best["c1_prose"], best["c2_prose"]],
                    "t2_counts_in_prose": [best["t2_c1_prose"], best["t2_c2_prose"]],
                    "joint_rarity_bits": round(info_bits, 2),
                }
                if gap <= 2:
                    mode1_matches.append(rec)
                    if is_par_start and gap == 1:
                        par_opener_matches.append(rec)
                mode4_same_line_matches.append(rec)

    mode1_matches.sort(
        key=lambda x: (
            0 if x["gap"] == 1 else 1,
            0 if "MultiWord_Label" in x["label_source_type"] else 1,
            -x["joint_rarity_bits"],
        )
    )
    mode4_same_line_matches.sort(
        key=lambda x: (
            0 if "MultiWord_Label" in x["label_source_type"] else 1,
            x["gap"],
            -x["joint_rarity_bits"],
        )
    )

    # MODE 2: Fused Compound Crib (`w1 . w2` or `w1 , w2` in diagram -> single compound word `w1w2` in prose)
    fused_label_index = defaultdict(list)
    for item in multiword_labels:
        fused_raw = item["w1"] + item["w2"]
        fused_t1 = canon_tier1(fused_raw)
        fused_t2 = stem_tier2(fused_raw)
        if len(fused_t2) >= 4:
            fused_label_index[fused_t1].append(item)
            fused_label_index[fused_t2].append(item)

    mode2_fused_matches = []
    for pl in prose_lines:
        for i, pw in enumerate(pl["words"]):
            pt1 = canon_tier1(pw)
            pt2 = stem_tier2(pw)
            hits = fused_label_index.get(pt1) or fused_label_index.get(pt2)
            if not hits:
                continue
            best = hits[0]
            if pl["folio"] == best["folio"]:
                continue
            cnt_prose = prose_t1_counts[pt1]
            if cnt_prose <= 25:
                mode2_fused_matches.append({
                    "prose_folio": pl["folio"],
                    "prose_loc": pl["loc_id"],
                    "prose_sec": pl["illus"],
                    "word_pos": i,
                    "prose_word": pw,
                    "prose_word_count": cnt_prose,
                    "prose_line_text": " . ".join(pl["words"]),
                    "label_source_type": best["source_type"],
                    "label_folio": best["folio"],
                    "label_loc": best["loc_id"],
                    "label_domain": best["domain"],
                    "label_words": f"{best['w1']} . {best['w2']}",
                })

    mode2_fused_matches.sort(key=lambda x: (x["prose_word_count"], x["prose_loc"]))

    # MODE 3: Split Compound Crib (Single-word rare compound label `W` -> split across 2 adjacent prose words `w1 . w2`)
    compound_label_index = defaultdict(list)
    for sw in single_word_labels:
        if len(sw["t1"]) >= 6 and sw["t1_prose_cnt"] <= 15:
            compound_label_index[sw["t1"]].append(sw)
            compound_label_index[sw["t2"]].append(sw)

    mode3_split_matches = []
    for pl in prose_lines:
        wlist = pl["words"]
        for i in range(len(wlist) - 1):
            pw1, pw2 = wlist[i], wlist[i + 1]
            if len(pw1) < 2 or len(pw2) < 2:
                continue
            joined_t1 = canon_tier1(pw1 + pw2)
            joined_t2 = stem_tier2(pw1) + canon_tier1(pw2)
            hits = compound_label_index.get(joined_t1) or compound_label_index.get(joined_t2)
            if not hits:
                continue
            best = hits[0]
            if pl["folio"] == best["folio"]:
                continue
            mode3_split_matches.append({
                "prose_folio": pl["folio"],
                "prose_loc": pl["loc_id"],
                "prose_sec": pl["illus"],
                "is_par_start": pl["has_par_start"] and i == 0,
                "word_pos": i,
                "prose_bigram": f"{pw1} . {pw2}",
                "joined_canon": joined_t1,
                "prose_line_text": " . ".join(wlist),
                "label_folio": best["folio"],
                "label_loc": best["loc_id"],
                "label_domain": best["domain"],
                "label_word": best["word"],
                "label_prose_cnt": best["t1_prose_cnt"],
            })

    mode3_split_matches.sort(key=lambda x: (x["label_prose_cnt"], x["prose_loc"]))

    # Fast 1,000-Trial Permutation Test on Mode 3 (Split Compound Cribs)
    prose_c1_list = [canon_tier1(w) for pl in prose_lines for w in pl["words"] if len(w) >= 2]
    prose_s2_list = [stem_tier2(w) for pl in prose_lines for w in pl["words"] if len(w) >= 2]
    rng = random.Random(42)
    obs_split_hits = len(mode3_split_matches)
    n_pool = len(prose_c1_list)
    null_split_counts = []
    for _ in range(500):
        cnt = 0
        for _ in range(33400):
            idx1 = rng.randrange(n_pool)
            idx2 = rng.randrange(n_pool)
            c1 = prose_c1_list[idx1]
            c2 = prose_c1_list[idx2]
            if (c1 + c2) in compound_label_index or (prose_s2_list[idx1] + c2) in compound_label_index:
                cnt += 1
        null_split_counts.append(cnt)
    mean_sp = sum(null_split_counts) / len(null_split_counts)
    std_sp = math.sqrt(sum((x - mean_sp) ** 2 for x in null_split_counts) / len(null_split_counts))
    z_sp = (obs_split_hits - mean_sp) / max(std_sp, 1e-6)
    p_sp = sum(1 for x in null_split_counts if x >= obs_split_hits) / len(null_split_counts)

    print(f"Mode 1 (Adjacent/Bridged 2-Word Phrase Cribs, gap<=2): {len(mode1_matches)} (Par Openers: {len(par_opener_matches)})")
    print(f"Mode 2 (2-Word/Comma Diagram Label -> Fused Prose Compound): {len(mode2_fused_matches)}")
    print(
        f"Mode 3 (Compound Diagram Label -> Split 2-Word Prose Bigram): {len(mode3_split_matches)} "
        f"(Expected={mean_sp:.2f}±{std_sp:.2f}, {obs_split_hits/max(mean_sp,1e-6):.2f}x, z={z_sp:+.2f}, p={p_sp:.4f})"
    )
    print(f"Mode 4 (Same-Line 2-Word Label Pair Co-Occurrences, gap<=6): {len(mode4_same_line_matches)}")

    output = {
        "summary": {
            "total_prose_lines": len(prose_lines),
            "total_label_lines": len(label_lines),
            "single_locus_multiword_label_pairs": len(multiword_labels),
            "contiguous_adjacent_label_pairs": len(contiguous_label_pairs),
            "mode1_adjacent_or_bridged_phrase_hits": len(mode1_matches),
            "mode1_paragraph_opener_hits": len(par_opener_matches),
            "mode2_fused_compound_hits": len(mode2_fused_matches),
            "mode3_split_compound_hits": len(mode3_split_matches),
            "mode4_same_line_pair_hits": len(mode4_same_line_matches),
        },
        "mode3_split_compound_permutation_test": {
            "observed_hits": obs_split_hits,
            "null_mean": round(mean_sp, 3),
            "null_std": round(std_sp, 3),
            "enrichment_ratio": round(obs_split_hits / max(mean_sp, 1e-6), 3),
            "z_score": round(z_sp, 2),
            "p_value": round(p_sp, 4),
        },
        "mode1_paragraph_opener_hits": par_opener_matches,
        "mode1_top_phrase_matches": mode1_matches[:50],
        "mode2_top_fused_compound_matches": mode2_fused_matches[:50],
        "mode3_top_split_compound_matches": mode3_split_matches[:50],
        "mode4_top_same_line_matches": mode4_same_line_matches[:50],
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
