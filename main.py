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
FISH_TOLERANCE = 15
cast = True
fishing_game_not_detected_counter = 0

sct = mss.mss()
exclamation = cv2.imread('images/exclamation.png', cv2.IMREAD_GRAYSCALE)
top_of_bar = cv2.imread('images/top_of_bar.png', cv2.IMREAD_GRAYSCALE)
bottom_of_bar = cv2.imread('images/bottom_of_bar.png', cv2.IMREAD_GRAYSCALE)
fish = cv2.imread('images/fish.png', cv2.IMREAD_GRAYSCALE)

fish_h, fish_w = fish.shape

def accept_item():
  time.sleep(1)
  pyautogui.mouseDown()
  time.sleep(0.1)
  pyautogui.mouseUp()

def steady():
  pyautogui.mouseDown()
  time.sleep(0.1)
  pyautogui.mouseUp()
  time.sleep(0.02)

def small_up():
  pyautogui.mouseDown()
  time.sleep(0.125)
  pyautogui.mouseUp()
  time.sleep(0.05)

def medium_up():
  pyautogui.mouseDown()
  time.sleep(0.18)
  pyautogui.mouseUp()
  time.sleep(0.02)

def small_down():
  pyautogui.mouseDown()
  time.sleep(0.1)
  pyautogui.mouseUp()
  time.sleep(0.05)

def medium_down():
  pyautogui.mouseDown()
  time.sleep(0.1)
  pyautogui.mouseUp()
  time.sleep(0.075)

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

def do_fishing_minigame():
  while True:
    img = np.array(sct.grab(BAR_BOX))
    frame = img[:, :, :3]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    res_top = cv2.matchTemplate(gray, top_of_bar, cv2.TM_CCOEFF_NORMED)
    res_bottom = cv2.matchTemplate(gray, bottom_of_bar, cv2.TM_CCOEFF_NORMED)
    res_fish = cv2.matchTemplate(gray, fish, cv2.TM_CCOEFF_NORMED)

    _, val_top, _, loc_top = cv2.minMaxLoc(res_top)
    _, val_bottom, _, loc_bottom = cv2.minMaxLoc(res_bottom)
    _, val_fish, _, loc_fish = cv2.minMaxLoc(res_fish)

    if (val_top >= BAR_CONFIDENCE and val_fish >= FISH_CONFIDENCE) or (val_bottom >= BAR_CONFIDENCE and val_fish >= FISH_CONFIDENCE):
      fishing_game_not_detected_counter = 0
      # print(f"fishing not detection counter: {fishing_game_not_detected_counter}")
      if val_top:
        top_y = loc_top[1] 
      if val_bottom:
        btm_y = loc_bottom[1]
      fish_y = loc_fish[1]
      fish_center_y = loc_fish[1] + (fish_h / 2)
      bar_center_y = (loc_top[1] + loc_bottom[1]) / 2
      distance = fish_center_y - bar_center_y

      if top_y < fish_y < btm_y:
        if abs(distance) <= FISH_TOLERANCE:
          print("steady")
          steady()
        elif distance < 0:
          print("small up")
          small_up()
        else:
          print("small down")
          small_down()
      elif fish_y < btm_y:
        print("medium up")
        medium_up()
      elif top_y < fish_y:
        print("medium down")
        medium_down()
      else:
        print(f"WARNING: Fish ({fish_y}) is OUTSIDE!")
        # todo implement logic
    else:
      print(f"fishing game not detected")
      fishing_game_not_detected_counter += 1
      if fishing_game_not_detected_counter >= 7:
        return False
      # print(f"fishing not detected counter: {fishing_game_not_detected_counter}")

    time.sleep(0.01)

def check_if_minigame():
  img = np.array(sct.grab(BAR_BOX))
  frame = img[:, :, :3]
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

  res_fish = cv2.matchTemplate(gray, fish, cv2.TM_CCOEFF_NORMED)
  _, val_fish, _, loc_fish = cv2.minMaxLoc(res_fish)
  if val_fish >= FISH_CONFIDENCE:
    print("fishing game detected")
    return True
  else:
    print("fishing game not detected")
    return False

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
  print("casting rod")
  cast_rod()

  if watch_for_bite():
    print("hook fish")
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.mouseUp()

    # if its the minigame, do minigame, else cast again
    # wait for a certain amount of time until the minigame pops up
    time.sleep(1.3)
    if check_if_minigame():
      # print("todo fishing game logic")
      if do_fishing_minigame():
        # wait an additional few seconds to reel in fish
        print("accepting fish")
        time.sleep(2)
        accept_item()
    else:
      # accept the item
      accept_item()