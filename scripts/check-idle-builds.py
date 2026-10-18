#!/usr/bin/env python3
"""Check that the right-hand diagnostic changes only its two polling options.

Also check firmware symbols and UF2 boundaries. This is not an on-device power
or wake-latency test. Run after building normal and diagnostic variants.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def config(folder):
    result = {}
    for line in (folder / 'zephyr/.config').read_text().splitlines():
        if line.startswith('CONFIG_'):
            key, value = line.split('=', 1)
            result[key] = value
        elif line.startswith('# CONFIG_') and line.endswith(' is not set'):
            result[line[2:-11]] = 'n'
    return result


def uf2(folder):
    data = (folder / 'zephyr/zmk.uf2').read_bytes()
    require(len(data) > 0 and len(data) % 512 == 0, 'Invalid UF2 file size')
    addresses = []
    for offset in range(0, len(data), 512):
        start, magic, flags, address, size, index, count, family = struct.unpack_from('<8I', data, offset)
        require((start, magic) == (0x0A324655, 0x9E5D5157), 'Invalid UF2 magic')
        require(struct.unpack_from('<I', data, offset + 508)[0] == 0x0AB16F30, 'Invalid UF2 end magic')
        require(flags == 0x2000 and family == 0xADA52840, 'Not nRF52840 flash firmware')
        require(index == offset // 512 and count == len(data) // 512, 'Invalid block sequence')
        require(size == 256 and address % 256 == 0, 'Unexpected UF2 block alignment')
        require(0x26000 <= address and address + size <= 0xEC000, 'UF2 outside nice!nano application slot')
        addresses.append(address)
    require(addresses[0] == 0x26000, 'Application must start after the bootloader')
    require(len(addresses) == len(set(addresses)), 'Duplicate flash addresses')
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('normal', type=Path)
    parser.add_argument('diagnostic', type=Path)
    args = parser.parse_args()
    normal, test = config(args.normal), config(args.diagnostic)
    feature = 'CONFIG_KNUCKLES_TPS43_IDLE_POLLING'
    interval = 'CONFIG_KNUCKLES_TPS43_IDLE_POLL_INTERVAL_MS'
    delta = {k for k in normal.keys() | test.keys() if normal.get(k) != test.get(k)}
    require(delta == {feature, interval}, f'Unexpected configuration changes: {sorted(delta)}')
    require(normal.get(feature) == 'n' and test.get(feature) == 'y', 'Diagnostic must be opt-in')
    for key, value in {
        interval: '250', 'CONFIG_INPUT_AZOTEQ_IQS5XX_POLL_INTERVAL_MS': '12',
        'CONFIG_ZMK_IDLE_TIMEOUT': '30000', 'CONFIG_ZMK_IDLE_SLEEP_TIMEOUT': '900000',
        'CONFIG_ZMK_SLEEP': 'y', 'CONFIG_ZMK_SPLIT_ROLE_CENTRAL': 'y',
        'CONFIG_ZMK_KEYBOARD_NAME': '"Knuckles TPS43"', 'CONFIG_LOG': 'n',
    }.items():
        require(test.get(key) == value, f'Unexpected {key}: {test.get(key)}')
    require((args.normal / 'zephyr/zephyr.dts').read_bytes() ==
            (args.diagnostic / 'zephyr/zephyr.dts').read_bytes(), 'Hardware configuration changed')
    for symbol in ['knuckles_tps43_poll_now', 'knuckles_tps43_poll_interval_ms']:
        require(symbol not in (args.normal / 'zephyr/zmk.map').read_text(), 'Normal build contains diagnostic hook')
        require(symbol in (args.diagnostic / 'zephyr/zmk.map').read_text(), 'Diagnostic hook is missing')
    print(json.dumps({'normal': uf2(args.normal), 'diagnostic': uf2(args.diagnostic),
                      'configuration_delta': sorted(delta), 'on_device_tested': False}, indent=2))


if __name__ == '__main__':
    main()
