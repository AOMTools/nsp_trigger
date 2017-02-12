'''
Simple script  to cavity spectrum wo atoms

'''
from sys import path
path.append("/home/qitlab/programs/CQTdevices/")
from CQTdevices import *
from Counter import Countercomm
import time
import numpy as np


miniusb_port='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_USB_Counter_Ucnt-QO10-if00'
miniusb=Countercomm(miniusb_port)
miniusb.set_gate_time(30)

#windfreak devices control probe freq
w1_port='/dev/ttyACM6'
w1=WindFreakUsb2(w1_port)
w1.serial.write('g0')
w1.set_freq(300)
#Analogminiusb for control of amplifer of eospace
#a_port=''
#a=AnalogComm(a_port)
#freq scanning range
fdefault=400

f_range=400+np.linspace(-100,100,21)
trans=[]
std_trans=[]

def set_freq_probe(w):
    w1.slow_set_freq(w,5)
    print('Set probe freq at', w)
    time.sleep(1)
def start():

    for i in f_range:
        set_freq_probe(i)
        tc=miniusb.get_countstat(average=50,c=1)
        print(tc)
        trans.append(tc[0])
        std_trans.append(tc[1])
if __name__=='__main__':
    start()
    print(trans)
    tp=np.column_stack((f_range,trans,std_trans))
    np.savetxt('empcav.dat',tp)
