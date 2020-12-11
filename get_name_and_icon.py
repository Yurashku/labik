from urllib.request import urlretrieve
import vk_api
import random
import requests
import Gen
import sys
import draw_labirint
import send_image
import requests
import bs4 as bs4
import urllib.request
from PIL import ImageDraw,Image
def crop_img(profile_img,output):

    def prepare_mask(size, antialias = 2): #меняет формат
        mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
        return mask.resize(size, Image.ANTIALIAS)
    def crop(im, s): #делает круглым
        w, h = im.size
        k = w / s[0] - h / s[1]
        if k > 0: im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
        elif k < 0: im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
        return im.resize(s, Image.ANTIALIAS)

    size = (30, 30)

    im = Image.open(profile_img)
    im = crop(im, size)
    im.putalpha(prepare_mask(size, 4))
    im.save(output)
    

#crop_img(st.split('/')[-1],"output.png")
def get_name_and_image(vk,user_id):
    user=vk.method("users.get",{'user_ids':str(user_id),"fields":"photo_50"})
    full_name = user[0]['first_name'] +  ' ' + user[0]['last_name']
    st=user[0]["photo_50"].split('?')[-2]
    image_name=st.split('/')[-1]
    urlretrieve(st, image_name)
    new_image_name="".join(image_name.split('.')[:-1:])+".png"
    crop_img(image_name,new_image_name)
    return [full_name,new_image_name]

def get_image(vk,user_id):
    user=vk.method("users.get",{'user_ids':str(user_id),"fields":"photo_50"})
    st=user[0]["photo_50"].split('?')[-2]
    image_name=st.split('/')[-1]
    urlretrieve(st, image_name)
    new_image_name="".join(image_name.split('.')[:-1:])+".png"
    im = Image.open(image_name)
    im.save(new_image_name)
    return new_image_name