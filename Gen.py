from math import*
import random
from tkinter import *

class cage:
            """клетка поля"""
            def __init__(self, x, y, status,rivers,holes,N):
                self.x = x
                self.y = y
                self.non_next=x*N+y
                self.status = status
                if self.status[-1]=='k':
                    self.tres=1
                else:
                    self.tres=0
                if 'r'==status or 'u'==status:
                    for i in range(len(rivers)):
                        for j in range(len(rivers[i])):
                            if x==rivers[i][j][0] and y==rivers[i][j][1]:
                                self.river_number=i
                                self.next=rivers[i][max(0,j-2)][0]*N+rivers[i][max(0,j-2)][1]
                elif 'd'==status[0]:
                    for i in range(len(holes)):
                        for j in range(len(holes[i])):
                            if x==holes[i][j][0] and y==holes[i][j][1]:
                                self.hole_number=i
                                self.next=holes[i][(j+1)%len(holes[i])][0]*N+holes[i][(j+1)%len(holes[i])][1]
                else:
                    self.next=x*N+y

                if x!=0:
                    self.up=(x-1)*N+y
                else:
                    self.up=None

                if y!=0:
                    self.left=x*N+y-1
                else:
                    self.left=None

                if x!=N-1:
                    self.down=(x+1)*N+y
                else:
                    self.down=None

                if y!=N-1:
                    self.right=x*N+y+1
                else:
                    self.right=None

def gen_my_map():
    N=4
    N2=N*N
    L=2*N+1
    W=2*N//3
    while True:
        All=N2
        All-=2
        r=4+random.randint(0,2)+random.randint(0,2) #4-8
        All-=r
        s=2+random.randint(0,2)+random.randint(0,1)+random.randint(0,All-6) #2-- All-1
        All-=s
        d=min(All,6)
        All-=d
        if All:
            All-=1
            s+=1
        r+=All
        u=1+random.randint(0,1)+random.randint(0,1)+random.randint(0,1)+random.randint(0,min(0,r-4)) #1-r
        u=min(u,r)
        rr=r-u
        l_rivers=[1]*u
        for i in range(u):
            t=random.randint(0,rr)
            l_rivers[i]+=t
            rr-=t
        l_rivers[0]+=rr
        l_rivers=sorted(l_rivers)[::-1]

        i=0
        global_key=0
        while 0==global_key:
            global_key=1
            key=0
            list_of_rivers=[]
            map=[["*" for i in range(N)] for j in range(N)]
            for i in range(u):
                key=0
                while 0==key:
                    x=random.randint(0,N-1)
                    y=random.randint(0,N-1)
                    if '*'==map[x][y]:
                        key=1
                        map[x][y]='u'
                        list_of_rivers.append([x,y])
                for j in range(l_rivers[i]-1):
                    ker=random.randint(0,3)
                    key2=0
                    key3=0
                    while 0==key2:
                        if 0==ker and x+1<N and '*'==map[x+1][y]:
                            x=x+1
                            map[x][y]='r'
                            key2=1
                            list_of_rivers[i].append(x)
                            list_of_rivers[i].append(y)
                        if 1==ker and y+1<N and '*'==map[x][y+1]:
                            y=y+1
                            map[x][y]='r'
                            key2=1
                            list_of_rivers[i].append(x)
                            list_of_rivers[i].append(y)
                        if 2==ker and x-1>=0 and '*'==map[x-1][y]:
                            x=x-1
                            map[x][y]='r'
                            key2=1
                            list_of_rivers[i].append(x)
                            list_of_rivers[i].append(y)
                        if 3==ker and y-1>=0 and '*'==map[x][y-1]:
                            y=y-1
                            map[x][y]='r'
                            key2=1
                            list_of_rivers[i].append(x)
                            list_of_rivers[i].append(y)
                        key3+=1
                        ker=(ker+1)%4
                        if(key3>5):
                            global_key=0
                            break
                    if 0==global_key:
                        break
                if 0==global_key:
                    break
        rivers=[]
        for r in list_of_rivers:
            t=[]
            for i in range(len(r)//2):
                t.append([r[2*i],r[2*i+1]])
            rivers.append(t)
        cdn=random.randint(0,d)
        cdn=max(cdn,1)
        dyry=[1]*cdn
        i=0
        t=d-cdn
        while t:
            tt=random.randint(0,1)
            dyry[i]+=tt
            t-=tt
            i=(i+1)%cdn
        dyry=sorted(dyry)[::-1]
        list_of_holes=[]
        for i in range(cdn):
            list_of_holes.append([])
            for j in range(dyry[i]):
                key=0
                while 0==key:
                    x=random.randint(0,N-1)
                    y=random.randint(0,N-1)
                    if '*'==map[x][y]:
                        key=1
                        map[x][y]='d'*(i+1)+str(j)
                        list_of_holes[i].append([x,y])

        key=0
        while 0==key:
            x=random.randint(0,N-1)
            y=random.randint(0,N-1)
            if '*'==map[x][y]:
                key=1
                map[x][y]='a'
        key=0
        while 0==key:
            x=random.randint(0,N-1)
            y=random.randint(0,N-1)
            if '*'==map[x][y]:
                key=1
                map[x][y]='m'

        #--------------------------------------------------
        key=0
        while 0==key:
            x=random.randint(0,N-1)
            y=random.randint(0,N-1)
            if '*'==map[x][y]:
                key=1
                map[x][y]='sk'
        key=0
        while 0==key:
            x=random.randint(0,N-1)
            y=random.randint(0,N-1)
            if '*'==map[x][y]:
                key=1
                map[x][y]='sm'
        for i in range(N):
            for j in range(N):
                if map[i][j]=='*':
                    map[i][j]='s'
        bmap=[["*" for i in range(2*N+1)] for j in range(2*N+1)]
        for i in range(N):
            for j in range(N):
                bmap[2*i+1][2*j+1]=map[i][j]
        for i in range(L):
            for j in range(L):
                if (i+j)%2==0 and bmap[i][j]=='*':
                    bmap[i][j]='0'
                if (i==0) or (i==L-1) or (j==0) or (j==L-1):
                    if bmap[i][j]=='*':
                        bmap[i][j]='mw'

        for i in range(N):
            for j in range(N):
                for x in range(N):
                    for y in range(N):
                        if (i,j)!=(x,y) and (   ((i-x),(j-y))==(0,1) or ((i-x),(j-y))==(1,0)   ):
                            if (map[i][j] in {'r','u'}) and (map[x][y] in {'r','u'}) and 'r' in set((map[i][j],map[x][x])):
                                xx=i+x+1
                                yy=j+y+1
                                bmap[xx][yy]='w'
        

        new_map=[cage(i//N,i%N,map[i//N][i%N],rivers,list_of_holes,N) for i in range(N2)]
        #----------------------------------------------------------------------------------------------------------------------------
        h_n=random.randint(N,N2)
        h_n=16
        proverka=0
        while proverka<10000:
            proverka+=1
            for i in range(h_n):  #------------генерация стен
                key=0
                while 0==key:
                    x=random.randint(0,N-1)
                    y=random.randint(0,N-1)
                    pos=random.randint(0,3)
                    if 0==pos and new_map[x*N+y].left!=None:
                        new_map[(new_map[x*N+y].left)%100].right+=100
                        new_map[x*N+y].left+=100
                        key=1
                    if 1==pos and new_map[x*N+y].right!=None:
                        new_map[(new_map[x*N+y].right)%100].left+=100
                        new_map[x*N+y].right+=100
                        key=1
                    if 2==pos and new_map[x*N+y].up!=None:
                        new_map[(new_map[x*N+y].up)%100].down+=100
                        new_map[x*N+y].up+=100
                        key=1
                    if 3==pos and new_map[x*N+y].down!=None:
                        new_map[(new_map[x*N+y].down)%100].up+=100
                        new_map[x*N+y].down+=100
                        key=1
            for i in range(N): #---------------------------------закрываем реки стенами
                for j in range(N):
                    if ('r'==new_map[i*N+j].status or 'u'==new_map[i*N+j].status) and new_map[i*N+j].left!=None and new_map[i*N+j].left<16 and 'r'==new_map[new_map[i*N+j].left].status:
                        new_map[new_map[i*N+j].left].right+=100
                        new_map[i*N+j].left+=100
                    if ('r'==new_map[i*N+j].status or 'u'==new_map[i*N+j].status) and new_map[i*N+j].right!=None and new_map[i*N+j].right<16 and 'r'==new_map[new_map[i*N+j].right].status:
                        new_map[new_map[i*N+j].right].left+=100
                        new_map[i*N+j].right+=100
                    if ('r'==new_map[i*N+j].status or 'u'==new_map[i*N+j].status) and new_map[i*N+j].up!=None and new_map[i*N+j].up<16 and 'r'==new_map[new_map[i*N+j].up].status:
                        new_map[new_map[i*N+j].up].down+=100
                        new_map[i*N+j].up+=100
                    if ('r'==new_map[i*N+j].status or 'u'==new_map[i*N+j].status) and new_map[i*N+j].down!=None and new_map[i*N+j].down<16 and 'r'==new_map[new_map[i*N+j].down].status:
                        new_map[new_map[i*N+j].down].up+=100
                        new_map[i*N+j].down+=100

            for river in rivers: #-----------------------------сносим стены в реке
                for i in range(len(river)-1):
                    if 1==river[i+1][0]-river[i][0]:
                        new_map[river[i+1][0]*N+river[i+1][1]].up%=100
                        new_map[river[i][0]*N+river[i][1]].down%=100
                    if -1==river[i+1][0]-river[i][0]:
                        new_map[river[i+1][0]*N+river[i+1][1]].down%=100
                        new_map[river[i][0]*N+river[i][1]].up%=100

                    if 1==river[i+1][1]-river[i][1]:
                        new_map[river[i+1][0]*N+river[i+1][1]].left%=100
                        new_map[river[i][0]*N+river[i][1]].right%=100
                    if -1==river[i+1][1]-river[i][1]:
                        new_map[river[i+1][0]*N+river[i+1][1]].right%=100
                        new_map[river[i][0]*N+river[i][1]].left%=100
            flag=1
            for k in range(N2):#--------------------------------------------по всем элементам
                test_matrix=[ 0 for i in range(N2)] #-----------------------проверка на связность
                test_matrix[k]=1
                list_of_cages=[k]
                while len(list_of_cages)>0:
                    new_list_of_cages=[]
                    for j in list_of_cages:
                        if new_map[j].status=='d':
                            new_list_of_cages.append(new_map[j].next)
                            if 1==test_matrix[new_list_of_cages[-1]]:
                                new_list_of_cages=new_list_of_cages[:-1:]
                            else:
                                test_matrix[new_list_of_cages[-1]]=1 

                        if new_map[j].left!=None and new_map[j].left<100:
                            if 'r'==new_map[new_map[j].left].status and new_map[j].status not in ['r','u'] :
                                new_list_of_cages.append(new_map[new_map[j].left].next)
                            elif 'd'==new_map[new_map[j].left].status[0]:
                                new_list_of_cages.append(new_map[new_map[j].left].next)
                            else:
                                new_list_of_cages.append(new_map[j].left)

                            if 1==test_matrix[new_list_of_cages[-1]]:
                                new_list_of_cages=new_list_of_cages[:-1:]
                            else:
                                test_matrix[new_list_of_cages[-1]]=1    



                        if new_map[j].right!=None and new_map[j].right<100:
                            if 'r'==new_map[new_map[j].right].status and new_map[j].status not in ['r','u']:
                                new_list_of_cages.append(new_map[new_map[j].right].next)
                            elif 'd'==new_map[new_map[j].right].status[0]:
                                new_list_of_cages.append(new_map[new_map[j].right].next)
                            else:
                                new_list_of_cages.append(new_map[j].right)

                            if 1==test_matrix[new_list_of_cages[-1]]:
                                new_list_of_cages=new_list_of_cages[:-1:]
                            else:
                                test_matrix[new_list_of_cages[-1]]=1

                        if new_map[j].up!=None and new_map[j].up<100:
                            if 'r'==new_map[new_map[j].up].status and new_map[j].status not in ['r','u']:
                                new_list_of_cages.append(new_map[new_map[j].up].next)
                            elif 'd'==new_map[new_map[j].up].status[0]:
                                new_list_of_cages.append(new_map[new_map[j].up].next)
                            else:
                                new_list_of_cages.append(new_map[j].up)

                            if 1==test_matrix[new_list_of_cages[-1]]:
                                new_list_of_cages=new_list_of_cages[:-1:]
                            else:
                                test_matrix[new_list_of_cages[-1]]=1

                        if new_map[j].down!=None and new_map[j].down<100:
                            if 'r'==new_map[new_map[j].down].status and new_map[j].status not in ['r','u']:
                                new_list_of_cages.append(new_map[new_map[j].down].next)
                            elif 'd'==new_map[new_map[j].down].status[0]:
                                new_list_of_cages.append(new_map[new_map[j].down].next)
                            else:
                                new_list_of_cages.append(new_map[j].down)

                            if 1==test_matrix[new_list_of_cages[-1]]:
                                new_list_of_cages=new_list_of_cages[:-1:]
                            else:
                                test_matrix[new_list_of_cages[-1]]=1
                        list_of_cages=new_list_of_cages.copy()

                flag=1
                for i in test_matrix:
                    flag*=i
                if flag:
                    continue
                else:
                    break
            if flag:
                break
            else:
                for i in range(N2):
                    if new_map[i].up!=None:
                        new_map[i].up%=100
                    if new_map[i].left!=None:
                        new_map[i].left%=100
                    if new_map[i].right!=None:
                        new_map[i].right%=100
                    if new_map[i].down!=None:
                        new_map[i].down%=100
        if proverka<10000:
            break





    p=random.randint(0,N-1)#---------------------(-1) - выход
    turn=random.randint(0,3)
    if turn==0:
        new_map[p].up=-1
    if turn==1:
        new_map[p*N+N-1].right=-1
    if turn==2:
        new_map[(N-1)*N+p].down=-1
    if turn==3:
        new_map[p*N].left=-1
    bmap=[["*" for i in range(2*N+1)] for j in range(2*N+1)]
    for i in range(N):
        for j in range(N):

            bmap[2*i+1][2*j+1]=new_map[i*N+j].status

            t=new_map[i*N+j].right
            if t==None:
                bmap[2*i+1][2*j+2]='mw'
            elif t>=100:
                bmap[2*i+1][2*j+2]='w'
            elif t==-1:
                bmap[2*i+1][2*j+2]='E'

            t=new_map[i*N+j].left
            if t==None:
                bmap[2*i+1][2*j]='mw'
            elif t>=100:
                bmap[2*i+1][2*j]='w'
            elif t==-1:
                bmap[2*i+1][2*j]='E'

            t=new_map[i*N+j].up
            if t==None:
                bmap[2*i][2*j+1]='mw'
            elif t>=100:
                bmap[2*i][2*j+1]='w'
            elif t==-1:
                bmap[2*i][2*j+1]='E'

            t=new_map[i*N+j].down
            if t==None:
                bmap[2*i+2][2*j+1]='mw'
            elif t>=100:
                bmap[2*i+2][2*j+1]='w'
            elif t==-1:
                bmap[2*i+2][2*j+1]='E'

    s=""
    s+="rivers:\n"
    s+=str(len(rivers))+"\n"
    for r in rivers:
        s+=str(len(r))+"\n"
        for i in range(len(r)):
            s+=str(r[i][0])+' '+str(r[i][1])+'\n'
    s+="holes:\n"
    s+=str(len(list_of_holes))+'\n'
    for r in list_of_holes:
        s+=str(len(r))+'\n'
        for i in range(len(r)):
            s+=str(r[i][0])+' '+str(r[i][1])+'\n'
    s+="map parameters:\n"
    s+=str(N)+'\n'
    for i in range(N2):
        s+=str(new_map[i].x*N+new_map[i].y)+' '
        s+=str(new_map[i].up)+' '
        s+=str(new_map[i].right)+' '
        s+=str(new_map[i].down)+' '
        s+=str(new_map[i].left)+' '
        s+=new_map[i].status+' '
        s+=str(new_map[i].next)+'\n'
    h=hash(s)
    address="MAP_LIBRARY/"+ str(h)+ ".txt"
    f = open(address, "w")
    f.write(s)
    f.close()
    
    return [rivers,list_of_holes,new_map,h]

