/* SPDX-License-Identifier: MIT */
#pragma once

#include <stdint.h>
#include <zephyr/device.h>

/* Called only by the no-RDY polling fallback, not the interrupt-driven path. */
uint32_t knuckles_tps43_poll_interval_ms(void);

/* Schedule an immediate poll on transition to active; performs no I2C itself. */
void knuckles_tps43_poll_now(const struct device *dev);
