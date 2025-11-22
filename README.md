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

## Build locally (without Docker)

Requirements:

- ARM GNU toolchain available (example below uses `/Users/fcoury/code/arm-gnu-toolchain` with `arm-none-eabi-*` symlinked in `bin/`)
- `west` and Python 3.11 with `pyelftools` installed
- Repo already initialized with `west` (`.west` at repo root)

Steps (from repo root `/Users/fcoury/code/zmk-config`):

```shell
# Toolchain env
export ZEPHYR_TOOLCHAIN_VARIANT=gnuarmemb
export GNUARMEMB_TOOLCHAIN_PATH=/Users/fcoury/code/arm-gnu-toolchain

# Install pyelftools once if missing
/opt/homebrew/opt/python@3.11/bin/python3.11 -m pip install --break-system-packages --user pyelftools

# Update modules (if not already done)
west update

# Build TPS43 test firmware
west build -p -b nice_nano_v2 -s zmk/app -d build/holykeebs_tps43 \
  -- -DSHIELD=holykeebs_tps43 -DZMK_CONFIG=./config
```

Or:

```shell
ZEPHYR_TOOLCHAIN_VARIANT=gnuarmemb GNUARMEMB_TOOLCHAIN_PATH=/Users/fcoury/code/arm-gnu-toolchain west build -p -b nice_nano_v2 -s zmk/app -d build/holykeebs_tps43 -- -DSHIELD=holykeebs_tps43 -DZMK_CONFIG=/Users/fcoury/code/zmk-config/config
```

# UF2 will be at:

build/holykeebs_tps43/zephyr/zmk.uf2
