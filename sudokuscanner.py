#!/usr/bin/env python

'''
Main program
'''

import plotter, sudokucapture, sudokusolver

if __name__ == '__main__':

	plotter.SPEAKER.tone([(2000, 200, 200)]).wait()
	plotter.reset()
	plotter.SPEAKER.tone([(2000, 70, 30), (3000, 200, 0)]).wait()

	while True:
		plotter.SCREEN.clear()
		plotter.SCREEN.draw.text((72, 50), 'Ready!')
		plotter.SCREEN.draw.text((5, 70), 'Insert paper and press enter')
		plotter.SCREEN.update()
		plotter.waitButton(buttonType='enter')

		plotter.SPEAKER.tone([(3000, 200, 200)]).wait()
		plotter.feedPaper()
		plotter.gotoXY(plotter.MAX_X, 300)

		plotter.SPEAKER.tone([(3000, 200, 200)]).wait()
		plotter.SCREEN.clear()
		plotter.SCREEN.draw.text((10, 30), 'Please position the sudoku')
		plotter.SCREEN.draw.text((20, 50), 'puzzle under the camera')
		plotter.SCREEN.draw.text((15, 70), 'using the left and right')
		plotter.SCREEN.draw.text((12, 90), 'buttons, then press enter')
		plotter.SCREEN.update()

		while True:
			if plotter.BUTTON.left and (plotter.ROLLER_MOTOR.position > 0):
				plotter.ROLLER_MOTOR.run_forever(duty_cycle_sp=-20)
			elif plotter.BUTTON.right and (plotter.ROLLER_MOTOR.position < plotter.MAX_Y):
				plotter.ROLLER_MOTOR.run_forever(duty_cycle_sp=20)
			elif plotter.BUTTON.enter:
				plotter.ROLLER_MOTOR.stop()
				plotter.SPEAKER.tone([(3000, 200, 200)]).wait()
				break
			else:
				plotter.ROLLER_MOTOR.stop()