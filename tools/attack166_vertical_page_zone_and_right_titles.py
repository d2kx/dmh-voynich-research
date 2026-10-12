#!/usr/bin/env python3
"""
Attack 166 (Phase 177 / Discovery 183):
The Right-Justified Herbal Titles (=Pt) & Vertical Page-Zone Anatomy Stratification.

Analyzes all right-justified title lines (=Pt / @Pt) in data/ZL3b-n.txt, tests their
local-folio and cross-section (Pharmaceutical P / Starred Recipes S) routing, and
compares the Upper Blossom/Leaf Zone vs Lower Stalk/Root Zone across all 112 Herbal folios.
"""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZL_PATH = ROOT / "data" / "ZL3b-n.txt"
OUT_JSON = ROOT / "data" / "attack166_vertical_page_zone_and_right_titles.json"

GALLOWS = set("pfkt")


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[^a-zA-Z0-9]", "", t)
    return t.lower().strip()


def canonical_stem(w: str) -> str:
    s = w
    for p in ("pold", "qo", "ol", "ot", "ok", "op", "od", "ch", "sh", "da", "sa", "yk", "yd", "o", "d", "s", "y", "l"):
        if s.startswith(p) and len(s) > len(p) + 1:
            s = s[len(p):]
            break
    for suf in ("eedy", "edy", "aiin", "ain", "iin", "oldy", "aldy", "ary", "ory", "ody", "am", "om", "ol", "or", "al", "ar", "dy", "y"):
        if s.endswith(suf) and len(s) > len(suf):
            s = s[:-len(suf)]
            break
    return s or w


def main():
    lines = ZL_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()

    current_section = "Unknown"
    folio_lines = {}
    section_vocab = {}
    section_stems = {}
    right_titles = []

    for line in lines:
        if line.startswith("#"):
            continue
        m_meta = re.match(r"^<f[0-9rv]+[0-9]*>\s*<!([^>]+)>", line)
        if m_meta:
            meta = m_meta.group(1)
            m_sec = re.search(r"\$I=([A-Z])", meta)
            if m_sec:
                current_section = m_sec.group(1)
            continue

        m_line = re.match(r"^<(f[0-9rv]+[0-9]*)\.([^,>]+)(?:,([^>]+))?>\s+(.*)$", line)
        if not m_line:
            continue
        folio, lnum, ltype, body = m_line.groups()
        ltype = ltype or "P0"

        body_clean = re.sub(r"<!.*?>", "", body).replace("<->", " ")
        toks = [clean_tok(t) for t in re.split(r"[.\s,]+", body_clean) if clean_tok(t)]
        if not toks:
            continue

        folio_lines.setdefault(folio, []).append((lnum, ltype, current_section, toks))
        section_vocab.setdefault(current_section, Counter()).update(toks)
        section_stems.setdefault(current_section, Counter()).update(canonical_stem(w) for w in toks)

        if "Pt" in ltype or "Pc" in ltype:
            right_titles.append({
                "folio": folio,
                "locus": f"{folio}.{lnum}",
                "ltype": ltype,
                "section": current_section,
                "tokens": toks,
                "title_text": " ".join(toks),
                "stems": [canonical_stem(w) for w in toks],
            })

    # Enrich right_titles with local folio and cross-section matches
    p_vocab = section_vocab.get("P", Counter())
    s_vocab = section_vocab.get("S", Counter())
    b_vocab = section_vocab.get("B", Counter())
    p_stems = section_stems.get("P", Counter())
    s_stems = section_stems.get("S", Counter())

    exact_in_medical = 0
    stem_in_medical = 0
    local_stem_echo = 0

    for rt in right_titles:
        folio = rt["folio"]
        other_toks = [
            w
            for lnum, lt, sec, tlist in folio_lines.get(folio, [])
            if f"{folio}.{lnum}" != rt["locus"]
            for w in tlist
        ]
        other_stems = set(canonical_stem(w) for w in other_toks)

        has_local_stem = any(st in other_stems for st in rt["stems"])
        has_exact_med = any((w in p_vocab or w in s_vocab or w in b_vocab) for w in rt["tokens"])
        has_stem_med = any((st in p_stems or st in s_stems) for st in rt["stems"])

        rt["local_folio_stem_echo"] = has_local_stem
        rt["exact_match_in_P_S_B"] = has_exact_med
        rt["stem_match_in_P_S"] = has_stem_med
        rt["hits_in_Pharma_P"] = sum(p_vocab[w] for w in rt["tokens"])
        rt["hits_in_Recipes_S"] = sum(s_vocab[w] for w in rt["tokens"])
        rt["hits_in_Balneo_B"] = sum(b_vocab[w] for w in rt["tokens"])

        if has_local_stem:
            local_stem_echo += 1
        if has_exact_med:
            exact_in_medical += 1
        if has_stem_med:
            stem_in_medical += 1

    # Compare Paragraph-Opening Lines (<%>) vs Paragraph-Closing Coda Lines (<$>) across all 112 Herbal folios
    top_zone_words = []
    bottom_zone_words = []
    herbal_folios_count = 0

    for folio, flist in folio_lines.items():
        if not flist or flist[0][2] != "H":
            continue
        prose_lines = [tlist for lnum, lt, sec, tlist in flist if "Pt" not in lt and not lt.startswith("@L")]
        n_lines = len(prose_lines)
        if n_lines < 4:
            continue
        herbal_folios_count += 1
        k = max(1, int(round(n_lines * 0.25)))
        for tlist in prose_lines[:k]:
            top_zone_words.extend(tlist)
        for tlist in prose_lines[-k:]:
            bottom_zone_words.extend(tlist)

    def zone_profile(words: list[str]) -> dict:
        n = len(words)
        return {
            "token_count": n,
            "init_gallows_rate": round(sum(1 for w in words if w[0] in GALLOWS) / n, 4),
            "ch_sh_infusion_rate": round(sum(1 for w in words if w.startswith(("ch", "sh"))) / n, 4),
            "o_nominal_rate": round(sum(1 for w in words if w.startswith("o")) / n, 4),
            "d_take_rate": round(sum(1 for w in words if w.startswith("d")) / n, 4),
            "final_y_nominal_rate": round(sum(1 for w in words if w.endswith("y")) / n, 4),
            "final_m_stop_rate": round(sum(1 for w in words if w.endswith("m")) / n, 4),
            "final_ol_or_medium_rate": round(sum(1 for w in words if w.endswith(("ol", "or"))) / n, 4),
            "root_stem_ar_or_kar_rate": round(
                sum(1 for w in words if any(sub in w for sub in ("kar", "kor", "tar", "rar", "oror", "dar"))) / n, 4
            ),
            "top_words": [w for w, _ in Counter(words).most_common(12)],
        }

    top_prof = zone_profile(top_zone_words)
    bot_prof = zone_profile(bottom_zone_words)

    n_rt = max(1, len(right_titles))
    result = {
        "attack": "Attack 166 (Phase 177 / Discovery 183)",
        "right_justified_titles_summary": {
            "total_right_and_centered_titles": len(right_titles),
            "local_folio_stem_echo_count": local_stem_echo,
            "local_folio_stem_echo_rate": round(local_stem_echo / n_rt, 4),
            "exact_match_in_P_S_B_count": exact_in_medical,
            "exact_match_in_P_S_B_rate": round(exact_in_medical / n_rt, 4),
            "stem_match_in_P_S_count": stem_in_medical,
            "stem_match_in_P_S_rate": round(stem_in_medical / n_rt, 4),
        },
        "right_justified_titles_table": right_titles,
        "herbal_vertical_zone_stratification": {
            "herbal_folios_analyzed": herbal_folios_count,
            "upper_blossom_leaf_zone_top25pct": top_prof,
            "lower_stalk_root_zone_bottom25pct": bot_prof,
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(
        f"Right-Justified & Centered Titles (=Pt / +Pc): n={len(right_titles)} | "
        f"Local Folio Stem Echo={local_stem_echo}/{len(right_titles)} ({local_stem_echo/n_rt*100:.1f}%) | "
        f"Exact Match in Medical (P/S/B)={exact_in_medical}/{len(right_titles)} ({exact_in_medical/n_rt*100:.1f}%) | "
        f"Stem Match in P/S={stem_in_medical}/{len(right_titles)} ({stem_in_medical/n_rt*100:.1f}%)"
    )
    print("Upper Blossom/Leaf Zone vs Lower Stalk/Root Zone on 112 Herbal Folios:")
    print(f"  Upper 30% (n={top_prof['token_count']}): gallows={top_prof['init_gallows_rate']*100:.1f}%, final_m={top_prof['final_m_stop_rate']*100:.2f}%, d_take={top_prof['d_take_rate']*100:.1f}%")
    print(f"  Lower 30% (n={bot_prof['token_count']}): gallows={bot_prof['init_gallows_rate']*100:.1f}%, final_m={bot_prof['final_m_stop_rate']*100:.2f}%, d_take={bot_prof['d_take_rate']*100:.1f}%")


if __name__ == "__main__":
    main()
