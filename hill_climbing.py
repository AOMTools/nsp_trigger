#!/usr/bin/python
#lock on ext programsimport numpy as np
#version 1.1
#modified to lock at non-maximum target
from Counter import Countercomm
from CQTdevices import *
import time
import zmq
from sys import exit
import subprocess as sp
import timeit
from sys import path
import numpy as np
from init_devices import *
import Errors
#path.append("/home/qitlab/programs/CQTdevices/")
#from tempRH import *



'''
#Setup communication with Cavity_retreat
##############################################################################################
context = zmq.Context()
#  Socket to talk to server
print ("Connecting to the retreat controller server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556")
'''

def setV(Vx,Vy):
    '''
    set an absolute voltage to piezo via delegating to cavity_retreat controller
    '''
    #socket.send("SetVolt5 0")
    #message = socket.recv()
    command1="SetVolt5 "+str(Vy)
    command2="SetVolt6 "+str(Vx)
    socket.send(command1)
    message=socket.recv()
    socket.send(command2)
    message=socket.recv()

'''
def getCount(miniusb,channel=0,average=10,c=0):
    #getCount from miniusb apd
    counts=[]
    for i in range(average):
        counts.append(miniusb.get_counts(channel))
    average_count=np.mean(counts)
    max_count=np.max(counts)
    if c==0:
        return average_count
    else:
        return (average_count,max_count)
'''
'''
def getCount(Vx,Vy,channel=0,average=10,c=0):
    #getCount simulated
    counts=[]
    i=None
    #print(Vx)
    for idx,elem in enumerate(Vsim):
        #print(elem)
        if abs(elem[0]-Vx)<1e-4 and abs(elem[1]-Vy)<1e-4:
            i=idx
    return(i,simdat[i,2])
    '''
def getPower(analogIO,channel=0,average=100):
    #Get the P810 transmission power on photodetector
    power=np.zeros(average)
    for i in range(average):
        power[i]=analogIO.get_voltage(channel)
    return np.mean(power)
def create_rastering_pattern(rangeVx,rangeVy,stepV):
    numStepx=int(rangeVx/stepV)
    numStepy=int(rangeVy/stepV)
    xgrid = np.arange(-numStepx ,numStepx+1)*stepV
    ygrid = np.arange(-numStepy ,numStepy+1)*stepV
    xscan=[]
    yscan=[]
    for i, yi in enumerate(ygrid):
        xscan.append(xgrid[::(-1)**i]) # reverse when i is odd
        yscan.append(np.ones_like(xgrid) * yi)
    xscan = np.concatenate(xscan)
    yscan = np.concatenate(yscan)
    return (xscan,yscan)
def patterns(d):
    #painful and amateur coding here
    xscan9=[s,s,0]
    yscan9=[0,s,s]

    xscan7=[0,-s,-s]
    yscan7=[s,s,0]

    xscan1=[-s,-s,0]
    yscan1=[0,-s,-s]

    xscan2=[-s,0,s]
    yscan2=[-s,-s,-s]

    xscan8=[-s,0,s]
    yscan8=[s,s,s]

    xscan3=[0,s,s]
    yscan3=[-s,-s,0]

    xscan4=[s,s,s]
    yscan4=[-s,0,s]

    xscan6=[-s,-s,-s]
    yscan6=[s,0,-s]

    if d==1:
        x=xscan1
        y=yscan1
    elif d==2:
        x=xscan2
        y=yscan2
    elif d==3:
        x=xscan3
        y=yscan3
    elif d==4:
        x=xscan4
        y=yscan4
    elif d==9:
        x=xscan9
        y=yscan9
    elif d==6:
        x=xscan6
        y=yscan6
    elif d==7:
        x=xscan7
        y=yscan7
    elif d==8:
        x=xscan8
        y=yscan8
    return(x,y)
def scouting(V0x,V0y,tref,step=0.01,m=0):
    #scanning around the setpoint in a square pattern and get the Tcount
    #for each point
    rangeVx=step
    rangeVy=step
    stepV=step
    (xscan,yscan)=create_rastering_pattern(rangeVx,rangeVy,stepV)
    Tcount=[]
    for i in range(np.size(xscan)):
        if i!=4:
            setV(xscan[i]+V0x,yscan[i]+V0y)
            #print(xscan[i]+V0x,yscan[i]+V0y)

    #            (idx,T)=getCount(xscan[i]+V0x,yscan[i]+V0y)
            time.sleep(0.5)
            if m==0:
                T=getCount(miniusb,average=50)
            elif m==1:
                T=getPower(analogIO,average=200)
            Tcount.append(T)
        else:
            Tcount.append(0)

    Tcount=np.asarray(Tcount)
    Tcount=abs(Tcount-tref)
    maxp=np.argmin(Tcount)
    d=maxp
    return (xscan[maxp],yscan[maxp],d)
def getCount(miniusb,channel=0,average=10,c=0):
    #getCount from miniusb apd
    counts=[]
    for i in range(average):
        counts.append(miniusb.get_counts(channel))
    average_count=np.mean(counts)
    max_count=np.max(counts)
    if c==0:
        return average_count
    else:
        return (average_count,max_count)
def hill_climbing(V0x,V0y,Tref,tolerance,m=0):
    #m: detection method
    #   0: usbminicounter
    #   1: analogIO
    #to track position of cavity when moving during the locking
    #process
    #Ttrack: tracking the transmission
    #result=0: lock Fail
    #result=1: Lock and Succeed
    #result=2: do not need to lock
    Vxtrack=[]
    Vytrack=[]
    Ttrack=[]


    Vx=V0x
    Vy=V0y
    Vxtrack.append(Vx)
    Vytrack.append(Vy)
    #get first count
    if m==0:
        t=getCount(miniusb,average=50)
    elif m==1:
        t=getPower(analogIO,average=200)
    Ttrack.append(t)
    tdiff=t-Tref
    i=0
    result=2

    if abs(tdiff)>(tolerance*Tref):
        print("Not at the target")
        print("Tcount: ",t)
        print("tdiff: ",tdiff)
        print("Start climbing")
    else:
        print("Already at the target")
        result=2
    print(tolerance*Tref)
    while abs(tdiff)>(tolerance*Tref):
            print((tdiff))

        #yes then lock kick in
            if i>10:
                print('Overexceed number of steps in transverse locking')
                result=3
                break

            if abs(tdiff)<3*(tolerance*Tref):
                step=0.01
            elif abs(tdiff)<2*(tolerance*Tref):
                step=0.005
            elif abs(tdiff)>4*(tolerance*Tref):
                step=0.03
            elif abs(tdiff)>5*(tolerance*Tref):
                step=0.05
            else:
                step=0.02
            (xmax,ymax,d)=scouting(Vx,Vy,Tref,step=step,m=m)
            #move to xmax ymax

            Vx=xmax+Vx
            Vy=ymax+Vy
            if (Vx>9) or (Vx<-9) or ( Vy>9) or (Vy<-9):
                print('\x1b[5;30;41m' + 'ERROR HIGH VOLTAGE ON PIEZO!' + '\x1b[0m')
                result=False
                break
            setV(Vx,Vy)
            #at new position, get new transmission
            if m==0:
                t=getCount(miniusb,average=50)
            elif m==1:
                t=getPower(analogIO,average=200)
            Ttrack.append(t)

            tdiff=t-Tref
            Vxtrack.append(Vx)
            Vytrack.append(Vy)
            i=i+1
            result=1

    print('Final count')
    print(Ttrack[-1])
    print('Final position')
    print(Vxtrack[-1],Vytrack[-1])
    print('Number of step',np.size(Vxtrack)-1)
    return(Vxtrack,Vytrack,Ttrack,result)

def get_Ext():
    pass
def scouting_EXT():
    pass
def hill_climbing_EXT(V0x,V0y,EXT_ref,tolerance=0.1):
    #to track position of cavity when moving during the locking
    #process
    #Ttrack: tracking the transmission
    Vxtrack=[]
    Vytrack=[]
    EXT_track=[]


    Vx=V0x
    Vy=V0y
    Vxtrack.append(Vx)
    Vytrack.append(Vy)
    #get first ext
    EXT=get_Ext()
    EXT_track.append(EXT)
    EXT_diff=ext-EXT_ref
    i=0
    result=2
    #result=0: lock Fail
    #result=1: Lock and Succeed
    #result=2: do not need to lock
    if abs(EXT_diff)>(tolerance*EXT_ref):
        print("Not at the target")
        print("EXT: ",EXT)
        print("Extdiff: ",EXT_diff)
        print("Start climbing")
    else:
        print("Already at the target")
        result=2
    result=1
    while abs(EXT_diff)>(tolerance*EXT_ref):
            print((EXT_diff))

        #yes then lock kick in
            if i>20:
                result=0
                break

            if abs(EXT_diff)>(EXT_ref/2):
                print('Too far away from the EXT ref. Dont dare to lock')
                break
            else:
                step=0.01
            (xmax,ymax,d)=scouting_EXT(Vx,Vy,EXT_ref,step=step)
            #move to xmax ymax

            Vx=xmax+Vx
            Vy=ymax+Vy
            if (Vx>8.8) or (Vx<-8.8) or ( Vy>8.8) or (Vy<-8.8):
                print('\x1b[5;30;41m' + 'ERROR HIGH VOLTAGE ON PIEZO!' + '\x1b[0m')
                result=False
                raise Errors.HighVoltage()

            setV(Vx,Vy)
            #at new position, get new transmission
            EXT=get_Ext()
            EXT_track.append(EXT)

            EXT_diff=EXT-EXT_ref
            Vxtrack.append(Vx)
            Vytrack.append(Vy)
            i=i+1


    print('Final count')
    print(Ttrack[-1])
    print('Final position')
    print(Vxtrack[-1],Vytrack[-1])
    print('Number of step',np.size(Vxtrack)-1)
    return(Vxtrack,Vytrack,Ttrack,result)
