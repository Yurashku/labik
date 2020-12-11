from func_main import *
import pandas as pd
import numpy as np
from datetime import datetime
def send_game_to_database(my_room):  
    games=pd.read_csv("bases/games.csv")
    it_game={"room_id":str(my_room.id), 
             "winner_id":str(my_room.winner_id),
             "start_time":my_room.start_time,
             "finish_time":my_room.finish_time}
    games=games.append(it_game,ignore_index=True)
    with open("bases/games.csv",mode='w',encoding="utf-8") as file:
        games.to_csv(file,index=False)
    
    records=pd.read_csv("bases/records.csv")
    for user in my_room.users:
        it_record={"user_id":user,"game_id":my_room.id}
        records=records.append(it_record,ignore_index=True)
    with open("bases/records.csv",mode='w',encoding="utf-8") as file:
        records.to_csv(file,index=False)
        

def update_users_in_database(vk,user_id):
    
    user=vk.method("users.get",{'user_ids':str(user_id)})
    full_name = user[0]['first_name'] +  ' ' + user[0]['last_name']
    
    if 0==len(full_name):
        return 0
    players=pd.read_csv("bases/players.csv")
    if players[players["user_id"]==user_id].empty:
        players=players.append({"user_id":user_id,
                                "user_name":full_name,
                                "first_visit":datetime.now().strftime("%d-%m-%Y %H:%M"),
                                "last_visit":datetime.now().strftime("%d-%m-%Y %H:%M"),
                                "raiting":1500},ignore_index=True)
    else:
        players.loc[players["user_id"]==user_id,"last_visit"]=datetime.now().strftime("%d-%m-%Y %H:%M")
    #print(players)
    with open("bases/players.csv",mode='w',encoding="utf-8") as file:
        players.to_csv(file,index=False)
        
def get_kontakts(user_id):
    kontakts=pd.read_csv("bases/kontakts.csv")
    return kontakts[kontakts["user_id1"]==user_id]["user_id2"].drop_duplicates().to_list()

def put_kontaks(user_id1,user_id2): #исправить добавление кратных пар и  себя самого
    kontakts=pd.read_csv("bases/kontakts.csv")
    
    it_kontakt={"user_id1":user_id1, "user_id2":user_id2}
    kontakts=kontakts.append(it_kontakt,ignore_index=True)
    with open("bases/kontakts.csv",mode='w',encoding="utf-8") as file:
        kontakts.to_csv(file,index=False)

def get_name_by_id(user_id):
    players=pd.read_csv("bases/players.csv")
    return players[players["user_id"]==user_id]["user_name"].to_list()[0]

def get_raiting_by_id(user_id):
    players=pd.read_csv("bases/players.csv")
    return players[players["user_id"]==user_id]["raiting"].to_list()[0]

def update_raiting(user_id,new_raiting):
    players=pd.read_csv("bases/players.csv")
    players.loc[players["user_id"]==user_id,"raiting"]=new_raiting
    with open("bases/players.csv",mode='w',encoding="utf-8") as file:
        players.to_csv(file,index=False)
        
def get_top10(): #сделать топ n<=100
    players=pd.read_csv("bases/players.csv")
    return str(players.sort_values("raiting",ascending=False)[["user_id","user_name","raiting"]].head(10))

def feedback(user_id, text):
    feedback=pd.read_csv("bases/feedback.csv")
    this_feedback={"user_id":user_id,
                   "text":text}
    feedback=feedback.append(this_feedback,ignore_index=True)
    with open("bases/feedback.csv",mode='w',encoding="utf-8") as file:
        feedback.to_csv(file,index=False)
        
        
def get_room_ids():
    records=pd.read_csv("bases/records.csv")
    return list(records["game_id"].values)