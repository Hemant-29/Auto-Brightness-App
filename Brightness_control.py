import threading
import mss
import numpy as np
import time
import ctypes
import platform
import wmi
import tkinter as tk
from tkinter import ttk

# Initial values
minBrightness = 40
maxBrightness = 70
BrightnessFactor = 0.85
updateFreq = 0.3

prevRGB = (0, 0, 0)
valueUpdated = False
running = True  # Control variable for running state

# WMI for brightness control
wmi_obj = wmi.WMI(namespace='wmi')
brightness_methods = wmi_obj.WmiMonitorBrightnessMethods()[0]


def set_brightness(level):
    if 0 <= level <= 100:
        brightness_methods.WmiSetBrightness(level, 0)
        print(f"Brightness set to {level}%")
    else:
        print("Brightness level must be between 0 and 100")


def get_average_color():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        avg_color = np.mean(img[:, :, :3], axis=(0, 1))
        return tuple(avg_color.astype(int))


def update_brightness():
    global valueUpdated
    global running, prevRGB
    avg_rgb = get_average_color()
    if (prevRGB != avg_rgb or valueUpdated) and running:
        avg_brightness = (avg_rgb[0] + avg_rgb[1] + avg_rgb[2]) / 3
        avg_brightness = int(avg_brightness * 100 / 255)

        print(f"Average Screen Brightness: {avg_brightness}")

        target_brightness = (100 - avg_brightness)
        if (target_brightness >= 50):
            target_brightness *= BrightnessFactor
        else:
            target_brightness *= (2 - BrightnessFactor)

        if target_brightness < minBrightness:
            target_brightness = minBrightness
        if target_brightness > maxBrightness:
            target_brightness = maxBrightness

        set_brightness(target_brightness)  # Set brightness

        prevRGB = avg_rgb
        valueUpdated = False

    # Schedule next update
    root.after(int(updateFreq * 1000), update_brightness)


def on_min_brightness_change(value):
    global valueUpdated
    valueUpdated = True

    global minBrightness
    minBrightness = int(float(value))
    try:
        min_brightness_label.config(text=f"{minBrightness}")
    except:
        None


def on_max_brightness_change(value):
    global valueUpdated
    valueUpdated = True

    global maxBrightness
    maxBrightness = int(float(value))
    try:
        max_brightness_label.config(text=f"{maxBrightness}")
    except:
        None


def on_brightness_factor_change(value):
    global valueUpdated
    valueUpdated = True

    global BrightnessFactor
    BrightnessFactor = float(value)
    try:
        brightness_factor_label.config(
            text=f"{BrightnessFactor:.1f}")
    except:
        None


def on_update_freq_change(value):
    global valueUpdated
    valueUpdated = True

    global updateFreq
    updateFreq = float(value)
    try:
        update_freq_label.config(text=f"{updateFreq:.1f} s")
    except:
        None

# Start/Stop toggle function


def toggle_running():
    global running
    running = not running
    if running:
        toggle_button.config(text="Pause")
    else:
        toggle_button.config(text="Resume")


# Tkinter GUI setup
root = tk.Tk()
root.title("Screen Brightness Control")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Min Brightness Slider
ttk.Label(frame, text="Min Brightness").grid(row=0, column=0, sticky=tk.W)
min_brightness_slider = ttk.Scale(
    frame, from_=0, to=100, orient=tk.HORIZONTAL, command=on_min_brightness_change)
min_brightness_slider.set(minBrightness)
min_brightness_slider.grid(row=0, column=1, sticky=(tk.W, tk.E))
min_brightness_label = ttk.Label(
    frame, text=f"{minBrightness}")
min_brightness_label.grid(row=0, column=2, sticky=tk.W)

# Max Brightness Slider
ttk.Label(frame, text="Max Brightness").grid(row=1, column=0, sticky=tk.W)
max_brightness_slider = ttk.Scale(
    frame, from_=0, to=100, orient=tk.HORIZONTAL, command=on_max_brightness_change)
max_brightness_slider.set(maxBrightness)
max_brightness_slider.grid(row=1, column=1, sticky=(tk.W, tk.E))
max_brightness_label = ttk.Label(
    frame, text=f"{maxBrightness}")
max_brightness_label.grid(row=1, column=2, sticky=tk.W)

# Brightness Factor Slider
ttk.Label(frame, text="Brightness Factor").grid(row=2, column=0, sticky=tk.W)
brightness_factor_slider = ttk.Scale(
    frame, from_=0, to=1, orient=tk.HORIZONTAL, command=on_brightness_factor_change)
brightness_factor_slider.set(BrightnessFactor)
brightness_factor_slider.grid(row=2, column=1, sticky=(tk.W, tk.E))
brightness_factor_label = ttk.Label(
    frame, text=f"{BrightnessFactor:.1f}")
brightness_factor_label.grid(row=2, column=2, sticky=tk.W)

# Update Frequency Slider
ttk.Label(frame, text="Update Frequency (s)").grid(
    row=3, column=0, sticky=tk.W)
update_freq_slider = ttk.Scale(
    frame, from_=0.1, to=2, orient=tk.HORIZONTAL, command=on_update_freq_change)
update_freq_slider.set(updateFreq)
update_freq_slider.grid(row=3, column=1, sticky=(tk.W, tk.E))
update_freq_label = ttk.Label(
    frame, text=f"{updateFreq:.1f} s")
update_freq_label.grid(row=3, column=2, sticky=tk.W)

# Button for Pause/Resume
toggle_button = tk.Button(root, text="Pause", command=toggle_running)
toggle_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Start the brightness update loop
root.after(int(updateFreq * 1000), update_brightness)

root.mainloop()
