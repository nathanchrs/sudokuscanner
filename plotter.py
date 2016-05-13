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

PAPER_FEED_EMPTY_COLOR = 1 # black
MAX_X = 350
MAX_Y = 350

# color sensor values:
# - 0: No color
# - 1: Black
# - 2: Blue
# - 3: Green
# - 4: Yellow
# - 5: Red
# - 6: White
# - 7: Brown


def waitMotor(motor, breakOnStall=False, stallSpeed=0):
	'''
	Wait until the specified motor stops running.
	If breakOnStall is True, this procedure will also end if the motor is stalled.
	Note: motor.state should have contained 'stalled' if the motor stalled, but this had not been implemented yet,
	so we use a speed-based stall detection system.
	in the December 2015 release of ev3dev.
	'''
	while 'running' in motor.state:
		if breakOnStall and (abs(motor.speed) <= abs(stallSpeed)):
			break
		pass

def waitSensor(sensor, value, negate=False):
	'''
	Wait until the specified sensor's value equals to the specified value.
	If negate is True, wait until the values are not equal.
	'''
	if negate:
		while sensor.value() == value:
			pass
	else:
		while sensor.value() != value:
			pass

def waitButton(buttonType='any', mode='pressed'):
	'''
	Wait until the specified button is up/down/pressed (down then up).
	Possible modes: up, down, pressed
	Possible buttonTypes: any, backspace, enter, up, down, left, right
	'''
	if buttonType == 'any':
		if (mode == 'down') or (mode == 'pressed'):
			while not BUTTON.any():
				pass
		if (mode == 'up') or (mode == 'pressed'):
			while BUTTON.any():
				pass
	elif buttonType == 'backspace':
		if (mode == 'down') or (mode == 'pressed'):
			while not BUTTON.backspace:
				pass
		if (mode == 'up') or (mode == 'pressed'):
			while BUTTON.backspace:
				pass
	elif buttonType == 'enter':
		if (mode == 'down') or (mode == 'pressed'):
			while not BUTTON.enter:
				pass
		if (mode == 'up') or (mode == 'pressed'):
			while BUTTON.enter:
				pass
	elif buttonType == 'up':
		if (mode == 'down') or (mode == 'pressed'):
			while not BUTTON.up:
				pass
		if (mode == 'up') or (mode == 'pressed'):
			while BUTTON.up:
				pass
	elif buttonType == 'down':
		if (mode == 'down') or (mode == 'pressed'):
			while not BUTTON.down:
				pass
		if (mode == 'up') or (mode == 'pressed'):
			while BUTTON.down:
				pass
	elif buttonType == 'left':
		if (mode == 'down') or (mode == 'pressed'):
			while not BUTTON.left:
				pass
		if (mode == 'up') or (mode == 'pressed'):
			while BUTTON.left:
				pass
	elif buttonType == 'right':
		if (mode == 'down') or (mode == 'pressed'):
			while not BUTTON.right:
				pass
		if (mode == 'up') or (mode == 'pressed'):
			while BUTTON.right:
				pass



def reset():
	'''Resets plotter rail, head and roller positions.'''
	SCREEN.clear()
	SCREEN.draw.text((60, 60), 'Preparing...')
	SCREEN.update()

	PLOTTER_HEAD_MOTOR.run_timed(time_sp=800, duty_cycle_sp=-50)
	waitMotor(PLOTTER_HEAD_MOTOR, breakOnStall=True, stallSpeed=20)

	PLOTTER_RAIL_MOTOR.run_forever(duty_cycle_sp=-30)
	waitSensor(PLOTTER_RAIL_SENSOR, 1)
	PLOTTER_RAIL_MOTOR.stop(stop_command='coast')
	PLOTTER_RAIL_MOTOR.reset()
	PLOTTER_RAIL_MOTOR.stop_command = 'brake'

	ROLLER_MOTOR.stop_command = 'brake'
	if PAPER_FEED_SENSOR.value() != PAPER_FEED_EMPTY_COLOR:
		ROLLER_MOTOR.run_forever(duty_cycle_sp=-40)
		waitSensor(PAPER_FEED_SENSOR, PAPER_FEED_EMPTY_COLOR)

	SCREEN.clear()
	SCREEN.draw.text((45, 60), 'Reset complete')
	SCREEN.update()

def feedPaper():
	'''Positions paper, resets roller motor.'''
	SCREEN.clear()
	SCREEN.draw.text((45, 60), 'F5eeding paper...')
	SCREEN.update()

	ROLLER_MOTOR.run_forever(duty_cycle_sp=40)
	waitSensor(PAPER_FEED_SENSOR, PAPER_FEED_EMPTY_COLOR, negate=True)
	ROLLER_MOTOR.run_forever(duty_cycle_sp=-10)
	waitSensor(PAPER_FEED_SENSOR, PAPER_FEED_EMPTY_COLOR)
	ROLLER_MOTOR.run_to_rel_pos(position_sp=-90, duty_cycle_sp=10)
	waitMotor(ROLLER_MOTOR)

	ROLLER_MOTOR.reset()
	ROLLER_MOTOR.stop_command = 'brake'

	SCREEN.clear()
	SCREEN.draw.text((35, 60), 'Paper in position')
	SCREEN.update()


if __name__ == '__main__':

	ev3.Sound.tone([(2000, 200, 200)]).wait()
	reset()
	ev3.Sound.tone([(2000, 70, 30), (3000, 200, 0)]).wait()

	while True:
		SCREEN.clear()
		SCREEN.draw.text((72, 50), 'Ready!')
		SCREEN.draw.text((5, 70), 'Insert paper and press enter')
		SCREEN.update()
		waitButton(buttonType='enter')
		
		feedPaper()

