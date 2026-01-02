import cv2
import mss
import numpy as np
import pyautogui
import time
import win32gui

title = "Stardew Valley"
hwnd = win32gui.FindWindow(None, title)
left, top, right, bottom = win32gui.GetWindowRect(hwnd)  # window coords[web:94]

win_w = right - left
win_h = bottom - top
BOX_SIZE = 300

WATCH_BOX = {
  "left": left + int((win_w - BOX_SIZE) / 2),
  "top":  top  + int((win_h - BOX_SIZE) / 2),
  "width": BOX_SIZE,
  "height": BOX_SIZE,
}
print(WATCH_BOX)

CONFIDENCE = 0.75
cast = True

sct = mss.mss()
exclamation = cv2.imread('images/exclamation.png', cv2.IMREAD_GRAYSCALE)

def cast_rod():
  print("Casting rod...")
  pyautogui.mouseDown()
  time.sleep(0.95)
  pyautogui.mouseUp()

def watch_for_bite():
  print("watching for bite")
  while True:
    img = np.array(sct.grab(WATCH_BOX))
    frame = img[:, :, :3]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray, exclamation, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    if max_val >= CONFIDENCE:
      return True

    time.sleep(0.01)

print("starting in 5 seconds")
time.sleep(5)

while cast:
  cast_rod()

  if watch_for_bite():
    print("hook fish")
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.mouseUp()
    cast = False