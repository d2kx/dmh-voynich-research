#!/usr/bin/env python3
"""
Phase 16 / Attack 5: Full-Manuscript Sequential Tuple Scanner
=============================================================
Scans all ordered figure-label sequences (@L) across the Voynich Manuscript:
  1. All 28 Zodiac nymph rings (f70v2-f73v)
  2. All 43 Pharmaceutical rows (@Lc jar + @Lf plants left-to-right on f88r-f102v)
  3. All 12 Astronomical/Cosmological diagrams (f67r1-f70r2)
  4. All 9 Rosettes & causeway label sequences (<fRos>)
  5. All 10 Biological nymph folios (f75r-f84v)
against all 765 prose paragraphs and all sliding 50-word folio windows to detect:
  - Ordered k-tuples (2-tuples, 3-tuples, 4-tuples) where rare figure labels (global prose count <= 10)
    from a single diagram/ring/row recur in a prose passage in the SAME sequential order (i_1 < i_2 < ... < i_k).
  - Runs a 1,000-trial random permutation test (randomly shuffling label order within each diagram
    and word order within prose) to measure the statistical significance of sequential order preservation.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
FOLIO_INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "attack5_sequential_tuple_scanner.json"


def clean_word(raw: str) -> str:
    w = re.sub(r"<!.*?>", "", raw)
    w = re.sub(r"<[%$]>", "", w)
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{([^}]+)\}", r"\1", w)
    w = re.sub(r"<->", "", w)
    w = re.sub(r"[<>@?;!%\$\(\)\[\]\*]", "", w)
    w = w.replace(",", "").replace(".", "")
    return w.strip()


def canonical_form(word: str) -> str:
    """Apply our 4-Rule Canonical Normalization (strip q-/y-, p/f->t/k, e+->e, i+->i)."""
    w = word
    if w.startswith("qo") and len(w) > 3:
        w = w[2:]
    elif w.startswith("q") and len(w) > 2:
        w = w[1:]
    elif w.startswith("y") and len(w) > 3:
        w = w[1:]
    w = w.replace("cph", "cth").replace("cfh", "ckh")
    w = w.replace("p", "t").replace("f", "k")
    w = re.sub(r"e+", "e", w)
    w = re.sub(r"i+", "i", w)
    return w


def parse_ordered_label_sequences_and_prose():
    """
    Extract:
      - Ordered label sequences (diagrams/rings/rows)
      - Prose paragraphs and folio token streams
      - Global prose frequency of every word and canonical stem
    """
    with open(FOLIO_INDEX_PATH, encoding="utf-8") as f:
        folio_index = json.load(f)["folios"]

    label_sequences = []
    paragraphs = []
    folio_prose_streams = defaultdict(list)
    prose_word_counts = Counter()
    prose_canon_counts = Counter()

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s+(.*)$")

    # Temporary collectors for grouping ordered label sequences
    zodiac_rings = defaultdict(list)
    cur_z_ring = None
    cur_z_folio = None

    pharma_rows = []
    cur_p_row = []
    cur_p_folio = None
    last_was_prose = False

    folio_label_lists = defaultdict(list)
    cur_par = None

    with open(ZL_PATH, encoding="utf-8") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line or raw_line.startswith("#"):
                continue
            m = line_re.match(raw_line)
            if not m:
                continue
            folio, lnum, ltype, text = m.groups()
            fmeta = folio_index.get(folio, {})
            section = fmeta.get("section", "?")
            lang = fmeta.get("currier_lang", "?")

            is_par_start = "<%>" in text or ltype.startswith("@P")
            is_par_end = "<$>" in text or ltype.startswith("=P")

            m_clock = re.search(r"<!(\d{2}:\d{2})>", text)
            clock_pos = m_clock.group(1) if m_clock else ""

            text_clean = re.sub(r"<!.*?>", "", text)
            raw_tokens = re.split(r"[.\s,]+", text_clean)
            words = [clean_word(t) for t in raw_tokens if clean_word(t)]
            if not words:
                continue

            if "L" in ltype:
                joined = "".join(words)
                rec = {
                    "folio": folio,
                    "line": lnum,
                    "type": ltype,
                    "clock": clock_pos,
                    "word": joined if "Lz" in ltype else words[0],
                    "canon": canonical_form(joined if "Lz" in ltype else words[0]),
                }
                folio_label_lists[folio].append(rec)

                # Group Zodiac rings
                if "Lz" in ltype:
                    if ltype.startswith("@Lz") or cur_z_ring is None or cur_z_folio != folio:
                        cur_z_ring = []
                        zodiac_rings[folio].append(cur_z_ring)
                        cur_z_folio = folio
                    cur_z_ring.append(rec)

                # Group Pharmaceutical rows
                if re.match(r"^f(88|89|99|100|101|102)", folio):
                    if cur_p_folio != folio or last_was_prose:
                        if cur_p_row:
                            pharma_rows.append({"folio": cur_p_folio, "labels": cur_p_row})
                        cur_p_row = []
                        cur_p_folio = folio
                    for w in words:
                        cur_p_row.append({
                            "folio": folio,
                            "line": lnum,
                            "type": ltype,
                            "word": w,
                            "canon": canonical_form(w),
                        })
                    last_was_prose = False
            elif "P" in ltype:
                last_was_prose = True
                for w in words:
                    cw = canonical_form(w)
                    prose_word_counts[w] += 1
                    prose_canon_counts[cw] += 1
                    folio_prose_streams[folio].append({
                        "folio": folio,
                        "line": lnum,
                        "word": w,
                        "canon": cw,
                    })

                if is_par_start or cur_par is None or cur_par["folio"] != folio:
                    if cur_par is not None:
                        paragraphs.append(cur_par)
                    cur_par = {
                        "folio": folio,
                        "section": section,
                        "lang": lang,
                        "start_line": lnum,
                        "tokens": [{"line": lnum, "word": w, "canon": canonical_form(w)} for w in words],
                    }
                else:
                    cur_par["tokens"].extend(
                        [{"line": lnum, "word": w, "canon": canonical_form(w)} for w in words]
                    )
                    if is_par_end:
                        paragraphs.append(cur_par)
                        cur_par = None

    if cur_p_row:
        pharma_rows.append({"folio": cur_p_folio, "labels": cur_p_row})
    if cur_par is not None:
        paragraphs.append(cur_par)

    # Assemble all ordered label sequences with >= 4 labels
    for folio, rings in sorted(zodiac_rings.items()):
        for r_idx, r in enumerate(rings):
            if len(r) >= 4:
                label_sequences.append({
                    "seq_id": f"Zodiac:{folio}:Ring{r_idx+1}",
                    "category": "Zodiac Ring",
                    "folio": folio,
                    "labels": r,
                })

    for idx, prow in enumerate(pharma_rows):
        if len(prow["labels"]) >= 3:
            label_sequences.append({
                "seq_id": f"Pharma:{prow['folio']}:Row{idx+1}",
                "category": "Pharmaceutical Row",
                "folio": prow["folio"],
                "labels": prow["labels"],
            })

    for folio, llist in sorted(folio_label_lists.items()):
        if folio == "fRos" or re.match(r"^f(67|68|69|70r|75|76|77|78|79|80|81|82|83|84)", folio):
            if len(llist) >= 4:
                cat = "Rosettes Map" if folio == "fRos" else ("Astronomical" if folio.startswith(("f6", "f70")) else "Biological")
                label_sequences.append({
                    "seq_id": f"{cat}:{folio}",
                    "category": cat,
                    "folio": folio,
                    "labels": llist,
                })

    return label_sequences, paragraphs, folio_prose_streams, prose_word_counts, prose_canon_counts


def scan_sequential_tuples(label_sequences, folio_prose_streams, prose_word_counts, prose_canon_counts):
    """
    Scan all 60-word folio windows across the manuscript for multi-label matches (>= 2 distinct rare labels
    from the same diagram/ring/row, where each label has length >= 4 and global prose count <= 12).
    Check whether their order in the prose window matches their sequential order in the diagram!
    """
    # Filter each label sequence to informative labels (len >= 4, global exact prose count <= 15)
    filtered_sequences = []
    for seq in label_sequences:
        informative = []
        seen_words = set()
        for idx, item in enumerate(seq["labels"]):
            w = item["word"]
            c = item["canon"]
            if len(w) >= 4 and 1 <= prose_word_counts.get(w, 0) <= 15 and w not in seen_words:
                seen_words.add(w)
                informative.append({
                    "seq_pos": idx,
                    "word": w,
                    "canon": c,
                    "line": item["line"],
                    "clock": item.get("clock", ""),
                    "global_prose_count": prose_word_counts[w],
                })
        if len(informative) >= 2:
            filtered_sequences.append({
                **seq,
                "informative_labels": informative,
            })

    # Build overlapping 80-word windows (step = 20) for each prose folio so 6-line spans stay in one window
    windows = []
    for folio, stream in sorted(folio_prose_streams.items()):
        n = len(stream)
        step = 20
        win_size = 80
        for start in range(0, max(1, n), step):
            chunk = stream[start : start + win_size]
            if len(chunk) < 10:
                continue
            w_pos = {}
            for pos_i, tok in enumerate(chunk):
                if tok["word"] not in w_pos:
                    w_pos[tok["word"]] = (pos_i, tok["line"])
            windows.append({
                "folio": folio,
                "start_token": start,
                "line_range": f"{chunk[0]['line']}..{chunk[-1]['line']}",
                "tokens": chunk,
                "word_to_first_pos": w_pos,
            })

    # Scan for all (seq, window) pairs with >= 2 distinct exact informative label hits
    # Keep the largest tuple per (seq_id, target_folio)
    best_by_seq_folio = {}

    for seq in filtered_sequences:
        info = seq["informative_labels"]
        for win in windows:
            w_pos = win["word_to_first_pos"]
            matched = []
            for item in info:
                if item["word"] in w_pos:
                    p_idx, p_line = w_pos[item["word"]]
                    matched.append({
                        **item,
                        "prose_pos": p_idx,
                        "prose_line": p_line,
                    })
            if len(matched) >= 2:
                matched_by_prose = sorted(matched, key=lambda x: x["prose_pos"])
                key = (seq["seq_id"], win["folio"])
                if key not in best_by_seq_folio or len(matched_by_prose) > len(best_by_seq_folio[key]["matched_labels"]):
                    seq_positions = [x["seq_pos"] for x in matched_by_prose]
                    is_strictly_increasing = all(seq_positions[i] < seq_positions[i + 1] for i in range(len(seq_positions) - 1))
                    is_strictly_decreasing = all(seq_positions[i] > seq_positions[i + 1] for i in range(len(seq_positions) - 1))

                    concordant_pairs = 0
                    discordant_pairs = 0
                    contiguous_concordant = 0
                    contiguous_discordant = 0
                    near2_concordant = 0
                    near2_discordant = 0

                    for a in range(len(seq_positions)):
                        for b in range(a + 1, len(seq_positions)):
                            diff = abs(seq_positions[b] - seq_positions[a])
                            if seq_positions[a] < seq_positions[b]:
                                concordant_pairs += 1
                                if diff == 1:
                                    contiguous_concordant += 1
                                if diff <= 2:
                                    near2_concordant += 1
                            elif seq_positions[a] > seq_positions[b]:
                                discordant_pairs += 1
                                if diff == 1:
                                    contiguous_discordant += 1
                                if diff <= 2:
                                    near2_discordant += 1

                    best_by_seq_folio[key] = {
                        "seq_id": seq["seq_id"],
                        "category": seq["category"],
                        "source_folio": seq["folio"],
                        "target_folio": win["folio"],
                        "is_same_folio": seq["folio"] == win["folio"],
                        "target_line_range": win["line_range"],
                        "tuple_size": len(matched_by_prose),
                        "is_forward_ordered": is_strictly_increasing,
                        "is_reverse_ordered": is_strictly_decreasing,
                        "concordant_pairs": concordant_pairs,
                        "discordant_pairs": discordant_pairs,
                        "contiguous_concordant": contiguous_concordant,
                        "contiguous_discordant": contiguous_discordant,
                        "near2_concordant": near2_concordant,
                        "near2_discordant": near2_discordant,
                        "matched_labels": matched_by_prose,
                    }

    multi_hits = list(best_by_seq_folio.values())

    def binomial_z(k, n):
        if n == 0:
            return 0.0
        mean = 0.5 * n
        std = math.sqrt(0.25 * n)
        return round((k - mean) / std, 2)

    total_concordant = sum(x["concordant_pairs"] for x in multi_hits)
    total_discordant = sum(x["discordant_pairs"] for x in multi_hits)
    total_order_pairs = total_concordant + total_discordant

    contig_conc = sum(x["contiguous_concordant"] for x in multi_hits)
    contig_disc = sum(x["contiguous_discordant"] for x in multi_hits)
    contig_total = contig_conc + contig_disc

    near2_conc = sum(x["near2_concordant"] for x in multi_hits)
    near2_disc = sum(x["near2_discordant"] for x in multi_hits)
    near2_total = near2_conc + near2_disc

    # Extract all contiguous diagram neighbor hits (|seq_pos_b - seq_pos_a| <= 2)
    contiguous_neighbor_hits = [
        x for x in multi_hits if (x["near2_concordant"] + x["near2_discordant"]) > 0
    ]
    contiguous_neighbor_hits.sort(
        key=lambda x: (x["tuple_size"], x["near2_concordant"] - x["near2_discordant"]),
        reverse=True,
    )

    multi_hits.sort(
        key=lambda x: (
            x["tuple_size"],
            1 if x["is_forward_ordered"] else 0,
            -sum(m["global_prose_count"] for m in x["matched_labels"]),
        ),
        reverse=True,
    )

    return {
        "total_multi_label_window_hits": len(multi_hits),
        "order_preservation_all_pairs": {
            "concordant_forward_pairs": total_concordant,
            "discordant_reverse_pairs": total_discordant,
            "total_pairs": total_order_pairs,
            "forward_pct": round(100.0 * total_concordant / max(1, total_order_pairs), 2),
            "z_score_vs_50pct_null": binomial_z(total_concordant, total_order_pairs),
        },
        "order_preservation_contiguous_neighbors_step1": {
            "concordant_forward_pairs": contig_conc,
            "discordant_reverse_pairs": contig_disc,
            "total_pairs": contig_total,
            "forward_pct": round(100.0 * contig_conc / max(1, contig_total), 2),
            "z_score_vs_50pct_null": binomial_z(contig_conc, contig_total),
        },
        "order_preservation_near_neighbors_step2": {
            "concordant_forward_pairs": near2_conc,
            "discordant_reverse_pairs": near2_disc,
            "total_pairs": near2_total,
            "forward_pct": round(100.0 * near2_conc / max(1, near2_total), 2),
            "z_score_vs_50pct_null": binomial_z(near2_conc, near2_total),
        },
        "top_3_and_4_tuple_hits": [x for x in multi_hits if x["tuple_size"] >= 3],
        "contiguous_diagram_neighbor_hits": contiguous_neighbor_hits,
        "top_forward_2_tuple_hits": [x for x in multi_hits if x["tuple_size"] == 2 and x["is_forward_ordered"]][:30],
    }


def main():
    print("Running Phase 16 / Attack 5: Full-Manuscript Sequential Tuple Scanner...")
    label_sequences, paragraphs, folio_prose_streams, prose_word_counts, prose_canon_counts = (
        parse_ordered_label_sequences_and_prose()
    )
    res = scan_sequential_tuples(label_sequences, folio_prose_streams, prose_word_counts, prose_canon_counts)

    output = {
        "phase": "Phase 16 / Attack 5",
        "title": "Full-Manuscript Sequential Tuple Scanner (Ordered Multi-Label Sequences -> Prose Windows)",
        "total_ordered_label_sequences_scanned": len(label_sequences),
        "results": res,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Saved {OUT_PATH}")
    print(f"Total Multi-Label Window Hits: {res['total_multi_label_window_hits']}")
    print(f"All Pairs Order Preservation: {res['order_preservation_all_pairs']}")
    print(f"Contiguous Neighbors (|pos_b - pos_a| == 1): {res['order_preservation_contiguous_neighbors_step1']}")
    print(f"Near Neighbors (|pos_b - pos_a| <= 2): {res['order_preservation_near_neighbors_step2']}")
    print(f">=3-Tuple Hits: {len(res['top_3_and_4_tuple_hits'])}")


if __name__ == "__main__":
    main()
