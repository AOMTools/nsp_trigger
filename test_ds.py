import time
import subprocess
from sys import path
path.append("/home/qitlab/programs/CQTdevices/")
from Counter import Countercomm
from CQTdevices import *
'''
def quadcoil_switchmode(smode=0):
    #switching mode to switch on/off quadcoil with triggering
    #smode=0: continuous
    #smode=1: onoff for pattern_generator triggering process
    if smode==0:
        print('QuadCoil is set to Continous mode')
        bashCommand="./getresponse -d /dev/ttyACM2 -t 1000 -c out,0,2"

    elif smode==1:
        print('Quadcoil is set to Triggering mode')
        bashCommand="./getresponse -d /dev/ttyACM2 -t 1000 -c out,0,0"
        #bashCommand="cat ../apps2/Q37_onoff.script | ./dds_encode -d /dev/ioboards/dds_QO0037"

    process=subprocess.Popen(bashCommand,cwd='/home/qitlab/programs/getresponse',stdout=subprocess.PIPE,shell=True)
    (output,error)=process.communicate()
    print(output)
'''
port='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Analog_Mini_IO_Unit_MIO-QO13-if00'
a=AnalogComm(port)
a.set_voltage(0,2)
#time.sleep(5)
#a.set_voltage(0,2)
