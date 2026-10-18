/* SPDX-License-Identifier: MIT */
#include <zephyr/device.h>
#include <zmk/activity.h>
#include <zmk/event_manager.h>
#include <zmk/events/activity_state_changed.h>
#include <knuckles/tps43_idle_polling.h>

uint32_t knuckles_tps43_poll_interval_ms(void) {
    return zmk_activity_get_state() == ZMK_ACTIVITY_ACTIVE
               ? CONFIG_INPUT_AZOTEQ_IQS5XX_POLL_INTERVAL_MS
               : CONFIG_KNUCKLES_TPS43_IDLE_POLL_INTERVAL_MS;
}

static int tps43_activity_listener(const zmk_event_t *eh) {
    const struct zmk_activity_state_changed *event = as_zmk_activity_state_changed(eh);
    const struct device *dev = DEVICE_DT_GET(DT_NODELABEL(tps43));

    if (event && event->state == ZMK_ACTIVITY_ACTIVE && device_is_ready(dev)) {
        knuckles_tps43_poll_now(dev);
    }
    return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(tps43_idle_polling, tps43_activity_listener);
ZMK_SUBSCRIPTION(tps43_idle_polling, zmk_activity_state_changed);
