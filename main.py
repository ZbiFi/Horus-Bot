
import ctypes

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
map_0_cords = [[523 , 130, 652, 181],[653 , 130, 772, 181],[773 , 130, 899, 181],[900 , 130, 1019, 181],[1020 , 130, 1139, 181],[1140 , 130, 1262, 181],[1263 , 130, 1407, 181],[1302, 182, 1433, 238],[1317, 239, 1462, 301],[1338 , 302, 1495, 371],[1362, 372, 1534, 454],[1392, 455, 1573,548],[1428, 549, 1660, 661],[1233, 549, 1402, 661],[1050, 549, 1232, 661],[875, 549, 1049, 661],[695, 549, 863, 661],[517, 549, 673, 661],[324, 549, 492, 661],[360, 455, 526,548],[398, 372, 561, 454],[435, 302, 590, 371],[466, 239, 611, 301],[500 , 182, 626, 238]]
map_0_if_top = ['The Halo Starts', 'Caliban', 'The Rubicon Straits', 'Port Maw']
map_0_cords_if_top =[[334, 273, 540, 396],[584, 273, 818, 396],[883, 273, 1080, 396],[1090, 273, 1377, 396]]
map_1 = ['Isstvann III', 'Warp Storm', 'Eye of Terror', 'Warp Storm', 'Davin', 'The Dominion of Storms', 'Paramar', 'The Kayvas Belt', 'Tallarn', 'The Uhulis Sector', 'Luna', 'Cthonia', 'Titan', 'The Mandragoran Sector', 'Mars', 'The Stellar Wastes']
map_1_cords = [[650 , 182, 767, 238],[775 , 182, 895, 238],[900 , 182, 1024, 238],[1025, 182, 1157, 238],[1158, 182, 1301, 238],[1168, 239, 1300, 301],[1182 , 302, 1319, 371],[1194, 372, 1341, 455],[1210, 455, 1373,548],[1040, 455, 1209,548],[884, 455, 1050,548],[725, 455, 874,548],[565, 455, 711,548],[592, 372, 732, 455],[609 , 302, 746, 371],[628, 239, 758, 301]]
map_2 = ['The Outer Palace', 'The Inner Palace', 'The Outer Palace', 'Damocles Startport', 'Arcus Orbital Plate', 'Spaceport Primus', 'Lemurya Orbital Plate', 'The Wastes']
map_2_cords = [[781, 239, 898, 301],[901, 239, 1021, 301],[1018, 239, 1145, 301],[1024 , 302, 1154, 371],[1028, 372, 1166, 454],[897, 372, 1027, 454],[762, 372, 892, 454],[770 , 302, 892, 371]]
map_3 = ['The Final Battle']
map_3_cords = [[899 , 302, 1023, 371]]
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

game_pid = 3332
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
    win32gui.EnumWindows(enum_win, toplist)
    # Game handle
    pid = 0
    pid = win32gui.FindWindow(None, 'Talisman : The Horus Heresy')

    true_base_memory = check_in_memory_for_user_data_and_get_true_base_memory(steam_name_4_lett, game_pid)
    #print(true_base_memory)

    while True:

        print(get_turn_current_player(true_base_memory, game_pid))
        position = win32gui.GetWindowRect(pid)
        offsetx, offsety, win_width, win_height = GetWindowRect(pid)
        background_screenshot(pid, win_width - offsetx, win_height - offsety)

        scroll_back(game_pid,1)

        # if found_player == 0:
        #     print("Before Search_mode" + str(search_mode) + " Player found" + str(found_player))
        #     found_player = looking(2, search_mode)
        #
        #     print("Search_mode" + str(search_mode) + " Player found" + str(found_player))
        #
        #     if found_player == 0:
        #         click_on_not_found_location(game_pid)
        #         scroll_forward(game_pid)
        #         #print("Scrolled forward")
        #
        #     if found_player == 1:
        #         scroll_back(game_pid,0)



        #load player stats
        if players_stats_map_status == 0:
            players_stats_map_status = load_player_stats(players_stats_map_status)
            #print(players_stats_map)

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

    x = 946
    y = 140
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
    time.sleep(1)

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

    filename = 'temp'

    check_fragment(1670, 730, 1890, 760, filename)
    if compare('ssmanipulations/' + filename + '.jpg',1) == 1:
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
                return (map_0[i],i)
        for i in range(len(map_1_cords)):
            if x <map_1_cords[i][2] and x >map_1_cords[i][0] and y<map_1_cords[i][3] and y>map_1_cords[i][1]:
                return (map_1[i],i)
        for i in range(len(map_2_cords)):
            if x <map_2_cords[i][2] and x >map_2_cords[i][0] and y<map_2_cords[i][3] and y>map_2_cords[i][1]:
                return (map_2[i],i)
        for i in range(len(map_3_cords)):
            if x <map_3_cords[i][2] and x >map_3_cords[i][0] and y<map_3_cords[i][3] and y>map_3_cords[i][1]:
                return (map_3[i],i)
    if mode2 ==1:
        for i in range(len(map_0_cords_if_top)):
            if x <map_0_cords_if_top[i][2] and x >map_0_cords_if_top[i][0] and y<map_0_cords_if_top[i][3] and y>map_0_cords_if_top[i][1]:
                return (map_0_if_top[i],i)

    return 0,0

def looking(mode, mode2):

    #mode: 1 - signle search 2 - all higher then threshold
    #mode2: 0 - normal 1 -top
    #img_rgb = cv2.imread('ssmanipulations/screenshot.bmp')
    img_rgb = cv2.imread('ssmanipulations/screenshot_small.bmp')
    img_rgb2 = cv2.imread('ssmanipulations/screenshot_small.bmp',0)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('ssmanipulations/wholeback.png',0)
    screen_w, screen_h = img_rgb2.shape[::-1]
    w, h = template.shape[::-1]

    x_to_X_template = 1363/1936
    y_to_Y_template = 537/1096

    x_to_X_current = w/screen_w
    y_to_Y_current = h/screen_h

    x_scale = x_to_X_template/x_to_X_current
    y_scale = y_to_Y_template/y_to_Y_current

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
        cv2.imshow('output', img_rgb)

        # The image is only displayed if we call this
        cv2.waitKey(0)
        return 1

    if mode == 2:

        threshold = 0.38
        print(w)
        print(h)

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

         #print(w)
        #print(h)
        iterations_found = 0
        for pt in zip(*loc[::-1]):
            place, location = (check_if_in_area(pt[0], pt[1] + h, mode2))
            #print(place)

            #print (pt[0])
            #print (pt[1])

            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (255,255,255), 1)

            #print("Threshold:" + str(threshold) + " Precision:" + str(precision_number))

        #if place == "":
        #    return 0
        cv2.imshow('output', img_rgb)
        cv2.waitKey(0)
        return 1

    if mode == 3:

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
        # print(screen_w)
        # print(w)
        # print(screen_h)
        # print(h)
        # print(w/screen_w)
        # print(h/screen_h)

        #width = int(template.shape[1] * scale_percent / 100)
        #height = int(template.shape[0] * scale_percent / 100)
        #dim = (width, height)

        #template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)


        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.3

        while stop_loop == 0:
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)


            iterations_found = 0
            for pt in zip(*loc[::-1]):
                place, location = (check_if_in_area(pt[0], pt[1] + h, mode2))
            #print(place)
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

                for i in range(len(x_cor)):
                    row_master_cord_matrix = []
                    for j in range(len(y_cor)):
                        temp_matrix = []
                        temp_matrix.append(x_cor[i])
                        temp_matrix.append(y_cor[j])
                        row_master_cord_matrix.append(temp_matrix)
                    master_cord_matrix.append(row_master_cord_matrix)


                for i in range(len(master_cord_matrix)-1):
                    print(master_cord_matrix[i])
                    for j in range(len(master_cord_matrix[i]) - 1):
                        cv2.rectangle(img_rgb, (master_cord_matrix[i][j][0] + x_for_single, master_cord_matrix[i][j][1] + y_for_single), (master_cord_matrix[i+1][j+1][0] + x_for_single, master_cord_matrix[i+1][j+1][1] + y_for_single), (0, 0, 255), 1)
                #for i in range(len(x_cords_matrix)-1):
                #    for j in range(len(y_cords_matrix)-1):
                #        cv2.rectangle(img_rgb, (x_cords_matrix[j]+x_for_single, y_cords_matrix[i])+y_for_single, (x_cords_matrix[j+1]+x_for_single, y_cords_matrix[i+1]+y_for_single), (0, 0, 255), 1)
                #print(x_cords_matrix)
                #print(y_cords_matrix)
                #cv2.rectangle(img_rgb, (w+x_cor[i], h+y_cor[j]), (w+x_cor[i]-1, h+y_cor[j]-1), (0, 0, 255), 1)

                #cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 1)
                stop_loop = 1
        #if place == "":
        #    return 0
        cv2.imshow('output', img_rgb)
        cv2.waitKey(0)
        return 1


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

def get_basic_map_points (x,y):

    x_cor = []
    y_cor = []
    for i in range (8):
        x_cor.append(round((x*i)/7))
        y_cor.append(round((y*i)/7))
    print (x)
    print (y)
    print (x_cor)
    print (y_cor)

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

def get_turn_current_player (base_adress, p_pid):

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

    return current_player

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
            return module


#true_base_memory = (check_in_memory_for_user_data_and_get_true_base_memory ('Kamo', 18256))
#
#print(true_base_memory)
#
#print(get_turn_current_player(true_base_memory, 18256))
#main()

looking(3,0)