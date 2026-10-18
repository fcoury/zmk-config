# Loaded through ZMK_EXTRA_MODULES by ZMK's reusable user-config workflow.
# Keep the polling fix with the config until the pinned upstream includes it.
if(CONFIG_INPUT_AZOTEQ_IQS5XX)
  find_package(Git REQUIRED)
  set(driver_dir "${ZEPHYR_ZMK_DRIVER_AZOTEQ_IQS5XX_MODULE_DIR}")
  set(driver_patches "${CMAKE_CURRENT_LIST_DIR}/patches/iqs5xx-polling-wake-retry.patch")
  if(CONFIG_KNUCKLES_TPS43_IDLE_POLLING)
    list(APPEND driver_patches "${CMAKE_CURRENT_LIST_DIR}/patches/iqs5xx-idle-polling.patch")
    zephyr_include_directories(include)
    zephyr_library()
    zephyr_library_include_directories(${APPLICATION_SOURCE_DIR}/include)
    zephyr_library_sources(src/tps43_idle_polling.c)
  endif()
  if(NOT EXISTS "${driver_dir}/drivers/input/iqs5xx.c")
    message(FATAL_ERROR "IQS5xx module not found; run west update first")
  endif()

  foreach(driver_patch IN LISTS driver_patches)
    execute_process(
      COMMAND "${GIT_EXECUTABLE}" -C "${driver_dir}" apply --reverse --check "${driver_patch}"
      RESULT_VARIABLE already_applied OUTPUT_QUIET ERROR_QUIET)
    if(NOT already_applied EQUAL 0)
      execute_process(
        COMMAND "${GIT_EXECUTABLE}" -C "${driver_dir}" apply --check "${driver_patch}"
        RESULT_VARIABLE patch_check OUTPUT_QUIET ERROR_VARIABLE patch_error)
      if(NOT patch_check EQUAL 0)
        message(FATAL_ERROR "IQS5xx patch ${driver_patch} does not match the driver: ${patch_error}")
      endif()
      execute_process(
        COMMAND "${GIT_EXECUTABLE}" -C "${driver_dir}" apply "${driver_patch}"
        RESULT_VARIABLE patch_result OUTPUT_QUIET ERROR_VARIABLE patch_error)
      if(NOT patch_result EQUAL 0)
        message(FATAL_ERROR "Could not apply IQS5xx patch ${driver_patch}: ${patch_error}")
      endif()
      message(STATUS "Applied IQS5xx patch ${driver_patch}")
    else()
      message(STATUS "IQS5xx patch ${driver_patch} already applied")
    endif()
  endforeach()
endif()
