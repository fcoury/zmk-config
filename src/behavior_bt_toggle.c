#define DT_DRV_COMPAT knuckles_behavior_bt_toggle

#include <zephyr/device.h>
#include <zephyr/bluetooth/conn.h>
#include <drivers/behavior.h>
#include <zmk/behavior.h>
#include <zmk/ble.h>

BUILD_ASSERT(ZMK_BLE_PROFILE_COUNT >= 2, "Bluetooth toggle requires two host profiles");

static int on_pressed(struct zmk_behavior_binding *binding,
                      struct zmk_behavior_binding_event event) {
    // Read the actual selection so the existing BT1-5 shortcuts stay in sync.
    // From any other profile, the toggle returns to BT1.
    return zmk_ble_prof_select(zmk_ble_active_profile_index() == 0 ? 1 : 0);
}

static int on_released(struct zmk_behavior_binding *binding,
                       struct zmk_behavior_binding_event event) {
    return ZMK_BEHAVIOR_OPAQUE;
}

static const struct behavior_driver_api behavior_bt_toggle_driver_api = {
    .binding_pressed = on_pressed,
    .binding_released = on_released,
};

BEHAVIOR_DT_INST_DEFINE(0, NULL, NULL, NULL, NULL, POST_KERNEL,
                        CONFIG_KERNEL_INIT_PRIORITY_DEFAULT, &behavior_bt_toggle_driver_api);
