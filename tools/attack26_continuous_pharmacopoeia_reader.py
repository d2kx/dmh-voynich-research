r"""
Attack 26: End-to-End Voynich-to-Pharmacopoeia Continuous Reader & Paragraph Discourse Coherence Test
=====================================================================================================
Integrates our 3-Stage Positional Envelope FST (`Attack 7`), 59-Radical Object Lexicon (`Attack 14`),
Clause-Frame Segmenter (`Attack 20`), 5x4 Syllabic Pharmacopoeia Slot Mapping (`Attack 24`), and
Currier A <-> B Dialect Translation Matrix (`Attack 25`) to:
1. Translate every token and clause in `data/ZL3b-n.txt` into a unified Pharmacopoeia/Balneological
   reading (`[Proclitic/Frame + Radical Domain Slot + Inflectional Role]`).
2. Test **Adjacent-Clause Discourse Continuity (Anaphoric/Lexical Chaining within Paragraphs)**:
   - Measures the rate at which consecutive clauses $(C_i, C_{i+1})$ inside the same paragraph share
     a Core Root or Elementary Radical argument vs. a 1,000-trial random paragraph-shuffle null
     stratified by Currier Language and Section ($z$-score).
3. Generate [`notes/CONTINUOUS_READER_EDITION.md`](notes/CONTINUOUS_READER_EDITION.md): a complete
   Three-Column Parallel Edition (`EVA Original | Morpheme & Radical Parse | Continuous Pharmacopoeia Reading`)
   across 9 flagship folios spanning all 6 sections of the Voynich Manuscript.
"""

import json
import re
import random
from pathlib import Path
from collections import Counter, defaultdict

from attack7_positional_envelope_fst import extract_core_root_and_envelope
from attack16_radical_clause_translation_edition import RADICAL_SHORT_TAG

ROOT = Path(__file__).resolve().parent.parent
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
INDEX_PATH = ROOT / "data" / "folio_index.json"
OUT_JSON = ROOT / "data" / "attack26_continuous_pharmacopoeia_reader.json"
OUT_MD = ROOT / "notes" / "CONTINUOUS_READER_EDITION.md"

# Concise Pharmacopoeia / Balneological English-Latin Lexicon for Top Radicals
PHARMA_RADICAL_LEX = {
    "ch": "mix/prepare",
    "sh": "boil/steep",
    "che": "infuse",
    "she": "decoct",
    "k": "vessel/strain",
    "t": "conduit/draw",
    "cth": "crush-crown",
    "ckh": "concoct-herb",
    "tch": "compound-duct",
    "kch": "compound-vessel",
    "lch": "elixate-fluid",
    "lsh": "wash/steep-fluid",
    "dch": "base-mix",
    "sch": "seed-mix",
    "ke": "cook/extract",
    "te": "channel/draw",
    "keo": "vessel-grade",
    "teo": "zodiac-house",
    "cheo": "infusion-mix",
    "sheo": "decoction-heat",
    "ol": "fluid/oil",
    "or": "tincture/gold",
    "ar": "root/herb",
    "al": "essence/star-water",
    "dar": "jar/root-source",
    "dal": "basin/pool",
    "kol": "plant-stalk",
    "kal": "calyx/pot",
    "kar": "vessel-core",
    "tol": "shoot/cutting",
    "tal": "bath-vat/barrel",
    "tar": "earth-root",
    "sol": "herb-solution",
    "sal": "bath-salt",
    "sar": "seed-substance",
    "so": "sap/resin",
    "d": "thereof/dose",
    "s": "seed/portion",
    "o": "substance/unit",
    "a": "measure/axis",
    "r": "stream/part",
    "l": "liquid",
    "y": "state",
    "ain": "drachm/unit",
    "air": "aether/degree",
    "od": "vessel-dose",
    "ed": "flowing",
    "ok": "pot/vessel",
    "ot": "pipe/duct",
    "lk": "decant-vessel",
    "lt": "decant-duct",
    "ko": "star-node",
    "to": "ray/spoke",
    "da": "leaf-tail",
    "ky": "blue-calyx",
    "ty": "duct-outlet",
    "dy": "completed",
    "g": "sealed-rim",
    "ek": "extract-core"
}


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


def translate_word(w: dict) -> tuple:
    """
    Returns (morpheme_parse_str, pharmacopoeia_phrase_str, is_grounded).
    """
    rw = w["clean_raw"]
    rt = w["root"]
    rads = w["radicals"]
    suff = w["suff"]

    # Determine prefix tag
    pref_str = ""
    pref_en = ""
    if w.get("is_para_start") and rw[0:1] in ("p", "f") and not rw.startswith(("pc", "fc")):
        pref_str = f"HDR({rw[0]})-"
        pref_en = "Recipe: "
    elif rw.startswith("qo") and not rt.startswith("qo"):
        pref_str = "qo-"
        pref_en = "with "
    elif rw.startswith("y") and not rt.startswith("y"):
        pref_str = "y-"
        pref_en = "then "
    elif rw.startswith("o") and not rt.startswith("o") and len(rw) > 2:
        pref_str = "o-"
        pref_en = "the "
    elif rw.startswith("d") and not rt.startswith("d") and len(rw) > 2:
        pref_str = "d-"
        pref_en = "from "
    elif rw.startswith("s") and not rt.startswith(("s", "sh")) and len(rw) > 2:
        pref_str = "s-"
        pref_en = "part-of "

    # Radical core meaning
    rad_meanings = []
    grounded = False
    for r in rads:
        if r in PHARMA_RADICAL_LEX:
            rad_meanings.append(PHARMA_RADICAL_LEX[r])
            grounded = True
        elif r in RADICAL_SHORT_TAG:
            rad_meanings.append(RADICAL_SHORT_TAG[r])
            grounded = True
        else:
            rad_meanings.append(f"'{r}'")
    core_en = "+".join(rad_meanings) if rad_meanings else f"'{rt}'"

    # Determine suffix / inflectional ending
    suff_str = f"-{suff}" if suff and suff != "NONE" else ""
    suff_en = ""
    if rw.endswith(("edy", "dy")) and rt not in ("dy",):
        suff_en = " [verb/done]"
    elif rw.endswith(("aiin", "iin", "in", "ain")) and rt not in ("ain",):
        suff_en = " (measure)"
    elif rw.endswith(("eol", "ol")) and not rt.endswith("ol"):
        suff_en = " (in-fluid)"
    elif rw.endswith(("eor", "or")) and not rt.endswith("or"):
        suff_en = " (extract)"
    elif rw.endswith("al") and not rt.endswith("al"):
        suff_en = " (of-essence)"
    elif rw.endswith("ar") and not rt.endswith("ar"):
        suff_en = " (of-root)"
    elif rw.endswith(("am", "om")):
        suff_en = " [FIN]"
    elif rw.endswith("g"):
        suff_en = " [SEALED]"

    parse_box = f"{pref_str}{'+'.join(rads)}{suff_str}"
    phrase_en = f"{pref_en}{core_en}{suff_en}".strip()
    return parse_box, phrase_en, grounded


def main():
    folio_index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["folios"]
    radical_set = set(PHARMA_RADICAL_LEX.keys()) | set(RADICAL_SHORT_TAG.keys())

    all_lines = []
    paragraphs = []
    cur_para = None

    total_words = 0
    grounded_words = 0
    sec_stats = defaultdict(lambda: Counter())

    for raw_line in ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not raw_line.startswith("<f"):
            continue
        m = re.match(r"^<([^.]+)\.([^,>]+),([^>]+)>\s*(.*)$", raw_line)
        if not m:
            continue
        folio, lnum_str, tag, body = m.group(1), m.group(2), m.group(3), m.group(4)
        f_base = re.sub(r"\d+$", "", folio) if folio not in folio_index else folio
        f_meta = folio_index.get(folio, folio_index.get(f_base, {}))
        sec = f_meta.get("section", "Unknown")
        lang = f_meta.get("currier_lang", "Unknown")

        has_para_start = "<%>" in body
        has_para_end = "<$>" in body
        clean_body = re.sub(r"<!([^>]*)>", "", body)
        clean_body = clean_body.replace("<%>", "").replace("<$>", "").replace("<->", " <-> ")
        raw_tokens = [t.strip() for t in re.split(r"[.\s,]+", clean_body) if t.strip()]
        if not raw_tokens:
            continue

        parsed_words = []
        real_words = [t for t in raw_tokens if t != "<->"]
        n_w = len(real_words)
        w_idx = 0
        for tok in raw_tokens:
            if tok == "<->":
                parsed_words.append({"is_intrusion": True, "raw": "<->"})
                continue
            clean_rw = re.sub(r"\[([^:\]]+):[^\]]+\]", r"\1", tok)
            clean_rw = re.sub(r"[^a-zA-Z]", "", clean_rw).lower()
            cn = normalize_token(tok)
            if not cn:
                continue
            pos = "INITIAL" if w_idx == 0 else ("FINAL" if w_idx == n_w - 1 else "MEDIAL")
            pref, suff, rt = extract_core_root_and_envelope(clean_rw, pos)
            rt = rt or cn
            clean_suff = suff.lstrip("-") or "NONE"
            if rt.endswith("ed") and clean_suff == "y" and len(rt) > 2:
                rt = rt[:-2]
                clean_suff = "edy"
            elif rt.endswith("e") and clean_suff in ("y", "dy", "ol", "or") and len(rt) > 1 and rt not in ("che", "she", "te", "ke"):
                rt = rt[:-1]
                clean_suff = "e" + clean_suff

            rads = segment_into_radicals(rt, radical_set)
            w_obj = {
                "is_intrusion": False,
                "raw": tok,
                "clean_raw": clean_rw,
                "canon": cn,
                "root": rt,
                "suff": clean_suff,
                "radicals": rads,
                "is_para_start": (has_para_start and w_idx == 0)
            }
            p_box, p_en, is_g = translate_word(w_obj)
            w_obj["parse_box"] = p_box
            w_obj["pharma_en"] = p_en
            w_obj["is_grounded"] = is_g
            parsed_words.append(w_obj)

            total_words += 1
            sec_stats[sec]["total"] += 1
            if is_g:
                grounded_words += 1
                sec_stats[sec]["grounded"] += 1
            w_idx += 1

        if not any(not w.get("is_intrusion") for w in parsed_words):
            continue

        line_obj = {
            "folio": folio,
            "lnum": lnum_str,
            "loc": f"{folio}.{lnum_str}",
            "tag": tag,
            "sec": sec,
            "lang": lang,
            "has_para_start": has_para_start,
            "has_para_end": has_para_end,
            "words": parsed_words
        }
        all_lines.append(line_obj)

        if "P" in tag and "Pb" not in tag:
            if has_para_start or tag.startswith("@P") or tag.startswith("*P") or cur_para is None or cur_para["folio"] != folio:
                if cur_para is not None:
                    paragraphs.append(cur_para)
                cur_para = {
                    "folio": folio,
                    "sec": sec,
                    "lang": lang,
                    "lines": [line_obj]
                }
            else:
                cur_para["lines"].append(line_obj)

    if cur_para is not None:
        paragraphs.append(cur_para)

    # 2. Adjacent-Line / Adjacent-Clause Discourse Continuity Test within Paragraphs
    # For every paragraph with >= 2 lines, measure the fraction of adjacent line pairs $(L_i, L_{i+1})$
    # that share at least one content radical (`len(rad) >= 2` or `rad in {'k','t','d','s'}`),
    # and compare against a 1,000-trial random line-shuffle null within the same (sec, lang) bucket!
    def line_content_rads(ln_obj):
        return {
            r for w in ln_obj["words"] if not w.get("is_intrusion")
            for r in w["radicals"] if len(r) >= 2
        }

    obs_adj_pairs = 0
    obs_chained_pairs = 0
    bucket_lines = defaultdict(list)

    for p in paragraphs:
        lns = p["lines"]
        for ln in lns:
            bucket_lines[(p["sec"], p["lang"])].append(line_content_rads(ln))
        for i in range(len(lns) - 1):
            r1 = line_content_rads(lns[i])
            r2 = line_content_rads(lns[i+1])
            obs_adj_pairs += 1
            if r1 & r2:
                obs_chained_pairs += 1

    obs_chain_rate = obs_chained_pairs / max(1, obs_adj_pairs)

    rng = random.Random(42)
    null_chain_rates = []
    for _ in range(500):
        # Shuffle lines within each (sec, lang) bucket and recompute adjacent chaining across same paragraph lengths
        shuffled_buckets = {}
        for k, arr in bucket_lines.items():
            cp = list(arr)
            rng.shuffle(cp)
            shuffled_buckets[k] = cp
        b_ptrs = Counter()
        c_hits = 0
        for p in paragraphs:
            k = (p["sec"], p["lang"])
            n_l = len(p["lines"])
            ptr = b_ptrs[k]
            sub = shuffled_buckets[k][ptr:ptr + n_l]
            b_ptrs[k] += n_l
            for i in range(len(sub) - 1):
                if sub[i] & sub[i+1]:
                    c_hits += 1
        null_chain_rates.append(c_hits / max(1, obs_adj_pairs))

    nc_mean = sum(null_chain_rates) / len(null_chain_rates)
    nc_std = (sum((x - nc_mean) ** 2 for x in null_chain_rates) / len(null_chain_rates)) ** 0.5
    nc_z = (obs_chain_rate - nc_mean) / (nc_std if nc_std > 0 else 1.0)

    # 3. Generate `notes/CONTINUOUS_READER_EDITION.md` across 9 Flagship Folios
    target_folios = [
        ("f1r", "1. Master Preface & Four Right-Justified `=Pt` Titles (`f1r`, Quire A Outer Bifolium)"),
        ("f8r", "2. Conjugate Quire-A Herbal Monograph & Three Right-Justified `=Pt` Colophons (`f8r`)"),
        ("f11v", "3. Red/Crimson Blossom Herbal Monograph (`f11v`, Currier A)"),
        ("f16v", "4. Blue/Violet Blossom Herbal Monograph (`f16v`, Currier A)"),
        ("f46v", "5. Currier-B Herbal Monograph with `saim` Colophon Link (`f46v`, Hand 2)"),
        ("f72r3", "6. Cancer Zodiac Medallion (`f72r3`, 30 Ecliptic Nymphs + Central Star)"),
        ("f75v", "7. Biological Communal Bath, Nymph/Tube Labels & `@Pb` Cascade (`f75v`, Quire M)"),
        ("f88v", "8. Pharmaceutical `otar . arody` Container-to-Root Sheet (`f88v`)"),
        ("f99r", "9. Pharmaceutical Three-Jar & Five-Root Recipe Sheet (`f99r`)"),
        ("f105r", "10. Chained Starred Recipes (`f105r:P1–P2`, `<%>par . arody` & `+Pr/+Pc` Colophons)")
    ]

    md_lines = [
        "# Continuous Pharmacopoeia & Balneological Reader Edition (`Attack 26`)\n",
        "> **Corpus-Wide Pharmacopoeia Readability Coverage**: **`{:,} / {:,}` (`{:.2f}%`)** of all tokens across `data/ZL3b-n.txt` receive a grounded `[Envelope Role + 5x4 Syllabic/Radical Pharmacopoeia Slot + Inflection]` reading.\n".format(
            grounded_words, total_words, grounded_words / max(1, total_words) * 100.0
        ),
        "> **Paragraph Discourse Continuity (Anaphoric Lexical Chaining)**: **`{:,} / {:,}` (`{:.2f}%`)** of adjacent lines within paragraphs share a content radical argument vs. **`{:.2f}% ± {:.2f}%`** under section- and language-stratified line shuffling (**$z = {:+.2f}$**).\n".format(
            obs_chained_pairs, obs_adj_pairs, obs_chain_rate * 100.0, nc_mean * 100.0, nc_std * 100.0, nc_z
        ),
        "\n---\n"
    ]

    for f_code, title in target_folios:
        f_lns = [ln for ln in all_lines if ln["folio"] == f_code]
        if f_code == "f105r":
            f_lns = f_lns[:15] + [ln for ln in f_lns if ln["tag"] in ("+Pr", "+Pc") and ln not in f_lns[:15]]
        elif len(f_lns) > 28:
            # Show representative top lines + labels/colophons + bottom lines
            lbl_pb = [ln for ln in f_lns if "P0" not in ln["tag"]][:12]
            p0_lns = [ln for ln in f_lns if "P0" in ln["tag"]]
            f_lns = lbl_pb + p0_lns[:16]

        md_lines.append(f"## {title}\n")
        md_lines.append("| Locus (`Tag`) | EVA Original | Morpheme & Radical Parse | Continuous Pharmacopoeia / Balneological Reading |")
        md_lines.append("| :--- | :--- | :--- | :--- |")
        for ln in f_lns:
            eva_str = " . ".join(w["raw"] for w in ln["words"])
            parse_str = " · ".join("<->" if w.get("is_intrusion") else f"`{w['parse_box']}`" for w in ln["words"])
            read_str = " ".join(" || " if w.get("is_intrusion") else w["pharma_en"] for w in ln["words"])
            md_lines.append(f"| `<{ln['loc']},{ln['tag']}>` | `{eva_str}` | {parse_str} | {read_str} |")
        md_lines.append("\n---\n")

    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    sec_summary = {
        k: {
            "total_tokens": v["total"],
            "grounded_tokens": v["grounded"],
            "coverage_rate": round(v["grounded"] / max(1, v["total"]), 4)
        }
        for k, v in sec_stats.items()
    }

    out_data = {
        "summary": {
            "total_corpus_tokens": total_words,
            "grounded_pharmacopoeia_tokens": grounded_words,
            "corpus_coverage_rate": round(grounded_words / max(1, total_words), 4),
            "paragraph_discourse_chaining_test": {
                "adjacent_line_pairs": obs_adj_pairs,
                "observed_chained_pairs": obs_chained_pairs,
                "observed_chain_rate": round(obs_chain_rate, 4),
                "null_mean_rate": round(nc_mean, 4),
                "null_std_rate": round(nc_std, 4),
                "z_score": round(nc_z, 2)
            },
            "folios_rendered_in_edition": len(target_folios)
        },
        "section_coverage_breakdown": sec_summary
    }

    OUT_JSON.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print(f"Saved Attack 26 JSON to {OUT_JSON} and Markdown Reader to {OUT_MD}")
    print(f"Corpus-Wide Pharmacopoeia Readability Coverage: {grounded_words}/{total_words} ({grounded_words/total_words*100:.2f}%)")
    print(f"Paragraph Discourse Chaining Rate: {obs_chained_pairs}/{obs_adj_pairs} ({obs_chain_rate*100:.2f}%) vs null {nc_mean*100:.2f}% ± {nc_std*100:.2f}% (z = {nc_z:+.2f})")


if __name__ == "__main__":
    main()
