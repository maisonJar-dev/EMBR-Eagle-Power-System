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

* [odrivetool](https://docs.odriverobotics.com/v/latest/interfaces/odrivetool.html)
* PlatformIO extension
* Visual Studio Code or another compatible IDE
