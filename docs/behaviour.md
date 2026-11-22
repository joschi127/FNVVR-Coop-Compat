# Behaviour of FNVVR-Coop-Compat's changes

What a player sees and does with each change of FNVVR-Coop-Compat compared to New Vegas Co-op, why it was changed,
its settings and its test state. Decisions with alternatives are in [adr/](adr/README.md). Version strings:
`<upstream>+fnvvr.<n>` (`src/version.h`).

## Reviving, dragging, giving a Stimpak

- **Controls:** hold Activate next to a downed friend to revive them; tap it to drag them, tap again to let go. The
  game's Grab still drags too. Hold Activate at a hurt friend to give a Stimpak.
- **Gamepads and VR controllers work.** The original read keyboard and mouse only (xNVSE's `IsControlPressed`), so a
  gamepad, and VR controllers that FNVVR passes to the game as a gamepad, could never hold Activate. Now the gamepad
  input the game binds to the control counts as well.
- **Prompts name the right button:** the key or gamepad button bound to the control, or, when a mod renames the
  game's controls (FNVVR in VR: "the A button"), the same name the game's own texts use.
- **Why tap to drag:** FNVVR uses the grip for its own physics grab and never passes the game's Grab on, so in VR
  dragging was impossible.
- Tested: revive both ways with a gamepad and with VR controllers (two PCs); drag by tapping (two PCs).

## Dragging

The dragged friend is **held at arm's length**: they stay where they lie as long as the dragger is closer than an
arm's length. When the dragger walks further away, the friend is pulled along the line between both, at arm's
length. Walking backwards, as people drag, keeps the friend in front and in view; walking forwards, they follow
behind; stepping sideways, they follow sideways. Short steps and turning on the spot do not move them.

| Setting (`NVCoop.ini`, `[Coop]`) | Default | Meaning |
|---|---|---|
| `DragDistanceFront` | 30 | Arm's length while the friend lies in front of the dragger (where they face), game units (1 unit ≈ 1.4 cm) |
| `DragDistanceBack` | 70 | Arm's length while the friend lies behind the dragger (the original distance) |

At the sides the arm's length lies in between (50 with the defaults). The dragged player's own setting counts. Height
follows on stairs. Dragging stays within one place: when both are more than 400 units apart or in different places
(a door, fast travel), the dragger lets go and the friend's bleed-out runs again.

Through a door: the dragger lets go when the door loads the other place; New Vegas Co-op then brings the friend
through the door as it does for every player, and they arrive standing (seen in game). That fits fleeing from a
fight to a safe place and is kept.

Decision and alternatives: [ADR 0001](adr/0001-drag-at-arms-length.md). Test state: tested in game (host in VR,
friend flat), the defaults feel right; to watch: turning the head in VR.

## Quick start

Quick start is offered once the player has stood up in Doc Mitchell's house (tutorial stage 55), not right after
waking up. Name, sex and face are chosen in the intro as usual; the rest of the house is skipped, and the
"finish your character" menu follows outside. Before, the first-person camera stayed rolled sideways (also flat) and
the third-person view was locked, kept in saves. Tested.

## Main menu

- Join Co-op: "The last IP address" comes first when `JoinAddress` is set. Tested.
- Host Co-op: "Steam friends, and by IP address" comes first. Tested.

## Name plates and chat above heads in VR

- **What:** the name plates over friends (`NVCoopMark0..3`, also "DOWNED") and the chat above heads
  (`NVCoopAbove0..4`) also carry their place in the world: the tile traits `user2` to `user4` hold the anchor
  (name plates 150 units above the character as on the flat screen, chat 125, below the name as on the flat screen), `user5` is 1 while it should be shown, `user6` = 1 marks
  a name plate as a person's. Text and colour are set as well. This is written also while the friend is off the
  flat screen, but only in the player's place (same interior, or both outside in the same world). Name plates have
  no distance limit (FNVVR keeps far ones at 20 m in the friend's direction), chat above heads the flat 3500 units.
- **Why:** the flat game projects the plate with the flat camera; in VR that puts it beside the friend and without
  depth (FNVVR run c34). FNVVR reads these traits and draws the tile at its place in each eye, and its compass
  shows a mark for each friend. The interface is general and described in FNVVR's
  [docs/hud-world-tiles.md](https://github.com/joschi127/FNVVR/blob/coop-compat/docs/hud-world-tiles.md); FNVVR
  [ADR 0003](https://github.com/joschi127/FNVVR/blob/coop-compat/docs/adr/0003-coop-markers-in-vr.md).
- **Flat game:** unchanged; the game itself does not read these traits. A script call is made only when a plate
  appears, disappears, changes its text or moves by more than one unit.
- **Settings:** none (the flat plates still follow `bFriendMarkers`).
- **Test state:** not yet tested in game.

## Testing with fakefriend

[tools/coop_test.py](../tools/coop_test.py) runs co-op without a second person or game copy: it sets `NVCoop.ini`
for automatic hosting (`Mode=host`, `AutoApproveJoins=1`, `IpHosting=1`) and restores it byte for byte afterwards,
waits for "Hosting" and "joined" in `NVCoop.log`, and starts `fakefriend` (built with the mod, `tools/fakefriend`)
joining this PC by IP. Load a save past the intro; co-op starts hosting within seconds. Works with the flat game
and with FNVVR (headset or emulator); FNVVR-Test-Bridge (game commands) and FNVVR's VR test channel can drive the
rest. Used in FNVVR's emulator runs since c34.
