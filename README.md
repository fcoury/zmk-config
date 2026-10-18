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
