#!/usr/bin/env python

'''
This module contains printer/plotter functions for the EV3 components.

I/O ports:
- A: Large motor, plotter rail
- B: Medium motor, plotter head
- D: Large motor, roller
- 1: Touch sensor, plotter rail reset sensor
- 2: Color sensor, paper feed detector
- /dev/video0: USB webcam
'''

import ev3dev.ev3 as ev3
import time

# hardware configuration

PLOTTER_RAIL_MOTOR = ev3.LargeMotor('A')
PLOTTER_HEAD_MOTOR = ev3.MediumMotor('B')
ROLLER_MOTOR = ev3.LargeMotor('D')

PLOTTER_RAIL_SENSOR = ev3.TouchSensor('1')
PAPER_FEED_SENSOR = ev3.ColorSensor('2')

SCREEN = ev3.Screen()
BUTTON = ev3.Button()

WEBCAM_NUMBER = 0 # USB webcam


def waitMotor(motor, breakOnStall=False):
	'''
	Wait until the specified motor stops running.
	If breakOnStall is True, this procedure will also end if the motor is stalled.
	Note: motor.state should have contained 'stalled' if the motor stalled, but this had not been implemented yet,
	so we use a speed-based stall detection system.
	in the December 2015 release of ev3dev.
	'''
	while 'running' in motor.state:
		if breakOnStall and (motor.speed == 0):
			break
		pass

def waitSensor(sensor, value):
	'''Wait until the specified sensor's value equals to the specified value.'''
	while sensor.value() != value:
		pass

def reset():
	'''
	Resets plotter rail, head and roller positions.
	'''
	PLOTTER_HEAD_MOTOR.run_timed(time_sp=800, duty_cycle_sp=-50)
	waitMotor(PLOTTER_HEAD_MOTOR, breakOnStall=True)

	PLOTTER_RAIL_MOTOR.run_forever(duty_cycle_sp=-30)
	waitSensor(PLOTTER_RAIL_SENSOR, 1)
	PLOTTER_RAIL_MOTOR.stop(stop_command='coast')
	PLOTTER_RAIL_MOTOR.reset()
	PLOTTER_RAIL_MOTOR.stop_command = 'brake'

	waitMotor(PLOTTER_RAIL_MOTOR)
	ROLLER_MOTOR.run_timed(time_sp=6000, duty_cycle_sp=-20)
	waitMotor(ROLLER_MOTOR)
	ROLLER_MOTOR.reset()
	ROLLER_MOTOR.stop_command = 'brake'



if __name__ == '__main__':
	reset()