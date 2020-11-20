
import ctypes
import math

import cv2

import win32api
import win32con
import win32process
import numpy as np
import win32gui
from scipy import spatial
from skimage import metrics
from win32gui import GetWindowRect
import win32ui
import pytesseract
from PIL import Image, ImageDraw
from skimage.measure import compare_ssim
import time
import wmi

# Detect the window with Tetris game
from win32process import ReadProcessMemory

windows_list = []
toplist = []
map_0_field_count = 24
map_1_field_count = 16
map_2_field_count = 8
map_3_field_count = 1

map_0 = ['Isstvann V', 'The Halo Starts', 'Caliban', 'The Rubicon Straits', 'Port Maw', 'The Ghoul Stars', 'Signus Prime', 'The Death of Reason', 'The Maelstorm', 'The Eastern Fringe', 'Tigrus', 'The Thirteen Realms', 'Macragge', 'Calth', 'Deliverance', 'The Charadon Sector', 'Prospero', 'The Golgothan Wastes', 'Nikaea', 'The Veiled Region', 'The Phall System', 'The Intergalactic Void', 'Lucius', 'The Isstvan Asteroid Range']
#cords [x1;y1;x2;y2]
map_0_cords = []
map_0_if_top = ['The Halo Starts', 'Caliban', 'The Rubicon Straits', 'Port Maw']
map_0_cords_if_top =[[334, 273, 540, 396],[584, 273, 818, 396],[883, 273, 1080, 396],[1090, 273, 1377, 396]]
map_1 = ['Isstvann III', 'Warp Storm', 'Eye of Terror', 'Warp Storm', 'Davin', 'The Dominion of Storms', 'Paramar', 'The Kayvas Belt', 'Tallarn', 'The Uhulis Sector', 'Luna', 'Cthonia', 'Titan', 'The Mandragoran Sector', 'Mars', 'The Stellar Wastes']
map_1_cords = []
map_2 = ['The Outer Palace', 'The Inner Palace', 'The Outer Palace', 'Damocles Startport', 'Arcus Orbital Plate', 'Spaceport Primus', 'Lemurya Orbital Plate', 'The Wastes']
map_2_cords = []
map_3 = ['The Final Battle']
map_3_cords = []
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
# Players positions (mapId, fieldId, status (0 - no player 1 - player in game)
players_status_map = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
# Statuses: iresolve, fate, resources, melee, range, strategy
players_stats_map_status = 0
players_stats_map = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
# board width
map_width = 7
# board height
map_height = 7

x_scale = 1
y_scale = 1

game_pid = 15024
steam_name_4_lett = "Kamo"
true_base_memory = 0
player_character = 'Roboute Guilliman'
c = wmi.WMI()
search_mode = 0

def enum_win(hwnd, result):
    win_text = win32gui.GetWindowText(hwnd)
    windows_list.append((hwnd, win_text))

def main ():

    global players_stats_map_status
    global true_base_memory
    global search_mode
    offsetx = 0
    offsety = 0
    found_player = 0
    win_width = 0
    win_height = 0
    player_turn = 0
    location_string = ""
    location = 0
    map_number = 0
    win32gui.EnumWindows(enum_win, toplist)
    # Game handle
    pid = 0
    pid = win32gui.FindWindow(None, 'Talisman : The Horus Heresy')
    true_base_memory = check_in_memory_for_user_data_and_get_true_base_memory(steam_name_4_lett, game_pid)
    #print(true_base_memory)

    looking(3, 0)  # loadCORDS for given resolution

    while True:


        #print(get_turn_current_player(true_base_memory, game_pid,player_character))
        position = win32gui.GetWindowRect(pid)
        offsetx, offsety, win_width, win_height = GetWindowRect(pid)
        background_screenshot(pid, win_width - offsetx, win_height - offsety)


        scroll_back(game_pid,1)

        if found_player == 0:
            #print("Before Search_mode" + str(search_mode) + " Player found" + str(found_player))

            print("Looking for Player in the marked area...")
            found_player, location_string, location, map_number = looking(2, search_mode)

            #print("Search_mode" + str(search_mode) + " Player found" + str(found_player))
            if found_player == 0:
                print("Looking for Player on Top")
                click_on_not_found_location(game_pid)
                scroll_forward(game_pid)
                print("Scrolled forward")
            if found_player == 1:

                print("Scrolled back")
                scroll_back(game_pid,0)

        if found_player == 1:
            print("Player found on: " + str(location_string) + "DEBUG: " + str(location) + " " + str(map_number))
            #load player stats
            if players_stats_map_status == 0:
                players_stats_map_status = load_player_stats(players_stats_map_status)
                print(players_stats_map)

            #check_if_roll_needed
            #if (if_waiting_for_roll()):
            #    press_space(pid)

        #check_fragment(1750, 650, 1820, 720, 'dice')
        #filename = 'ssmanipulations/' + 'dice' + '.jpg'
        #print ("Dice:" + str(compare(filename,2)))
        #looking(1)
        wait = cv2.waitKey(10)
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
    #cv2.imshow("Screen", img)
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

def click_on_not_found_location (pid):

    print(x_scale)
    print(y_scale)

    x = round(946*x_scale)
    y = round(140*y_scale)
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(1)


def scroll_back (pid, inicial):

    global search_mode
    win32api.SendMessage(pid,  win32con.MOUSE_WHEELED, (win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)))
    time.sleep(1)
    win32api.SendMessage(pid, win32con.MOUSE_WHEELED, (win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)))
    time.sleep(1)
    if inicial != 1:
        search_mode = 0
    time.sleep(1)

def scroll_forward (pid):

    global search_mode
    win32api.SendMessage(pid,  win32con.MOUSE_WHEELED, (win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 1, 0)))
    search_mode = 1
    time.sleep(2)

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

    return compare(filename, 0)

def compare (filename,mode):

    stat_list = ['0_blue', '1_blue', '2_blue', '3_blue', '4_blue', '5_blue', '6_blue', '7_blue', '8_blue', '9_blue', '10_blue', '11_blue', '12_blue', '13_blue', '14_blue', '15_blue', '16_blue', '17_blue', '18_blue', '19_blue', '20_blue', '0_red', '1_red', '2_red', '3_red', '4_red', '5_red', '6_red', '7_red', '8_red', '9_red', '10_red', '11_red', '12_red', '13_red', '14_red', '15_red', '16_red', '17_red', '18_red', '19_red', '20_red']
    stat_value_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    ui_list = ['empty', 'role_dice']
    ui_value_list = [0, 1]
    dice_list = ['dice_0', 'dice_1', 'dice_2', 'dice_3', 'dice_4', 'dice_5', 'dice_6']
    dice_value_list = [0, 1, 2, 3, 4, 5, 6]
    best_number = 0
    best_hit = 0
    i = 0
    if (mode == 0):
        list = stat_list
        value_list = stat_value_list
    if (mode == 1):
        list = ui_list
        value_list = ui_value_list
    if (mode == 2):
        list = dice_list
        value_list = dice_value_list

    while i < len(list):
        imageA = cv2.imread('templates/' + list[i] + '.jpg')
        imageB = cv2.imread(filename)
        # convert the images to grayscale
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        (score, diff) = metrics.structural_similarity(grayA, grayB, full=True)
        #diff = (diff * 255).astype("uint8")
        if score > best_number:
            best_number = score
            best_hit = i
        i += 1

        #print("Best SSIM: {}".format(best_number) + ' ' + str(value_list[best_hit]))

    return value_list[best_hit]


def check_fragment(left,top,right,bottom, filename):

    im = Image.open(r'ssmanipulations/screenshot.bmp')

    # Cropped image of above dimension
    # (It will not change orginal image)
    im1 = im.crop((left, top, right, bottom))

    # Shows the image in image viewer
    #im1.show()

    full_file_name = 'ssmanipulations/' + filename + '.jpg'

    im1 = im1.save(full_file_name)


def if_waiting_for_roll():

    filename = 'role_dice'

    check_fragment(1670, 730, 1890, 760, filename)
    if compare('templates/' + filename + '.jpg',1) == 1:
        #print("Waiting for roll")
        return True
    else:
        return False

def load_player_stats(status):

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

    return 1

#main()
#check_stats()
#compare()
#check_fragment(1730,300,1880,340, 'temp')
#check_stats(3,1,0)

#check_fragment(475,108,615,130, 'player')
#check_fragment(510, 80, 580, 150, 'dice')

#check_fragment(1750,650,1820,720, 'stat')
#print(players_stats_map)
#print(compare('ssmanipulations/' + 'dice' + '.jpg',2))

#alt left dice
#check_fragment(510, 80, 580, 150, 'dice')

#alt right dice
#check_fragment(1355, 80, 1425, 150, 'dice')
#

# (507, 111) (654, 162)


def check_if_in_area(x,y,mode2):

    if mode2 ==0:
        for i in range(len(map_0_cords)):
            if x <map_0_cords[i][2] and x >map_0_cords[i][0] and y<map_0_cords[i][3] and y>map_0_cords[i][1]:
                return (map_0[i],i,0)
        for i in range(len(map_1_cords)):
            if x <map_1_cords[i][2] and x >map_1_cords[i][0] and y<map_1_cords[i][3] and y>map_1_cords[i][1]:
                return (map_1[i],i,1)
        for i in range(len(map_2_cords)):
            if x <map_2_cords[i][2] and x >map_2_cords[i][0] and y<map_2_cords[i][3] and y>map_2_cords[i][1]:
                return (map_2[i],i,2)
        for i in range(len(map_3_cords)):
            if x <map_3_cords[i][2] and x >map_3_cords[i][0] and y<map_3_cords[i][3] and y>map_3_cords[i][1]:
                return (map_3[i],i,3)
    if mode2 ==1:
        for i in range(len(map_0_cords_if_top)):
            if x <map_0_cords_if_top[i][2] and x >map_0_cords_if_top[i][0] and y<map_0_cords_if_top[i][3] and y>map_0_cords_if_top[i][1]:
                return (map_0_if_top[i],i,0)

    return 0,0

def looking(mode, mode2):

    global x_scale
    global y_scale
    #mode: 1 - signle search 2 - all higher then threshold
    #mode2: 0 - normal 1 -top
    #img_rgb = cv2.imread('ssmanipulations/screenshot.bmp')
    img_rgb = cv2.imread('ssmanipulations/screenshot.bmp')
    img_rgb2 = cv2.imread('ssmanipulations/screenshot.bmp',0)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    screen_w, screen_h = img_rgb2.shape[::-1]

    x_to_X_template = 1349 / 1936
    y_to_Y_template = 523 / 1096

    if mode == 1 or mode == 2:
        template = cv2.imread('ssmanipulations/rob2.png', 0)
    if mode == 3:
        template = cv2.imread('ssmanipulations/wholeback_2.png', 0)

    w, h = template.shape[::-1]

    x_to_X_current = w/screen_w
    y_to_Y_current = h/screen_h

    x_scale = x_to_X_template/x_to_X_current
    y_scale = y_to_Y_template/y_to_Y_current
    if mode == 3:
        # resizing screen for right resoluction
        if (x_scale != 1 and y_scale != 1):
            width = int(template.shape[1] * x_scale)
            height = int(template.shape[0] * y_scale)
            dim = (width, height)
            # resize image
            template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)
            w, h = template.shape[::-1]

    if mode == 1:
        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED )

        #threshold = 0.75
        threshold = 0.5
        #print (res)

        if (np.max(res) > threshold):
            # We want the minimum squared difference
            mn, _, mnLoc, _ = cv2.minMaxLoc(res)

            # Draw the rectangle:
            # Extract the coordinates of our best match
            MPx, MPy = mnLoc

            # Step 2: Get the size of the template. This is the same size as the match.
            trows, tcols = template.shape[:2]

            #show all fields
            # for i in range(len(map_0_cords)):
            #     cv2.rectangle(img_rgb, (map_0_cords[i][0], map_0_cords[i][1]), (map_0_cords[i][2], map_0_cords[i][3]), (0, 0, 255), 1)
            #
            # for i in range(len(map_1_cords)):
            #     cv2.rectangle(img_rgb, (map_1_cords[i][0], map_1_cords[i][1]), (map_1_cords[i][2], map_1_cords[i][3]), (0, 255, 0), 1)
            #
            # for i in range(len(map_2_cords)):
            #     cv2.rectangle(img_rgb, (map_2_cords[i][0], map_2_cords[i][1]), (map_2_cords[i][2], map_2_cords[i][3]), (255, 0, 0), 1)
            # for i in range(len(map_3_cords)):
            #     cv2.rectangle(img_rgb, (map_3_cords[i][0], map_3_cords[i][1]), (map_3_cords[i][2], map_3_cords[i][3]), (255, 255, 255), 1)

            place, location =  check_if_in_area(MPx, MPy + trows,mode2)
            # print(place)

            # Step 3: Draw the rectangle on large_image
            cv2.rectangle(img_rgb, (MPx, MPy), (MPx + tcols, MPy + trows), (0, 0, 255), 1)
            #cv2.rectangle(img_rgb, (MPx, MPy), (MPx + tcols, MPy + trows), (0, 0, 255), 2)

        # Display the original image with the rectangle around the match.
        #cv2.imshow('output', img_rgb)

        # The image is only displayed if we call this
        #cv2.waitKey(0)
        return 1, None, None, None

    if mode == 2:

        place = ""
        location = 0
        map_number = 0
        threshold = 0.6
        #print(w)
        #print(h)

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where( res >= threshold)

        # for i in range(len(map_0_cords)):
        #     cv2.rectangle(img_rgb, (map_0_cords[i][0], map_0_cords[i][1]), (map_0_cords[i][2], map_0_cords[i][3]),
        #                   (0, 0, 255), 1)
        #
        # for i in range(len(map_1_cords)):
        #     cv2.rectangle(img_rgb, (map_1_cords[i][0], map_1_cords[i][1]), (map_1_cords[i][2], map_1_cords[i][3]),
        #                   (0, 255, 0), 1)
        #
        # for i in range(len(map_2_cords)):
        #     cv2.rectangle(img_rgb, (map_2_cords[i][0], map_2_cords[i][1]), (map_2_cords[i][2], map_2_cords[i][3]),
        #                   (255, 0, 0), 1)
        # for i in range(len(map_3_cords)):
        #     cv2.rectangle(img_rgb, (map_3_cords[i][0], map_3_cords[i][1]), (map_3_cords[i][2], map_3_cords[i][3]),
        #                   (255, 255, 255), 1)


        for pt in zip(*loc[::-1]):
            place, location, map_number = (check_if_in_area(pt[0], pt[1] + h, mode2))
            #print(place)

            #print (pt[0])
            #print (pt[1])

            #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (255,255,255), 1)

            #print("Threshold:" + str(threshold) + " Precision:" + str(precision_number))

        #print(place)
        if place == "":
            return 0, "", -1, -1
        #cv2.imshow('output', img_rgb)
        #cv2.waitKey(10)
        #print (place)
        #print (location)
        #print(map_number)
        return 1, place, location, map_number

    if mode == 3: #for creating map cords

        iterations_found = 0
        stop_loop = 0
        find_one = 1
        precision_number = 1
        x_for_single = 0
        y_for_single = 0
        place = ""
        location = ""
        x_cor = []
        y_cor = []
        x_cords_matrix = []
        y_cords_matrix = []
        row_master_cord_matrix = []
        master_cord_matrix = []
        temp_matrix =[]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.3

        while stop_loop == 0:
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)


            iterations_found = 0
            for pt in zip(*loc[::-1]):

                iterations_found += 1
                #print (pt[0])
                #print (pt[1])
                x_for_single = pt[0]
                y_for_single = pt[1]
                if (find_one == 0):
                    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (255,255,255), 1)

            #print("Threshold:" + str(threshold) + " Precision:" + str(precision_number))

            if iterations_found > 1:
                threshold += 0.2/precision_number
            if iterations_found == 0:
                threshold -= 0.1/precision_number
                precision_number += 1
            if iterations_found == 1:

                playable_board_size_x = w
                playable_board_size_y = h

                #print(str(x_for_single) + " " + str(y_for_single))
                x_cor, y_cor = get_basic_map_points(playable_board_size_x,playable_board_size_y)

                for j in range(len(y_cor)):

                    row_master_cord_matrix = []
                    for i in range(len(x_cor)):
                        temp_matrix = []
                        temp_matrix.append(x_cor[i])
                        temp_matrix.append(y_cor[j])
                        row_master_cord_matrix.append(temp_matrix)
                    master_cord_matrix.append(row_master_cord_matrix)

                #print(w)
                #print(h)
                #print(x_for_single)
                #print(y_for_single)
                matrix = transform_master_matrix(master_cord_matrix,w,h,x_scale,y_scale)
                populate_maps_with_cords(matrix,x_for_single,y_for_single)

                # for i in range(len(map_0_cords)):
                #     cv2.rectangle(img_rgb, (map_0_cords[i][0], map_0_cords[i][1]), (map_0_cords[i][2], map_0_cords[i][3]), (0, 255, 255), 1)
                # for i in range(len(map_1_cords)):
                #     cv2.rectangle(img_rgb, (map_1_cords[i][0], map_1_cords[i][1]), (map_1_cords[i][2], map_1_cords[i][3]), (0, 255, 0), 1)
                # for i in range(len(map_2_cords)):
                #     cv2.rectangle(img_rgb, (map_2_cords[i][0], map_2_cords[i][1]), (map_2_cords[i][2], map_2_cords[i][3]), (255, 0, 0), 1)
                # for i in range(len(map_3_cords)):
                #     cv2.rectangle(img_rgb, (map_3_cords[i][0], map_3_cords[i][1]), (map_3_cords[i][2], map_3_cords[i][3]), (255, 255, 255), 1)

                #for i in range(len(master_cord_matrix)-1):
                #   print(master_cord_matrix[i])
                #   for j in range(len(master_cord_matrix[i]) - 1):
                #       cv2.rectangle(img_rgb, (master_cord_matrix[i][j][0] + x_for_single, master_cord_matrix[i][j][1] + y_for_single), (master_cord_matrix[i+1][j+1][0] + x_for_single, master_cord_matrix[i+1][j+1][1] + y_for_single), (0, 0, 255), 1)
                #for i in range(len(x_cords_matrix)-1):
                #    for j in range(len(y_cords_matrix)-1):
                #        cv2.rectangle(img_rgb, (x_cords_matrix[j]+x_for_single, y_cords_matrix[i])+y_for_single, (x_cords_matrix[j+1]+x_for_single, y_cords_matrix[i+1]+y_for_single), (0, 0, 255), 1)
                #print(x_cords_matrix)
                #print(y_cords_matrix)

                #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 1)
                stop_loop = 1
        #if place == "":
        #    return 0
        #cv2.imshow('output', img_rgb)
        #cv2.waitKey(10)
        return 1, None, None, None


#looking(2)
# # #
# PROCESS_ALL_ACCESS = 0x1F0FFF
# processHandle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
# modules = win32process.EnumProcessModules(processHandle)
# processHandle.close()
# print (modules)
# print (len(modules))
# base_addr = modules[0]
# print (base_addr)
# print (hex(base_addr))
#
#

def transform_master_matrix(matrix,width,hight,x_scale,y_scale):

    #obliczanie tangesów kątów linii pochyłych (dane 1- x.... wybrane z proporcji z pixeli)
    tg1 = 2.07
    tg1v2 = hight/(width*(1-0.826)) #~2,234
    tg2 = 2.9
    tg2v2 = hight/(width*(0.862-0.734)) #~3,037
    tg3 = 4.83
    tg3v2 = hight / (width*(0.719-0.64))  # ~4,921
    tg4 = 14.51
    tg4v2 = hight / (width*(0.573-0.55))  # ~16,903

    #offsets to y axis
    y0 = 0 * hight
    y1 = 0.088 * hight
    y2 = 0.195 * hight
    y3 = 0.317 * hight
    y4 = 0.453 * hight
    y5 = 0.612 * hight
    y6 = 0.792 * hight
    y7 = 1 * hight
    y_offset = [y0,y1,y2,y3,y4,y5,y6,y7]


    for i in range(len(matrix)):
        #print(matrix[i])
        for j in range(len(matrix[i])):

            #matrix[i][j][1] = matrix[i][j][1] - round((matrix[i][j][1]/hight))
            matrix[i][j][1] = round(y_offset[i])
            if j == 0:
                matrix[i][j][0] = matrix[i][j][0] + round((hight / tg1v2) - (matrix[i][j][1] / tg1v2)*1.3)
            if j == 1:
                matrix[i][j][0] = matrix[i][j][0] + round((hight / tg2v2) - (matrix[i][j][1] / tg2v2)*1.1)
            if j == 2:
                matrix[i][j][0] = matrix[i][j][0] + round((hight / tg3v2) - (matrix[i][j][1] / tg3v2)*1.1)
            if j == 3:
                matrix[i][j][0] = matrix[i][j][0] + round((hight / tg4v2) - (matrix[i][j][1] / tg4v2)*1.1)
            if j == 4:
                matrix[i][j][0] = matrix[i][j][0] - round((hight / tg4v2) - (matrix[i][j][1] / tg4v2)*1.1)
            if j == 5:
                matrix[i][j][0] = matrix[i][j][0] - round((hight / tg3v2) - (matrix[i][j][1] / tg3v2)*1.1)
            if j == 6:
                matrix[i][j][0] = matrix[i][j][0] - round((hight / tg2v2) - (matrix[i][j][1] / tg2v2)*1.1)
            if j == 7:
                matrix[i][j][0] = matrix[i][j][0] - round((hight / tg1v2) - (matrix[i][j][1] / tg1v2)*1.3)

    return matrix

def populate_maps_with_cords (matrix,x_offset,y_offset):

    #!!!!!! X cords switch places for things on the right from centre of the map X1 <-> X2
    # [Y][!X1!][0]
    # [Y][!X1!][0]
    # [Y][!X2!][0]
    # [Y][!X2!][0]

    global map_0_cords
    global map_1_cords
    global map_2_cords
    global map_3_cords

    map_0_cords = []
    map_1_cords = []
    map_2_cords = []
    map_3_cords = []

    temp_array = [] #map0 field 1

    temp_array.append((matrix[0][0][0] + x_offset))
    temp_array.append((matrix[0][0][1] + y_offset))
    temp_array.append((matrix[1][1][0] + x_offset))
    temp_array.append((matrix[1][1][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 2

    temp_array.append((matrix[0][1][0] + x_offset))
    temp_array.append((matrix[0][1][1] + y_offset))
    temp_array.append((matrix[1][2][0] + x_offset))
    temp_array.append((matrix[1][2][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 3

    temp_array.append((matrix[0][2][0] + x_offset))
    temp_array.append((matrix[0][2][1] + y_offset))
    temp_array.append((matrix[1][3][0] + x_offset))
    temp_array.append((matrix[1][3][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 4

    temp_array.append((matrix[0][3][0] + x_offset))
    temp_array.append((matrix[0][3][1] + y_offset))
    temp_array.append((matrix[1][4][0] + x_offset))
    temp_array.append((matrix[1][4][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 5

    temp_array.append((matrix[0][5][0] + x_offset))
    temp_array.append((matrix[0][5][1] + y_offset))
    temp_array.append((matrix[1][4][0] + x_offset))
    temp_array.append((matrix[1][4][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 6

    temp_array.append((matrix[0][6][0] + x_offset))
    temp_array.append((matrix[0][6][1] + y_offset))
    temp_array.append((matrix[1][5][0] + x_offset))
    temp_array.append((matrix[1][5][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 7

    temp_array.append((matrix[0][7][0] + x_offset))
    temp_array.append((matrix[0][7][1] + y_offset))
    temp_array.append((matrix[1][6][0] + x_offset))
    temp_array.append((matrix[1][6][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 8

    temp_array.append((matrix[1][7][0] + x_offset))
    temp_array.append((matrix[1][7][1] + y_offset))
    temp_array.append((matrix[2][6][0] + x_offset))
    temp_array.append((matrix[2][6][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 9

    temp_array.append((matrix[2][7][0] + x_offset))
    temp_array.append((matrix[2][7][1] + y_offset))
    temp_array.append((matrix[3][6][0] + x_offset))
    temp_array.append((matrix[3][6][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 10

    temp_array.append((matrix[3][7][0] + x_offset))
    temp_array.append((matrix[3][7][1] + y_offset))
    temp_array.append((matrix[4][6][0] + x_offset))
    temp_array.append((matrix[4][6][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 11

    temp_array.append((matrix[4][7][0] + x_offset))
    temp_array.append((matrix[4][7][1] + y_offset))
    temp_array.append((matrix[5][6][0] + x_offset))
    temp_array.append((matrix[5][6][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 12

    temp_array.append((matrix[5][7][0] + x_offset))
    temp_array.append((matrix[5][7][1] + y_offset))
    temp_array.append((matrix[6][6][0] + x_offset))
    temp_array.append((matrix[6][6][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 13

    temp_array.append((matrix[6][7][0] + x_offset))
    temp_array.append((matrix[6][7][1] + y_offset))
    temp_array.append((matrix[7][6][0] + x_offset))
    temp_array.append((matrix[7][6][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 14

    temp_array.append((matrix[6][6][0] + x_offset))
    temp_array.append((matrix[6][6][1] + y_offset))
    temp_array.append((matrix[7][5][0] + x_offset))
    temp_array.append((matrix[7][5][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 15

    temp_array.append((matrix[6][5][0] + x_offset))
    temp_array.append((matrix[6][5][1] + y_offset))
    temp_array.append((matrix[7][4][0] + x_offset))
    temp_array.append((matrix[7][4][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 16

    temp_array.append((matrix[6][3][0] + x_offset))
    temp_array.append((matrix[6][3][1] + y_offset))
    temp_array.append((matrix[7][4][0] + x_offset))
    temp_array.append((matrix[7][4][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 17

    temp_array.append((matrix[6][2][0] + x_offset))
    temp_array.append((matrix[6][2][1] + y_offset))
    temp_array.append((matrix[7][3][0] + x_offset))
    temp_array.append((matrix[7][3][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 18

    temp_array.append((matrix[6][1][0] + x_offset))
    temp_array.append((matrix[6][1][1] + y_offset))
    temp_array.append((matrix[7][2][0] + x_offset))
    temp_array.append((matrix[7][2][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 19

    temp_array.append((matrix[6][0][0] + x_offset))
    temp_array.append((matrix[6][0][1] + y_offset))
    temp_array.append((matrix[7][1][0] + x_offset))
    temp_array.append((matrix[7][1][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 20

    temp_array.append((matrix[5][0][0] + x_offset))
    temp_array.append((matrix[5][0][1] + y_offset))
    temp_array.append((matrix[6][1][0] + x_offset))
    temp_array.append((matrix[6][1][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 21

    temp_array.append((matrix[4][0][0] + x_offset))
    temp_array.append((matrix[4][0][1] + y_offset))
    temp_array.append((matrix[5][1][0] + x_offset))
    temp_array.append((matrix[5][1][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 22

    temp_array.append((matrix[3][0][0] + x_offset))
    temp_array.append((matrix[3][0][1] + y_offset))
    temp_array.append((matrix[4][1][0] + x_offset))
    temp_array.append((matrix[4][1][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 23

    temp_array.append((matrix[2][0][0] + x_offset))
    temp_array.append((matrix[2][0][1] + y_offset))
    temp_array.append((matrix[3][1][0] + x_offset))
    temp_array.append((matrix[3][1][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map0 field 24

    temp_array.append((matrix[1][0][0] + x_offset))
    temp_array.append((matrix[1][0][1] + y_offset))
    temp_array.append((matrix[2][1][0] + x_offset))
    temp_array.append((matrix[2][1][1] + y_offset))
    map_0_cords.append(temp_array)

    temp_array = [] #map1 field 1

    temp_array.append((matrix[1][1][0] + x_offset))
    temp_array.append((matrix[1][1][1] + y_offset))
    temp_array.append((matrix[2][2][0] + x_offset))
    temp_array.append((matrix[2][2][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 2

    temp_array.append((matrix[1][2][0] + x_offset))
    temp_array.append((matrix[1][2][1] + y_offset))
    temp_array.append((matrix[2][3][0] + x_offset))
    temp_array.append((matrix[2][3][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 3

    temp_array.append((matrix[1][3][0] + x_offset))
    temp_array.append((matrix[1][3][1] + y_offset))
    temp_array.append((matrix[2][4][0] + x_offset))
    temp_array.append((matrix[2][4][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 4

    temp_array.append((matrix[1][5][0] + x_offset))
    temp_array.append((matrix[1][5][1] + y_offset))
    temp_array.append((matrix[2][4][0] + x_offset))
    temp_array.append((matrix[2][4][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 5

    temp_array.append((matrix[1][6][0] + x_offset))
    temp_array.append((matrix[1][6][1] + y_offset))
    temp_array.append((matrix[2][5][0] + x_offset))
    temp_array.append((matrix[2][5][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 6

    temp_array.append((matrix[2][6][0] + x_offset))
    temp_array.append((matrix[2][6][1] + y_offset))
    temp_array.append((matrix[3][5][0] + x_offset))
    temp_array.append((matrix[3][5][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 7

    temp_array.append((matrix[3][6][0] + x_offset))
    temp_array.append((matrix[3][6][1] + y_offset))
    temp_array.append((matrix[4][5][0] + x_offset))
    temp_array.append((matrix[4][5][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 8

    temp_array.append((matrix[4][6][0] + x_offset))
    temp_array.append((matrix[4][6][1] + y_offset))
    temp_array.append((matrix[5][5][0] + x_offset))
    temp_array.append((matrix[5][5][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 9

    temp_array.append((matrix[5][6][0] + x_offset))
    temp_array.append((matrix[5][6][1] + y_offset))
    temp_array.append((matrix[6][5][0] + x_offset))
    temp_array.append((matrix[6][5][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 10

    temp_array.append((matrix[5][5][0] + x_offset))
    temp_array.append((matrix[5][5][1] + y_offset))
    temp_array.append((matrix[6][4][0] + x_offset))
    temp_array.append((matrix[6][4][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 11

    temp_array.append((matrix[5][3][0] + x_offset))
    temp_array.append((matrix[5][3][1] + y_offset))
    temp_array.append((matrix[6][4][0] + x_offset))
    temp_array.append((matrix[6][4][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 12

    temp_array.append((matrix[5][2][0] + x_offset))
    temp_array.append((matrix[5][2][1] + y_offset))
    temp_array.append((matrix[6][3][0] + x_offset))
    temp_array.append((matrix[6][3][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 13

    temp_array.append((matrix[5][1][0] + x_offset))
    temp_array.append((matrix[5][1][1] + y_offset))
    temp_array.append((matrix[6][2][0] + x_offset))
    temp_array.append((matrix[6][2][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 14

    temp_array.append((matrix[4][1][0] + x_offset))
    temp_array.append((matrix[4][1][1] + y_offset))
    temp_array.append((matrix[5][2][0] + x_offset))
    temp_array.append((matrix[5][2][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 15

    temp_array.append((matrix[3][1][0] + x_offset))
    temp_array.append((matrix[3][1][1] + y_offset))
    temp_array.append((matrix[4][2][0] + x_offset))
    temp_array.append((matrix[4][2][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map1 field 16

    temp_array.append((matrix[2][1][0] + x_offset))
    temp_array.append((matrix[2][1][1] + y_offset))
    temp_array.append((matrix[3][2][0] + x_offset))
    temp_array.append((matrix[3][2][1] + y_offset))
    map_1_cords.append(temp_array)

    temp_array = [] #map2 field 1

    temp_array.append((matrix[2][2][0] + x_offset))
    temp_array.append((matrix[2][2][1] + y_offset))
    temp_array.append((matrix[3][3][0] + x_offset))
    temp_array.append((matrix[3][3][1] + y_offset))
    map_2_cords.append(temp_array)

    temp_array = [] #map2 field 2

    temp_array.append((matrix[2][3][0] + x_offset))
    temp_array.append((matrix[2][3][1] + y_offset))
    temp_array.append((matrix[3][4][0] + x_offset))
    temp_array.append((matrix[3][4][1] + y_offset))
    map_2_cords.append(temp_array)

    temp_array = [] #map2 field 3

    temp_array.append((matrix[2][5][0] + x_offset))
    temp_array.append((matrix[2][5][1] + y_offset))
    temp_array.append((matrix[3][4][0] + x_offset))
    temp_array.append((matrix[3][4][1] + y_offset))
    map_2_cords.append(temp_array)

    temp_array = [] #map2 field 4

    temp_array.append((matrix[3][5][0] + x_offset))
    temp_array.append((matrix[3][5][1] + y_offset))
    temp_array.append((matrix[4][4][0] + x_offset))
    temp_array.append((matrix[4][4][1] + y_offset))
    map_2_cords.append(temp_array)

    temp_array = [] #map2 field 5

    temp_array.append((matrix[4][5][0] + x_offset))
    temp_array.append((matrix[4][5][1] + y_offset))
    temp_array.append((matrix[5][4][0] + x_offset))
    temp_array.append((matrix[5][4][1] + y_offset))
    map_2_cords.append(temp_array)

    temp_array = [] #map2 field 6

    temp_array.append((matrix[4][3][0] + x_offset))
    temp_array.append((matrix[4][3][1] + y_offset))
    temp_array.append((matrix[5][4][0] + x_offset))
    temp_array.append((matrix[5][4][1] + y_offset))
    map_2_cords.append(temp_array)

    temp_array = [] #map2 field 7

    temp_array.append((matrix[4][2][0] + x_offset))
    temp_array.append((matrix[4][2][1] + y_offset))
    temp_array.append((matrix[5][3][0] + x_offset))
    temp_array.append((matrix[5][3][1] + y_offset))
    map_2_cords.append(temp_array)

    temp_array = [] #map2 field 8

    temp_array.append((matrix[3][2][0] + x_offset))
    temp_array.append((matrix[3][2][1] + y_offset))
    temp_array.append((matrix[4][3][0] + x_offset))
    temp_array.append((matrix[4][3][1] + y_offset))
    map_2_cords.append(temp_array)

    temp_array = [] #map3 field 1

    temp_array.append((matrix[3][3][0] + x_offset))
    temp_array.append((matrix[3][3][1] + y_offset))
    temp_array.append((matrix[4][4][0] + x_offset))
    temp_array.append((matrix[4][4][1] + y_offset))
    map_3_cords.append(temp_array)


    # for i in range(len(matrix)-1):
    #     print(matrix[i])
    #     for j in range(len(matrix[i])-1):
    #         print(str(i*(len(matrix)-1) + j))
    #         print ("[" + str(matrix[i][j][0]+x_offset) + " " + str(matrix[i][j][1]+y_offset)  + "]" + " [" + str(matrix[i+1][j+1][0]+x_offset) + " " + str(matrix[i+1][j+1][1]+y_offset) + "]")
    #

def get_basic_map_points (x,y):

    x_cor = []
    y_cor = []
    for i in range (8):
        x_cor.append(round((x*i)/7))
        y_cor.append(round((y*i)/7))
    #print (x)
    #print (y)
    #print (x_cor)
    #print (y_cor)

    return x_cor, y_cor


def read_process_memory(process_id, address, offsets, size_of_data=8):

    p_handle = ctypes.windll.kernel32.OpenProcess(win32con.PROCESS_VM_READ, False, process_id)

    data = ctypes.c_uint(size_of_data)
    bytesRead = ctypes.c_uint(size_of_data)

    current_address = ctypes.c_void_p(address + offsets)
    if offsets:
        # Do something to the offsets
        ctypes.windll.kernel32.ReadProcessMemory(p_handle, current_address, ctypes.byref(data), ctypes.sizeof(data), ctypes.byref(bytesRead))

    else:
        ctypes.windll.kernel32.ReadProcessMemory(p_handle, current_address, ctypes.byref(data), ctypes.sizeof(data), ctypes.byref(bytesRead))


    return data.value


#
# adress1 = base_addr

# for module in modules:
#     if module == 83755008:
#         print ('tu')
#
#     adress2 = module + int('7D28D0', 16)
#     print (adress2)
#
#
#
#     result = (read_process_memory(2964, adress2, False))
#     print(result)
#     result2 = result.to_bytes(4, 'little')
#     print(result2)
#

# adress2 = 1720975360 + int('7FDF70', 16)
# #print(adress2)
# war = True
# current_player = ''
# temp_offset = 0
# while war:
#     result = (read_process_memory(pid, adress2, temp_offset, False))
#     #print(result)
#     result2 = result.to_bytes(4, 'little')
#     #print(result2)
#     if (current_player) == '':
#         current_player = result2.decode("utf-8")
#     else:
#         current_player = current_player + result2.decode("utf-8")[-1]
#     if result2[2] == 0 and result2[3] == 0:
#         #print ("wystarczy")
#         current_player = current_player.strip()
#         war = False
#     temp_offset += 1
#
#     #print (current_player)

def get_turn_current_player (base_adress, p_pid, player_char):

    #7FDF70 -> offset for currently selected player
    base_adress_2 = base_adress+ int('7FDF70', 16)
    war = True
    current_player = ''
    temp_offset = 0
    while war:
        result = (read_process_memory(p_pid, base_adress_2, temp_offset, False))
        # print(result)
        result2 = result.to_bytes(4, 'little')
        # print(result2)
        if (current_player) == '':
            current_player = result2.decode("utf-8")
        else:
            current_player = current_player + result2.decode("utf-8")[-1]
        if result2[2] == 0 and result2[3] == 0:
            # print ("wystarczy")
            current_player = current_player.strip()
            war = False
        temp_offset += 1

    if current_player.__contains__(player_char):
        return 1
    else:
        return 0
    #return current_player


def get_data_from_memory_for_dices (adress,p_pid):

    PROCESS_ALL_ACCESS = 0x1F0FFF
    processHandle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, p_pid)
    modules = win32process.EnumProcessModules(processHandle)
    processHandle.close()

    for module in modules:
        adress2 = int(adress, 16)
        result = (read_process_memory(p_pid, adress2, 0, False))
        result2 = result.to_bytes(4, 'little')
        #print(result2)
        try:
            check = result2.decode("utf-8")
        except UnicodeDecodeError:
            continue

        return check

def get_current_primary_dice_value_all_players_one (p_pid):

    # 1170767D -> memory address#1 for primary dice (one) (movement) from dx -> igd9dxva32.dll + 160 ' 1A 00
    # 117076C9 -> memory address#2 for primary dice (one) (movement) from dx -> igd9dxva32.dll + 160 ' 24 00

    # 1489767D alt
    # 148976C9 alt

    result = get_data_from_memory_for_dices ("1489767D", p_pid)

    return (result)


def get_current_primary_dice_value_all_players_two(p_pid):
    #
    #

    # 1489827D alt
    # 148982C9 alt

    result = get_data_from_memory_for_dices("1489827D   ", p_pid)

    return (result)

def get_current_battle_dice_value_player_one (p_pid):


    # 116C607D -> memory address#1 for battle dice (only 1)
    # 116C60C9 -> memory address#2 for battle dice(only 1)

    # 1485607D
    # 148560C9

    result = get_data_from_memory_for_dices("116C607D", p_pid)

    return (result)

def get_current_battle_dice_value_enemy_one (p_pid):


    # 1485027D -> memory address#1 for battle dice (only 1)
    # 1485027D -> memory address#2 for battle dice(only 1)

    #
    #

    result = get_data_from_memory_for_dices("116C02C9", p_pid)

    return (result)


def check_in_memory_for_user_data_and_get_true_base_memory (fourLetters, p_pid):

    PROCESS_ALL_ACCESS = 0x1F0FFF
    processHandle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, p_pid)
    modules = win32process.EnumProcessModules(processHandle)
    processHandle.close()
    #print(modules)

    for module in modules:
        adress2 = module + int('7D28D0', 16)
        result = (read_process_memory(p_pid, adress2, 0, False))
        result2 = result.to_bytes(4, 'little')
        #print(result2)
        try:
            check = result2.decode("utf-8")
        except UnicodeDecodeError:
            #print(result2)
            continue

        if check == fourLetters:
            print (module)
            return module


#true_base_memory = (check_in_memory_for_user_data_and_get_true_base_memory ('Kamo', 18256))
#
#print(true_base_memory)
#
#print(get_turn_current_player(true_base_memory, 18256))
#main()
#check_in_memory_for_user_data_and_get_true_base_memory("Kamo",17336)
print(get_current_primary_dice_value_all_players_one(5816))
print(get_current_primary_dice_value_all_players_two(5816))
print(get_current_battle_dice_value_player_one(5816))
print(get_current_battle_dice_value_enemy_one(5816))
#looking(3,0)
#looking(2,1)