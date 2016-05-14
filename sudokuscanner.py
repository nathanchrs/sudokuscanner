#!/usr/bin/env python

'''
Main program
'''

import cv2, time
import plotter, sudokucapture, sudokusolver
from copy import deepcopy

if __name__ == '__main__':

	plotter.beep('starting')
	plotter.reset()
	plotter.beep('ready')

	while True:
		plotter.SCREEN.clear()
		plotter.SCREEN.draw.text((72, 50), 'Ready!')
		plotter.SCREEN.draw.text((5, 70), 'Insert paper and press enter')
		plotter.SCREEN.update()
		plotter.waitButton(buttonType='enter')

		# feed and position paper

		plotter.beep('ok')
		plotter.feedPaper()
		plotter.gotoXY(plotter.MAX_X, 300)

		plotter.beep('ok')
		plotter.SCREEN.clear()
		plotter.SCREEN.draw.text((10, 30), 'Please position the sudoku')
		plotter.SCREEN.draw.text((20, 50), 'puzzle under the camera')
		plotter.SCREEN.draw.text((15, 70), 'using the left and right')
		plotter.SCREEN.draw.text((12, 90), 'buttons, then press enter')
		plotter.SCREEN.update()

		cancelOperation = False
		while True:
			if plotter.BUTTON.left and (-plotter.ROLLER_MOTOR.position > 0):
				plotter.ROLLER_MOTOR.run_forever(duty_cycle_sp=100)
			elif plotter.BUTTON.right and (-plotter.ROLLER_MOTOR.position < plotter.MAX_Y):
				plotter.ROLLER_MOTOR.run_forever(duty_cycle_sp=-100)
			elif plotter.BUTTON.enter:
				plotter.ROLLER_MOTOR.stop()
				offsetY = plotter.MAX_Y + plotter.ROLLER_MOTOR.position
				plotter.beep('ok')
				break
			elif plotter.BUTTON.backspace:
				plotter.SCREEN.clear()
				plotter.SCREEN.draw.text((30, 60), 'Operation cancelled')
				plotter.SCREEN.update()
				plotter.unfeedPaper()
				plotter.beep('warning')
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
			plotter.SCREEN.clear()
			plotter.SCREEN.draw.text((10, 60), 'Failed to access camera #' + str(plotter.WEBCAM_NUMBER))
			plotter.SCREEN.update()
			plotter.unfeedPaper()
			plotter.beep('error')
			plotter.waitButton(buttonType='any')
			continue

		plotter.SCREEN.clear()
		plotter.SCREEN.draw.text((37, 60), 'Processing image...')
		plotter.SCREEN.update()
		retval, sudoku, processedImage, sudokuPosition = sudokucapture.read(inputImage)
		if not retval:
			plotter.SCREEN.clear()
			plotter.SCREEN.draw.text((10, 60), 'Sudoku puzzle not detected')
			plotter.SCREEN.update()
			plotter.unfeedPaper()
			plotter.beep('warning')
			plotter.waitButton(buttonType='any')
			continue

		cam.release()

		# solve sudoku

		originalSudoku = deepcopy(sudoku)
		plotter.SCREEN.clear()
		plotter.SCREEN.draw.text((65, 60), 'Solving...')
		plotter.SCREEN.update()
		retval, solvedSudoku = sudokusolver.solve(sudoku)
		if not retval:
			plotter.SCREEN.clear()
			plotter.SCREEN.draw.text((35, 60), 'Solution not found')
			plotter.SCREEN.update()
			plotter.unfeedPaper()
			plotter.beep('warning')
			plotter.waitButton(buttonType='any')
			continue

		# show solved sudoku on screen

		plotter.SCREEN.clear()
		lineY = 8
		for i in range(3):
			for l in range(3):
				b = i*3 + l
				line = ''
				for j in range(3):
					for k in range(3):
						c = j*3 + k
						line += str(solvedSudoku[b][c])
						if k < 2:
							line += ' '
					if j < 2:
						line += ' | '
				plotter.SCREEN.draw.text((26, lineY), line)
				lineY += 10
			if i < 2:
				plotter.SCREEN.draw.text((24, lineY), '----------------------')
				lineY += 10
		plotter.SCREEN.update()

		# calculate positions of digits

		sudokuTopLeftX, sudokuTopLeftY = plotter.convertCameraCoordinates(sudokuPosition[0][0], sudokuPosition[0][1])
		sudokuBottomLeftX, sudokuBottomLeftY = plotter.convertCameraCoordinates(sudokuPosition[1][0], sudokuPosition[1][1])
		sudokuBottomRightX, sudokuBottomRightY = plotter.convertCameraCoordinates(sudokuPosition[2][0], sudokuPosition[2][1])
		sudokuTopRightX, sudokuTopRightY = plotter.convertCameraCoordinates(sudokuPosition[3][0], sudokuPosition[3][1])

		sudokuX = (sudokuTopLeftX + sudokuBottomLeftX) / 2.0
		sudokuY = (sudokuTopLeftY + sudokuTopRightY) / 2.0 + offsetY
		sudokuWidth = (sudokuTopRightX + sudokuBottomRightX - sudokuTopLeftX - sudokuBottomLeftX) / 2.0
		sudokuHeight = (sudokuBottomLeftY + sudokuBottomRightY - sudokuTopLeftY - sudokuTopRightY) / 2.0
		sudokuCellWidth = sudokuWidth / 9.0
		sudokuCellHeight = sudokuHeight / 9.0
		sudokuCellPaddingX = sudokuWidth * 0.02
		sudokuCellPaddingY = sudokuHeight * 0.01
		sudokuDigitWidth = sudokuWidth * 0.06
		sudokuDigitHeight = sudokuHeight * 0.08

		# draw digits

		for i in range(9):
			for j in range(9):
				if originalSudoku[i][j] == 0:
					plotter.drawDigit(solvedSudoku[i][j], sudokuX + j*sudokuCellWidth + sudokuCellPaddingX, sudokuY + i*sudokuCellHeight + sudokuCellPaddingY, sudokuDigitWidth, sudokuDigitHeight)

		plotter.reset()
		plotter.beep('done')