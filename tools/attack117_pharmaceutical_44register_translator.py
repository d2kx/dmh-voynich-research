#!/usr/bin/env python3
r"""
Attack 117 (Discovery 134): Complete 44-Register Pharmaceutical Formulary Translator,
`@Lf -> Herbal Monograph` Specimen Traceability & Deictic-Anaphoric Scaling Law (`f88r–f102v2`)

Tests & Builds:
1. Traces every one of the `210` `@Lf` Botanical Root/Leaf Row Labels across the `16` Pharmaceutical
   folios (`f88r–f102v2`) back to its exact source Herbal Monograph(s) (`$I=H`, both direct canonical
   stem match and `o-`-stripped / gallows-folded stem match), measuring the **Botanical Specimen
   Traceability Rate (`% of @Lf labels traceable to $I=H / $I=S / $I=B` or attested 2-stem compounds)**.
2. Tests the **Register Label-Count -> Prose Deictic/Container Scaling Law**:
   - Compares Pharmaceutical Registers that have a full row of `@Lf` plant-part labels (`n_lf >= 4`)
     against unlabelled/sparse registers (`n_lf <= 1`, e.g., `f101r`, `f102r1.Reg2/3`, `f102r2.Reg1/2`):
   - Tests how `@Lf` label multiplicity scales with `@P0` prose length, Measured Dose `-aiin` count,
     Active `qo-` processing verbs, and Container/Deictic pronouns (`ol, dal, dar, or, daiin, chol, cheol`).
3. Builds the **Complete 44-Register Interlinear & Procedural Translation Table (`f88r.Reg1 .. f102v2.Reg2`)**:
   - For all `44` Compounding Registers, outputs:
     a) Decomposed `@Lc` Master Apothecary Vessel Title + functional gloss,
     b) Row of `@Lf` Raw Botanical Specimens + their matched Herbal Monographs (`$I=H`),
     c) Complete clause-by-clause procedural translation of the `<%> @P0` preparation paragraph,
     d) Stoichiometric tally (`Active Verbs : Measured Doses : Container/Deictic Anaphors`),
     e) Downstream clinical routing (`#1` Starred Decoction Recipe `$I=S` and `#1` Balneological Bath `$I=B`).
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
A115_PATH = ROOT / "data" / "attack115_pharmaceutical_register_row_decomposition.json"
OUT_PATH = ROOT / "data" / "attack117_pharmaceutical_44register_translator.json"


def normalize_token(w: str) -> str:
    w = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", w)
    w = re.sub(r"\{[^}]*\}", "", w)
    w = re.sub(r"<[^>]*>", "", w)
    w = w.replace("?", "").replace("!", "").replace("*", "").replace("%", "").strip()
    return w


def canonical_stem(w: str, is_top_line: bool = False) -> str:
    s = w
    if is_top_line:
        s = s.replace("p", "t").replace("f", "k")
    if s.startswith("qo") and len(s) > 2:
        s = s[1:]
    elif s.startswith("q") and len(s) > 2:
        s = s[1:]
    s = re.sub(r"i{2,}", "ii", s)
    s = re.sub(r"e{2,}", "ee", s)
    if len(s) >= 4 and s.endswith("dy"):
        s = s[:-2] + "y"
    return s


def folded_stem(w: str) -> str:
    s = w.replace("p", "t").replace("f", "k")
    if s.endswith("g"):
        s = s[:-1] + "m"
    return canonical_stem(s, is_top_line=True)


def strip_o_prefix(cs: str) -> str:
    if cs.startswith("o") and not cs.startswith(("ol", "or")) and len(cs) >= 4:
        return canonical_stem(cs[1:], is_top_line=True)
    return cs


# Deterministic structural gloss for tokens in Pharmaceutical registers
CLOSED_GLOSS = {
    "daiin": "FROM-THIS [1-part dose]",
    "dain": "FROM-THIS [half-dose]",
    "aiin": "ONE-PART [measure]",
    "oiin": "WHOLE-PART [measure]",
    "saiin": "AND-ONE-PART [measure]",
    "or": "PART/PORTION",
    "ol": "THE-VESSEL/FLUID",
    "al": "TO-THE-VESSEL",
    "ar": "AT-THE-MIXTURE",
    "dar": "INTO-THE-VESSEL",
    "dal": "FROM-THE-VESSEL",
    "dol": "IN-THE-JAR",
    "chol": "LEAF/HERB-EXTRACT",
    "cheol": "INFUSED-HERB-LIQUID",
    "cheor": "HERB-PORTION",
    "chor": "LEAF-PORTION",
    "shol": "PLUMED-SAP/FLUID",
    "sheol": "PLUMED-INFUSION",
    "qokol": "BOIL/SIMMER [vessel-herb]",
    "qokeol": "DECOCT/EXTRACT [infused-herb]",
    "qokor": "STEEP/DOSE [root-portion]",
    "qokeey": "INFUSE-THOROUGHLY",
    "qokedy": "BOIL-PROCESS",
    "qokeedy": "SIMMER-INTENSELY",
    "okol": "VESSEL-HERB [stock]",
    "okeol": "INFUSED-STOCK",
    "okor": "ROOT-STOCK",
    "otar": "SPOUT/ROOT-PORTION",
    "otal": "SPOUT/VESSEL-TOTAL",
    "otol": "VESSEL-MEASURE",
    "dam": "FINAL-MIXTURE [end]",
    "am": "COMPLETE [end]",
    "sam": "AND-COMPLETE [end]",
    "om": "WHOLE-YIELD [end]",
}


def gloss_pharm_word(w: str, is_top: bool = False) -> str:
    cs = canonical_stem(w, is_top)
    if w in CLOSED_GLOSS:
        return CLOSED_GLOSS[w]
    if cs in CLOSED_GLOSS:
        return f"{CLOSED_GLOSS[cs]}"

    parts = []
    s = w
    if s.startswith("qo"):
        parts.append("PROC/BOIL")
        s = s[2:]
    elif s.startswith("o") and not s.startswith(("ol", "or")) and len(s) >= 4:
        parts.append("NOM")
        s = s[1:]
    elif s.startswith(("d", "da")) and len(s) >= 4:
        parts.append("FROM/INTO")
        s = s[2:] if s.startswith("da") else s[1:]
    elif s.startswith(("s", "sa")) and len(s) >= 4:
        parts.append("NEXT/AND")
        s = s[2:] if s.startswith("sa") else s[1:]
    elif s.startswith(("y", "yt", "yk")) and len(s) >= 4:
        parts.append("THEN")
        s = s[1:]

    # Core radical
    if any(r in s for r in ("kch", "tch", "pch", "fch", "ckh", "cth", "cph", "cfh")):
        parts.append("COMPOUND-HERB")
    elif any(r in s for r in ("ke", "te", "pe", "fe")):
        parts.append("HEATED-STEM")
    elif any(r in s for r in ("k", "t", "p", "f")):
        parts.append("ROOT-SPECIMEN")
    elif "sh" in s:
        parts.append("SAP/JUICE")
    elif "ch" in s:
        parts.append("HERB/LEAF")
    else:
        parts.append("LIQUID/PART")

    # Suffix
    if w.endswith(("aiin", "oiin", "iin")):
        parts.append("[1-DOSE]")
    elif w.endswith("edy"):
        parts.append("[MIXED]")
    elif w.endswith(("ol", "al")):
        parts.append("[IN-JAR]")
    elif w.endswith(("or", "ar")):
        parts.append("[PORTION]")
    elif w.endswith(("am", "om", "m")):
        parts.append("[DONE]")
    elif w.endswith(("dy", "y")):
        parts.append("[STATE]")

    return "-".join(parts) + f" ({cs})"


def main():
    with open(A115_PATH, "r", encoding="utf-8") as f:
        a115 = json.load(f)

    folio_meta_re = re.compile(r"^<f([0-9]+[rv][0-9]*)>\s*<!\s*(.*?)\s*>$")
    line_re = re.compile(r"^<f([0-9]+[rv][0-9]*)\.([0-9]+),([^>]+)>\s+(.*)$")

    folios_meta = {}
    canon_counts = Counter()
    folio_canon_set = defaultdict(set)
    herbal_stem_to_folios = defaultdict(list)
    starred_stem_to_folios = defaultdict(list)
    balneo_stem_to_folios = defaultdict(list)

    # Also store full token sequences for each Pharmaceutical register
    pharm_reg_lines = defaultdict(list)  # reg_id -> list of (lnum, [(w, cs, is_top)])
    current_pharm_reg_idx = defaultdict(int)
    in_para_top = defaultdict(lambda: True)

    with open(ZL_PATH, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            sline = raw_line.strip()
            mf = folio_meta_re.match(sline)
            if mf:
                fol = "f" + mf.group(1)
                meta_str = mf.group(2)
                m_dict = {}
                for kv in meta_str.split():
                    if "=" in kv:
                        k, v = kv.lstrip("$").split("=", 1)
                        m_dict[k] = v
                folios_meta[fol] = {
                    "section": m_dict.get("I", ""),
                    "language": m_dict.get("L", ""),
                    "hand": m_dict.get("H", ""),
                }
                continue

            m = line_re.match(sline)
            if not m:
                continue
            fol = "f" + m.group(1)
            lnum = int(m.group(2))
            loc = m.group(3)
            text = m.group(4)

            sec = folios_meta.get(fol, {}).get("section", "")
            has_para_start = "<%>" in text
            has_para_end = "<$>" in text

            clean_line = re.sub(r"<[^>]*>", " ", text)
            raw_tokens = [t for t in re.split(r"[.\s,]+", clean_line) if t]
            words = [normalize_token(t) for t in raw_tokens]
            words = [w for w in words if w and re.search(r"[a-z]", w)]
            if not words:
                if has_para_end:
                    in_para_top[fol] = True
                continue

            is_label = "@L" in loc or "+L" in loc
            is_top = (not is_label) and (has_para_start or lnum == 1 or in_para_top[fol])

            line_toks = []
            for w in words:
                cs = canonical_stem(w, is_top)
                fcs = folded_stem(w)
                ncs = strip_o_prefix(fcs)
                canon_counts[cs] += 1
                folio_canon_set[fol].add(cs)
                line_toks.append((w, cs, is_top))

                if sec == "H" and fol not in ("f58r", "f58v"):
                    for cand in {cs, fcs, ncs}:
                        if fol not in herbal_stem_to_folios[cand]:
                            herbal_stem_to_folios[cand].append(fol)
                elif sec == "S" or fol in ("f58r", "f58v"):
                    for cand in {cs, fcs, ncs}:
                        if fol not in starred_stem_to_folios[cand]:
                            starred_stem_to_folios[cand].append(fol)
                elif sec == "B":
                    for cand in {cs, fcs, ncs}:
                        if fol not in balneo_stem_to_folios[cand]:
                            balneo_stem_to_folios[cand].append(fol)

            if sec == "P" and not is_label:
                if has_para_start or current_pharm_reg_idx[fol] == 0:
                    current_pharm_reg_idx[fol] += 1
                reg_id = f"{fol}.Reg{current_pharm_reg_idx[fol]}"
                pharm_reg_lines[reg_id].append((lnum, line_toks))

            if not is_label:
                in_para_top[fol] = False
            if has_para_end:
                in_para_top[fol] = True

    # 1. Trace all 210 @Lf Botanical Root/Leaf Labels to Herbal Monographs ($I=H), Starred ($I=S), Balneo ($I=B), or 2-stem compounds
    attested_vocab = {cs for cs, cnt in canon_counts.items() if cnt >= 2 and len(cs) >= 2}

    def trace_lf_specimen(w: str):
        fcs = folded_stem(w)
        ncs = strip_o_prefix(fcs)
        h_matches = sorted(set(herbal_stem_to_folios.get(fcs, []) + herbal_stem_to_folios.get(ncs, [])))
        s_matches = sorted(set(starred_stem_to_folios.get(fcs, []) + starred_stem_to_folios.get(ncs, [])))
        b_matches = sorted(set(balneo_stem_to_folios.get(fcs, []) + balneo_stem_to_folios.get(ncs, [])))
        if h_matches or s_matches or b_matches:
            return {
                "trace_type": "DIRECT_OR_O_STRIPPED_STEM",
                "matched_stem": ncs if (not herbal_stem_to_folios.get(fcs) and herbal_stem_to_folios.get(ncs)) else fcs,
                "herbal_folios": h_matches[:6],
                "n_herbal_folios": len(h_matches),
                "n_starred_folios": len(s_matches),
                "n_balneo_folios": len(b_matches),
            }
        # Try 2-stem compound split (and 2-stem + coda / 3-stem)
        s = w.replace("p", "t").replace("f", "k")
        if s.endswith("g"):
            s = s[:-1] + "m"
        for cand in (s, s[1:] if s.startswith("o") and len(s) >= 5 else ""):
            if not cand:
                continue
            for i in range(2, len(cand) - 1):
                p1, p2 = canonical_stem(cand[:i], True), canonical_stem(cand[i:], True)
                if p1 in attested_vocab and p2 in attested_vocab:
                    hm = sorted(set(herbal_stem_to_folios.get(p1, [])) & set(herbal_stem_to_folios.get(p2, [])))
                    if not hm:
                        hm = sorted(set(herbal_stem_to_folios.get(p1, []) + herbal_stem_to_folios.get(p2, [])))
                    return {
                        "trace_type": "TWO_STEM_BOTANICAL_COMPOUND",
                        "matched_stem": f"{p1}+{p2}",
                        "herbal_folios": hm[:6],
                        "n_herbal_folios": len(hm),
                        "n_starred_folios": len(set(starred_stem_to_folios.get(p1, []) + starred_stem_to_folios.get(p2, []))),
                        "n_balneo_folios": len(set(balneo_stem_to_folios.get(p1, []) + balneo_stem_to_folios.get(p2, []))),
                    }
            for i in range(2, len(cand) - 2):
                p1, p2 = canonical_stem(cand[:i], True), canonical_stem(cand[i:-1], True)
                if p1 in attested_vocab and len(p2) >= 2 and p2 in attested_vocab:
                    hm = sorted(set(herbal_stem_to_folios.get(p1, []) + herbal_stem_to_folios.get(p2, [])))
                    return {
                        "trace_type": "TWO_STEM_PLUS_CODA_COMPOUND",
                        "matched_stem": f"{p1}+{p2}+{cand[-1]}",
                        "herbal_folios": hm[:6],
                        "n_herbal_folios": len(hm),
                        "n_starred_folios": len(set(starred_stem_to_folios.get(p1, []) + starred_stem_to_folios.get(p2, []))),
                        "n_balneo_folios": len(set(balneo_stem_to_folios.get(p1, []) + balneo_stem_to_folios.get(p2, []))),
                    }
            for i in range(2, len(cand) - 3):
                for j in range(i + 2, len(cand) - 1):
                    p1, p2, p3 = canonical_stem(cand[:i], True), canonical_stem(cand[i:j], True), canonical_stem(cand[j:], True)
                    if p1 in attested_vocab and p2 in attested_vocab and p3 in attested_vocab:
                        hm = sorted(set(herbal_stem_to_folios.get(p1, []) + herbal_stem_to_folios.get(p2, []) + herbal_stem_to_folios.get(p3, [])))
                        return {
                            "trace_type": "THREE_STEM_BOTANICAL_COMPOUND",
                            "matched_stem": f"{p1}+{p2}+{p3}",
                            "herbal_folios": hm[:6],
                            "n_herbal_folios": len(hm),
                            "n_starred_folios": len(set(starred_stem_to_folios.get(p1, []) + starred_stem_to_folios.get(p2, []))),
                            "n_balneo_folios": len(set(balneo_stem_to_folios.get(p1, []) + balneo_stem_to_folios.get(p2, []))),
                        }
        return {
            "trace_type": "RARE_SPECIMEN_SINGLETON",
            "matched_stem": fcs,
            "herbal_folios": [],
            "n_herbal_folios": 0,
            "n_starred_folios": 0,
            "n_balneo_folios": 0,
        }

    # Build lookup of @Lc decompositions from Attack 115
    lc_decomp_map = {
        d["loc"]: d for d in a115["locus_comparison"]["lc_apothecary_jar_labels"]["compound_decompositions"]
    }

    # 2. Process all 44 Pharmaceutical Registers
    translated_registers = []
    lf_trace_counts = Counter()
    total_lf_traced_to_herbal = 0
    total_lf_count = 0

    multi_lf_regs = []   # n_lf >= 4
    sparse_lf_regs = []  # n_lf <= 1

    DEICTIC_CONTAINERS = {"ol", "al", "ar", "or", "dar", "dal", "dol", "chol", "cheol", "chor", "cheor", "shol", "sheol", "daiin", "dain", "saiin"}

    for reg in a115["registers"]:
        rid = reg["register_id"]
        lines_data = pharm_reg_lines[rid]

        # Trace @Lc vessel labels
        lc_entries = []
        for lc in reg["paired_lc_jar_labels"]:
            d = lc_decomp_map.get(lc["loc"], {})
            lc_entries.append({
                "loc": lc["loc"],
                "surface": lc["w"],
                "decomposition_type": d.get("decomposition_type", "DIRECT"),
                "constituent_stems": d.get("constituent_stems", [lc["folded_cs"]]),
                "vessel_gloss": f"VESSEL-COMPOUND [{' + '.join(d.get('constituent_stems', [lc['folded_cs']]))}]",
            })

        # Trace @Lf plant-part labels
        lf_entries = []
        for lf in reg["paired_lf_plant_labels"]:
            tr = trace_lf_specimen(lf["w"])
            total_lf_count += 1
            lf_trace_counts[tr["trace_type"]] += 1
            if tr["n_herbal_folios"] > 0:
                total_lf_traced_to_herbal += 1
            lf_entries.append({
                "loc": lf["loc"],
                "surface": lf["w"],
                "folded_cs": lf["folded_cs"],
                "trace_type": tr["trace_type"],
                "matched_stem": tr["matched_stem"],
                "source_herbal_folios": tr["herbal_folios"],
                "specimen_gloss": gloss_pharm_word(lf["w"], False),
            })

        # Translate each line of the <%> @P0 preparation paragraph
        line_translations = []
        n_active_verbs = 0
        n_nominal_o = 0
        n_measured_doses = 0
        n_deictic_containers = 0
        total_toks = 0

        for lnum, ltoks in lines_data:
            raw_words = [w for w, _, _ in ltoks]
            gloss_words = []
            for w, cs, itop in ltoks:
                total_toks += 1
                if w.startswith("qo") or w.endswith("edy"):
                    n_active_verbs += 1
                if w.startswith("o") and not w.startswith(("ol", "or")):
                    n_nominal_o += 1
                if w.endswith(("aiin", "oiin", "iin", "ain")):
                    n_measured_doses += 1
                if cs in DEICTIC_CONTAINERS or w in DEICTIC_CONTAINERS or w.endswith(("ol", "or", "al", "ar")):
                    n_deictic_containers += 1
                gloss_words.append(f"{w} [{gloss_pharm_word(w, itop)}]")
            line_translations.append({
                "line_num": lnum,
                "eva_text": " . ".join(raw_words),
                "interlinear_translation": " | ".join(gloss_words),
            })

        stoich = {
            "n_tokens": total_toks,
            "n_open_stems": reg["n_open_stems"],
            "n_lf_labels": len(lf_entries),
            "n_lc_labels": len(lc_entries),
            "n_active_verbs": n_active_verbs,
            "n_nominal_o": n_nominal_o,
            "nominal_o_pct": round(100.0 * n_nominal_o / max(1, total_toks), 2),
            "n_measured_doses": n_measured_doses,
            "n_deictic_containers": n_deictic_containers,
            "verb_to_dose_ratio": round(n_active_verbs / max(1, n_measured_doses), 2),
            "deictic_container_pct": round(100.0 * n_deictic_containers / max(1, total_toks), 2),
        }

        if len(lf_entries) >= 4:
            multi_lf_regs.append(stoich)
        elif len(lf_entries) <= 1:
            sparse_lf_regs.append(stoich)

        translated_registers.append({
            "register_id": rid,
            "folio": reg["folio"],
            "reg_num": reg["reg_num"],
            "line_span": reg["line_span"],
            "stoichiometry": stoich,
            "lc_vessel_titles": lc_entries,
            "lf_botanical_specimens": lf_entries,
            "row_lf_to_prose_direct_matches": reg["row_lf_to_prose_matches"],
            "top_cited_herbal_monographs": reg["top_herbal_monographs"],
            "top_downstream_starred_recipes": reg["top_starred_recipes"],
            "top_downstream_balneo_folios": reg["top_balneo_folios"],
            "line_by_line_translation": line_translations,
        })

    def avg_metric(rlist, key):
        if not rlist:
            return 0.0
        return round(sum(r[key] for r in rlist) / len(rlist), 2)

    scaling_comparison = {
        "multi_specimen_registers_lf_ge_4": {
            "n_registers": len(multi_lf_regs),
            "mean_lf_labels": avg_metric(multi_lf_regs, "n_lf_labels"),
            "mean_prose_tokens": avg_metric(multi_lf_regs, "n_tokens"),
            "mean_active_verbs": avg_metric(multi_lf_regs, "n_active_verbs"),
            "mean_measured_doses": avg_metric(multi_lf_regs, "n_measured_doses"),
            "mean_deictic_containers": avg_metric(multi_lf_regs, "n_deictic_containers"),
            "mean_deictic_container_pct": avg_metric(multi_lf_regs, "deictic_container_pct"),
            "mean_verb_to_dose_ratio": avg_metric(multi_lf_regs, "verb_to_dose_ratio"),
        },
        "sparse_or_unlabelled_registers_lf_le_1": {
            "n_registers": len(sparse_lf_regs),
            "mean_lf_labels": avg_metric(sparse_lf_regs, "n_lf_labels"),
            "mean_prose_tokens": avg_metric(sparse_lf_regs, "n_tokens"),
            "mean_active_verbs": avg_metric(sparse_lf_regs, "n_active_verbs"),
            "mean_measured_doses": avg_metric(sparse_lf_regs, "n_measured_doses"),
            "mean_deictic_containers": avg_metric(sparse_lf_regs, "n_deictic_containers"),
            "mean_deictic_container_pct": avg_metric(sparse_lf_regs, "deictic_container_pct"),
            "mean_verb_to_dose_ratio": avg_metric(sparse_lf_regs, "verb_to_dose_ratio"),
        },
    }

    summary = {
        "attack_id": 117,
        "discovery_id": 134,
        "title": "Complete 44-Register Pharmaceutical Formulary Translator, @Lf Specimen Traceability & Deictic-Anaphoric Scaling",
        "lf_botanical_specimen_traceability": {
            "total_lf_labels": total_lf_count,
            "trace_type_breakdown": dict(lf_trace_counts),
            "resolved_to_herbal_or_compound_count": total_lf_count - lf_trace_counts["RARE_SPECIMEN_SINGLETON"],
            "resolved_to_herbal_or_compound_pct": round(100.0 * (total_lf_count - lf_trace_counts["RARE_SPECIMEN_SINGLETON"]) / max(1, total_lf_count), 2),
            "traced_directly_to_herbal_folios_count": total_lf_traced_to_herbal,
            "traced_directly_to_herbal_folios_pct": round(100.0 * total_lf_traced_to_herbal / max(1, total_lf_count), 2),
        },
        "register_label_scaling_comparison": scaling_comparison,
        "translated_registers": translated_registers,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("=== ATTACK 117: 44-REGISTER PHARMACEUTICAL TRANSLATOR & @Lf TRACEABILITY ===")
    tr_stat = summary["lf_botanical_specimen_traceability"]
    print(f"@Lf Specimen Traceability: {tr_stat['resolved_to_herbal_or_compound_count']}/{tr_stat['total_lf_labels']} ({tr_stat['resolved_to_herbal_or_compound_pct']}%) resolved ({tr_stat['traced_directly_to_herbal_folios_count']} = {tr_stat['traced_directly_to_herbal_folios_pct']}% traced directly to Herbal $I=H folios)!")
    print("  Breakdown:", tr_stat["trace_type_breakdown"])
    print("Multi-Specimen (n_lf >= 4) vs Sparse (n_lf <= 1) Registers:")
    print("  Multi-Specimen:", scaling_comparison["multi_specimen_registers_lf_ge_4"])
    print("  Sparse/Unlbl:  ", scaling_comparison["sparse_or_unlabelled_registers_lf_le_1"])


if __name__ == "__main__":
    main()
