#!/usr/bin/env python3
"""
Attack 181 (Discovery 198): The f85r1-f86v6 Rosettes Treatise Envelope,
`=Pt / +Pr` Right-Justified Title/Coda Law & 9-Sphere Map Lexical Coupling.

Investigates:
1. Complete census of all 22 right-justified title/coda lines (`=Pt` standalone titles/signatures
   and `+Pr` right-justified paragraph codas) across all 226 folios in `data/ZL3b-n.txt`:
   folio distribution, word counts, morphological profiles, and lexical/stem coupling to their
   host paragraph and folio.
2. Codicological and lexical anatomy of the 6-panel Rosettes physical sheet (`f85r1`,
   `f85r2`, `f85v2`/`fRos`, `f86v3`, `f86v4`, `f86v5`, `f86v6`).
3. Exact & canonical stem coupling between the outer Rosettes Treatise Envelope
   (`f85r1`, `f85r2`, `f86v3..6`) and the inner `f85v2` (`fRos`) 9-Sphere Cosmos Map, tested
   against 1,000 random Currier B folio sets.
"""

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

random.seed(42)


def clean_tok(t: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", t)
    t = re.sub(r"\[([^]:]+):[^\]]+\]", r"\1", t)
    t = re.sub(r"[\[\]<>@*$?!%'0-9]", "", t)
    return t.strip()


def canonical_stem(w: str) -> str:
    s = w
    s = re.sub(r"ch", "C", s)
    s = re.sub(r"sh", "S", s)
    s = re.sub(r"ii+", "i", s)
    s = re.sub(r"ee+", "e", s)
    for pref in ("qo", "ok", "ot", "op", "of", "ol", "or", "da", "so", "yk", "yt", "yp"):
        if s.startswith(pref) and len(s) - len(pref) >= 2:
            s = s[len(pref):]
            break
    for suf in ("aiin", "oiin", "eiin", "iin", "edy", "eey", "ody", "am", "om", "al", "ar", "ol", "or", "dy", "ey", "in", "y", "m"):
        if s.endswith(suf) and len(s) - len(suf) >= 1:
            s = s[:-len(suf)]
            break
    s = s.replace("C", "ch").replace("S", "sh")
    return s


def main():
    zl_path = Path("data/ZL3b-n.txt")
    idx_path = Path("data/folio_index.json")
    idx = json.loads(idx_path.read_text(encoding="utf-8"))

    line_re = re.compile(r"^<(f(?:Ros|[0-9]+[rv][0-9]*))\.([0-9]+),([^>]+)>\s+(.*)$")

    pt_pr_lines = []
    paragraphs_by_folio = defaultdict(lambda: defaultdict(list))
    folio_tokens = defaultdict(list)
    folio_loci = defaultdict(list)

    curr_para_id = 0
    last_folio = None

    for raw in zl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        m = line_re.match(raw)
        if not m:
            continue
        folio_raw = m.group(1)
        folio = "f85v2" if folio_raw == "fRos" else folio_raw
        line_no = int(m.group(2))
        loc_raw = m.group(3).strip()
        body = m.group(4)

        if folio != last_folio:
            curr_para_id = 1
            last_folio = folio
        if "<%>" in body or loc_raw.startswith("@P"):
            curr_para_id += 1

        body_clean = re.sub(r"<[^>]*>", " ", body)
        raw_words = [clean_tok(w) for w in re.split(r"[.,\s]+", body_clean)]
        words = [w for w in raw_words if w]
        if not words:
            continue

        folio_tokens[folio].extend(words)
        folio_loci[folio].append((line_no, loc_raw, words))
        paragraphs_by_folio[folio][curr_para_id].append((line_no, loc_raw, words))

        if loc_raw in ("=Pt", "+Pr") or loc_raw.endswith(("Pt", "Pr")):
            fmeta = idx["folios"].get(folio, {})
            pt_pr_lines.append({
                "folio": folio,
                "line_no": line_no,
                "loc": loc_raw,
                "tag_type": "Pt_Title_Signature" if loc_raw.endswith("Pt") else "Pr_Right_Justified_Coda",
                "para_id": curr_para_id,
                "section": fmeta.get("section", "Unknown"),
                "language": fmeta.get("currier_lang", "?"),
                "hand": fmeta.get("hand", "?"),
                "words": words,
                "word_count": len(words),
                "text": " ".join(words),
            })

    # Enrich each =Pt / +Pr line with lexical overlap against its host paragraph and host folio
    para_overlap_hits = 0
    para_stem_hits = 0
    folio_overlap_hits = 0
    folio_stem_hits = 0
    pt_total_words = 0
    folio_pt_counts = Counter()
    section_pt_counts = Counter()
    tag_type_counts = Counter()

    for item in pt_pr_lines:
        f = item["folio"]
        pid = item["para_id"]
        folio_pt_counts[f] += 1
        section_pt_counts[item["section"]] += 1
        tag_type_counts[item["tag_type"]] += 1

        para_lines = paragraphs_by_folio[f][pid]
        para_other_words = []
        for lno, lloc, lwords in para_lines:
            if lno != item["line_no"]:
                para_other_words.extend(lwords)

        folio_other_words = []
        for lno, lloc, lwords in folio_loci[f]:
            if lno != item["line_no"]:
                folio_other_words.extend(lwords)

        para_set = set(para_other_words)
        para_stems = {canonical_stem(w) for w in para_other_words}
        f_set = set(folio_other_words)
        f_stems = {canonical_stem(w) for w in folio_other_words}

        exact_para = [w for w in item["words"] if w in para_set]
        stem_para = [w for w in item["words"] if canonical_stem(w) in para_stems]
        exact_folio = [w for w in item["words"] if w in f_set]
        stem_folio = [w for w in item["words"] if canonical_stem(w) in f_stems]

        item["para_other_word_count"] = len(para_other_words)
        item["exact_shared_in_para"] = exact_para
        item["stem_shared_in_para"] = stem_para
        item["exact_shared_in_folio"] = exact_folio
        item["stem_shared_in_folio"] = stem_folio

        para_overlap_hits += len(exact_para)
        para_stem_hits += len(stem_para)
        folio_overlap_hits += len(exact_folio)
        folio_stem_hits += len(stem_folio)
        pt_total_words += len(item["words"])

    # Permutation baseline for =Pt / +Pr host-paragraph and host-folio overlap
    all_paras = [
        (f, pid, [w for _, _, lw in plines for w in lw])
        for f, pdict in paragraphs_by_folio.items()
        for pid, plines in pdict.items()
        if sum(len(lw) for _, _, lw in plines) >= 15
    ]
    all_folios_list = [f for f, toks in folio_tokens.items() if len(toks) >= 50]

    null_para_exact, null_para_stem = [], []
    null_folio_exact, null_folio_stem = [], []
    for _ in range(1000):
        pe, ps, fe, fs = 0, 0, 0, 0
        for item in pt_pr_lines:
            _, _, rpara_words = random.choice(all_paras)
            rpset = set(rpara_words)
            rpstems = {canonical_stem(w) for w in rpara_words}
            pe += sum(1 for w in item["words"] if w in rpset)
            ps += sum(1 for w in item["words"] if canonical_stem(w) in rpstems)

            rf = random.choice(all_folios_list)
            rfwords = folio_tokens[rf]
            rfset = set(rfwords)
            rfstems = {canonical_stem(w) for w in rfwords}
            fe += sum(1 for w in item["words"] if w in rfset)
            fs += sum(1 for w in item["words"] if canonical_stem(w) in rfstems)
        null_para_exact.append(100.0 * pe / pt_total_words)
        null_para_stem.append(100.0 * ps / pt_total_words)
        null_folio_exact.append(100.0 * fe / pt_total_words)
        null_folio_stem.append(100.0 * fs / pt_total_words)

    def calc_z(obs_val, arr):
        m = sum(arr) / len(arr)
        sd = math.sqrt(sum((x - m) ** 2 for x in arr) / len(arr)) or 1e-9
        return round(m, 2), round((obs_val - m) / sd, 2)

    obs_pe_pct = 100.0 * para_overlap_hits / max(1, pt_total_words)
    obs_ps_pct = 100.0 * para_stem_hits / max(1, pt_total_words)
    obs_fe_pct = 100.0 * folio_overlap_hits / max(1, pt_total_words)
    obs_fs_pct = 100.0 * folio_stem_hits / max(1, pt_total_words)

    null_pe_mean, z_pe = calc_z(obs_pe_pct, null_para_exact)
    null_ps_mean, z_ps = calc_z(obs_ps_pct, null_para_stem)
    null_fe_mean, z_fe = calc_z(obs_fe_pct, null_folio_exact)
    null_fs_mean, z_fs = calc_z(obs_fs_pct, null_folio_stem)

    # Analyze the 6-panel Rosettes physical sheet: f85r1, f85r2, f85v2, f86v3, f86v4, f86v5, f86v6
    rosettes_sheet_folios = ["f85r1", "f85r2", "f85v2", "f86v3", "f86v4", "f86v5", "f86v6"]
    sheet_panel_profiles = []
    for rf in rosettes_sheet_folios:
        toks = folio_tokens.get(rf, [])
        loci = folio_loci.get(rf, [])
        fmeta = idx["folios"].get(rf, {})
        pt_cnt = folio_pt_counts[rf]
        qo_cnt = sum(1 for w in toks if w.startswith("qo"))
        edy_cnt = sum(1 for w in toks if w.endswith(("edy", "dy")))
        aiin_cnt = sum(1 for w in toks if w.endswith(("aiin", "iin")))
        sheet_panel_profiles.append({
            "folio": rf,
            "section": fmeta.get("section", "Unknown"),
            "language": fmeta.get("currier_lang", "?"),
            "hand": fmeta.get("hand", "?"),
            "lines": len(loci),
            "words": len(toks),
            "unique_types": len(set(toks)),
            "pt_pr_lines": pt_cnt,
            "qo_pct": round(100.0 * qo_cnt / max(1, len(toks)), 2),
            "edy_pct": round(100.0 * edy_cnt / max(1, len(toks)), 2),
            "aiin_pct": round(100.0 * aiin_cnt / max(1, len(toks)), 2),
        })

    # Lexical & Stem Coupling between the Rosettes Treatise Envelope (f85r1, f85r2, f86v3, f86v4, f86v5, f86v6)
    # and the inner 9-Sphere Cosmos Map (f85v2)
    map_tokens = folio_tokens["f85v2"]
    map_types = set(map_tokens)
    map_stems = {canonical_stem(w) for w in map_tokens if len(w) >= 3}

    envelope_folios = ["f85r1", "f85r2", "f86v3", "f86v4", "f86v5", "f86v6"]
    env_tokens = [w for ef in envelope_folios for w in folio_tokens[ef]]
    env_types = set(env_tokens)
    env_stems = {canonical_stem(w) for w in env_tokens if len(w) >= 3}

    shared_exact_types = sorted(map_types & env_types)
    shared_stems = sorted(map_stems & env_stems)

    b_folios = [
        f for f, meta in idx["folios"].items()
        if meta.get("currier_lang") == "B" and f not in rosettes_sheet_folios and len(folio_tokens.get(f, [])) >= 80
    ]

    obs_map_token_cov = sum(1 for w in map_tokens if w in env_types) / max(1, len(map_tokens))
    obs_map_stem_cov = sum(1 for w in map_tokens if len(w) >= 3 and canonical_stem(w) in env_stems) / max(1, sum(1 for w in map_tokens if len(w) >= 3))
    obs_jaccard_types = len(shared_exact_types) / max(1, len(map_types | env_types))

    all_word_counts = Counter(w for f, toks in folio_tokens.items() for w in toks)
    rare_shared = [
        {"word": w, "corpus_freq": all_word_counts[w], "map_count": map_tokens.count(w), "env_count": env_tokens.count(w)}
        for w in shared_exact_types
        if all_word_counts[w] <= 25 and len(w) >= 4
    ]
    rare_shared.sort(key=lambda x: (x["corpus_freq"], -x["map_count"] - x["env_count"]))

    null_jaccards = []
    null_rare_counts = []
    null_token_covs = []
    for _ in range(1000):
        sampled = []
        pool = b_folios[:]
        random.shuffle(pool)
        for pf in pool:
            sampled.extend(folio_tokens[pf])
            if len(sampled) >= len(env_tokens):
                break
        sampled = sampled[:len(env_tokens)]
        stypes = set(sampled)
        sh = map_types & stypes
        null_jaccards.append(len(sh) / max(1, len(map_types | stypes)))
        null_token_covs.append(sum(1 for w in map_tokens if w in stypes) / max(1, len(map_tokens)))
        r_cnt = sum(1 for w in sh if all_word_counts[w] <= 25 and len(w) >= 4)
        null_rare_counts.append(r_cnt)

    mean_j = sum(null_jaccards) / len(null_jaccards)
    sd_j = math.sqrt(sum((x - mean_j) ** 2 for x in null_jaccards) / len(null_jaccards)) or 1e-9
    z_jaccard = (obs_jaccard_types - mean_j) / sd_j

    mean_r = sum(null_rare_counts) / len(null_rare_counts)
    sd_r = math.sqrt(sum((x - mean_r) ** 2 for x in null_rare_counts) / len(null_rare_counts)) or 1e-9
    z_rare = (len(rare_shared) - mean_r) / sd_r

    mean_tc = sum(null_token_covs) / len(null_token_covs)
    sd_tc = math.sqrt(sum((x - mean_tc) ** 2 for x in null_token_covs) / len(null_token_covs)) or 1e-9
    z_tc = (obs_map_token_cov - mean_tc) / sd_tc

    # Panel-by-panel coupling to f85v2
    panel_to_map_coupling = []
    for ef in envelope_folios:
        etoks = folio_tokens[ef]
        etypes = set(etoks)
        estems = {canonical_stem(w) for w in etoks if len(w) >= 3}
        sh = sorted(map_types & etypes)
        sh_stems = sorted(map_stems & estems)
        r_sh = [w for w in sh if all_word_counts[w] <= 25 and len(w) >= 4]
        panel_to_map_coupling.append({
            "folio": ef,
            "panel_words": len(etoks),
            "panel_types": len(etypes),
            "shared_types_with_f85v2": len(sh),
            "shared_stems_with_f85v2": len(sh_stems),
            "pct_of_panel_types_in_f85v2": round(100.0 * len(sh) / max(1, len(etypes)), 2),
            "pct_of_panel_stems_in_f85v2": round(100.0 * len(sh_stems) / max(1, len(estems)), 2),
            "rare_shared_types_le25": r_sh,
        })

    out = {
        "attack": 181,
        "discovery": 198,
        "title": "The f85r1-f86v6 Rosettes Treatise Envelope, =Pt/+Pr Right-Justified Title/Coda Law & 9-Sphere Map Coupling",
        "pt_pr_lines_summary": {
            "total_lines": len(pt_pr_lines),
            "tag_type_counts": dict(tag_type_counts),
            "total_words": pt_total_words,
            "mean_words_per_line": round(pt_total_words / max(1, len(pt_pr_lines)), 2),
            "exact_word_overlap_with_host_para_pct": round(obs_pe_pct, 2),
            "null_para_exact_pct": null_pe_mean,
            "z_para_exact": z_pe,
            "stem_overlap_with_host_para_pct": round(obs_ps_pct, 2),
            "null_para_stem_pct": null_ps_mean,
            "z_para_stem": z_ps,
            "exact_word_overlap_with_host_folio_pct": round(obs_fe_pct, 2),
            "null_folio_exact_pct": null_fe_mean,
            "z_folio_exact": z_fe,
            "stem_overlap_with_host_folio_pct": round(obs_fs_pct, 2),
            "null_folio_stem_pct": null_fs_mean,
            "z_folio_stem": z_fs,
            "by_folio": dict(folio_pt_counts.most_common()),
            "by_section": dict(section_pt_counts.most_common()),
            "all_lines": pt_pr_lines,
        },
        "rosettes_sheet_panels": sheet_panel_profiles,
        "envelope_to_f85v2_coupling": {
            "f85v2_words": len(map_tokens),
            "f85v2_types": len(map_types),
            "envelope_words": len(env_tokens),
            "envelope_types": len(env_types),
            "shared_exact_types_count": len(shared_exact_types),
            "shared_stems_count": len(shared_stems),
            "f85v2_token_coverage_by_envelope_pct": round(100.0 * obs_map_token_cov, 2),
            "f85v2_stem_coverage_by_envelope_pct": round(100.0 * obs_map_stem_cov, 2),
            "null_token_coverage_pct_mean": round(100.0 * mean_tc, 2),
            "z_token_coverage": round(z_tc, 2),
            "observed_jaccard": round(obs_jaccard_types, 4),
            "null_currier_b_jaccard_mean": round(mean_j, 4),
            "z_jaccard": round(z_jaccard, 2),
            "rare_shared_types_le25_count": len(rare_shared),
            "null_rare_shared_mean": round(mean_r, 2),
            "z_rare_shared": round(z_rare, 2),
            "rare_shared_examples": rare_shared[:25],
            "panel_by_panel": panel_to_map_coupling,
        },
    }

    out_path = Path("data/attack181_rosettes_treatise_envelope_and_pt_titles.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print(f"Total =Pt/+Pr lines: {len(pt_pr_lines)} ({pt_total_words} words), tags: {dict(tag_type_counts)}")
    print(f"Host-para stem overlap: {out['pt_pr_lines_summary']['stem_overlap_with_host_para_pct']}%, Host-folio stem overlap: {out['pt_pr_lines_summary']['stem_overlap_with_host_folio_pct']}%")
    print(f"Rosettes Envelope -> f85v2 token coverage: {out['envelope_to_f85v2_coupling']['f85v2_token_coverage_by_envelope_pct']}% (stem cov: {out['envelope_to_f85v2_coupling']['f85v2_stem_coverage_by_envelope_pct']}%) "
          f"(shared types={len(shared_exact_types)}, Jaccard z={z_jaccard:+.2f}, Rare shared={len(rare_shared)} vs {mean_r:.2f}, z={z_rare:+.2f})")


if __name__ == "__main__":
    main()
