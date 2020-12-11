import vk_api
import random
import requests
import Gen
import sys
import draw_labirint
import send_image
import requests
import bs4 as bs4
import urllib
#import urllib.reques
#import event.user_id
import get_name_and_icon
from func_main import *
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import work_with_database

keys1=VkKeyboard(one_time=False)
keys1.add_button('info', color="default")
keys1.add_line()
keys1.add_button('generate', color="primary")
keys1.add_button('connect', color=VkKeyboardColor.POSITIVE)

keys_standart=VkKeyboard(one_time=False) #кнопки при ходах

keys_standart.add_button('show labirint', color="default")

keys_standart.add_line()

keys_standart.add_button('go right', color="positive")
keys_standart.add_button('go left', color="positive")
keys_standart.add_button('go up', color="positive")
keys_standart.add_button('go down', color="positive")


keys_standart.add_line()

keys_standart.add_button('ruin right', color="primary")
keys_standart.add_button('ruin left', color="primary")
keys_standart.add_button('ruin up', color="primary")
keys_standart.add_button('ruin down', color="primary")

keys_standart.add_line()

keys_standart.add_button('bang right', color="negative")
keys_standart.add_button('bang left', color="negative")
keys_standart.add_button('bang up', color="negative")
keys_standart.add_button('bang down', color="negative")

keys_standart.add_line()

keys_standart.add_button('info', color="primary")
keys_standart.add_button('get', color="positive")
keys_standart.add_button('put', color="default")
keys_standart.add_button('exit', color="negative")

keys_coord=VkKeyboard(one_time=False) #координаты
keys_coord.add_button('coordinate random', color="positive")

for i in range(4):
    keys_coord.add_line()
    for j in range(4):
        keys_coord.add_button(str(j)+" "+str(3-i), color="default")

def construct_button_for_add_friends(my_room): #разные кнопки для разных пользователей
    button=VkKeyboard(one_time=False)
    for player in my_room.players:
        button.add_button('add '+str(player.id)+" ("+player.name+")", color="default")
        button.add_line()
    button.add_button('generate', color="primary")
    button.add_button('connect', color="positive")
    return button

def construct_button_for_invent(vk,dic_rooms,user_id,first,last): #для приглашения
    kontakts=work_with_database.get_kontakts(user_id)

    button=VkKeyboard(one_time=False)
    button.add_button('previous kontakts ['+str(first-5)+','+str(last-5)+']', color="primary")
    button.add_line()
    short_kontakts=kontakts[first:last]
    for kontakt in short_kontakts:
        col="default"
        if 1==vk.method("users.get",{'user_ids':str(kontakt),"fields":"online"})[0]["online"] and None==dic_rooms.get(int(kontakt),None):
            col="positive"
            
        button.add_button('call '+str(kontakt)+" ("+work_with_database.get_name_by_id(kontakt)+")", color=col)
        button.add_line()
    button.add_button('next kontakts ['+str(first+5)+','+str(last+5)+']', color="primary")
    button.add_line()
    button.add_button('start', color="positive")
    button.add_button('exit', color="negative")
    return button

def construct_button_for_answer(room_id): #для ответа на приглашение
    button=VkKeyboard(one_time=False)
    button.add_button('connect '+str(room_id), color="positive")
    button.add_line()
    button.add_button('generate', color="primary")
    button.add_button('connect', color="positive")
    return button