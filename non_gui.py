import mss
import numpy as np
import time

# For Brightness
import ctypes
import platform
import wmi

minBrightness = 20
maxBrightness = 80
BrightnessFactor = 1
updateFreq = 0.5

prevBrightness = 0
prevRGB = (0, 0, 0)

# Changing Brigthness

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
        # Capture the entire screen
        monitor = sct.monitors[1]  # [1] is for the primary screen
        screenshot = sct.grab(monitor)

        # Convert the screenshot to a numpy array (height x width x channels)
        img = np.array(screenshot)

        # Compute the average RGB values
        # Ignore the alpha channel if present
        avg_color = np.mean(img[:, :, :3], axis=(0, 1))

        return tuple(avg_color.astype(int))


try:
    None
    while True:
        avg_rgb = get_average_color()
        if (prevRGB != avg_rgb):
            avg_brightness = (avg_rgb[0]+avg_rgb[1]+avg_rgb[2])/3
            avg_brightness = avg_brightness*100/255
            print(f"Average Screen Brightness: {avg_brightness}")

            # Configuring Target Brightness
            target_brightness = (100 - avg_brightness) * BrightnessFactor
            if (target_brightness < minBrightness):
                target_brightness = minBrightness
            if (target_brightness > maxBrightness):
                target_brightness = maxBrightness

        if (target_brightness != prevBrightness):
            set_brightness(target_brightness)  # Set brightness

        prevBrightness = target_brightness
        prevRGB = avg_rgb

        # Sleep for a small interval before next update
        time.sleep(updateFreq)  # Adjust update rate

except KeyboardInterrupt:
    print("\nProgram exited.")
