# Project guidelines (FNVVR-Coop-Compat)

Guidelines for everyone working on this fork: developers and AI coding agents alike. Agent entry files
(`CLAUDE.md`, `AGENTS.md`) only point here.

## What this is

A **modified version** of [New Vegas Co-op](https://github.com/Zyrcxies/NewVegasCoop) by Zyrcxies, kept small: only
the changes needed to play New Vegas Co-op together with the VR mod
[FNVVR](https://github.com/joschi127/FNVVR) (fork of [df4l/FNVVR](https://github.com/df4l/FNVVR)), and fixes that
help every player (for example gamepad support). It is not the official New Vegas Co-op. Everything that is not
specific to this fork is documented in the upstream README and CHANGELOG.

The two mods stay separate: FNVVR does not contain co-op code, and this fork does not contain VR code. What the two
need from each other is documented in both repositories and kept as small as possible (see FNVVR's
`docs/adr/0001-two-separate-mods-that-cooperate.md` and `docs/analysis/conflicts.md`).

## Licence (read before changing or sharing anything)

This repository is under the New Vegas Co-op licence (`LICENSE`), not FNVVR's zlib licence:

- Keep every copyright, licence and credit notice. Changed files get a short `FNVVR-Coop-Compat:` comment next to the
  change and in the file header; the original header line stays.
- Modified versions must credit "based on New Vegas Co-op by Zyrcxies" with a link, say they are modified and not
  official, must not use the name "New Vegas Co-op" as their own name, include `LICENSE`, and keep their complete
  source public under the same licence for as long as they are distributed.
- Built files of this fork are shared only together with this source and the notices above. The unmodified original
  is never shared or reuploaded (licence section 2); link to the author's pages instead.
- Code from this fork must not go into FNVVR (its zlib licence cannot take it). Code from FNVVR may come here with its
  zlib notice kept. Facts (addresses, call order, structure layouts) may be used in both.

## Git workflow

- Remotes: `origin` = this fork (https://github.com/joschi127/FNVVR-Coop-Compat), `upstream` =
  Zyrcxies/NewVegasCoop, fetch only (push URL disabled). Never push to `upstream`.
- `main` mirrors `upstream/main` (fast-forward only). Fork work happens on `vr-compat` in small commits that each
  build; upstream releases arrive as one commit per version, merge them into `vr-compat`.
- Version string: upstream version plus `+fnvvr.<n>` (`src/version.h`), so logs show a modified build. The plugin
  version number and the network protocol stay upstream's.
- Both players need the identical `NVCoop.dll` (co-op compares NVSE plugins between players).
- No AI attribution in commits or pull requests; commits are authored by the repository owner.
- Coordination with Zyrcxies (issues, pull requests) is the repository owner's decision. Fixes that help every
  player are good candidates to offer upstream.

## Behaviour and decisions

- [behaviour.md](behaviour.md) describes every change as players see it (controls, prompts, settings, test state);
  update it with each change.
- Decisions with alternatives go into [adr/](adr/README.md) of this repository. Decisions about FNVVR or about how
  the two mods relate stay in the FNVVR repository. Plan behaviour changes with the maintainer before coding.

## Build and test

See the upstream README (Visual Studio 2026, CMake presets `x86` / `release`). `nvcoop_tests` must pass. Game tests
(with FNVVR, `fakefriend`, two PCs) are planned and logged in the FNVVR repository's local notes.
