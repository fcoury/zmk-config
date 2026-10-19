#pragma once
#include <stdint.h>
#define ZMK_BLE_PROFILE_COUNT 5
int zmk_ble_prof_select(uint8_t index);
int zmk_ble_active_profile_index(void);
