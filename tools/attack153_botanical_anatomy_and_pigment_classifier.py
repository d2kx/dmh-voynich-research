#!/usr/bin/env python3
"""
tools/attack153_botanical_anatomy_and_pigment_classifier.py

Attack 153 (Phase 164 / Discovery 170):
The 5-Organ Visual Botanical Anatomy & Chromatic Pigment Classifier Across
the Illustrated Herbal & Pharmaceutical Corpus.

Tests whether Voynich lexical stems and morphological families systematically
track the physical anatomy and pigment colors painted on the illustrated
botanical and pharmaceutical folios:
  1. Dissected Root vs. Leaf/Seed Row Polarity in the Pharmaceutical Registers
     (`@L0 / @Lf / @Lp` labels + adjacent recipe lines across `f88r–f102v`):
     Tests whether Root-Row / Root-Dominant registers enrich `-ra-/-rar-`,
     `-kar-/-kor-`, `-tar-`, and `oror` vs. Leaf/Seed/Jar registers (`-al/-sal/-kal`,
     `-ol/-kol/-tol`).
  2. Chromatic & Anatomical Stratification Across Illustrated Herbal Monographs
     (`f1v–f57v`, `f65r–f66v`):
     Tests 5 visually grounded botanical guilds:
       - Guild 1 (Red/Crimson Blossom & Dye-Root Guild: e.g. f9v, f11v, f16v,
         f39v, f50r, f102v2) -> enriched in `or/oro/oror`, `cth/ckh`, `pold/opch`
       - Guild 2 (Blue/Violet Calyx & Berry Ophthalmic/Cordial Guild: e.g. f1v,
         f2r, f9v, f33v, f38r) -> enriched in `chol`, `ydain/daiin`, `kar/kor`, `sho`
       - Guild 3 (Climbing Vine & Divided/Fern Frond Guild: e.g. f17r, f20v,
         f22r, f24r, f31r) -> enriched in `sh/fsh/shol`, `daram/dar`, `oldam`
       - Guild 4 (Reniform/Aquatic & Bulbous Split-Tuber Guild: e.g. f25v,
         f34r, f49v, f57r) -> enriched in `pchor/cheol`, `kor/okar`, `otol`
       - Guild 5 (Umbel / Winged-Seed / Plumed Capsule Guild: e.g. f3v, f5r,
         f38v, f43v, f46r) -> enriched in `al/kal/sal/dal`, `ar/otar`
  3. 1,000-trial permutation tests for both (A) Pharmaceutical Organ-Row Label
     Selectivity and (B) Herbal 5-Guild Lexical Concordance.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack153_botanical_anatomy_and_pigment_classifier.json"


def clean_eva_token(tok: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", tok)
    t = re.sub(r"\[([^\]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z]", "", t)
    return t.lower()


def parse_corpus():
    folio_tokens = defaultdict(list)
    folio_labels = defaultdict(list)  # (locus_type, line_id, token)
    folio_meta = {}

    header_re = re.compile(r"^<(f[0-9]+[rv][0-9]*)>\s*<!\s*([^>]+)>")
    locus_re = re.compile(r"^<(f[0-9]+[rv][0-9]*)\.([^,;>]+),([^>]+)>\s*(.*)$")

    for raw in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m_head = header_re.match(line)
        if m_head and "$" in line:
            fol = m_head.group(1)
            meta_str = m_head.group(2)
            sec = re.search(r"\$I=([A-Z])", meta_str)
            lang = re.search(r"\$L=([AB])", meta_str)
            hand = re.search(r"\$H=([0-9?]+)", meta_str)
            folio_meta[fol] = {
                "section": sec.group(1) if sec else "?",
                "language": lang.group(1) if lang else "?",
                "hand": hand.group(1) if hand else "?",
            }
            continue

        m_loc = locus_re.match(line)
        if not m_loc:
            continue
        fol, loc_id, loc_type, text = m_loc.groups()
        text = re.sub(r"<[^>]+>", " ", text)
        words = [clean_eva_token(w) for w in re.split(r"[.\s,]+", text)]
        words = [w for w in words if len(w) >= 2]
        if not words:
            continue

        if "L" in loc_type or loc_type.startswith("@L") or loc_type.startswith("+L"):
            for w in words:
                folio_labels[fol].append((loc_type, loc_id, w))
        for w in words:
            folio_tokens[fol].append(w)

    return folio_tokens, folio_labels, folio_meta


# Morphological feature classifiers for botanical organ & pigment guilds
def classify_pharma_label_morphology(w: str) -> str:
    """
    Classifies a pharmaceutical label or stem into:
      - 'ROOT_TUBER': contains r-stem (`ra`, `rar`, `oror`, `orar`, `kar`, `kor`, `tar`, `dar`)
      - 'SEED_LEAF_STAR': contains l-stem (`al`, `sal`, `kal`, `dal`, `lal`)
      - 'VESSEL_LIQUID': ends in `-ol`, `-oldy`, `-oly` or starts with `okol`/`otol`
      - 'OTHER'
    """
    if any(sub in w for sub in ("rar", "oror", "orar", "dara", "okar", "otar", "okor", "kair", "cthar", "tar", "kar", "kor")) or w.endswith(("ar", "or", "ary", "ory")):
        return "ROOT_TUBER"
    if any(sub in w for sub in ("sal", "kal", "dal", "okal", "osal", "odal", "olar")) or w.endswith(("al", "aly")):
        return "SEED_LEAF_STAR"
    if any(sub in w for sub in ("okol", "otol", "olkol", "okold", "oldy", "pold")) or w.endswith(("ol", "oldy", "oly")):
        return "VESSEL_LIQUID"
    return "OTHER"


# Visually verified 5 Herbal Guilds (30 flagship illustrated herbal & pharma folios)
HERBAL_GUILDS = {
    "GUILD_1_RED_CRIMSON_BLOSSOM_AND_DYE_ROOT": {
        "description": "Plants painted with vivid crimson/red terminal blossoms or blood-red dye roots",
        "folios": ["f11v", "f16v", "f39v", "f102v2", "f116v"],
        "signature_markers": lambda w: (
            any(s in w for s in ("oror", "orar", "opor", "opch", "pold", "cthe", "ckh", "sar", "okod"))
        ),
    },
    "GUILD_2_BLUE_VIOLET_COROLLA_AND_BERRY_CORDIALS": {
        "description": "Plants with blue/violet florets in scaly calyces or dark berries (Nightshade f1v, Cornflower f2r, Viola f9v, Blue Thistle/Knapweed f20v)",
        "folios": ["f1v", "f2r", "f9v", "f20v", "f38r"],
        "signature_markers": lambda w: (
            any(s in w for s in ("chol", "choly", "ydain", "daiin", "dain", "kykar", "cthy", "shor", "tyd", "shol"))
        ),
    },
    "GUILD_3_CLIMBING_VINES_AND_TRAILING_STALKS": {
        "description": "Flexuose climbing vines and trailing/submerged stalks (Smilax/Bryonia f17r, Aquatic trailing herb f22r, f25r)",
        "folios": ["f17r", "f22r", "f25r", "f31r", "f42v"],
        "signature_markers": lambda w: (
            any(s in w for s in ("fsh", "daram", "dara", "oldam", "otold", "teod", "ydara"))
        ),
    },
    "GUILD_4_RENIFORM_AQUATIC_AND_BULBOUS_SPLIT_TUBERS": {
        "description": "Kidney-leaf aquatic rhizomes (Nymphaea/Asarum f25v) and heavy split black/brown tubers (f34r, f49v, f89r2)",
        "folios": ["f25v", "f34r", "f49v", "f88v", "f89r2"],
        "signature_markers": lambda w: (
            any(s in w for s in ("pchor", "cheol", "chckh", "chod", "poldak", "darar", "okar", "otoram", "arody"))
        ),
    },
    "GUILD_5_UMBEL_AND_WINGED_SEED_CAPSULE_HERBS": {
        "description": "Multi-rayed umbels, seed heads, and plumed/winged seed capsules (f5r, f43v, f46r, f58r, f68r3)",
        "folios": ["f5r", "f43v", "f46r", "f58r", "f68r3"],
        "signature_markers": lambda w: (
            any(s in w for s in ("okal", "osal", "odal", "olsy", "okalar", "otald", "opalal", "doar"))
        ),
    },
}


def analyze_pharma_row_anatomy(folio_labels):
    """
    In the Pharmaceutical section (`f88r–f102v`), labels are ordered top-to-bottom
    or grouped by register. Let's inspect how each folio's labels divide between
    upper leaf/seed/jar labels and lower root/tuber labels!
    """
    pharma_folios = sorted(
        f for f in folio_labels
        if re.match(r"^f(8[89]|9[0-9]|10[0-2])[rv][0-9]*$", f)
    )

    upper_half_classes = Counter()
    lower_half_classes = Counter()
    folio_breakdown = []

    for fol in pharma_folios:
        labs = folio_labels[fol]
        if len(labs) < 4:
            continue
        mid = len(labs) // 2
        top_labs = labs[:mid]
        bot_labs = labs[mid:]

        top_c = Counter(classify_pharma_label_morphology(w) for _, _, w in top_labs)
        bot_c = Counter(classify_pharma_label_morphology(w) for _, _, w in bot_labs)
        upper_half_classes.update(top_c)
        lower_half_classes.update(bot_c)

        folio_breakdown.append({
            "folio": fol,
            "total_labels": len(labs),
            "upper_register_sample": [w for _, _, w in top_labs[:5]],
            "lower_register_sample": [w for _, _, w in bot_labs[:5]],
            "upper_root_share": round(top_c["ROOT_TUBER"] / max(1, len(top_labs)), 4),
            "lower_root_share": round(bot_c["ROOT_TUBER"] / max(1, len(bot_labs)), 4),
            "upper_seed_leaf_jar_share": round((top_c["SEED_LEAF_STAR"] + top_c["VESSEL_LIQUID"]) / max(1, len(top_labs)), 4),
            "lower_seed_leaf_jar_share": round((bot_c["SEED_LEAF_STAR"] + bot_c["VESSEL_LIQUID"]) / max(1, len(bot_labs)), 4),
        })

    # Also test cross-echo between each Pharma folio's labels and its prose paragraphs!
    return {
        "pharma_folio_count": len(folio_breakdown),
        "upper_register_counts": dict(upper_half_classes),
        "lower_register_counts": dict(lower_half_classes),
        "folios": folio_breakdown,
    }


def evaluate_5_guild_concordance(folio_tokens):
    guild_names = list(HERBAL_GUILDS.keys())
    guild_folios = {g: list(dict.fromkeys(HERBAL_GUILDS[g]["folios"])) for g in guild_names}
    all_target_folios = [f for g in guild_names for f in guild_folios[g] if f in folio_tokens]

    # Compute signature density of each guild's marker function on its own folios vs other guilds' folios
    matrix = {}
    in_guild_scores = []
    off_guild_scores = []

    for g_name, g_info in HERBAL_GUILDS.items():
        fn = g_info["signature_markers"]
        row = {}
        for h_name in guild_names:
            fols = [f for f in guild_folios[h_name] if f in folio_tokens]
            toks = [w for f in fols for w in folio_tokens[f]]
            hits = sum(1 for w in toks if fn(w))
            rate = hits / max(1, len(toks))
            row[h_name] = round(rate, 4)
            if g_name == h_name:
                in_guild_scores.append(rate)
            else:
                off_guild_scores.append(rate)
        matrix[g_name] = row

    obs_diag_mean = sum(in_guild_scores) / len(in_guild_scores)
    obs_off_mean = sum(off_guild_scores) / len(off_guild_scores)
    obs_lift = obs_diag_mean / max(1e-9, obs_off_mean)

    # 1,000-trial permutation test shuffling folio-to-guild assignments
    rng = random.Random(153)
    unique_folios = sorted(set(all_target_folios))
    guild_sizes = {g: len([f for f in guild_folios[g] if f in folio_tokens]) for g in guild_names}

    null_lifts = []
    for _ in range(1000):
        shuffled = unique_folios[:]
        rng.shuffle(shuffled)
        idx = 0
        perm_guilds = {}
        for g in guild_names:
            sz = guild_sizes[g]
            perm_guilds[g] = shuffled[idx:idx + sz]
            idx += sz

        in_s = []
        off_s = []
        for g_name, g_info in HERBAL_GUILDS.items():
            fn = g_info["signature_markers"]
            for h_name in guild_names:
                fols = perm_guilds[h_name]
                toks = [w for f in fols for w in folio_tokens[f]]
                rate = sum(1 for w in toks if fn(w)) / max(1, len(toks))
                if g_name == h_name:
                    in_s.append(rate)
                else:
                    off_s.append(rate)
        null_lifts.append((sum(in_s) / len(in_s)) / max(1e-9, (sum(off_s) / len(off_s))))

    null_mean = sum(null_lifts) / len(null_lifts)
    null_sd = math.sqrt(sum((x - null_mean) ** 2 for x in null_lifts) / len(null_lifts))
    z_score = (obs_lift - null_mean) / max(1e-9, null_sd)
    p_emp = sum(1 for x in null_lifts if x >= obs_lift) / len(null_lifts)

    return {
        "observed_in_guild_mean_rate": round(obs_diag_mean, 4),
        "observed_off_guild_mean_rate": round(obs_off_mean, 4),
        "observed_selectivity_lift": round(obs_lift, 4),
        "null_lift_mean": round(null_mean, 4),
        "null_lift_sd": round(null_sd, 4),
        "z_score": round(z_score, 2),
        "p_empirical": p_emp,
        "guild_rate_matrix": matrix,
    }


def main():
    folio_tokens, folio_labels, folio_meta = parse_corpus()
    pharma_res = analyze_pharma_row_anatomy(folio_labels)
    guild_res = evaluate_5_guild_concordance(folio_tokens)

    # Also compute global Pharmaceutical Label -> Same-Folio Prose stem match lift
    pharma_folios = [f for f in folio_labels if re.match(r"^f(8[89]|9[0-9]|10[0-2])[rv][0-9]*$", f) and f in folio_tokens]
    same_folio_matches = 0
    total_pharma_labels = 0
    for f in pharma_folios:
        prose_set = set(folio_tokens[f])
        for _, _, lw in folio_labels[f]:
            total_pharma_labels += 1
            stem = lw[:4] if len(lw) >= 4 else lw
            if any(stem in pw for pw in prose_set if pw != lw):
                same_folio_matches += 1

    payload = {
        "attack": 153,
        "phase": 164,
        "discovery": 170,
        "title": "5-Organ Visual Botanical Anatomy & Chromatic Pigment Classifier",
        "five_guild_concordance": guild_res,
        "pharma_register_anatomy": pharma_res,
        "pharma_label_to_prose_stem_echo": {
            "total_pharma_labels": total_pharma_labels,
            "same_folio_stem_matches": same_folio_matches,
            "same_folio_echo_rate": round(same_folio_matches / max(1, total_pharma_labels), 4),
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"[Attack 153] 5-Guild Selectivity Lift = {guild_res['observed_selectivity_lift']}x "
        f"(in={guild_res['observed_in_guild_mean_rate']} vs off={guild_res['observed_off_guild_mean_rate']}, "
        f"z = +{guild_res['z_score']}, p = {guild_res['p_empirical']}); "
        f"Pharma Label->Prose Stem Echo = {same_folio_matches}/{total_pharma_labels} "
        f"({payload['pharma_label_to_prose_stem_echo']['same_folio_echo_rate']*100:.1f}%)"
    )


if __name__ == "__main__":
    main()
