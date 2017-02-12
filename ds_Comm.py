#communicate to dinosaur seeker
import zmq
import numpy as np
import time
#Setup communication with Dinosaur_seeker
##############################################################################################
context = zmq.Context()
#  Socket to talk to server
#print ("Connecting to the Dinosaur_seeker server")
#socket2 = context.socket(zmq.REQ)
#socket2.connect("tcp://localhost:5558")

class dsComm():
    def __init__(self):
        print('Connecting to Dionosaur Seeker Server')
        self.socket=context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5558")

    def restart(self):
        while True:
            self.socket.send("Restart Please")
            self.message = self.socket.recv()

            if self.message != "Unable Boss":
                self.result=self.message
                break
            else:
                time.sleep(0.1)

    def reset(self):
        while True:

            self.socket.send("Reset Please")
            self.message = self.socket.recv()

            if self.message != "Unable Boss":
                self.result=self.message
                break
            else:
                time.sleep(0.1)
        return self.result

    def resave(self,savepath):
        print("Resav "+savepath)
        while True:
            self.socket.send("Resav "+savepath)
            self.message = self.socket.recv()
            if self.message != "Unable Boss":
                self.result=self.message
                break
            else:
                time.sleep(0.1)
        print(self.result)
        return self.result

    def get_trig(self):
        time.sleep(0.5)

        self.socket.send("Check Trig")
        self.message = self.socket.recv()
        if self.message=='Not Started':
            print(message)

        self.m=self.message.split()
        trig_num=int(self.m[1])
        time.sleep(0.1)
        return trig_num

    def get_exp_result_duration(self,duration=10):
        self.restart()
        print('Data Collection in Progress')
        time.sleep(duration)
        self.message=self.reset()
        #need to convert message to number
        #example return message Okay Trig 13 Ext -746.40 198.47
        print(self.message)
        self.m=self.message.split()
        trig_num=int(self.m[2])
        Ext=float(self.m[4])
        std_Ext=float(self.m[5])
        t=float(self.m[7])
        std_t=float(self.m[8])
        decaytime=float(self.m[10])
        std_decaytime=float(self.m[11])
        print('Data Collection is finished')
        return (trig_num,Ext,std_Ext,t,std_t,decaytime,std_decaytime)

    def get_exp_result_trignum(self,trignum=50,savepath='/home/temp/',sp=0):
        '''
        record until reaching a desired number of triggering (trignum)
        '''
        self.restart()
        print('Data Collection in Progress')
        time.sleep(1)
        trig_count=0
        i=0 # keep track of a number of repeated trigcount
        print(trignum)
        while (self.get_trig())<trignum:

            time.sleep(3)
            tr=self.get_trig()

            if trig_count==tr:
                i=i+1
            else:
                i=0
            trig_count=tr
            if i>5:
                print('Call Human for help')
        print('Data Collection is Finished')
        if sp==0:
            self.message=self.reset()
        elif sp==1:
            self.message=self.resave(savepath=savepath)
        #need to convert message to number
        #example return message Okay Trig 13 Ext -746.40 198.47
        print(self.message)
        self.m=self.message.split()
        trig_num=int(self.m[2])
        Ext=float(self.m[4])
        std_Ext=float(self.m[5])
        t=float(self.m[7])
        std_t=float(self.m[8])
        decaytime=float(self.m[10])
        std_decaytime=float(self.m[11])

        return (trig_num,Ext,std_Ext,t,std_t,decaytime,std_decaytime)
if __name__=='__main__':
    ds1=dsComm()
    re=ds1.get_exp_result_duration()
    print(re)
