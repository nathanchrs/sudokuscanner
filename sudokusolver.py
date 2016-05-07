# Sudoku Solver by nathanchrs
#
# References:
# http://norvig.com/sudoku.html
# http://www.math.cornell.edu/~mec/Summer2009/meerkamp/Site/Solving_any_Sudoku_II.html

import sys
from copy import deepcopy
from time import sleep

BLANK_CELL = 0;

# Returns the box index of a cell (0-based)

def getBoxIndex(row, col):
	return 3*(row//3) + (col//3)

# Returns an array of a box's cell coordinates

def getBoxCells(index):
	res = []
	for i in range(3):
		for j in range(3):
			res.append((i+3*(index//3),j+3*(index%3)))
	return res

# Prints a sudoku grid

def printGrid(sudoku):
	for r in range(9):
		print sudoku[r]


# Iteratively fills empty cells in the sudoku grid if there is only 1 digit possibility for that cell.
# Returns False if the given sudoku grid is found to be invalid.

def reduce(sudoku):
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
					
# Solve a sudoku puzzle using DFS

def solve(sudoku):
	valid, available = reduce(sudoku)
	if not valid:
		return (False, [])

	solved = True
	for r in range(9):
		for c in range(9):
			if sudoku[r][c] == 0:
				solved = False
				break
	if solved:
		return (True, sudoku)

	minLength,tryRow,tryCol = (10,0,0)
	for r in range(9):
		for c in range(9):
			if (sudoku[r][c] == 0) and (len(available[r][c]) < minLength):
				minLength, tryRow, tryCol = (len(available[r][c]), r, c)

	for i in available[tryRow][tryCol]:
		newSudoku = deepcopy(sudoku)
		newSudoku[tryRow][tryCol] = i
		res, solution = solve(newSudoku)
		if res:
			return (True, solution)
	return (False, [])

# Main program

if __name__ == '__main__':

	# Input sudoku puzzle

	print 'Input sudoku puzzle (space-separated digits, indicate blanks using 0):'
	inputSudoku = [map(int, raw_input().split()) for r in range(9)]

	# Check input validity

	if len(inputSudoku) == 9:
		validInput = True
		for r in range(9):
			if validInput and (len(inputSudoku[r]) == 9):
				for c in range(9):
					if inputSudoku[r][c] not in range(10):
						validInput = False
						break
			else:
				validInput = False
				break
	else:
		validInput = False

	# TODO: also count the number of digits, a digit must not occur more than 9 times except 0

	if not validInput:
		print "Invalid sudoku puzzle input, digits must be between 0-9, grid size 9x9"
		sys.exit()

	print inputSudoku

	res, solvedSudoku = solve(inputSudoku)

	if res:
		printGrid(solvedSudoku)
	else:
		print "No solution!"