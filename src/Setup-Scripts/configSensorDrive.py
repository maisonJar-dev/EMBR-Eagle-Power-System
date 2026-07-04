import odrive
from odrive.enums import *
import time
import argparse

"""
Maintainer: Maison Gulyas
Testing Purposes
UNO R3 -> ODrive 3.6 56V -> Eagle Power LA8308 KV130
Communication: UART (Moving to CANbus eventually)
Encoder: Magnetic AMS AS5047P in SPI mode)
        CS Pin -> GPIO 6 (ODESC3.6 56V)

Note this is ran in odrivetool at the moment which is why dev0
is undefined as it is exposed in the shell.

This config is for setup with Sensor (Magnetic Encoder)
"""

# Connect to the ODrive'
# Change odrv1 to whatever Odrive you are working

print("Configuring ODrive (With Encoder)")
print(f"Firmware:{dev0.fw_version_major}.{dev0.fw_version_minor}.{dev0.fw_version_revision}")

class Args(argparse.Namespace):
    battery_capacity: float = 8.0    # Ah (Vevor 36V 8Ah)
    discharge_rating: float = 3.75   # C  (30A BMS / 8Ah)
    charge_rating: float = 1.0       # C  (Standard 1C Li-ion)
    pole_pair_count: int = 20         # Eagle Power LA8308 (40 Magnets / 2)
    kv_constant: int = 130            # Eagle Power LA8308 KV130
    baud_rate: int = 115200
    pwm_vel_limit: float = 5.0
    current_limit: float = 20.0
    # Magnetic encoder CPR: AS5047P = 16384 CPR
    # Adjust to match your encoder's datasheet.
    encoder_cpr: int = 16384

args = Args()

# Derived
battery_current_limit = args.battery_capacity * args.discharge_rating
torque_constant = 8.27 / args.kv_constant

#==========Main Configuration==========#
# MARK: Main Config

# Clear old errors
print("\tClearing Errors")
dev0.clear_errors()
time.sleep(0.5)

# Make sure axis is idle while configuring
dev0.axis1.requested_state = AXIS_STATE_IDLE
time.sleep(0.5)

# ---------- Board-level config ----------
# MARK: Board-level
print("\tApplying board config")
time.sleep(0.5)

dev0.config.enable_brake_resistor = True
dev0.config.brake_resistance = 2.0  
dev0.config.dc_max_negative_current = -3

# Set baud rate
dev0.config.uart_a_baudrate = args.baud_rate

# Set to use ASCII stream protocol
dev0.config.uart0_protocol = STREAM_PROTOCOL_TYPE_ASCII_AND_STDOUT

# ---------- PWM input config ----------
# MARK: PWM
print("\tApplying PWM config")
time.sleep(0.5)

# WARNING:
# Don't use GPIO1 as it is the UART TX pin
# Keep GPIO1/GPIO2 for UART
dev0.config.gpio1_mode = GPIO_MODE_UART_A
dev0.config.gpio2_mode = GPIO_MODE_UART_A

# Use GPIO3 for PWM velocity control
dev0.config.gpio3_mode = GPIO_MODE_PWM
dev0.config.gpio3_pwm_mapping.endpoint = dev0.axis1.controller._input_vel_property
dev0.config.gpio3_pwm_mapping.min = -args.pwm_vel_limit
dev0.config.gpio3_pwm_mapping.max = args.pwm_vel_limit

# ---------- Axis 1 motor config ----------
# MARK: Motor
print("\tApplying axis1 motor config")
time.sleep(0.5)

dev0.axis1.motor.config.motor_type = MOTOR_TYPE_HIGH_CURRENT
dev0.axis1.motor.config.calibration_current = 5.0
dev0.axis1.motor.config.current_lim = args.current_limit
dev0.axis1.motor.config.pole_pairs = args.pole_pair_count
dev0.axis1.motor.config.torque_constant = torque_constant
# 

# ---------- Axis 1 controller config ----------
# MARK: Controller
print("\tApplying Axis1 controller config")
time.sleep(0.5)

dev0.axis1.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
dev0.axis1.controller.config.input_mode = INPUT_MODE_PASSTHROUGH

# Keep this aligned with or above your PWM mapping max.
dev0.axis1.controller.config.vel_limit = args.pwm_vel_limit

# Start stopped
dev0.axis1.controller.input_vel = 0.0

# ---------- Axis Start-Up ----------
# MARK: Start-Up
print("\tStarting Up")
time.sleep(0.5)

# Encoder-based startup sequence:
#   1. Motor calibration measures R and L.
#   2. Encoder index search spins slowly until the Z pulse is detected,
#      giving an absolute phase reference.
#   3. Closed-loop control starts using the encoder for feedback.
#
# If use_index = False, replace startup_encoder_index_search with
# startup_encoder_offset_calibration = True instead.
dev0.axis1.config.startup_motor_calibration = True
dev0.axis1.config.startup_encoder_index_search = False
dev0.axis1.encoder.config.use_index = False
dev0.axis1.config.startup_encoder_offset_calibration = True
dev0.axis1.config.startup_closed_loop_control = False

# Sensorless mode is NOT used with an encoder.
dev0.axis1.config.enable_sensorless_mode = False

# ---------- Control Structure & Tuning ----------
# MARK: Tuning
# Velocity and position gains — tune after first successful spin.
# These are conservative starting points for a BLDC of this size.
dev0.axis1.controller.config.vel_gain = 0.02          # [A/(turn/s)]
dev0.axis1.controller.config.vel_integrator_gain = 0.1  # [A/((turn/s)*s)]

dev0.axis1.encoder.config.abs_spi_cs_gpio_pin = 4
dev0.config.gpio4_mode = GPIO_MODE_DIGITAL_PULL_UP
dev0.axis1.encoder.config.mode = ENCODER_MODE_SPI_ABS_AMS
dev0.axis1.encoder.config.cpr = args.encoder_cpr

# ---------- Save Config ----------
# MARK: Save
print("Saving Config")
time.sleep(0.5)
print("\tODrive Configured, Configuration Saved, Rebooting :)")

# Toggle off if you haven't previously ran the sensor config for encoder use
dev0.axis1.motor.config.pre_calibrated = False
dev0.axis1.encoder.config.pre_calibrated = False
dev0.save_configuration()

#======================================#