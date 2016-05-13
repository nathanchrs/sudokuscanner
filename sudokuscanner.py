#!/usr/bin/env python

'''
Main program
'''

import cv2
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

		# feed and position paper

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

		cancelOperation = False
		while True:
			if plotter.BUTTON.left and (plotter.ROLLER_MOTOR.position > 0):
				plotter.ROLLER_MOTOR.run_forever(duty_cycle_sp=-20)
			elif plotter.BUTTON.right and (plotter.ROLLER_MOTOR.position < plotter.MAX_Y):
				plotter.ROLLER_MOTOR.run_forever(duty_cycle_sp=20)
			elif plotter.BUTTON.enter:
				plotter.ROLLER_MOTOR.stop()
				plotter.SPEAKER.tone([(3000, 200, 200)]).wait()
				break
			elif plotter.BUTTON.backspace:
				plotter.SCREEN.clear()
				plotter.SCREEN.draw.text((30, 60), 'Operation cancelled')
				plotter.SCREEN.update()
				plotter.SPEAKER.tone([(2000, 70, 30), (2000, 70, 30)]).wait()
				plotter.waitButton(buttonType='any')
				cancelOperation = True
				break
			else:
				plotter.ROLLER_MOTOR.stop()
		if cancelOperation:
			continue

		# read sudoku puzzle

		plotter.SCREEN.clear()
		plotter.SCREEN.draw.text((65, 60), 'Scanning...')
		plotter.SCREEN.update()
		cam = cv2.VideoCapture(plotter.WEBCAM_NUMBER)
		retval, inputImage = cam.read()
		if not retval:
			plotter.SPEAKER.tone([(2000, 70, 30), (2000, 70, 30), (2000, 70, 30)]).wait()
			plotter.SCREEN.clear()
			plotter.SCREEN.draw.text((10, 60), 'Failed to access camera #' + str(plotter.WEBCAM_NUMBER))
			plotter.SCREEN.update()
			plotter.waitButton(buttonType='any')
			sys.exit(1)

		plotter.SCREEN.clear()
		plotter.SCREEN.draw.text((35, 60), 'Processing image...')
		plotter.SCREEN.update()
		retval, sudoku, processedImage, sudokuPosition = sudokucapture.read(inputImage)
		if not retval:
			plotter.SCREEN.clear()
			plotter.SCREEN.draw.text((10, 60), 'Sudoku puzzle not detected')
			plotter.SCREEN.update()
			plotter.SPEAKER.tone([(2000, 70, 30), (2000, 70, 30)]).wait()
			plotter.waitButton(buttonType='any')
			continue
		
		# found sudoku, show on screen

		plotter.SCREEN.clear()
		lineY = 8
		for i in range(3):
			for l in range(3):
				b = i*3 + l
				line = ''
				for j in range(3):
					for k in range(3):
						c = j*3 + k
						line += str(sudoku[b][c])
						if k < 2:
							line += ' '
					if j < 2:
						line += ' | '
				plotter.SCREEN.draw.text((25, lineY), line)
				lineY += 10
			if i < 2:
				plotter.SCREEN.draw.text((25, lineY), '----------------------')
				lineY += 10
		plotter.SCREEN.update()

		plotter.SPEAKER.tone([(3000, 200, 200)]).wait()
		plotter.waitButton(buttonType='any')