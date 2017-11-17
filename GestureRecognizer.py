import numpy as np
import math
import config
import pickle

class GestureRecognizer(object):
    def __init__(self):
        self.gesture_library = np.empty((0, config.MAX_GESTURE_LENGTH * 2), dtype = np.float)
        self.gesture_names = []

    def register_gesture(self, gesture_deltas, gesture_name):
        self.gesture_names.append(gesture_name)
        temp = np.asarray(self.interpolate(gesture_deltas), dtype = np.float).reshape((1, -1))
        self.gesture_library = np.vstack((self.gesture_library, temp))

    def save_gestures(self, filename):
        with open(filename, "w") as of:
            pickle.dump((self.gesture_names, self.gesture_library), of, pickle.HIGHEST_PROTOCOL)

    def dump_java_gesture_list(self):
        # Write out a Java compatible array
        print "private static int ROW_LENGTH = %d;" % config.ARRAY_WIDTH
        print "private static int MAX_GESTURE_LENGTH = %d;" % config.MAX_GESTURE_LENGTH
        print "private static int[][] GESTURE_LIBRARY = { "
        for row in self.gesture_library:
            print "{",
            for elem in row[:-1]:
                print "%f, " % elem,
            print "%f" % row[-1],
            print "},"
        print "};"
        print "private static String[] GESTURE_NAMES = {",
        for name in self.gesture_names[:-1]:
            print '"%s",' % name,
        print '"%s"' % self.gesture_names[-1],
        print "};"

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

    def draw_interpolated(self, drawing_area, starting_point, gesture_deltas, WIDTH_SPACING, HEIGHT_SPACING):
        # Create interpolated line
        interp = self.interpolate(gesture_deltas)
        current_point = ((starting_point[0] + 0.5) * WIDTH_SPACING, (starting_point[1] + 0.5) * HEIGHT_SPACING)
        # Scale according to degree of interpolation
        WIDTH_SPACING *= (len(gesture_deltas)) / float(config.MAX_GESTURE_LENGTH)
        HEIGHT_SPACING *= (len(gesture_deltas)) / float(config.MAX_GESTURE_LENGTH)
        if __debug__:
            print "Drawing interpolated gesture..."
            print "Starting point: %r" % (current_point, )
        for delta in interp:
            next_point = (current_point[0] + delta[0] * WIDTH_SPACING, current_point[1] + delta[1] * HEIGHT_SPACING)
            drawing_area.create_line(current_point[0], current_point[1], next_point[0], next_point[1], fill = "red")
            if __debug__:
                print "Plotting line from (%d, %d) to (%d, %d)" % (current_point[0], current_point[1], next_point[0], next_point[1])
            current_point = next_point

    def interpolate(self, gesture_deltas):
        step_size = (len(gesture_deltas) - 1) / float(config.MAX_GESTURE_LENGTH)
        current_step = 0.0
        interpolated = []
        if __debug__:
            print "Received gesture deltas of length %d: %r" % (len(gesture_deltas), gesture_deltas)
            print "Using a step size of %f" % step_size

        for i in xrange(config.MAX_GESTURE_LENGTH):
            # Points to interpolate
            left_val = gesture_deltas[int(math.floor(current_step))]
            right_val = gesture_deltas[int(math.ceil(current_step))]
            # Compute weights
            left_weight = (math.floor(current_step) + 1) - current_step
            right_weight = 1 - left_weight
            if __debug__:
                print "Computing step %f" % current_step
                print "Interpolating gesture_deltas[%d] = %r and gesture_deltas[%d] = %r" % (math.floor(current_step), left_val, math.ceil(current_step), right_val)
                print "Weights: %f and %f" % (left_weight, right_weight)
            interpolated.append(self.compute_interpolated_delta(left_val, right_val, left_weight, right_weight))
            current_step += step_size
        if __debug__:
            print "Interpolated deltas: %r" % interpolated
        return interpolated

    def compute_interpolated_delta(self, left_val, right_val, left_weight, right_weight):
        return (float(left_val[0] * left_weight + right_val[0] * right_weight), float(left_val[1] * left_weight + right_val[1] * right_weight))
