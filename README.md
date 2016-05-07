# Sudoku Scanner

Program for an EV3 robot that reads a sudoku puzzle using a webcam and solves them.

By nathanchrs.

## Modules

- `sudokusolver`: sudoku puzzle checker and solver logic.
- `sudokucapture.py`: reads a sudoku puzzle from an image.
- `opencv_functions.py`: contains miscellaneous image processing functions from the OpenCV 2.4.12 Python 2 samples (`common.py` and `digits.py`).
- `digitcapture.py`: reads free-standing digits from an image (currently the image must be clean and only contain the numbers).

Sample usage can be found by running each module directly.

## Training Data

Training data for each dataset consists of 2 numpy `.npy` files:
- `samples.npy`: contains a numpy float32 array of 20x20 px images.
- `labels.npy`: contains a numpy array of integers corresponding to each image in the samples file.

These files are placed in the `data/[DATASET_NAME]/` directory.

Currently there are 2 available datasets:
- `sudoku_digits`: sans-serif 1-9 digits
- `handwritten_digits`: handwritten 0-9 digits, generated from MNIST samples (see Credits).

There are trainer programs, or programs used to generate datasets, in each dataset's directory.

## Credits

This project uses the following open source components:

- ev3dev - Debian Linux for LEGO MINDSTORMS EV3, license (GNU GPL v2): https://github.com/ev3dev/ev3dev/blob/master/LICENSE
- ev3dev Python language bindings
- OpenCV 2.4.12 - Open Source Computer Vision Library, license (3-clause BSD License): http://opencv.org/license.html

Handwritten digit training uses samples from MNIST: http://yann.lecun.com/exdb/mnist/

Sudoku digit samples uses sudoku puzzle images from Google Image Search.

## References

- http://opencvpython.blogspot.co.id/2012/06/sudoku-solver-part-2.html
- http://docs.opencv.org/3.1.0/da/d6e/tutorial_py_geometric_transformations.html#gsc.tab=0
- http://sudokugrab.blogspot.co.id/2009/07/how-does-it-all-work.html
- http://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example
- http://stackoverflow.com/questions/8076889/tutorial-on-opencv-simpleblobdetector
- http://norvig.com/sudoku.html
- http://www.math.cornell.edu/~mec/Summer2009/meerkamp/Site/Solving_any_Sudoku_II.html
- http://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html#gsc.tab=0