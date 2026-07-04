import odrive
from odrive.enums import *
import time
import argparse

"""
Maintainer: Maison Gulyas
Testing Purposes
UNO R3 -> ODrive 3.6 56V -> Eagle Power LA8308 KV130
Communication: UART + RC-PWM input

Note:
- This is run inside odrivetool, so dev0 is already exposed.
- This config is for SENSORLESS velocity control.
- Smooth acceleration/deceleration is handled using INPUT_MODE_VEL_RAMP.
"""

print("Configuring ODrive Sensorless Smooth Velocity Ramp")
print(f"Firmware: {dev0.fw_version_major}.{dev0.fw_version_minor}.{dev0.fw_version_revision}")


class Args(argparse.Namespace):
    battery_capacity: float = 8.0       # Ah, Vevor 36V 8Ah
    discharge_rating: float = 3.75      # C, 30A BMS / 8Ah
    charge_rating: float = 1.0          # C
    pole_pair_count: int = 20           # Eagle Power LA8308: 40 magnets / 2
    kv_constant: int = 130              # Eagle Power LA8308 KV130
    baud_rate: int = 115200

    # RC-PWM velocity range
    # Keep low while testing.
    pwm_vel_limit: float = 5.0          # turns/s command range

    # Motor/current safety
    current_limit: float = 20.0         # A

    # Smoothness tuning
    # Lower = softer/slower acceleration
    # Higher = more aggressive acceleration
    vel_ramp_rate: float = 2.0          # turns/s^2

    # Velocity PI tuning
    # Start gentle. Tune upward only if response is weak.
    vel_gain: float = 0.02
    vel_integrator_gain: float = 0.1


args = Args()

# Derived values
battery_current_limit = args.battery_capacity * args.discharge_rating
torque_constant = 8.27 / args.kv_constant

# For sensorless flux linkage:
# Formula commonly used:
# pm_flux_linkage = 5.51328895422 / (pole_pairs * KV)
pm_flux_linkage = 5.51328895422 / (args.pole_pair_count * args.kv_constant)


# ===================== Main Configuration ===================== #

print("\tClearing old errors")
dev0.clear_errors()
time.sleep(0.5)

print("\tSetting axis1 to IDLE")
dev0.axis1.requested_state = AXIS_STATE_IDLE
time.sleep(0.5)


# ---------- Board-level config ----------
print("\tApplying board config")
time.sleep(0.5)

dev0.config.enable_brake_resistor = False

# Allows some regen current back into the DC bus.
# Be careful: if your battery/BMS cannot accept regen, this can cause over-voltage faults.
dev0.config.dc_max_negative_current = -3

# UART config
dev0.config.uart_a_baudrate = args.baud_rate
dev0.config.uart0_protocol = STREAM_PROTOCOL_TYPE_ASCII_AND_STDOUT


# ---------- GPIO / PWM input config ----------
print("\tApplying GPIO/PWM config")
time.sleep(0.5)

# Keep GPIO1/GPIO2 for UART
dev0.config.gpio1_mode = GPIO_MODE_UART_A
dev0.config.gpio2_mode = GPIO_MODE_UART_A

# Use GPIO3 for RC-PWM velocity command
dev0.config.gpio3_mode = GPIO_MODE_PWM

# Map PWM input to controller.input_vel
# This is important: input_vel goes through INPUT_MODE_VEL_RAMP.
dev0.config.gpio3_pwm_mapping.endpoint = dev0.axis1.controller._input_vel_property

# RC-PWM command range
# Full reverse PWM -> -5 turns/s
# Neutral PWM      ->  0 turns/s
# Full forward PWM -> +5 turns/s
dev0.config.gpio3_pwm_mapping.min = -args.pwm_vel_limit
dev0.config.gpio3_pwm_mapping.max = args.pwm_vel_limit


# ---------- Axis 1 motor config ----------
print("\tApplying axis1 motor config")
time.sleep(0.5)

dev0.axis1.motor.config.motor_type = MOTOR_TYPE_HIGH_CURRENT

# Calibration current
# If calibration fails, this may need to increase slightly.
# If the motor gets hot or jumps hard, reduce it.
dev0.axis1.motor.config.calibration_current = 5.0

# Current limit
dev0.axis1.motor.config.current_lim = args.current_limit

# Motor-specific constants
dev0.axis1.motor.config.pole_pairs = args.pole_pair_count
dev0.axis1.motor.config.torque_constant = torque_constant


# ---------- Sensorless config ----------
print("\tApplying sensorless config")
time.sleep(0.5)

dev0.axis1.config.enable_sensorless_mode = True

# Sensorless estimator needs flux linkage.
dev0.axis1.sensorless_estimator.config.pm_flux_linkage = pm_flux_linkage

# Sensorless startup ramp.
# This is only for getting sensorless control started.
# It is NOT the same as your normal input velocity ramp.
dev0.axis1.config.sensorless_ramp.current = 10.0
dev0.axis1.config.sensorless_ramp.vel = -3.0
dev0.axis1.config.sensorless_ramp.accel = 1.0


# ---------- Axis 1 controller config ----------
print("\tApplying axis1 smooth velocity controller config")
time.sleep(0.5)

dev0.axis1.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL

# Smooth acceleration/deceleration
dev0.axis1.controller.config.input_mode = INPUT_MODE_VEL_RAMP
dev0.axis1.controller.config.vel_ramp_rate = args.vel_ramp_rate
dev0.axis1.controller.config.vel_limit = args.pwm_vel_limit

# Remove integral action
dev0.axis1.controller.config.vel_integrator_gain = 0.0

# Keep small proportional velocity correction
dev0.axis1.controller.config.vel_gain = 0.01

# Optional acceleration feed-forward
dev0.axis1.controller.config.inertia = 0.01

# Start stopped
dev0.axis1.controller.input_vel = 0.0

# ---------- Startup behavior ----------
print("\tApplying startup config")
time.sleep(0.5)

# For first testing, I recommend NOT auto-starting closed loop on boot.
# Manually start it after checking errors.
dev0.axis1.config.startup_motor_calibration = True
dev0.axis1.config.startup_closed_loop_control = False
dev0.axis1.config.enable_sensorless_mode = True


# ---------- Save config ----------
print("Saving config")
time.sleep(0.5)

dev0.save_configuration()

print("\tConfiguration saved.")
print("\tAfter reboot/reconnect, clear errors and manually start axis1.")

dev0.clear_errors()
dev0.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL