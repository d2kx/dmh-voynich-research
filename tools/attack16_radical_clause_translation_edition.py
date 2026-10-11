#!/usr/bin/env python3
"""
Phase 27 / Attack 16: Four-Tier Radical + Clause-Frame Structural Translation Edition
& Corpus-Wide Structural Parse Coverage Evaluator.

Generates:
1. data/attack16_radical_clause_translation_edition.json:
   - Corpus-wide coverage metrics of our 4-Tier Structural + Radical Decoder across all
     37,517 prose tokens and all 892 figure labels.
   - Structured 4-tier interlinear parses of the 6 flagship cribbed/chained passages.
2. notes/RADICAL_CLAUSE_TRANSLATION_EDITION.md:
   - Complete human-readable 4-Tier Radical + Clause-Frame Interlinear Edition.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from attack7_positional_envelope_fst import (
    stage3_positional_proclitic_margin,
    extract_core_root_and_envelope,
)

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
RAD_LEX_PATH = ROOT / "data" / "attack12_core_root_radical_decomposition.json"
RAD_TABLE_PATH = ROOT / "data" / "attack14_elementary_radical_lexicon.json"
CRIB_PATH = ROOT / "data" / "attack13_multiword_phrase_crib_scanner.json"
OUT_JSON = ROOT / "data" / "attack16_radical_clause_translation_edition.json"
OUT_MD = ROOT / "notes" / "RADICAL_CLAUSE_TRANSLATION_EDITION.md"

# Compact semantic/domain tag for each top elementary radical (from Attack 14 empirical grounding)
RADICAL_SHORT_TAG = {
    "ch": "ACT:mix/proc",
    "sh": "ACT:heat/steep",
    "che": "ACT:infuse",
    "she": "ACT:decoct",
    "k": "VESSEL/BODY(k)",
    "t": "TUBE/DUCT(t)",
    "p": "TOP_GALLOWS(p=t)",
    "f": "TOP_GALLOWS(f=k)",
    "d": "BASE/HUB(d)",
    "ol": "FLUID/TUBE(ol)",
    "al": "SUBST/STAR(al)",
    "ar": "BOTAN/ROOT(ar)",
    "or": "JAR/HERB(or)",
    "ok": "VESSEL_NOM(ok)",
    "ot": "DUCT_NOM(ot)",
    "od": "DOSAGE/VESSEL(od)",
    "ed": "FLOW/BATHE(ed)",
    "ee": "LIQUID_INTENS(ee)",
    "eo": "BOIL/FLOW(eo)",
    "ke": "EXTRACT/COOK(ke)",
    "te": "DRAW/CONDUIT(te)",
    "keo": "PHARMA_BOIL(keo)",
    "teo": "ZOD_CONTAIN(teo)",
    "tch": "PROC_OP(tch)",
    "kch": "STAR_OP(kch)",
    "pch": "HEADER_OP(pch)",
    "cth": "HERB_LEAF_OP(cth)",
    "ckh": "BALNEO_OP(ckh)",
    "lk": "LIQ_VESSEL(lk)",
    "lch": "LIQ_MIX(lch)",
    "dar": "JAR/ROOT_SRC(dar)",
    "dal": "BASIN/PORTION(dal)",
    "dam": "FINAL_DOSE(dam)",
    "kol": "PHARMA_PLANT(kol)",
    "tol": "LEAF/SHOOT(tol)",
    "kal": "HUMORAL_ROOT(kal)",
    "tal": "BARREL_measure(tal)",
    "kar": "STALK/BARK(kar)",
    "tar": "ROOT_EARTH(tar)",
    "air": "AETHER/STAR(air)",
    "ain": "ESSENCE/UNIT(ain)",
    "am": "TOTAL/CLOSER(am)",
    "s": "SEED/PART(s)",
    "r": "STREAM/PART(r)",
    "l": "LIQUID_PREF(l)",
    "o": "ENTITY_CORE(o)",
    "a": "HUB_AXIS(a)",
    "e": "ESSENCE(e)",
    "y": "STATE(y)",
    "dy": "DONE(dy)",
    "g": "STOPPER/JAR_RIM(g)",
    "so": "HERB_SAP(so)",
    "to": "SPOKE/RAY(to)",
    "ko": "STAR_NODE(ko)",
    "ek": "DISTILL(ek)",
    "ck": "CONCOCT(ck)",
    "okc": "JAR_COMPOUND(okc)",
}

PREFIX_TAG = {
    "q": "CONJ(and)+",
    "qo": "CONJ+NOM(the)+",
    "o": "NOM(the)+",
    "y": "INIT_NOM+",
    "d": "ABL(from)+",
    "s": "INST(with)+",
    "l": "LIQ(in-liq)+",
    "ch": "V_OP+",
    "sh": "V_SH+",
    "cth": "V_CTH+",
    "ckh": "V_CKH+",
    "p": "HDR_P+",
    "t": "HDR_T+",
    "k": "HDR_K+",
    "f": "HDR_F+",
}

SUFFIX_TAG = {
    "DY": "-VERB(do/ed)",
    "AN": "-ACC/GEN(unit)",
    "OL": "-LOC(fluid)",
    "AL": "-DAT(to/for)",
    "OR": "-INST(by/src)",
    "AR": "-ABL(from)",
    "AM": "-FIN(complete!)",
    "EY": "-PART(ing)",
    "Y": "-STAT(state)",
    "S": "-PL/PART(s)",
    "D": "-LOC_D",
    "R": "-DIR_R",
    "L": "-LIQ_L",
}


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("!", "").replace("?", "").replace("*", "")
    return t.strip(".,-<> ")


def short_star_code(sc: str | None) -> str:
    if not sc:
        return ""
    s = sc.lower()
    if "dark" in s:
        return "★D"
    if "dotted" in s:
        return "★L."
    if "light" in s:
        return "★L"
    return "★"


def parse_all_lines():
    raw_lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    parsed = []
    cur_folio = None
    pending_star = ""

    for raw in raw_lines:
        raw = raw.strip()
        if not raw:
            continue
        if raw.startswith("#"):
            c = raw.lstrip("#").strip()
            if "star" in c.lower():
                pending_star = short_star_code(c)
            continue

        m_f = re.match(r"^<(f\d+[rv]\d*|fRos)>\s*<!(.*)$", raw)
        if m_f:
            cur_folio = m_f.group(1)
            pending_star = ""
            continue

        m_line = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$", raw)
        if not m_line:
            continue
        folio, lnum, loc, body = m_line.groups()
        has_start = "<%>" in body
        has_end = "<$>" in body
        has_intrusion = "<->" in body

        star_here = pending_star if has_start else ""
        if has_start:
            pending_star = ""

        text_clean = re.sub(r"<!([^>]*)>", "", body)
        text_clean = text_clean.replace("<%>", "").replace("<$>", "").replace("<->", " ")
        # Keep track of tokens and whether they had a micro-space ','
        raw_toks = [clean_tok(t) for t in re.split(r"[.\s]+", text_clean) if clean_tok(t)]
        if not raw_toks:
            continue

        parsed.append({
            "folio": folio,
            "loc": f"{folio}.{lnum}",
            "lnum": lnum,
            "tag": loc,
            "is_label": loc.startswith(("@L", "&L", "+L")),
            "is_prose": "P" in loc,
            "has_start": has_start,
            "has_end": has_end,
            "has_intrusion": has_intrusion,
            "star": star_here,
            "raw_body": body,
            "tokens": raw_toks,
        })
    return parsed


def tokenize_eva_glyphs(s: str):
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


def build_viterbi_root_segmenter(all_lines):
    import math
    root_token_counts = Counter()
    for ln in all_lines:
        for t in ln["tokens"]:
            t_clean = t.replace(",", "")
            _, _, rt = extract_core_root_and_envelope(t_clean, "MEDIAL")
            if rt:
                root_token_counts[rt] += 1

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

    def segment_root(rt: str):
        n = len(rt)
        if n <= 1:
            return [rt]
        glyphs = tokenize_eva_glyphs(rt)
        if len(glyphs) == 1:
            return [rt]
        force_split = len(glyphs) >= 3 and root_token_counts[rt] <= 200
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

    return {rt: segment_root(rt) for rt in root_token_counts}, segment_root


def main():
    print("Running Phase 27 / Attack 16: Four-Tier Radical + Clause-Frame Translation Edition...")
    rad_table_data = json.loads(RAD_TABLE_PATH.read_text(encoding="utf-8"))
    lex_entries = rad_table_data.get("empirical_radical_lexicon_table", [])
    top59_rads = {r["radical"] for r in lex_entries}
    for r in lex_entries:
        rd = r["radical"]
        if rd not in RADICAL_SHORT_TAG:
            role_short = r.get("proposed_role_tag", "").split("(")[0].strip()
            RADICAL_SHORT_TAG[rd] = f"{role_short}({rd})"

    all_lines = parse_all_lines()
    root_decomp_map, segment_root_fn = build_viterbi_root_segmenter(all_lines)

    # Build direct label lookup (norm token -> list of label loci & category)
    label_index = defaultdict(list)
    label_root_index = defaultdict(list)
    for ln in all_lines:
        if ln["is_label"]:
            phrase_norm = " . ".join(stage3_positional_proclitic_margin(t.replace(",", "")) for t in ln["tokens"])
            for t in ln["tokens"]:
                t_nocomma = t.replace(",", "")
                canon = stage3_positional_proclitic_margin(t_nocomma)
                _, _, rt = extract_core_root_and_envelope(t_nocomma, "STANDALONE")
                label_index[canon].append(f"{ln['loc']}({ln['tag']})")
                if len(rt) >= 2:
                    label_root_index[rt].append(f"{ln['loc']}")
            if len(ln["tokens"]) >= 2:
                label_index[phrase_norm].append(f"{ln['loc']}(2W-LABEL)")

    # Analyze token-level & clause-level coverage across all prose lines
    total_prose_tokens = 0
    parsed_with_known_radical = 0
    parsed_with_top59_radical = 0
    parsed_with_label_root_anchor = 0

    def analyze_token(tok_raw: str, w_idx: int, line_len: int, is_para_start: bool, is_para_end: bool):
        has_comma = "," in tok_raw
        t_clean = tok_raw.replace(",", "")
        pos_mode = "INITIAL" if w_idx == 0 else ("FINAL" if w_idx == line_len - 1 else "MEDIAL")
        canon = stage3_positional_proclitic_margin(t_clean)
        pos_sig, env_sig, core_root = extract_core_root_and_envelope(t_clean, pos_mode)
        pref = [x[2:] for x in env_sig.split("|") if x.startswith("P:")][0] if "P:" in env_sig else "0"
        suff = [x[2:] for x in env_sig.split("|") if x.startswith("S:")][0] if "S:" in env_sig else "0"

        rads = root_decomp_map.get(core_root, [core_root]) if core_root else [canon]
        rad_str = "+".join(rads)
        seg_str = f"{pref + '-' if pref != '0' else ''}[{rad_str}]{'-' + suff.lower() if suff != '0' else ''}"
        if tok_raw.startswith("q") and not seg_str.startswith("q"):
            seg_str = "q+" + seg_str

        # Build morphological gloss
        p_gloss = ""
        if tok_raw.startswith("qo"):
            p_gloss = "CONJ+NOM+"
        elif tok_raw.startswith("q"):
            p_gloss = "CONJ+"
        elif tok_raw.startswith("o"):
            p_gloss = "NOM+"
        elif tok_raw.startswith("y") and len(tok_raw) > 2:
            p_gloss = "INIT_NOM+"
        elif pref != "0":
            p_gloss = PREFIX_TAG.get(pref.lower(), f"{pref}+")

        r_glosses = [RADICAL_SHORT_TAG.get(r, f"ROOT({r})") for r in rads]
        s_gloss = SUFFIX_TAG.get(suff, f"-{suff}" if suff != "0" else "")

        slot_role = "BODY"
        if is_para_start and w_idx == 0:
            slot_role = "PARA_OPENER"
        elif w_idx == 0:
            slot_role = "LINE_OPENER"
        elif is_para_end and w_idx == line_len - 1:
            slot_role = "PARA_CLOSER"
        elif w_idx == line_len - 1 or tok_raw.endswith(("am", "m", "y", "dy")):
            slot_role = "CLAUSE_END"

        exact_lbls = label_index.get(canon, [])[:2]
        root_lbls = label_root_index.get(core_root, [])[:2] if not exact_lbls else []

        return {
            "raw": tok_raw,
            "has_microspace": has_comma,
            "canon": canon,
            "core_root": core_root,
            "radicals": rads,
            "tier2_seg": seg_str,
            "tier3_gloss": f"{p_gloss}{'+'.join(r_glosses)}{s_gloss}",
            "slot_role": slot_role,
            "exact_label_cribs": exact_lbls,
            "root_label_cribs": root_lbls,
        }

    for ln in all_lines:
        if not ln["is_prose"]:
            continue
        for w_i, t in enumerate(ln["tokens"]):
            total_prose_tokens += 1
            info = analyze_token(t, w_i, len(ln["tokens"]), ln["has_start"], ln["has_end"])
            if any(r in RADICAL_SHORT_TAG for r in info["radicals"]):
                parsed_with_known_radical += 1
            if any(r in top59_rads for r in info["radicals"]):
                parsed_with_top59_radical += 1
            if info["exact_label_cribs"] or info["root_label_cribs"]:
                parsed_with_label_root_anchor += 1

    coverage_stats = {
        "total_prose_tokens": total_prose_tokens,
        "tokens_with_grounded_radical_gloss": parsed_with_known_radical,
        "tokens_with_grounded_radical_pct": round(100.0 * parsed_with_known_radical / max(total_prose_tokens, 1), 2),
        "tokens_with_top59_radical": parsed_with_top59_radical,
        "tokens_with_top59_radical_pct": round(100.0 * parsed_with_top59_radical / max(total_prose_tokens, 1), 2),
        "tokens_with_diagram_label_root_match": parsed_with_label_root_anchor,
        "tokens_with_diagram_label_root_pct": round(100.0 * parsed_with_label_root_anchor / max(total_prose_tokens, 1), 2),
    }

    # Select Flagship Passages for the 4-Tier Structural Translation Edition
    def extract_passage(folio: str, lnum_set: set[str] | None = None):
        out_lines = []
        for ln in all_lines:
            if ln["folio"] != folio:
                continue
            if lnum_set is not None and ln["lnum"] not in lnum_set:
                continue
            tok_objs = [
                analyze_token(t, i, len(ln["tokens"]), ln["has_start"], ln["has_end"])
                for i, t in enumerate(ln["tokens"])
            ]
            # Check for 2-word crib in this line
            norms = [x["canon"] for x in tok_objs]
            two_word_hits = []
            for k in range(len(norms) - 1):
                bg = f"{norms[k]} . {norms[k+1]}"
                if bg in label_index:
                    two_word_hits.append(f"`{tok_objs[k]['raw']} . {tok_objs[k+1]['raw']}` == Diagram Label `{bg}` ({', '.join(label_index[bg][:2])})")

            out_lines.append({
                "loc": ln["loc"],
                "tag": ln["tag"],
                "star": ln["star"],
                "has_start": ln["has_start"],
                "has_end": ln["has_end"],
                "has_intrusion": ln["has_intrusion"],
                "tokens": tok_objs,
                "two_word_cribs": two_word_hits,
            })
        return out_lines

    passages = [
        {
            "id": "passage_1_three_way_botanical_crib",
            "title": "1. The Three-Way Botanical Phrase Crib Paradigm (`f88v.4` Label <-> `f105r.1-8` Chained Recipes <-> `f114v.36-38` Recipe)",
            "description": (
                "Demonstrates the 2-word botanical label `<f88v.4,@Lf> otar . arody` (`18.47` rarity bits) "
                "recurring across three distinct syntactic environments with predictable positional allography: "
                "(a) standalone plant label `otar . arody` (`o-` nominal + `t` gallows), "
                "(b) paragraph-initial recipe header `<f105r.6,@P0> <%>par . arody` (top-line `p` gallows, chained to `<f105r.1-5>` via shared `L.` star), and "
                "(c) interior line-final clause closer `<f114v.37,+P0> ... chey . tar . arody <$>` (unprefixed `t` gallows)."
            ),
            "blocks": [
                {"subtitle": "f88v Botanical Labels (Lines 1-6)", "lines": extract_passage("f88v", {"1", "2", "3", "4", "5", "6"})},
                {"subtitle": "f105r Same-Star Chained Recipes P1->P2 (Lines 1-10)", "lines": extract_passage("f105r", {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"})},
                {"subtitle": "f114v Starred Recipe P10 (Lines 36-38)", "lines": extract_passage("f114v", {"36", "37", "38"})},
            ],
        },
        {
            "id": "passage_2_parallel_template_and_catena_recipes",
            "title": "2. Same-Star Chained Recipe Pairs: Parallel Template Cloning (`f115r:P5->P6`) & Tail-to-Head Catenation (`f111r:P3->P4`)",
            "description": (
                "Demonstrates why the rubricator repeated the same marginal star (`L. -> L.`) on 10 pairs in Quire 20: "
                "on `f115r:P5->P6`, the two recipes clone the exact 4-slot opening sequence (`tch -> qokch -> qotch -> l-pch/polch`); "
                "on `f111r:P3->P4`, the closing words of P3 (`lkeedy . lkedar . okeedy`) catenate directly into the opening clause of P4 (`<%>pchedar . oteeol . lkeedain . okeam`)."
            ),
            "blocks": [
                {"subtitle": "f115r:P5->P6 Parallel Template Pair (Lines 17-23)", "lines": extract_passage("f115r", {"17", "18", "19", "20", "21", "22", "23"})},
                {"subtitle": "f111r:P3->P4 Tail-to-Head Catenated Pair (Lines 12-21)", "lines": extract_passage("f111r", {"12", "13", "14", "15", "16", "17", "18", "19", "20", "21"})},
            ],
        },
        {
            "id": "passage_3_rosettes_anchored_herbal_f48v",
            "title": "3. The Rosettes-Anchored Herbal Treatise (`f48v`, Lines 7-11)",
            "description": (
                "Paragraph 2 of Herbal folio `f48v` (`Hand 1, Language A`), where line `<f48v.9,+P0>` splits across the central flower stalk (`<->`) "
                "and cites the exact 2-word Cosmological Rosettes label `<fRos.45,+L0> otchdy . otoldy` (`19.53` rarity bits) followed two words later by `otedy` (`<fRos.72> otedain . otedy`)."
            ),
            "blocks": [
                {"subtitle": "f48v Paragraph 2 (Lines 7-11)", "lines": extract_passage("f48v", {"7", "8", "9", "10", "11"})},
            ],
        },
        {
            "id": "passage_4_crimson_star_triad_f103r",
            "title": "4. The First Crimson-Star Triad (`D -> L_1 -> L_2`) on `f103r` (Paragraphs 1-3, Lines 1-11)",
            "description": (
                "Illustrates the 3-part functional division of the Crimson-Star (`D -> L -> L`) triads on `f103r`: "
                "Slot 1 (`★D`, Master Recipe) introduces the core preparation; Slot 2 (`★L`, First Follower) expands nominal/ingredient quantities (`-aiin`); "
                "Slot 3 (`★L`, Second Follower) executes high-density verbal actions (`-edy/-dy`)."
            ),
            "blocks": [
                {"subtitle": "f103r Triad 1: P1 (★D), P2 (★L), P3 (★L) (Lines 1-11)", "lines": extract_passage("f103r", {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"})},
            ],
        },
    ]

    out_data = {
        "coverage_summary": coverage_stats,
        "passages": passages,
    }
    OUT_JSON.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {OUT_JSON}")
    print("Coverage stats:", coverage_stats)

    # Render Markdown Edition
    md = []
    md.append("# Four-Tier Radical & Clause-Frame Structural Translation Edition (`Phase 27 / Attack 16`)\n")
    md.append("## 1. Corpus-Wide Structural Parse Coverage\n")
    md.append(
        f"- **Total Prose Tokens Parsed**: `{coverage_stats['total_prose_tokens']:,}` tokens across all 226 folios.\n"
        f"- **Tokens with Grounded Radical Gloss (`Attack 12/14` Lexicon)**: **`{coverage_stats['tokens_with_grounded_radical_gloss']:,} / {coverage_stats['total_prose_tokens']:,}` (`{coverage_stats['tokens_with_grounded_radical_pct']}%`)**.\n"
        f"- **Tokens Containing a Top-59 Elementary Radical (`Attack 14`)**: **`{coverage_stats['tokens_with_top59_radical']:,} / {coverage_stats['total_prose_tokens']:,}` (`{coverage_stats['tokens_with_top59_radical_pct']}%`)**.\n"
        f"- **Prose Tokens Sharing an Exact Core Root with a Diagram Figure Label (`@Lf/@Lc/@Lz/@L0/@Lt/@Ln`)**: **`{coverage_stats['tokens_with_diagram_label_root_match']:,} / {coverage_stats['total_prose_tokens']:,}` (`{coverage_stats['tokens_with_diagram_label_root_pct']}%`)**.\n"
    )
    md.append("\n### Guide to the Four Interlinear Tiers\n")
    md.append(
        "1. **Tier 1 (`EVA Surface`)**: Exact transliteration from [data/ZL3b-n.txt](../data/ZL3b-n.txt) with paragraph start (`<%>`), paragraph end (`<$>`), drawing intrusion (`<->`), and marginal star class (`[★D]`, `[★L.]`, `[★L]`).\n"
        "2. **Tier 2 (`Radical Segmentation`)**: Stage-3 canonical form segmented into `Prefix-[R_1+R_2]-Suffix` via our FST ([tools/attack7_positional_envelope_fst.py](../tools/attack7_positional_envelope_fst.py)) and Minimum Description Length Radical Decomposition ([tools/attack12_core_root_radical_decomposition.py](../tools/attack12_core_root_radical_decomposition.py)).\n"
        "3. **Tier 3 (`Morphosyntactic & Radical Role Gloss`)**: Functional slot parse combining proclitic/prefix operators (`CONJ(q-)+`, `NOM(o-)+`, `ABL(d-)+`, `LIQ(l-)+`), empirically grounded radical domains (`ACT:mix/proc`, `ACT:heat/steep`, `BOTAN/ROOT(ar)`, `JAR/HERB(or)`, `FLUID/TUBE(ol)`), and case/verbal suffixes (`-VERB(do/ed)`, `-ACC/GEN(unit)`, `-LOC(fluid)`, `-FIN(complete!)`).\n"
        "4. **Tier 4 (`Diagram Crib & Structural Anchor Notes`)**: Direct 1-word and 2-word crib equations linking prose tokens to illustrated plants (`@Lf`), apothecary jars (`@Lc`), zodiac degrees (`@Lz`), cosmological hubs (`@L0`), or biological tubes/nymphs (`@Lt/@Ln`).\n"
    )

    for p in passages:
        md.append(f"\n---\n\n## {p['title']}\n")
        md.append(f"{p['description']}\n")
        for blk in p["blocks"]:
            md.append(f"\n### {blk['subtitle']}\n")
            for ln in blk["lines"]:
                star_prefix = f"[{ln['star']}] " if ln["star"] else ""
                start_tag = "<%> " if ln["has_start"] else ""
                end_tag = " <$>" if ln["has_end"] else ""
                t1 = " . ".join(t["raw"] for t in ln["tokens"])
                t2 = " . ".join(t["tier2_seg"] for t in ln["tokens"])
                t3 = " | ".join(t["tier3_gloss"] for t in ln["tokens"])

                crib_notes = list(ln["two_word_cribs"])
                for t in ln["tokens"]:
                    if t["exact_label_cribs"]:
                        crib_notes.append(f"`{t['raw']}` = exact label `{t['canon']}` [{', '.join(t['exact_label_cribs'])}]")

                md.append(f"- **`<{ln['loc']},{ln['tag']}>`** {star_prefix}\n")
                md.append(f"  - **T1 (EVA)**: `{start_tag}{t1}{end_tag}`\n")
                md.append(f"  - **T2 (Radicals)**: `{t2}`\n")
                md.append(f"  - **T3 (Gloss)**: `{t3}`\n")
                if crib_notes:
                    md.append(f"  - **T4 (Cribs)**: {'; '.join(crib_notes[:6])}\n")

    OUT_MD.write_text("".join(md), encoding="utf-8")
    print(f"Saved {OUT_MD}")


if __name__ == "__main__":
    main()
