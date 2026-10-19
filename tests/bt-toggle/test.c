#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdint.h>

static int current_profile, selected_profile, select_calls, select_error;

int zmk_ble_active_profile_index(void) { return current_profile; }
int zmk_ble_prof_select(uint8_t index) {
    select_calls++;
    selected_profile = index;
    if (!select_error) { current_profile = index; }
    return select_error;
}

// Compile the real callbacks; only ZMK registration and BLE APIs are stubbed.
#include "../../src/behavior_bt_toggle.c"

int main(void) {
    struct zmk_behavior_binding binding = {0};
    struct zmk_behavior_binding_event event = {0};
    for (int profile = 0; profile < 5; profile++) {
        current_profile = profile; // Includes selection through an existing BT shortcut.
        select_calls = 0;
        assert(behavior_bt_toggle_driver_api.binding_pressed(&binding, event) == 0);
        assert(selected_profile == (profile == 0 ? 1 : 0));
        assert(select_calls == 1);
        assert(behavior_bt_toggle_driver_api.binding_released(&binding, event) == ZMK_BEHAVIOR_OPAQUE);
        assert(select_calls == 1); // Key release must not switch a second time.
    }
    current_profile = 0;
    for (int press = 0; press < 6; press++) {
        assert(behavior_bt_toggle_driver_api.binding_pressed(&binding, event) == 0);
        assert(current_profile == (press % 2 == 0 ? 1 : 0));
    }
    select_error = -EIO;
    current_profile = 1;
    assert(behavior_bt_toggle_driver_api.binding_pressed(&binding, event) == -EIO);
    assert(current_profile == 1);
    puts("BT toggle: all profiles, repeated switching, external selection, release and error propagation passed.");
}
