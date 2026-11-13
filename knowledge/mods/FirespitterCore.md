# Firespitter Core

- CKAN id: `FirespitterCore`, version v7.17, by Roverdude
- Kind: Part framework. Changes rocket design: Indirectly
- Needs: nothing else in this install
- Needed by: Shuttle Lifting Body
- Links: [Source](https://github.com/snjo/Firespitter), [Forum or homepage](http://snjo.github.io/)

Firespitter Core is the plugin part of Firespitter, without its parts. Part mods use its modules
for texture, mesh and fuel switching.

## Firespitter Core: what ingest sees

- In your install, Shuttle Lifting Body needs it, and Kerbal Reusability Expansion uses it for the
  black Falcon 9 variant.
- A part that uses its fuel switch (`FSfuelSwitch`) gets its resources at runtime, so ingest can
  show it with the wrong fuel or none.
