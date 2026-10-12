#!/usr/bin/env python3
"""
Attack 186 (Discovery 203): The f84r Three-Pool Vertical Hydro-Cascade, Canopy
Minimal-Pair Alternation (otdar -> otedar -> otody -> okol -> qokal -> okal -> qokol),
and Adjacent Diagram-Label Minimal-Pair Chaining Across the Manuscript.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

random.seed(186)


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[-1] + 1, prev[j] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


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
            txt_clean = re.sub(r"<[^>]+>", " ", txt_clean)
            txt_clean = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", txt_clean)
            txt_clean = re.sub(r"[^a-zA-Z0-9.\s]", "", txt_clean)
            words = [w.strip() for w in re.split(r"[.\s]+", txt_clean) if w.strip() and not w.strip().isdigit()]
            if words:
                folios[f_id]["lines"].append({
                    "line_id": f"{f_id}.{l_num}",
                    "loc": loc,
                    "words": words,
                })
    return folios


def main():
    zl_path = Path("data/ZL3b-n.txt")
    folios = parse_zl(zl_path)

    # 1. Detailed forensic dissection of f84r (Three-Pool Vertical Hydro-Cascade)
    f84r_lines = folios["f84r"]["lines"]
    f84r_labels = []
    f84r_paragraphs = []
    cur_p = []
    for l in f84r_lines:
        if "L" in l["loc"]:
            f84r_labels.append({
                "line_id": l["line_id"],
                "loc": l["loc"],
                "words": l["words"],
                "stems": [canonical_stem(w) for w in l["words"]],
            })
        elif "P" in l["loc"]:
            if l["loc"].startswith("@P") and cur_p:
                f84r_paragraphs.append(cur_p)
                cur_p = [l]
            else:
                cur_p.append(l)
    if cur_p:
        f84r_paragraphs.append(cur_p)

    f84r_label_words = [w for lb in f84r_labels for w in lb["words"]]
    f84r_prose_words = [w for p in f84r_paragraphs for l in p for w in l["words"]]
    f84r_prose_set = set(f84r_prose_words)
    f84r_prose_stems = set(canonical_stem(w) for w in f84r_prose_words)

    for lb in f84r_labels:
        lb["in_f84r_prose_exact"] = [w in f84r_prose_set for w in lb["words"]]
        lb["in_f84r_prose_stem"] = [canonical_stem(w) in f84r_prose_stems for w in lb["words"]]

    # Analyze adjacent pair edit distances on f84r canopy labels
    f84r_adj_pairs = []
    for i in range(len(f84r_label_words) - 1):
        w1, w2 = f84r_label_words[i], f84r_label_words[i + 1]
        f84r_adj_pairs.append({
            "pair": f"{w1} -> {w2}",
            "edit_distance": levenshtein(w1, w2),
            "same_canonical_stem": canonical_stem(w1) == canonical_stem(w2),
            "stem_1": canonical_stem(w1),
            "stem_2": canonical_stem(w2),
        })

    # 2. Global Adjacent Diagram-Label Minimal-Pair & Stem-Echo Test across all folios with >= 3 single-word @L/@R labels
    folio_label_seqs = {}
    all_label_tokens = []
    sec_label_tokens = defaultdict(list)

    for fid, fdata in folios.items():
        sec = fdata["meta"].get("I", "?")
        seq = []
        for l in fdata["lines"]:
            if ("L" in l["loc"] or "R" in l["loc"]) and len(l["words"]) <= 2:
                for w in l["words"]:
                    if len(w) >= 2:
                        seq.append(w)
                        all_label_tokens.append(w)
                        sec_label_tokens[sec].append(w)
        if len(seq) >= 3:
            folio_label_seqs[fid] = {"sec": sec, "words": seq}

    adj_pairs_total = 0
    adj_lev_le2 = 0
    adj_same_stem = 0
    adj_mean_lev_sum = 0
    notable_minimal_pairs = []

    for fid, info in folio_label_seqs.items():
        seq = info["words"]
        for i in range(len(seq) - 1):
            w1, w2 = seq[i], seq[i + 1]
            adj_pairs_total += 1
            d = levenshtein(w1, w2)
            s1, s2 = canonical_stem(w1), canonical_stem(w2)
            same_s = (s1 == s2 and len(s1) >= 1)
            adj_mean_lev_sum += d
            if d <= 2:
                adj_lev_le2 += 1
            if same_s:
                adj_same_stem += 1
            if d <= 2 or same_s:
                notable_minimal_pairs.append({
                    "folio": fid,
                    "sec": info["sec"],
                    "w1": w1,
                    "w2": w2,
                    "edit_distance": d,
                    "same_stem": same_s,
                    "stem": s1 if same_s else f"{s1}/{s2}",
                })

    obs_lev_le2_rate = adj_lev_le2 / adj_pairs_total
    obs_same_stem_rate = adj_same_stem / adj_pairs_total
    obs_mean_lev = adj_mean_lev_sum / adj_pairs_total

    # Section-stratified 2,000-trial permutation test
    null_lev_le2 = []
    null_same_stem = []
    null_mean_lev = []

    for _ in range(2000):
        shuffled_by_sec = {}
        for sec, toks in sec_label_tokens.items():
            shuf = toks[:]
            random.shuffle(shuf)
            shuffled_by_sec[sec] = iter(shuf)

        c_le2 = 0
        c_stem = 0
        c_sum = 0
        for fid, info in folio_label_seqs.items():
            sec = info["sec"]
            n_w = len(info["words"])
            sim_seq = [next(shuffled_by_sec[sec]) for _ in range(n_w)]
            for i in range(n_w - 1):
                w1, w2 = sim_seq[i], sim_seq[i + 1]
                d = levenshtein(w1, w2)
                s1, s2 = canonical_stem(w1), canonical_stem(w2)
                c_sum += d
                if d <= 2:
                    c_le2 += 1
                if s1 == s2 and len(s1) >= 1:
                    c_stem += 1
        null_lev_le2.append(c_le2 / adj_pairs_total)
        null_same_stem.append(c_stem / adj_pairs_total)
        null_mean_lev.append(c_sum / adj_pairs_total)

    def z_stats(obs, arr):
        m = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - m) ** 2 for x in arr) / len(arr)) or 1e-9
        return round(m, 4), round(obs / max(m, 1e-9), 2), round((obs - m) / sd, 2)

    null_le2_m, le2_lift, z_le2 = z_stats(obs_lev_le2_rate, null_lev_le2)
    null_stem_m, stem_lift, z_stem = z_stats(obs_same_stem_rate, null_same_stem)
    null_lev_m, lev_ratio, z_lev = z_stats(obs_mean_lev, null_mean_lev)

    # 3. Balneological ($I=B) Label-to-Host-Folio Echo across all Balneo folios with labels
    balneo_folios = {}
    total_b_labels = 0
    b_exact_in_host = 0
    b_stem_in_host = 0

    for fid, fdata in folios.items():
        if fdata["meta"].get("I") == "B":
            l_words = [w for l in fdata["lines"] if "L" in l["loc"] for w in l["words"]]
            p_words = [w for l in fdata["lines"] if "P" in l["loc"] for w in l["words"]]
            p_set = set(p_words)
            p_stems = set(canonical_stem(w) for w in p_words)
            if l_words:
                ex = sum(1 for w in l_words if w in p_set)
                st = sum(1 for w in l_words if canonical_stem(w) in p_stems)
                total_b_labels += len(l_words)
                b_exact_in_host += ex
                b_stem_in_host += st
                balneo_folios[fid] = {
                    "n_labels": len(l_words),
                    "n_prose_words": len(p_words),
                    "exact_in_host_rate": round(ex / len(l_words), 4),
                    "stem_in_host_rate": round(st / len(l_words), 4),
                    "labels": l_words,
                }

    out = {
        "attack": "Attack 186",
        "discovery": "Discovery 203",
        "title": "f84r Three-Pool Vertical Hydro-Cascade, Canopy Minimal-Pair Alternation, and Global Diagram-Label Minimal-Pair Chaining",
        "f84r_hydro_cascade": {
            "n_labels": len(f84r_label_words),
            "n_prose_paragraphs": len(f84r_paragraphs),
            "n_prose_words": len(f84r_prose_words),
            "labels": f84r_labels,
            "adjacent_label_pairs": f84r_adj_pairs,
            "exact_echo_in_f84r_prose": round(sum(1 for w in f84r_label_words if w in f84r_prose_set) / len(f84r_label_words), 4),
            "stem_echo_in_f84r_prose": round(sum(1 for w in f84r_label_words if canonical_stem(w) in f84r_prose_stems) / len(f84r_label_words), 4),
            "paragraph_summaries": [
                {
                    "paragraph_index": idx + 1,
                    "n_lines": len(p),
                    "n_words": sum(len(l["words"]) for l in p),
                    "first_line": ".".join(p[0]["words"][:8]),
                    "last_line": ".".join(p[-1]["words"][-8:]),
                }
                for idx, p in enumerate(f84r_paragraphs)
            ],
        },
        "global_diagram_label_minimal_pairs": {
            "n_folios_with_label_chains": len(folio_label_seqs),
            "n_adjacent_label_pairs": adj_pairs_total,
            "obs_lev_le2_count": adj_lev_le2,
            "obs_lev_le2_rate": round(obs_lev_le2_rate, 4),
            "null_lev_le2_rate": null_le2_m,
            "lev_le2_lift": le2_lift,
            "z_lev_le2": z_le2,
            "obs_same_stem_count": adj_same_stem,
            "obs_same_stem_rate": round(obs_same_stem_rate, 4),
            "null_same_stem_rate": null_stem_m,
            "same_stem_lift": stem_lift,
            "z_same_stem": z_stem,
            "obs_mean_edit_distance": round(obs_mean_lev, 4),
            "null_mean_edit_distance": null_lev_m,
            "z_mean_edit_distance": z_lev,
            "top_minimal_pair_chains": notable_minimal_pairs[:45],
        },
        "balneological_label_to_host_echo": {
            "total_balneo_labels": total_b_labels,
            "exact_in_host_count": b_exact_in_host,
            "exact_in_host_rate": round(b_exact_in_host / max(total_b_labels, 1), 4),
            "stem_in_host_count": b_stem_in_host,
            "stem_in_host_rate": round(b_stem_in_host / max(total_b_labels, 1), 4),
            "by_folio": balneo_folios,
        },
    }

    out_path = Path("data/attack186_f84r_canopy_minimal_pairs_and_balneo_cascade.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print(f"Global Adjacent Label Minimal Pairs (Lev <= 2): {obs_lev_le2_rate:.4f} vs null {null_le2_m:.4f} ({le2_lift}x, z={z_le2})")
    print(f"Global Adjacent Label Same Canonical Stem: {obs_same_stem_rate:.4f} vs null {null_stem_m:.4f} ({stem_lift}x, z={z_stem})")
    print(f"Global Adjacent Label Mean Edit Distance: {obs_mean_lev:.4f} vs null {null_lev_m:.4f} (z={z_lev})")
    print(f"Balneo Labels in Host Folio Prose: exact={b_exact_in_host}/{total_b_labels} ({b_exact_in_host/total_b_labels:.4f}), stem={b_stem_in_host}/{total_b_labels} ({b_stem_in_host/total_b_labels:.4f})")


if __name__ == "__main__":
    main()
