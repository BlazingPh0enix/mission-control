# ReStock+

- CKAN id: `ReStockPlus`, version 1.5.1, by ReStock Team
- Kind: Parts. Changes rocket design: Yes
- Needs: Module Manager, ReStock
- Needed by: nothing else in this install
- Links: [Source](https://github.com/PorktoberRevolution/ReStocked), [Forum or homepage](https://forum.kerbalspaceprogram.com/index.php?/topic/182679-161-restock-revamping-ksps-art/)

ReStock+ adds about 120 new parts "that fill gaping holes in the stock lineup": a full 1.875 m
line (tanks, adapters, decouplers, engine plates, heat shield, Mk2 'Acorn' pod), a 5 m line
(Kerbodyne SIV tanks, decoupler, separator, nosecone, engine adapter), 0.625 m tanks and
engines, and new engines, SRBs, pods, RCS, batteries and structural parts.

## ReStock+: engines

| Engine | Internal name | Thrust, vacuum (kN) | Isp sea level / vacuum (s) | Mass (t) |
|---|---|---|---|---|
| UR-1 'Galleon' | `restock-engine-galleon-1` | 1,350 | 290 / 305 | 5.0 |
| TCK-2 'Castor' SRB | `restock-srb-castor-1` | 1,300 | 200 / 225 | 8.0 |
| KR-1 'Boar' | `restock-engine-boar` | 1,000 | 280 / 300 | 3.5 |
| KR-10A 'Corgi' (vacuum) | `restock-engine-375-corgi` | 750 | 95 / 355 | 5.25 |
| UR-2 'Caravel' | `restock-engine-caravel-1` | 510 | 265 / 320 | 2.0 |
| LV-N410 'Cherenkov' (nuclear) | `restock-engine-cherenkov` | 300 | 200 / 820 | 12.0 |
| RK-107 'Ursa' | `restock-engine-ursa-1` | 260 | 285 / 300 | 1.25 |
| UR-137 'Schnauzer' (vacuum) | `restock-engine-schnauzer-1` | 110 | 70 / 350 | 0.8 |
| LV-T15 'Valiant' | `restock-engine-125-valiant` | 100 | 240 / 270 | 0.75 |
| Mk-1H 'Torch' | `restock-engine-torch` | 55 | 275 / 295 | 0.29 |
| RK-1 'Trash Panda' vernier | `restock-engine-panda-1` | 32 | 285 / 300 | 0.18 |
| LV-303 'Pug' (carries 18 LF / 22 Ox) | `restock-engine-125-pug` | 25 | 150 / 330 | 0.2 |

## ReStock+: design notes

- 17 parts are hidden in the game (`TechHidden`, category none), including the Mallet, Striker and
  Anvil SRBs and many RCS blocks. Ingest includes them; never suggest a part whose category is
  `none`. The full list: `restock-claw-625-1`, `restock-engineplate-125-1`,
  `restock-nosecone-1875-1`, `restock-rcs-block-dual-1`, `restock-rcs-block-dual-mini-1`,
  `restock-rcs-block-quad-angled-1`, `restock-rcs-block-quad-angled-mini-1`,
  `restock-rcs-block-quad-mini-1`, `restock-rcs-block-quint-1`, `restock-rcs-block-qunit-mini-1`,
  `restock-rcs-block-triple-angled-1`, `restock-rcs-block-triple-angled-mini-1`,
  `restock-rcs-single-mini-1`, `restock-relay-radial-2`, `restock-srb-anvil-1`,
  `restock-srb-mallet-1`, `restock-srb-striker-1`.
- The FL-S1200 tank (`restock-fueltank-1875-soyuz-1`, 540 LF / 660 Ox) has a small built-in
  separation motor, so ingest tags it as an engine (32 kN on 4 units of SolidFuel). Treat it as a
  tank, not a stage's engine.
- Size names in parts.db: `size1p5` is 1.875 m and `size4` is 5 m.
