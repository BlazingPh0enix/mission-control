# Making History (DLC)

- CKAN id: `MakingHistory-DLC`, version 1.12.1, installed outside CKAN, by SQUAD
- Kind: Parts (DLC). Changes rocket design: Yes
- Needs: nothing else in this install
- Needed by: nothing else in this install

Making History is Squad's first expansion: the Mission Builder, a History Pack of missions, new
parts and extra launch sites (Woomerang and Dessert). It's installed outside CKAN, in
`GameData/SquadExpansion/MakingHistory`, so parts.db lists its parts under the mod `SquadExpansion`
(shared with Breaking Ground).

## Making History: design notes

- New engines include the Wolfhound (vacuum), Skiff, Cub (vernier), Kodiak, Cheetah, Bobcat and
  Mastodon. Players often rate the Wolfhound highly as a vacuum engine (about 375 kN, Isp 412 s
  according to forum posts); take exact stats from `get_part`.
- It adds a 1.875 m size class, which parts.db calls `size1p5`.
- The Soyuz-style conical tanks have built-in separation motors, so ingest may tag them as
  engines. Treat them as tanks.
- Woomerang and Dessert are away from KSC. KSC sits on the equator, so launch from KSC when the
  target orbit is equatorial.
