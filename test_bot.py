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
from buttons import *
import random
import numpy as np
session = requests.Session()
token="5e687395dff870a6f6c9b95bc6e50c9651c98367439c4ecaffdf16fc53e7e57b0bd0bb276b335d5b88ade"
vk = vk_api.VkApi(token=token, scope='messages')
#vk_session.auth(token_only=True)
longpoll = VkLongPoll(vk)

   
my_room=0
Rooms=[]
dic_rooms={}


#try:
for event in longpoll.listen():
    #print(event.user_id)
    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня( то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            request = event.text

            work_with_database.update_users_in_database(vk,event.user_id)
            try:
                if dic_rooms.get(event.user_id,None)==None: #-------------------------------------начало внешнего блока
                    if request.split()[0] == "generate":
                        generate(vk,Rooms,dic_rooms,event.user_id,request)
                        my_room=dic_rooms[event.user_id]
                        draw_labirint.draw_labirint(my_room)
                        draw_labirint.draw_waiting(vk,my_room)
                        send_image.send_image_to_all_viewers(vk,my_room.users,"images/waiting"+str(my_room.hash)+".png")
                        if "create"==my_room.status:
                            write_msg_with_buttons(vk,event.user_id,"Вы можете позвать в игру своих друзей.",construct_button_for_invent(vk,dic_rooms,event.user_id,0,5))


                    elif request.split()[0] == "connect":
                        connect(vk,Rooms,dic_rooms,event.user_id,request)
                        if dic_rooms.get(event.user_id,None)!=None:
                            my_room=dic_rooms[event.user_id]
                            draw_labirint.draw_waiting(vk,my_room)
                            send_image.send_image_to_all_viewers(vk,my_room.users,"images/waiting"+str(my_room.hash)+".png")
                            if "create"==my_room.status:
                                write_msg_with_buttons(vk,event.user_id,"Вы можете позвать в игру своих друзей.",construct_button_for_invent(vk,dic_rooms,event.user_id,0,5))


                    elif "view"==request.split()[0]:

                        view(vk,Rooms,dic_rooms,event.user_id,request)
                        my_room=dic_rooms[event.user_id]
                        draw_labirint.draw_labirint(my_room)
                        send_image.send_image_to_all_viewers(vk,my_room.viewers,"images/"+str(my_room.hash)+".png")
                    elif "add"==request.split()[0]:
                        work_with_database.put_kontaks(event.user_id,request.split()[1])
                        write_msg(vk,event.user_id,"Вы пополнили список своих контактов!")
                    elif "top10"==request.split()[0]:
                        write_msg(vk,event.user_id,work_with_database.get_top10())
                    elif "my raiting"==request:
                        write_msg(vk,event.user_id,str(work_with_database.get_raiting_by_id(event.user_id)))
                    elif "info"==request.split()[0]:
                        write_msg_with_buttons(vk,event.user_id, open('info_text.txt').read(),keys1)
                    elif "feedback"==request.split()[0]:
                        work_with_database.feedback(event.user_id,request[8::])
                        write_msg_with_buttons(vk,event.user_id, "Большое спасибо за обратную связь. Это очень важно для нас.",keys1)
                    else:
                        write_msg_with_buttons(vk,event.user_id, "Некорректные входные данные. Такой команды нет.",keys1)
                else:#------------------------------------------------------------------------начало внутреннего блока
                    my_room=dic_rooms[event.user_id]
                    if "create"==my_room.status:
                        if request.split()[0] == "start":

                            #my_room=dic_rooms[event.user_id]
                            start(vk,my_room)
                        elif "call"==request.split()[0]:
                            #print(request.split()[1])
                            if dic_rooms.get(int(request.split()[1]),None)==None:
                                write_msg_with_buttons(vk,request.split()[1],"Игрок "+str(event.user_id)+" ("+work_with_database.get_name_by_id(event.user_id)+") приглашает Вас в игру. ",construct_button_for_answer(my_room.id))
                            write_msg_with_buttons(vk,event.user_id,"Вы отправили приглашение.", construct_button_for_invent(vk,dic_rooms,event.user_id,0,5))
                        elif "exit"==request.split()[0]:
                            my_room.users.remove(event.user_id)
                            my_room.real_num-=1
                            dic_rooms.pop(event.user_id)

                            if 0==my_room.real_num:
                                my_room.status="end"
                            else:
                                draw_labirint.draw_waiting(vk,my_room)
                                send_image.send_image_to_all_viewers(vk,my_room.users,"images/waiting"+str(my_room.hash)+".png")
                            write_msg_with_buttons(vk,event.user_id,"Вы вышли из комнаты, теперь Вы можете начать новую игру.",keys1)
                        elif "next"==request.split()[0] or "previous"==request.split()[0]:
                            
                            if len(request.split())==3:
                                first,last=request.split()[2][1:-1].split(',')
                                first=int(first)
                                last=int(last)
                                write_msg_with_buttons(vk,event.user_id,"Следующие контакты",construct_button_for_invent(vk,dic_rooms,event.user_id,first,last))
                            else:
                                write_msg(vk,event.user_id,"Некорректные входные данные. Такой команды нет.")
                        else:
                            write_msg(vk,event.user_id, "Некорректные входные данные. Такой команды нет.")

                    elif "game prepare"==my_room.status:

                        if request.split()[0] == "coordinate":
                            coordinate(vk,my_room,event.user_id,request)
                            draw_labirint.draw_labirint(my_room)
                            send_image.send_image_to_all_viewers(vk,my_room.viewers,"images/"+str(my_room.hash)+".png")
                            write_msg_with_buttons(vk,event.user_id,"Вы можете пользоваться кнопками быстрых ответов!",keys_standart)

                        else: #при высадке и некорректном вводе
                            coordinate(vk,my_room,event.user_id,"coordinate "+request)
                            draw_labirint.draw_labirint(my_room)
                            send_image.send_image_to_all_viewers(vk,my_room.viewers,"images/"+str(my_room.hash)+".png")
                            write_msg_with_buttons(vk,event.user_id,"Вы можете пользоваться кнопками быстрых ответов!",keys_standart)

                    elif "game"==my_room.status:

                        if request.split()[0] == "get":
                            get(vk,my_room,dic_rooms,event.user_id)
                            draw_labirint.draw_labirint(my_room)
                            send_image.send_image_to_all_viewers(vk,my_room.viewers,"images/"+str(my_room.hash)+".png")

                        elif request.split()[0] == "go":
                            if 2==len(request.split()):
                                go(vk,my_room,dic_rooms,event.user_id,request)
                                draw_labirint.draw_labirint(my_room)
                                send_image.send_image_to_all_viewers(vk,my_room.viewers,"images/"+str(my_room.hash)+".png")
                            else:
                                write_msg(vk,event.user_id, "Некорректные входные данные. Такой команды нет.")

                        elif request.split()[0] == "put":
                            put(vk,my_room,dic_rooms,event.user_id)
                            draw_labirint.draw_labirint(my_room)
                            send_image.send_image_to_all_viewers(vk,my_room.viewers,"images/"+str(my_room.hash)+".png")

                        elif request=="show labirint":

                            draw_labirint.draw_labirint(my_room)
                            #draw_labirint.draw_labirint(my_room)
                            send_image.send_image(vk,event.user_id,"images/"+str(my_room.hash)+".png")

                        elif request.split()[0]=="ruin":
                            if 2==len(request.split()):
                                ruin(vk,my_room,dic_rooms,event.user_id,request)
                                draw_labirint.draw_labirint(my_room)
                                send_image.send_image_to_all_viewers(vk,my_room.viewers,"images/"+str(my_room.hash)+".png")
                            else:
                                write_msg(vk,event.user_id, "Некорректные входные данные. Такой команды нет.")

                        elif request.split()[0]=="bang":
                            if 2==len(request.split()):
                                bang(vk,my_room,dic_rooms,event.user_id,request)
                                draw_labirint.draw_labirint(my_room)
                                send_image.send_image_to_all_viewers(vk,my_room.viewers,"images/"+str(my_room.hash)+".png")
                            else:
                                write_msg(vk,event.user_id, "Некорректные входные данные. Такой команды нет.")

                        elif request.split()[0]=="exit":
                            exit(vk,event.user_id,dic_rooms)
                        elif request.split()[0]=="info":
                            write_msg(vk,event.user_id, open('info_text.txt').read())
                        else:
                            write_msg(vk,event.user_id, "Некорректные входные данные. Такой команды нет.")
                    else:
                        for i in range(len(my_room.users)):
                            write_msg(vk,my_room.users[i], "Game Over")
            
            except Exception as e:
                print(e)
                for room in Rooms:
                    for user in room.users:
                        print(user)
                        write_msg(vk,user, "Sorry. Server Error. I may play now.")
  