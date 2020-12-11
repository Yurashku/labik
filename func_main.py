import vk_api
import random
import requests
import Gen
import sys
import draw_labirint
import send_image
import requests
import bs4 as bs4 #можно удалить
import urllib
#import urllib.reques
#import event.user_id
import get_name_and_icon
from buttons import *
from datetime import datetime
import work_with_database
import numpy as np
word_dic={"s":" s(суша)","r":" r(река).","u":" u(устье).","d":" d(телепорт).","a":" a(арсенал).","m":" m(медпункт)."}
class Player:
    def __init__(self,id_user,x,y):
        self.x=3-int(y)
        self.y=int(x)
        self.coord=self.x*4+self.y
        self.id=id_user
        self.bullet=1
        self.grenade=2
        self.treasure=0
        self.wound=0
        self.name=""
        self.icon=""
        
class Room:

    def __init__(self,user_id,num=3):
        self.num=num
        self.id=random.randint(0,1000000)
        self.users=[user_id]
        self.real_num=1
        self.rivers,self.holes,self.map,self.hash=Gen.gen_my_map()
        self.status="create"
        self.med_open=0
        self.players=[]
        self.viewers=[]
        self.winner_id=None
        self.start_time=datetime.now().strftime("%d-%m-%Y %H:%M")
        
    def add_user(self,user_id):
        if(len(self.users)<self.num and self.status=="create"):
            self.users.append(user_id)
            return True
        else:
            return False
    def start(self):
        self.status="game prepare"
        self.turn_number=0
    def finish(self,vk,dic_rooms):
        for user in self.users:
            if dic_rooms.get(user,None)!=None and dic_rooms.get(user,None).id==self.id:
                dic_rooms.pop(user)
                send_image.send_image(vk,user,"images/"+str(self.hash)+".png")
                write_msg_with_buttons(vk,user,"Вы закончили партию! Если Вам понравилась игра Ваших противников, то Вы можете добавить их в список Ваших контактов для того, чтобы сыграть с ними в следующий раз.",construct_button_for_add_friends(self))
        self.finish_time=datetime.now().strftime("%d-%m-%Y %H:%M")
        work_with_database.send_game_to_database(self)
        self.status="end"
        raitings=[work_with_database.get_raiting_by_id(user) for user in self.users]##############рейтинг
        middle_raiting=count_middle_raiting(raitings)
        for i in range(len(raitings)):
            if self.winner_id!=None and self.winner_id==self.users[i]:
                res=recount_raiting(raitings[i],middle_raiting,1)
            else:
                res=recount_raiting(raitings[i],middle_raiting,0)
            work_with_database.update_raiting(self.users[i],res)
            write_msg(vk,self.users[i],"Результат игры "+str(self.id)+": "+str(raitings[i])+"->"+str(res))
            
    def add_player(self,id_user,x,y):
        self.players.append(Player(id_user,x,y))
        
def write_msg(vk,user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'random_id': random.randint(0,1000000000),'message': message})

def write_to_all(vk,dic_rooms,my_room,user_id,text1,text2):
    for user in my_room.users:
        if dic_rooms.get(user,None)!=None and my_room.id==dic_rooms.get(user,None).id:
            if user_id!=user:
                write_msg(vk,user,text1)
            else:
                write_msg(vk,user,text2)
        
                

def write_msg_with_buttons(vk,user_id,message,keyboard):
    vk.method('messages.send', {'user_id': user_id, 'random_id': random.randint(0,1000000000),'message': message,'keyboard':keyboard.get_keyboard()})

def send_keybroad(vk,user_id,keyboard):
    vk.method('messages.send',{'user_id': user_id, 'random_id': random.randint(0,1000000000),'keyboard':keyboard.get_keyboard(),'message':"Вы можете отправить быстрый ответ"})
    
def send_keybroad_to_all(vk,my_room,dic_rooms,keyboard):
    for user in my_room.users:
        #print(my_room.id,dic_rooms.get(user,None).id)
        if dic_rooms.get(user,None)!=None and my_room.id==dic_rooms.get(user,None).id:
            
            send_keybroad(vk,user,keyboard)
            
def in_one_river(rivers,coord1,coord2):
    key=False
    for river in rivers:
        cur_river=[x[0]*4+x[1] for x in river]        
        if coord1 in cur_river and coord2 in cur_river:          
            key=True
            break
    return key

def next_move(vk,my_room,dic_rooms):
    if my_room.status!="end":
        my_room.turn_number+=1
        while 2==my_room.players[my_room.turn_number%len(my_room.players)].wound:
            if dic_rooms.get(my_room.players[my_room.turn_number%len(my_room.players)].id,None)!=None and dic_rooms.get(my_room.players[my_room.turn_number%len(my_room.players)].id,None).id==my_room.id:
                write_msg(vk,my_room.players[my_room.turn_number%len(my_room.players)].id,"К сожалению, Вы выбыли из игры, поэтому пропускаете ход.")
            my_room.turn_number+=1 
    
        write_msg(vk,my_room.players[my_room.turn_number%len(my_room.players)].id,"Ваш ход.")
        
def lose_treasure(vk,my_room,dic_rooms,my_player):
    if 1==my_player.treasure:
        my_player.treasure=0
        my_room.map[my_player.coord].tres=1
        write_to_all(vk,dic_rooms,my_room,my_player.id,"Игрок "+my_player.name+" был ранен и потерял сокровище.","Вы были ранены и потеряли сокровище.")
    if 1==my_player.wound:
        my_room.real_num-=1
    if 0==my_room.real_num:
        my_room.finish(vk,dic_rooms)

def count_middle_raiting(raitings):
    res=0
    for raiting in raitings:
        res+=raiting*raiting
    return res**0.5

def recount_raiting(my_raiting,middle_raiting,wins_or_lose_flag):
    if my_raiting>2000:
        k=10
    elif my_raiting>1500:
        k=20
    elif my_raiting>1000:
        k=30
    else:
        k=40
    Ea=1./(1.+10.**((middle_raiting-my_raiting+0.)/600.))
    return my_raiting+k*(wins_or_lose_flag-Ea)
                            
def get_coord(request):
    x=random.randint(0,3)
    y=random.randint(0,3)
    li=request.split()
    if 3==len(li) and li[1].isdigit() and li[2].isdigit() and int(li[1]) in range(4) and int(li[2]) in range(4):
        x=int(li[1])
        y=int(li[2])
    elif 2==len(li) and li[1].isdigit() and int(li[1]) in range(16):
        y=4-int(li[1])//4
        x=int(li[1])%4
    return [x,y]
  
def generate(vk,Rooms,dic_rooms,user_id,request):
    using_id=[*[x.id for x in Rooms],*work_with_database.get_room_ids()]
    if 2==len(request.split()) and request.split()[1].isdigit() and int(request.split()[1]) in range(1,6):
        my_room=Room(user_id,int(request.split()[1]))
        
        while my_room.id in using_id:
            my_room=Room(user_id,int(request.split()[1]))
    else:
        my_room=Room(user_id)
        while my_room.id in using_id:
            my_room=Room(user_id)
            
    Rooms.append(my_room)
    dic_rooms[user_id]=my_room
    write_msg(vk,user_id, "Создана комната "+str(my_room.id))
    if 1==my_room.num:
        start(vk,my_room)
    
    #my_room.viewers.append(user_id)

def connect(vk,Rooms,dic_rooms,user_id,request):
    if 2==len(request.split()):
        for room in Rooms:
            key=0
            if str(room.id)==request.split()[1]:
                #print(user_id)
                key=1
                if room.add_user(user_id):
                    write_msg(vk,user_id, "Вы успешно присоедеились к игре.") 
                    dic_rooms[user_id]=room
                    room.real_num+=1
                    if len(room.users)==room.num and "create"==room.status:
                        start(vk,room)
                else:
                    write_msg(vk,user_id, "Комната, в которую Вы попытались зайти, -полна.") 
            if(0==key):
                write_msg(vk,user_id, "К сожалению, комнаты с таким идентификационным номером не существует.")

    elif 1==len(request.split()):
        for room in Rooms:
            if room.add_user(user_id):
                write_msg(vk,user_id, "Вы успешно присоедеились к игре.") 
                dic_rooms[user_id]=room
                room.real_num+=1
                if len(room.users)==room.num and "create"==room.status:
                    start(vk,room)
                break
        if None==dic_rooms.get(user_id,None):
            write_msg(vk,user_id, "Все комнаты заполнены. Вы можете создать свою игровую комнату. Для этого испоьзуйте команду generate")
    else:
        write_msg(vk,user_id, "Ошибка ввода. Правильная команда connect room_id, где room_id-ключ комнаты.")
            
def view(vk,Rooms,dic_rooms,user_id,request):#можно починить
    for room in Rooms:
        key=0
        if str(room.id)==request.split()[1]:
            print("eeeeeee\n")
            room.viewers.append(user_id)
            write_msg(vk,user_id, "Connection is valid") 
            dic_rooms[user_id]=room
            key=1
        if(0==key):
            write_msg(vk,user_id, "Incorrect room id")
            
def start(vk,my_room):
    if my_room.status!="create":
        write_msg(vk,user, "Игра уже началась.")
    else:
        my_room.start()
        for i in range(len(my_room.users)):
            write_msg(vk,my_room.users[i], "Игра началась.")#TODO написать правила, отправить картинку

            if i!=my_room.turn_number:
                write_msg(vk,my_room.users[i], "Сейчас не Ваш ход. Подождите, пока другие игроки высадятся.")
            else:
                write_msg_with_buttons(vk,my_room.users[i],"Введите координаты клетки, в которую Вы хотели бы высадиться. ",keys_coord)
                #write_msg(vk,my_room.users[i], "Put your start coordinates")
           
        
def coordinate(vk,my_room,user_id,request):
    
    if my_room.turn_number>=len(my_room.users):
         write_msg(vk,user_id, "Высадка завершена.")

    elif my_room.users[my_room.turn_number%len(my_room.users)]==user_id:
        my_room.add_player(user_id,*get_coord(request))
        my_room.players[-1].name,my_room.players[-1].icon=get_name_and_icon.get_name_and_image(vk,user_id)
        if "m"==my_room.map[my_room.players[-1].coord].status[0]:
            my_room.med_open=1
        my_room.players[-1].coord=my_room.map[my_room.players[-1].coord].next
        my_room.turn_number+=1

        if my_room.users[-1]==user_id:
            for i in range(len(my_room.users)):
                write_msg(vk,my_room.users[i], '''Все игроки высадились в лабиринт!\n
                Вы находитесь в '''+word_dic[my_room.map[my_room.players[i].coord].status[0]])
                if my_room.map[my_room.players[i].coord].tres:
                    write_msg(vk,my_room.users[i], "Здесь находится сокровище. Вы можете взять его.")
        for i in range(len(my_room.users)):
            if i==my_room.turn_number:
                #write_msg(vk,my_room.users[i], "Put your start coordinates")
                write_msg_with_buttons(vk,my_room.users[i],"Введите координаты клетки, в которую Вы хотели бы высадиться.",keys_coord)
            elif i==my_room.turn_number%len( my_room.users):
                write_msg(vk,my_room.users[i], "Ваш ход.")
            else:
                write_msg(vk,my_room.users[i], "Подождите своего хода.")
    else:
        write_msg(vk,user_id, "Сейчас не Ваша очередь ходить. Подождите других игроков.")
    if my_room.turn_number==len(my_room.users):
        my_room.status="game"
    

        
def get(vk,my_room,dic_rooms,user_id):
    pl_num=my_room.turn_number%len(my_room.users)
    if my_room.users[pl_num]!=user_id:
        write_msg(vk,user_id, "Сейчас не Ваша очередь ходить. Подождите других игроков.")
    elif my_room.map[my_room.players[pl_num].coord].tres and 0==my_room.players[pl_num].wound:
        my_room.map[my_room.players[pl_num].coord].tres=0
        my_room.players[pl_num].treasure=1
        
        write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' 
                 взял сокровище''',"Поздравляем, Вы подняли сокровище!")
        
        next_move(vk,my_room,dic_rooms)
    else:
        write_msg(vk,user_id, "В текущей клетки нет сокровища, или же Вы ранены и не можете поднять его.")
        
        
        
def go(vk,my_room,dic_rooms,user_id,request):
    if my_room.users[my_room.turn_number%len(my_room.users)]!=user_id:
        write_msg(vk,user_id, "Сейчас не Ваша очередь ходить. Подождите других игроков.")
    else:
        pl_num=my_room.turn_number%len(my_room.users)
        if request.split()[1][0] == "u":
            cletka=my_room.map[my_room.players[pl_num].coord].up
            if cletka==None or cletka>=100:

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' 
                        пошел вверх, но уперся в стену.''',"Стена в данном направлении.")
                
            elif -1==cletka and 0==my_room.players[pl_num].treasure:

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' пошел вверх и нашел выход из лабиринта, однако у него нет сокровища, чтобы закончить игру.''',"Вы нашли выход из лабиринта! К сожалению, у Вас нет сокровища, чтобы закончить игру.")
                
            elif -1==cletka and 1==my_room.players[pl_num].treasure:
                
                my_room.winner_id=my_room.players[pl_num].id
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' пошел вверх и нашел выход из лабиринта, у него также имеется сокровище. 
Он победил!!!
Game over!''','''Это выход из лабиринта и у Вас имеется сокровище, чтобы открыть его.
Поздравляем, Вы победили!!!

Вестимо так, Вы победили,
Судьба-на Вашей стороне! 
Пусть знают все враги отныне,
Кто их разбил в лихой борьбе!

Game over!''')
                my_room.finish(vk,dic_rooms)
            else:

                my_room.players[pl_num].coord=my_room.map[cletka].next if not in_one_river(my_room.rivers,cletka,my_room.players[pl_num].coord) else my_room.map[cletka].non_next 

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+'''
                        пошел вверх. Сейчас он находится в '''+word_dic[my_room.map[my_room.players[pl_num].coord].status[0]],"Сечас Вы находитесь в  "+word_dic[my_room.map[my_room.players[pl_num].coord].status[0]])

            next_move(vk,my_room,dic_rooms)


        elif request.split()[1][0] == "d":
            cletka=my_room.map[my_room.players[pl_num].coord].down
            if cletka==None or cletka>=100:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+'''  
                        пошел вниз и уперся в стену.''',"Стена в данном направлении.")

            elif -1==cletka and 0==my_room.players[pl_num].treasure:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' пошел вниз и нашел выход из лабиринта, однако у него нет сокровища, чтобы закончить игру.''',"Вы нашли выход из лабиринта! К сожалению, у Вас нет сокровища, чтобы закончить игру.")

            elif -1==cletka and 1==my_room.players[pl_num].treasure:
                
                my_room.winner_id=my_room.players[pl_num].id
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' пошел вниз . 
и нашел выход из лабиринта, у него также имеется сокровище. 
Он победил!!!
Game over!''','''Это выход из лабиринта и у Вас имеется сокровище, чтобы открыть его.
Поздравляем, Вы победили!!!

Вестимо так, Вы победили,
Судьба-на Вашей стороне! 
Пусть знают все враги отныне,
Кто их разбил в лихой борьбе!

Game over!''')
                my_room.finish(vk,dic_rooms)
            else:

                my_room.players[pl_num].coord=my_room.map[cletka].next if not in_one_river(my_room.rivers,cletka,my_room.players[pl_num].coord) else my_room.map[cletka].non_next 

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' 
                            пошел вниз.Сейчас он находится в  '''+word_dic[my_room.map[my_room.players[pl_num].coord].status[0]],"Сейчас Вы находитесь в  "+word_dic[my_room.map[my_room.players[pl_num].coord].status[0]])


            next_move(vk,my_room,dic_rooms)

        elif request.split()[1][0] == "r":
            cletka=my_room.map[my_room.players[pl_num].coord].right
            if cletka==None or cletka>=100:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+'''
                         пошел вправо и уперся в стену.''',"Стена в данном направлении.")

            elif -1==cletka and 0==my_room.players[pl_num].treasure:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' пошел вправо и нашел выход из лабиринта, однако у него нет сокровища, чтобы закончить игру.''',"Вы нашли выход из лабиринта! К сожалению, у Вас нет сокровища, чтобы закончить игру.")

            elif -1==cletka and 1==my_room.players[pl_num].treasure:
                
                my_room.winner_id=my_room.players[pl_num].id
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' пошел вправо  
и нашел выход из лабиринта, у него также имеется сокровище. 
Он победил!!!
Game over!''','''Это выход из лабиринта и у Вас имеется сокровище, чтобы открыть его.
Поздравляем, Вы победили!!!

Вестимо так, Вы победили,
Судьба-на Вашей стороне! 
Пусть знают все враги отныне,
Кто их разбил в лихой борьбе!

Game over!''')
                my_room.finish(vk,dic_rooms)
            else:
                
                my_room.players[pl_num].coord=my_room.map[cletka].next if not in_one_river(my_room.rivers,cletka,my_room.players[pl_num].coord) else my_room.map[cletka].non_next 

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+'''
                         пошел вправо. Сейчас он находится в '''+word_dic[my_room.map[my_room.players[pl_num].coord].status[0]],"Сейчас Вы находитесь в   "+word_dic[my_room.map[my_room.players[pl_num].coord].status[0]])

            next_move(vk,my_room,dic_rooms)

        elif request.split()[1][0] == "l":
            cletka=my_room.map[my_room.players[pl_num].coord].left
            if cletka==None or cletka>=100:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+'''
                        пошел влево и уперся в стену.''',"Стена в данном направлении.")
                
            elif -1==cletka and 0==my_room.players[pl_num].treasure:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' пошел влево и нашел выход из лабиринта, однако у него нет сокровища, чтобы закончить игру.''',"Вы нашли выход из лабиринта! К сожалению, у Вас нет сокровища, чтобы закончить игру.")

            elif -1==cletka and 1==my_room.players[pl_num].treasure:
                
                my_room.winner_id=my_room.players[pl_num].id
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+''' пошел влево  
и нашел выход из лабиринта, у него также имеется сокровище. 
Он победил!!!
Game over!''','''Это выход из лабиринта и у Вас имеется сокровище, чтобы открыть его.
Поздравляем, Вы победили!!!

Вестимо так, Вы победили,
Судьба-на Вашей стороне! 
Пусть знают все враги отныне,
Кто их разбил в лихой борьбе!

Game over!''')
                my_room.finish(vk,dic_rooms)
                
            else:

                my_room.players[pl_num].coord=my_room.map[cletka].next if not in_one_river(my_room.rivers,cletka,my_room.players[pl_num].coord) else my_room.map[cletka].non_next 

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+'''
                         пошел влево. Сейчас он находится в '''+word_dic[my_room.map[my_room.players[pl_num].coord].status[0]],"Сейчас Вы находитесь в "+word_dic[my_room.map[my_room.players[pl_num].coord].status[0]])

            next_move(vk,my_room,dic_rooms)

        elif request.split()[1][0] == "t":
            if "d"!=my_room.map[my_room.players[pl_num].coord].status[0]:
                write_msg(vk,user_id, "Вы не можете телепортироваться")
            else:
                my_room.players[pl_num].coord=my_room.map[my_room.players[pl_num].coord].next
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+'''
                         телепортировался.''',"Вы телепортировались.")

                next_move(vk,my_room,dic_rooms)

        else:
            write_msg(vk,user_id, '''Направление пути введено неправильно. Попробуйти написать 
            go l -для движения влево
            go r -для движения вправо 
            go u -для движения вверх
            go d -для движения вниз
            go t -для телепортации''')

        if "a"==my_room.map[my_room.players[pl_num].coord].status[0]:
            my_room.players[pl_num].bullet=3
            my_room.players[pl_num].grenade=3

        if "m"==my_room.map[my_room.players[pl_num].coord].status[0]:
            my_room.players[pl_num].wound=0
            my_room.med_open=1

        if my_room.map[my_room.players[pl_num].coord].tres:
            write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+" нашел сокровище.","Здесь находится сокровище. Вы можете взять его.")

            
            
            
def ruin(vk,my_room,dic_rooms,user_id,request):
    pl_num=my_room.turn_number%len(my_room.users)
    if my_room.users[pl_num]!=user_id:
        write_msg(vk,user_id, "Сейчас не Ваша очередь ходить. Подождите других игроков.")
    elif 0==my_room.players[pl_num].grenade:
        write_msg(vk,user_id, "У Вас закончились гранаты.")
    else:

        my_room.players[pl_num].grenade-=1
        if request.split()[1][0] == "u":
            cletka=my_room.map[my_room.players[pl_num].coord].up
            if None==cletka:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' попытался разрушить верхнюю стену, но она монолитна.',"Эта стена-монолитна. Вы не можете разрушить её.")

            elif -1==cletka:
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' попытался уничтожить верхнюю стену, но это выход из лабиринта',"Это выход из лабиринта.")

            else:
                my_room.map[my_room.players[pl_num].coord].up%=100
                my_room.map[my_room.map[my_room.players[pl_num].coord].up].down%=100

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' взорвал верхнюю стену.',"Путь свободен.")

            next_move(vk,my_room,dic_rooms)

        elif request.split()[1][0] == "d":
            cletka=my_room.map[my_room.players[pl_num].coord].down
            if None==cletka:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' попытался разрушить нижнюю стену, но она монолитна.',"Эта стена-монолитна. Вы не можете разрушить её.")

            elif -1==cletka:
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' попытался уничтожить нижнюю стену, но это выход из лабиринта',"Это выход из лабиринта.")
            else:
                my_room.map[my_room.players[pl_num].coord].down%=100
                my_room.map[my_room.map[my_room.players[pl_num].coord].down].up%=100
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' взорвал нижнюю стену.',"Путь свободен.")


            next_move(vk,my_room,dic_rooms)

        elif request.split()[1][0] == "l":
            cletka=my_room.map[my_room.players[pl_num].coord].left
            if None==cletka:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' попытался разрушить левую стену, но она монолитна.',"Эта стена-монолитна. Вы не можете разрушить её.")
                            
            elif -1==cletka:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' попытался уничтожить левую стену, но это выход из лабиринта',"Это выход из лабиринта.")

            else:
                my_room.map[my_room.players[pl_num].coord].left%=100
                my_room.map[my_room.map[my_room.players[pl_num].coord].left].right%=100

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' взорвал левую стену.',"Путь свободен.")

            next_move(vk,my_room,dic_rooms)

        elif request.split()[1][0] == "r":
            cletka=my_room.map[my_room.players[pl_num].coord].right
            if None==cletka:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' попытался разрушить правую стену, но она монолитна.',"Эта стена-монолитна. Вы не можете разрушить её.")
                          
            elif -1==cletka:
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' попытался уничтожить правую стену, но это выход из лабиринта',"Это выход из лабиринта.")

            else:
                my_room.map[my_room.players[pl_num].coord].right%=100
                my_room.map[my_room.map[my_room.players[pl_num].coord].right].left%=100

                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' взорвал правую стену.',"Путь свободен.")

            next_move(vk,my_room,dic_rooms)
        else:
            write_msg(vk,user_id, '''Направление подрыва введено неправильно. Попробуйти написать 
            ruin l -для взрыва левой стены
            ruin r -для взрыва правой стены 
            ruin u -для взрыва верхней стены
            ruin d -для взрыва нижней стены
            ''')
        
        if "a"==my_room.map[my_room.players[pl_num].coord].status[0]:
            my_room.players[pl_num].bullet=3
            my_room.players[pl_num].grenade=3

        if "m"==my_room.map[my_room.players[pl_num].coord].status[0]:
            my_room.players[pl_num].wound=0
            my_room.med_open=1

            
def put(vk,my_room,dic_rooms,user_id):
    pl_num=my_room.turn_number%len(my_room.users)
    if my_room.users[pl_num]!=user_id:
        write_msg(vk,user_id, "Сейчас не Ваша очередь ходить. Подождите других игроков.")
    elif 1==my_room.players[pl_num].treasure:
        my_room.players[pl_num].treasure=0
        my_room.map[my_room.players[pl_num].coord].tres=1
        
        write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' выложил клад',"Вы выложили клад и можете продолжить свой ход.")
        
    else:
        write_msg(vk,user_id, "У Вас нет сокровища. Вы можете продолжить свой ход.")
        
    
    
def bang(vk,my_room,dic_rooms,user_id,request):
    pl_num=my_room.turn_number%len(my_room.users)
    if my_room.users[pl_num]!=user_id:
        write_msg(vk,user_id, "Сейчас не Ваша очередь ходить. Подождите других игроков.")
    elif 0==my_room.med_open:
        write_msg(vk,user_id, "Никто из игроков еще не нашёл медпункт, поэтому введен мораторий на стрельбу.")
    elif 0==my_room.players[pl_num].bullet:
        write_msg(vk,user_id, "У Вас закончилис патроны.")
    else:
        my_room.players[pl_num].bullet-=1
        bullet_path=my_room.players[pl_num].coord
        wound_list=""
        for player in my_room.players:
            if bullet_path==player.coord and player.id!=user_id and 2!=player.wound:
                lose_treasure(vk,my_room,dic_rooms,player)
                player.wound+=1
                wound_list+=player.name+", "
                
        if 'a'==my_room.map[bullet_path].status[0]:
            lose_treasure(vk,my_room,dic_rooms,my_room.players[pl_num])
            my_room.players[pl_num].wound+=1
            wound_list+=my_room.players[pl_num].name+", "
            
        if request.split()[1][0] == "r":
            while my_room.map[bullet_path].right!=None and my_room.map[bullet_path].right<100 and my_room.map[bullet_path].right!=-1:
                bullet_path=my_room.map[bullet_path].right
                for player in my_room.players:
                    if bullet_path==player.coord and player.id!=user_id and 2!=player.wound:
                        lose_treasure(vk,my_room,dic_rooms,player)
                        player.wound+=1
                        wound_list+=player.name+", "
                if len(wound_list)>0:
                    break

            if 0==len(wound_list):
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' выстрелил вправо, но промахнулся.',"Вы выстрелили вправо и промахнулись.")

            else:
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' выстрелил вправо и попал в '+wound_list[:-2:],"Вы попали в "+wound_list[:-2:])

            next_move(vk,my_room,dic_rooms) 

        elif request.split()[1][0] == "l":
            while my_room.map[bullet_path].left!=None and my_room.map[bullet_path].left<100 and my_room.map[bullet_path].left!=-1:
                bullet_path=my_room.map[bullet_path].left
                for player in my_room.players:
                    if bullet_path==player.coord and player.id!=user_id and 2!=player.wound:
                        lose_treasure(vk,my_room,dic_rooms,player)
                        player.wound+=1
                        wound_list+=player.name+", "
                if len(wound_list)>0:
                    break

            if 0==len(wound_list):
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' выстрелил влево, но промахнулся.',"Вы выстрелили влево и промахулись.")

            else:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' выстрелил влево и попал в '+wound_list[:-2:],"Вы попали в "+wound_list[:-2:])

            next_move(vk,my_room,dic_rooms)                 

        elif request.split()[1][0] == "u":
            while my_room.map[bullet_path].up!=None and my_room.map[bullet_path].up<100 and my_room.map[bullet_path].up!=-1:
                bullet_path=my_room.map[bullet_path].up
                for player in my_room.players:
                    if bullet_path==player.coord and player.id!=user_id and 2!=player.wound:
                        lose_treasure(vk,my_room,dic_rooms,player)
                        player.wound+=1
                        wound_list+=player.name+", "
                if len(wound_list)>0:
                    break

            if 0==len(wound_list):
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' выстрелил вверх, но промахнулся.',"Вы выстрелили вверх и промахнулись.")


            else:
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' выстрелил вверх и попал в '+wound_list[:-2:],"Вы попали в "+wound_list[:-2:])
                
            next_move(vk,my_room,dic_rooms) 

        elif request.split()[1][0] == "d":
            while my_room.map[bullet_path].down!=None and my_room.map[bullet_path].down<100 and my_room.map[bullet_path].down!=-1:
                bullet_path=my_room.map[bullet_path].down
                for player in my_room.players:
                    if bullet_path==player.coord and player.id!=user_id and 2!=player.wound:
                        lose_treasure(vk,my_room,dic_rooms,player)
                        player.wound+=1
                        wound_list+=player.name+", "
                if len(wound_list)>0:
                    break

            if 0==len(wound_list):
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+ ' выстрелил вниз, но промахнулся.',"Вы выстрелили вниз и промахнулись.")

            else:
                
                write_to_all(vk,dic_rooms,my_room,my_room.users[pl_num],"Игрок "+my_room.players[pl_num].name+' выстрелил вниз и попал в '+wound_list[:-2:],"Вы выстрелили вниз и попали в "+wound_list[:-2:])

            next_move(vk,my_room,dic_rooms)
        else:
            write_msg(vk,my_room.users[pl_num], '''Направление стрельбы введено неправильно. Попробуйти написать 
            bang l -для выстрела влево
            bang r -для выстрела вправо 
            bang u -для выстрела вверх
            bang d -для выстрела вниз
            ''')
                            
        if "a"==my_room.map[my_room.players[pl_num].coord].status[0]:
            my_room.players[pl_num].bullet=3
            my_room.players[pl_num].grenade=3

        if "m"==my_room.map[my_room.players[pl_num].coord].status[0]:
            my_room.players[pl_num].wound=0
            my_room.med_open=1                
                            
def exit(vk,user_id,dic_rooms):
    if dic_rooms.get(user_id,None)!=None:
        my_room=dic_rooms.pop(user_id)
        room_id=str(my_room.id)
        write_msg(vk,user_id,"Вы покинули комнату "+room_id)
        
        for player in my_room.players:
            if user_id==player.id:
                my_player=player
                break
        my_player.wound=2
        write_to_all(vk,dic_rooms,my_room,user_id,"Игрок "+my_player.name+" покинул комнату","you exit")
        if 1==my_player.treasure:
            my_player.treasure=0
            my_room.map[my_player.coord].tres=1
            write_to_all(vk,dic_rooms,my_room,user_id,"Игрок "+my_player.name+" потерял сокровище","you exit")
        my_room.real_num-=1
        if 0==my_room.real_num:
            my_room.finish(vk,dic_rooms)
        draw_labirint.draw_labirint(my_room)
        send_image.send_image(vk,user_id,"images/"+str(my_room.hash)+".png")
        write_msg_with_buttons(vk,user_id,"Вы можете начать новую игру! Если Вам понравилась игра Ваших противников, то Вы можете добавить их в список Ваших контактов для того, чтобы сыграть с ними в следующий раз.",construct_button_for_add_friends(my_room))
        next_move(vk,my_room,dic_rooms)
        
