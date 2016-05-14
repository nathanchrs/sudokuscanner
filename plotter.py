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
SPEAKER = ev3.Sound

WEBCAM_NUMBER = 0 # USB webcam

PAPER_FEED_EMPTY_COLOR = 1 # black
MAX_X = 350
MAX_Y = 16000

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

def plotterHeadUp(halfRaise=True):
	'''Raises the plotter head. If halfRaise is True, the plotter head will only be lifted a bit to reduce time needed.'''
	if halfRaise:
		PLOTTER_HEAD_MOTOR.run_timed(time_sp=200, duty_cycle_sp=-50)
	else:
		PLOTTER_HEAD_MOTOR.run_timed(time_sp=800, duty_cycle_sp=-50)
	waitMotor(PLOTTER_HEAD_MOTOR, breakOnStall=True, stallSpeed=30)
	time.sleep(0.5)

def plotterHeadDown():
	'''Presses the plotter head down.'''
	PLOTTER_HEAD_MOTOR.run_timed(time_sp=800, duty_cycle_sp=50)
	waitMotor(PLOTTER_HEAD_MOTOR, breakOnStall=True, stallSpeed=30)
	time.sleep(0.5)

def reset():
	'''Resets plotter rail, head and roller positions.'''
	SCREEN.clear()
	SCREEN.draw.text((60, 60), 'Preparing...')
	SCREEN.update()

	plotterHeadUp(halfRaise=False)

	PLOTTER_RAIL_MOTOR.run_forever(duty_cycle_sp=-30)
	waitSensor(PLOTTER_RAIL_SENSOR, 1)
	PLOTTER_RAIL_MOTOR.stop(stop_command='coast')
	PLOTTER_RAIL_MOTOR.reset()
	PLOTTER_RAIL_MOTOR.stop_command = 'brake'

	ROLLER_MOTOR.stop_command = 'brake'
	PAPER_FEED_SENSOR.mode = 'COL-COLOR'
	if PAPER_FEED_SENSOR.value() != PAPER_FEED_EMPTY_COLOR:
		ROLLER_MOTOR.run_forever(duty_cycle_sp=100)
		waitSensor(PAPER_FEED_SENSOR, PAPER_FEED_EMPTY_COLOR)
		ROLLER_MOTOR.stop()

	SCREEN.clear()
	SCREEN.draw.text((45, 60), 'Reset complete')
	SCREEN.update()

def feedPaper():
	'''Positions paper, resets roller motor.'''
	SCREEN.clear()
	SCREEN.draw.text((45, 60), 'Feeding paper...')
	SCREEN.update()

	ROLLER_MOTOR.stop_command = 'brake'
	ROLLER_MOTOR.run_forever(duty_cycle_sp=-100)
	waitSensor(PAPER_FEED_SENSOR, PAPER_FEED_EMPTY_COLOR, negate=True)
	ROLLER_MOTOR.run_forever(duty_cycle_sp=100)
	waitSensor(PAPER_FEED_SENSOR, PAPER_FEED_EMPTY_COLOR)
	ROLLER_MOTOR.run_to_rel_pos(position_sp=1500, duty_cycle_sp=100)
	waitMotor(ROLLER_MOTOR)

	ROLLER_MOTOR.reset()
	ROLLER_MOTOR.stop_command = 'brake'

	SCREEN.clear()
	SCREEN.draw.text((35, 60), 'Paper in position')
	SCREEN.update()

def unfeedPaper():
	'''Cancel operation, return paper to starting position.'''
	ROLLER_MOTOR.run_forever(duty_cycle_sp=100)
	waitSensor(PAPER_FEED_SENSOR, PAPER_FEED_EMPTY_COLOR)
	ROLLER_MOTOR.run_to_rel_pos(position_sp=3500, duty_cycle_sp=100)
	waitMotor(ROLLER_MOTOR)

def beep(beepType='ok'):
	'''Emit sounds according to beepType: ok, starting, ready, warning, error, done.'''
	if beepType == 'ok':
		SPEAKER.tone([(3000, 200, 200)]).wait()
	elif beepType == 'starting':
		SPEAKER.tone([(2000, 200, 200)]).wait()
	elif beepType == 'ready':
		SPEAKER.tone([(2000, 70, 30), (3000, 200, 0)]).wait()
	elif beepType == 'warning':
		SPEAKER.tone([(2000, 70, 30), (2000, 70, 30)]).wait()
	elif beepType == 'error':
		SPEAKER.tone([(2000, 70, 30), (2000, 70, 30), (2000, 70, 30)]).wait()
	elif beepType == 'done':
		SPEAKER.tone([(2000, 70, 30), (3000, 70, 30), (4000, 200, 0)]).wait()

def gotoXY(x, y, bcm=True):
	'''
	Positions the plotter head at the specified coordinate.
	(0,0) is at the top-left corner of the paper.
	Paper is fed bottom-first.
	'''
	x = MAX_X - x
	y = MAX_Y - y
	if x < 0:
		x = 0
	if x > MAX_X:
		x = MAX_X
	if y < 0 :
		y = 0
	if y > MAX_Y:
		y = MAX_Y

	dx = abs(x - PLOTTER_RAIL_MOTOR.position)
	dy = abs(y + ROLLER_MOTOR.position)

	if bcm:
		if(y > -ROLLER_MOTOR.position):
			bcmy = 200
		else:
			bcmy = -200
		ROLLER_MOTOR.position += bcmy

	if dy > 0:
		ROLLER_MOTOR.run_to_abs_pos(position_sp=-y, duty_cycle_sp=100)
	if dx > 0:
		PLOTTER_RAIL_MOTOR.run_to_abs_pos(position_sp=x, duty_cycle_sp=30)
	if dy > 0:
		waitMotor(ROLLER_MOTOR)
	if dx > 0:
		waitMotor(PLOTTER_RAIL_MOTOR)
	time.sleep(0.5)

def convertCameraCoordinates(cameraX, cameraY):
	'''Converts camera coordinates (in pixels) to plotter coordinates (in degrees).'''
	pcx = round((cameraX - 96) * 0.800)
	pcy = round(((cameraY - 30) * 16.350) + 1900)
	return (pcx, pcy)

def drawDigit(digit, x, y, width, height):
	'''Draws a digit in the specified position, with the specified size.'''
	plotterHeadUp()
	if digit == 0:
		gotoXY(x, y)
		plotterHeadDown()
		gotoXY(x, y+height)
		gotoXY(x+width, y+height)
		gotoXY(x+width, y)
		gotoXY(x, y)
	elif digit == 1:
		gotoXY(x+width/2, y)
		plotterHeadDown()
		gotoXY(x+width/2, y+height)
	elif digit == 2:
		gotoXY(x, y)
		plotterHeadDown()
		gotoXY(x+width, y)
		gotoXY(x+width, y+height/2)
		gotoXY(x, y+height/2)
		gotoXY(x, y+height)
		gotoXY(x+width, y+height)
	elif digit == 3:
		gotoXY(x, y)
		plotterHeadDown()
		gotoXY(x+width, y)
		gotoXY(x+width, y+height/2)
		gotoXY(x, y+height/2)
		plotterHeadUp()
		gotoXY(x+width, y+height/2)
		plotterHeadDown()
		gotoXY(x+width, y+height)
		gotoXY(x, y+height)
	elif digit == 4:
		gotoXY(x, y)
		plotterHeadDown()
		gotoXY(x, y+height/2)
		gotoXY(x+width, y+height/2)
		plotterHeadUp()
		gotoXY(x+width, y)
		plotterHeadDown()
		gotoXY(x+width, y+height)
	elif digit == 5:
		gotoXY(x+width, y)
		plotterHeadDown()
		gotoXY(x, y)
		gotoXY(x, y+height/2)
		gotoXY(x+width, y+height/2)
		gotoXY(x+width, y+height)
		gotoXY(x, y+height)
	elif digit == 6:
		gotoXY(x+width, y)
		plotterHeadDown()
		gotoXY(x, y)
		gotoXY(x, y+height)
		gotoXY(x+width, y+height)
		gotoXY(x+width, y+height/2)
		gotoXY(x, y+height/2)
	elif digit == 7:
		gotoXY(x, y)
		plotterHeadDown()
		gotoXY(x+width, y)
		gotoXY(x+width, y+height)
	elif digit == 8:
		gotoXY(x, y)
		plotterHeadDown()
		gotoXY(x, y+height)
		gotoXY(x+width, y+height)
		gotoXY(x+width, y)
		gotoXY(x, y)
		plotterHeadUp()
		gotoXY(x, y+height/2)
		plotterHeadDown()
		gotoXY(x+width, y+height/2)
	elif digit == 9:
		gotoXY(x+width, y+height/2)
		plotterHeadDown()
		gotoXY(x, y+height/2)
		gotoXY(x, y)
		gotoXY(x+width, y)
		gotoXY(x+width, y+height)
		gotoXY(x, y+height)
	plotterHeadUp()

def printGrid(grid, x, y, width, height):
	'''Prints an image as contained on the 0-1 grid.'''
	row = len(grid)
	if row > 0:
		col = len(grid[0])

	dx = int(width/col)
	dy = int(height/row)

	plotterHeadUp()
	gotoXY(x-20, y-100) # backlash compensation
	gotoXY(x, y)

	for i in range(row):
		gotoXY(x-20, y+i*dy, bcm=False)
		segments = []
		cstart = 0
		prev = 0
		for j in range(col):
			if (prev == 0) and (grid[i][j] == 1): # start of a segment
				cstart = j
			elif (prev == 1) and (grid[i][j] == 0): # end of a segment
				segments.append([cstart, j])
			prev = grid[i][j]
		if (prev == 1):
			segments.append([cstart, j])
		for j in range(len(segments)):
			segStartX = x+segments[j][0]*dx
			segEndX = x+segments[j][1]*dx
			gotoXY(segStartX, y+i*dy, bcm=False)
			plotterHeadDown()
			gotoXY(segEndX, y+i*dy, bcm=False)
			plotterHeadUp()
		gotoXY(x+width+20, y+i*dy, bcm=False)
		gotoXY(x+width+20, y+(i+1)*dy, bcm=False)

def sudokuToGrid(sudoku, mask):
	'''Converts a sudoku puzzle to grid format. Only convert digits which corresponding mask is 0.'''
	grid = [[0 for j in range(43)] for i in range(61)]
	for i in range(9):
		for j in range(9):
			if mask[i][j] == 0:
				cr = i*7
				cc = j*5

				if sudoku[i][j] == 1:
					for k in range(5):
						grid[cr+k][cc+1] = 1
				elif sudoku[i][j] == 2:
					for k in range(3):
						grid[cr][cc+k] = 1
						grid[cr+2][cc+k] = 1
						grid[cr+4][cc+k] = 1
					grid[cr+3][cc] = 1
					grid[cr+1][cc+2] = 1
				elif sudoku[i][j] == 3:
					for k in range(3):
						grid[cr][cc+k] = 1
						grid[cr+2][cc+k] = 1
						grid[cr+4][cc+k] = 1
					grid[cr+3][cc+2] = 1
					grid[cr+1][cc+2] = 1
				elif sudoku[i][j] == 4:
					for k in range(3):
						grid[cr+k][cc] = 1
					for k in range(5):
						grid[cr+k][cc+2] = 1
					grid[cr+2][cc+1] = 1
				elif sudoku[i][j] == 5:
					for k in range(3):
						grid[cr][cc+k] = 1
						grid[cr+2][cc+k] = 1
						grid[cr+4][cc+k] = 1
					grid[cr+3][cc+2] = 1
					grid[cr+1][cc] = 1
				elif sudoku[i][j] == 6:
					for k in range(3):
						grid[cr][cc+k] = 1
						grid[cr+2][cc+k] = 1
						grid[cr+4][cc+k] = 1
					grid[cr+3][cc] = 1
					grid[cr+3][cc+2] = 1
					grid[cr+1][cc] = 1
				elif sudoku[i][j] == 7:
					for k in range(3):
						grid[cr+k][cc+2] = 1
					grid[cr+3][cc+1] = 1
					grid[cr+4][cc+1] = 1
					grid[cr][cc] = 1
					grid[cr][cc+1] = 1
				elif sudoku[i][j] == 8:
					for k in range(3):
						grid[cr][cc+k] = 1
						grid[cr+2][cc+k] = 1
						grid[cr+4][cc+k] = 1
					grid[cr+3][cc] = 1
					grid[cr+1][cc] = 1
					grid[cr+3][cc+2] = 1
					grid[cr+1][cc+2] = 1
				elif sudoku[i][j] == 9:
					for k in range(3):
						grid[cr][cc+k] = 1
						grid[cr+2][cc+k] = 1
						grid[cr+4][cc+k] = 1
					grid[cr+1][cc] = 1
					grid[cr+3][cc+2] = 1
					grid[cr+1][cc+2] = 1

	return grid
