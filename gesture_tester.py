from Tkinter import *
from GestureRecognizer import GestureRecognizer
import config
import pickle
import numpy as np

b1 = False
xold, yold = None, None
gesture = []
recognizer = GestureRecognizer()

INPUT_PANEL_WIDTH = 800
INPUT_PANEL_HEIGHT = 800
WIDTH_SPACING = INPUT_PANEL_WIDTH / config.ARRAY_WIDTH
HEIGHT_SPACING = INPUT_PANEL_HEIGHT / config.ARRAY_HEIGHT
# GUI Constants
MAX_COLUMN_SPAN = 4
BACKGROUND_COLOR = "white"

def main():
    global status_text, register_text, loadfile_text
    root = Tk(className = "Gesture Tester")
    # Current status
    status_text = StringVar()
    status_box = Label(root, textvariable = status_text)
    status_box.grid(row = 2, columnspan = MAX_COLUMN_SPAN)
    # Load file name Text Entry box.
    loadfile_text = StringVar()
    loadfile_textbox = Entry(root, textvariable = loadfile_text)
    loadfile_textbox.grid(row = 1, column = 0)
    # Buttons
    recognize_button = Button(root, text = "Recognize", bg = BACKGROUND_COLOR, command = process_gesture)
    recognize_button.grid(row = 1, column = 1)
    save_button = Button(root, text = "Load", bg = BACKGROUND_COLOR, command = load_gestures)
    save_button.grid(row = 1, column = 2)
    clear_button = Button(root, text = "Clear", bg = BACKGROUND_COLOR, command = lambda: reset_grid(drawing_area))
    clear_button.grid(row = 1, column = 3)
    # Drawing area
    drawing_area = Canvas(root, width = INPUT_PANEL_WIDTH, height = INPUT_PANEL_HEIGHT, bg = BACKGROUND_COLOR)
    drawing_area.grid(row = 0, column = 0, columnspan = MAX_COLUMN_SPAN)
    reset_grid(drawing_area)
    drawing_area.bind("<Motion>", motion)
    drawing_area.bind("<ButtonPress-1>", b1down)
    drawing_area.bind("<ButtonRelease-1>", b1up)
    # Start!
    status_text.set("Program Started")
    loadfile_text.set("Gestures.pkl")
    load_gestures()
    root.mainloop()

def b1down(event):
    global b1
    b1 = True

def b1up(event):
    global b1, xold, yold
    b1 = False
    xold = None
    yold = None

def motion(event):
    if b1:
        global xold, yold, gesture
        if xold is not None and yold is not None:
            event.widget.create_line(xold, yold, event.x, event.y, smooth=TRUE)
        if (event.x < INPUT_PANEL_WIDTH and event.y < INPUT_PANEL_HEIGHT):
            gesture.append((event.x, event.y))
        xold = event.x
        yold = event.y

def reset_grid(drawing_area):
    global gesture, status_text
    drawing_area.delete("all")
    gesture = []
    # Create grid
    for i in range(config.ARRAY_WIDTH):
        drawing_area.create_line(WIDTH_SPACING * i, 0, WIDTH_SPACING * i, INPUT_PANEL_HEIGHT)
    for i in range(config.ARRAY_HEIGHT):
        drawing_area.create_line(0, HEIGHT_SPACING * i, INPUT_PANEL_WIDTH, HEIGHT_SPACING * i)
    status_text.set("Grid Cleared")

def locate_point(point):
    return (point[0] / WIDTH_SPACING, point[1] / HEIGHT_SPACING)

def process_gesture():
    global gesture, register_text, status_text, recognizer
    previous_point = locate_point(gesture[0])
    gesture_deltas = [(0, 0)] * config.MAX_GESTURE_LENGTH
    index = 0
    for point in gesture:
        if (index >= config.MAX_GESTURE_LENGTH):
            status_text.set("Could not recognize - Gesture too long")
            return
        downsampled_point = locate_point(point)
        # Add this square if it hasn't shown up before.
        if (downsampled_point != previous_point):
            gesture_deltas[index] = (downsampled_point[0] - previous_point[0], downsampled_point[1] - previous_point[1])
            index += 1
            previous_point = downsampled_point
    # Display status
    status_text.set("Recognized gesture as %r" % recognizer.identify_gesture(gesture_deltas))

def load_gestures():
    global loadfile_text, recognizer, status_text
    status_text.set("Loading gestures from %r" % loadfile_text.get())
    recognizer.load_gestures(loadfile_text.get())

if __name__ == "__main__":
    main()
