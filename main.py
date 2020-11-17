
import ctypes

import cv2

import win32api
import win32con
import win32process
import numpy as np
import win32gui
from scipy import spatial
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

c = wmi.WMI()

def enum_win(hwnd, result):
    win_text = win32gui.GetWindowText(hwnd)
    windows_list.append((hwnd, win_text))

def main ():

    global players_stats_map_status
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

        #load player stats
        if players_stats_map_status == 0:
            players_stats_map_status = load_player_stats(players_stats_map_status)
            #print(players_stats_map)

        #check_if_roll_needed
        #if (if_waiting_for_roll()):
        #    press_space(pid)
        check_fragment(1750, 650, 1820, 720, 'dice')
        filename = 'ssmanipulations/' + 'dice' + '.jpg'
        #print ("Dice:" + str(compare(filename,2)))
        #looking(1)
        wait = cv2.waitKey(100)
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
    #looking(1)
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

        (score, diff) = compare_ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")
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


def check_if_in_area(x,y):

    for i in range(len(map_0_cords)):
        if x <map_0_cords[i][2] and x >map_0_cords[i][0] and y<map_0_cords[i][3] and y>map_0_cords[i][1]:
            return (map_0[i])
    for i in range(len(map_1_cords)):
        if x <map_1_cords[i][2] and x >map_1_cords[i][0] and y<map_1_cords[i][3] and y>map_1_cords[i][1]:
            return (map_1[i])
    for i in range(len(map_2_cords)):
        if x <map_2_cords[i][2] and x >map_2_cords[i][0] and y<map_2_cords[i][3] and y>map_2_cords[i][1]:
            return (map_2[i])
    for i in range(len(map_3_cords)):
        if x <map_3_cords[i][2] and x >map_3_cords[i][0] and y<map_3_cords[i][3] and y>map_3_cords[i][1]:
            return (map_3[i])

    return 0

def looking(mode):
    img_rgb = cv2.imread('ssmanipulations/screenshot.bmp')
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('ssmanipulations/rob.png',0)
    w, h = template.shape[::-1]



    if mode == 1:
        res = cv2.matchTemplate(img_gray,template,cv2.TM_SQDIFF_NORMED )


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

        print(check_if_in_area(MPx, MPy + trows))

        # Step 3: Draw the rectangle on large_image
        #cv2.rectangle(img_rgb, (MPx, MPy), (MPx + tcols, MPy + trows), (0, 0, 255), 2)

        # Display the original image with the rectangle around the match.
        #cv2.imshow('output', img_rgb)

        # The image is only displayed if we call this
        #cv2.waitKey(0)

    if mode == 2:

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        print (res)
        loc = np.where( res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

        print(pt, (pt[0] + w, pt[1] + h))
        cv2.imshow('output', img_rgb)
        cv2.waitKey(0)


main()

#looking(1)


pid = 2736
current_player_offset = '7FDF70'
user_offset = '7D28D0'

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


#true_base_memory = (check_in_memory_for_user_data_and_get_true_base_memory ('Kamo', 4760))
#
#print(true_base_memory)
#
#print(get_turn_current_player(true_base_memory, 4760))
