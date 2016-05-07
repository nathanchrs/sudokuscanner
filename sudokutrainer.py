import numpy as np
import cv2, sys
from numpy.linalg import norm
from common import mosaic

WEBCAM_NUMBER = 0
CROP_PIXELS = 4
CELL_SIZE = 20
PROCESS_SQUARE_SIZE = (CELL_SIZE + 2*CROP_PIXELS)*9
DIGIT_MIN_AREA = (CELL_SIZE*CELL_SIZE)//10

if __name__ == '__main__':

	iteration = raw_input('Enter iteration name: '):

	# capture an image from webcam
	print "Capturing training sudoku image from webcam #" + str(WEBCAM_NUMBER) + "..."
	cam = cv2.VideoCapture(WEBCAM_NUMBER)
	ret_val, inputImage = cam.read()
	if not ret_val:
		print 'Failed to read from webcam #' + str(WEBCAM_NUMBER)
		sys.exit(1)

	# pre-process image
	processedImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
	processedImage = cv2.GaussianBlur(processedImage, (5,5), 0)
	processedImage = cv2.adaptiveThreshold(processedImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)

	# find contours in image
	contours, hierarchy = cv2.findContours(processedImage.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# find largest square (sudoku grid)
	sudokuSquare = None
	maxArea = 0
	for i in contours:
		area = cv2.contourArea(i)
		if area > 100:
			perimeter = cv2.arcLength(i, True) # arcLength(img, closed) finds the perimeter of a closed/open contour
			contourPolygon = cv2.approxPolyDP(i, 0.02*perimeter, True) # approxPolyDP(img, accuracy, closed) generates a simple polygon from a contour according to the accuracy parameter
			if (len(contourPolygon) == 4) and (area > maxArea):
				sudokuSquare = contourPolygon
				maxArea = area

	if sudokuSquare is None:
		print 'Sudoku grid not detected.'
		sys.exit(1)

	# order sudoku square points from top-left corner to bottom-left corner, clockwise
	sudokuSquare = np.squeeze(sudokuSquare)
	orderedSudokuSquare = np.zeros((4,2), dtype='float32')
	xySum = sudokuSquare.sum(axis=1)
	xyDiff = np.diff(sudokuSquare, axis=1)
	orderedSudokuSquare[0] = sudokuSquare[np.argmin(xySum)]
	orderedSudokuSquare[1] = sudokuSquare[np.argmax(xyDiff)]
	orderedSudokuSquare[2] = sudokuSquare[np.argmax(xySum)]
	orderedSudokuSquare[3] = sudokuSquare[np.argmin(xyDiff)]

	# deskew and straighten processedImage
	perspectiveMatrix = cv2.getPerspectiveTransform(np.float32(orderedSudokuSquare), np.float32([[0,0], [0,PROCESS_SQUARE_SIZE], [PROCESS_SQUARE_SIZE,PROCESS_SQUARE_SIZE], [PROCESS_SQUARE_SIZE,0]]))
	deskewedImage = cv2.warpPerspective(processedImage, perspectiveMatrix, (PROCESS_SQUARE_SIZE,PROCESS_SQUARE_SIZE))

	# slice image into 81 blocks, crop borders
	cells = np.array([np.hsplit(row, 9) for row in np.vsplit(deskewedImage, 9)])
	cells = cells.reshape(81, PROCESS_SQUARE_SIZE//9, PROCESS_SQUARE_SIZE//9)
	cells = [cell[CROP_PIXELS:(PROCESS_SQUARE_SIZE//9 - CROP_PIXELS), CROP_PIXELS:(PROCESS_SQUARE_SIZE//9 - CROP_PIXELS)] for cell in cells]

	# process each cell - if the cell has a digit (largest contour area exceeds threshold area), then mark cell for training
	labels = []
	samples = []
	for i in range(81):
		cell = cells[i]
		contours, hierarchy = cv2.findContours(cell.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		if len(contours) > 0:
			largestContour = contours[np.argmax(map(cv2.contourArea, contours))]
			if cv2.contourArea(largestContour) >= DIGIT_MIN_AREA:
				cv2.imshow('What digit is this?', cell)
				label = cv2.waitKey(0)-48
				if (label >= 1) and (label <= 9):
					labels.append(label)
					samples.append(cell)
				elif (label == 27):
					break

	cv2.imshow('Acquired data', mosaic(25, samples))
	print labels

	cv2.waitKey(0)

	np.save('data/samples_sudoku' + iteration, samples)
	np.save('data/labels_sudoku' + iteration, labels)
	print 'Data #' + iteration + ' saved'

	# exit
	cv2.destroyAllWindows()

