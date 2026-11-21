# 0001: Dragging a downed friend at arm's length

- Status: Accepted
- Date: 2026-11-21
- Decided by: the maintainer

## Context

New Vegas Co-op lets a player drag a downed friend (to cover, to revive them there). The dragged player's own game
places their character: always 70 units (about 1 m) behind the dragger, against the way the dragger faces, whichever
way they walk.

In VR (FNVVR) people drag the way they would in reality: walking backwards, looking at the friend. The friend then
lay behind their back and was only in view when looking straight down. Moving them further behind (98 units, build
`0.1.11+fnvvr.6`) made it worse: out of view entirely.

Options considered:

1. Keep 70 behind (original).
2. A fixed spot in front of the dragger, or beside them.
3. Behind or in front depending on the walking direction.
4. **Arm's length**: the friend stays where they lie until the dragger is further away than an arm's length, then is
   pulled along the line between both; the arm's length is shorter in front of the dragger than behind.

Dragging also never ended on its own when both were apart (a door, fast travel): the friend stayed where they lay,
"dragged", with their bleed-out paused. Ending only after a delay (to ride out loading behind doors) was considered
and dropped in favour of watching the simple rule first. Carrying a friend through doors and teleports would need a
larger change and is not attempted.

## Decision

- Option 4: arm's length **30 units in front, 70 behind**, in between at the sides (50 exactly sideways). "In front"
  is where the dragger faces; in VR that is the body direction FNVVR takes from the head.
- Starting to drag from further away (up to the original 150) pulls the friend to arm's length with the first step.
  Height follows on stairs as in the original (over 60 units difference).
- Dragging stays within one place as in the original. When the friend is more than 400 units away or in another
  place, the dragger lets go at once and the bleed-out runs again.
- Both lengths are settings in `NVCoop.ini`: `DragDistanceFront`, `DragDistanceBack`. The dragged player's setting
  counts, since their game places them.

## Consequences

- Behaviour described in [../behaviour.md](../behaviour.md#dragging); code in `src/coop/drag_trail.h` (with a unit
  test) and `src/downed.cpp`.
- To watch in play: whether loading behind a door ends a drag too early; whether the original kept dragging across
  places on purpose; whether turning only the head in VR flips front and back in an unpleasant way.
- Changing the rule later is a new ADR.

## Test results (2026-11-21)

- Dragging by tapping Activate works with VR controllers and a gamepad (two PCs: one in VR and one flat, and both
  in VR). The arm's length (30 in front, 70 behind) was tried with the host in VR and the friend flat and feels
  right; walking backwards keeps the friend in view.
- Through a door: the dragger lets go when the door loads the other place ("not in this place"); New Vegas Co-op then
  brings the friend through the door as it does for every player, and they arrive standing next to the dragger. That
  fits fleeing from a fight to a safe place and is kept. So the worry about loading behind doors is settled.
- Still to watch: turning only the head in VR.
