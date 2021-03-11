# USAGE
# python train_digit_classifier.py --model output/digit_classifier.h5

# import the necessary packages
# from pyimagesearch.models import SudokuNet
# from pyimagesearch.models import LeNet
from tf_model import LeNet
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.datasets import mnist
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import classification_report
import argparse
from image_process import merge_minist_EI339

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
	help="path to output model after training")
args = vars(ap.parse_args())

# initialize the initial learning rate, number of epochs to train
# for, and batch size
INIT_LR = 0.0015
EPOCHS = 20
BS = 128

# grab the MNIST dataset
# print("[INFO] accessing MNIST...")
# ((trainData, trainLabels), (testData, testLabels)) = mnist.load_data()
print("[INFO] accessing dataset...")
(trainData, trainLabels, testData, testLabels) = merge_minist_EI339()

# add a channel (i.e., grayscale) dimension to the digits
trainData = trainData.reshape((trainData.shape[0], 28, 28, 1))
testData = testData.reshape((testData.shape[0], 28, 28, 1))

# scale data to the range of [0, 1]
trainData = trainData.astype("float32") / 255.0
testData = testData.astype("float32") / 255.0

# convert the labels from integers to vectors
le = LabelBinarizer()
trainLabels = le.fit_transform(trainLabels)
testLabels = le.transform(testLabels)

# initialize the optimizer and model
print("[INFO] compiling model...")
opt = Adam(lr=INIT_LR)
# model = SudokuNet.build(width=28, height=28, depth=1, classes=10)
model = LeNet.build(width=28, height=28, depth=1, classes=20)
model.compile(loss="categorical_crossentropy", optimizer=opt,
	metrics=["accuracy"])

# train the network
print("[INFO] training network...")
H = model.fit(
	trainData, trainLabels,
	validation_data=(testData, testLabels),
	batch_size=BS,
	epochs=EPOCHS,
	verbose=1)
f=open("model.txt","w")
print(H.history,file=f)
f.close()

# evaluate the network
print("[INFO] evaluating network...")
predictions = model.predict(testData)
print(classification_report(
	testLabels.argmax(axis=1),
	predictions.argmax(axis=1),
	target_names=[str(x) for x in le.classes_]))

# serialize the model to disk
print("[INFO] serializing digit model...")
model.save(args["model"], save_format="h5")