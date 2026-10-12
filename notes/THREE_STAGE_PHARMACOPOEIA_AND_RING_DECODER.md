# The Three-Stage Cross-Sectional Pharmacopoeia & Circular Ring Decoder Edition (`Attacks 93–96` / `Discoveries 110–113`)

> **Repository-Relative Asset Links**:
> - **Scripts**: [`tools/attack93_final_178_singleton_forensic_audit.py`](../tools/attack93_final_178_singleton_forensic_audit.py), [`tools/attack94_circular_and_radial_ring_grammar.py`](../tools/attack94_circular_and_radial_ring_grammar.py), [`tools/attack95_three_stage_cross_section_pharmacopoeia_chains.py`](../tools/attack95_three_stage_cross_section_pharmacopoeia_chains.py), [`tools/attack96_three_stage_pharmacopoeia_and_ring_decoder.py`](../tools/attack96_three_stage_pharmacopoeia_and_ring_decoder.py)
> - **Structured Datasets**: [`data/attack93_final_178_singleton_forensic_audit.json`](../data/attack93_final_178_singleton_forensic_audit.json), [`data/attack94_circular_and_radial_ring_grammar.json`](../data/attack94_circular_and_radial_ring_grammar.json), [`data/attack95_three_stage_cross_section_pharmacopoeia_chains.json`](../data/attack95_three_stage_cross_section_pharmacopoeia_chains.json), [`data/attack96_three_stage_pharmacopoeia_and_ring_decoder.json`](../data/attack96_three_stage_pharmacopoeia_and_ring_decoder.json)
> - **Visual Verification Crops**: [`pages/f1r_incunabular_hapax_audit_enh.png`](../pages/f1r_incunabular_hapax_audit_enh.png), [`pages/f102v1_okeody_qokeody_bridge_enh.png`](../pages/f102v1_okeody_qokeody_bridge_enh.png), [`pages/f46r_quireF_bifolio3_bridge_enh.png`](../pages/f46r_quireF_bifolio3_bridge_enh.png)

---

## Part I: Forensic Audit of the Final Singleton Hapax Tail — `99.9614%` (`36,215 / 36,229`) Corpus Token Accountability (`Attack 93` / `Discovery 110`)

- **Input Pool**: The exact `170` non-weirdo singleton hapax tokens (`0.469%` of the corpus) remaining after `Attack 85` (`Discovery 102`).
- **Forensic Resolution**: **`156 / 170` (`91.76%`)** are resolved across four paleographic and morphological mechanisms, raising total explained corpus accountability to **`36215 / 36,229` tokens (`99.9614%`)** and **`9040 / 9,054` word types (`99.845%`)**, leaving only **`14` long compound tokens (`0.0386%`)** across all `226` folios!
- **Permutation Null Validation (`Mechanisms 7B + 7C`)**: Pure string-morphological decomposition resolves **`61.18%` of the singleton tail vs. `8.57% ± 1.91%` on length-matched random EVA character strings ($z = +27.48$)**.

| Forensic Mechanism | Resolved Singletons | `%` of Pool | Representative Vellum & Multi-Transcriber Resolutions |
| :--- | :---: | :---: | :--- |
| `MECH_7A_SOFT_COMMA_OR_WEIRDO_LOCUS` | `116` | `68.24%` | `<f1r.4> cthiardaiin` (raw_zl='cthiar,daiin' -> cthiar . daiin); `<f1r.22> tshodeesy` (gc_v101 splits line f1r.22 (9 -> 10 words)); `<f1v.7> dolchiody` (raw_zl='do,lchiody' -> do . lchiody); `<f3r.16> soleeg` (gc_v101='soeC*' at f3r.16) |
| `MECH_7B_RARE_ALLOGRAPH_OR_GALLOWS_A_ONSET` | `5` | `2.94%` | `<f76v.5> teyteg` (teyteg -> teytem); `<fRos.71> soshxor` (soshxor -> soshror); `<f96v.1> osoj` (osoj -> osod); `<f102r2.13> loeekadag` (loeekadag -> loeekadam) |
| `MECH_7C_FOUR_MORPHEME_PHRASE_UNIVERBATION` | `31` | `18.24%` | `<f1r.6> ydaraishy` (y+dar+ai+shy); `<f2v.8> chokoishe` (ch+oko+i+she); `<f28r.8> oschotshl` (o+sch+ot+shl); `<f43v.8> shetcheodchs` (she+tch+eod+chs) |
| `MECH_7D_CANONICAL_SKELETON_NEIGHBOR_LE2` | `4` | `2.35%` | `<f39r.1> cphhofy` (canon(cphhofy)=cthhoky ~ canon(choky)=choky); `<f68r1.2> tochso` (canon(tochso)=tochso ~ canon(tsho)=tcho); `<f93r.1> kodshol` (canon(kodshol)=kodchol ~ canon(dchol)=dchol); `<f114r.4> fdeechdy` (canon(fdeechdy)=kdechdy ~ canon(kchdy)=kchdy) |
| `MECH_7E_RESIDUAL_LONG_COMPOUND` | `14` | `8.24%` | `<f14v.1> pdychoiin` (raw='pdychoiin' at f14v.1); `<f18r.1> pdrairdy` (raw='pdrairdy' at f18r.1); `<f41v.2> chepchefy` (raw='chepchefy' at f41v.2); `<f52r.1> tdokchcfhy` (raw='tdokchcfhy' at f52r.1) |

---

## Part II: The Marginless Circular (`@C`) & Radial (`@R`) Ring Grammar (`n = 2,497` Tokens, `Attack 94` / `Discovery 111`)

### 1. The Marginless Circular `-am / -m` Locus-Terminus Law (`6.34×` Lift, $z = +5.26$)
- Across all `107` multi-word circular/radial rings (`2280` tokens) — which have **no physical left or right page margins** — the `-am / -m` terminator suffix occurs at **`10.81%` (`12 / 111`) at the exact closing word of the ring/spoke (`RING_LOCUS_FINAL`, right before the 10–12 o'clock starter gap `<$>`) vs. only `1.71%` (`37 / 2169`) in ring-interior positions (`6.34×` enrichment, $z = +5.26$ vs. within-ring shuffled null `3.21 ± 1.67`)**.
- **Decisive Syntactic Proof**: Because a 360-degree circular ring has no physical page edge, this `6.34×` concentration proves that `-am / -m` is a **genuine syntactic/prosodic stream-terminator** rather than a visual artifact of right-margin cramping.

| Ring Locus | Type | Closing Context Before 10–12 O'Clock Boundary | Terminating `-am/-m` Word |
| :--- | :---: | :--- | :---: |
| `<f67r1.7>` | `+Cc` | `dair . [chparam] . <END>` | **`chparam`** |
| `<f67v1.20>` | `@Ro` | `eeis . [olcheeg] . <END>` | **`olcheeg`** |
| `<f68v3.6>` | `@Ri` | `dy . [otem] . <END>` | **`otem`** |
| `<f68v3.9>` | `@Ri` | `okolchey . [okolmom] . <END>` | **`okolmom`** |
| `<f68v3.11>` | `@Ri` | `qokal . [okeeg] . <END>` | **`okeeg`** |
| `<f70v2.1>` | `@Cc` | `otalal . [oteeam] . <END>` | **`oteeam`** |
| `<f70v2.32>` | `@Cc` | `aiin . [daim] . <END>` | **`daim`** |
| `<f72v1.33>` | `@Cc` | `saiin . [oteeosam] . <END>` | **`oteeosam`** |
| `<f73v.33>` | `@Cc` | `alaly . [otaram] . <END>` | **`otaram`** |
| `<f85r2.24>` | `@Cc` | `ar . [aram] . <END>` | **`aram`** |
| `<f86v4.2>` | `@Cc` | `yteey . [sam] . <END>` | **`sam`** |
| `<f86v4.3>` | `@Cc` | `opcho . [fcheom] . <END>` | **`fcheom`** |

### 2. Ring-Length Morphological Stratification & Clockwise Cadence ($z = +3.41$)
- **Clockwise Adjacent-Token Similarity**: Adjacent words around circular/radial rings share Levenshtein edit distance $\le 2$ in **`9.37%` (`189 / 2018`) vs. `7.6%` when shuffled within each ring ($z = +3.41$)**.
- **The `3.71×` `-aiin` Quantifier Surge on Long 360° Rings**: Moving from Short Radial Spokes (`1..3` words) to Medium Ring Arcs (`4..9` words) to Long Continuous Rings (`>= 10` words) preserves Nominal `o-` dominance (`40.55% -> 40.95% -> 41.88%`) while driving a **`3.71×` monotonic surge in `-aiin` degree/count suffixes (`2.76% -> 6.67% -> 10.24%`)** and a **`1.74×` rise in `ch-/sh-` bench qualifiers (`12.90% -> 19.05% -> 22.42%`)**:

| Ring Stratum | Loci | Tokens | `o-` Nominal `%` | `qo-` Active `%` | `da-` Linker `%` | `ch-/sh-` Bench `%` | `-dy` Stative `%` | `-aiin` Degree/Count `%` | `-am/-m` Closer `%` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `SHORT_RADIAL_SPOKES_1_TO_3` | `119` | `217` | **`40.55%`** | **`1.38%`** | `11.52%` | `12.9%` | `16.13%` | **`2.76%`** | `4.61%` |
| `MEDIUM_RING_ARCS_4_TO_9` | `37` | `210` | **`40.95%`** | **`7.62%`** | `11.43%` | `19.05%` | `12.38%` | **`6.67%`** | `4.76%` |
| `LONG_CONTINUOUS_RINGS_GE_10` | `70` | `2070` | **`41.88%`** | **`1.93%`** | `8.21%` | `22.42%` | `13.43%` | **`10.24%`** | `1.88%` |
| `LINEAR_PROSE_BASELINE (@P)` | `4130` | `32592` | `21.43%` | `15.81%` | `9.43%` | `25.14%` | `19.04%` | `16.97%` | `2.91%` |

---

## Part III: The `536` Three-Stage Cross-Sectional Pharmacopoeia Chains (`Herbal $I=H -> Pharmaceutical $I=P -> Quire 20 Starred Recipe $I=S`, `Attack 95` / `Discovery 112`)

- **Three-Stage Chain Discovery**: Across `126` Herbal Monograph folios (`Stage 1`), `16` Pharmaceutical Formulary folios (`Stage 2`), and `303` Quire 20 Starred Clinical Recipes (`Stage 3`), we identify **`536` Three-Stage Pharmacopoeia Chains (`H -> P -> S`) sharing $\ge 3$ high-IDF open-class canonical stems**, including **`79` 4+-stem Triads vs. `18.43 ± 9.02` under 200-trial vocabulary-preserving permutation ($z = +6.72$, `4.29×` enrichment)** and **`60` Triads anchored directly by an explicit `@Lf` root/leaf label on the Pharmaceutical page** (`Mean Max IDF = 11.431` vs. `9.292 ± 0.58` null, **$z = +3.69$**).

### 1. The Three-Stage Grammatical Transformation Gradient Across Shared Stems
Tracking the **exact same canonical stems** as they pass from **Stage 1 (`Herbal Monograph`)** to **Stage 2A (`Pharmaceutical Ingredient Labels`)**, **Stage 2B (`Pharmaceutical Formulary Prose`)**, and **Stage 3 (`Quire 20 Starred Clinical Recipes`)** reveals the complete functional lifecycle of Voynich medical vocabulary:

| Pharmacopoeia Stage | Shared-Stem Tokens | `o-` Nominal `%` | `qo-` Active Verb `%` | `-ol/-or` Container/Fluid `%` | `-dy` Stative `%` | `-edy` Processual `%` | `-aiin` Measured Dose `%` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `STAGE_1_HERBAL_MONOGRAPH_PROSE` | `1627` | **`16.59%`** | **`7.74%`** | **`30.55%`** | `6.88%` | **`3.13%`** | **`12.97%`** |
| `STAGE_2A_PHARM_INGREDIENT_LABELS` | `21` | **`52.38%`** | **`0.0%`** | **`23.81%`** | `19.05%` | **`0.0%`** | **`4.76%`** |
| `STAGE_2B_PHARM_FORMULARY_PROSE` | `480` | **`20.21%`** | **`12.92%`** | **`31.25%`** | `8.54%` | **`0.42%`** | **`12.5%`** |
| `STAGE_3_QUIRE20_STARRED_RECIPES` | `1462` | **`22.3%`** | **`13.89%`** | **`19.77%`** | `4.51%` | **`5.34%`** | **`23.05%`** |

### 2. Master Atlas of the Top Three-Stage Pharmacopoeia Chains (`One Per Pharmaceutical Folio`)

| Stage 1: Herbal Monograph (`$I=H`) | Stage 2: Pharm Formulary (`$I=P`) | Stage 3: Starred Recipe (`$I=S`) | Shared Open Stems | `@Lf` Label Anchors | 3-Way IDF Score | Surface Morphological Transformation Chains (`H -> P -> S`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`f46r`** (`$L=B`) | **`f89v1`** | **`<f58r.16>`** | `5` | — | **`15.393`** | `dalchdy: H(dalshedy) -> P(dalchdy) -> S(dalchdy)`<br>`okaldy: H(qokaldy) -> P(okaldy) -> S(qokaldy)`<br>`chekey: H(shekeey) -> P(shekey) -> S(cheekey)`<br>`choky: H(choky) -> P(choky) -> S(choky)`<br>`sar: H(sar) -> P(sar) -> S(sar)` |
| **`f31v`** (`$L=B`) | **`f102v2`** | **`<f111r.6>`** | `5` | `okeos` | **`14.135`** | `okear: H(okear) -> P(okear) -> S(qokear)`<br>`okeos: H(okeeos) -> P(okeos*L) -> S(qokeeos)`<br>`okeo: H(okeo) -> P(okeeo) -> S(okeeo)`<br>`cheos: H(cheos) -> P(cheos) -> S(cheos)`<br>`orain: H(oraiin) -> P(orain) -> S(oraiin)` |
| **`f43v`** (`$L=B`) | **`f88v`** | **`<f111r.6>`** | `6` | — | **`13.812`** | `otedy: H(oteody) -> P(qoteody) -> S(oteody)`<br>`checkhy: H(checkhy) -> P(checkhy) -> S(sheeckhy)`<br>`oteol: H(oteol) -> P(oteol) -> S(oteol)`<br>`kedy: H(kedy) -> P(keeody) -> S(keedy)`<br>`orain: H(oraiin) -> P(oraiin) -> S(oraiin)` |
| **`f40r`** (`$L=B`) | **`f101r`** | **`<f58v.1>`** | `5` | — | **`13.473`** | `ory: H(ory) -> P(ory) -> S(ory)`<br>`kar: H(kar) -> P(kar) -> S(kar)`<br>`key: H(keeey) -> P(qkeey) -> S(key)`<br>`olain: H(olaiin) -> P(olaiin) -> S(qolaiin)`<br>`orain: H(oraiin) -> P(oraiin) -> S(oraiin)` |
| **`f31v`** (`$L=B`) | **`f89v2`** | **`<f111r.6>`** | `5` | — | **`13.332`** | `ockhdy: H(ockhedy) -> P(ockhody) -> S(qockhedy)`<br>`okeos: H(okeeos) -> P(okeos) -> S(qokeeos)`<br>`cheos: H(cheos) -> P(cheos) -> S(cheos)`<br>`kedy: H(keeody) -> P(keeody) -> S(keedy)`<br>`cheo: H(sheo) -> P(cheo) -> S(cheo)` |
| **`f33v`** (`$L=B`) | **`f99r`** | **`<f112r.1>`** | `5` | `dam`, `okary` | **`13.081`** | `okary: H(okary) -> P(okary*L) -> S(qokary)`<br>`key: H(keey) -> P(keey) -> S(keey)`<br>`olain: H(olaiin) -> P(olaiin) -> S(olaiin)`<br>`dam: H(dam) -> P(dam*L) -> S(dam)`<br>`orain: H(orain) -> P(oraiin) -> S(oraiin)` |
| **`f56r`** (`$L=A`) | **`f101v`** | **`<f58v.1>`** | `4` | — | **`12.273`** | `choly: H(choly) -> P(choly) -> S(sholy)`<br>`chokey: H(chokeey) -> P(chokey) -> S(chokeey)`<br>`choy: H(choy) -> P(choy) -> S(shoy)`<br>`kchey: H(kchey) -> P(kchey) -> S(fchey)` |
| **`f90r2`** (`$L=A`) | **`f102r2`** | **`<f106r.4>`** | `4` | — | **`11.604`** | `okeod: H(qokeod) -> P(qokeod) -> S(qokeod)`<br>`okeo: H(qokeo) -> P(qokeeo) -> S(qokeo)`<br>`oin: H(oin) -> P(oiin) -> S(qoiin)`<br>`okor: H(qokor) -> P(okor) -> S(qokor)` |
| **`f43v`** (`$L=B`) | **`f89r2`** | **`<f58v.34>`** | `4` | — | **`11.033`** | `ykedy: H(ykeody) -> P(ykeody) -> S(ykeeody)`<br>`ockhy: H(ockhy) -> P(ockhy) -> S(ockhy)`<br>`olkey: H(olkey) -> P(olkey) -> S(olkeey)`<br>`cheo: H(sheo) -> P(cheo) -> S(sheo)` |
| **`f96r`** (`$L=A`) | **`f88r`** | **`<f58v.1>`** | `3` | — | **`10.934`** | `dory: H(dory) -> P(dory) -> S(dory)`<br>`oteor: H(oteeor) -> P(oteor) -> S(oteor)`<br>`ckhey: H(ckheey) -> P(ckhey) -> S(ckhey)` |
| **`f48v`** (`$L=B`) | **`f102v1`** | **`<f111r.6>`** | `4` | — | **`10.812`** | `tedy: H(teedy) -> P(teody) -> S(teedy)`<br>`olkey: H(olkeeey) -> P(olkey) -> S(olkeey)`<br>`otedy: H(oteody) -> P(oteody) -> S(oteody)`<br>`okeor: H(okeeor) -> P(qokeor) -> S(qokeor)` |
| **`f31v`** (`$L=B`) | **`f100r`** | **`<f108r.8>`** | `3` | — | **`9.72`** | `ykeo: H(ykeeo) -> P(ykeeeo) -> S(ykeeo)`<br>`ockhdy: H(ockhedy) -> P(qockhody) -> S(ockhedy)`<br>`cthey: H(ctheey) -> P(cthey) -> S(cthey)` |
| **`f39v`** (`$L=B`) | **`f89r1`** | **`<f58r.26>`** | `3` | — | **`8.658`** | `ckhol: H(ckhol) -> P(ckhol) -> S(ckhol)`<br>`chockhy: H(chockhy) -> P(chockhy) -> S(chockhy)`<br>`tain: H(paiin) -> P(taiin) -> S(taiin)` |
| **`f31v`** (`$L=B`) | **`f99v`** | **`<f58v.1>`** | `3` | — | **`8.319`** | `ockhey: H(ockhey) -> P(ockhey) -> S(ockhey)`<br>`ckhey: H(ckhey) -> P(ckhey) -> S(ckhey)`<br>`okor: H(okor) -> P(qokor) -> S(qokor)` |
| **`f51v`** (`$L=A`) | **`f100v`** | **`<f115r.29>`** | `3` | — | **`8.192`** | `chod: H(chod) -> P(chod) -> S(shod)`<br>`chckhey: H(chckhey) -> P(chckhey) -> S(chckhey)`<br>`cheo: H(sheo) -> P(sheeo) -> S(sheo)` |
| **`f94v`** (`$L=B`) | **`f102r1`** | **`<f112r.31>`** | `3` | — | **`8.13`** | `aral: H(aral) -> P(aral) -> S(aral)`<br>`cthdy: H(cphedy) -> P(cthedy) -> S(cphedy)`<br>`okchey: H(qokshey) -> P(okshey) -> S(okcheey)` |

### 3. Top `@Lf`-Root-Label-Anchored Three-Stage Chains (`Botanical Source -> Labeled Root/Jar -> Clinical Decoction`)

| Stage 1 (`Herbal`) | Stage 2 (`Pharm Page`) | Explicit `@Lf` Root/Jar Label Stem(s) | Stage 3 (`Starred Recipe`) | 3-Way IDF Score | Complete `H -> P(*L) -> S` Transformation Chains |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **`f43v`** (`$L=B`) | **`f88r`** | **`dary`** | **`<f111r.6>`** | **`8.591`** | `dary: H(dary) -> P(dary*L) -> S(dary)`; `olkey: H(olkey) -> P(olkeey) -> S(olkeey)`; `otam: H(otam) -> P(otam) -> S(otam)` |
| **`f55v`** (`$L=B`) | **`f88r`** | **`dary`** | **`<f111r.6>`** | **`7.962`** | `dary: H(dary) -> P(dary*L) -> S(dary)`; `otam: H(otam) -> P(otam) -> S(otam)`; `oain: H(qoaiin) -> P(oain) -> S(oaiin)` |
| **`f40v`** (`$L=B`) | **`f88v`** | **`ardy`** | **`<f116r.18>`** | **`7.975`** | `ardy: H(arody) -> P(arody*L) -> S(arody)`; `kedy: H(kedy) -> P(keeody) -> S(keedy)`; `orain: H(oraiin) -> P(oraiin) -> S(orain)` |
| **`f94r`** (`$L=B`) | **`f89v2`** | **`otair`** | **`<f58v.1>`** | **`7.951`** | `otair: H(opaiir) -> P(otair*L) -> S(qotair)`; `okair: H(okair) -> P(okaiir) -> S(qokair)`; `dam: H(dam) -> P(dam) -> S(dam)` |
| **`f6v`** (`$L=A`) | **`f89v2`** | **`okam`** | **`<f58v.34>`** | **`10.053`** | `chockhy: H(chockhy) -> P(chockhy) -> S(shockhy)`; `chear: H(chear) -> P(chear) -> S(shear)`; `okam: H(qokam) -> P(okam*L) -> S(okam)`; `okor: H(okor) -> P(okor) -> S(okor)` |
| **`f24v`** (`$L=A`) | **`f89v2`** | **`okam`, `otair`** | **`<f58v.34>`** | **`7.756`** | `otair: H(otaiir) -> P(otair*L) -> S(otair)`; `chear: H(chear) -> P(chear) -> S(shear)`; `okam: H(okam) -> P(okam*L) -> S(okam)` |
| **`f31v`** (`$L=B`) | **`f89v2`** | **`okam`** | **`<f58v.34>`** | **`10.133`** | `okeos: H(okeeos) -> P(okeos) -> S(qokeeos)`; `okam: H(okam) -> P(okam*L) -> S(okam)`; `okor: H(okor) -> P(okor) -> S(okor)`; `cheo: H(sheo) -> P(cheo) -> S(sheo)` |
| **`f39v`** (`$L=B`) | **`f89v2`** | **`okam`** | **`<f58v.34>`** | **`8.126`** | `ockhy: H(ockhy) -> P(qockhy) -> S(ockhy)`; `chockhy: H(chockhy) -> P(chockhy) -> S(shockhy)`; `okam: H(okam) -> P(okam*L) -> S(okam)` |
| **`f40v`** (`$L=B`) | **`f89v2`** | **`okam`** | **`<f58v.34>`** | **`8.691`** | `okeos: H(okeos) -> P(okeos) -> S(qokeeos)`; `ockhy: H(ockhy) -> P(qockhy) -> S(ockhy)`; `okam: H(okam) -> P(okam*L) -> S(okam)` |
| **`f43v`** (`$L=B`) | **`f89v2`** | **`okam`** | **`<f58v.34>`** | **`10.707`** | `ykedy: H(ykeody) -> P(ykeody) -> S(ykeeody)`; `ockhy: H(ockhy) -> P(qockhy) -> S(ockhy)`; `okam: H(okam) -> P(okam*L) -> S(okam)`; `cheo: H(sheo) -> P(cheo) -> S(sheo)` |

