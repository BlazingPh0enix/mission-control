# B9 Aerospace Procedural Wings - Fork

- CKAN id: `B9-PWings-Fork`, version 3:0.46.1, by Crzyrndm, jrodrigv, Rafterman82, CarnationRED, tetraflon, linuxgurugamer
- Kind: Parts (procedural). Changes rocket design: Yes
- Needs: Module Manager
- Needed by: nothing else in this install
- Links: [Source](https://github.com/B9-Procedural-Wings/B9-PWings-Modified), [Forum or homepage](https://forum.kerbalspaceprogram.com/index.php?/topic/203629-*)

B9 Procedural Wings adds three procedural parts whose size and shape you set in the editor:
`B9_Aero_Wing_Procedural_TypeA` (B9-PW wing), `TypeB` (B9-PCST control surface) and `TypeC`
(B9-PCSA all-moving control surface). Press J over a wing to open its settings.

## B9 Procedural Wings: design notes

- The wing sets its own parameters from its dimensions at runtime, so the config's 0.05 t isn't
  the real mass and parts.db's mass for these parts is wrong. Leave them out of delta-v-critical
  stages, or ask the player for the VAB mass.
- Useful for spaceplanes and the Shuttle Lifting Body orbiter. The configs carry FAR modules, but
  FAR isn't installed, so stock aerodynamics apply.
- Deferred needs version 0.46.0 or later; 0.46.1 is installed.
