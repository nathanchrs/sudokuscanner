#!/usr/bin/env python

'''
Scans free-standing digits.
'''

import numpy as np
import cv2, sys
from opencv_functions import mosaic, prepKNN

GAUSSIAN_BLUR_RADIUS = 11 # must be odd
CELL_SIZE = 20
CELL_SPACING = 2
DIGIT_MIN_SIZE = 20
KNN_K = 6

def read(inputImage, dataset='handwritten_digits'):
	'''
	Processes inputImage to find digits.
	Returns (retval, digits, digitImages).
	retval will be True if digit(s) are found, False otherwise.
	digits will be returned as a list of integers.
	digitsImage will contain a list of images of each found digit, each CELL_SIZE x CELL_SIZE pixels large,
	in numpy float32 array format.
	'''
	assert (dataset=='sudoku_digits') or (dataset=='handwritten_digits') # safety check - dataset parameter will be used in file paths
	samplesFile = 'data/' + dataset + '/samples.npy'
	labelsFile = 'data/' + dataset + '/labels.npy'

	# pre-process image
	processedImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
	processedImage = cv2.GaussianBlur(processedImage, (GAUSSIAN_BLUR_RADIUS,GAUSSIAN_BLUR_RADIUS), 0)
	processedImage = cv2.adaptiveThreshold(processedImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)

	# find contours in image
	contours, hierarchy = cv2.findContours(processedImage.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# separate digits
	cells = []
	for contour in contours:
		x, y, width, height = cv2.boundingRect(contour)
		if (width > DIGIT_MIN_SIZE) and (height > DIGIT_MIN_SIZE):
			if width > height:
				y -= (width-height)//2
				height = width
			else:
				x -= (height-width)//2
				width = height
			x -= CELL_SPACING
			y -= CELL_SPACING
			height += CELL_SPACING*2
			width += CELL_SPACING*2
			perspectiveMatrix = cv2.getPerspectiveTransform(np.float32([[x,y], [x,y+height], [x+width,y+height], [x+width,y]]), np.float32([[0,0], [0,CELL_SIZE], [CELL_SIZE,CELL_SIZE], [CELL_SIZE,0]]))
			cell = cv2.warpPerspective(processedImage, perspectiveMatrix, (CELL_SIZE,CELL_SIZE))
			cells.append(cell)

	if len(cells) == 0:
		return (False, [], [])

	# prepare and train KNN
	samples = np.load(samplesFile)
	samples = prepKNN(samples, CELL_SIZE)
	labels = np.load(labelsFile).astype(int)
	knn = cv2.KNearest()
	knn.train(samples, labels)

	# process each cell - if the cell has a digit (largest contour area exceeds threshold area), then apply knn to cell
	digits = [0 for i in range(len(cells))]
	for i in range(len(cells)):
		retval, results, neighborResponses, dists = knn.find_nearest(prepKNN([cells[i]], CELL_SIZE), KNN_K)
		digits[i] = int(results.ravel()[0])

	return (True, digits, cells)


if __name__ == '__main__':

	WEBCAM_NUMBER = 0

	# capture an image from webcam
	print "Capturing digits image from webcam #" + str(WEBCAM_NUMBER) + "..."
	cam = cv2.VideoCapture(WEBCAM_NUMBER)
	retval, inputImage = cam.read()
	if not retval:
		print 'Failed to read from webcam #' + str(WEBCAM_NUMBER)
		sys.exit(1)

	# read digits from image
	retval, digits, digitImages = read(inputImage)
	if retval:
		print 'Found ' + str(len(digitImages)) + ' digit(s):'
		print digits
		cv2.imshow('Input Image', inputImage)
		cv2.imshow('Digit Images', mosaic(25, digitImages))
	else:
		print 'No digit found in input image.'
		cv2.imshow('Input Image', inputImage)

	print 'Press any key to exit...'
	cv2.waitKey(0)
	cv2.destroyAllWindows()

