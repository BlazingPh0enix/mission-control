# Tundra Exploration - Stockalike Dragon V2 and Falcon 9

- CKAN id: `TundraExploration`, version 7.2.0, by damon
- Kind: Parts. Changes rocket design: Yes
- Needs: Kerbal Reusability Expansion, B9 Part Switch, Module Manager, SmokeScreen - Extended FX Plugin, KSP Community Part Modules
- Needed by: nothing else in this install
- Links: [SpaceDock](https://spacedock.info/mod/223/Tundra%20Exploration%20-%20Stockalike%20Dragon%20V2%20and%20Falcon%209), [Source](https://github.com/TundraMods/TundraExploration), [Forum or homepage](https://forum.kerbalspaceprogram.com/index.php?/topic/166915-131-tundra-exploration-v093-stockalike-falcon-9-and-dragon-v2/)

Tundra Exploration adds stockalike SpaceX hardware with kaiju names: Mothra (Falcon 1),
Ghidorah 9 (Falcon 9), Bagorah 9 (Falcon 9 v1.0), Ghidorah Heavy parts (Falcon Heavy), Rodan
(Crew Dragon), Gigan (Cargo Dragon) and Gigan XL (Dragon XL). CKAN installs about 50 parts from
the `TundraExploration` folder, plus example craft in `Ships/VAB`. The Tundra Technologies parts in
the same repository (probe cores, antennas, the Gaira station) are a separate mod and aren't
installed.

## Tundra Exploration: fuel tanks (important)

The six tanks have no fuel in their part configs. B9 Part Switch fills them when the game runs,
using B9's LFO tank type (0.45 LiquidFuel and 0.55 Oxidizer per unit of volume, plus 0.000125 t of
tank mass per unit). Until ingest understands B9 tanks, parts.db lists these tanks as empty, so
`evaluate_build` reports their stages as having no propellant. Use these figures instead and say
so in the answer:

| Tank | Internal name | LiquidFuel | Oxidizer | Propellant (t) | Dry mass (t) |
|---|---|---|---|---|---|
| Ghidorah K1-180 (F9 stage 1) | `TE_19_F9_S1_Tank` | 10,080 | 12,320 | 112.0 | 14.0 |
| Ghidorah K2-81 (F9 stage 2) | `TE_19_F9_S2_Tank` | 2,340 | 2,860 | 26.0 | 3.25 |
| Bagorah K1-125 (F9 v1.0 stage 1) | `TE_19_F910_S1_Tank` | 7,020 | 8,580 | 78.0 | 9.75 |
| Bagorah K2-42 (F9 v1.0 stage 2) | `TE_19_F910_S2_Tank` | 1,215 | 1,485 | 13.5 | 1.69 |
| Mothra B1-21 (Falcon 1 stage 1) | `TE_F1_S1_Tank` | 720 | 880 | 8.0 | 1.0 |
| Mothra B2-52 (Falcon 1 stage 2) | `TE_F1_S2_Tank` | 144 | 176 | 1.6 | 0.2 |

Dry mass is the config mass plus B9's tank mass. Figures are computed from the 7.2.0 configs.

## Tundra Exploration: engines

| Engine | Internal name | Thrust, vacuum (kN) | Isp sea level / vacuum (s) | Mass (t) |
|---|---|---|---|---|
| VL-9R "Octopus" (F9 stage 1, the whole engine cluster in one part) | `TE_19_F9_S1_Engine` | 2,560 | 282 / 311 | 9.4 |
| VL-9D "Octopus" (F9 v1.0 stage 1) | `TE_19_F910_S1_Engine` | 1,600 | 275 / 305 | 9.4 |
| DF-1K Marlin (single engine) | `TE2_19_F9_Merlin_1D` | 250 | 282 / 311 | 1.0 |
| RU-1K "Marlin" Vacuum (F9 stage 2) | `TE_19_F9_S2_Engine` | 580 | 85 / 348 | 4.2 |
| RU-1C "Marlin" Vacuum (F9 v1.0 stage 2) | `TE_19_F910_S2_Engine` | 352 | 85 / 342 | 3.4 |
| RU-1Ci "Marlin 1Ci" (Falcon 1 stage 1) | `TE_F1_S1_Engine` | 198 | 261 / 303 | 0.9 |
| Tetra VAC (Falcon 1 stage 2) | `TE_F1_S2_Engine` | 26 | 85 / 317 | 0.2 |
| Rodan pod's built-in engines (MonoPropellant) | `TE_18_DRAGONV2_POD` | 228 | 290 / 305 | 3.4 (whole pod) |

## Tundra Exploration: design notes

- The Ghidorah, Ghidorah 40 and Bagorah 40 Launcher Platforms weigh 1,000 t each. They're launch
  towers that decouple from the rocket and stay on the pad, like launch clamps, so never count
  them in a stage's mass.
- The vacuum Marlins have a sea-level Isp of 85 s: upper stages only.
- The RU-1K has a nozzle switch. The small nozzle is 0.26 t lighter and changes the engine's
  stats; parts.db records the big nozzle.
- Falcon Heavy uses the GH-01 Nose Cone Guidance Unit and GH-02 Booster Decoupler on the side
  boosters.
- Crew: Rodan Command Pod (also Tourism and Cargo versions) with the RVS-42 trunk, PICA-K heat
  shield and Rodan drogue and main parachutes. The pod's built-in engines burn MonoPropellant, but
  the pod's config holds none, so check where the craft's monopropellant comes from.
- Booster landings need Kerbal Reusability Expansion (a required mod) for legs and grid fins.
  KSC Extended's Landing Zone 1 is a landing target, and Trajectories helps aim the descent.
- The example craft in `Ships/VAB` show the intended staging.
