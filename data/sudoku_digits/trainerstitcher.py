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

