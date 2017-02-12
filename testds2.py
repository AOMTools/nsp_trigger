import numpy as np
import time
from init_devices import *
import transverse_lock as tl
import Errors
import subprocess
import time
import sys
from ds_Comm import dsComm
analogIO_port='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Analog_Mini_IO_Unit_MIO-QO13-if00'
analogIO=AnalogComm(analogIO_port)

def getPower(analogIO,channel=0,average=100):
    #Get the P810 transmission power on photodetector
    power=np.zeros(average)
    channel=0
    for i in range(average):
        power[i]=analogIO.get_voltage(channel)
    return (np.mean(power),np.std(power))
ds1=dsComm()
result=[]
t=[]
trig=[]
ext=[]
std_ext=[]
p810=[]
std_p810=[]
for i in range (10):
    p=getPower(analogIO,average=150)
    p810.append(p[0])
    std_p810.append(p[1])
    re=ds1.get_exp_result_trignum(trignum=30)
    print(re)
    result.append(re)
    t.append(int(time.time()))
    trig.append(re[0])
    ext.append(re[1])
    std_ext.append(re[2])
print(result)
resave=np.column_stack((t,trig,ext,std_ext,p810,std_p810))
np.savetxt('testlogext.log',resave)
