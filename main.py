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
BAR_AT_BOTTOM_CONFIDENCE = 0.95
FISH_CONFIDENCE = 0.7
cast = True
fishing_game_not_detected_counter = 0

sct = mss.mss()
exclamation = cv2.imread('images/exclamation.png', cv2.IMREAD_GRAYSCALE)
top_of_bar = cv2.imread('images/top_of_bar.png', cv2.IMREAD_GRAYSCALE)
bottom_of_bar = cv2.imread('images/bottom_of_bar.png', cv2.IMREAD_GRAYSCALE)
fish = cv2.imread('images/fish.png', cv2.IMREAD_GRAYSCALE)
bar_at_bottom = cv2.imread('images/bar_at_bottom.png', cv2.IMREAD_GRAYSCALE)

fish_h, fish_w = fish.shape

def accept_item():
  time.sleep(1)
  pyautogui.mouseDown()
  time.sleep(0.1)
  pyautogui.mouseUp()

def move_bar(percentage, is_above):
  base_hold = 0.15
  base_wait = 0.01

  if is_above:
    hold_time = base_hold + (percentage * 0.3)
    if hold_time > 0.5: hold_time = 0.5

    pyautogui.mouseDown()
    time.sleep(hold_time)
    pyautogui.mouseUp()
    time.sleep(base_wait)
      
  else:
    brake_time = 0.06
    wait_time = base_wait + (percentage * 0.05)
    if wait_time > 1: wait_time = 1
    if wait_time == 1: brake_time = 0.2

    pyautogui.mouseDown()
    time.sleep(brake_time)
    pyautogui.mouseUp()
    time.sleep(wait_time)

def steady():
  pyautogui.mouseDown()
  time.sleep(0.15)
  pyautogui.mouseUp()
  time.sleep(0.01)

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

def get_initial_bar_height():
  print("Detecting initial bar height...")
  attempts = 0
  max_attempts = 10
  
  while attempts < max_attempts:
    img = np.array(sct.grab(BAR_BOX))
    frame = img[:, :, :3]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    res_top = cv2.matchTemplate(gray, top_of_bar, cv2.TM_CCOEFF_NORMED)
    res_bottom = cv2.matchTemplate(gray, bottom_of_bar, cv2.TM_CCOEFF_NORMED)

    _, val_top, _, loc_top = cv2.minMaxLoc(res_top)
    _, val_bottom, _, loc_bottom = cv2.minMaxLoc(res_bottom)

    if val_top >= BAR_CONFIDENCE and val_bottom >= BAR_CONFIDENCE:
      top_y = loc_top[1]
      btm_y = loc_bottom[1]
      bar_height = btm_y - top_y
      print(f"Bar height detected: {bar_height} pixels")
      return bar_height, top_y, btm_y
    
    attempts += 1
    time.sleep(0.05)
  
  print("Warning: Could not detect initial bar height, using default")
  return None, None, None

def do_fishing_minigame():
  initial_bar_height, initial_top_y, initial_btm_y = get_initial_bar_height()
  
  if initial_bar_height is None:
    print("Failed to get initial bar height, aborting minigame")
    return True
  
  fishing_game_not_detected_counter = 0
  while True:
    img = np.array(sct.grab(BAR_BOX))
    frame = img[:, :, :3]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    res_top = cv2.matchTemplate(gray, top_of_bar, cv2.TM_CCOEFF_NORMED)
    res_bottom = cv2.matchTemplate(gray, bottom_of_bar, cv2.TM_CCOEFF_NORMED)
    res_fish = cv2.matchTemplate(gray, fish, cv2.TM_CCOEFF_NORMED)
    res_bar_at_bottom = cv2.matchTemplate(gray, bar_at_bottom, cv2.TM_CCOEFF_NORMED)

    _, val_top, _, loc_top = cv2.minMaxLoc(res_top)
    _, val_bottom, _, loc_bottom = cv2.minMaxLoc(res_bottom)
    _, val_fish, _, loc_fish = cv2.minMaxLoc(res_fish)
    _, val_bar_at_bottom, _, _, = cv2.minMaxLoc(res_bar_at_bottom)

    if (val_top >= BAR_CONFIDENCE and val_fish >= FISH_CONFIDENCE) or (val_bottom >= BAR_CONFIDENCE and val_fish >= FISH_CONFIDENCE):
      fishing_game_not_detected_counter = 0

      if val_top >= BAR_CONFIDENCE and val_bottom >= BAR_CONFIDENCE:
        # Both visible - use actual positions
        top_y = loc_top[1]
        btm_y = loc_bottom[1]
      elif val_top >= BAR_CONFIDENCE:
        # Only top visible - fish must be covering bottom
        top_y = loc_top[1]
        btm_y = top_y + initial_bar_height
        print("(Bottom obscured by fish, using calculated position)")
      else:
        # Only bottom visible - fish must be covering top
        btm_y = loc_bottom[1]
        top_y = btm_y - initial_bar_height
        print("(Top obscured by fish, using calculated position)")
      
      fish_center_y = loc_fish[1] + (fish_h / 2)
      bar_center_y = (loc_top[1] + loc_bottom[1]) / 2
      
      distance = fish_center_y - bar_center_y
      distance_percent = abs(distance) / initial_bar_height

      fish_above = distance < 0

      if fish_center_y > bar_center_y and val_bar_at_bottom >= BAR_AT_BOTTOM_CONFIDENCE:
        print("fish is below middle, and bar is at bottom so don't do anything")
      elif distance_percent < 0.08:
        # Steady hovering
        print(f"STEADY ({distance_percent:.1%})")
        steady()
      else:
        # Dynamic movement
        direction = "UP" if fish_above else "DOWN"
        print(f"{direction} (dist: {distance_percent:.1%})")
        move_bar(distance_percent, fish_above)

    else:
      print(f"fishing game not detected")
      fishing_game_not_detected_counter += 1
      if fishing_game_not_detected_counter >= 7:
        # game is over
        return True
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
        # need additional logic to handle if didn't catch fish
        cast = False
        # print("accepting fish")
        # time.sleep(2)
        # accept_item()
        
    else:
      # accept the item
      accept_item()