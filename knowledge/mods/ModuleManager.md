# Module Manager

- CKAN id: `ModuleManager`, version 4.2.3, by ialdabaoth, Sarbian, Blowfish
- Kind: Library. Changes rocket design: Indirectly
- Needs: nothing else in this install
- Needed by: Avalanche Plumes, B9 Aerospace Procedural Wings - Fork, B9 Part Switch, Firefly, Kerbal Reusability Expansion, Kopernicus Planetary System Modifier, KSC Extended, KSP Texture Loader, MechJeb 2, MechJeb and Engineer for all!, Omega's Stockalike Structures: No Textures Required, Parallax Continued, Parallax Continued Planet Textures, Parallax Continued Terrain Textures, ReStock, ReStock+, Rocket Sound Enhancement - Default, Shuttle Lifting Body, Stock Waterfall Effects, Trajectories, Tundra Exploration - Stockalike Dragon V2 and Falcon 9, Tundra's Space Center, VAB Organizer, Waterfall - Restock, Waterfall Core, ZTheme
- Links: [Source](https://github.com/sarbian/ModuleManager), [Forum or homepage](https://forum.kerbalspaceprogram.com/index.php?/topic/50533-*)

Module Manager applies patches (`@PART[...]`) to game configs at load time. Most part mods
depend on it.

## Module Manager: what ingest relies on

- After loading, Module Manager writes the fully patched configs to
  `GameData/ModuleManager.ConfigCache`. Ingest parses that file, so part stats include every mod's
  patches.
- It also writes `GameData/ModuleManager.TechTree`, which ingest uses when the cache has no tech
  tree.
- After adding, removing or updating mods, start KSP and wait for the main menu before running
  ingest, so the cache is current.
