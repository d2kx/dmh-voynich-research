# The Voynich Constituent Treebank & Parallel Cross-Dialect Reader (`Attacks 69–72`)
## 1. Executive Summary: From Words to Phrase Constituents & Cross-Dialect Clause Trees
- **Corpus Parsed**: `5,376` lines | `36,229` words $\to$ **`29,461` Phrase Constituents** (`1.230` words/constituent, `5.480` constituents/line).
- **Three-Stage Phrase-Univerbation Continuum (`A . B <-> A,B <-> AB`, Attack 69)**: **`38.57%` (`334 / 866`)** of frequent 2-word phrases also occur as single-word fused compounds (`AB` or micro-spaced `A,B`) vs. `20.61%` null (**$z = +16.16$**), with identical external syntactic context frames (`mean cosine = 0.6965`, **$z = +7.4$**).
- **Constituent Phrase Transition Grammar (`Attack 70`)**: Adjacent phrase constituents (`TOP_HEAD`, `PP_PREP`, `VP_PROC`, `NP_MEAS`, `FIN_CLOSE`) exhibit **`0.03900 bits`** of transition mutual information vs. `0.00609 ± 0.00053 bits` within-line permutation null (**$z = +62.49$**).
- **Cross-Dialect `Currier A <-> Currier B` Structural & Lexical Alignment (`Attack 71`)**: Currier A (`1,557` prose lines) and Currier B (`2,467` prose lines) share a constituent transition bigram cosine of **`0.8873`**, and the Top-60 Currier A lexemes align to Currier B distributional counterparts at **`mean cosine = 0.9784`** (`heteronym cosine = 0.9686`, **$z = +7.59$**).

---

## 2. The Three-Stage Phrase-Univerbation Law (`A . B <-> A,B <-> AB`)
| Two-Word Phrase (`A . B`) | Analytical (`A . B`) | Uncertain Space (`A,B`) | Fused Compound (`AB`) | Context Frame Cosine | Total Tokens |
| :--- | :---: | :---: | :--- | :---: | :---: |
| `qol . keedy` | `2` | `2` | `qolkeedy` (8), `qokeedy` (307) | **`0.7892`** | `317` |
| `chy . dy` | `2` | `2` | `chydy` (1), `chdy` (147) | **`0.4147`** | `150` |
| `okey . dy` | `3` | `2` | `okedy` (120) | **`0.6633`** | `123` |
| `chol . dy` | `8` | `4` | `choldy` (11), `chody` (92) | **`0.8246`** | `111` |
| `cheol . dy` | `3` | `3` | `cheody` (91), `cheoldy` (6) | **`0.6368`** | `100` |
| `chor . dy` | `2` | `0` | `chody` (92), `chordy` (2) | **`0.5639`** | `96` |
| `or . aiin` | `58` | `28` | `oraiin` (34) | **`0.9168`** | `92` |
| `chy . cthy` | `4` | `0` | `chcthy` (81) | **`0.7164`** | `85` |
| `chol . daiin` | `33` | `6` | `chodaiin` (46), `choldaiin` (3) | **`0.8599`** | `82` |
| `chey . ky` | `2` | `2` | `cheyky` (2), `cheky` (67) | **`0.6650`** | `71` |
| `qoky . chy` | `2` | `0` | `qokchy` (67) | **`0.6983`** | `69` |
| `ol . aiin` | `14` | `7` | `olaiin` (52) | **`0.7825`** | `66` |
| `shol . dy` | `4` | `0` | `sholdy` (8), `shody` (53) | **`0.7832`** | `65` |
| `qoty . chy` | `3` | `0` | `qotchy` (62) | **`0.4909`** | `65` |
| `qo . tchy` | `2` | `2` | `qotchy` (62) | **`0.3751`** | `64` |
| `ol . chedy` | `22` | `6` | `olchedy` (39) | **`0.8555`** | `61` |
| `chor . daiin` | `9` | `0` | `chodaiin` (46) | **`0.8328`** | `55` |
| `sho . dy` | `2` | `0` | `shody` (53) | **`0.5852`** | `55` |
| `opchey . dy` | `2` | `0` | `opchedy` (49) | **`0.2300`** | `51` |
| `ol . keedy` | `6` | `4` | `olkeedy` (45) | **`0.5296`** | `51` |

---

## 3. Cross-Dialect (`Currier A <-> Currier B`) Distributional Translation Bridge
| Currier A Word (`$L=A`) | Count (`A`) | Best Currier B Overall (`$L=B`) | Cosine | Best Currier B Heteronym (`$L=B`) | Count (`B`) | Heteronym Cosine |
| :--- | :---: | :--- | :---: | :--- | :---: | :---: |
| **`daiin`** | `499` | `okaiin` | `0.9749` | **`okaiin`** | `305/168` | **`0.9749`** |
| **`chol`** | `276` | `chol` | `0.9818` | **`ol`** | `100/422` | **`0.9816`** |
| **`s`** | `203` | `s` | `0.9772` | **`dal`** | `104/128` | **`0.8890`** |
| **`chor`** | `177` | `otar` | `0.9855` | **`otar`** | `27/115` | **`0.9855`** |
| **`dy`** | `125` | `dy` | `0.9759` | **`dal`** | `115/128` | **`0.8768`** |
| **`chy`** | `118` | `chy` | `0.9912` | **`cheey`** | `49/133` | **`0.9859`** |
| **`shol`** | `117` | `chol` | `0.9815` | **`chol`** | `57/100` | **`0.9815`** |
| **`ol`** | `109` | `ol` | `0.9812` | **`al`** | `422/187` | **`0.9787`** |
| **`y`** | `107` | `y` | `0.9741` | **`dar`** | `171/184` | **`0.8780`** |
| **`or`** | `106` | `or` | `0.9797` | **`ar`** | `259/265` | **`0.9796`** |
| **`sho`** | `103` | `o` | `0.9767` | **`o`** | `14/77` | **`0.9767`** |
| **`dain`** | `99` | `ykaiin` | `0.9700` | **`ykaiin`** | `111/35` | **`0.9700`** |
| **`dar`** | `98` | `dar` | `0.9615` | **`sar`** | `184/51` | **`0.8988`** |
| **`cthy`** | `93` | `oky` | `0.9829` | **`oky`** | `6/51` | **`0.9829`** |
| **`chey`** | `89` | `chy` | `0.9899` | **`chy`** | `247/49` | **`0.9899`** |
| **`aiin`** | `86` | `ain` | `0.9768` | **`ain`** | `368/97` | **`0.9768`** |
| **`dal`** | `80` | `dal` | `0.9765` | **`qol`** | `128/136` | **`0.9138`** |
| **`o`** | `72` | `o` | `0.9881` | **`cheo`** | `77/42` | **`0.9875`** |
| **`shor`** | `69` | `char` | `0.9712` | **`char`** | `26/43` | **`0.9712`** |
| **`cheol`** | `66` | `al` | `0.9866` | **`al`** | `98/187` | **`0.9866`** |
| **`shy`** | `64` | `chy` | `0.9898` | **`chy`** | `37/49` | **`0.9898`** |
| **`dol`** | `62` | `dal` | `0.9670` | **`dal`** | `43/128` | **`0.9670`** |
| **`cho`** | `60` | `cheo` | `0.9775` | **`cheo`** | `16/42` | **`0.9775`** |
| **`shey`** | `59` | `chey` | `0.9905` | **`chey`** | `202/247` | **`0.9905`** |
| **`ar`** | `55` | `ar` | `0.9867` | **`air`** | `265/51` | **`0.9782`** |

---

## 4. Top 12 Aligned Cross-Dialect Parallel Clause Trees (`Currier A <-> Currier B`)
| Alignment Score | Currier A Clause (`$L=A`) | Currier B Parallel Clause (`$L=B`) | Shared Constituent Skeleton |
| :---: | :--- | :--- | :--- |
| **`0.7690`** | `f20v.4 (H)`: `sho . or . aiin . shol . daiin` | `f85r2.4 (C)`: `dair . sheo . oraiin . chol . daiin` | `NP_MEAS -> NP_MEAS -> NP_MEAS -> NP_MEAS -> NP_MEAS` |
| **`0.7428`** | `f27r.12 (H)`: `dain . cheokeey . chey . cthey . otal` | `f94v.12 (H)`: `daiin . chcthy . chdy . chckhy . okaiin` | `NP_MEAS -> VP_PROC -> VP_PROC -> VP_PROC -> NP_MEAS` |
| **`0.6277`** | `f30r.13 (H)`: `chodaiin . chtchey . chear . shy . keey` | `f106r.35 (S)`: `okaiin . choky . lkar . chdy . lchedy` | `NP_MEAS -> VP_PROC -> NP_MEAS -> VP_PROC -> VP_PROC` |
| **`0.6205`** | `f22v.8 (H)`: `qotchy . cthy . qokol . daiin . dam` | `f104r.9 (S)`: `ycheeoy . qokecho . qokol . cheeo . dam` | `VP_PROC -> VP_PROC -> VP_PROC -> NP_MEAS -> PP_PREP` |
| **`0.6152`** | `f4r.9 (H)`: `daiin . ckhochy . tchy . kor . aiin` | `f94v.12 (H)`: `daiin . chcthy . chdy . chckhy . okaiin` | `NP_MEAS -> VP_PROC -> VP_PROC -> NP_MEAS -> NP_MEAS` |
| **`0.6123`** | `f1r.20 (T)`: `shok . chor . chey . dain . ckhey` | `f31r.14 (H)`: `saiis . or . chedy . daiin . okeedy` | `NP_MEAS -> NP_MEAS -> VP_PROC -> NP_MEAS -> VP_PROC` |
| **`0.5998`** | `f7r.10 (H)`: `s . chain . chor . daiin . chckhy` | `f85r2.2 (C)`: `sain . or . or . aiin . opchdy` | `PP_PREP -> NP_MEAS -> NP_MEAS -> NP_MEAS -> VP_PROC` |
| **`0.5966`** | `f15v.11 (H)`: `sol . oiin . cheor . chol . daiin . cthy` | `f82r.33 (B)`: `sain . ol . cheol . ey . cheor . chey` | `PP_PREP -> NP_MEAS -> NP_MEAS -> NP_MEAS -> NP_MEAS -> VP_PROC` |
| **`0.5917`** | `f11r.4 (H)`: `dchol . chy . kchy . dy . daiin` | `f94v.12 (H)`: `daiin . chcthy . chdy . chckhy . okaiin` | `NP_MEAS -> VP_PROC -> VP_PROC -> PP_PREP -> NP_MEAS` |
| **`0.5904`** | `f4v.5 (H)`: `shor . sheey . otoiin . shey . qotchoiin . chodain` | `f104v.21 (S)`: `yshor . sheedy . qokaiin . shokchey . qokeey . chodain` | `NP_MEAS -> VP_PROC -> NP_MEAS -> VP_PROC -> VP_PROC -> NP_MEAS` |
| **`0.5868`** | `f24r.12 (H)`: `qokchy . qotchy . tol . tod . ckhy` | `f83v.8 (B)`: `rolkeedy . qokaiin . okaiin . ched . okchey` | `VP_PROC -> VP_PROC -> NP_MEAS -> NP_MEAS -> VP_PROC` |
| **`0.5787`** | `f22v.10 (H)`: `qokchy . daiin . s . or . ytal` | `f80v.29 (B)`: `qokain . olkain . olkain . ol . keeol` | `VP_PROC -> NP_MEAS -> PP_PREP -> NP_MEAS -> NP_MEAS` |

---

## 5. Full Constituent-Bracketed & Cross-Dialect Annotated Editions of 6 Landmark Folios
Notation inside each bracketed constituent `[TYPE: words (≡fused / <split) [Dialect Counterpart]]`:
- `(≡AB)` indicates a 2-word analytical constituent that also appears in the corpus as the single fused word `AB`.
- `(<A+B)` indicates a single fused word decomposed into its underlying `A + B` constituent morphemes.
- `[B:word]` / `[A:word]` provides the top cross-dialect distributional counterpart between Currier A and Currier B.

### Folio `f20v` (Section `$I=H`, Currier `$L=A`, Hand `$H=1`, `11` lines)
- **`<f20v.1,@P0>`** <%> `faiisar . okoy . shypofochey . opchy . qopy . choldy . opydy . cphy`
  - **Tree**: `[TOP_HEAD: faiisar . okoy] [VP_PROC: shypofochey] [NP_MEAS: opchy] [VP_PROC: qopy . choldy] [NP_MEAS: opydy] [NP_MEAS: cphy]`
- **`<f20v.2,+P0>`** `sos . ykoiin . cheol . chol . choiin . checthy . otol . chol . chodaiin . oty`
  - **Tree**: `[PP_PREP: sos . ykoiin] [NP_MEAS: cheol [B:al]] [NP_MEAS: chol [B:ol]] [NP_MEAS: choiin] [VP_PROC: checthy] [NP_MEAS: otol [B:ol]] [NP_MEAS: chol [B:ol]] [NP_MEAS: chodaiin (<cho+daiin) [B:okaiin]] [NP_MEAS: oty [B:oky]]`
- **`<f20v.3,+P0>`** `okchy . shokchol . shol . chcthy . qoty . chy . tolshy . qotchy`
  - **Tree**: `[NP_MEAS: okchy] [NP_MEAS: shokchol] [PP_PREP: shol [B:chol]] [VP_PROC: chcthy . qoty . chy [B:lchey,B:cheey]] [NP_MEAS: tolshy] [VP_PROC: qotchy [B:olkeey]]`
- **`<f20v.4,+P0>`** `sho . or . aiin . shol . daiin`
  - **Tree**: `[PP_PREP: sho . or [B:o,B:ar]] [NP_MEAS: aiin [B:ain]] [PP_PREP: shol . daiin (≡sholdaiin) [B:chol,B:okaiin]]`
- **`<f20v.5,+P0>`** <%> `tshol . folchol . otor . shol . shor . fshodchy . otchy . chcphy . dy`
  - **Tree**: `[TOP_HEAD: tshol . folchol] [NP_MEAS: otor] [PP_PREP: shol [B:chol]] [PP_PREP: shor . fshodchy [B:char]] [NP_MEAS: otchy [B:shy]] [VP_PROC: chcphy] [FIN_CLOSE: dy [B:dal]]`
- **`<f20v.6,+P0>`** `doiiin . chockhy . dan . cheoy . shos . cheos . char . cthaiin`
  - **Tree**: `[NP_MEAS: doiiin] [VP_PROC: chockhy (<cho+ckhy)] [PP_PREP: dan] [VP_PROC: cheoy] [PP_PREP: shos . cheos] [NP_MEAS: char [B:otar]] [NP_MEAS: cthaiin]`
- **`<f20v.7,+P0>`** `shocthy . sho . cthy . daiin . sheoy . tey . s . soaiin`
  - **Tree**: `[VP_PROC: shocthy (<sho+cthy)] [PP_PREP: sho . cthy (≡shocthy) [B:o,B:oky]] [NP_MEAS: daiin (<d+aiin) [B:okaiin]] [VP_PROC: sheoy] [NP_MEAS: tey] [PP_PREP: s . soaiin [B:dal]]`
- **`<f20v.8,+P0>`** `shain . choraly . sho . ar . chy . daiin . d . s`
  - **Tree**: `[PP_PREP: shain] [VP_PROC: choraly] [PP_PREP: sho . ar (≡shoar) [B:o,B:air]] [VP_PROC: chy [B:cheey]] [NP_MEAS: daiin (<d+aiin) [B:okaiin]] [PP_PREP: d [B:s]] [PP_PREP: s [B:dal]]`
- **`<f20v.9,+P0>`** `ykchy . keody . cho . cthy . chol . shd . qoty . d`
  - **Tree**: `[PP_PREP: ykchy . keody] [NP_MEAS: cho [B:cheo]] [NP_MEAS: cthy [B:oky]] [NP_MEAS: chol [B:ol]] [PP_PREP: shd] [VP_PROC: qoty [B:lchey]] [PP_PREP: d [B:s]]`
- **`<f20v.10,+P0>`** `shokaiin . chocthy . chol . daiin . chy . chor . ety`
  - **Tree**: `[NP_MEAS: shokaiin (<sho+kaiin)] [VP_PROC: chocthy (<cho+cthy)] [NP_MEAS: chol . daiin (≡choldaiin) [B:ol,B:okaiin]] [VP_PROC: chy [B:cheey]] [NP_MEAS: chor [B:otar]] [NP_MEAS: ety]`
- **`<f20v.11,+P0>`** `okoiin . chey . ol . chory`
  - **Tree**: `[NP_MEAS: okoiin] [VP_PROC: chey [B:chy]] [VP_PROC: ol . chory [B:al]]`

### Folio `f1r` (Section `$I=T`, Currier `$L=A`, Hand `$H=1`, `28` lines)
- **`<f1r.1,@P0>`** <%> `fachys . ykal . ar . ataiin . shol . shory . cthres . y . kor . sholdy`
  - **Tree**: `[TOP_HEAD: fachys] [PP_PREP: ykal . ar [B:air]] [NP_MEAS: ataiin] [PP_PREP: shol [B:chol]] [VP_PROC: shory] [NP_MEAS: cthres] [PP_PREP: y . kor (≡ykor) [B:dar]] [VP_PROC: sholdy]`
- **`<f1r.2,+P0>`** `sory . ckhar . ory . kair . chtaiin . shar . ase . cthar . cthardan`
  - **Tree**: `[PP_PREP: sory . ckhar] [NP_MEAS: ory] [NP_MEAS: kair] [NP_MEAS: chtaiin] [PP_PREP: shar . ase] [NP_MEAS: cthar] [NP_MEAS: cthardan]`
- **`<f1r.3,+P0>`** `syaiir . sheky . or . ykaiin . shod . cthoary . cthes . daraiin . sy`
  - **Tree**: `[NP_MEAS: syaiir] [VP_PROC: sheky] [NP_MEAS: or [B:ar]] [NP_MEAS: ykaiin (<y+kaiin)] [PP_PREP: shod . cthoary] [NP_MEAS: cthes] [NP_MEAS: daraiin] [PP_PREP: sy]`
- **`<f1r.4,+P0>`** `soiin . oteey . oteosroloty . cthiardaiin . okaiin . or . okan`
  - **Tree**: `[PP_PREP: soiin . oteey] [NP_MEAS: oteosroloty] [NP_MEAS: cthiardaiin] [NP_MEAS: okaiin [B:otaiin]] [NP_MEAS: or [B:ar]] [NP_MEAS: okan]`
- **`<f1r.5,+P0>`** `sairy . chear . cthaiin . cphar . cfhaiin`
  - **Tree**: `[PP_PREP: sairy . chear] [NP_MEAS: cthaiin] [NP_MEAS: cphar] [NP_MEAS: cfhaiin]`
- **`<f1r.6,=Pt>`** `ydaraishy`
  - **Tree**: `[NP_MEAS: ydaraishy]`
- **`<f1r.7,*P0>`** <%> `odar . shol . cphoy . oydar . sh . s . cfhoaiin . shodary`
  - **Tree**: `[TOP_HEAD: odar] [PP_PREP: shol . cphoy [B:chol]] [NP_MEAS: oydar] [PP_PREP: sh] [PP_PREP: s . cfhoaiin [B:dal]] [VP_PROC: shodary]`
- **`<f1r.8,+P0>`** `yshey . shody . okchoy . otchol . chocthy . oschy . dain . chor . kos`
  - **Tree**: `[PP_PREP: yshey] [VP_PROC: shody] [NP_MEAS: okchoy] [NP_MEAS: otchol] [VP_PROC: chocthy (<cho+cthy)] [NP_MEAS: oschy . dain [B:ykaiin]] [NP_MEAS: chor [B:otar]] [NP_MEAS: kos]`
- **`<f1r.9,+P0>`** `daiin . shos . cfhol . shody`
  - **Tree**: `[NP_MEAS: daiin (<d+aiin) [B:okaiin]] [PP_PREP: shos . cfhol] [VP_PROC: shody]`
- **`<f1r.10,=Pt>`** `dain . os . teody`
  - **Tree**: `[NP_MEAS: dain [B:ykaiin]] [NP_MEAS: os] [NP_MEAS: teody]`
- **`<f1r.11,*P0>`** <%> `ydain . cphesaiin . ols . cphey . ytain . shoshy . cphodales`
  - **Tree**: `[TOP_HEAD: ydain . cphesaiin] [NP_MEAS: ols] [NP_MEAS: cphey] [PP_PREP: ytain] [VP_PROC: shoshy] [NP_MEAS: cphodales]`
- **`<f1r.12,+P0>`** `oksho . kshoy . otairin . oteol . okan . shodain . sckhey . daiin`
  - **Tree**: `[NP_MEAS: oksho] [NP_MEAS: kshoy] [NP_MEAS: otairin] [NP_MEAS: oteol] [NP_MEAS: okan] [NP_MEAS: shodain] [NP_MEAS: sckhey . daiin [B:okaiin]]`
- **`<f1r.13,+P0>`** `shoy . ckhey . kodaiin . cphy . cphodaiils . cthey . sho . oldain . d`
  - **Tree**: `[VP_PROC: shoy] [NP_MEAS: ckhey] [NP_MEAS: kodaiin] [NP_MEAS: cphy] [NP_MEAS: cphodaiils] [NP_MEAS: cthey [B:chckhy]] [PP_PREP: sho . oldain [B:o]] [PP_PREP: d [B:s]]`
- **`<f1r.14,+P0>`** `dain . oiin . chol . odaiin . chodain . chdy . okain . dn . cthy . kod`
  - **Tree**: `[NP_MEAS: dain [B:ykaiin]] [NP_MEAS: oiin] [NP_MEAS: chol [B:ol]] [NP_MEAS: odaiin] [NP_MEAS: chodain] [VP_PROC: chdy] [NP_MEAS: okain] [PP_PREP: dn . cthy [B:oky]] [NP_MEAS: kod]`
- **`<f1r.15,+P0>`** `daiin . shckhey . eo . r . char . shey . kol . chol . chol . kor . chal`
  - **Tree**: `[NP_MEAS: daiin (<d+aiin) [B:okaiin]] [VP_PROC: shckhey] [NP_MEAS: eo] [NP_MEAS: r [B:ar]] [NP_MEAS: char [B:otar]] [VP_PROC: shey [B:chey]] [NP_MEAS: kol] [NP_MEAS: chol [B:ol]] [NP_MEAS: chol [B:ol]] [NP_MEAS: kor] [NP_MEAS: chal]`
- **`<f1r.16,+P0>`** `sho . chol . shodan . kshy . kchy . d . or . chodaiin . sho . koeam`
  - **Tree**: `[PP_PREP: sho . chol [B:o,B:ol]] [NP_MEAS: shodan] [NP_MEAS: kshy] [NP_MEAS: kchy [B:otey]] [PP_PREP: d . or (≡dor) [B:s,B:ar]] [NP_MEAS: chodaiin (<cho+daiin) [B:okaiin]] [PP_PREP: sho [B:o]] [FIN_CLOSE: koeam]`
- **`<f1r.17,+P0>`** `ycho . tchey . chekain . sheopshol . dydyd . cthy . daiy`
  - **Tree**: `[PP_PREP: ycho . tchey] [NP_MEAS: chekain] [NP_MEAS: sheopshol] [PP_PREP: dydyd . cthy [B:oky]] [PP_PREP: daiy]`
- **`<f1r.18,+P0>`** `yto . shol . she . kodshey . cphealy . darain . dain . ckhyds`
  - **Tree**: `[PP_PREP: yto] [PP_PREP: shol [B:chol]] [PP_PREP: she . kodshey] [NP_MEAS: cphealy] [NP_MEAS: darain . dain [B:ykaiin]] [NP_MEAS: ckhyds]`
- **`<f1r.19,+P0>`** `dchar . shcthaiin . okaiir . chey . chy . tol . cthols . dloo`
  - **Tree**: `[PP_PREP: dchar . shcthaiin] [NP_MEAS: okaiir] [VP_PROC: chey . chy [B:chy,B:cheey]] [NP_MEAS: tol] [NP_MEAS: cthols] [PP_PREP: dloo]`
- **`<f1r.20,+P0>`** `shok . chor . chey . dain . ckhey`
  - **Tree**: `[PP_PREP: shok . chor [B:otar]] [VP_PROC: chey [B:chy]] [NP_MEAS: dain [B:ykaiin]] [NP_MEAS: ckhey]`

### Folio `f78r` (Section `$I=B`, Currier `$L=B`, Hand `$H=2`, `47` lines)
- **`<f78r.1,@Lt>`** `okchdldlo`
  - **Tree**: `[NP_MEAS: okchdldlo]`
- **`<f78r.2,@Lt>`** `okchdy`
  - **Tree**: `[NP_MEAS: okchdy]`
- **`<f78r.3,@P0>`** <%> `tshedor . shedy . qopchedy . qokedy . dyqokol . oky`
  - **Tree**: `[TOP_HEAD: tshedor] [VP_PROC: shedy . qopchedy . qokedy [A:shey/shol,A:qoky/cthy]] [NP_MEAS: dyqokol] [NP_MEAS: oky [A:cthy]]`
- **`<f78r.4,+P0>`** `qokeedy . qokedy . shedy . tchedy . otar . olkedy . dam`
  - **Tree**: `[VP_PROC: qokeedy . qokedy . shedy [A:qotchy/cthy,A:qoky/cthy,A:shey/shol]] [NP_MEAS: tchedy] [NP_MEAS: otar [A:chor]] [VP_PROC: olkedy (<ol+kedy)] [FIN_CLOSE: dam]`
- **`<f78r.5,+P0>`** `qckhedy . cheky . dol . chedy . qokedy . qokain . olkedy`
  - **Tree**: `[NP_MEAS: qckhedy] [VP_PROC: cheky [A:okeey]] [PP_PREP: dol] [VP_PROC: chedy . qokedy . qokain [A:chey/chol,A:qoky/cthy]] [VP_PROC: olkedy (<ol+kedy)]`
- **`<f78r.6,+P0>`** `yteedy . qotal . dolshedy . qokedar . chcthey . otor . dor . or`
  - **Tree**: `[NP_MEAS: yteedy] [VP_PROC: qotal] [NP_MEAS: dolshedy] [VP_PROC: qokedar . chcthey] [NP_MEAS: otor] [PP_PREP: dor . or [A:dair]]`
- **`<f78r.7,+P0>`** `qokal . otedy . qokedy . qokedy . dal . qokedy . qokedy . sam`
  - **Tree**: `[VP_PROC: qokal [A:qokol]] [NP_MEAS: otedy] [VP_PROC: qokedy . qokedy [A:qoky/cthy,A:qoky/cthy]] [VP_PROC: dal . qokedy . qokedy [A:s,A:qoky/cthy,A:qoky/cthy]] [FIN_CLOSE: sam]`
- **`<f78r.8,+P0>`** `dshedy . qokedy . okar . qokedy . shedy . ykedy . shedy . qoky`
  - **Tree**: `[NP_MEAS: dshedy (<d+shedy)] [VP_PROC: qokedy (<qo+kedy) [A:qoky/cthy]] [NP_MEAS: okar] [VP_PROC: qokedy . shedy [A:qoky/cthy,A:shey/shol]] [NP_MEAS: ykedy (<y+kedy)] [VP_PROC: shedy . qoky [A:shey/shol]]`
- **`<f78r.9,+P0>`** `schedy . keedy . qokedy . chckhd . qokain . chedy . qotedy . dy`
  - **Tree**: `[NP_MEAS: schedy (<s+chedy)] [NP_MEAS: keedy] [VP_PROC: qokedy (<qo+kedy) [A:qoky/cthy]] [NP_MEAS: chckhd] [VP_PROC: qokain . chedy . qotedy [A:chey/chol]] [FIN_CLOSE: dy [A:dam]]`
- **`<f78r.10,+P0>`** `dshedy . deedy . qokeedy . otedy . otal . tedy . otey . oloiin`
  - **Tree**: `[NP_MEAS: dshedy (<d+shedy)] [NP_MEAS: deedy] [VP_PROC: qokeedy (<qo+keedy) [A:qotchy/cthy]] [NP_MEAS: otedy] [NP_MEAS: otal] [NP_MEAS: tedy] [NP_MEAS: otey [A:kchy]] [NP_MEAS: oloiin]`
- **`<f78r.11,+P0>`** `qoky . okeedy . sheety . qoteedy . otey . shckhedy . sokol . or`
  - **Tree**: `[VP_PROC: qoky] [NP_MEAS: okeedy] [VP_PROC: sheety . qoteedy] [NP_MEAS: otey [A:kchy]] [VP_PROC: shckhedy] [PP_PREP: sokol . or [A:dair]]`
- **`<f78r.12,+P0>`** `dor . shekedy . qokol . kechdy . otedy . ol . tedy . chckhedy`
  - **Tree**: `[PP_PREP: dor] [VP_PROC: shekedy . qokol [A:qokeol]] [NP_MEAS: kechdy] [NP_MEAS: otedy] [VP_PROC: ol [A:chol]] [NP_MEAS: tedy] [VP_PROC: chckhedy]`
- **`<f78r.13,+P0>`** `qokedy . olkedy . qokain . okedy . kedy . toldy . qoteedydy`
  - **Tree**: `[VP_PROC: qokedy . olkedy . qokain [A:qoky/cthy]] [NP_MEAS: okedy] [NP_MEAS: kedy] [NP_MEAS: toldy] [VP_PROC: qoteedydy]`
- **`<f78r.14,+P0>`** `sor . checkhy . or . chckhdy . dol . kedy . qokededy . qokan . ol`
  - **Tree**: `[PP_PREP: sor] [VP_PROC: checkhy] [NP_MEAS: or [A:dair]] [VP_PROC: chckhdy] [PP_PREP: dol . kedy] [VP_PROC: qokededy . qokan] [NP_MEAS: ol [A:chol]]`
- **`<f78r.15,+P0>`** `dchckhedy . qokchdy . qokedy . okedy . dalor . okeed . olkain`
  - **Tree**: `[NP_MEAS: dchckhedy] [VP_PROC: qokchdy . qokedy [A:qoky/cthy]] [NP_MEAS: okedy] [PP_PREP: dalor . okeed] [NP_MEAS: olkain]`
- **`<f78r.16,+P0>`** `qokol . oted . okain . ched . ar . alory`
  - **Tree**: `[VP_PROC: qokol [A:qokeol]] [NP_MEAS: oted] [NP_MEAS: okain] [NP_MEAS: ched] [NP_MEAS: ar [A:or]] [NP_MEAS: alory]`
- **`<f78r.17,+P0>`** `soiin . kar . kedy . pchey . tchdoltdy`
  - **Tree**: `[PP_PREP: soiin . kar] [NP_MEAS: kedy] [NP_MEAS: pchey] [NP_MEAS: tchdoltdy]`
- **`<f78r.18,+P0>`** `olchedy . qokain . dar . ar . okain`
  - **Tree**: `[VP_PROC: olchedy . qokain] [PP_PREP: dar . ar (≡darar) [A:y,A:or]] [NP_MEAS: okain]`
- **`<f78r.19,+P0>`** `y . ches . aiin . okeedy . qokain . chl`
  - **Tree**: `[PP_PREP: y . ches (≡yches)] [NP_MEAS: aiin] [NP_MEAS: okeedy] [VP_PROC: qokain] [NP_MEAS: chl]`
- **`<f78r.20,+P0>`** `solshedy . dalshdy . qokychdy`
  - **Tree**: `[NP_MEAS: solshedy] [NP_MEAS: dalshdy] [VP_PROC: qokychdy]`

### Folio `f85r2` (Section `$I=C`, Currier `$L=B`, Hand `$H=2`, `24` lines)
- **`<f85r2.1,@Cc>`** `odeedy . otedy . opaees . ar . chcthy . otchdy . otody . otar . chepaiin . otodar . otodaiin . opaiin . otaiin . qopchas . otchedy . olkaiin . odar . aloees . otchedy . qotedaiin . odar . octhody . shedaiin . olaiin . olfor . daiin . ol . lkechch . os . aiin . oteedy . dar . otees . opaiin . chcphdar`
  - **Tree**: `[NP_MEAS: odeedy] [NP_MEAS: otedy] [NP_MEAS: opaees] [NP_MEAS: ar [A:or]] [VP_PROC: chcthy] [NP_MEAS: otchdy] [NP_MEAS: otody] [NP_MEAS: otar [A:chor]] [NP_MEAS: chepaiin] [NP_MEAS: otodar] [NP_MEAS: otodaiin] [NP_MEAS: opaiin] [NP_MEAS: otaiin [A:okaiin]] [VP_PROC: qopchas] [NP_MEAS: otchedy] [NP_MEAS: olkaiin (<ol+kaiin)] [NP_MEAS: odar] [NP_MEAS: aloees] [NP_MEAS: otchedy] [VP_PROC: qotedaiin] [NP_MEAS: odar] [NP_MEAS: octhody] [NP_MEAS: shedaiin] [NP_MEAS: olaiin (<ol+aiin)] [NP_MEAS: olfor . daiin] [VP_PROC: ol [A:chol]] [NP_MEAS: lkechch] [NP_MEAS: os . aiin (≡osaiin)] [NP_MEAS: oteedy] [PP_PREP: dar . otees [A:y]] [NP_MEAS: opaiin] [NP_MEAS: chcphdar]`
- **`<f85r2.2,@Pb>`** <%> `sain . or . oraiin . opchdy`
  - **Tree**: `[TOP_HEAD: sain . or [A:saiin,A:dair]] [NP_MEAS: oraiin (<or+aiin)] [NP_MEAS: opchdy]`
- **`<f85r2.3,+Pb>`** `qotor . sheedy . shodaiin . olfarary`
  - **Tree**: `[VP_PROC: qotor . sheedy] [NP_MEAS: shodaiin (<sho+daiin)] [NP_MEAS: olfarary]`
- **`<f85r2.4,+Pb>`** `dair . sheo . oraiin . choldaiin`
  - **Tree**: `[PP_PREP: dair] [PP_PREP: sheo . oraiin] [NP_MEAS: choldaiin (<chol+daiin)]`
- **`<f85r2.5,+Pb>`** `ockhdar . olkar . shoral`
  - **Tree**: `[NP_MEAS: ockhdar] [NP_MEAS: olkar] [NP_MEAS: shoral]`
- **`<f85r2.6,+Pb>`** `roseer`
  - **Tree**: `[NP_MEAS: roseer]`
- **`<f85r2.7,@Pb>`** <%> `pchedeey . olkey . qokedy . sheos . fcheey`
  - **Tree**: `[TOP_HEAD: pchedeey] [VP_PROC: olkey . qokedy [A:qoky/cthy]] [PP_PREP: sheos . fcheey]`
- **`<f85r2.8,+Pb>`** `otchedy . chotey . qocthey . oteey . ol . oloqorain`
  - **Tree**: `[NP_MEAS: otchedy] [VP_PROC: chotey . qocthey] [NP_MEAS: oteey [A:qokeey]] [VP_PROC: ol [A:chol]] [NP_MEAS: oloqorain]`
- **`<f85r2.9,+Pb>`** `daiin . qotaiin . tchedy . otedy . qotchdy . chckhey`
  - **Tree**: `[NP_MEAS: daiin (<d+aiin)] [VP_PROC: qotaiin (<qo+taiin)] [NP_MEAS: tchedy] [NP_MEAS: otedy] [VP_PROC: qotchdy . chckhey]`
- **`<f85r2.10,+Pb>`** `ytchedyqodar . qotedar . qokar . qotchd . qotom`
  - **Tree**: `[NP_MEAS: ytchedyqodar] [VP_PROC: qotedar . qokar . qotchd] [FIN_CLOSE: qotom]`
- **`<f85r2.11,+Pb>`** `soiisaiin . shedaiin . chokm`
  - **Tree**: `[NP_MEAS: soiisaiin] [NP_MEAS: shedaiin] [FIN_CLOSE: chokm]`
- **`<f85r2.12,@Pb>`** <%> `otchs . shedor . cheysorain`
  - **Tree**: `[TOP_HEAD: otchs . shedor] [NP_MEAS: cheysorain]`
- **`<f85r2.13,+Pb>`** `or . shedy . tedy . sodaiiin . chy`
  - **Tree**: `[NP_MEAS: or [A:dair]] [VP_PROC: shedy [A:shey/shol]] [NP_MEAS: tedy] [NP_MEAS: sodaiiin] [VP_PROC: chy [A:chey]]`
- **`<f85r2.14,+Pb>`** `ytedar . chzs . aiin . arody`
  - **Tree**: `[NP_MEAS: ytedar] [NP_MEAS: chzs . aiin] [NP_MEAS: arody]`
- **`<f85r2.15,+Pb>`** `ypshedy . dar . chedy . oram`
  - **Tree**: `[TOP_HEAD: ypshedy] [PP_PREP: dar [A:y]] [VP_PROC: chedy [A:chey/chol]] [FIN_CLOSE: oram]`
- **`<f85r2.16,+Pb>`** `oteey . qodaiin . odain . an . chey`
  - **Tree**: `[NP_MEAS: oteey [A:qokeey]] [VP_PROC: qodaiin (<qo+daiin)] [NP_MEAS: odain] [NP_MEAS: an] [VP_PROC: chey [A:shey]]`
- **`<f85r2.17,+Pb>`** `orar . oldar . ain`
  - **Tree**: `[NP_MEAS: orar] [NP_MEAS: oldar . ain [A:aiin]]`
- **`<f85r2.18,@Pb>`** <%> `okees . olaiin . qokal . chdy . sary`
  - **Tree**: `[TOP_HEAD: okees . olaiin] [VP_PROC: qokal . chdy (≡qokalchdy) [A:qokol,A:chody]] [PP_PREP: sary]`
- **`<f85r2.19,+Pb>`** `qokshedy . qodain . chckhy . ykeedy . chedy`
  - **Tree**: `[VP_PROC: qokshedy . qodain . chckhy [A:cthey]] [NP_MEAS: ykeedy (<y+keedy)] [VP_PROC: chedy [A:chey/chol]]`
- **`<f85r2.20,+Pb>`** `oraiin . ckheda . or . ain . olchey . qokal . shedy`
  - **Tree**: `[NP_MEAS: oraiin (<or+aiin)] [NP_MEAS: ckheda] [NP_MEAS: or . ain (≡orain) [A:dair,A:aiin]] [VP_PROC: olchey . qokal . shedy [A:qokol,A:shey/shol]]`

### Folio `f99r` (Section `$I=P`, Currier `$L=A`, Hand `$H=1`, `52` lines)
- **`<f99r.1,@Lc>`** `okaradag`
  - **Tree**: `[NP_MEAS: okaradag]`
- **`<f99r.2,@Lf>`** `okary`
  - **Tree**: `[NP_MEAS: okary]`
- **`<f99r.3,@Lf>`** `darar`
  - **Tree**: `[PP_PREP: darar]`
- **`<f99r.4,@Lf>`** `oky`
  - **Tree**: `[NP_MEAS: oky [B:chy]]`
- **`<f99r.5,@Lf>`** `salo`
  - **Tree**: `[PP_PREP: salo]`
- **`<f99r.6,@Lf>`** `aro`
  - **Tree**: `[NP_MEAS: aro]`
- **`<f99r.7,+Lf>`** `ain`
  - **Tree**: `[NP_MEAS: ain]`
- **`<f99r.8,@Lf>`** `okor`
  - **Tree**: `[NP_MEAS: okor]`
- **`<f99r.9,@Lf>`** `ralol`
  - **Tree**: `[NP_MEAS: ralol]`
- **`<f99r.10,@Lf>`** `skeeal`
  - **Tree**: `[NP_MEAS: skeeal]`
- **`<f99r.11,@Lf>`** `okary`
  - **Tree**: `[NP_MEAS: okary]`
- **`<f99r.12,@Lf>`** `okolo`
  - **Tree**: `[NP_MEAS: okolo]`
- **`<f99r.13,@Lf>`** `otalam`
  - **Tree**: `[FIN_CLOSE: otalam]`
- **`<f99r.14,@Lf>`** `otoldy`
  - **Tree**: `[NP_MEAS: otoldy]`
- **`<f99r.15,@P0>`** <%> `pcheody . oteody . daiin . cpheey . tshol . dal . cfheol . olaiin . sar`
  - **Tree**: `[TOP_HEAD: pcheody . oteody] [NP_MEAS: daiin (<d+aiin) [B:okaiin]] [NP_MEAS: cpheey] [NP_MEAS: tshol] [VP_PROC: dal [B:qol]] [NP_MEAS: cfheol] [NP_MEAS: olaiin (<ol+aiin)] [PP_PREP: sar]`
- **`<f99r.16,+P0>`** `saroshy . shor . sshor . sheol . kolsheol . qoeol . sholkol . ckhol . ckhory`
  - **Tree**: `[NP_MEAS: saroshy] [PP_PREP: shor [B:char]] [PP_PREP: sshor] [PP_PREP: sheol . kolsheol [B:al]] [VP_PROC: qoeol] [NP_MEAS: sholkol] [NP_MEAS: ckhol] [NP_MEAS: ckhory]`
- **`<f99r.17,+P0>`** `dcheor . chr . al . yckhy . okeol . ckhor . oraiin . chor . qokeeor . chory`
  - **Tree**: `[NP_MEAS: dcheor] [NP_MEAS: chr] [VP_PROC: al] [PP_PREP: yckhy . okeol [B:okal]] [NP_MEAS: ckhor] [NP_MEAS: oraiin (<or+aiin)] [NP_MEAS: chor [B:otar]] [VP_PROC: qokeeor . chory]`
- **`<f99r.18,+P0>`** `qokeor . chol . ykol . cheey . chody . ckhol . daiin . okeoly . daiin . ckhy`
  - **Tree**: `[VP_PROC: qokeor] [NP_MEAS: chol [B:ol]] [PP_PREP: ykol] [VP_PROC: cheey . chody [B:sheey,B:chdy]] [NP_MEAS: ckhol . daiin [B:okaiin]] [NP_MEAS: okeoly . daiin [B:okaiin]] [NP_MEAS: ckhy]`
- **`<f99r.19,@Lc>`** `oparal`
  - **Tree**: `[TOP_HEAD: oparal]`
- **`<f99r.20,@Lf>`** `oaro`
  - **Tree**: `[NP_MEAS: oaro]`

### Folio `f107r` (Section `$I=S`, Currier `$L=B`, Hand `$H=3`, `51` lines)
- **`<f107r.1,@P0>`** <%> `pchdlar . sheolor . ykeeol . qokchy . otor . okeesodar . tarair . oteey . otaiin . ytar`
  - **Tree**: `[TOP_HEAD: pchdlar . sheolor] [NP_MEAS: ykeeol] [VP_PROC: qokchy] [NP_MEAS: otor] [NP_MEAS: okeesodar] [NP_MEAS: tarair] [NP_MEAS: oteey [A:qokeey]] [NP_MEAS: otaiin [A:okaiin]] [PP_PREP: ytar]`
- **`<f107r.2,+P0>`** `dchey . qoteos . aiin . shedy . oteed . qor . aiin . cheockhy . olkeey . qotain . chey . qeeey . lor`
  - **Tree**: `[PP_PREP: dchey] [VP_PROC: qoteos] [NP_MEAS: aiin] [VP_PROC: shedy [A:shey/shol]] [NP_MEAS: oteed] [VP_PROC: qor] [NP_MEAS: aiin] [VP_PROC: cheockhy . olkeey . qotain [A:qotchy]] [VP_PROC: chey [A:shey]] [NP_MEAS: qeeey] [NP_MEAS: lor]`
- **`<f107r.3,+P0>`** `olcheey . cheos . qokeeey . ycheedy . qotain . ykain . okeey . raiin`
  - **Tree**: `[VP_PROC: olcheey] [NP_MEAS: cheos] [VP_PROC: qokeeey] [NP_MEAS: ycheedy] [VP_PROC: qotain] [PP_PREP: ykain . okeey] [NP_MEAS: raiin]`
- **`<f107r.4,+P0>`** <%> `teeody . chedain . qoteey . qokar . deeoltedy . otarain . chady . otokcho . qoked . okchedy`
  - **Tree**: `[TOP_HEAD: teeody . chedain] [VP_PROC: qoteey . qokar] [NP_MEAS: deeoltedy] [NP_MEAS: otarain] [VP_PROC: chady] [NP_MEAS: otokcho] [VP_PROC: qoked] [NP_MEAS: okchedy]`
- **`<f107r.5,+P0>`** `olkchedy . tedy . oteeey . okchedy . qokeed . qokear . chedy . chokchedy . qokain . ar`
  - **Tree**: `[VP_PROC: olkchedy] [NP_MEAS: tedy] [NP_MEAS: oteeey] [NP_MEAS: okchedy] [VP_PROC: qokeed . qokear . chedy [A:chey/chol]] [VP_PROC: chokchedy . qokain] [NP_MEAS: ar [A:or]]`
- **`<f107r.6,+P0>`** `okcheey . qokeedy . chotchedy . daiinar . oteey . lteey . chedaiin . okchey . otaiin . am`
  - **Tree**: `[NP_MEAS: okcheey] [VP_PROC: qokeedy . chotchedy [A:qotchy/cthy]] [NP_MEAS: daiinar] [NP_MEAS: oteey [A:qokeey]] [VP_PROC: lteey] [NP_MEAS: chedaiin] [NP_MEAS: okchey] [NP_MEAS: otaiin [A:okaiin]] [FIN_CLOSE: am]`
- **`<f107r.7,+P0>`** `ytaiin . cheotchey . okaiin . chckhy . okeedy . otcheey`
  - **Tree**: `[NP_MEAS: ytaiin (<y+taiin)] [VP_PROC: cheotchey] [NP_MEAS: okaiin [A:daiin]] [VP_PROC: chckhy [A:cthey]] [NP_MEAS: okeedy] [NP_MEAS: otcheey]`
- **`<f107r.8,+P0>`** <%> `torshor . sheeey . oteeol . qokeey . qokedy . lkaiin . qokaiin . qokaral . okiroley`
  - **Tree**: `[TOP_HEAD: torshor] [VP_PROC: sheeey] [NP_MEAS: oteeol] [VP_PROC: qokeey . qokedy [A:qokey/chey,A:qoky/cthy]] [NP_MEAS: lkaiin] [VP_PROC: qokaiin . qokaral [A:qokain/daiin]] [NP_MEAS: okiroley]`
- **`<f107r.9,+P0>`** `okaiin . sheey . tcheolkain . okeey . chedy . okeedy . chdykchedy . cheykainan`
  - **Tree**: `[NP_MEAS: okaiin [A:daiin]] [VP_PROC: sheey [A:cheey]] [NP_MEAS: tcheolkain] [NP_MEAS: okeey] [VP_PROC: chedy [A:chey/chol]] [NP_MEAS: okeedy] [VP_PROC: chdykchedy] [NP_MEAS: cheykainan]`
- **`<f107r.10,+P0>`** `yteedy . qokeedy . okeol . lchedy . qokal . lor . sheal . cheedaiin . chey . sair . alom`
  - **Tree**: `[NP_MEAS: yteedy] [VP_PROC: qokeedy (<qo+keedy) [A:qotchy/cthy]] [NP_MEAS: okeol] [VP_PROC: lchedy . qokal [A:qokol]] [NP_MEAS: lor] [PP_PREP: sheal . cheedaiin] [VP_PROC: chey [A:shey]] [PP_PREP: sair] [FIN_CLOSE: alom]`
- **`<f107r.11,+P0>`** `cheeo . cheeol . qokaiin . ytain . y . keeoll . oraiin . okaiin . okar . okaiin . otaram`
  - **Tree**: `[NP_MEAS: cheeo] [NP_MEAS: cheeol] [VP_PROC: qokaiin (<qo+kaiin) [A:qokain/daiin]] [PP_PREP: ytain] [PP_PREP: y . keeoll] [NP_MEAS: oraiin (<or+aiin)] [NP_MEAS: okaiin [A:daiin]] [NP_MEAS: okar] [NP_MEAS: okaiin [A:daiin]] [FIN_CLOSE: otaram]`
- **`<f107r.12,+P0>`** `ychol . chol . loraiir . aiinal`
  - **Tree**: `[PP_PREP: ychol . chol [A:shol]] [NP_MEAS: loraiir] [NP_MEAS: aiinal]`
- **`<f107r.13,+P0>`** <%> `polchlsaiin . sheky . qokaiin . opchal . shedy . pshedaiin . otodal . shedy . otaral`
  - **Tree**: `[TOP_HEAD: polchlsaiin] [VP_PROC: sheky . qokaiin [A:qokain/daiin]] [NP_MEAS: opchal] [VP_PROC: shedy [A:shey/shol]] [NP_MEAS: pshedaiin] [NP_MEAS: otodal] [VP_PROC: shedy [A:shey/shol]] [NP_MEAS: otaral]`
- **`<f107r.14,+P0>`** `cthedy . lshedy . cheolchear . oralam . chtaiin . otarain . chey . qokaiin . otain`
  - **Tree**: `[NP_MEAS: cthedy] [VP_PROC: lshedy] [NP_MEAS: cheolchear] [NP_MEAS: oralam] [NP_MEAS: chtaiin] [NP_MEAS: otarain] [VP_PROC: chey . qokaiin [A:shey,A:qokain/daiin]] [NP_MEAS: otain]`
- **`<f107r.15,+P0>`** `ychol . oiin . chey . qockhal . al . otaraiin . sheky . okeeey . raiin . airal`
  - **Tree**: `[PP_PREP: ychol . oiin] [VP_PROC: chey . qockhal [A:shey]] [VP_PROC: al [A:ol]] [NP_MEAS: otaraiin] [VP_PROC: sheky] [NP_MEAS: okeeey . raiin] [NP_MEAS: airal]`
- **`<f107r.16,+P0>`** `tolshoror . olkeedy . qotaiin . otalar . opcheol . qeeoy . shey . kair . otaiinam`
  - **Tree**: `[NP_MEAS: tolshoror] [VP_PROC: olkeedy . qotaiin] [NP_MEAS: otalar] [NP_MEAS: opcheol] [NP_MEAS: qeeoy] [VP_PROC: shey] [NP_MEAS: kair] [FIN_CLOSE: otaiinam]`
- **`<f107r.17,+P0>`** `sair . chey . losaiin . chey`
  - **Tree**: `[PP_PREP: sair] [VP_PROC: chey [A:shey]] [NP_MEAS: losaiin] [VP_PROC: chey [A:shey]]`
- **`<f107r.18,+P0>`** <%> `poalosy . shey . taray . farsheey . fol . rolchy . sheey . opolkaiin . ypaiinal`
  - **Tree**: `[TOP_HEAD: poalosy] [VP_PROC: shey] [NP_MEAS: taray] [NP_MEAS: farsheey] [NP_MEAS: fol] [NP_MEAS: rolchy] [VP_PROC: sheey [A:cheey]] [NP_MEAS: opolkaiin] [NP_MEAS: ypaiinal]`
- **`<f107r.19,+P0>`** `oaiin . ol . rar . sheey . ylaraiin . cholal . dy . cheeody . okeeey . cheodaiin . aldy`
  - **Tree**: `[NP_MEAS: oaiin] [VP_PROC: ol [A:chol]] [NP_MEAS: rar] [VP_PROC: sheey [A:cheey]] [NP_MEAS: ylaraiin] [NP_MEAS: cholal] [PP_PREP: dy [A:dam]] [VP_PROC: cheeody] [NP_MEAS: okeeey] [NP_MEAS: cheodaiin] [NP_MEAS: aldy]`
- **`<f107r.20,+P0>`** `tcheol . kcheedy`
  - **Tree**: `[NP_MEAS: tcheol] [NP_MEAS: kcheedy]`
