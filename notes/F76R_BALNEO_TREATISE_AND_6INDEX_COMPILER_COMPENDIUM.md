# The `f76r` Balneological Master Treatise, 6-Folio Master Index Architecture & Cross-Line Anaphoric Polyptoton Compendium (`Attacks 145–148` / `Discoveries 162–165`)

> **Repository-Relative Asset Links**: [`tools/attack145_f76r_balneological_master_index_and_9key_router.py`](../tools/attack145_f76r_balneological_master_index_and_9key_router.py) | [`data/attack145_f76r_balneological_master_index_and_9key_router.json`](../data/attack145_f76r_balneological_master_index_and_9key_router.json) | [`tools/attack146_six_master_index_folios_unified_compiler_test.py`](../tools/attack146_six_master_index_folios_unified_compiler_test.py) | [`data/attack146_six_master_index_folios_unified_compiler_test.json`](../data/attack146_six_master_index_folios_unified_compiler_test.json) | [`tools/attack147_cross_line_anaphoric_polyptoton_and_chaining_law.py`](../tools/attack147_cross_line_anaphoric_polyptoton_and_chaining_law.py) | [`data/attack147_cross_line_anaphoric_polyptoton_and_chaining_law.json`](../data/attack147_cross_line_anaphoric_polyptoton_and_chaining_law.json) | [`tools/attack148_f76r_6index_and_crossline_polyptoton_compendium.py`](../tools/attack148_f76r_6index_and_crossline_polyptoton_compendium.py) | [`data/attack148_f76r_6index_and_crossline_polyptoton_compendium.json`](../data/attack148_f76r_6index_and_crossline_polyptoton_compendium.json) | [`pages/f76r_vertical_9glyph_margin_key_enh.png`](../pages/f76r_vertical_9glyph_margin_key_enh.png)

---

## 1. Executive Summary (`Discoveries 162–165`)

1. **Discovery 162 (`Attack 145` — `f76r` as the Unillustrated 9-Key Balneological Master Treatise of `Quire M`, $z = +3.69$)**:
   - Among the `20` folios of the Balneological Quire (`Quire M`, `f75r..f84v`, Scribe Hand 2, Currier B), **`f76r`** (`$Q=M, $B=2, $I=T`) is the **only unillustrated pure-text folio** (`560` prose words vs. `329.37` mean across the `19` illustrated bath folios = **`1.7×` text density**, and **`39`** vs. **`27.37`** unique open stems = **`+42.5%` stem diversity**).
   - **`76.92%` (`30 / 39`)** of `f76r`'s open stems recur inside `Quire M`, yielding **`86.347`** shared IDF bits vs. **`47.411 ± 10.541`** across `1,000` random codex folio draws (**`1.82×` lift, $z = +3.69, p = 0.00011$**).
   - Even though `f76r` has zero drawings or labels of its own, its body prose shares **`3`** open stems with the `@Ln/@Lt` nymph and tub labels of `Quire M` (**Rank `#5 / 20`** across all pages of `Quire M`), shows **`1.16×` higher shared IDF** with its physical `$B=2` bifolio sheet-mates (`f76v, f83r, f83v`), and routes its **`11` structural units** (`P0`, `9` margin-keyed sub-blocks of `P1`, and `P2`) across **`7` distinct `#1` Illustrated Bath Folio targets** (`f75r, f77r, f78r, f80r, f82r, f83r, f84r`), with **`63.64%` (`7 / 11`)** selecting a **Currier B Herbal (`$L=B`)** `#1` botanical partner.

2. **Discovery 163 (`Attack 146` — Unified Structural & Lexical Compiler Test of the Six Master Index & Margin-Keyed Folios `f1r, f49v, f58r, f58v, f66r, f76r`, $z = +4.67 / +4.59 / +3.50$)**:
   - Tested as a unified architectural class against the remaining `201` prose folios (`1,000`-trial 6-folio permutation baseline), the **Six Master Index & Margin-Keyed Folios** (`f1r, f49v, f58r, f58v, f66r, f76r`, spanning Hands `1, 2, 3, 5` and Languages `A` & `B`) exhibit **`2.0×` Prose Word Density** (`329.5` vs. `164.597`, **$z = +2.79$**), **`2.21×` Open-Stem Diversity** (`41.167` vs. `18.667`, **$z = +3.42$**), **`2.77×` Diagram-Label Stem Matches** (`11.333` vs. `4.095`, **$z = +4.67$**), **`2.82×` Diagram-Label IDF** (**$z = +4.59$**), and **`2.26×` Multi-Section Hub IDF** (**$z = +3.5$**).
   - Although these `6` pages represent only **`2.90%` (`6 / 207`)** of the manuscript's prose folios, their union (`183` open stems) covers **`43.09%` (`134 / 311`)** of all Multi-Section Hub Stems in the codex, while **`75.41%` (`138 / 183`)** of their open stems are **exclusive to a single Master Index Folio** (`mean pairwise Jaccard = 0.0739`).

3. **Discovery 164 (`Attack 147` — Cross-Line Anaphoric Polyptoton & Sequential Stem Chaining `Line t -> Line t+1`, $z = +25.04 / +8.05$)**:
   - Across all **`736`** multi-line paragraphs (**`3315`** adjacent `Line t -> Line t+1` pairs), **`56.68%` (`1879 / 3315`)** contain **Cross-Line Cognate Polyptoton** (`w_t != w_{t+1}` sharing the exact same canonical stem `S`), generating **`4090`** cross-line cognate links vs. **`1819`** exact token repeats (**`2.25×` preference for inflectional variation over verbatim repetition**).
   - Against `1,000` **Within-(Section `$I`, Language `$L`) Line-Shuffle Permutations**, observed Cross-Line Cognate Polyptoton (`4090`) exceeds the null (`2613.07 ± 58.98`) by **`1.565×` ($z = +25.04, p < 10^-100$)**; and even under a **Strict Within-Paragraph Line-Order Shuffle** inside the `493` paragraphs of `>= 4` lines (preserving the exact stem inventory of every single paragraph), adjacent lines `Line t -> Line t+1` exhibit **`3563`** vs. **`3154.39 ± 50.75`** null links (**`1.13×` lift, $z = +8.05, p < 10^-15$**), proving local sentence-to-sentence anaphoric chaining above and beyond paragraph topic persistence.
   - Across `Line t -> Line t+1` cognate handoffs, `Line t+1` significantly enriches **`l-/ol-` Applicative/Locative prefixation** (`9.95% -> 11.54%`, `+16.0%`, sign-flip **$z = +2.53$**) and **`-ol/-or/-al/-ar` Liquid Nominal derivation** (`7.56% -> 8.75%`, `+15.7%`, sign-flip **$z = +2.27$**), while `START->END` (`6.00×`), `END->START` (`3.86×` anadiplosis), and `MID->START` (`3.50×` body-to-head topicalization) exhibit the strongest preference for inflectional variation over exact repetition.

---

## 2. Table 1 — The 11 Structural Units of the `f76r` Balneological Master Treatise (`Attack 145`)

| Unit | Key (`@L0`) | Lines | Words | Open Stems | Bath-Label Hits | Top `#1` Illustrated Bath Target (`IDF`) | Top `#1` Botanical Herbal Partner (`Lang`, `IDF`) | Opening Clause (`EVA`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| `U1_P1_KEY1_s` | `s` | `L1..L4` (`4L`) | `50` | `8` | `0` | **`f77r`** (`8.079`) | **`f17r`** (`$L=A`, `5.393`) | `potchokor chcfhdy opshdy qolp chcphy chcphdy opshey qofshy` |
| `U2_P1_KEY2_d` | `d` | `L5..L6` (`2L`) | `26` | `3` | `0` | **`f83r`** (`4.269`) | **`f95r1`** (`$L=B`, `3.074`) | `solchedy qokeedy qopchedy qokeeo rol shedy qokedy sheey` |
| `U3_P1_KEY3_q` | `q` | `L7..L8` (`2L`) | `27` | `3` | `0` | **`NONE`** (`0.0`) | **`f31r`** (`$L=B`, `4.339`) | `shed al shckhy r ain chcphedy ain olkeey` |
| `U4_P1_KEY4_s` | `s` | `L9..L11` (`3L`) | `40` | `4` | `1` | **`f80v`** (`4.873`) | **`f90r1`** (`$L=A`, `6.501`) | `solshedy qool qctheed shdy qa ol keey dain` |
| `U5_P1_KEY5_o` | `o` | `L12..L14` (`3L`) | `34` | `2` | `0` | **`f80r`** (`3.837`) | **`NONE`** (`$L=A`, `0.0`) | `qotes chedy shckhy qokeey okeey kain checkhy qokeedy` |
| `U6_P1_KEY6_l` | `l` | `L15..L17` (`3L`) | `37` | `2` | `0` | **`f79v`** (`3.165`) | **`f55v`** (`$L=B`, `3.659`) | `dshedy qo chedy lchedy qokey qolchey qotain chckhy` |
| `U7_P1_KEY7_k` | `k` | `L18..L20` (`3L`) | `40` | `3` | `0` | **`f83v`** (`5.375`) | **`f46r`** (`$L=B`, `5.592`) | `dalshedy qol sheedy qokaldy chepy dain alolor olain` |
| `U8_P1_KEY8_r` | `r` | `L21..L23` (`3L`) | `39` | `4` | `1` | **`f80v`** (`7.518`) | **`f39r`** (`$L=B`, `2.781`) | `soin sheey chear ol aiin chodaiin qokaiin chey` |
| `U9_P1_KEY9_s` | `s` | `L24..L27` (`4L`) | `54` | `5` | `0` | **`f83r`** (`8.249`) | **`f39r`** (`$L=B`, `3.887`) | `cheo r ain okaiin dain chey dalshedy qokaiin` |
| `U10_PARA2_UNKEYED` | `P2_GALL_p` | `L28..L34` (`7L`) | `79` | `6` | `0` | **`f80v`** (`6.691`) | **`f46v`** (`$L=B`, `5.393`) | `qokal shedy sheol cheol alshy chol chdy talor` |
| `U11_PARA3_UNKEYED` | `P3_GALL_p` | `L35..L47` (`13L`) | `134` | `9` | `2` | **`f77v`** (`11.546`) | **`f1v`** (`$L=A`, `4.482`) | `poleedaran shckhy qoty ykar alol lkaiin ol shedy` |

---

## 3. Table 2 — Unified Architecture of the Six Master Index & Margin-Keyed Folios (`Attack 146`)

| Master Folio | Section (`$I`) | Lang (`$L`) | Hand (`$H`) | Prose Words | Open Stems (`Excl %`) | Diagram-Label Matches (`IDF`) | Multi-Section Hub Stems (`IDF`) | Architectural Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`f1r`** | `T` | `A` | `H1` | `214` | **`30`** (`50.0%`) | **`8`** (`17.996`) | **`25`** (`64.873`) | Quire A $B=1 ($I=T, $L=A, $H=1): Opening Master Preface with =Pt Right-Justified Rubrics |
| **`f49v`** | `H` | `A` | `H1` | `142` | **`26`** (`65.38%`) | **`3`** (`7.615`) | **`19`** (`51.313`) | Quire G $B=1 ($I=H, $L=A, $H=1): 26-Glyph + Arabic Numeral 1..5 Vertical Margin Key |
| **`f58r`** | `S` | `A` | `H3` | `378` | **`64`** (`60.94%`) | **`21`** (`52.914`) | **`47`** (`132.365`) | Quire H $B=2 ($I=T, $L=B, $H=3): Unillustrated Starred Botanical-Apothecary Master Index I |
| **`f58v`** | `S` | `A` | `H3` | `375` | **`39`** (`46.15%`) | **`10`** (`23.005`) | **`27`** (`71.347`) | Quire H $B=2 ($I=T, $L=B, $H=3): Unillustrated Starred Botanical-Apothecary Master Index II |
| **`f66r`** | `T` | `B` | `H5` | `308` | **`50`** (`54.0%`) | **`15`** (`39.539`) | **`42`** (`120.794`) | Quire H $B=1 ($I=T, $L=B, $H=5): 15-Word + 34-Key Dual Left-Margin Clinical Treatise |
| **`f76r`** | `T` | `B` | `H2` | `560` | **`38`** (`57.89%`) | **`11`** (`28.567`) | **`35`** (`103.351`) | Quire M $B=2 ($I=T, $L=B, $H=2): Unillustrated 9-Key Balneological Master Treatise |

---

## 4. Table 3 — Cross-Line Horizontal Zone Handoff Matrix (`Line t -> Line t+1`, `Attack 147`)

| Zone Transition (`Line t -> Line t+1`) | Cognate Polyptoton Links (`w_t != w_{t+1}`) | Cognate Share (`%`) | Exact Repeat Links (`w_t == w_{t+1}`) | Exact Share (`%`) | Cognate / Exact Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`START->START`** | `47` | `1.15%` | `15` | `0.82%` | **`3.13×`** |
| **`START->MID`** | `234` | `5.72%` | `69` | `3.79%` | **`3.39×`** |
| **`START->END`** | `30` | `0.73%` | `5` | `0.27%` | **`6.0×`** |
| **`MID->START`** | `378` | `9.24%` | `108` | `5.94%` | **`3.5×`** |
| **`MID->MID`** | `2777` | `67.9%` | `1375` | `75.59%` | **`2.02×`** |
| **`MID->END`** | `279` | `6.82%` | `108` | `5.94%` | **`2.58×`** |
| **`END->START`** | `27` | `0.66%` | `7` | `0.38%` | **`3.86×`** |
| **`END->MID`** | `264` | `6.45%` | `105` | `5.77%` | **`2.51×`** |
| **`END->END`** | `54` | `1.32%` | `27` | `1.48%` | **`2.0×`** |

---

## 5. Table 4 — Cross-Line Directional Morphological Shift (`Line t -> Line t+1`, `Attack 147`)

| Morphological Feature | `Line t` Count (`%`) | `Line t+1` Count (`%`) | Delta (`t -> t+1`) | Discordant Gain / Loss (`0->1` / `1->0`) | Sign-Flip $z$-Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `is_qo_act` | `374` (`9.14%`) | `346` (`8.46%`) | `-0.68%` | `260 / 288` | **`-1.20`** |
| `is_l_ol_appl` | `407` (`9.95%`) | `472` (`11.54%`) | `+1.59%` | `363 / 298` | **`+2.53`** |
| `is_da_art` | `40` (`0.98%`) | `29` (`0.71%`) | `-0.27%` | `16 / 27` | **`-1.68`** |
| `is_ds_deictic` | `711` (`17.38%`) | `672` (`16.43%`) | `-0.95%` | `596 / 635` | **`-1.11`** |
| `is_edy_proc` | `1080` (`26.41%`) | `1067` (`26.09%`) | `-0.32%` | `205 / 218` | **`-0.63`** |
| `is_dy_perf` | `111` (`2.71%`) | `108` (`2.64%`) | `-0.07%` | `96 / 99` | **`-0.21`** |
| `is_y_stat` | `383` (`9.36%`) | `347` (`8.48%`) | `-0.88%` | `243 / 279` | **`-1.58`** |
| `is_liq_nom` | `309` (`7.56%`) | `358` (`8.75%`) | `+1.20%` | `257 / 208` | **`+2.27`** |
| `is_nasal_quant` | `100` (`2.44%`) | `82` (`2.0%`) | `-0.44%` | `65 / 83` | **`-1.48`** |
| `is_am_term` | `41` (`1.0%`) | `38` (`0.93%`) | `-0.07%` | `22 / 25` | **`-0.44`** |

