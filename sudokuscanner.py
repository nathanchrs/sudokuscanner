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

WEBCAM_NUMBER = 0
CROP_PIXELS = 4
CELL_SIZE = 20
PROCESS_SQUARE_SIZE = (CELL_SIZE + 2*CROP_PIXELS)*9
DIGIT_MIN_AREA = (CELL_SIZE*CELL_SIZE)//20
SAMPLES_FILE = 'data/samples_typeddigits.npy'
LABELS_FILE = 'data/labels_typeddigits.npy'
KNN_K = 6

def deskew(img):
    m = cv2.moments(img)
    if abs(m['mu02']) < 1e-2:
        return img.copy()
    skew = m['mu11']/m['mu02']
    M = np.float32([[1, skew, -0.5*CELL_SIZE*skew], [0, 1, 0]])
    img = cv2.warpAffine(img, M, (CELL_SIZE, CELL_SIZE), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
    return img

def preprocess_simple(digits):
    return np.float32(digits).reshape(-1, CELL_SIZE*CELL_SIZE) / 255.0

def preprocess_hog(digits):
    samples = []
    for img in digits:
        gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
        mag, ang = cv2.cartToPolar(gx, gy)
        bin_n = 16
        bin = np.int32(bin_n*ang/(2*np.pi))
        bin_cells = bin[:10,:10], bin[10:,:10], bin[:10,10:], bin[10:,10:]
        mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
        hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
        hist = np.hstack(hists)

        # transform to Hellinger kernel
        eps = 1e-7
        hist /= hist.sum() + eps
        hist = np.sqrt(hist)
        hist /= norm(hist) + eps

        samples.append(hist)
    return np.float32(samples)

def prepKNN(samples):
	samples = np.float32(samples).reshape(-1, CELL_SIZE, CELL_SIZE)
	deskewedSamples = map(deskew, samples)
	samples = preprocess_hog(deskewedSamples)
	return samples

if __name__ == '__main__':

	# capture an image from webcam
	cam = cv2.VideoCapture(WEBCAM_NUMBER)
	ret_val, inputImage = cam.read()
	if not ret_val:
		print 'Failed to read from webcam #' + str(WEBCAM_NUMBER)
		sys.exit(1)

	cv2.imshow('Input Image', inputImage)

	# pre-process image
	processedImage = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
	processedImage = cv2.GaussianBlur(processedImage, (5,5), 0)
	processedImage = cv2.adaptiveThreshold(processedImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)

	cv2.imshow('Thresholded Image', processedImage)

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

	# prepare and train KNN
	samples = np.load(SAMPLES_FILE)
	samples = prepKNN(samples)
	labels = np.load(LABELS_FILE).astype(int)
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
				retval, results, neighborResponses, dists = knn.find_nearest(prepKNN([cell]), KNN_K)
				sudoku[i] = int(results.ravel()[0])

	sudoku = np.array(sudoku)
	sudoku = sudoku.reshape(9,9)
	print sudoku

	# show the resulting image
	cv2.imshow('Deskewed Image', deskewedImage)

	cv2.waitKey(0)
			
	# exit
	cv2.destroyAllWindows()

