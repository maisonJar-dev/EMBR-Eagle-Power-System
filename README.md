# Gearbox System Firmware V1.0

> Firmware and testing environment for the development, configuration, and validation of the gearbox control system.

## Hardware Overview

| Hardware     | Firmware | Logic Voltage |
| ------------ | -------- | ------------- |
| ODESC3.6 56V | 5.6      | 3.3 V         |
| AS5047P      | N/A      | 3.3 V         |

---

## Current Testing Configuration

```text
Arduino Uno R3
      │
      ▼
ODESC3.6 56V
      │
      ▼
Eagle Power LA8308
```

> **Note:** The AS5047P encoder is currently experiencing integration issues. As a result, current testing is limited to feedforward control systems that do not rely on encoder feedback.

---

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/) with the recommended
  PlatformIO IDE extension, or a standalone PlatformIO Core installation
- [odrivetool](https://docs.odriverobotics.com/v/latest/interfaces/odrivetool.html)
  for drive configuration scripts

## First-time setup

Clone the repository, open the repository root in VS Code, accept the recommended
extensions, and run:

```sh
./scripts/bootstrap.sh
```

The script works with either a system `pio` command or PlatformIO Core installed
by the VS Code extension. It installs the board and library dependencies,
generates the VS Code IntelliSense configuration and compilation database, and
performs a complete firmware build.

Do not open only the `src` directory in VS Code. The repository root containing
`platformio.ini` must be the workspace folder.

## Build

From a terminal where `pio` is available:

```sh
pio run
```

If the VS Code extension installed PlatformIO but `pio` is not on the shell
`PATH`, use the bootstrap script or the PlatformIO toolbar instead. The firmware
output is written to `.pio/build/uno/firmware.hex`.

## Editor troubleshooting

The firmware may build while VS Code still displays stale diagnostics. Run
`C/C++: Reset IntelliSense Database`, followed by `Developer: Reload Window`.
