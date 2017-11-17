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
MAX_COLUMN_SPAN = 6
BACKGROUND_COLOR = "white"

def main():
    global status_text, register_text, savefile_text
    root = Tk(className = "Gesture Input")
    # Current status
    status_text = StringVar()
    status_box = Label(root, textvariable = status_text)
    status_box.grid(row = 2, columnspan = MAX_COLUMN_SPAN)
    # Gesture name Text Entry box.
    register_text = StringVar()
    register_textbox = Entry(root, textvariable = register_text)
    register_textbox.grid(row = 1, column = 0)
    # Save file name Text Entry box.
    savefile_text = StringVar()
    savefile_textbox = Entry(root, textvariable = savefile_text)
    savefile_textbox.grid(row = 1, column = 1)
    # Buttons
    register_button = Button(root, text = "Register", bg = BACKGROUND_COLOR, command = lambda: process_gesture(drawing_area))
    register_button.grid(row = 1, column = 2)
    save_button = Button(root, text = "Save", bg = BACKGROUND_COLOR, command = save_gestures)
    save_button.grid(row = 1, column = 3)
    clear_button = Button(root, text = "Clear", bg = BACKGROUND_COLOR, command = lambda: reset_grid(drawing_area))
    clear_button.grid(row = 1, column = 4)
    print_java_button = Button(root, text = "Print Java", bg = BACKGROUND_COLOR, command = print_java)
    print_java_button.grid(row = 1, column = 5)
    # Drawing area
    drawing_area = Canvas(root, width = INPUT_PANEL_WIDTH, height = INPUT_PANEL_HEIGHT, bg = BACKGROUND_COLOR)
    drawing_area.grid(row = 0, column = 0, columnspan = MAX_COLUMN_SPAN)
    reset_grid(drawing_area)
    drawing_area.bind("<Motion>", motion)
    drawing_area.bind("<ButtonPress-1>", b1down)
    drawing_area.bind("<ButtonRelease-1>", b1up)
    # Start!
    status_text.set("Program Started")
    register_text.set("LRSwipe")
    savefile_text.set("Gestures.pkl")
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

def process_gesture(drawing_area):
    global gesture, register_text, status_text, recognizer
    previous_point = locate_point(gesture[0])
    # gesture_deltas = [(0, 0)] * config.MAX_GESTURE_LENGTH
    gesture_deltas = []
    index = 0
    for point in gesture:
        if (index >= config.MAX_GESTURE_LENGTH):
            status_text.set("Could not register - Gesture too long")
            return
        downsampled_point = locate_point(point)
        # Add this square if it hasn't shown up before.
        if (downsampled_point != previous_point):
            gesture_deltas.append((downsampled_point[0] - previous_point[0], downsampled_point[1] - previous_point[1]))
            index += 1
            previous_point = downsampled_point
    # Display status
    status_text.set("Registering %r under %r" % (gesture_deltas[0:index], register_text.get()))
    recognizer.register_gesture(gesture_deltas, register_text.get())
    recognizer.draw_interpolated(drawing_area, starting_point = locate_point(gesture[0]),
        gesture_deltas = gesture_deltas, WIDTH_SPACING = WIDTH_SPACING, HEIGHT_SPACING = HEIGHT_SPACING)

def save_gestures():
    global savefile_text, recognizer, status_text
    status_text.set("Saving gestures to %r" % savefile_text.get())
    recognizer.save_gestures(savefile_text.get())


def print_java():
    global recognizer
    recognizer.dump_java_gesture_list()


if __name__ == "__main__":
    main()
