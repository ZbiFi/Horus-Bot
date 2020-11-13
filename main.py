import random

import cv2
import imutils as imutils
import numpy as np
import win32api
import win32con
from PIL import ImageGrab
from ctypes import windll
import win32gui
from win32gui import GetWindowRect
import win32ui
import pytesseract
from PIL import Image
from skimage.measure import compare_ssim
import time
import wmi

# Detect the window with Tetris game
windows_list = []
toplist = []
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
# Players positions + status (0 - no player 1 - player in game)
players_status_map = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
# Statuses: iresolve, fate, resources, melee, range, strategy
players_stats_map = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
# board width
map_width = 7
# board height
map_height = 7

c = wmi.WMI()

def enum_win(hwnd, result):
    win_text = win32gui.GetWindowText(hwnd)
    windows_list.append((hwnd, win_text))

def main ():

    offsetx = 0
    offsety = 0
    win_width = 0
    win_height = 0
    player_turn = 0
    win32gui.EnumWindows(enum_win, toplist)
    # Game handle
    pid = 0
    pid = win32gui.FindWindow(None, 'Talisman : The Horus Heresy')

    while True:

        position = win32gui.GetWindowRect(pid)
        offsetx, offsety, win_width, win_height = GetWindowRect(pid)
        background_screenshot(pid, win_width - offsetx, win_height - offsety)

        #load_player_stats()
        #print(players_stats_map)

        wait = cv2.waitKey(25)
        if wait == 27:
            break

        #time.sleep(0.5)

def background_screenshot(hwnd, width, height):
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(width, height) , dcObj, (0,0), win32con.SRCCOPY)
    dataBitMap.SaveBitmapFile(cDC, 'ssmanipulations/screenshot.bmp')
    img = cv2.imread('ssmanipulations/screenshot.bmp', cv2.COLOR_BGR2GRAY)
    cv2.imshow("Screen", img)
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())


def scroll_back (pid):

    win32api.SendMessage(pid,  win32con.MOUSE_WHEELED, (win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)))
    time.sleep(0.5)

def press_space (pid):

    win32api.SendMessage(pid, win32con.WM_KEYDOWN, win32con.VK_SPACE)
    time.sleep(0.5)
    win32api.SendMessage(pid, win32con.WM_KEYUP, win32con.VK_SPACE)

def check_stats(stat,row_2,column_2):

    im = Image.open(r'ssmanipulations/screenshot.bmp')
    #stat = 3
    #row_2 = 0
    #column_2 = 1

    #stat = random.randint(0, 5)
    #row_2 = random.randint(0, 1)
    #column_2 = random.randint(0, 1)

    left = 12 + (1891*column_2)
    top = 79 + (stat*35-(0.25*stat)) + (297 * row_2)
    right = 32 + (1891*column_2)
    bottom = 99 + (stat*35-(0.25*stat)) + (297 * row_2)

    # Cropped image of above dimension
    # (It will not change orginal image)
    im1 = im.crop((left, top, right, bottom))

    # Shows the image in image viewer
    #im1.show()

    filename = 'ssmanipulations/' + 'temp_stat' + '.jpg'
    im1 = im1.save(filename)

    return compare(filename)

def compare (filename):

    template_list = ['0_blue', '1_blue', '2_blue', '3_blue', '4_blue', '5_blue', '0_red', '1_red', '2_red', '3_red', '4_red', '5_red']
    value_list = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]
    best_number = 0
    best_hit = 0
    i = 0

    while i < len(template_list):
        imageA = cv2.imread('templates/' + template_list[i] + '.jpg')
        imageB = cv2.imread(filename)
        # convert the images to grayscale
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        (score, diff) = compare_ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")
        if score > best_number:
            best_number = score
            best_hit = i
        i += 1

    # print("Best SSIM: {}".format(best_number) + ' ' + str(value_list[best_hit]))

    return value_list[best_hit]

def load_player_stats ():

    row_2 = 0
    column_2 = 0

    for player_number in range (4):
        for stat_number in range(6):
            if player_number == 0:
                row_2 = 0
                column_2 = 0
            if player_number == 1:
                row_2 = 0
                column_2 = 1
            if player_number == 2:
                row_2 = 1
                column_2 = 0
            if player_number == 3:
                row_2 = 1
                column_2 = 1

            #print (str(player_number) + ' ' + str(stat_number))
            players_stats_map [player_number][stat_number] = check_stats(stat_number,row_2,column_2)


main()
#check_stats()
#compare()
#load_player_stats()
print(players_stats_map)