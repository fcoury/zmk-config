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
