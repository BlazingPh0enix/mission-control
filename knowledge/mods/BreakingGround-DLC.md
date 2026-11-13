# Breaking Ground (DLC)

- CKAN id: `BreakingGround-DLC`, version 1.7.1, installed outside CKAN, by SQUAD
- Kind: Parts (DLC). Changes rocket design: Indirectly
- Needs: nothing else in this install
- Needed by: nothing else in this install

Breaking Ground is Squad's second expansion: robotic parts (a hinge, piston, rotor and rotational
servo in various sizes), deployable science equipment that keeps collecting data on a surface,
surface features to investigate (meteors, craters, rock outcroppings, cryovolcanoes) and a new
suit. It's installed outside CKAN, in `GameData/SquadExpansion/Serenity`, so parts.db lists its
parts under the mod `SquadExpansion`.

## Breaking Ground: design notes

- `evaluate_build` treats robotic parts as dry mass. It doesn't model rotors, propellers or
  moving parts, so it can't check aircraft or helicopter designs.
- Deployed science stations earn science over time, which helps a career tech-tree plan.
