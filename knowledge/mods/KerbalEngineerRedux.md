# Kerbal Engineer Redux

- CKAN id: `KerbalEngineerRedux`, version 1.1.9.5, by CYBUTEK, jrbudda
- Kind: Flight tool. Changes rocket design: No
- Needs: nothing else in this install
- Needed by: nothing else in this install
- Links: [Source](https://github.com/jrbudda/KerbalEngineer), [Forum or homepage](https://forum.kerbalspaceprogram.com/index.php?/topic/17833-*)

Kerbal Engineer Redux shows craft and orbit statistics while building (Build Engineer) and flying
(Flight Engineer).

## Kerbal Engineer Redux: notes for the copilot

- The Build Engineer's per-stage delta-v and TWR are the reference to check `evaluate_build`
  against (the step-5 VAB check). Set its body and atmosphere to match the stage being compared.
- MechJeb and Engineer for All gives every pod and probe core the Engineer modules, so no Engineer
  part is needed.
