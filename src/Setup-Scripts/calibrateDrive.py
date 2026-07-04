import odrive
from odrive.enums import *
import time
import argparse

"""
Maintainer: Maison Gulyas
Testing Purposes
UNO R3 -> ODrive 3.6 56V -> Eagle Power LA8308 KV130
Communication: UART (Moving to CANbus eventually)
Encoder: Magnetic incremental (e.g. AMS AS5047P / AS5048A in ABZ mode)
         Connect A/B/Z to GPIO encoder pins; Z (index) is optional but recommended.

This is the Setup Callibration with Index Signal 
"""
# Change odrv1 to whatever Odrive you are working on

dev0.axis1.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
dev0.axis1.motor.config.pre_calibrated = True
dev0.axis1.encoder.config.pre_calibrated = True
dev0.save_configuration()
