# USAGE
# python solve_sudoku_puzzle.py --model output/digit_classifier.h5 --image sudoku_puzzle.jpg

# import the necessary packages
from pyimagesearch.sudoku import extract_digit
from pyimagesearch.sudoku import find_puzzle
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from sudoku import Sudoku
from sudokuu import solution
import numpy as np
import argparse
import imutils
import cv2
import copy

image_path="2-1.jpg"
model_path="output/mm2.h5"
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=False,
	help="path to trained digit classifier")
ap.add_argument("-i", "--image", required=False,
	help="path to input sudoku puzzle image")
ap.add_argument("-d", "--debug", type=int, default=-1,
	help="whether or not we are visualizing each step of the pipeline")
args = vars(ap.parse_args())

# load the digit classifier from disk
print("[INFO] loading digit classifier...")
#model = load_model(args["model"])
model = load_model(model_path)

# load the input image from disk and resize it
print("[INFO] processing image...")
#image = cv2.imread(args["image"])
image = cv2.imread(image_path)
image = imutils.resize(image, width=600)

# find the puzzle in the image and then
(puzzleImage, warped) = find_puzzle(image, debug=args["debug"] > 0)

# initialize our 9x9 sudoku board
board = np.zeros((9, 9), dtype="int")

# a sudoku puzzle is a 9x9 grid (81 individual cells), so we can
# infer the location of each cell by dividing the warped image
# into a 9x9 grid
stepX = warped.shape[1] // 9
stepY = warped.shape[0] // 9

# initialize a list to store the (x, y)-coordinates of each cell
# location
cellLocs = []

# loop over the grid locations
for y in range(0, 9):
	# initialize the current list of cell locations
	row = []

	for x in range(0, 9):
		# compute the starting and ending (x, y)-coordinates of the
		# current cell
		startX = x * stepX
		startY = y * stepY
		endX = (x + 1) * stepX
		endY = (y + 1) * stepY

		# add the (x, y)-coordinates to our cell locations list
		row.append((startX, startY, endX, endY))

		# crop the cell from the warped transform image and then
		# extract the digit from the cell
		cell = warped[startY:endY, startX:endX]
		digit = extract_digit(cell, debug=args["debug"] > 0)

		# verify that the digit is not empty
		if digit is not None:

			# resize the cell to 28x28 pixels and then prepare the
			# cell for classification
			roi = cv2.resize(digit, (28, 28))
			roi = roi.astype("float") / 255.0
			roi = img_to_array(roi)
			roi = np.expand_dims(roi, axis=0)

			# classify the digit and update the sudoku board with the
			# prediction
			pred = model.predict(roi).argmax(axis=1)[0]
			if pred>=10:
				pred=pred-9
			board[y, x] = pred

	# add the row to our cell locations
	cellLocs.append(row)

# construct a sudoku puzzle from the board
print("[INFO] OCR'd sudoku board:")
puzzle = Sudoku(3, 3, board=board.tolist())
puzzle.show()

# solve the sudoku puzzle
print("[INFO] solving sudoku puzzle...")
puz=board.tolist()
prob=copy.deepcopy(puz)
pu=solution(puz)
sol=pu.start()
print(sol)
#solution = puzzle.solve()
#solution.show_full()

# loop over the cell locations and board
for (cellRow, boardRow, solrow) in zip(cellLocs, prob, sol):
	# loop over individual cell in the row
	for (box, digit, big) in zip(cellRow, boardRow, solrow):
		# unpack the cell coordinates
		startX, startY, endX, endY = box

		# compute the coordinates of where the digit will be drawn
		# on the output puzzle image
		textX = int((endX - startX) * 0.33)
		textY = int((endY - startY) * -0.2)
		textX += startX
		textY += endY

		# draw the result digit on the sudoku puzzle image
		if digit == 0:
			cv2.putText(puzzleImage, str(big), (textX, textY),
				cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
		else:
			cv2.putText(puzzleImage, str(big), (textX, textY),
				cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

# show the output image
cv2.imshow("Sudoku Result", puzzleImage)
cv2.waitKey(0)