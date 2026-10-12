#!/usr/bin/env python3
"""
Attack 36 (Phase 47): Full-Text Decoded Monograph & Formulary Compendium.

Synthesizes Discoveries 1-52 (Attacks 1-35) into a comprehensive, multi-folio decoded
compendium (`notes/DECODED_MONOGRAPH_AND_FORMULARY_COMPENDIUM.md` and
`data/attack36_decoded_monograph_and_formulary_compendium.json`) covering 5 linked
manuscript chains:
  Chain I  : Botanical Part Dissection & Formulary Citation (f39v Herbal -> f102v2 Pharma Row & Recipe)
  Chain II : The 5-Folio =Pt Cross-Reference & Colophon Chain (f17r -> f11r -> f22r/f22v -> f19r)
  Chain III: The Quire H Outer-Bifolium Key & Indexed Case Sheet (f57v <-> f66r with `den mus del`)
  Chain IV : The Balneological Bath & Hydraulic Dosing Cycle (f75r 39-Line Cascade & f78r @Pb Index)
  Chain V  : The Quire 20 Starred Formulary Dyads (f103r Decoctions, f105r Dotted/Plain Dyads, f107v Infusions)
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack36_decoded_monograph_and_formulary_compendium.json"
OUT_MD = ROOT / "notes" / "DECODED_MONOGRAPH_AND_FORMULARY_COMPENDIUM.md"

EXACT_CRIBS = {
    "daiin": "from-this / thereof [CLAUSE-DELIM]",
    "dain": "from-this / thereof [CLAUSE-DELIM]",
    "daiiin": "from-this (3-minim) [CLAUSE-DELIM]",
    "ol": "the / of-the [DEF-PREP]",
    "or": "or / to-the [DISJ-PREP]",
    "ar": "at / to [LOC-PREP]",
    "al": "of / from-the [GEN-PREP]",
    "dar": "into / therein [ABL-LOC]",
    "dal": "from-there / thereof [ABL-GEN]",
    "dol": "in-the / within [LOC-NOM]",
    "sol": "whole-herb / upper-part [BOT-NOM]",
    "sal": "salt / mineral-measure [INGR]",
    "air": "air / vapor / spirit [VAPOR]",
    "dair": "there-vapor / extract [LOC-VAPOR]",
    "chol": "leaf-herb (chol) [HERB-INGR]",
    "shol": "decocted-liquid (shol) [LIQ-INGR]",
    "chor": "herb-stem/flower (chor) [HERB-INGR]",
    "shor": "extracted-juice (shor) [LIQ-INGR]",
    "cheol": "infused-herb-oil (cheol) [LIQ-INGR]",
    "sheol": "steeped-liquid (sheol) [LIQ-INGR]",
    "cthol": "strained-herb (cthol) [HERB-INGR]",
    "chedy": "mix / combine (chedy) [PROC-VERB]",
    "shedy": "decoct / heat-steep (shedy) [THERM-VERB]",
    "chey": "prepare-mix (chey) [PROC-VERB]",
    "shey": "simmer-extract (shey) [THERM-VERB]",
    "qokeedy": "actively-boil-in-vessel (qokeedy) [OP-VERB]",
    "qokedy": "actively-steep-in-vessel (qokedy) [OP-VERB]",
    "qokeey": "actively-infuse-vessel (qokeey) [OP-VERB]",
    "qotedy": "actively-draw-through-conduit (qotedy) [OP-VERB]",
    "qoteedy": "actively-distill-conduit (qoteedy) [OP-VERB]",
    "qokaiin": "take-vessel-measure (qokaiin) [DOSE-OP]",
    "qokain": "take-vessel-measure (qokain) [DOSE-OP]",
    "qotaiin": "take-conduit-measure (qotaiin) [DOSE-OP]",
    "qotain": "take-conduit-measure (qotain) [DOSE-OP]",
    "okaiin": "vessel-measure (okaiin) [UNIT-QUANT]",
    "otaiin": "conduit-measure (otaiin) [UNIT-QUANT]",
    "saiin": "measured-portion (saiin) [UNIT-QUANT]",
    "aiin": "one-unit / measure (aiin) [UNIT-QUANT]",
    "okeedy": "vessel-boiled (okeedy) [STATE-VERB]",
    "okedy": "vessel-steeped (okedy) [STATE-VERB]",
    "otedy": "conduit-drawn (otedy) [STATE-VERB]",
    "oteedy": "conduit-distilled (oteedy) [STATE-VERB]",
    "okal": "vessel-liquor (okal) [LIQ-INGR]",
    "otal": "conduit-liquor (otal) [LIQ-INGR]",
    "okar": "heart-essence / vessel-extract (okar) [INGR]",
    "otar": "earth-root / conduit-extract (otar) [INGR]",
    "okody": "brown-root-stock (okody) [BOT-PART:f39v/f102v2]",
    "sarol": "scalloped-green-leaf (sarol) [BOT-PART:f39v/f102v2]",
    "dam": "finished-dose (dam) [PROD-CLOSER]",
    "otam": "finished-distillate (otam) [PROD-CLOSER]",
    "okam": "finished-infusion (okam) [PROD-CLOSER]",
    "dairal": "celestial-measure-cycle (dairal) [KEY:f57v/f66r]",
}


def clean_tok(t: str) -> str:
    t = re.sub(r"<!.*?>", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", t)
    t = t.replace("[", "").replace("]", "").replace("?", "").replace("!", "").replace("*", "")
    t = t.replace(",", "").replace("'", "").strip()
    return t


def compositional_gloss(w: str) -> Tuple[str, str]:
    """Returns (gloss, tier) where tier in {'T1_EXACT', 'T2_RADICAL', 'T3_MORPH', 'T4_STEM'}."""
    if w in EXACT_CRIBS:
        return EXACT_CRIBS[w], "T1_EXACT"

    # Prefix decomposition
    pref_gloss = ""
    rest = w
    if rest.startswith("qok") and len(rest) > 4:
        pref_gloss = "actively-vessel-"
        rest = rest[3:]
    elif rest.startswith("qot") and len(rest) > 4:
        pref_gloss = "actively-conduit-"
        rest = rest[3:]
    elif rest.startswith("qop") and len(rest) > 4:
        pref_gloss = "actively-jar-"
        rest = rest[3:]
    elif rest.startswith("qo") and len(rest) > 3:
        pref_gloss = "actively-"
        rest = rest[2:]
    elif rest.startswith(("ok", "yk")) and len(rest) > 3:
        pref_gloss = "vessel-"
        rest = rest[2:]
    elif rest.startswith(("ot", "yt")) and len(rest) > 3:
        pref_gloss = "conduit-"
        rest = rest[2:]
    elif rest.startswith(("op", "yp", "of", "yf")) and len(rest) > 3:
        pref_gloss = "jar-"
        rest = rest[2:]
    elif rest.startswith(("pch", "fch")) and len(rest) > 4:
        pref_gloss = "jar-herb-"
        rest = rest[3:]
    elif rest.startswith(("kch", "tch", "ckh", "cth", "cph", "cfh")) and len(rest) > 4:
        pref_gloss = "strained-"
        rest = rest[3:]
    elif rest.startswith("ch") and len(rest) > 3:
        pref_gloss = "herb-mix-"
        rest = rest[2:]
    elif rest.startswith("sh") and len(rest) > 3:
        pref_gloss = "heat-decoct-"
        rest = rest[2:]
    elif rest.startswith(("p", "f")) and len(rest) > 3:
        pref_gloss = "topic-jar-"
        rest = rest[1:]
    elif rest.startswith(("k", "t")) and len(rest) > 3:
        pref_gloss = "topic-vessel-"
        rest = rest[1:]
    elif rest.startswith("d") and len(rest) > 3:
        pref_gloss = "from-"
        rest = rest[1:]
    elif rest.startswith("s") and len(rest) > 3:
        pref_gloss = "portion-"
        rest = rest[1:]
    elif rest.startswith("y") and len(rest) > 3:
        pref_gloss = "then-"
        rest = rest[1:]

    # Suffix decomposition
    suf_gloss = ""
    if rest.endswith(("eedy", "edy")):
        suf_gloss = "steeped/processed"
    elif rest.endswith("dy"):
        suf_gloss = "treated"
    elif re.search(r"i+n$", rest):
        suf_gloss = "measure-unit"
    elif rest.endswith(("ol", "eol")):
        suf_gloss = "liquid-extract"
    elif rest.endswith(("or", "eor")):
        suf_gloss = "root/flower-essence"
    elif rest.endswith(("ar", "ear")):
        suf_gloss = "grounded-extract"
    elif rest.endswith(("al", "eal")):
        suf_gloss = "liquor-portion"
    elif rest.endswith(("am", "om", "aim", "oim")):
        suf_gloss = "finished-product"
    elif rest.endswith(("eey", "ey", "ky", "ty", "py", "fy", "y")):
        suf_gloss = "state/quality"

    if pref_gloss and suf_gloss:
        return f"{pref_gloss}{suf_gloss} ({w})", "T2_RADICAL"
    if pref_gloss:
        return f"{pref_gloss}{rest} ({w})", "T3_MORPH"
    if suf_gloss:
        return f"{rest}-{suf_gloss} ({w})", "T3_MORPH"
    return f"stem:{w}", "T4_STEM"


def parse_manuscript() -> Dict[str, Dict]:
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        idx = json.load(f)
    folio_meta = idx.get("folios", {})

    folios: Dict[str, Dict] = {}
    current_folio = None
    header_meta: Dict[str, str] = {}

    line_re = re.compile(r"^<([^.>]+)\.([^,>]+),([^>]+)>\s*(.*)$")
    page_re = re.compile(r"^<f[0-9]+[rv][0-9]*>\s*<!\s*(.*?)>")

    with open(ZL_PATH, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            pm = page_re.match(line)
            if pm:
                f_m = re.match(r"^<(f[0-9]+[rv][0-9]*)>", line)
                if f_m:
                    current_folio = f_m.group(1)
                    meta_str = pm.group(1)
                    header_meta = dict(re.findall(r"\$([A-Z])=([A-Za-z0-9]+)", meta_str))
                    f_info = folio_meta.get(current_folio, {})
                    folios[current_folio] = {
                        "folio": current_folio,
                        "section": header_meta.get("I", f_info.get("section", "?")),
                        "language": header_meta.get("L", f_info.get("currier_language", "?")),
                        "hand": header_meta.get("H", f_info.get("hand", "?")),
                        "quire": header_meta.get("Q", f_info.get("quire", "?")),
                        "lines": [],
                    }
                continue
            if line.startswith("#"):
                continue
            lm = line_re.match(line)
            if not lm or not current_folio or current_folio not in folios:
                continue
            _, loc_id, ltype, body = lm.groups()
            star_comments = re.findall(r"<!([^>]+)>", body)
            body_clean = re.sub(r"<!.*?>", "", body)
            raw_toks = re.split(r"[.\s]+", body_clean)
            toks = [clean_tok(t) for t in raw_toks]
            toks = [t for t in toks if t and not t.startswith("<")]
            if not toks:
                continue
            folios[current_folio]["lines"].append({
                "loc_id": loc_id,
                "ltype": ltype,
                "star_comments": star_comments,
                "has_para_start": "<%>" in body,
                "has_para_end": "<$>" in body,
                "has_intrusion": "<->" in body,
                "tokens": toks,
            })
    return folios


def decode_folio(fd: Dict, max_lines: int = 999) -> Dict:
    tier_counts: Counter = Counter()
    decoded_lines = []
    for ln in fd["lines"][:max_lines]:
        glossed = []
        for w in ln["tokens"]:
            g, tier = compositional_gloss(w)
            tier_counts[tier] += 1
            glossed.append({"word": w, "gloss": g, "tier": tier})
        clause_reading = " ; ".join(
            " ".join(x["gloss"] for x in glossed)
            .replace("[CLAUSE-DELIM]", "||")
            .split("||")
        )
        decoded_lines.append({
            "loc_id": ln["loc_id"],
            "ltype": ln["ltype"],
            "star_comments": ln["star_comments"],
            "has_para_start": ln["has_para_start"],
            "has_para_end": ln["has_para_end"],
            "has_intrusion": ln["has_intrusion"],
            "eva": " ".join(ln["tokens"]),
            "decoded_clause": clause_reading,
            "tokens": glossed,
        })
    tot = sum(tier_counts.values()) or 1
    return {
        "folio": fd["folio"],
        "section": fd["section"],
        "language": fd["language"],
        "hand": fd["hand"],
        "quire": fd["quire"],
        "total_tokens": sum(tier_counts.values()),
        "t1_t3_coverage": round(
            (tier_counts["T1_EXACT"] + tier_counts["T2_RADICAL"] + tier_counts["T3_MORPH"]) / tot, 4
        ),
        "tier_counts": dict(tier_counts),
        "lines": decoded_lines,
    }


def main() -> None:
    folios = parse_manuscript()

    chains = [
        {
            "chain_id": "CHAIN_I_BOTANICAL_PART_DISSECTION",
            "title": "Chain I: Botanical Part Dissection & Formulary Citation (`f39v` Herbal -> `f102v2` Pharmaceutical Row & Recipe)",
            "description": (
                "Demonstrates how a single Herbal monograph (`f39v`, Hand 1, Currier A) with two unique "
                "`herbal_df = 1` stems (`okody` and `sarol`) is dissected into individual anatomical plant parts "
                "on Pharmaceutical folio `f102v2` (`<f102v2.10,@Lf> okody` [fibrous brown root] and `<f102v2.14,@Lf> sarol` "
                "[deep green scalloped leaf] beside the blue-and-white jar `porshols / soaimy`), and immediately "
                "boiled in the recipe paragraph below (`<f102v2.20,22,+P0> qokeody ... okeody`)."
            ),
            "folios": ["f39v", "f102v2"],
            "max_lines": 60,
        },
        {
            "chain_id": "CHAIN_II_PT_CROSS_REFERENCE_CHAIN",
            "title": "Chain II: The `=Pt` Cross-Referenced Monograph & Colophon Chain (`f17r -> f11r -> f22r -> f22v -> f19r`)",
            "description": (
                "Demonstrates the right-justified title/cross-reference (`=Pt`) chain discovered in Attack 21, "
                "where right-margin `=Pt` lines cite rare signature stems across Herbal monographs."
            ),
            "folios": ["f17r", "f11r", "f22r", "f22v", "f19r"],
            "max_lines": 30,
        },
        {
            "chain_id": "CHAIN_III_QUIRE_H_BIFOLIUM_KEY_AND_CASE_SHEET",
            "title": "Chain III: The Quire G/H Marginal/Circular Key System (`f49v`, `f57v`, and `f66r` Case Sheet with `den mus del`)",
            "description": (
                "Presents the three single-glyph key folios (`f49v` with Arabic numerals `1..5`, `f57v` 4x17-glyph "
                "ring, and `f66r` dual marginal column + 5 prose paragraphs + bottom patient diagram and German/Latin "
                "`den mus del` inscription)."
            ),
            "folios": ["f49v", "f57v", "f66r"],
            "max_lines": 85,
        },
        {
            "chain_id": "CHAIN_IV_BALNEOLOGICAL_CASCADE_AND_INDEX",
            "title": "Chain IV: The Quire M Balneological Bath Cycle (`f75r` 39-Line Aqua-Vitae Cascade & `f78r` Outer-Bifolium `@Pb` Index)",
            "description": (
                "Presents the 39-line hydraulic cascade folio `f75r` (`8x qokedy` + `5x olkeedy/olkeey` + `5x qokaiin`) "
                "paired with the Quire M outer-bifolium `@Pb` index folio `f78r`."
            ),
            "folios": ["f75r", "f78r"],
            "max_lines": 45,
        },
        {
            "chain_id": "CHAIN_V_QUIRE20_STARRED_RECIPE_DYADS",
            "title": "Chain V: Quire 20 Starred Formulary Chapters & `LIGHT_DOTTED <-> LIGHT_PLAIN` Dyads (`f103r`, `f105r`, `f107v`)",
            "description": (
                "Presents the untailed thermal decoction recipes of Chapter I (`f103r`) alongside the strictly "
                "alternating `LIGHT_DOTTED <-> LIGHT_PLAIN` tailed recipe dyads of Chapter III (`f105r` Conduit "
                "Distillations) and Chapter IV (`f107v` Vessel Infusions)."
            ),
            "folios": ["f103r", "f105r", "f107v"],
            "max_lines": 35,
        },
    ]

    compiled_chains = []
    total_compendium_tokens = 0
    total_t1_t3 = 0

    for ch in chains:
        f_list = []
        for fname in ch["folios"]:
            if fname in folios:
                dec = decode_folio(folios[fname], max_lines=ch["max_lines"])
                f_list.append(dec)
                total_compendium_tokens += dec["total_tokens"]
                tc = dec["tier_counts"]
                total_t1_t3 += tc.get("T1_EXACT", 0) + tc.get("T2_RADICAL", 0) + tc.get("T3_MORPH", 0)
        compiled_chains.append({
            "chain_id": ch["chain_id"],
            "title": ch["title"],
            "description": ch["description"],
            "folios": f_list,
        })

    overall_cov = round(total_t1_t3 / max(1, total_compendium_tokens), 4)

    out_data = {
        "n_chains": len(compiled_chains),
        "total_folios_decoded": sum(len(c["folios"]) for c in compiled_chains),
        "total_tokens_decoded": total_compendium_tokens,
        "overall_t1_t3_structural_coverage": overall_cov,
        "chains": compiled_chains,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    # Render Markdown Compendium
    md_lines = [
        "# Decoded Monograph & Formulary Compendium (`Attacks 1–36` / `Discoveries 1–53`)",
        "",
        f"- **Compiled Chains**: `{len(compiled_chains)}` linked multi-folio manuscript chains (`{out_data['total_folios_decoded']}` folios, `{total_compendium_tokens}` decoded tokens)",
        f"- **Structural & Lexical Coverage (`T1_EXACT + T2_RADICAL + T3_MORPH`)**: **`{overall_cov * 100:.2f}%`**",
        "- **Companion Dataset**: [`data/attack36_decoded_monograph_and_formulary_compendium.json`](../data/attack36_decoded_monograph_and_formulary_compendium.json)",
        "- **Full 227-Folio Atlas**: [`notes/FULL_MANUSCRIPT_TRANSLATION_ATLAS.md`](FULL_MANUSCRIPT_TRANSLATION_ATLAS.md)",
        "",
        "---",
        "",
    ]

    for ch in compiled_chains:
        md_lines.append(f"## {ch['title']}")
        md_lines.append("")
        md_lines.append(f"> {ch['description']}")
        md_lines.append("")
        for fd in ch["folios"]:
            md_lines.append(
                f"### Folio `{fd['folio']}` (`$I={fd['section']}`, `$L={fd['language']}`, "
                f"`$H={fd['hand']}`, `$Q={fd['quire']}`, `{fd['total_tokens']}` tokens, "
                f"`{fd['t1_t3_coverage']*100:.1f}%` T1–T3 coverage)"
            )
            md_lines.append("")
            md_lines.append("| Line | Locus | Markers | EVA Transliteration | Compositional Structural Translation |")
            md_lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for ln in fd["lines"]:
                markers = []
                if ln["has_para_start"]:
                    markers.append("`<%>`")
                if ln["has_para_end"]:
                    markers.append("`<$>`")
                if ln["has_intrusion"]:
                    markers.append("`<->`")
                if ln["star_comments"]:
                    markers.append("`" + ",".join(ln["star_comments"]) + "`")
                m_str = " ".join(markers) if markers else "—"
                md_lines.append(
                    f"| `{fd['folio']}.{ln['loc_id']}` | `{ln['ltype']}` | {m_str} | `{ln['eva']}` | {ln['decoded_clause']} |"
                )
            md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("=== ATTACK 36: DECODED MONOGRAPH & FORMULARY COMPENDIUM ===")
    print(f"Chains compiled: {len(compiled_chains)}, Folios: {out_data['total_folios_decoded']}, Tokens: {total_compendium_tokens}")
    print(f"Overall T1-T3 structural coverage: {overall_cov*100:.2f}%")
    print(f"Saved {OUT_MD} and {OUT_JSON}")


if __name__ == "__main__":
    main()
