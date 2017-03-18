#!/usr/bin/python
#transverse lock
from CQTdevices import *
import time
import zmq
from sys import exit
import subprocess as sp
import timeit
#from Errors import *
import logging
from init_devices import *
import numpy as np
#from hill_climbing import *
from hill_climbing import *
import datetime
import os
from printstyle import *
#locking results
global num_lock# number of lock
global atlockfreq
global T780lbf
global T780laft
global T810lbf
global T810laft
global mltl#multi lock?
global ls780#lock steps 780
global ls810#lock steps 810
global Vxbfl
global Vybfl
global Vxafl
global Vyafl
global w810sb#freq of rf 810 sideband
global tsl#timestartlock
global lockdu#duration of lock
num_lock=0
atlockfreq=[]
T780lbf=[]
T780laft=[]
T810lbf=[]
T810laft=[]
mltl=[]
ls780=[]
ls810=[]
lockdu=[]
tsl=[]
lockdu=[]
Vxbfl=[]
Vybfl=[]
Vxafl=[]
Vyafl=[]
w810sb=[]
def lock(Tref,tolerance,Tref_810,tolerance_810,V0x,V0y,mypath,f780=0,w810sb_e=0):
    global num_lock# number of lock
    global atlockfreq
    global T780lbf
    global T780laft
    global T810lbf
    global T810laft
    global mltl#multi lock?
    global ls780#lock steps 780
    global ls810#lock steps 810
    global Vxbfl
    global Vybfl
    global Vxafl
    global w810sb
    global tsl#timestartlock
    global lockdu#duration of lock
    print('Start transverse locking')
    print('Checking T780 and T810')
    t=miniusb.get_countstat(average=100)
    t810=getPower(analogIO,average=200)
    tdiff=t-Tref
    tdiff_810=t810-Tref_810
    print(t810)
    print(t)
    print(tdiff_810)
    print('Difference in 780 Counts: %d' %tdiff )
    print('Difference in 780 Counts: %1.4f' %tdiff_810 )
    result=0
    result2=0
    result3=0
    lock_log_filename=mypath+'/'+'lock.log'
    f=open(lock_log_filename,'ab')
    f.write('Target T780: %1.3f \t Tolerance %1.2f ~ %1.3f' %(Tref,tolerance,tolerance*Tref))
    f.write('\n')
    f.write('Target T810: %1.3f \t Tolerance %1.2f ~ %1.3f' %(Tref_810,tolerance_810,tolerance_810*Tref_810))
    f.write('\n')
    s=time.strftime("%H:%M:%S", time.localtime())
    ts1=time.time()
    f.write('Time start: %s' %s)
    f.write('\n')
    f.write('Initial Transmission: T780 %1.3f T810 %1.3f ' %(t,t810))
    f.write('\n')
    f.write('\n')
    if ( (abs(t-Tref)<tolerance*Tref) and (abs(t810-Tref_810)<tolerance_810*Tref_810)):
        print('TRANSMISSION TEST PASSES')
        print('DO NOT NEED TO LOCK')
        f.write('Do not need to lock \n')
        f.write('Locking result: 1 \n')
        result=2
    else:
        num_lock=num_lock+1

    T780lbf.append(t)
    T810lbf.append(t810)
    Vxbfl.append(V0x)
    Vybfl.append(V0y)
    tsl.append(s)
    atlockfreq.append(f780)
    w810sb.append(w810sb_e)
    lss780=0
    lss810=0
    while( (abs(t-Tref)>tolerance*Tref) or (abs(t810-Tref_810)>tolerance_810*Tref_810)):
        lss780=0
        lss810=0

        print('TRANSMISSION TEST FAIL')
        print('TRANVERSE LOCKING STARTING')


        print('Locking on 780 T')
        (Vxtrack,Vytrack,Ttrack,result)=hill_climbing(V0x,V0y,Tref,tolerance)
        lss780=lss780+np.size(Vxtrack)-1
        V0x=Vxtrack[-1]
        V0y=Vytrack[-1]
        if result==3:
            printstyle_warning('Exceed maximum allowed number of steps in transvers lock 780')
            f.write('T780 Lock \n')
            log_track=np.column_stack((Vxtrack,Vytrack,Ttrack))
            np.savetxt(f,log_track,fmt='%1.3f')
            f.write('Lock result: '+ str(result))
            f.write('\n')
            break

        print('Locking on 810 T')
        (Vxtrack2,Vytrack2,Ttrack2,result2)=hill_climbing(V0x,V0y,Tref_810,tolerance_810,m=1)
        lss810=lss810+np.size(Vxtrack)-1
        V0x=Vxtrack2[-1]
        V0y=Vytrack2[-1]
        t=miniusb.get_countstat()
        t810=getPower(analogIO,average=150)

        print('T780 after lock ', t)
        print('T810 after lock ', t810)
        print('T780 difference %f' %(t-Tref))
        print('T810 difference %f' %(t810-Tref_810))

        log_track=np.column_stack((Vxtrack,Vytrack,Ttrack))
        log_track2=np.column_stack((Vxtrack2,Vytrack2,Ttrack2))
        f.write('T780 Lock \n')
        np.savetxt(f,log_track,fmt='%1.3f')
        f.write('Lock result: '+ str(result))
        f.write('\n')
        f.write('T810 Lock')
        f.write('\n')
        np.savetxt(f,log_track2,fmt='%1.3f')
        f.write('Lock result: '+ str(result2))
        f.write('\n')
        f.write('\n')

    T780laft.append(t)
    T810laft.append(t810)

    Vxafl.append(V0x)
    Vyafl.append(V0y)
    ls780.append(lss780)
    ls810.append(lss810)

    s2=time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    ts2=time.time()
    durationlock=int(ts2-ts1)
    lockdu.append(durationlock)
    f.write('Finished at %s' %s2)
    f.write('\n')
    f.write('Locking duration %d seconds' %durationlock)
    f.write('\n')
    f.write('T780 and T810 after locking %1.3f %1.3f \n' %(t,t810))
    f.write('\n')
    f.write('\n')
    f.write("#"*20)
    f.write('\n')

    f.close()

    #result3=result*result2#temp


    return result
