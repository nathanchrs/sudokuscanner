#!/usr/bin/env python

'''
This module captures images from a webcam and processes them to find sudoku puzzles.
The sudoku grid format used by this module is a list of list (9x9) of integer.
A blank cell is denoted by 0.
'''

import numpy as np
import cv2, sys, os
from opencv_functions import prepKNN

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) # needed because ev3's brickman messes with relative paths - see https://github.com/ev3dev/ev3dev/issues/263

GAUSSIAN_BLUR_RADIUS = 5 # must be odd
CROP_PIXELS = 4
CELL_SIZE = 20
PROCESS_SQUARE_SIZE = (CELL_SIZE + 2*CROP_PIXELS)*9
DIGIT_MIN_AREA = (CELL_SIZE*CELL_SIZE)//20
KNN_K = 6

def read(inputImage, dataset='sudoku_digits', returnSplitImages=False):
	'''
	Processes inputImage to find a sudoku puzzle.
	If returnSplitImages is True, it will return an array of cell images, otherwise it will return the whole sudoku image.
	Returns (retval, sudoku, processedImage, sudokuPoints).
	retval will be True if a sudoku puzzle is found, and False otherwise.
	sudokuPoints will be an array of 4 points (top-left to top-right, counter-clockwise) of the coordinates of the sudoku grid
	found in the image. Each point will be an array of 2 floats.
	The sudoku grid format used by this module is a list of list (9x9) of integer.
	A blank cell is denoted by 0.
	A processedImage with size PROCESS_SQUARE_SIZE x PROCESS_SQUARE_SIZE will be returned.
	'''
	assert (dataset=='sudoku_digits') or (dataset=='handwritten_digits') # safety check - dataset parameter will be used in file paths
	samplesFile = SCRIPT_DIRECTORY + '/data/' + dataset + '/samples.npy'
	labelsFile = SCRIPT_DIRECTORY + '/data/' + dataset + '/labels.npy'

	# pre-process image
	processedImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
	processedImage = cv2.GaussianBlur(processedImage, (GAUSSIAN_BLUR_RADIUS,GAUSSIAN_BLUR_RADIUS), 0)
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
		return (False, [], processedImage, [])

	# order sudoku square points from top-left corner to top-right corner, counter-clockwise
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

	# prepare and train KNN
	samples = np.load(samplesFile)
	samples = prepKNN(samples, CELL_SIZE)
	labels = np.load(labelsFile).astype(int)
	knn = cv2.KNearest()
	knn.train(samples, labels)

	# process each cell - if the cell has a digit (largest contour area exceeds threshold area), then apply knn to cell
	sudoku = [0 for i in range(81)]
	for i in range(81):
		cell = cells[i]
		contours, hierarchy = cv2.findContours(cell.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		if len(contours) > 0:
			largestContour = contours[np.argmax(map(cv2.contourArea, contours))]
			if cv2.contourArea(largestContour) >= DIGIT_MIN_AREA:
				# this cell has a digit, apply knn
				retval, results, neighborResponses, dists = knn.find_nearest(prepKNN([cell], CELL_SIZE), KNN_K)
				sudoku[i] = int(results.ravel()[0])

	sudoku = np.array(sudoku)
	sudoku = sudoku.reshape(9,9)
	if returnSplitImages:
		return (True, sudoku, samples, orderedSudokuSquare.tolist())
	else:
		return (True, sudoku, deskewedImage, orderedSudokuSquare.tolist())


if __name__ == '__main__':

	WEBCAM_NUMBER = 0

	# capture an image from webcam
	print "Capturing sudoku image from webcam #" + str(WEBCAM_NUMBER) + "..."
	cam = cv2.VideoCapture(WEBCAM_NUMBER)
	retval, inputImage = cam.read()
	if not retval:
		print 'Failed to read from webcam #' + str(WEBCAM_NUMBER)
		sys.exit(1)

	# read sudoku puzzle from image
	retval, sudoku, processedImage, pos = read(inputImage)
	if retval:
		print 'Found a sudoku puzzle:'
		print sudoku
		cv2.imshow('Input Image', inputImage)
		cv2.imshow('Processed Image', processedImage)
	else:
		print 'Sudoku puzzle not found in input image.'
		cv2.imshow('Input Image', inputImage)

	print 'Press any key to exit...'
	cv2.waitKey(0)
	cv2.destroyAllWindows()
