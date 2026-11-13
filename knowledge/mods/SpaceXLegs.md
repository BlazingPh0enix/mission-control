# Kerbal Reusability Expansion

- CKAN id: `SpaceXLegs`, version 2.9.3, by EmbersArc, damon
- Kind: Parts. Changes rocket design: Yes
- Needs: Module Manager
- Needed by: Tundra Exploration - Stockalike Dragon V2 and Falcon 9
- Links: [SpaceDock](https://spacedock.info/mod/841/Kerbal%20Reusability%20Expansion), [Source](https://github.com/TundraMods/Kerbal-Reusability-Expansion), [Forum or homepage](https://forum.kerbalspaceprogram.com/index.php?/topic/195546-110-kre-kerbal-reusability-expansion/)

Kerbal Reusability Expansion (KRE) adds parts for reusable rockets: Falcon 9 landing legs in
three sizes (plus Mk2 versions), New Glenn "Glenn Legs" with mounts, ITS "LT-37" landing gear,
New Shepard legs, grid fins in three sizes (steel, and titanium "Nemesis"), deployable booster
wings, SuperDraco engines, a Dragon fuel tank, a Dragon heat shield, a trunk, an aerodynamic
docking port and vernier thrusters. Its DeployableAeroSurfaces plugin drives the grid fins.

## Kerbal Reusability Expansion: design notes

- SuperDraco: 90 kN, Isp 240/270 s, LiquidFuel and Oxidizer, 0.2 t. The Dragon Fuel Tank holds 180
  LiquidFuel and 220 Oxidizer (0.18 t dry).
- Falcon legs: 0.15 t (small), 0.25 t (medium), 0.55 t (large). Grid fins: 0.05, 0.2 and 0.35 t
  (titanium: 0.05, 0.1 and 0.3 t).
- The delta-v map has no figure for boostback and landing burns. When a design recovers its
  first stage, keep propellant in reserve in that stage and say how much was assumed.
- 11 old duplicates are hidden in the game (`TechHidden`, category none): `HexLegsL`, `HexLegsM`,
  `HexLegsMountL`, `HexLegsMountM`, `ITSLeg-L-KRE`, `ITSLeg-M-KRE`, `ShepardLeg-M`, `ShepardLeg-S`,
  `SpaceXLegs-S`, `SpaceXLegs-L` and `SpaceXLegs-XL`. Ingest includes them; suggest the `KRE-*`
  parts instead.
- KRE recommends Trajectories (installed) and FMRS Continued (not installed).
