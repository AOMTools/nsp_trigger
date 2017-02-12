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
def lock(Tref,tolerance,Tref_810,tolerance_810,V0x,V0y,mypath):
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
    s=time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
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

    while( (abs(t-Tref)>tolerance*Tref) or (abs(t810-Tref_810)>tolerance_810*Tref_810)):
        print('TRANSMISSION TEST FAIL')
        print('TRANVERSE LOCKING STARTING')
        print('Locking on 780 T')
        (Vxtrack,Vytrack,Ttrack,result)=hill_climbing(V0x,V0y,Tref,tolerance)
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


    f.write('T780 and T810 after locking %1.3f %1.3f \n' %(t,t810))
    f.write('\n')
    f.write('\n')
    f.write("#"*20)
    f.write('\n')

    f.close()

    #result3=result*result2#temp


    return result
