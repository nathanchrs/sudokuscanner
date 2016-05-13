#!/usr/bin/env python

'''
This module generates datasets for training handwritten digits (0-9) classifiers
from the TRAINING_IMAGE_FILE image (MNIST samples, from the OpenCV 2.4.12 Python 2 samples)
'''

import numpy as np
import cv2
from opencv_functions import prepKNN

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) # needed because ev3's brickman messes with relative paths - see https://github.com/ev3dev/ev3dev/issues/263

CELL_SIZE = 20
TRAINING_IMAGE_FILE = SCRIPT_DIRECTORY + '/data/handwritten_digits/handwritten_digits.png'
SAMPLES_FILE = SCRIPT_DIRECTORY + '/data/handwritten_digits/samples.npy'
LABELS_FILE = SCRIPT_DIRECTORY + '/data/handwritten_digits/labels.npy'

# load training image
print 'Loading training image from ' + TRAINING_IMAGE_FILE + '...'
trainingImage = cv2.imread(TRAINING_IMAGE_FILE, cv2.IMREAD_GRAYSCALE)

# split training image
imageHeight, imageWidth = trainingImage.shape[:2]
samples = [np.hsplit(row, imageWidth//CELL_SIZE) for row in np.vsplit(trainingImage, imageHeight//CELL_SIZE)]
samples = prepKNN(samples, CELL_SIZE, 'none')

# generate labels corresponding to the training images
labels = np.repeat(np.arange(10), len(samples)//10)

# save data
np.save(SAMPLES_FILE, samples)
np.save(LABELS_FILE, labels)
print 'Data for handwritten_digits saved.'
