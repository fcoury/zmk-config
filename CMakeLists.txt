# Loaded through ZMK_EXTRA_MODULES by ZMK's reusable user-config workflow.
# Keep the polling fix with the config until the pinned upstream includes it.
if(CONFIG_INPUT_AZOTEQ_IQS5XX)
  find_package(Git REQUIRED)
  set(driver_dir "${ZEPHYR_ZMK_DRIVER_AZOTEQ_IQS5XX_MODULE_DIR}")
  set(retry_patch "${CMAKE_CURRENT_LIST_DIR}/patches/iqs5xx-polling-wake-retry.patch")
  if(NOT EXISTS "${driver_dir}/drivers/input/iqs5xx.c")
    message(FATAL_ERROR "IQS5xx module not found; run west update first")
  endif()

  execute_process(
    COMMAND "${GIT_EXECUTABLE}" -C "${driver_dir}" apply --reverse --check "${retry_patch}"
    RESULT_VARIABLE already_applied OUTPUT_QUIET ERROR_QUIET)
  if(NOT already_applied EQUAL 0)
    execute_process(
      COMMAND "${GIT_EXECUTABLE}" -C "${driver_dir}" apply --check "${retry_patch}"
      RESULT_VARIABLE patch_check OUTPUT_QUIET ERROR_VARIABLE patch_error)
    if(NOT patch_check EQUAL 0)
      message(FATAL_ERROR "IQS5xx wake retry patch does not match the driver: ${patch_error}")
    endif()
    execute_process(
      COMMAND "${GIT_EXECUTABLE}" -C "${driver_dir}" apply "${retry_patch}"
      RESULT_VARIABLE patch_result OUTPUT_QUIET ERROR_VARIABLE patch_error)
    if(NOT patch_result EQUAL 0)
      message(FATAL_ERROR "Could not apply IQS5xx wake retry patch: ${patch_error}")
    endif()
    message(STATUS "Applied IQS5xx polling wake retry fix")
  else()
    message(STATUS "IQS5xx polling wake retry fix already applied")
  endif()
endif()
