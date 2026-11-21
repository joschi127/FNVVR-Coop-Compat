# Architecture decision records

Decisions about this fork that shape its behaviour or code and are hard to reverse. Decisions about FNVVR or about
how the two mods relate live in the FNVVR repository: [joschi127/FNVVR docs/adr](https://github.com/joschi127/FNVVR/blob/coop-compat/docs/adr/README.md)
(see its ADR 0001 and 0005).

## How to add one

1. Copy [template.md](template.md) to `NNNN-short-title.md` with the next free number.
2. Fill in context, decision and consequences. Keep it short; link to code, docs, issues or commits instead of
   repeating them.
3. Status `Proposed` while it is open, `Accepted` once the maintainer agrees. An accepted ADR is not rewritten: a
   later change is a new ADR that supersedes it, and the old one gets status `Superseded by NNNN`.
4. Add it to the list below in the same commit, and describe the resulting behaviour in
   [../behaviour.md](../behaviour.md).

## Records

| No. | Title | Status |
|---|---|---|
| [0001](0001-drag-at-arms-length.md) | Dragging a downed friend at arm's length | Accepted |
