# B9 Part Switch

- CKAN id: `B9PartSwitch`, version v2.21.0.4, by blowfish, linuxgurugamer
- Kind: Part framework. Changes rocket design: Indirectly
- Needs: Module Manager
- Needed by: Stock Waterfall Effects, Tundra Exploration - Stockalike Dragon V2 and Falcon 9
- Links: [Source](https://github.com/KSPModStewards/B9PartSwitch)

B9 Part Switch lets a part switch between meshes, resources, nodes and modules in the editor or in
flight. Its tank switching defines a part's fuel through named tank types instead of RESOURCE
nodes.

## B9 Part Switch: what ingest sees

- A switchable tank has a `ModuleB9PartSwitch` with SUBTYPEs that name a `tankType`, and a
  `baseVolume`. The first SUBTYPE is the default. Each `B9_TANK_TYPE` gives units per volume for
  each resource and a `tankMass` per volume that's added to the part's dry mass.
- B9's built-in LFO type: 0.45 LiquidFuel and 0.55 Oxidizer per unit of volume, tank mass
  0.000125 t per unit.
- Ingest reads RESOURCE nodes only, so these tanks show up empty in parts.db. In your install that
  affects Tundra Exploration's six tanks (capacities are in the Tundra Exploration note).
- A subtype can also change an engine's stats or add mass (Tundra's RU-1K nozzle switch). Ingest
  records the part's base config.
- Needed by Tundra Exploration and Stock Waterfall Effects.
