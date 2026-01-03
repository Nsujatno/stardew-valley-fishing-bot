import cv2
import mss
import numpy as np
import pyautogui
import time
import win32gui
import os

title = "Stardew Valley"
hwnd = win32gui.FindWindow(None, title)
left, top, right, bottom = win32gui.GetWindowRect(hwnd)  # window coords[web:94]

print(left, right, top, bottom)

win_w = right - left
win_h = bottom - top
BOX_SIZE = 300

WATCH_BOX = {
  "left": left + int((win_w - BOX_SIZE) / 2),
  "top":  top  + int((win_h - BOX_SIZE) / 2),
  "width": BOX_SIZE,
  "height": BOX_SIZE,
}

BAR_BOX = {
  "left": left + int(win_w / 5),
  "top": top,
  "width": win_w - (int(win_w / 5) * 2),
  "height": win_h
}
print(WATCH_BOX)

CONFIDENCE = 0.7
BAR_CONFIDENCE = 0.9
FISH_CONFIDENCE = 0.7
cast = True

sct = mss.mss()
exclamation = cv2.imread('images/exclamation.png', cv2.IMREAD_GRAYSCALE)
top_of_bar = cv2.imread('images/top_of_bar.png', cv2.IMREAD_GRAYSCALE)
bottom_of_bar = cv2.imread('images/bottom_of_bar.png', cv2.IMREAD_GRAYSCALE)
fish = cv2.imread('images/fish.png', cv2.IMREAD_GRAYSCALE)

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

def watch_for_fish_and_bar():
  while True:
    img = np.array(sct.grab(BAR_BOX))
    frame = img[:, :, :3]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray, top_of_bar, cv2.TM_CCOEFF_NORMED)
    res2 = cv2.matchTemplate(gray, bottom_of_bar, cv2.TM_CCOEFF_NORMED)
    res3 = cv2.matchTemplate(gray, fish, cv2.TM_CCOEFF_NORMED)

    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    _, max_val_2, _, max_loc_2 = cv2.minMaxLoc(res2)
    _, max_val_3, _, max_loc_3 = cv2.minMaxLoc(res3)

    if max_val >= BAR_CONFIDENCE and max_val_2 >= BAR_CONFIDENCE and max_val_3 >= FISH_CONFIDENCE:
      top_y = max_loc[1] 
      btm_y = max_loc_2[1]
      fish_y = max_loc_3[1]

      if top_y < fish_y < btm_y:
        print(f"SAFE: Fish ({fish_y}) is inside bar ({top_y} - {btm_y})")
      else:
        print(f"WARNING: Fish ({fish_y}) is OUTSIDE!")
    else:
      print(f"fishing game not detected")

    time.sleep(0.01)

# helper function to determine boxes
def get_rel_coords():
  while True:
      # Get current absolute mouse position
      mouse_x, mouse_y = pyautogui.position()
      
      # Calculate relative position inside the window
      rel_x = mouse_x - left
      rel_y = mouse_y - top
      
      # Clear console for clean reading (Windows)
      os.system('cls') 
      
      print(f"Window Location: ({left}, {top})")
      print(f"Mouse Absolute:  ({mouse_x}, {mouse_y})")
      print("-" * 30)
      print(f"REL OFFSET X: {rel_x}") 
      print(f"REL OFFSET Y: {rel_y}")
      
      time.sleep(0.1)

print("starting in 5 seconds")
time.sleep(5)

while cast:
  # cast_rod()

  # if watch_for_bite():
  #   print("hook fish")
  #   pyautogui.mouseDown()
  #   time.sleep(0.1)
  #   pyautogui.mouseUp()
  #   cast = False

  # print("watching for bar")
  # if watch_for_bar():
  #   print("bar found")
  #   cast = False

  # if watch_for_fish():
  #   cast = False

  watch_for_fish_and_bar()