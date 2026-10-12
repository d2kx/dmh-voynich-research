#!/usr/bin/env python3
"""
Attack 169 (Discovery 186): The 12 Visual Twin Plant Pairs ("Same Plant As..." Atlas)
Across Herbal Monographs (H) and Pharmaceutical Dissected Root/Jar Registers (P).

Tests all 12 paleographically & visually documented twin plant pairs noted by
Petersen, Friedman (FSG), Stolfi, and Landini (GL) in data/ZL3b-n.txt, comparing:
  1. Exact whole-word overlap between the Herbal monograph and its Pharmaceutical
     twin folio & specific register paragraph/labels.
  2. Canonical root-stem overlap (norm_word) between the Herbal monograph and its
     Pharmaceutical twin folio & specific register.
  3. A 1,000-trial random permutation test pairing the 12 Herbal monographs with
     random Pharmaceutical folios/registers to measure lexical & stem lift.
  4. Morphological shift from Herbal plant monograph (nominal o- / d- descriptions)
     to Pharmaceutical compounding register (qo- / ch- / -edy / @Lc jar recipes).
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ZL_PATH = Path("data/ZL3b-n.txt")
OUT_PATH = Path("data/attack169_visual_twin_plants_herbal_to_pharma.json")


def clean_word(w: str) -> str:
    w = re.sub(r"<!.*?>", "", w)
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{([^}]+)\}", r"\1", w)
    w = re.sub(r"@\d+;", "", w)
    w = re.sub(r"[^a-zA-Z]", "", w)
    return w.lower().strip()


def norm_stem(w: str) -> str:
    w = clean_word(w)
    if not w:
        return ""
    w = w.replace("ch", "C").replace("sh", "S").replace("ckh", "K").replace("cth", "T").replace("cph", "P").replace("cfh", "F")
    w = re.sub(r"i+", "i", w)
    w = re.sub(r"e+", "e", w)
    for p in ("qo", "o", "y", "d", "s"):
        if w.startswith(p) and len(w) > len(p) + 1:
            w = w[len(p):]
            break
    for s in ("aiin", "ain", "iin", "in", "edy", "ody", "ey", "dy", "ol", "or", "al", "ar", "am", "y", "m", "s"):
        if w.endswith(s) and len(w) > len(s) + 1:
            w = w[:-len(s)]
            break
    w = w.replace("C", "ch").replace("S", "sh").replace("K", "kh").replace("T", "th").replace("P", "ph").replace("F", "fh")
    return w


def parse_zl():
    lines = ZL_PATH.read_text(encoding="utf-8").splitlines()
    folio_tokens = defaultdict(list)
    folio_lines = defaultdict(list)
    folio_labels = defaultdict(list)
    cur_folio = ""
    for line in lines:
        m_f = re.match(r"^<(f[0-9]+[rv][0-9]*)>", line)
        if m_f:
            cur_folio = m_f.group(1)
            continue
        if not cur_folio or line.startswith("#"):
            continue
        m_l = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s+(.*)$", line)
        if not m_l:
            continue
        fol, lno, ltype, text = m_l.groups()
        text_clean = re.sub(r"<!.*?>", "", text)
        text_clean = text_clean.replace("<%>", "").replace("<$>", "").replace("<->", ".")
        raw_words = [clean_word(t) for t in re.split(r"[.,\s]+", text_clean)]
        words = [w for w in raw_words if w]
        if not words:
            continue
        folio_lines[fol].append({"line_no": lno, "locus_type": ltype, "words": words})
        folio_tokens[fol].extend(words)
        if "L" in ltype:
            folio_labels[fol].append({"line_no": lno, "locus_type": ltype, "words": words})
    return folio_tokens, folio_lines, folio_labels


VISUAL_TWIN_PAIRS = [
    {
        "pair_id": "TWIN-01",
        "herbal_folio": "f1v",
        "herbal_name": "Belladonna / Solanum nigrum (Deadly Nightshade)",
        "pharma_folio": "f102r1",
        "pharma_locus": "f102r1[3,2]",
        "pharma_register_lines": ["12", "13", "14", "15", "16", "17"],
        "authority": "Petersen, Stolfi",
        "visual_feature": "Arched dark berry cluster, ovate leaves, and curved brown taproot",
    },
    {
        "pair_id": "TWIN-02",
        "herbal_folio": "f18v",
        "herbal_name": "broad-crowned palmate rosette herb",
        "pharma_folio": "f102r2",
        "pharma_locus": "f102r2[3,1]",
        "pharma_register_lines": ["13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
        "authority": "FSG, Stolfi",
        "visual_feature": "Segmented creeping rhizome with claw-like rootlets (koldarod)",
    },
    {
        "pair_id": "TWIN-03",
        "herbal_folio": "f19r",
        "herbal_name": "Slender-leaved branching herb with twin root",
        "pharma_folio": "f102v1",
        "pharma_locus": "f102v1[2,2]",
        "pharma_register_lines": ["16", "17", "18", "19", "20", "21", "22", "23", "24"],
        "authority": "Stolfi, Petersen",
        "visual_feature": "Forked root stock with serrated collar and narrow opposite leaves (loralody)",
    },
    {
        "pair_id": "TWIN-04",
        "herbal_folio": "f23r",
        "herbal_name": "Creeping Dragon-Root / Bryonia herb",
        "pharma_folio": "f102r2",
        "pharma_locus": "f102r2[3,1]",
        "pharma_register_lines": ["13", "14", "15", "16", "17", "18", "19", "20", "21", "22"],
        "authority": "FSG, Landini (GL)",
        "visual_feature": "Horizontal dragon-clawed rhizome with vertical shoots (koldarod / odalydary)",
    },
    {
        "pair_id": "TWIN-05",
        "herbal_folio": "f32v",
        "herbal_name": "Campanula / Glockenblume (Bellflower)",
        "pharma_folio": "f102r2",
        "pharma_locus": "f102r2[1,2]",
        "pharma_register_lines": ["1", "2", "3", "4", "5", "6"],
        "authority": "FSG, Stolfi",
        "visual_feature": "Blue bell-shaped flower, white calyx buds, green star-shaped leaves, and curved brown collar root",
    },
    {
        "pair_id": "TWIN-06",
        "herbal_folio": "f37v",
        "herbal_name": "Trefoil / Spade-Leaved Marsh Herb",
        "pharma_folio": "f102r1",
        "pharma_locus": "f102r1[3,1]",
        "pharma_register_lines": ["12", "13", "14", "15", "16", "17"],
        "authority": "Stolfi",
        "visual_feature": "Crimson-orange branching tuber with twin cordate/ovate basal leaves (ddardsh)",
    },
    {
        "pair_id": "TWIN-07",
        "herbal_folio": "f39r",
        "herbal_name": "Crocus / Plumed Calyx Herb",
        "pharma_folio": "f95r2",
        "pharma_locus": "f95r2[full]",
        "pharma_register_lines": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
        "authority": "Stolfi, Zandbergen",
        "visual_feature": "Three-lobed bulbous root and对称 serrated leaves with central flower spike",
    },
    {
        "pair_id": "TWIN-08",
        "herbal_folio": "f47v",
        "herbal_name": "Doronicum Pardalianches / Gemswurz (Leopard's Bane)",
        "pharma_folio": "f102r2",
        "pharma_locus": "f102r2[1,1]",
        "pharma_register_lines": ["1", "2", "3", "4", "5", "6"],
        "authority": "Petersen, Holm",
        "visual_feature": "Octopus-like splayed brown root with red collar teeth and broad ovate green leaf (kodaiig)",
    },
    {
        "pair_id": "TWIN-09",
        "herbal_folio": "f48r",
        "herbal_name": "Paired Basal-Leaf Herb with Whiskered Bulb",
        "pharma_folio": "f89v2",
        "pharma_locus": "f89v2[3,4]",
        "pharma_register_lines": ["15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "27", "28"],
        "authority": "Stolfi",
        "visual_feature": "Bulbous root with radiating whiskers and twin arching basal leaves (daseky)",
    },
    {
        "pair_id": "TWIN-10",
        "herbal_folio": "f48v",
        "herbal_name": "Opposite-Leaved Spike Herb with Ringed Root",
        "pharma_folio": "f89v1",
        "pharma_locus": "f89v1[1,4]",
        "pharma_register_lines": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
        "authority": "Stolfi",
        "visual_feature": "Ringed vertical taproot with symmetrical opposite leaf pairs (darshody)",
    },
    {
        "pair_id": "TWIN-11",
        "herbal_folio": "f90v2",
        "herbal_name": "Osmunda regalis (Royal Fern)",
        "pharma_folio": "f100r",
        "pharma_locus": "f100r[1,3]",
        "pharma_register_lines": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"],
        "authority": "Stolfi",
        "visual_feature": "Plumed fern frond with curled fiddlehead tips and bulbous rhizome (otear)",
    },
    {
        "pair_id": "TWIN-12",
        "herbal_folio": "f96v",
        "herbal_name": "Smilax tracheia / Chenopodium",
        "pharma_folio": "f99r",
        "pharma_locus": "f99r[4,1]",
        "pharma_register_lines": ["41", "42", "43", "44", "45", "46", "47", "48", "49", "50"],
        "authority": "Landini (GL)",
        "visual_feature": "Trailing vine with spade-shaped leaves and knotted rootstock (tolsasy)",
    },
]


def main():
    folio_tokens, folio_lines, folio_labels = parse_zl()

    pair_results = []
    total_exact_shared_types = 0
    total_stem_shared_types = 0
    reg_stem_hits = 0

    for p in VISUAL_TWIN_PAIRS:
        h_fol = p["herbal_folio"]
        p_fol = p["pharma_folio"]
        h_words = folio_tokens[h_fol]
        p_words = folio_tokens[p_fol]

        # Extract specific register words on the pharma folio
        reg_set = set(p["pharma_register_lines"])
        reg_words = []
        reg_labels = []
        for lobj in folio_lines[p_fol]:
            if lobj["line_no"] in reg_set:
                reg_words.extend(lobj["words"])
                if "L" in lobj["locus_type"]:
                    reg_labels.extend(lobj["words"])

        h_vocab = set(h_words)
        p_vocab = set(p_words)
        reg_vocab = set(reg_words)

        h_stems = {norm_stem(w) for w in h_words if len(norm_stem(w)) >= 2}
        p_stems = {norm_stem(w) for w in p_words if len(norm_stem(w)) >= 2}
        reg_stems = {norm_stem(w) for w in reg_words if len(norm_stem(w)) >= 2}

        exact_folio_shared = sorted(h_vocab & p_vocab)
        exact_reg_shared = sorted(h_vocab & reg_vocab)
        stem_folio_shared = sorted(h_stems & p_stems)
        stem_reg_shared = sorted(h_stems & reg_stems)

        # Map each shared stem to concrete surface word pairs (Herbal -> Pharma Register)
        concrete_bridges = []
        for st in stem_reg_shared:
            hw_list = sorted({w for w in h_words if norm_stem(w) == st})
            rw_list = sorted({w for w in reg_words if norm_stem(w) == st})
            concrete_bridges.append({"stem": st, "herbal_words": hw_list[:4], "pharma_reg_words": rw_list[:4]})

        total_exact_shared_types += len(exact_folio_shared)
        total_stem_shared_types += len(stem_folio_shared)
        if stem_reg_shared:
            reg_stem_hits += 1

        # Morphological profile shift: Herbal vs Pharma Register
        h_qo = sum(1 for w in h_words if w.startswith("qo")) / max(1, len(h_words))
        p_qo = sum(1 for w in reg_words if w.startswith("qo")) / max(1, len(reg_words))
        h_o = sum(1 for w in h_words if w.startswith("o") and not w.startswith("qo")) / max(1, len(h_words))
        p_o = sum(1 for w in reg_words if w.startswith("o") and not w.startswith("qo")) / max(1, len(reg_words))

        pair_results.append({
            **p,
            "herbal_word_count": len(h_words),
            "pharma_folio_word_count": len(p_words),
            "pharma_register_word_count": len(reg_words),
            "pharma_register_labels": reg_labels,
            "exact_folio_shared_words": exact_folio_shared,
            "exact_register_shared_words": exact_reg_shared,
            "stem_folio_shared_count": len(stem_folio_shared),
            "stem_register_shared_count": len(stem_reg_shared),
            "stem_register_shared": stem_reg_shared,
            "concrete_stem_bridges": concrete_bridges[:10],
            "herbal_qo_rate": round(h_qo * 100, 2),
            "pharma_reg_qo_rate": round(p_qo * 100, 2),
            "herbal_o_rate": round(h_o * 100, 2),
            "pharma_reg_o_rate": round(p_o * 100, 2),
        })

    # morphological summary across all 12 pairs
    mean_h_qo = sum(r["herbal_qo_rate"] for r in pair_results) / len(pair_results)
    mean_p_qo = sum(r["pharma_reg_qo_rate"] for r in pair_results) / len(pair_results)
    exact_pair_hit_rate = sum(1 for r in pair_results if r["exact_folio_shared_words"]) / len(pair_results)
    reg_exact_hit_rate = sum(1 for r in pair_results if r["exact_register_shared_words"]) / len(pair_results)
    reg_stem_hit_rate = reg_stem_hits / len(pair_results)

    # Compute folio document frequency (DF) for every word and stem across all folios
    word_df = Counter()
    stem_df = Counter()
    total_folios = len(folio_tokens)
    for fol, wlist in folio_tokens.items():
        for w in set(wlist):
            word_df[w] += 1
        for st in {norm_stem(w) for w in wlist if len(norm_stem(w)) >= 2}:
            stem_df[st] += 1

    def rare_word_idf_score(h_fol_words, reg_words_list):
        shared = set(h_fol_words) & set(reg_words_list)
        # Sum IDF^2 for words appearing in <= 45 folios (filtering out ubiquitous function words daiin/chol/or)
        return sum((math.log(total_folios / max(1, word_df[w]))) ** 2 for w in shared if word_df[w] <= 45)

    obs_rare_idf = 0.0
    for idx, p in enumerate(VISUAL_TWIN_PAIRS):
        h_words = folio_tokens[p["herbal_folio"]]
        p_fol = p["pharma_folio"]
        reg_set = set(p["pharma_register_lines"])
        reg_words = [w for lobj in folio_lines[p_fol] if lobj["line_no"] in reg_set for w in lobj["words"]]
        rare_shared = sorted(
            [w for w in (set(h_words) & set(reg_words)) if word_df[w] <= 45],
            key=lambda x: word_df[x],
        )
        pair_results[idx]["rare_diagnostic_register_words"] = [
            {"word": w, "manuscript_folio_df": word_df[w]} for w in rare_shared
        ]
        obs_rare_idf += rare_word_idf_score(h_words, reg_words)

    # Permutation baseline: compare the 12 Pharma registers against random Currier-A/B Herbal folios
    all_herbal_folios = [f for f in folio_tokens if re.match(r"^f([1-9]|[1-5][0-9]|6[0-6])[rv]$", f)]
    rng = random.Random(169)
    null_rare_idf_totals = []
    for _ in range(1000):
        tot_idf = 0.0
        for p in VISUAL_TWIN_PAIRS:
            rand_h = rng.choice(all_herbal_folios)
            p_fol = p["pharma_folio"]
            reg_set = set(p["pharma_register_lines"])
            reg_words = [w for lobj in folio_lines[p_fol] if lobj["line_no"] in reg_set for w in lobj["words"]]
            tot_idf += rare_word_idf_score(folio_tokens[rand_h], reg_words)
        null_rare_idf_totals.append(tot_idf)

    obs_reg_stem_total = sum(r["stem_register_shared_count"] for r in pair_results)
    null_mean = sum(null_rare_idf_totals) / len(null_rare_idf_totals)
    null_sd = math.sqrt(sum((x - null_mean) ** 2 for x in null_rare_idf_totals) / len(null_rare_idf_totals)) or 1.0
    z_score = (obs_rare_idf - null_mean) / null_sd

    out = {
        "attack": "Attack 169",
        "discovery": "Discovery 186",
        "title": "The 12 Visual Twin Plant Pairs (Herbal-to-Pharmaceutical Specimen Concordance Atlas)",
        "summary": {
            "total_visual_twin_pairs": len(pair_results),
            "folio_level_exact_word_pair_hit_rate_pct": round(exact_pair_hit_rate * 100, 2),
            "register_level_exact_word_pair_hit_rate_pct": round(reg_exact_hit_rate * 100, 2),
            "register_level_stem_pair_hit_rate_pct": round(reg_stem_hit_rate * 100, 2),
            "total_exact_folio_shared_word_instances": total_exact_shared_types,
            "total_stem_folio_shared_instances": total_stem_shared_types,
            "observed_register_shared_stems": obs_reg_stem_total,
            "observed_rare_word_idf_score": round(obs_rare_idf, 2),
            "null_rare_word_idf_mean": round(null_mean, 2),
            "null_rare_word_idf_sd": round(null_sd, 2),
            "rare_word_specificity_z_score": round(z_score, 2),
            "mean_herbal_qo_active_verb_rate_pct": round(mean_h_qo, 2),
            "mean_pharma_register_qo_active_verb_rate_pct": round(mean_p_qo, 2),
            "pharma_vs_herbal_qo_verb_surge_ratio": round(mean_p_qo / max(0.01, mean_h_qo), 2),
        },
        "twin_pairs": pair_results,
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {OUT_PATH}")
    print("Summary:", json.dumps(out["summary"], indent=2))
    for r in pair_results:
        print(
            f"  {r['pair_id']}: {r['herbal_folio']} ({r['herbal_name'][:28]}) <-> {r['pharma_locus']} | "
            f"Exact Folio={len(r['exact_folio_shared_words'])} ({r['exact_folio_shared_words'][:5]}), "
            f"Exact Reg={len(r['exact_register_shared_words'])} ({r['exact_register_shared_words'][:5]}), "
            f"Stem Reg={r['stem_register_shared_count']} ({r['stem_register_shared'][:6]}) | "
            f"qo: H={r['herbal_qo_rate']}% -> P_reg={r['pharma_reg_qo_rate']}%"
        )


if __name__ == "__main__":
    main()
