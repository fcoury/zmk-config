#pragma once
#include <stddef.h>
#define BUILD_ASSERT(condition, message) _Static_assert(condition, message)
// Device registration is exercised by the firmware builds, not this host test.
#define BEHAVIOR_DT_INST_DEFINE(...)
