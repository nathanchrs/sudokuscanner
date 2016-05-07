#!/usr/bin/env python

'''
This module contains a solver for sudoku puzzles.
The sudoku grid format used by this module is a list of list (9x9) of integer.
A blank cell is denoted by 0.
'''

import sys
from copy import deepcopy

def getBoxIndex(row, col):
	'''Returns the box index of a cell (0-based).'''
	return 3*(row//3) + (col//3)

def getBoxCells(index):
	'''Returns an array of a box's cell coordinates.'''
	res = []
	for i in range(3):
		for j in range(3):
			res.append((i+3*(index//3),j+3*(index%3)))
	return res

def printGrid(sudoku):
	'''Prints a sudoku grid.'''
	for r in range(9):
		print sudoku[r]

def reduce(sudoku):
	'''
	Iteratively fills empty cells in the sudoku grid if there is only 1 digit possibility for that cell.
	Returns False if the given sudoku grid is found to be invalid.
	'''
	# Processes input digits, removes that digit from the row, column, and box available digit list
	available = [[range(1,10) for c in range(9)] for r in range(9)]
	for r in range(9):
		for c in range(9):
			if sudoku[r][c] > 0:
				if sudoku[r][c] in available[r][c]:
					available[r][c] = []
					for i in range(9):
						if sudoku[r][c] in available[i][c]:
							available[i][c].remove(sudoku[r][c])
						if sudoku[r][c] in available[r][i]:
							available[r][i].remove(sudoku[r][c])
					for i,j in getBoxCells(getBoxIndex(r,c)):
						if sudoku[r][c] in available[i][j]:
							available[i][j].remove(sudoku[r][c])
				else:
					return (False,[])
	# Finds a cell with only 1 possible digit and fills it with that digit, then repeat until no more such cells are found
	while True:
		added = False
		for r in range(9):
			for c in range(9):
				if (sudoku[r][c] == 0) and (len(available[r][c]) == 1):
					added = True
					sudoku[r][c] = available[r][c][0]
					for i in range(9):
						if sudoku[r][c] in available[i][c]:
							available[i][c].remove(sudoku[r][c])
						if sudoku[r][c] in available[r][i]:
							available[r][i].remove(sudoku[r][c])
					for i,j in getBoxCells(getBoxIndex(r,c)):
						if sudoku[r][c] in available[i][j]:
							available[i][j].remove(sudoku[r][c])
				elif (sudoku[r][c] == 0) and (len(available[r][c]) == 0):
					return (False, [])
		if not added:
			return (True, available)

def isValid(sudoku):
	'''Checks whether a sudoku grid is a valid sudoku puzzle.'''
	if len(sudoku) == 9:
		for r in range(9):
			if validInput and (len(sudoku[r]) == 9):
				for c in range(9):
					if sudoku[r][c] not in range(10):
						validInput = False
						break
			else:
				return False
		validReduce, reduceResult = reduce(sudoku)
		return validReduce
	else:
		return False

def solve(sudoku):
	'''Solves a sudoku puzzle using DFS.'''
	# Try to reduce the puzzle
	valid, available = reduce(sudoku)
	if not valid:
		return (False, [])

	# Check whether the puzzle is solved already
	solved = True
	for r in range(9):
		for c in range(9):
			if sudoku[r][c] == 0:
				solved = False
				break
	if solved:
		return (True, sudoku)

	# Finds a cell with the minimum number of possible digits
	minLength,tryRow,tryCol = (10,0,0)
	for r in range(9):
		for c in range(9):
			if (sudoku[r][c] == 0) and (len(available[r][c]) < minLength):
				minLength, tryRow, tryCol = (len(available[r][c]), r, c)

	# Recursively tries possible digits
	for i in available[tryRow][tryCol]:
		newSudoku = deepcopy(sudoku)
		newSudoku[tryRow][tryCol] = i
		res, solution = solve(newSudoku)
		if res:
			return (True, solution)
	return (False, [])


if __name__ == '__main__':

	# Input sudoku puzzle
	print 'Input sudoku puzzle (space-separated digits, indicate blanks using 0):'
	inputSudoku = [map(int, raw_input().split()) for r in range(9)]

	# Check input validity
	if not isValid(inputSudoku):
		print "Invalid sudoku puzzle input!"
		sys.exit()

	# Solve sudoku
	print 'Solving...'
	res, solvedSudoku = solve(inputSudoku)

	# Show solution
	if res:
		print 'Solution:'
		printGrid(solvedSudoku)
	else:
		print "No solution!"