import numpy as np
import config
import pickle

class GestureRecognizer(object):
    def __init__(self):
        self.gesture_library = np.empty((0, config.MAX_GESTURE_LENGTH * 2))
        self.gesture_names = []

    def register_gesture(self, gesture_deltas, gesture_name):
        self.gesture_names.append(gesture_name)
        temp = np.asarray(gesture_deltas).reshape((1, -1))
        self.gesture_library = np.vstack((self.gesture_library, temp))

    def save_gestures(self, filename):
        with open(filename, "w") as of:
            pickle.dump((self.gesture_names, self.gesture_library), of, pickle.HIGHEST_PROTOCOL)

    def load_gestures(self, filename):
        with open(filename, "r") as f:
            temp = pickle.load(f)
        self.gesture_names = temp[0]
        self.gesture_library = temp[1]

    def identify_gesture(self, gesture_deltas):
        # TODO: find the closest gesture using MSE
        temp = np.asarray(gesture_deltas).reshape((1, -1))
        mse = ((self.gesture_library - temp) ** 2).mean(axis = 1)
        closest_index = np.argmin(mse)
        return self.gesture_names[closest_index]
