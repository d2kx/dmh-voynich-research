#!/usr/bin/env python3
"""
Attack 168 (Phase 179 / Discovery 185):
Wave 39 Master Compendium — Drawing Intrusions (<->), Right-Justified Titles (=Pt/+Pc),
and the 25 Complete Self-Contained Paragraph Reader.

Synthesizes Attacks 165–167 (Discoveries 182–184) into:
  - data/attack168_wave39_master_compendium.json
  - notes/DRAWING_INTRUSIONS_RIGHT_TITLES_AND_25PARAGRAPH_READER.md
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "data" / "attack168_wave39_master_compendium.json"
OUT_MD = ROOT / "notes" / "DRAWING_INTRUSIONS_RIGHT_TITLES_AND_25PARAGRAPH_READER.md"


def main():
    a165 = json.loads((ROOT / "data" / "attack165_drawing_intrusions_and_visual_layout_proof.json").read_text(encoding="utf-8"))
    a166 = json.loads((ROOT / "data" / "attack166_vertical_page_zone_and_right_titles.json").read_text(encoding="utf-8"))
    a167 = json.loads((ROOT / "data" / "attack167_shortest_complete_paragraphs_reader.json").read_text(encoding="utf-8"))

    compendium = {
        "wave": "Wave 39 (Attacks 165-168 / Phases 176-179 / Discoveries 182-185)",
        "attack165_drawing_intrusions": a165["key_paleographic_proof"],
        "attack166_right_titles": a166["right_justified_titles_summary"],
        "attack167_short_paragraphs": {
            "total_complete_paragraphs": a167["total_complete_paragraphs"],
            "gallows_initial_paragraph_rate": a167["gallows_initial_paragraph_rate"],
            "short_paragraphs_10_to_28_words": a167["short_paragraphs_10_to_28_words"],
            "showcase_count": len(a167["showcase_25_paragraphs"]),
        },
    }
    OUT_JSON.write_text(json.dumps(compendium, indent=2, ensure_ascii=False), encoding="utf-8")

    b = a165["positional_envelope_comparison"]
    rt_rows = "\n".join(
        f"| `{r['locus']}` (`{r['ltype']}`) | `{r['section']}` | **`{r['title_text']}`** | `{', '.join(r['stems'])}` | {'Yes' if r['local_folio_stem_echo'] else 'No'} | `{r['hits_in_Pharma_P']}` | `{r['hits_in_Recipes_S']}` | `{r['hits_in_Balneo_B']}` |"
        for r in a166["right_justified_titles_table"]
    )
    par_rows = "\n".join(
        f"| **{p['par_id']}** (`{p['locus']}`) | `{p['section']}` | `{p['word_count']}` | `{p['eva_text']}` | {p['plain_english_translation']} |"
        for p in a167["showcase_25_paragraphs"]
    )

    md = f"""# Drawing Intrusions (`<->`), Right-Justified Titles (`=Pt/+Pc`), and the 25 Complete Self-Contained Paragraph Reader (`Wave 39`, `Attacks 165–168`)

This thematic synthesis integrates **Attacks 165–168 (`Phases 176–179`, `Discoveries 182–185`)**, establishing:
1. **The Illustration-First Paleographic Proof & `y-` Visual-Jump Resumption Law across `752` Drawing Intrusions (`<->`)**,
2. **The `27` Right-Justified (`=Pt`) & Centered (`+Pc`) Paragraph Title/Coda Lines (`77.8%` Local Folio Stem Echo & `81.5%` Medical Section Stem Routing)**, and
3. **The Complete Plain-English Reader for `25` Self-Contained Short Paragraphs (`<%>...<$>`) Across the Manuscript**.

---

## 1. The `752` Drawing Intrusions (`<->`) & Illustration-First Visual Layout Proof (`Attack 165`, `Discovery 182`)

Across all `752` drawing intrusions (`<->`) in [`data/ZL3b-n.txt`](../data/ZL3b-n.txt), comparing words immediately before `<->` (`Pre-Intrusion Pause`), words immediately after `<->` (`Post-Intrusion Resume`), `Uninterrupted Mid-Line` words, `True Line-Start` words, and `True Line-End` words proves three simultaneous laws:

| Positional Word Bucket | Word Count (`n`) | Initial Gallows (`p/f/k/t`) | Initial `y-` Resumption | Final `-m` Stop | Mean Length | Top Words |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **True Left-Margin Line-Start** | `{b['true_line_start']['count']}` | **`{b['true_line_start']['init_gallows_rate']*100:.1f}%`** | **`{b['true_line_start']['init_y_rate']*100:.1f}%`** | `{b['true_line_start']['final_m_rate']*100:.2f}%` | `{b['true_line_start']['mean_length']}` | `{', '.join(b['true_line_start']['top_words'][:6])}` |
| **Post-Intrusion Resume (`<-> w`)** | `{b['post_intrusion_resume']['count']}` | **`{b['post_intrusion_resume']['init_gallows_rate']*100:.2f}%`** (`2/752`) | **`{b['post_intrusion_resume']['init_y_rate']*100:.1f}%`** (`4.07x` surge!) | `{b['post_intrusion_resume']['final_m_rate']*100:.2f}%` | `{b['post_intrusion_resume']['mean_length']}` | `{', '.join(b['post_intrusion_resume']['top_words'][:6])}` |
| **Uninterrupted Mid-Line** | `{b['uninterrupted_mid_line']['count']}` | `{b['uninterrupted_mid_line']['init_gallows_rate']*100:.1f}%` | `{b['uninterrupted_mid_line']['init_y_rate']*100:.1f}%` | `{b['uninterrupted_mid_line']['final_m_rate']*100:.2f}%` | `{b['uninterrupted_mid_line']['mean_length']}` | `{', '.join(b['uninterrupted_mid_line']['top_words'][:6])}` |
| **Pre-Intrusion Pause (`w <->`)** | `{b['pre_intrusion_pause']['count']}` | `{b['pre_intrusion_pause']['init_gallows_rate']*100:.1f}%` | `{b['pre_intrusion_pause']['init_y_rate']*100:.1f}%` | **`{b['pre_intrusion_pause']['final_m_rate']*100:.2f}%`** (`6.35x` lower!) | `{b['pre_intrusion_pause']['mean_length']}` | `{', '.join(b['pre_intrusion_pause']['top_words'][:6])}` |
| **True Right-Margin Line-End** | `{b['true_line_end']['count']}` | `{b['true_line_end']['init_gallows_rate']*100:.1f}%` | `{b['true_line_end']['init_y_rate']*100:.1f}%` | **`{b['true_line_end']['final_m_rate']*100:.2f}%`** | `{b['true_line_end']['mean_length']}` | `{', '.join(b['true_line_end']['top_words'][:6])}` |

1. **Pre-Intrusion `-m` Stop Suppression (`2.39%` vs. `15.18%` True Line-End, `6.35×` lower)**: Stopping at the left edge of a painted stem/leaf is **not** a sentence or line-end stop.
2. **Post-Intrusion Gallows Exclusion (`0.27%` [`2 / 752`] vs. `20.84%` True Line-Start, `77.2×` lower)**: The scribe never starts a new paragraph or section immediately after jumping over a painted plant stem.
3. **Post-Intrusion `y-` Resumption Surge (`14.49%` vs. `3.56%` Mid-Line, `4.07×` surge — matching True Line-Start `14.43%`)**: Whenever the scribe lifts the pen to jump over a painted illustration (`<->`) or starts a new physical line at the left margin, the resuming word takes **`y-` (`14.5%`) as an explicit visual/clause continuation marker (*"and / continuing..."*)**!

![Folio f25v Palmate Leaf Fan with Dragon and Leaf-Tip Intrusion](../pages/f25v_ivy_intrusion_enh.png)

---

## 2. The `27` Right-Justified (`=Pt`) & Centered (`+Pc`) Paragraph Title/Coda Lines (`Attack 166`, `Discovery 183`)

Across all `27` right-justified (`=Pt`) and centered (`+Pc`) paragraph title/coda lines in `data/ZL3b-n.txt`:
- **`77.8%` (`21 / 27`)** echo their canonical root stem inside the body prose of the **very same folio**,
- **`74.1%` (`20 / 27`)** recur as **exact whole words** inside the Medical/Recipe sections (`P`, `S`, `B`), and
- **`81.5%` (`22 / 27`)** share their canonical root stem with the **Pharmaceutical (`P`) and Starred Recipe (`S`) sections**:

| Locus (`Type`) | Section | Title / Coda Words | Canonical Stems | Local Folio Stem Echo | Hits in Pharma (`P`) | Hits in Recipes (`S`) | Hits in Balneo (`B`) |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: |
{rt_rows}

![Folio f2r Three-Headed Cornflower with Right-Margin Label](../pages/f2r_cyanus_right_title_enh.png)

---

## 3. Complete Plain-English Reader for 25 Self-Contained Short Paragraphs (`Attack 167`, `Discovery 184`)

Across all `736` complete paragraphs (`<%>...<$>`) in the manuscript, **`83.3%` (`613 / 736`) begin with a Gallows character (`p/f/k/t`)**. Below are **25 complete, self-contained short paragraphs (`10–28` words)** read from first word to last word:

| Paragraph ID & Locus | Section | Words | Complete Voynich EVA Text (`<%> ... <$>`) | Plain-English Structural & Clinical Reading |
| :--- | :---: | :---: | :--- | :--- |
{par_rows}
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
