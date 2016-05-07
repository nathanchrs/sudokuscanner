# Sudoku Scanner by nathanchrs
# 
# References:
# http://opencvpython.blogspot.co.id/2012/06/sudoku-solver-part-2.html
# http://docs.opencv.org/3.1.0/da/d6e/tutorial_py_geometric_transformations.html#gsc.tab=0
# http://sudokugrab.blogspot.co.id/2009/07/how-does-it-all-work.html
# http://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example
# http://stackoverflow.com/questions/8076889/tutorial-on-opencv-simpleblobdetector
# OpenCV Python 2 Digits sample

import numpy as np
import cv2, sys
from numpy.linalg import norm
from common import mosaic

CELL_SIZE = 20
SAMPLES_FILE = 'data/samples_typeddigits'
LABELS_FILE = 'data/labels_typeddigits'
PUZZLE_COUNT = 20

if __name__ == '__main__':

	samples = np.array([])
	labels = np.array([])
	for iteration in range(1,PUZZLE_COUNT+1):
		samples = np.append(samples, np.load('data/samples_sudoku' + str(iteration) + '.npy'))
		labels = np.append(labels, np.load('data/labels_sudoku' + str(iteration) + '.npy'))

	samples = samples.reshape(-1, CELL_SIZE, CELL_SIZE)

	print labels
	cv2.imshow('Samples', mosaic(100, samples))
	cv2.waitKey(0)

	np.save(SAMPLES_FILE, samples)
	np.save(LABELS_FILE, labels)
	print 'Stitched training data saved.'

	# exit
	cv2.destroyAllWindows()

