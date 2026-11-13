# Mod notes

One note per mod in the current install (57 mods, KSP 1.12), named by its CKAN
identifier so it matches what `mod_info` returns. Each note says what the mod does and, where it
matters, how it changes rocket design and what ingest sees.

## Read these first

- Tundra Exploration's six fuel tanks are empty in parts.db, because B9 Part Switch fills them at
  runtime. The Tundra Exploration note has their real capacities.
- ReStock+ (17 parts) and Kerbal Reusability Expansion (11 parts) have parts hidden in the game.
  Never suggest a part whose category is `none`.
- Some tanks carry built-in separation motors (ReStock+'s FL-S1200 and Making History's
  Soyuz-style tanks), so ingest tags them as engines. Treat them as tanks.
- B9 Procedural Wings' mass in parts.db is a placeholder.
- Eleven of KSC Extended's launch sites are at the Tundra Space Center, 17 degrees north of the
  equator, which changes the launch inclination. Its pads also have size limits and opening costs;
  its note lists them.
- No planet pack is installed, so the delta-v map applies as is.

## All mods

| Mod | Note | Kind | Changes rocket design |
|---|---|---|---|
| KSC Extended | [KSCExtended.md](KSCExtended.md) | Launch sites | Yes |
| Kerbal Reusability Expansion | [SpaceXLegs.md](SpaceXLegs.md) | Parts | Yes |
| ReStock+ | [ReStockPlus.md](ReStockPlus.md) | Parts | Yes |
| Shuttle Lifting Body | [ShuttleLiftingBodyCormorantAeronology.md](ShuttleLiftingBodyCormorantAeronology.md) | Parts | Yes |
| Tundra Exploration - Stockalike Dragon V2 and Falcon 9 | [TundraExploration.md](TundraExploration.md) | Parts | Yes |
| Making History (DLC) | [MakingHistory-DLC.md](MakingHistory-DLC.md) | Parts (DLC) | Yes |
| B9 Aerospace Procedural Wings - Fork | [B9-PWings-Fork.md](B9-PWings-Fork.md) | Parts (procedural) | Yes |
| Kerbal Konstructs | [KerbalKonstructs.md](KerbalKonstructs.md) | Launch sites | Indirectly |
| Tundra's Space Center | [TundraSpaceCenter.md](TundraSpaceCenter.md) | Launch sites | Indirectly |
| Module Manager | [ModuleManager.md](ModuleManager.md) | Library | Indirectly |
| B9 Part Switch | [B9PartSwitch.md](B9PartSwitch.md) | Part framework | Indirectly |
| Firespitter Core | [FirespitterCore.md](FirespitterCore.md) | Part framework | Indirectly |
| KSP Community Part Modules | [KSPCommunityPartModules.md](KSPCommunityPartModules.md) | Part framework | Indirectly |
| Breaking Ground (DLC) | [BreakingGround-DLC.md](BreakingGround-DLC.md) | Parts (DLC) | Indirectly |
| Kopernicus Planetary System Modifier | [Kopernicus.md](Kopernicus.md) | Planet system | Indirectly |
| [x] Science! Continued | [xScienceContinued.md](xScienceContinued.md) | Planning tool | Indirectly |
| Transfer Window Planner - Fork | [TransferWindowPlannerFork.md](TransferWindowPlannerFork.md) | Planning tool | Indirectly |
| Kerbal Engineer Redux | [KerbalEngineerRedux.md](KerbalEngineerRedux.md) | Flight tool | No |
| MechJeb 2 | [MechJeb2.md](MechJeb2.md) | Flight tool | No |
| MechJeb and Engineer for all! | [MechJebForAll.md](MechJebForAll.md) | Flight tool | No |
| Trajectories | [Trajectories.md](Trajectories.md) | Flight tool | No |
| Omega's Stockalike Structures: No Textures Required | [StockalikeStructures.md](StockalikeStructures.md) | Launch sites | No |
| ClickThrough Blocker | [ClickThroughBlocker.md](ClickThroughBlocker.md) | Library | No |
| Custom Pre Launch Checks | [CustomPreLaunchChecks.md](CustomPreLaunchChecks.md) | Library | No |
| FireflyAPI | [FireflyAPI.md](FireflyAPI.md) | Library | No |
| Harmony 2 | [Harmony2.md](Harmony2.md) | Library | No |
| KSP Texture Loader | [KSPTextureLoader.md](KSPTextureLoader.md) | Library | No |
| KSPBurst Compiler | [KSPBurst.md](KSPBurst.md) | Library | No |
| KSPBurst Plugins | [KSPBurst-Lite.md](KSPBurst-Lite.md) | Library | No |
| ModularFlightIntegrator | [ModularFlightIntegrator.md](ModularFlightIntegrator.md) | Library | No |
| Shabby | [Shabby.md](Shabby.md) | Library | No |
| SpaceTux Library | [SpaceTuxLibrary.md](SpaceTuxLibrary.md) | Library | No |
| Toolbar Controller | [ToolbarController.md](ToolbarController.md) | Library | No |
| ReStock | [ReStock.md](ReStock.md) | Parts (visual replacement) | No |
| Rocket Sound Enhancement | [RocketSoundEnhancement.md](RocketSoundEnhancement.md) | Sound | No |
| Rocket Sound Enhancement - Default | [RocketSoundEnhancement-Config-Default.md](RocketSoundEnhancement-Config-Default.md) | Sound | No |
| HUD Replacer | [HUDReplacer.md](HUDReplacer.md) | UI | No |
| TriggerAu Flags | [TriggerAu-Flags.md](TriggerAu-Flags.md) | UI | No |
| VAB Organizer | [VABOrganizer.md](VABOrganizer.md) | UI | No |
| ZTheme | [ZTheme.md](ZTheme.md) | UI | No |
| Avalanche Plumes | [AvalanchePlumes.md](AvalanchePlumes.md) | Visuals | No |
| Deferred | [Deferred.md](Deferred.md) | Visuals | No |
| Environmental Visual Enhancements Redux | [EnvironmentalVisualEnhancements.md](EnvironmentalVisualEnhancements.md) | Visuals | No |
| EVE - Stock Planet Configs | [EnvironmentalVisualEnhancements-HR.md](EnvironmentalVisualEnhancements-HR.md) | Visuals | No |
| Firefly | [Firefly.md](Firefly.md) | Visuals | No |
| Parallax Continued | [ParallaxContinued.md](ParallaxContinued.md) | Visuals | No |
| Parallax Continued Planet Textures | [ParallaxContinued-Planet-Textures.md](ParallaxContinued-Planet-Textures.md) | Visuals | No |
| Parallax Continued Scatter Textures | [ParallaxContinued-Scatter-Textures.md](ParallaxContinued-Scatter-Textures.md) | Visuals | No |
| Parallax Continued Terrain Textures | [ParallaxContinued-Terrain-Textures.md](ParallaxContinued-Terrain-Textures.md) | Visuals | No |
| Scatterer | [Scatterer.md](Scatterer.md) | Visuals | No |
| Scatterer Default Config | [Scatterer-config.md](Scatterer-config.md) | Visuals | No |
| Scatterer Sunflare | [Scatterer-sunflare.md](Scatterer-sunflare.md) | Visuals | No |
| SmokeScreen - Extended FX Plugin | [SmokeScreen.md](SmokeScreen.md) | Visuals | No |
| Stock Waterfall Effects | [StockWaterfallEffects.md](StockWaterfallEffects.md) | Visuals | No |
| VaporCones | [VaporCones.md](VaporCones.md) | Visuals | No |
| Waterfall - Restock | [WaterfallRestock.md](WaterfallRestock.md) | Visuals | No |
| Waterfall Core | [Waterfall.md](Waterfall.md) | Visuals | No |

## Adding a mod

When you install a new mod, add `<CKAN id>.md` here and a row above: what it changes about
rocket design or flying, rules of thumb the copilot should follow, and parts you like or avoid.
