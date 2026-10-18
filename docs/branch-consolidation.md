# Knuckles branch consolidation plan

Audited 2026-10-18. The original integration sequence is retained below.
The user subsequently authorized local merges; see execution status.
Temporary `integration/knuckles` branches were used in each repository.
The two repositories have independent branches and release artifacts.

## Firmware: fcoury/zmk-config

Start the integration branch from refreshed `origin/main` (audited `ee8b4b43`).
Bring in `feat/knuckles-mouse-buttons`, based on the following existing work:

| Work | Revision | Treatment |
| --- | --- | --- |
| Working TPS43 setup and polling wake retry | `abe5c7cb` (`feat/knuckles-tps43-v2`) | Include |
| Opt-in idle polling diagnostic | `224327ed` (`feat/knuckles-tps43-idle-power`) | Include, keep disabled by default |
| EXTRA + F/D/S mouse buttons | `feat/knuckles-mouse-buttons` | Include after build and device validation |
| `origin/knuckles`, `origin/feat/tps43` | `aa603db`, `53d9ea4` | Preserve refs; do not bulk merge obsolete implementations |
| `origin/zeph` | `ceb1f62` | Leave separate; unrelated keyboard work |

The current TPS43 implementation descends directly from main, rather than from
those older feature branches. Comparing their keymaps found no missing bindings;
the old copies use an obsolete hold-tap property spelling. Merging their old
shield and driver configuration would risk reverting the working setup.
The existing local IQS5xx fork is not the dependency used by this firmware:
retain the pinned suchobits driver and repository patches.

Before promotion:

1. Build all four nice!nano Knuckles targets and the opt-in idle right target.
   Run `scripts/check-idle-builds.py` against the two right builds. Inspect the
   compiled keymap: EXTRA S/D/F must be middle/right/left mouse buttons; base
   letters and other bindings must remain unchanged.
2. On the existing pair, flash only the new right-central image. Verify both
   halves, pointer movement, taps, scrolling, three physical mouse buttons,
   held drag and normal F/D/S typing, over USB and Bluetooth. Do not clear bonds.
3. Complete the separate idle/deep-sleep and battery comparison from README
   before considering any change to the default polling policy. The reported
   short idle wake test does not establish power savings.
4. Run the full existing CI matrix, including Cosmos, Corne, Caldera, Souffle,
   TOTEM and settings reset. The branch also changes the shared reusable ZMK
   build-workflow version, so Knuckles-only builds are insufficient for main.
5. Open a firmware PR. Keep previous branches until main and its artifacts are
   verified. Preserve a known-working right UF2 for rollback.

A read-only `git merge-tree` check found no conflict between audited main and
`224327ed`. Recheck against fetched branches when executing this plan.

## PCB and cases: fcoury/knuckles

Start a separate integration branch from refreshed `origin/main` (audited
`24febbc`). Local main was behind by five commits at audit time; do not use it
as the integration base without updating it.

Already incorporated into origin/main: thin cases, Knuckles silkscreen,
scriptable 18.5/19.5 mm spacing, persisted KiCad project settings, README rewrite
and the archive of the ordered wireless PCB. Do not merge those branches again.
Keep 18.5 mm as the default and preserve the ordered-board archive.

Merge `feat/integrated-controller` (`2c2221a9`) into the staging branch. The
read-only merge check found one content conflict, in README.md. Preserve the
current reader-oriented README, artwork and archive links; add a clear link to
the integrated-controller engineering documentation. This branch adds the
engineering, sourcing, power, firmware and routed integrated-layout work.

Before promotion:

1. Run `npm test` and `npm run check:integrated`.
2. Generate both spacings with `npm run build:integrated` and
   `npm run build:integrated -- --spacing 19.5` in isolated output/workspaces as
   required by its build instructions. Check all four native routed layouts
   with `npm run check:integrated:routed`; inspect DRC/connectivity reports and
   the routing/engineering checklist. Regenerate routing only if changed
   geometry or validation requires it.
3. Verify existing nice!nano outputs, silkscreen, cases and spacing selection.
   Keep the integrated design opt-in and visibly an engineering prototype;
   source validation and saved routing do not establish fabrication readiness.
4. Review the integrated-controller firmware snapshot separately. Port the
   chosen mouse bindings and applicable driver fixes deliberately; preserve
   its own pin map, power design and bootloader requirements rather than
   copying a nice!nano devicetree wholesale.
5. Open the PCB PR with validation evidence and remaining manufacturing gates.
   Ordering, PCBA submission and fabrication approval remain separate work.

## Subsequent work

Use main as the durable base after the two integration PRs pass. Keep the
TinyTouch experiment in its independent project and a dedicated port branch;
first prove its sensor on the spare nice!nano, then integrate the verified
pointing driver. It is not part of this merge. Remove old branches/worktrees
only after explicit cleanup authorization and verification that useful work
has been retained.

## Execution status — 2026-10-18

The user authorized merging the eligible work into local main. The firmware
integration includes TPS43 wake fixes, opt-in idle polling, mouse buttons and
reproducible layer diagrams. All 15 targets in `build.yaml` passed local builds,
including both Studio-enabled targets and settings reset. The separate idle
right build and configuration/UF2 comparison passed. Both resulting right UF2s
match the earlier mouse-button artifacts byte-for-byte. See
[integration-validation.json](integration-validation.json) for the matrix and
artifact hashes. These are local reproductions of the CI matrix, not a hosted
GitHub Actions run.

The user confirmed that mouse buttons, drag, both halves' keys and touchpad
movement work after flashing the right half. Idle polling stays default-off;
long-sleep and battery comparison remain pending. The checker itself does not
perform hardware tests.

The PCB integration merged `feat/integrated-controller` with refreshed main,
resolved README, and synchronized only the integrated firmware mouse keymap.
The existing wake patch already matched. Both spacings rebuilt; all three
build tests, electrical/source checks and all four routed checks passed.
Both integrated firmware halves and the custom bootloader rebuilt, and the
sanitized charge-policy tests passed. PCB validation details and manufacturing
limits are retained in `hardware/integrated-controller/INTEGRATION.md` in the
PCB repository. The default remains the nice!nano board at 18.5 mm.

Feature branches and worktrees are retained. Superseded firmware branches,
unrelated Zeph work and TinyTouch were excluded as planned. No integrated
hardware was flashed or ordered. Remote publication is separate from these
local merges.
