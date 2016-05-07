#!/usr/bin/env python

'''
Scans free-standing digits.
'''


import numpy as np
import cv2, sys
from numpy.linalg import norm
from common import mosaic

WEBCAM_NUMBER = 0
CELL_SIZE = 20
CELL_SPACING = 2
DIGIT_MIN_SIZE = 20
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
	processedImage = cv2.GaussianBlur(processedImage, (11,11), 0)
	processedImage = cv2.adaptiveThreshold(processedImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 1)

	cv2.imshow('Thresholded Image', processedImage)

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
		print 'No contour detected.'
		sys.exit(1)

	# prepare and train KNN
	samples = np.load(SAMPLES_FILE)
	samples = prepKNN(samples)
	labels = np.load(LABELS_FILE).astype(int)
	knn = cv2.KNearest()
	knn.train(samples, labels)

	# process each cell - if the cell has a digit (largest contour area exceeds threshold area), then apply knn to cell
	digits = [0 for i in range(len(cells))]
	for i in range(len(cells)):
		retval, results, neighborResponses, dists = knn.find_nearest(prepKNN([cells[i]]), KNN_K)
		digits[i] = int(results.ravel()[0])

	print digits

	# show the resulting image
	cv2.imshow('Detected Digits', mosaic(10, cells))

	cv2.waitKey(0)
			
	# exit
	cv2.destroyAllWindows()

