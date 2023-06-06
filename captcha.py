from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from connectivity_bot.telegram_wrapper import *
from logging.handlers import TimedRotatingFileHandler
import os
import signal
import telegram_interface
import itertools
import base64
import numpy as np
import cv2
import io
from imageio import imread
from collections import Counter
'''
0   1   2
3   4   5
6   7   8
'''


def check_box_touches(images):
    '''
    images[0][
        vertical_distance_from_top,
        horizontal_distance_from_left
        ]
    '''
    # LineCheck: 0 1 2
    row1_touch1 = any(images[0][55,-1]==images[1][55,0])
    row1_touch2 = any(images[1][55,-1]==images[2][55,0])
    if False in [row1_touch1, row1_touch2]:
        if row1_touch1 == False and row1_touch2 == False:
            return 1
        elif row1_touch1 == False:
            return 0
        else:
            return 2

    # LineCheck: 6 7 8
    row3_touch1 = any(images[6][110,-1]==images[7][110,0])
    row3_touch2 = any(images[7][110,-1]==images[8][110,0])
    if False in [row3_touch1, row3_touch2]:
        if row3_touch1 == False and row3_touch2 == False:
            return 7
        elif row3_touch1 == False:
            return 6
        else:
            return 8
        
    # Column check: 0 3 6
    column1_touch1 = any(images[0][80,-1]==images[3][80,0])
    column1_touch2 = any(images[3][80,-1]==images[6][80,0])
    if False in [column1_touch1, column1_touch2]:
        if column1_touch1 == False and column1_touch2 == False:
            return 3
        elif column1_touch1 == False:
            return 0
        else:
            return 6

    # Column check: 2 5 8
    column3_touch1 = any(images[2][-1,110]==images[5][0,110])
    column3_touch2 = any(images[5][-1,110]==images[8][0,110])
    if False in [column3_touch1, column3_touch2]:
        if column3_touch1 == False and column3_touch2 == False:
            return 5
        elif column3_touch1 == False:
            return 2
        else:
            return 8
    
    return 4


def invade_horizontal(images, indexes, background_color, reverse=True):
    resistances = []
    for idx in indexes:
        invasion_line = (images[idx][85,:]==background_color)[:,0]

        if reverse:
            invasion_line = invasion_line[::-1]

        resistance_point = np.where(invasion_line == False)[0][0] + 3
        resistances.append(resistance_point)
    return resistances


def invade_vertical(images, indexes, background_color, reverse=True):
    resistances = []
    for idx in indexes:
        invasion_line = (images[idx][:,85]==background_color)[:,0]

        if reverse:
            invasion_line = invasion_line[::-1]

        resistance_point = np.where(invasion_line == False)[0][0] + 3
        resistances.append(resistance_point)
    return resistances


def find_different_index(results):
    match_01 = results[0] == results[1]
    match_12 = results[1] == results[2]

    if match_01 == False and match_12 == False:
        return 1
    elif match_01 == False:
        return 0
    else:
        return 2

def color_invasion(images, background_color):
    res_top = invade_vertical(images, [0,1,2], background_color, False)

    if len(np.unique(res_top)) != 1:
        return find_different_index(res_top)

    res_bot = invade_vertical(images, [6,7,8], background_color, True)
    if len(np.unique(res_bot)) != 1:
        return find_different_index(res_bot) + 6

    res_left = invade_horizontal(images, [0,3,6], background_color, False)
    if len(np.unique(res_left)) != 1:
        return find_different_index(res_left)*3

    res_right = invade_horizontal(images, [2,5,8], background_color, True)
    if len(np.unique(res_right)) != 1:
        return find_different_index(res_right)*3 + 2
    
    return 0


def eval_background_color(image):
    corner_colors = np.array([image[0,0], image[0,-1], image[-1,-1], image[-1,0]])
    counts = np.bincount(corner_colors[:,0])
    val = np.argmax(counts)
    index = np.where(corner_colors[:,0] == val)[0][0]
    return corner_colors[index]


def load_images(driver):
    images = []
    for idx in range(9):
        base64s = driver.find_elements(By.ID, str(idx))[0].get_attribute('src').split(',')[1]
        cv2_img = cv2.cvtColor(imread(io.BytesIO(base64.b64decode(base64s))), cv2.COLOR_RGB2BGR)
        images.append(cv2_img)
    return images


def solve(images):
    background_color = eval_background_color(images[0])
    return color_invasion(images, background_color)


if __name__ == '__main__':
    f = open(str(sys.argv[1]),'r')
    main_config = json.load(f)

    driver = webdriver.Chrome(main_config['chrome_driver'])
    driver.get("file:///D:/git/pararius-bot/resources/captcha1.html")

    images = load_images(driver)
    index = solve(images)
    
    print('Upsidedown index:',index)

