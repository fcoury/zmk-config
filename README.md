# Build locally

```shell
devcontainer up --workspace-folder "/Users/fcoury/code/zmk-config/zmk"
docker exec -w /workspaces/zmk -it <container-id> /bin/bash
```

Inside the container:

```shell
west init -l app/
west update
west build -p -s /workspaces/zmk/app -b nice_nano_v2 -- -DZMK_CONFIG=/workspaces/zmk-config/config -DSHIELD=caldera_left
mv build/zephyr/zmk.uf2 caldera_left.uf2
west build -p -s /workspaces/zmk/app -b nice_nano_v2 -- -DZMK_CONFIG=/workspaces/zmk-config/config -DSHIELD=caldera_right
mv build/zephyr/zmk.uf2 caldera_right.uf2
```

## Knuckles TPS43

The HolyKeebs TPS43 module mounts on top of the nice!nano and uses its power,
SDA, and SCL pins. Build and flash `knuckles_tps43_left` on the left half and
`knuckles_tps43_right` on the right half. The right half is the split central
because that is where the touchpad input is processed.

The HolyKeebs adapter does not expose the TPS43 RDY signal. The IQS5xx driver
therefore uses 12 ms I2C polling; do not add an `rdy-gpios` assignment unless a
real RDY wire has been added to the hardware.

The build applies `patches/iqs5xx-polling-wake-retry.patch` to the pinned driver
at CMake configuration time. A sleeping sensor may NACK its first read; the fix
retries after 200 microseconds in polling mode and opens the setup communication
window the same way. The patch is checked before applying and is safe to reuse
on an already patched workspace. GitHub's reusable build automatically loads
this repository as a Zephyr module via `zephyr/module.yml`.

For a local west workspace with dependencies already installed, build with:

```sh
west build -s zmk/app -d build/knuckles_tps43_right -b nice_nano_v2 -- \
  -DZMK_CONFIG=/absolute/path/to/zmk-config/config \
  -DZMK_EXTRA_MODULES=/absolute/path/to/zmk-config \
  -DSHIELD=knuckles_tps43_right
```

Replace the shield and build-directory suffix with `knuckles_tps43_left` for
the other half. `knuckles_left` and `knuckles_right` are the non-touchpad variant.
The diagnostic `.conf`/`.overlay` files are optional and are not enabled by the
normal build matrix. The probe configuration disables touchpad input to allow
raw I2C diagnosis; it is not a daily-use firmware.

Bluetooth slots are selected by holding the far-right bottom letter-row key
(apostrophe on the base layer) and pressing a number key from 1 to 5. Choose an
unused slot to pair a new host without replacing an existing pairing.

## Mouse buttons

On Knuckles TPS43, hold the left thumb Space key to activate EXTRA, then use
left-hand F for left click, D for right click, or S for middle click. Hold F
while moving a finger on the right-hand touchpad to drag; release F to drop.
These keys remain letters on the base layer. The existing touchpad gestures remain available.

The right TPS43 central processes key positions from both halves, so this
keymap update requires only the right half to be reflashed. It preserves the
left firmware and Bluetooth bonds. Non-pointing Knuckles builds retain their
previous transparent EXTRA bindings.

After flashing, test single clicks, right click, middle click and a held drag,
then confirm F/D/S still type normally after releasing EXTRA. Test over USB
and Bluetooth. Keep holding EXTRA until the mouse-button key is released.

## TPS43 idle polling diagnostic

The opt-in right-hand test uses the existing 12 ms polling while ZMK is active,
and 250 ms polling after the usual 30 seconds without keys or reported pointer
input. Key activity changes ZMK back to active and requests an immediate poll.
Pointer input also restores the active rate; first pointer response after idle
can take roughly 250 ms plus sensor/communication latency. This build retains
15-minute keyboard deep sleep, the existing keymap, BLE identity and sensor
configuration. USB logging stays disabled for a comparable battery test.

This tests polling overhead. It does not suspend the TPS43 or switch off its
supply, and it does not establish lower deep-sleep current. Touch-to-wake from
keyboard deep sleep is not added; press a keyboard key to wake as usual.

Use a separate driver checkout/build directory for this experiment. In a local
west workspace containing the pinned dependencies, first run `west zephyr-export`,
then build (replace both absolute config paths):

```sh
west build -s zmk/app -d build/knuckles_tps43_right_idle_test -b nice_nano_v2 -- \
  -DZMK_CONFIG=/absolute/path/to/zmk-config/config \
  -DZMK_EXTRA_MODULES=/absolute/path/to/zmk-config \
  -DSHIELD=knuckles_tps43_right \
  -DEXTRA_CONF_FILE=/absolute/path/to/zmk-config/config/knuckles_tps43_idle_test.conf
```

Omit `EXTRA_CONF_FILE` and use a different build directory for normal firmware.
The default build matrix does not enable this diagnostic. Both driver patches
are checked before applying and tolerate reconfiguration of an already patched
checkout. The idle patch's hooks compile only when the diagnostic is enabled.

After both builds, validate the configuration difference, compiled hooks and
UF2 family/application boundaries:

```sh
python3 scripts/check-idle-builds.py build/right-normal build/knuckles_tps43_right_idle_test
```

### On-device check and comparison

1. Flash only the right-hand diagnostic UF2 using its existing bootloader.
   Leave the left firmware and Bluetooth bonds in place; do not flash settings reset.
2. Confirm right/left keys, mouse movement, tap, hold/drag and scrolling still work.
3. Leave both halves untouched for at least 35 seconds. Try pointer movement
   first, then repeat with a quick tap first: check that the initial action is
   recognized and normal responsiveness returns. Repeat with a keypress first.
4. Unplug USB and leave idle over 16 minutes. Press a key to wake, then verify
   keys and pointing again. Also test after disconnecting/reconnecting the host.
5. Compare equal unplugged idle periods starting from full charge with the
   normal firmware and this diagnostic, under the same host/split conditions.
   Prefer battery-current measurements; voltage-based percentages are approximate.
6. Restore the normal right-hand UF2 if input behavior regresses.

Compilation/configuration checks do not verify this hardware sequence or battery
savings. If drain persists, measure current with the touchpad powered versus
physically disconnected, then investigate sensor suspend or its power rail.
