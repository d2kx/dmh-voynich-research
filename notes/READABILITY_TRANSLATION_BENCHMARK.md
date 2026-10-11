# Voynich Manuscript Functional Clause-Translation Benchmark (`Phase 31 / Attack 20`)

## 1. Quantitative Proof of Verb–Argument Selectional Preference Within Clauses
- **Total Syntactic Clauses Segmented Across Manuscript**: `7,179` clauses (bounded by `<%>`/`<$>`, physical margins, `<->` Virtual Margins from `Attack 17`, and `-am/-m`/`q-/y-` clause transitions).
- **Clauses Containing Both a Verbal Operator Radical (`ch/sh/che/she/cth/ckh/ke/te/...`) and a Nominal Argument Radical (`ol/al/ar/or/dar/dal/kol/tol/...`)**: `4,990` clauses.
- **Observed Verb–Argument Selectional Mutual Information $I(R_{\text{verb}} ; R_{\text{nom}})$**: **`0.0885 bits` vs. `0.0557 bits` shuffled baseline ($z = +9.48$)**.

### Top Verb–Argument Selectional Pairings

| Verbal Operator (`R_verb`) | Procedural Role | Nominal Argument (`R_nom`) | Object/Substance Domain | Observed Clauses | Expected | Enrichment |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **`tch`** | `compound/treat` | **`dy`** | `completed-state(dy)` | `19` | `9.3` | **`2.04×`** |
| **`che`** | `infuse` | **`ain`** | `unit-measure(ain)` | `20` | `11.1` | **`1.81×`** |
| **`cth`** | `press/extract(leaf)` | **`d`** | `base/hub(d)` | `54` | `33.7` | **`1.6×`** |
| **`lk`** | `decant-liquid` | **`k`** | `vessel/body(k)` | `36` | `23.6` | **`1.52×`** |
| **`ckh`** | `bathe/wash(blue-herb)` | **`s`** | `seed/part(s)` | `18` | `12.0` | **`1.5×`** |
| **`te`** | `draw/channel` | **`d`** | `base/hub(d)` | `42` | `28.9` | **`1.45×`** |
| **`tch`** | `compound/treat` | **`t`** | `conduit/tube(t)` | `132` | `96.5` | **`1.37×`** |
| **`lch`** | `blend-in-liquid` | **`k`** | `vessel/body(k)` | `28` | `20.4` | **`1.37×`** |
| **`ch`** | `mix/prepare` | **`ko`** | `star-node(ko)` | `16` | `11.8` | **`1.36×`** |

---

## 2. Clause-by-Clause Readable Structural Translations of 8 Flagship Folios & Treatises

### 1. Herbal `f11v` (`Language A, Hand 1` — Red-and-Green Checkered Crown Tree: `cthe` & `<->` Virtual Margin Showcase)

- **`<f11v.1>`** `¶ poldchody . shcphy . shordy . qoty [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ ¶ [RECIPE-HEADER] leafy-shoot(tol)+[dch]-treated ; heat/steep+press/extract(leaf) ; heat/steep+jar-herb(or) ; and the conduit/tube(t) [VIRTUAL-RIGHT-MARGIN] <->
- **`<f11v.1>`** `<-> [VIRTUAL-LEFT-MARGIN] shol . cphar . dany`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] heat/steep [in-fluid] ; press/extract(leaf) [of-root] ; base/hub(d)+[an]
- **`<f11v.2>`** `shol . dy . chckhy . shcthy . daiin . dam [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ heat/steep [in-fluid] ; completed-state(dy)-treated ; mix/prepare+bathe/wash(blue-herb) ; heat/steep+press/extract(leaf) ; base/hub(d) [1-unit] ; base/hub(d) (to completion!) [VIRTUAL-RIGHT-MARGIN] <->
- **`<f11v.2>`** `<-> [VIRTUAL-LEFT-MARGIN] ykchy . dain . dchy`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] then distill/align(star) ; base/hub(d) [1-unit] ; [dch]
- **`<f11v.3>`** `otchor . dy . kchy . tchy . ar . qokchd [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ the PHARMA-HERB:otchor[f100v.3] [from-source] ; completed-state(dy)-treated ; distill/align(star) ; compound/treat ; root-shoot(ar) [of-root] ; and the distill/align(star) [VIRTUAL-RIGHT-MARGIN] <->
- **`<f11v.3>`** `<-> [VIRTUAL-LEFT-MARGIN] oky . choldydy`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] the vessel/body(k) ; [chol]+completed-state(dy)-treated
- **`<f11v.4>`** `qokchor . cholol . chyky . dchy . qoky [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ and the distill/align(star) [from-source] ; mix/prepare+fluid/stream(ol) [in-fluid] ; mix/prepare+[yk] ; [dch] ; and the vessel/body(k) [VIRTUAL-RIGHT-MARGIN] <->
- **`<f11v.4>`** `<-> [VIRTUAL-LEFT-MARGIN] ctho . tchey . tu`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] [ctho] ; compound/treat ; conduit/tube(t)+[u]
- **`<f11v.5>`** `dd`
  - $\Rightarrow$ base/hub(d)
- **`<f11v.6>`** `soydy . qoteey . qot . chor . dy . ddy [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ sap-resin(so)+[y]-treated ; and the conduit/tube(t) ; and the [ot] ; mix/prepare [from-source] ; completed-state(dy)-treated ; base/hub(d)-treated [VIRTUAL-RIGHT-MARGIN] <->
- **`<f11v.6>`** `<-> [VIRTUAL-LEFT-MARGIN] cthor . shyarg`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] press/extract(leaf) [from-source] ; [shy]+root-shoot(ar)+stoppered-jar(g)
- **`<f11v.7>`** `ycheor . ksho . dor . cthey . schold ∎`
  - $\Rightarrow$ thus infuse [from-source] ; vessel/body(k)+[sho] ; base/hub(d) [from-source] ; press/extract(leaf) ; seed/part(s)+[chol] ∎

### 2. Herbal `f16v` (`Language A, Hand 1` — Bright Blue 8-Pointed Blossom: `ckh/ky` Showcase)

- **`<f16v.1>`** `¶ pchroiin . otchor . chpchol . chpchey . spchoy`
  - $\Rightarrow$ ¶ [RECIPE-HEADER] compound/treat+[ro] ; the PHARMA-HERB:otchor[f100v.3] [from-source] ; mix/prepare+compound/treat [in-fluid] ; mix/prepare+compound/treat ; seed/part(s)+[tcho]
- **`<f16v.2>`** `ytchor . y . kychokchy . qokchocthor . shory`
  - $\Rightarrow$ thus compound/treat [from-source] ; [y] ; blue-petal-extract(ky)+[chok]+mix/prepare ; and the [kcho]+press/extract(leaf) [from-source] ; heat/steep
- **`<f16v.3>`** `ykchy . dy . choy . qoty . chykchy . koshet`
  - $\Rightarrow$ thus distill/align(star) ; completed-state(dy)-treated ; [cho] ; and the conduit/tube(t) ; [chy]+distill/align(star) ; star-node(ko)+[shet]
- **`<f16v.4>`** `dchol . chcthody . cphod . chotol . dal`
  - $\Rightarrow$ [dch] [in-fluid] ; mix/prepare+press/extract(leaf) ; [ctho] ; [cho]+conduit/tube(t) [in-fluid] ; base/hub(d) [to-measure]
- **`<f16v.5>`** `ytchy . chyty . chor . chol . ytchy . dan`
  - $\Rightarrow$ thus compound/treat ; mix/prepare+[yt] ; mix/prepare [from-source] ; mix/prepare [in-fluid] ; thus compound/treat ; base/hub(d)+[an]
- **`<f16v.6>`** `sor . chkar . oty . chkar . chol . dairin ∎`
  - $\Rightarrow$ seed/part(s) [from-source] ; [chk] [of-root] ; the conduit/tube(t) ; [chk] [of-root] ; mix/prepare [in-fluid] ; base/hub(d)+aether/degree(air) ∎
- **`<f16v.7>`** `¶ pchocthy . chypchy . qotchy . chy . sy`
  - $\Rightarrow$ ¶ [RECIPE-HEADER] [tcho]+press/extract(leaf) ; [chy]+compound/treat ; and the compound/treat ; mix/prepare ; seed/part(s)
- **`<f16v.8>`** `daiin . chol . y . daiin . chcthy . qotchar . chor . sholo`
  - $\Rightarrow$ base/hub(d) [1-unit] ; mix/prepare [in-fluid] ; [y] ; base/hub(d) [1-unit] ; mix/prepare+press/extract(leaf) ; and the PHARMA-HERB:otchar[f89v1.3] [of-root] ; mix/prepare [from-source] ; heat/steep+[olo]
- **`<f16v.9>`** `dshy . okaiin . okaiin . chol . chor . cthor . ty . chody`
  - $\Rightarrow$ [dsh] ; the vessel/body(k) [1-unit] ; the vessel/body(k) [1-unit] ; mix/prepare [in-fluid] ; mix/prepare [from-source] ; press/extract(leaf) [from-source] ; conduit/tube(t) ; mix/prepare
- **`<f16v.10>`** `qokchy . chydy . ykchy . chckhy . otain . cthor . cth:y`
  - $\Rightarrow$ and the distill/align(star) ; [chy]-treated ; thus distill/align(star) ; mix/prepare+bathe/wash(blue-herb) ; the conduit/tube(t) [1-unit] ; press/extract(leaf) [from-source] ; press/extract(leaf)+[:]
- **`<f16v.11>`** `okytaiin . chkchy . saiin`
  - $\Rightarrow$ the vessel/body(k)+[yt] [1-unit] ; mix/prepare+distill/align(star) ; seed/part(s) [1-unit]
- **`<f16v.12>`** `daiin . yky . otor . chody`
  - $\Rightarrow$ base/hub(d) [1-unit] ; thus vessel/body(k) ; the conduit/tube(t) [from-source] ; mix/prepare
- **`<f16v.13>`** `sokar . oaorar ∎`
  - $\Rightarrow$ sap-resin(so)+vessel/body(k) [of-root] ; the [a]+jar-herb(or) [of-root] ∎

### 3. Herbal `f48v` (`Language A, Hand 1` — Twin Dark Seed-Pods Citing Rosettes `<fRos.45> otchdy . otoldy`)

- **`<f48v.7>`** `¶ pchedar . chey [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ ¶ [RECIPE-HEADER] conduit/tube(t)+[ched] [of-root] ; mix/prepare [VIRTUAL-RIGHT-MARGIN] <->
- **`<f48v.7>`** `<-> [VIRTUAL-LEFT-MARGIN] ypchedy . otedy . shefeeedy . al [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] then compound/treat ; the ROSETTE/ZOD:otedy[fRos.72/Scorpio]-treated ; decoct/boil+vessel/body(k) ; substance/degree(al) [to-measure] [VIRTUAL-RIGHT-MARGIN] <->
- **`<f48v.7>`** `<-> [VIRTUAL-LEFT-MARGIN] shedy . otedy . fcheodal . cpheeg`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] heat/steep ; the ROSETTE/ZOD:otedy[fRos.72/Scorpio]-treated ; distill/align(star)+[eod] [to-measure] ; press/extract(leaf)+[eg]
- **`<f48v.8>`** `oteody . chkey [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ the draw/channel ; [chk] [VIRTUAL-RIGHT-MARGIN] <->
- **`<f48v.8>`** `<-> [VIRTUAL-LEFT-MARGIN] okedy . chckhedy . ykedy . oldy [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] the vessel/body(k)-treated ; mix/prepare+bathe/wash(blue-herb) ; then vessel/body(k)-treated ; the fluid/stream(ol)-treated [VIRTUAL-RIGHT-MARGIN] <->
- **`<f48v.8>`** `<-> [VIRTUAL-LEFT-MARGIN] otoly . chey . kaly . tokar . otam`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] the conduit/tube(t) ; mix/prepare ; vessel/body(k) ; ray/spoke(to)+vessel/body(k) [of-root] ; the PLANT/DEG:otar[f88v.4/Pisces] (to completion!)
- **`<f48v.9>`** `tor . shody . okal [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ conduit/tube(t) [from-source] ; heat/steep ; the vessel/body(k) [to-measure] [VIRTUAL-RIGHT-MARGIN] <->
- **`<f48v.9>`** `<-> [VIRTUAL-LEFT-MARGIN] otchedy . cheky . oly . loldy . lol [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] the compound/treat ; infuse+vessel/body(k) ; the fluid/stream(ol)+[y] ; liquid(l)+fluid/stream(ol)-treated ; liquid(l) [in-fluid] [VIRTUAL-RIGHT-MARGIN] <->
- **`<f48v.9>`** `<-> [VIRTUAL-LEFT-MARGIN] otchdy . otoldy . ytam`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] **[2-WORD ROSETTES CRIB: `otchdy . otoldy` (fRos.45)]** the ROSETTE/STAR:otchdy[fRos.45/f67v2] ; the ROSETTE-HUB:otoldy[fRos.45]-treated ; then conduit/tube(t) (to completion!)
- **`<f48v.9>`** `otedy`
  - $\Rightarrow$ the ROSETTE/ZOD:otedy[fRos.72/Scorpio]-treated
- **`<f48v.10>`** `tol . chedy . ytedy [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ conduit/tube(t) [in-fluid] ; mix/prepare ; thus conduit/tube(t)-treated [VIRTUAL-RIGHT-MARGIN] <->
- **`<f48v.10>`** `<-> [VIRTUAL-LEFT-MARGIN] ykeol . chdy . chdor . chtol . chdy [VIRTUAL-RIGHT-MARGIN] <->`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] then cook/simmer [in-fluid] ; mix/prepare ; [chd] [from-source] ; [cht] [in-fluid] ; mix/prepare [VIRTUAL-RIGHT-MARGIN] <->
- **`<f48v.10>`** `<-> [VIRTUAL-LEFT-MARGIN] ytchedal . cthey . okarar . ary`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] then conduit/tube(t)+[ched] [to-measure] ; press/extract(leaf) ; the vessel/body(k)+root-shoot(ar) [of-root] ; root-shoot(ar)+[y]
- **`<f48v.11>`** `ykeedal . chckhy [VIRTUAL-RIGHT-MARGIN] <-> ∎`
  - $\Rightarrow$ thus cook/simmer+base/hub(d) [to-measure] ; mix/prepare+bathe/wash(blue-herb) [VIRTUAL-RIGHT-MARGIN] <-> ∎
- **`<f48v.11>`** `<-> [VIRTUAL-LEFT-MARGIN] ykal . ytam`
  - $\Rightarrow$ <-> [VIRTUAL-LEFT-MARGIN] then vessel/body(k) [to-measure] ; then conduit/tube(t) (to completion!)
- **`<f48v.11>`** `or . cheedls . sary ∎`
  - $\Rightarrow$ the jar-herb(or) [from-source] ; [ched]+liquid(l) ; seed/part(s) ∎

### 4. Biological `f84r` (`Language B, Hand 2` — Overhead Conduits `t`, Bathing Nymphs `k`, Basins `sh/d` & `<fRos> daraldy . otedaiin`)

- **`<f84r.1>`** `ololal`
  - $\Rightarrow$ the fluid/stream(ol)+fluid/stream(ol) [to-measure]
- **`<f84r.2>`** `or . shekar`
  - $\Rightarrow$ the jar-herb(or) [from-source] ; decoct/boil+vessel/body(k) [of-root]
- **`<f84r.3>`** `ydy`
  - $\Rightarrow$ thus [y]-treated
- **`<f84r.4>`** `okedy`
  - $\Rightarrow$ the vessel/body(k)-treated
- **`<f84r.5>`** `loly`
  - $\Rightarrow$ liquid(l)
- **`<f84r.6>`** `doiir`
  - $\Rightarrow$ [doi]
- **`<f84r.32>`** `qotar . ytedy . tedy . dar . olkedy`
  - $\Rightarrow$ and the PLANT/DEG:otar[f88v.4/Pisces] [of-root] ; thus conduit/tube(t)-treated ; conduit/tube(t)-treated ; base/hub(d) [of-root] ; the [olk]-treated
- **`<f84r.32>`** `qotedy . shckhy . chtol . tedy . dar . oroly`
  - $\Rightarrow$ and the ROSETTE/ZOD:otedy[fRos.72/Scorpio]-treated ; heat/steep+bathe/wash(blue-herb) ; [cht] [in-fluid] ; conduit/tube(t)-treated ; base/hub(d) [of-root] ; the jar-herb(or)
- **`<f84r.33>`** `shol . tchdytedy . ykain . shey . cheolytedy . olkedy . okedar . olkeedolary`
  - $\Rightarrow$ heat/steep [in-fluid] ; [tchd]+[yt]-treated ; thus vessel/body(k) [1-unit] ; heat/steep ; infuse+[oly]+conduit/tube(t) ; the [olk]-treated ; the cook/simmer+base/hub(d) [of-root] ; the fluid/stream(ol)+[ked]+fluid/stream(ol)
- **`<f84r.34>`** `dsheyteey . sor . ol . shedy . daraldy . otedaiin . shckhchy . chckhy . daiinaryly`
  - $\Rightarrow$ base/hub(d)+decoct/boil+[yt] ; seed/part(s) [from-source] ; the fluid/stream(ol) [in-fluid] ; heat/steep ; ROSETTE-HAPAX:daraldy[fRos]-treated ; the ROSETTE:otedain[fRos.72/103] [1-unit] ; heat/steep+bathe/wash(blue-herb)+mix/prepare ; mix/prepare+bathe/wash(blue-herb) ; [dain]+root-shoot(ar)+[y]
- **`<f84r.35>`** `qokal . daiin . dain . otey . cheor . air . shckhy . orairoro ∎`
  - $\Rightarrow$ and the vessel/body(k) [to-measure] ; base/hub(d) [1-unit] ; base/hub(d) [1-unit] ; the conduit/tube(t) ; infuse [from-source] ; [ai] ; heat/steep+bathe/wash(blue-herb) ; the jar-herb(or)+aether/degree(air)+jar-herb(or)+core-entity(o) ∎

### 5. Starred Recipe `f105r:P1–P2` (`Language B, Hand 3` — Same-Star `★L. -> ★L.` Chained Recipes for `<f88v.4> otar . arody`)

- **`<f105r.1>`** `[★L.] ¶ aiindar . chcphy . qokeey . qopaiin`
  - $\Rightarrow$ [★L.] ¶ unit-measure(ain)+base/hub(d) [of-root] ; mix/prepare+press/extract(leaf) ; and the vessel/body(k) ; and the conduit/tube(t) [1-unit]
- **`<f105r.1>`** `ypcheeey . saraisl . aiin . cheedy . aiin . arody`
  - $\Rightarrow$ thus compound/treat ; [sar]+[ai]+seed/part(s) ; unit-measure(ain) [1-unit] ; mix/prepare ; unit-measure(ain) [1-unit] ; ROOT:arody[f88v.4]-treated
- **`<f105r.2>`** `dshees . yey . cheey . raiin . otchdy`
  - $\Rightarrow$ base/hub(d)+decoct/boil ; thus [ey] ; mix/prepare ; portion(r) [1-unit] ; the ROSETTE/STAR:otchdy[fRos.45/f67v2]
- **`<f105r.2>`** `qodor . ches . or . cheey . okees . odar . cheodyqody`
  - $\Rightarrow$ and the base/hub(d) [from-source] ; infuse ; the jar-herb(or) [from-source] ; mix/prepare ; the cook/simmer ; the base/hub(d) [of-root] ; [cheo]+completed-state(dy)+[q]-treated
- **`<f105r.3>`** `olshey . qoden . odeey . kcheody . cheeo . ar . yteey`
  - $\Rightarrow$ the fluid/stream(ol)+heat/steep ; and the [de]+[n] ; the base/hub(d) ; vessel/body(k)+infuse ; [cheo] ; root-shoot(ar) [of-root] ; thus conduit/tube(t)
- **`<f105r.3>`** `ytchy . otedy . qokeedy . qokeey . rol`
  - $\Rightarrow$ thus compound/treat ; the ROSETTE/ZOD:otedy[fRos.72/Scorpio]-treated ; and the vessel/body(k)-treated ; and the vessel/body(k) ; portion(r) [in-fluid]
- **`<f105r.4>`** `ykaiin . olkeedy . odaiin . okar . eeeodaiin`
  - $\Rightarrow$ thus vessel/body(k) [1-unit] ; the [olk]-treated ; the base/hub(d) [1-unit] ; the vessel/body(k) [of-root] ; [eod] [1-unit]
- **`<f105r.4>`** `yteey . ochedy . qokeeey . oy . teedy . qotam`
  - $\Rightarrow$ thus conduit/tube(t) ; the mix/prepare ; and the vessel/body(k) ; the core-entity(o) ; conduit/tube(t)-treated ; and the PLANT/DEG:otar[f88v.4/Pisces] (to completion!)
- **`<f105r.5>`** `daiin . yteedy . yteeeody . yl . cheod . or . aiiroekey . otchdy . otey ∎`
  - $\Rightarrow$ base/hub(d) [1-unit] ; thus conduit/tube(t)-treated ; thus draw/channel ; [y] ; [cheo] ; the jar-herb(or) [from-source] ; aether/degree(air)+[oe]+vessel/body(k) ; the ROSETTE/STAR:otchdy[fRos.45/f67v2] ; the conduit/tube(t) ∎
- **`<f105r.6>`** `[★L.] ¶ par . arody . shedeeey . qopchedy`
  - $\Rightarrow$ [★L.] ¶ **[2-WORD BOTANICAL CRIB: `otar . arody` (f88v.4 Plant #4)]** [RECIPE-HEADER] conduit/tube(t) [of-root] ; ROOT:arody[f88v.4]-treated ; decoct/boil+base/hub(d) ; and the compound/treat
- **`<f105r.6>`** `qody . qoteody . aiin . yteody . qokor . olpshedy`
  - $\Rightarrow$ and the completed-state(dy)-treated ; and the draw/channel ; unit-measure(ain) [1-unit] ; thus draw/channel ; and the vessel/body(k) [from-source] ; the fluid/stream(ol)+[tsh]-treated
- **`<f105r.7>`** `ysheeody . ykeeos . or . aiiin . shey`
  - $\Rightarrow$ thus decoct/boil ; thus boil-pharma ; the jar-herb(or) [from-source] ; unit-measure(ain) ; heat/steep
- **`<f105r.7>`** `qodaiiin . qokeed . qokeey . saiin . aiirody`
  - $\Rightarrow$ and the base/hub(d) ; and the cook/simmer ; and the vessel/body(k) ; seed/part(s) [1-unit] ; aether/degree(air)-treated
- **`<f105r.8>`** `sheey . oleeey . orair . qokaiin . chey`
  - $\Rightarrow$ heat/steep ; the fluid/stream(ol) ; the jar-herb(or)+[ai] ; and the vessel/body(k) [1-unit] ; mix/prepare
- **`<f105r.8>`** `qokeedy . qokedy . oteedy . lchedy . oesal`
  - $\Rightarrow$ and the vessel/body(k)-treated ; and the vessel/body(k)-treated ; the ROSETTE/ZOD:otedy[fRos.72/Scorpio]-treated ; blend-in-liquid ; the [es] [to-measure]
- **`<f105r.9>`** `oeeolchy . okeeydy . okeey . okchey`
  - $\Rightarrow$ the [eol]+mix/prepare ; the vessel/body(k)+[ey]-treated ; the vessel/body(k) ; the distill/align(star)
- **`<f105r.10>`** `sairy . ore . daiindy . ytam ∎`
  - $\Rightarrow$ [sai] ; the jar-herb(or)+[e] ; base/hub(d)+unit-measure(ain)-treated ; thus conduit/tube(t) (to completion!) ∎

### 6. Starred Recipe `f114v:P1 & P10` (`Language B, Hand 3` — 5-Crib Recipe P1 & Clause-Final `tar . arody` Recipe P10)

- **`<f114v.1>`** `[★L] ¶ pchdol . dar . chedain . chodalr . fcheey . dchedy`
  - $\Rightarrow$ [★L] ¶ [RECIPE-HEADER] compound/treat+base/hub(d) [in-fluid] ; base/hub(d) [of-root] ; infuse+base/hub(d) [1-unit] ; [chod]+substance/degree(al) ; distill/align(star) ; [dch]-treated
- **`<f114v.1>`** `qocphdy . otdady . qotedar . daiin`
  - $\Rightarrow$ and the press/extract(leaf) ; the conduit/tube(t)+seed-pod(da)-treated ; and the draw/channel+base/hub(d) [of-root] ; base/hub(d) [1-unit]
- **`<f114v.2>`** `dshedal . qoteody . choddy . otol . chedal . otain . chedol . chedain . shedy . qotched . dl`
  - $\Rightarrow$ base/hub(d)+[shed] [to-measure] ; and the draw/channel ; [cho]+base/hub(d)-treated ; the conduit/tube(t) [in-fluid] ; infuse+base/hub(d) [to-measure] ; the conduit/tube(t) [1-unit] ; infuse+base/hub(d) [in-fluid] ; infuse+base/hub(d) [1-unit] ; heat/steep ; and the conduit/tube(t)+infuse ; base/hub(d)
- **`<f114v.3>`** `oeos . qotcheo . odain . qotain . otar . qotchd . dol . qotchedy . choty . ol . lchdaiin . dal`
  - $\Rightarrow$ the [eo] ; and the conduit/tube(t)+[cheo] ; the base/hub(d) [1-unit] ; and the conduit/tube(t) [1-unit] ; the PLANT/DEG:otar[f88v.4/Pisces] [of-root] ; and the compound/treat ; base/hub(d) [in-fluid] ; and the compound/treat ; [cho]+conduit/tube(t) ; the fluid/stream(ol) [in-fluid] ; blend-in-liquid+base/hub(d) [1-unit] ; base/hub(d) [to-measure]
- **`<f114v.4>`** `qokedy . cheocthedy . qoted . qotedol . chedar . qotedy . okeedy . daiin . chedaiin . oky`
  - $\Rightarrow$ and the vessel/body(k)-treated ; [cheo]+press/extract(leaf) ; and the draw/channel ; and the draw/channel+base/hub(d) [in-fluid] ; infuse+base/hub(d) [of-root] ; and the ROSETTE/ZOD:otedy[fRos.72/Scorpio]-treated ; the vessel/body(k)-treated ; base/hub(d) [1-unit] ; infuse+base/hub(d) [1-unit] ; the vessel/body(k)
- **`<f114v.5>`** `chedy . qokeedy . okaly . cheedain . shedy ∎`
  - $\Rightarrow$ mix/prepare ; and the vessel/body(k)-treated ; the vessel/body(k) ; infuse+base/hub(d) [1-unit] ; heat/steep ∎
- **`<f114v.36>`** `[★L.] ¶ tshey . oidal . op . shoko . otchey`
  - $\Rightarrow$ [★L.] ¶ [tsh] ; the [i]+base/hub(d) [to-measure] ; the [ot] ; [sho]+star-node(ko) ; the compound/treat
- **`<f114v.36>`** `qopchol . qopaiin . qotar . alkal . ram`
  - $\Rightarrow$ and the compound/treat [in-fluid] ; and the conduit/tube(t) [1-unit] ; and the PLANT/DEG:otar[f88v.4/Pisces] [of-root] ; substance/degree(al)+vessel/body(k) [to-measure] ; portion(r) (to completion!)
- **`<f114v.37>`** `dcheey . ol . cheodaiiin . qokar . otaiin . otal . okaiin . chey . tar . arody`
  - $\Rightarrow$ **[2-WORD BOTANICAL CRIB: `otar . arody` (f88v.4 Plant #4)]** [dch] ; the fluid/stream(ol) [in-fluid] ; [cheo]+base/hub(d) ; and the vessel/body(k) [of-root] ; the conduit/tube(t) [1-unit] ; the conduit/tube(t) [to-measure] ; the vessel/body(k) [1-unit] ; mix/prepare ; conduit/tube(t) [of-root] ; ROOT:arody[f88v.4]-treated
- **`<f114v.38>`** `oteey . okedaiin . otaiin . qotchey`
  - $\Rightarrow$ the conduit/tube(t) ; the cook/simmer+base/hub(d) [1-unit] ; the conduit/tube(t) [1-unit] ; and the compound/treat
- **`<f114v.38>`** `qoteeody . otaiin . okal . dals`
  - $\Rightarrow$ and the draw/channel ; the conduit/tube(t) [1-unit] ; the vessel/body(k) [to-measure] ; base/hub(d)+substance/degree(al)

### 7. Starred Recipe `f107r:P4` (`Language B, Hand 3` — The 5-Nymph Water-Trigon Astrological Recipe: `20°–22° Pisces + 19° Cancer + 17° Virgo`)

- **`<f107r.11>`** `cheeo . cheeol . qokaiin . ytain`
  - $\Rightarrow$ [cheo] ; infuse [in-fluid] ; and the vessel/body(k) [1-unit] ; thus conduit/tube(t) [1-unit]
- **`<f107r.11>`** `y . keeoll . oraiin . okaiin . okar . okaiin . otaram`
  - $\Rightarrow$ [y] ; cook/simmer+fluid/stream(ol) ; the jar-herb(or) [1-unit] ; the vessel/body(k) [1-unit] ; the vessel/body(k) [of-root] ; the vessel/body(k) [1-unit] ; the conduit/tube(t)+root-shoot(ar) (to completion!)
- **`<f107r.12>`** `ychol . chol . loraiir . aiinal ∎`
  - $\Rightarrow$ thus mix/prepare [in-fluid] ; mix/prepare [in-fluid] ; [lo]+[rai] ; unit-measure(ain) [to-measure] ∎
- **`<f107r.13>`** `[★L] ¶ polchlsaiin . sheky . qokaiin . opchal . shedy`
  - $\Rightarrow$ [★L] ¶ [RECIPE-HEADER] conduit/tube(t)+[olch]+[ls] [1-unit] ; decoct/boil+vessel/body(k) ; and the vessel/body(k) [1-unit] ; the compound/treat [to-measure] ; heat/steep
- **`<f107r.13>`** `pshedaiin . otodal . shedy . otaral`
  - $\Rightarrow$ conduit/tube(t)+[shed] [1-unit] ; the ray/spoke(to)+base/hub(d) [to-measure] ; heat/steep ; the ZODIAC:21°Pisces(otaral)[f70v2.23] [to-measure]
- **`<f107r.14>`** `cthedy . lshedy . cheolchear . oralam`
  - $\Rightarrow$ press/extract(leaf) ; [lsh]-treated ; [cheo]+[lche] [of-root] ; the jar-herb(or)+substance/degree(al) (to completion!)
- **`<f107r.14>`** `chtaiin . otarain . chey . qokaiin . otain`
  - $\Rightarrow$ [cht] [1-unit] ; the conduit/tube(t)+root-shoot(ar) [1-unit] ; mix/prepare ; and the vessel/body(k) [1-unit] ; the conduit/tube(t) [1-unit]
- **`<f107r.15>`** `ychol . oiin . chey . qockhal . al . otaraiin . sheky . okeeey . raiin . airal`
  - $\Rightarrow$ thus mix/prepare [in-fluid] ; the [in] ; mix/prepare ; and the bathe/wash(blue-herb) [to-measure] ; substance/degree(al) [to-measure] ; the conduit/tube(t)+root-shoot(ar) [1-unit] ; decoct/boil+vessel/body(k) ; the vessel/body(k) ; portion(r) [1-unit] ; ZODIAC:19°Cancer(airal)[f72r3.21] [to-measure]
- **`<f107r.16>`** `tolshoror . olkeedy . qotaiin . otalar . opcheol . qeeoy . shey . kair . otaiinam`
  - $\Rightarrow$ conduit/tube(t)+[olsh]+jar-herb(or) [from-source] ; the [olk]-treated ; and the conduit/tube(t) [1-unit] ; the ZODIAC:22°Pisces(otalar)[f70v2.24] [of-root] ; the conduit/tube(t)+infuse [in-fluid] ; and [eo] ; heat/steep ; [kai] ; the ZODIAC-HAPAX:17°Virgo(opaiinam)[f72v2.18] (to completion!)

### 8. Starred Recipe `f113r:P1` (`Language B, Hand 3` — Exact Partile Water-Trigon Trine: `12° Cancer ykolairol` + `12° Scorpio oteeosy`)

- **`<f113r.1>`** `[★L] ¶ pcheschy . ypcheedy . fchdy . chetar . qopchedaiin . oteey . oty . lkchy . chodain . alar . chedy`
  - $\Rightarrow$ [★L] ¶ [RECIPE-HEADER] [tche]+[sch] ; thus compound/treat ; distill/align(star) ; infuse+conduit/tube(t) [of-root] ; and the conduit/tube(t)+[ched] [1-unit] ; the conduit/tube(t) ; the conduit/tube(t) ; decant-liquid+mix/prepare ; [cho]+base/hub(d) [1-unit] ; substance/degree(al) [of-root] ; mix/prepare
- **`<f113r.2>`** `dar . okeedy . oteeody . qokedy . otchechy . okeorl . alkeeos . ched . al . ar . chy . ykolairol`
  - $\Rightarrow$ base/hub(d) [of-root] ; the vessel/body(k)-treated ; the draw/channel ; and the vessel/body(k)-treated ; the [tche]+mix/prepare ; the cook/simmer+jar-herb(or) ; substance/degree(al)+boil-pharma ; infuse ; substance/degree(al) [to-measure] ; root-shoot(ar) [of-root] ; mix/prepare ; thus ZODIAC-HAPAX:12°Cancer(ykolairol)[f72r3.13] [in-fluid]
- **`<f113r.3>`** `shchs . oal . chsaiin . oteeosy ∎`
  - $\Rightarrow$ [shch] ; the substance/degree(al) [to-measure] ; [chs] [1-unit] ; the contain/measure+seed/part(s) ∎
