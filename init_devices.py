from sys import path
path.append("/home/qitlab/programs/CQTdevices/")
from CQTdevices import *
import zmq
from printstyle import *
print('#'*40)
printstyle_stage2('Inititating devices...')
print('#'*40)
################################################
#initial miniusb counter device
############################################################################################3
miniusb_port='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_USB_Counter_Ucnt-QO10-if00'
miniusb=Countercomm(miniusb_port)
miniusb.set_gate_time(30)
#################################################

analogIO_port='/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Analog_Mini_IO_Unit_MIO-QO13-if00'
analogIO=AnalogComm(analogIO_port)
#################################################

#Initialize DDS
##############################################################################################
dds_probe_port='/dev/ioboards/dds_QO0037'
channel_probe=0
dds_probe=DDSComm(dds_probe_port,channel_probe)


#dds channel for REPUMP
dds_mot_port='/dev/ioboards/dds_QO0019'
channel_mot=0
dds_mot=DDSComm(dds_mot_port,channel_mot)

dds810_port='/dev/ioboards/dds_QO0062'
channel_810=0
dds_810=DDSComm(dds810_port,channel_810)

init_power=600

amplmot=500
amplprobe=70

w810eom=95
#130 or 120 is for 810 to be resonant with 780D2
##############################################################################################

#Setup communication with Cavity_retreat
##############################################################################################
context = zmq.Context()
#  Socket to talk to server
print ("Connecting to the retreat controller server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556")

socket.send("CheckVolt 5")
V0y=float((socket.recv()).split()[-1])
socket.send("CheckVolt 6")
V0x=float((socket.recv()).split()[-1])
##############################################################################################

#Windfreak Communication for Probe freq
w_probe_port='/dev/ttyACM6'
w_probe=WindFreakUsb2(w_probe_port)
w_probe.serial.write('g0')
w_probe.set_freq(390)
w_probe.set_power(2)

#Windfreak Communication for Probe freq
w_810_port='/dev/ttyACM7'
w_810=WindFreakUsb2(w_810_port,initfreq=w810eom)
w_810.slow_set_freq(w810eom,5)
##############################################################################################
#Setup communication with Dinosaur_seeker
##############################################################################################
context = zmq.Context()
#  Socket to talk to server
print ("Connecting to the Dinosaur_seeker server")
socket2 = context.socket(zmq.REQ)
socket2.connect("tcp://localhost:5558")
