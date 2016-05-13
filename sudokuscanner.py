#!/usr/bin/env python

'''
Main program
'''

import * from plotter
import sudokucapture, sudokusolver

if __name__ == '__main__':

	SPEAKER.tone([(2000, 200, 200)]).wait()
	reset()
	SPEAKER.tone([(2000, 70, 30), (3000, 200, 0)]).wait()

	while True:
		SCREEN.clear()
		SCREEN.draw.text((72, 50), 'Ready!')
		SCREEN.draw.text((5, 70), 'Insert paper and press enter')
		SCREEN.update()
		waitButton(buttonType='enter')

		SPEAKER.tone([(3000, 200, 200)]).wait()
		feedPaper()
		gotoXY(MAX_X, 300)

		SPEAKER.tone([(3000, 200, 200)]).wait()
		SCREEN.clear()
		SCREEN.draw.text((10, 30), 'Please position the sudoku')
		SCREEN.draw.text((20, 50), 'puzzle under the camera')
		SCREEN.draw.text((15, 70), 'using the left and right')
		SCREEN.draw.text((12, 90), 'buttons, then press enter')
		SCREEN.update()

		while True:
			if BUTTON.left and (ROLLER_MOTOR.position > 0):
				ROLLER_MOTOR.run_forever(duty_cycle_sp=-20)
			elif BUTTON.right and (ROLLER_MOTOR.position < MAX_Y):
				ROLLER_MOTOR.run_forever(duty_cycle_sp=20)
			elif BUTTON.enter:
				ROLLER_MOTOR.stop()
				SPEAKER.tone([(3000, 200, 200)]).wait()
				break
			else:
				ROLLER_MOTOR.stop()