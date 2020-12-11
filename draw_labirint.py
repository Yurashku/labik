from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from get_name_and_icon import *
def draw_labirint(my_room):    
    image = QImage(400, 400, QImage.Format_RGB32)

    painter = QPainter(image)
    painter.setBrush(Qt.white)
    painter.setPen(Qt.white)
    painter.drawRect(0, 0, 400, 400)
    pen = QPen(Qt.black, 4, Qt.SolidLine)
    pen_med=QPen(Qt.red,20,Qt.SolidLine)
    pen_river=QPen(Qt.red,4,Qt.SolidLine)
    pen_hole=QPen(Qt.yellow,10,Qt.DotLine)
    for i in range(4):
        for j in range(4):
            if my_room.map[i*4+j].status[0]=='u':
                painter.setBrush(Qt.blue)
            elif my_room.map[i*4+j].status[0]=='r':
                painter.setBrush(Qt.darkBlue)
            elif "s"==my_room.map[i*4+j].status[0]:
                painter.setBrush(Qt.darkGreen)
            elif "d"==my_room.map[i*4+j].status[0]:
                painter.setBrush(Qt.gray)
            elif "a"==my_room.map[i*4+j].status:
                painter.setBrush(Qt.red)
            else:
                painter.setBrush(Qt.white)
            painter.drawRect(j*100, i*100, (i+1)*100, (j+1)*100)
            if "a"==my_room.map[i*4+j].status:
                arcenal_image=QImage("arcenal_small.png")
                #arcenal.scaled(100, 100,Qt.KeepAspectRatio)
                painter.drawImage(j*100+10,i*100+10,arcenal_image)
            if 1==my_room.map[i*4+j].tres:
                treasure_image=QImage("treasure_small.png")
                painter.drawImage(j*100+10,i*100+10,treasure_image)
    painter.setPen(pen)        
    for i in range(4):
        for j in range(4):
            if my_room.map[i*4+j].left==None or my_room.map[i*4+j].left>=100:
                painter.drawLine(j*100+5, i*100+5, j*100+5, i*100+95)
            if my_room.map[i*4+j].right==None or my_room.map[i*4+j].right>=100:
                painter.drawLine(j*100+95, i*100+5, j*100+95, i*100+95)
            if my_room.map[i*4+j].up==None or my_room.map[i*4+j].up>=100:
                painter.drawLine(j*100+5, i*100+5, j*100+95, i*100+5)
            if my_room.map[i*4+j].down==None or my_room.map[i*4+j].down>=100:
                painter.drawLine(j*100+5, i*100+95, j*100+95, i*100+95)
            if "m"==my_room.map[i*4+j].status:
                painter.setPen(pen_med)
                painter.drawLine(j*100+50,i*100+20,j*100+50,i*100+80)
                painter.drawLine(j*100+20,i*100+50,j*100+80,i*100+50)
                painter.setPen(pen)
            if "d"==my_room.map[i*4+j].status[0]:
                painter.setBrush(Qt.gray)
                painter.drawEllipse(QPoint(j*100+50, i*100+50), 30,30)
    painter.setPen(pen_river) 
    for river in my_room.rivers:
        for i in range(len(river)-1):
            painter.drawLine(river[i][1]*100+50,river[i][0]*100+50,river[i+1][1]*100+50,river[i+1][0]*100+50)
    painter.setPen(pen_hole) 
    for hole in my_room.holes:
        for i in range(len(hole)):
            painter.drawLine(hole[i][1]*100+50,hole[i][0]*100+50,hole[(i+1)%len(hole)][1]*100+50,hole[(i+1)%len(hole)][0]*100+50)
    painter.setPen(pen)     
    for player in my_room.players:
        icon=QImage(player.icon)
        painter.drawImage((player.coord%4)*100+35,(player.coord//4)*100+35,icon)
    painter.end()

    image.save("images/"+str(my_room.hash)+".png", "PNG")
    
def draw_waiting(vk,my_room):
    image = QImage(400, 100, QImage.Format_RGB32)
    painter = QPainter(image)
    painter.setBrush(Qt.gray)
    painter.setPen(Qt.white)
    painter.drawRect(0, 0, 400, 100)
    pen = QPen(Qt.black, 4, Qt.SolidLine)
    unknown=QImage("unknown_small.png")
    margins=[0,175,140,105,70,35]
    for i in range(my_room.num):
        if i<len(my_room.users):
            icon=QImage(get_image(vk,my_room.users[i]))
            painter.drawImage(margins[my_room.num]+i*70,25,icon)
        else:
            painter.drawImage(margins[my_room.num]+i*70,25,unknown)
    painter.end()
    image.save("images/waiting"+str(my_room.hash)+".png", "PNG")         