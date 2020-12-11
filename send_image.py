import vk_api
import random
import requests
import Gen
import sys
import draw_labirint
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key

def send_photo(vk, peer_id, owner_id, photo_id, access_key):
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk.messages.send(
        random_id=get_random_id(),
        peer_id=peer_id,
        attachment=attachment
    )
def send_image(vk,user_id,image_name):
    vk1=vk.get_api()
    upload = VkUpload(vk1)
    send_photo(vk1, user_id, *upload_photo(upload, image_name))
    
def send_image_to_all_viewers(vk,viewers_list,image_name):
    for viewer in viewers_list:
        send_image(vk,viewer,image_name)
        
def safe_send_image_to_all(vk, my_room, dic_rooms,viewers_list,image_name):
    for viewer in viewers_list:
        if dic_rooms.get(viewer,None)!=None and dic_rooms.get(viewer,None)==my_room.id:
            send_image(vk,viewer,image_name)