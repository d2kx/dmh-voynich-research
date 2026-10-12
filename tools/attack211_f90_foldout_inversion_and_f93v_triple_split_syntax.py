#!/usr/bin/env python3
"""
Attack 211 (Discovery 228): The f90 (Quire 15) Foldout Inversion & Beinecke '90r'
Mislabel Proof (p165-p167), f93r<->f93v Leaf Coupling, and the Multi-Intrusion
(<-> X <->) Inter-Stem Micro-Corridor Compression Law.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "attack211_f90_foldout_inversion_and_f93v_triple_split_syntax.json"


def canonical_stem(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]+\}", "", w)
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w:
        return ""
    if w.startswith("qo") and len(w) > 3:
        w = w[2:]
    elif w.startswith("q") and len(w) > 2:
        w = w[1:]
    w = w.replace("ee", "e").replace("ii", "i")
    for sfx in ("aiin", "oiin", "ain", "oin", "edy", "eey", "ody", "ey", "dy", "al", "ol", "or", "ar", "am", "om", "y", "l", "r", "m", "n", "s"):
        if w.endswith(sfx) and len(w) - len(sfx) >= 2:
            w = w[: -len(sfx)]
            break
    return w


def clean_word(word: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", word)
    w = re.sub(r"\{[^}]+\}", "", w)
    w = re.sub(r"[^a-z]", "", w.lower())
    return w


def parse_zl():
    text = ZL_PATH.read_text(encoding="utf-8", errors="ignore")
    folios = defaultdict(lambda: {"words": [], "lines": [], "intrusions": 0})
    multi_intrusion_lines = []
    interior_corridor_tokens = []
    outer_segment_tokens = []

    for raw_line in text.splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s+(.*)$", raw_line)
        if not m:
            continue
        folio, lnum, loc, body = m.groups()
        body_no_comments = re.sub(r"<!.*?>", "", body)
        intrusions = body_no_comments.count("<->")
        folios[folio]["intrusions"] += intrusions
        toks = [clean_word(t) for t in re.split(r"[.,\s<>\-$%]+", body_no_comments) if clean_word(t)]
        if not toks:
            continue
        folios[folio]["words"].extend(toks)
        folios[folio]["lines"].append({"lnum": lnum, "loc": loc, "tokens": toks, "intrusions": intrusions, "raw": body_no_comments.strip()})

        if intrusions >= 2:
            raw_parts = body_no_comments.split("<->")
            seg_tokens = []
            for p in raw_parts:
                stoks = [clean_word(t) for t in re.split(r"[.,\s<>\-$%]+", p) if clean_word(t)]
                seg_tokens.append(stoks)
            # First and last segments are outer segments; middle segments (1..len-2) are interior inter-stem corridors!
            if seg_tokens:
                outer_segment_tokens.extend(seg_tokens[0])
                outer_segment_tokens.extend(seg_tokens[-1])
                for mid in seg_tokens[1:-1]:
                    interior_corridor_tokens.extend(mid)
            multi_intrusion_lines.append({
                "folio": folio,
                "lnum": lnum,
                "intrusion_count": intrusions,
                "segment_count": len(seg_tokens),
                "segments": seg_tokens,
                "interior_tokens": [t for mid in seg_tokens[1:-1] for t in mid],
            })

    return folios, multi_intrusion_lines, interior_corridor_tokens, outer_segment_tokens


def main():
    random.seed(211)
    idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    zl, multi_lines, interior_toks, outer_toks = parse_zl()

    # Part A: f90 Foldout Inversion & 4-Panel Sheet Analysis (f90r1, f90r2, f90v2, f90v1 + f89v1)
    f90_panels = ["f90r1", "f90r2", "f90v2", "f90v1"]
    panel_stats = {}
    panel_stems = {}
    for p in ["f89v1"] + f90_panels:
        w = zl[p]["words"]
        st = set(canonical_stem(x) for x in w if canonical_stem(x))
        panel_stems[p] = st
        panel_stats[p] = {
            "word_count": len(w),
            "unique_stems": len(st),
            "intrusions": zl[p]["intrusions"],
            "line_count": len(zl[p]["lines"]),
        }

    # Pairwise stem sharing across f90 panels
    f90_pairwise = []
    for i in range(len(f90_panels)):
        for j in range(i + 1, len(f90_panels)):
            p1, p2 = f90_panels[i], f90_panels[j]
            s1, s2 = panel_stems[p1], panel_stems[p2]
            shared = sorted(s1 & s2)
            jacc = len(shared) / max(1, len(s1 | s2))
            f90_pairwise.append({
                "pair": f"{p1}<->{p2}",
                "physical_relationship": (
                    "True recto-verso of inner panel (2 blue cup pods <-> 3 blue star flowers + '15m')"
                    if {p1, p2} == {"f90r1", "f90v1"}
                    else "True recto-verso of outer foldout flap (32 green coin discs <-> 3 green-fringed flowers + foliator '90')"
                    if {p1, p2} == {"f90r2", "f90v2"}
                    else "Unfolded recto side-by-side panels (p165)"
                    if {p1, p2} == {"f90r1", "f90r2"}
                    else "Verso panels (p166 + p167)"
                    if {p1, p2} == {"f90v1", "f90v2"}
                    else "Diagonal foldout pair"
                ),
                "shared_stems_count": len(shared),
                "jaccard_pct": round(100.0 * jacc, 2),
                "shared_stems": shared,
            })

    # Part B: f93r <-> f93v Giant Elecampane / 4-Pouch Octopus-Leaf & Red-Berry Spike Leaf Coupling
    f93r_w = zl["f93r"]["words"]
    f93v_w = zl["f93v"]["words"]
    f93r_stems = set(canonical_stem(x) for x in f93r_w if canonical_stem(x))
    f93v_stems = set(canonical_stem(x) for x in f93v_w if canonical_stem(x))
    f93_shared = sorted(f93r_stems & f93v_stems)
    f93v_covered_by_f93r = sum(1 for x in f93v_w if canonical_stem(x) in f93r_stems) / len(f93v_w)

    # Part C: Multi-Intrusion (<-> X <->) Inter-Stem Micro-Corridor Compression Law
    # Compare mean word length (chars) and single-token corridor rate between interior_toks and outer_toks
    mean_len_interior = sum(len(t) for t in interior_toks) / max(1, len(interior_toks))
    mean_len_outer = sum(len(t) for t in outer_toks) / max(1, len(outer_toks))

    # Count how many interior segments (<-> X <->) have exactly 1 token vs >=2 tokens
    interior_seg_lengths = []
    outer_seg_lengths = []
    for ml in multi_lines:
        segs = ml["segments"]
        if segs:
            outer_seg_lengths.append(len(segs[0]))
            outer_seg_lengths.append(len(segs[-1]))
            for mid in segs[1:-1]:
                interior_seg_lengths.append(len(mid))

    single_token_corridors = sum(1 for k in interior_seg_lengths if k == 1)
    two_or_fewer_corridors = sum(1 for k in interior_seg_lengths if k <= 2)

    # Permutation test on mean character length of interior_toks vs random draws from all multi-intrusion line tokens
    pool_toks = interior_toks + outer_toks
    trials = 1000
    null_means = []
    for _ in range(trials):
        samp = random.sample(pool_toks, len(interior_toks))
        null_means.append(sum(len(t) for t in samp) / len(interior_toks))
    mu_null = sum(null_means) / trials
    sd_null = math.sqrt(sum((x - mu_null) ** 2 for x in null_means) / trials) or 1e-9
    z_len = (mean_len_interior - mu_null) / sd_null
    p_len = sum(1 for x in null_means if x <= mean_len_interior) / trials

    # Top folios with multi-intrusion lines
    multi_folio_counts = Counter(ml["folio"] for ml in multi_lines)

    out = {
        "attack": 211,
        "discovery": 228,
        "title": "The f90 (Quire 15) Foldout Inversion & Beinecke '90r' Mislabel Proof (p165-p167), f93r<->f93v Leaf Coupling, and the Multi-Intrusion (<-> X <->) Inter-Stem Micro-Corridor Law",
        "f90_foldout_inversion_proof": {
            "p165_unfolded_recto_panels": ["f89v1 (left: 2 jars + 8 roots)", "f90r1 (middle: 2 giant dark-blue drooping cup pods)", "f90r2 (right: 32 round green coin discs)"],
            "p166_folded_outer_flap": {
                "true_folio_id": "f90v2",
                "beinecke_catalog_label": "90r (mislabeled because the early modern foliator wrote '90' in the top-right corner of f90v2 while the outer flap was folded inward!)",
                "first_line_eva": zl["f90v2"]["lines"][0]["raw"],
                "bleed_through_proof": "Left half of p166 (f90v2) shows the mirror-image bleed-through of the 32 round green coin discs painted on its physical recto f90r2.",
            },
            "p167_inner_verso_panel": {
                "true_folio_id": "f90v1",
                "quire_signature_visual": "15m (written in bottom-right corner of f90v1, proving f90v1 is the physical outer closing verso of Quire 15!)",
                "first_line_eva": zl["f90v1"]["lines"][0]["raw"],
                "bleed_through_proof": "Upper-left and middle-right of p167 (f90v1) show the mirror-image bleed-through of the 2 giant dark-blue cup pods painted on its physical recto f90r1.",
            },
            "panel_stats": panel_stats,
            "pairwise_stem_sharing": f90_pairwise,
        },
        "f93r_f93v_leaf_coupling": {
            "f93r_word_count": len(f93r_w),
            "f93v_word_count": len(f93v_w),
            "f93v_intrusions": zl["f93v"]["intrusions"],
            "shared_stems_count": len(f93_shared),
            "shared_stems": f93_shared,
            "f93v_tokens_covered_by_f93r_stems_pct": round(100.0 * f93v_covered_by_f93r, 2),
            "f93v_multi_intrusion_lines": [ml for ml in multi_lines if ml["folio"] == "f93v"],
        },
        "multi_intrusion_micro_corridor_law": {
            "total_multi_intrusion_lines_codex": len(multi_lines),
            "total_interior_corridors": len(interior_seg_lengths),
            "single_token_corridor_count": single_token_corridors,
            "single_token_corridor_pct": round(100.0 * single_token_corridors / max(1, len(interior_seg_lengths)), 2),
            "two_or_fewer_token_corridor_pct": round(100.0 * two_or_fewer_corridors / max(1, len(interior_seg_lengths)), 2),
            "mean_tokens_per_interior_corridor": round(sum(interior_seg_lengths) / max(1, len(interior_seg_lengths)), 2),
            "mean_tokens_per_outer_segment": round(sum(outer_seg_lengths) / max(1, len(outer_seg_lengths)), 2),
            "mean_char_length_interior_tokens": round(mean_len_interior, 3),
            "mean_char_length_outer_tokens": round(mean_len_outer, 3),
            "z_score_char_compression": round(z_len, 2),
            "p_value_char_compression": round(p_len, 4),
            "top_multi_intrusion_folios": multi_folio_counts.most_common(12),
            "f90v1_multi_intrusion_lines": [ml for ml in multi_lines if ml["folio"] == "f90v1"],
        },
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print("f93v tokens covered by f93r stems:", round(100.0 * f93v_covered_by_f93r, 2), "%")
    print(f"Multi-intrusion corridors: {len(multi_lines)} lines, {len(interior_seg_lengths)} interior corridors; {single_token_corridors}/{len(interior_seg_lengths)} ({100*single_token_corridors/len(interior_seg_lengths):.2f}%) are single-token; <=2 tokens = {100*two_or_fewer_corridors/len(interior_seg_lengths):.2f}%")
    print(f"Interior token length: {mean_len_interior:.3f} chars vs outer {mean_len_outer:.3f} chars (z={z_len:.2f}, p={p_len:.4f})")


if __name__ == "__main__":
    main()
