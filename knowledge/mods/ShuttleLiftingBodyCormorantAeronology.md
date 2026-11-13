# Shuttle Lifting Body

- CKAN id: `ShuttleLiftingBodyCormorantAeronology`, version 1.12.5b, by Pak
- Kind: Parts. Changes rocket design: Yes
- Needs: Firespitter Core, Module Manager
- Needed by: nothing else in this install
- Links: [SpaceDock](https://spacedock.info/mod/417/Shuttle%20Lifting%20Body), [Forum or homepage](http://forum.kerbalspaceprogram.com/index.php?/topic/119951-cormorant-aeronology-dev-thread/&page=1)

Shuttle Lifting Body (Cormorant Aeronology) builds on the stock Mk3 parts to make a full Space
Shuttle: boosters, an external tank, an MMU and payload mounting options, plus new texture options
for the stock Mk3 cockpit, payload bays and landing gear. It needs Firespitter Core.

## Shuttle Lifting Body: design notes

- If the orbiter's main engines burn from the external tank, as on the real Shuttle, their thrust
  sits off the stack's centre. Check that their gimbal can hold the stack straight as the tank
  drains.
- One player's published profile for the CA Mk3 Shuttle (KerbalX, by gc1ceo): lock the main and
  orbital engines' gimbals for launch, start pitching over at about 325 m/s or 2.5 km, keep time to
  apoapsis above about 45 s, keep 100 to 130 m/s for re-entry, re-enter at about 40 degrees angle
  of attack, and land on runway 09 or 27 at 120 m/s or less. Their MechJeb settings: 128 km
  target orbit, turn from 2.5 km to 80 km, 80% throttle at lift-off and 40% at 70 km.
- That profile's "historical" method drops the tank with periapsis at 20 to 50 km and finishes
  the orbit with the orbital engines, so the orbiter needs its own propellant for that burn.

## Shuttle Lifting Body: what ingest sees

The part configs couldn't be checked: the mod isn't on GitHub, and SpaceDock downloads weren't
reachable from here. If `search_parts` shows the
external tank or the orbital engines' tanks empty, a Firespitter fuel switch is filling them at
runtime, the same problem as B9 Part Switch tanks.
