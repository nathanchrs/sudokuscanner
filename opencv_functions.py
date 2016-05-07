#!/usr/bin/env python

'''
This module contais some common routines used by other samples.
Code taken from OpenCV 2.4.12 Python 2 samples (common.py, digits.py)
'''

import numpy as np
import cv2
import itertools as it
from numpy.linalg import norm

def grouper(n, iterable, fillvalue=None):
    '''grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx'''
    args = [iter(iterable)] * n
    return it.izip_longest(fillvalue=fillvalue, *args)

def mosaic(w, imgs):
    '''Make a grid from images.

    w    -- number of grid columns
    imgs -- images (must have same size and format)
    '''
    imgs = iter(imgs)
    img0 = imgs.next()
    pad = np.zeros_like(img0)
    imgs = it.chain([img0], imgs)
    rows = grouper(w, imgs, pad)
    return np.vstack(map(np.hstack, rows))

def deskew(img, cellSize):
    '''Deskews each sample image.'''
    m = cv2.moments(img)
    if abs(m['mu02']) < 1e-2:
        return img.copy()
    skew = m['mu11']/m['mu02']
    M = np.float32([[1, skew, -0.5*cellSize*skew], [0, 1, 0]])
    img = cv2.warpAffine(img, M, (cellSize, cellSize), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
    return img

def preprocess_simple(digits, cellSize):
    '''Flattens sample images and scales its pixel values.'''
    return np.float32(digits).reshape(-1, cellSize*cellSize) / 255.0

def preprocess_hog(digits, cellSize):
    '''Computes histogram-of-gradients for each sample image.'''
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

def prepKNN(samples, cellSize):
    '''Applies deskewing and histogram-of-gradients preprocessing to sample images.'''
    samples = np.float32(samples).reshape(-1, cellSize, cellSize)
    deskewedSamples = [deskew(sample, cellSize) for sample in samples]
    return preprocess_hog(deskewedSamples, cellSize)