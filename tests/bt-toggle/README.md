# Bluetooth toggle callback test

From the repository root:

```sh
cc -std=c11 -Wall -Wextra -Werror -Wno-unused-parameter \
  -fsanitize=address,undefined -I tests/bt-toggle/stubs \
  tests/bt-toggle/test.c -o /tmp/knuckles-bt-toggle-test
/tmp/knuckles-bt-toggle-test
```

This compiles the real behavior callbacks with minimal ZMK registration/BLE
stubs. It checks selection from every existing slot, repeated switching,
selection through another shortcut, one switch per press and error propagation.
Firmware builds separately check the real headers, devicetree and registration.
This test cannot establish host reconnection timing or radio behavior.
