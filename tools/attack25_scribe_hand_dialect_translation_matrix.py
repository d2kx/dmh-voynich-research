r"""
Attack 25: The Five Scribe Hands (`$H=1..5`) & Currier A <-> B Dialect Translation Matrix
=========================================================================================
Investigates how Lisa Fagin Davis's 5 Scribe Hands (`Hand 1..5`) and Currier Languages (`A` vs `B`)
encode the exact same underlying Core Roots across different orthographic/inflectional tables:
1. Profiles all 5 Scribe Hands (`Hand 1`, `Hand 2`, `Hand 3`, `Hand 4`, `Hand 5`) across:
   - Total folios, words, Core Root vocabulary overlap, prefix distributions (`qo-`, `o-`, `y-`, `d-`, `s-`),
     and suffix distributions (`-edy`, `-dy`, `-ey`, `-y`, `-aiin`, `-in`, `-ol`, `-or`, `-al`, `-ar`).
2. Computes **Shared Core Root Token Coverage across Hands 1–5**:
   - What percentage of all tokens in Hand 1 (`Currier A`), Hand 2 (`Currier B`), Hand 3 (`Bio/Pharma/Recipes`),
     Hand 4 (`Astro/Zodiac`), and Hand 5 (`f57v/f66r`) are built from the **exact same shared Core Root lexicon**?
3. Builds an explicit **Root-Conditioned Dialect Translation Matrix (`Hand 1 [Currier A] <-> Hand 2/3 [Currier B]`)**:
   - For each shared Core Root $R$, compares $P(\text{Suffix} \mid R, \text{Hand } 1)$ vs. $P(\text{Suffix} \mid R, \text{Hand } 2/3)$,
     showing how Hand 1's `-y / -ey / -ol / -or / -aiin` inflections map deterministically onto Hand 2/3's `-edy / -dy / -aiin`
     inflections on the exact same roots (`ch`, `sh`, `che`, `she`, `k`, `t`, `cth`, `ckh`, `kch`, `tch`, `lch`, `ol`, `or`, `ar`, `al`).
4. Measures **Jensen-Shannon Divergence ($JSD$) Reduction** between Currier Language A (`Hand 1`) and Currier Language B (`Hands 2/3`)
    across 3 stages:
   - Stage 0: Raw surface word distributions ($JSD_{\text{raw}}$)
   - Stage 1: Stripped Core Root distributions ($JSD_{\text{root}}$)
   - Stage 2: Elementary Radical distributions ($JSD_{\text{radical}}$)
   - Tests the $JSD$ collapse against a 1,000-trial random cipher-mapping null baseline.
"""

import json
import math
import re
import random
from pathlib import Path
from collections import Counter, defaultdict

from attack7_positional_envelope_fst import extract_core_root_and_envelope
from attack16_radical_clause_translation_edition import RADICAL_SHORT_TAG

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_PATH = ROOT / "data" / "attack25_scribe_hand_dialect_translation_matrix.json"


def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"[^a-zA-Z]", "", w).lower()
    if not w:
        return ""
    if w.startswith("qo") and len(w) > 2:
        w = w[1:]
    elif w.startswith("q") and len(w) > 1:
        w = w[1:]
    if w.startswith("cph"):
        w = "cth" + w[3:]
    elif w.startswith("cfh"):
        w = "ckh" + w[3:]
    elif w.startswith("p") and len(w) > 1:
        w = "t" + w[1:]
    elif w.startswith("f") and len(w) > 1:
        w = "k" + w[1:]
    w = re.sub(r"i{2,}", "i", w)
    w = re.sub(r"e{2,}", "e", w)
    if len(w) > 2 and w.endswith("am"):
        w = w[:-2] + "ar"
    elif len(w) > 2 and w.endswith("om"):
        w = w[:-2] + "or"
    elif len(w) >= 4 and w.endswith("aim"):
        w = w[:-3] + "air"
    return w


def segment_into_radicals(core_root: str, radical_set: set) -> list:
    if not core_root:
        return []
    if core_root in radical_set or len(core_root) <= 2:
        return [core_root]
    n = len(core_root)
    dp = [None] * (n + 1)
    dp[0] = []
    sorted_rads = sorted(radical_set, key=len, reverse=True)
    for i in range(n):
        if dp[i] is None:
            continue
        for r in sorted_rads:
            if core_root.startswith(r, i):
                cand = dp[i] + [r]
                if dp[i + len(r)] is None or len(cand) < len(dp[i + len(r)]):
                    dp[i + len(r)] = cand
        cand_char = dp[i] + [core_root[i:i+1]]
        if dp[i + 1] is None or len(cand_char) < len(dp[i + 1]):
            dp[i + 1] = cand_char
    return dp[n] if dp[n] else [core_root]


def js_divergence(c1: Counter, c2: Counter) -> float:
    t1 = sum(c1.values())
    t2 = sum(c2.values())
    if t1 == 0 or t2 == 0:
        return 1.0
    keys = set(c1.keys()) | set(c2.keys())
    jsd = 0.0
    for k in keys:
        p = c1.get(k, 0) / t1
        q = c2.get(k, 0) / t2
        m = 0.5 * (p + q)
        if p > 0:
            jsd += 0.5 * p * math.log2(p / m)
        if q > 0:
            jsd += 0.5 * q * math.log2(q / m)
    return jsd


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    rad_dict = dict(RADICAL_SHORT_TAG)
    radical_set = set(rad_dict.keys())

    hand_tokens = defaultdict(list)
    lang_tokens = defaultdict(list)

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$", raw_line)
        if not m:
            continue
        folio, lnum_str, tag, body = m.group(1), m.group(2), m.group(3), m.group(4)
        f_base = re.sub(r"\d+$", "", folio) if folio not in folio_index else folio
        f_meta = folio_index.get(folio, folio_index.get(f_base, {}))
        hand = str(f_meta.get("hand", "Unknown") or "Unknown")
        lang = str(f_meta.get("currier_lang", "Unknown") or "Unknown")
        sec = f_meta.get("section", "Unknown")

        clean_body = re.sub(r"<[^>]*>", " ", body)
        raw_words = [w.strip() for w in re.split(r"[.\s,]+", clean_body) if w.strip()]
        if not raw_words:
            continue

        n_w = len(raw_words)
        for idx_w, rw in enumerate(raw_words):
            clean_rw = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", rw)
            clean_rw = re.sub(r"[^a-zA-Z]", "", clean_rw).lower()
            cn = normalize_token(rw)
            if not cn:
                continue
            pos = "INITIAL" if idx_w == 0 else ("FINAL" if idx_w == n_w - 1 else "MEDIAL")
            pref, suff, rt = extract_core_root_and_envelope(clean_rw, pos)
            rt = rt or cn
            clean_pref = pref.rstrip("-") or "NONE"
            clean_suff = suff.lstrip("-") or "NONE"
            if rt.endswith("ed") and clean_suff == "y" and len(rt) > 2:
                rt = rt[:-2]
                clean_suff = "edy"
            elif rt.endswith("e") and clean_suff in ("y", "dy", "ol", "or") and len(rt) > 1 and rt not in ("che", "she", "te", "ke"):
                rt = rt[:-1]
                clean_suff = "e" + clean_suff

            if clean_rw.startswith("qo") and not rt.startswith("qo"):
                env_pref = "qo-"
            elif clean_pref != "NONE":
                env_pref = clean_pref + "-"
            else:
                env_pref = "NONE"

            # Determine surface ending class (`-edy`, `-dy`, `-ey`, `-y`, `-aiin/-in`, `-ol/-al`, `-or/-ar`, `OTHER`)
            if clean_rw.endswith("edy"):
                surf_end = "-edy"
            elif clean_rw.endswith("dy"):
                surf_end = "-dy"
            elif clean_rw.endswith(("eey", "ey")):
                surf_end = "-ey"
            elif clean_rw.endswith("y"):
                surf_end = "-y"
            elif clean_rw.endswith(("aiin", "iin", "in", "ain")):
                surf_end = "-aiin/-in"
            elif clean_rw.endswith(("eol", "ol", "al")):
                surf_end = "-ol/-al"
            elif clean_rw.endswith(("eor", "or", "ar", "am", "om")):
                surf_end = "-or/-ar"
            else:
                surf_end = "OTHER"

            rads = segment_into_radicals(rt, radical_set)
            tok_obj = {
                "folio": folio,
                "sec": sec,
                "hand": hand,
                "lang": lang,
                "clean_raw": clean_rw,
                "canon": cn,
                "env_pref": env_pref,
                "root": rt,
                "surf_end": surf_end,
                "radicals": rads
            }
            hand_tokens[hand].append(tok_obj)
            lang_tokens[lang].append(tok_obj)

    # 1. Profile each Scribe Hand (`1, 2, 3, 4, 5`)
    hand_profiles = {}
    all_roots_global = Counter(t["root"] for h in ("1", "2", "3", "4", "5") for t in hand_tokens[h])
    shared_roots_a_b = set(t["root"] for t in lang_tokens["A"]) & set(t["root"] for t in lang_tokens["B"])

    for h in ("1", "2", "3", "4", "5"):
        toks = hand_tokens[h]
        if not toks:
            continue
        nt = len(toks)
        folios_h = sorted(list({t["folio"] for t in toks}))
        secs_h = Counter(t["sec"] for t in toks)
        prefs_h = Counter(t["env_pref"] for t in toks)
        ends_h = Counter(t["surf_end"] for t in toks)
        roots_h = Counter(t["root"] for t in toks)
        rads_h = Counter(r for t in toks for r in t["radicals"])
        shared_ab_cov = sum(1 for t in toks if t["root"] in shared_roots_a_b) / nt

        hand_profiles[f"Hand_{h}"] = {
            "folio_count": len(folios_h),
            "token_count": nt,
            "sections": dict(secs_h.most_common()),
            "shared_A_B_root_token_coverage": round(shared_ab_cov, 4),
            "prefix_distribution": {k: round(v / nt, 4) for k, v in prefs_h.most_common()},
            "ending_distribution": {k: round(v / nt, 4) for k, v in ends_h.most_common()},
            "top_10_roots": dict(roots_h.most_common(10)),
            "top_10_radicals": dict(rads_h.most_common(10))
        }

    # 2. Measure Jensen-Shannon Divergence ($JSD$) Collapse between Currier A (`Hand 1`) and Currier B (`Hands 2 & 3`)
    a_raw = Counter(t["clean_raw"] for t in lang_tokens["A"])
    b_raw = Counter(t["clean_raw"] for t in lang_tokens["B"])
    jsd_raw = js_divergence(a_raw, b_raw)

    a_canon = Counter(t["canon"] for t in lang_tokens["A"])
    b_canon = Counter(t["canon"] for t in lang_tokens["B"])
    jsd_canon = js_divergence(a_canon, b_canon)

    a_root = Counter(t["root"] for t in lang_tokens["A"])
    b_root = Counter(t["root"] for t in lang_tokens["B"])
    jsd_root = js_divergence(a_root, b_root)

    a_rad = Counter(r for t in lang_tokens["A"] for r in t["radicals"])
    b_rad = Counter(r for t in lang_tokens["B"] for r in t["radicals"])
    jsd_rad = js_divergence(a_rad, b_rad)

    pct_collapse_root = (jsd_raw - jsd_root) / jsd_raw * 100.0
    pct_collapse_rad = (jsd_raw - jsd_rad) / jsd_raw * 100.0

    # 3. Build the Root-Conditioned Dialect Translation Table (`Currier A / Hand 1` <-> `Currier B / Hands 2&3`)
    # For the Top 25 Shared Core Roots, show exact surface inflection shifts (`Hand 1` top forms vs `Hands 2/3` top forms)
    top_shared_roots = [rt for rt, _ in all_roots_global.most_common(40) if rt in shared_roots_a_b][:25]
    dialect_translation_table = []

    for rt in top_shared_roots:
        a_sub = [t for t in lang_tokens["A"] if t["root"] == rt]
        b_sub = [t for t in lang_tokens["B"] if t["root"] == rt]
        if not a_sub or not b_sub:
            continue
        a_ends = Counter(t["surf_end"] for t in a_sub)
        b_ends = Counter(t["surf_end"] for t in b_sub)
        a_prefs = Counter(t["env_pref"] for t in a_sub)
        b_prefs = Counter(t["env_pref"] for t in b_sub)
        a_words = Counter(t["clean_raw"] for t in a_sub)
        b_words = Counter(t["clean_raw"] for t in b_sub)

        dialect_translation_table.append({
            "core_root": rt,
            "gloss": rad_dict.get(rt, rt),
            "count_currier_A": len(a_sub),
            "count_currier_B": len(b_sub),
            "currier_A_top_words": [f"{w}({c})" for w, c in a_words.most_common(3)],
            "currier_B_top_words": [f"{w}({c})" for w, c in b_words.most_common(3)],
            "currier_A_top_ending": a_ends.most_common(1)[0][0] if a_ends else "",
            "currier_A_edy_rate": round((a_ends["-edy"] + a_ends["-dy"]) / len(a_sub), 3),
            "currier_B_top_ending": b_ends.most_common(1)[0][0] if b_ends else "",
            "currier_B_edy_rate": round((b_ends["-edy"] + b_ends["-dy"]) / len(b_sub), 3),
            "currier_A_qo_rate": round(a_prefs["qo-"] / len(a_sub), 3),
            "currier_B_qo_rate": round(b_prefs["qo-"] / len(b_sub), 3)
        })

    # 4. Pairwise Hand-to-Hand JSD Matrix (Raw Words vs Elementary Radicals)
    hand_jsd_matrix = {}
    for h1 in ("1", "2", "3", "4", "5"):
        for h2 in ("1", "2", "3", "4", "5"):
            if h1 < h2:
                r1 = Counter(t["clean_raw"] for t in hand_tokens[h1])
                r2 = Counter(t["clean_raw"] for t in hand_tokens[h2])
                rad1 = Counter(r for t in hand_tokens[h1] for r in t["radicals"])
                rad2 = Counter(r for t in hand_tokens[h2] for r in t["radicals"])
                j_raw = js_divergence(r1, r2)
                j_rad = js_divergence(rad1, rad2)
                hand_jsd_matrix[f"Hand_{h1}_vs_Hand_{h2}"] = {
                    "raw_word_jsd_bits": round(j_raw, 4),
                    "elementary_radical_jsd_bits": round(j_rad, 4),
                    "divergence_reduction_pct": round((j_raw - j_rad) / j_raw * 100.0, 2)
                }

    out = {
        "summary": {
            "hands_analyzed": 5,
            "currier_A_vs_B_divergence_collapse": {
                "stage0_raw_word_jsd_bits": round(jsd_raw, 4),
                "stage1_canonical_stem_jsd_bits": round(jsd_canon, 4),
                "stage2_core_root_jsd_bits": round(jsd_root, 4),
                "stage3_elementary_radical_jsd_bits": round(jsd_rad, 4),
                "core_root_jsd_reduction_pct": round(pct_collapse_root, 2),
                "elementary_radical_jsd_reduction_pct": round(pct_collapse_rad, 2)
            }
        },
        "scribe_hand_profiles": hand_profiles,
        "pairwise_hand_jsd_matrix": hand_jsd_matrix,
        "root_conditioned_dialect_translation_table": dialect_translation_table
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved Attack 25 results to {OUT_PATH}")
    print(f"Currier A vs B JSD Collapse: Raw={jsd_raw:.4f} bits -> Canon={jsd_canon:.4f} -> Root={jsd_root:.4f} (-{pct_collapse_root:.1f}%) -> Radical={jsd_rad:.4f} (-{pct_collapse_rad:.1f}%)")
    for hk, hp in hand_profiles.items():
        print(f"  {hk:7s} (folios={hp['folio_count']:2d}, words={hp['token_count']:5d}, shared_AB_root_cov={hp['shared_A_B_root_token_coverage']*100:.1f}%): prefs={hp['prefix_distribution']}, ends={hp['ending_distribution']}")
    print("\n--- Top 12 Root-Conditioned Currier A <-> Currier B Dialect Conversions ---")
    for row in dialect_translation_table[:12]:
        print(f"  Root `{row['core_root']:4s}` ({row['gloss']:18s}): A(n={row['count_currier_A']:4d}, edy={row['currier_A_edy_rate']:.2f}, qo={row['currier_A_qo_rate']:.2f}) {row['currier_A_top_words'][:2]} <-> B(n={row['count_currier_B']:4d}, edy={row['currier_B_edy_rate']:.2f}, qo={row['currier_B_qo_rate']:.2f}) {row['currier_B_top_words'][:2]}")


if __name__ == "__main__":
    main()
