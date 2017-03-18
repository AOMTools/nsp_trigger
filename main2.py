from __future__ import print_function
import numpy as np
import time
from init_devices import *
import transverse_lock as tl
import Errors
import subprocess
import time
import datetime
import sys,traceback
import os
from ds_Comm import dsComm #dinosaur seeker
from printstyle import *
from fitter import *
from misc import *

################################################
#PAREMETER DEFNITIION
w_ref=384 #ref probe freq for checking transmisison
#360 is for 780probe resonant with D2
w_ref_ext=384 # ref to check ext

w_ref_res=384# freq of probe that chosen for the cavity to be resoant with
            #used for checking spectrum scan
probe_freq_range=w_ref+np.asarray(freq_range_gen())
#probe_freq_range=w_ref+np.linspace(-10,10,11)
probe_freq_range=np.asarray([504,504,504,504,504,504,504,504])
print(probe_freq_range)
#print(probe_freq_range)

#Tref=1050
Tref=900
tolerance=0.06

#for 600amp 2mW Pin810
#Tref_810=0.024
# 2.6mW 810: Tref_810=0.0325

Tref_810=0.058
tolerance_810=0.04

tn=10 #Number of triggered atoms taken for one freq point
#################################################
#INITIATE Dinosaur_seeker connection
#################################################
ds1=dsComm()
#################################################
status_preparation=0
#################################################
#Saving
#
#################################################

def master_saving_folder_gen():
    date_folder="{:%Y_%m_%d_%H_%M}".format(datetime.datetime.now())
    mypath = '/home/qitlab/programs/nsp_trigger/exp_data/'+date_folder
    if not os.path.isdir(mypath):
        os.makedirs(mypath)
    return mypath

name_exp="default"
date_exp="{:%Y_%m_%d_%H%M}".format(datetime.datetime.now())
name_exp=date_exp
savefilename=name_exp+'.dat'

#master_path=master_saving_folder_gen()

#################################################
trig_num=[]
Ext=[]
std_Ext=[]
freq=[]
t_exp=[]#time conduct exp

Tnoatom=[]
std_Tnoatom=[]

Rnoatom=[]
std_Rnoatom=[]
T810=[]
Vx_exp=[]#Vx values just before main exp
Vy_exp=[]
f_r=[]#freq of probe resonant with cavity
time_take=[] #time take to finish one iteration of main_exp non including the locking time
#10 field
header_data='t_exp  freq    trig_num    Ext     std_Ext Tnoatom\
std_Tnoatom Vx_exp  Vy_exp  time_take'
data_to_save=(t_exp,freq,trig_num,Ext,std_Ext,Tnoatom,std_Tnoatom,Vx_exp,Vy_exp,time_take)
#################################################
#Report information
tlock=[]





def report():
    global tstart
    global tend
    global tstart_f
    global tend_f
    global tlock
    global master_path
    timeexp=tend_f-tstart_f
    hour_exp=int(timeexp/3600)
    minute_exp=int((timeexp%3600)/60)
    sec_exp=int((timeexp%3600)%60)
    filename=master_path+'/'+'report'
    with open(filename,'w') as fout:
        fout.write('Experimental Parameters \n')
        fout.write('\t Probe Reference Freq \n')
        fout.write('\t \t for checking T: %d' %w_ref)
        fout.write('\t \t for checking EXT: %d' %w_ref_ext)
        fout.write('\t \t for checking cavity length: %d \n' %w_ref_res)
        fout.write('\t Locking Targets \n')
        fout.write('\t \t for checking T780: \t Target: %d \t tolerance: %1.3f~%d \n' %(Tref,tolerance,tolerance*Tref))
        fout.write('\t \t for checking T810: \t Target: %d \t tolerance: %1.3f~%d ' %(Tref_810,tolerance_810,tolerance_810*Tref_810))
        fout.write('\nTemporal Information \n')
        fout.write('\tTime start: %s' %tstart)
        fout.write('\n\tTime end: %s' %tend)
        fout.write('\n\tDuration: %d seconds ~ %d hours  %d minutes  %d seconds' %(timeexp,hour_exp,minute_exp,sec_exp))
        fout.write('\nLocking Info \n')
###################################################
def set_probe_freq(w):
    '''
    set probe freq to w
    '''
    print('Set probe freq to ',w)
    w_probe.slow_set_freq(w,step=5)

def get_initV():
    socket.send("CheckVolt 5")
    V0y=float((socket.recv()).split()[-1])
    socket.send("CheckVolt 6")
    V0x=float((socket.recv()).split()[-1])
    return(V0x,V0y)

def get_Ext(tn,savepath='/home/temp/',sp=0):
    '''
    Retrieve EXT with probe freq at w via dinosaur_seeker
    Input : (tn,savepath,sp)
        tn: number of triggering per Call
        savepath: saving location
        sp: 0: no trace saving via reset in dsComm
            1: trace saving via resave in dsComm
    Output: (ext,num_trig)
        ext: ext level
        num_trig: number of triggered atoms
    '''
    result=ds1.get_exp_result_trignum(trignum=tn,savepath=savepath,sp=sp)
    return result

def getPower(analogIO,channel=0,average=100):
    #Get the P810 transmission power on photodetector
    power=np.zeros(average)
    channel=0
    for i in range(average):
        power[i]=analogIO.get_voltage(channel)
    return (np.mean(power))

def setV(Vx,Vy):
    '''
    set an absolute voltage to piezo by delegating to cavity_retreat controller
    '''
    #socket.send("SetVolt5 0")
    #message = socket.recv()
    command1="SetVolt5 "+str(Vy)
    command2="SetVolt6 "+str(Vx)
    socket.send(command1)
    message=socket.recv()
    socket.send(command2)
    message=socket.recv()


def probe_dds_switchmode(smode=0):
    #switching mode of probe dds via bash command to cat a file to dds_encode
    #smode=0: continuous
    #smode=1: onoff for pattern_generator triggering process
    if smode==0:
        print('DDS Probe is set to Continuous mode')
        bashCommand="cat ../apps2/Q37_2.script | ./dds_encode -d /dev/ioboards/dds_QO0037"

    elif smode==1:
        print('DDS Probe is set to Triggering mode')
        bashCommand="cat ../apps2/Q37_onoff.script | ./dds_encode -d /dev/ioboards/dds_QO0037"

    process=subprocess.Popen(bashCommand,cwd='/home/qitlab/programs/usbdds/apps',stdout=subprocess.PIPE,shell=True)
    (output,error)=process.communicate()

def sideprobe_dds_switchmode(smode=0):
    #switching mode of probe dds via bash command to cat a file to dds_encode
    #smode=0: continuous
    #smode=1: onoff for pattern_generator triggering process
    if smode==0:
        print('DDS Probe is set to Continuous mode')
        bashCommand="cat ../apps2/Q37_2.script | ./dds_encode -d /dev/ioboards/dds_QO0037"

    elif smode==1:
        print('DDS Probe is set to Triggering mode')
        bashCommand="cat ../apps2/Q37_sp_onoff.script | ./dds_encode -d /dev/ioboards/dds_QO0037"

    process=subprocess.Popen(bashCommand,cwd='/home/qitlab/programs/usbdds/apps',stdout=subprocess.PIPE,shell=True)
    (output,error)=process.communicate()

def pattern_switchmode(smode=0):
    if smode==0:
        print('Pattern is set to  NON-Triggering mode')
        bashCommand="./arbitrarypatterngeneratorL700  -o /dev/ioboards/pattgen_serial_04 -d delayfile -i cav_pattern/t03_checkatom"
    elif smode==1:
        print('Pattern is set to Triggering mode')
        bashCommand="./arbitrarypatterngeneratorL700  -o /dev/ioboards/pattgen_serial_04 -d delayfile -i cav_pattern/t05_ext_50ms"
    process=subprocess.Popen(bashCommand,cwd='/home/qitlab/programs/patt_gen',stdout=subprocess.PIPE,shell=True)
    (output,error)=process.communicate()

    time.sleep(5)

def quadcoil_switchmode(smode=0):
    #switching mode to switch on/off quadcoil with triggering
    #smode=0: continuous
    #smode=1: onoff for pattern_generator triggering process
    if smode==0:
        print('QuadCoil is set to Continuous mode')
        analogIO.set_voltage(0,2)

    elif smode==1:
        print('Quadcoil is set to Triggering mode')
        analogIO.set_voltage(0,0)
        #bashCommand="cat ../apps2/Q37_onoff.script | ./dds_encode -d /dev/ioboards/dds_QO0037"
    time.sleep(0.5)


def mot_dds_switchmode(smode=0):
    #switching mode of probe dds via bash command to cat a file to dds_encode
    #smode=0: continuous
    #smode=1: onoff for pattern_generator triggering process
    if smode==0:
        print('DDS MOT is set to Continous mode')
        bashCommand="cat ../apps2/Q19_2.script | ./dds_encode -d /dev/ioboards/dds_QO0019"

    elif smode==1:
        print('DDS MOT is set to Triggering mode')
        bashCommand="cat ../apps2/Q19_onoff.script | ./dds_encode -d /dev/ioboards/dds_QO0019"

    process=subprocess.Popen(bashCommand,cwd='/home/qitlab/programs/usbdds/apps',stdout=subprocess.PIPE,shell=True)
    (output,error)=process.communicate()

def check_transmission():
    print('Preparing Transmission Check')
    preparation_check()
    print('Checking Tranmission')
    result=0
    time.sleep(1)
    t=miniusb.get_countstat(average=100)
    tdiff=t-Tref

    t810=getPower(analogIO,average=150)
    tdiff_810=t810-Tref_810
    print(t)
    print(t810)
    print('Difference in 780 Counts: %d' %tdiff )
    print('Difference in 780 Counts: %1.4f' %tdiff_810 )
    if abs(t-Tref)>tolerance*Tref:
        print('Transmission Test 780 FAIL')


        result=0
    elif abs(t810-Tref_810)>tolerance_810*Tref_810:
        print('Tranmission Test 810 FAIL')
        result=0
    else:
        print('Tranmission Test PASSES')
        result=2
    return result

def check_Ext():
    Ext_ref=10
    print('\x1b[0;33;40m'+'Preparing Ext Check'+'\x1b[0m')
    preparation_Ext(w_ref_ext)
    print('\x1b[0;33;40m'+'Checking Ext'+'\x1b[0m')
    ext=get_Ext(20)[1]
    print('Extinction level is ',ext)
    result=0
    if ext<Ext_ref:
        print('Fail Extinction Check')
    else:
        result=1
        print('Pass Extinction Check')

    return result


def lock_trans(f=0,w810=0):
    print('Preparing Transmission Check')
    preparation_check()
    global master_path
    '''
    result=check_transmission() #check if cavity thermal drift causes changes in transmission
    if result==0: #Fail checking and now proceed to locking
        (V0x,V0y)=get_initV()
        result=tl.lock(Tref,tolerance,Tref_810,tolerance_810,V0x,V0y,mypath=master_path)
    '''
    (V0x,V0y)=get_initV()
    result=tl.lock(Tref,tolerance,Tref_810,tolerance_810,V0x,V0y,mypath=master_path,f780=f,w810sb_e=w810)
    return result

def lock_Ext():

    result=check_Ext() #check if Ext is still the same
    if result==0:#fail checking and now proceed to locking
        printstyle_stage2('Fail Extinction Check')
        #result=lock_Ext() # has not implemented ext lock yet

    return result

def preparation_check():

    quadcoil_switchmode()
    probe_dds_switchmode()
    set_probe_freq(w_ref)
    mot_dds_switchmode()
    dds_mot.off()
    time.sleep(5)

def preparation_Ext(w):
    #should switch back to smode=1 for main exp later
    quadcoil_switchmode(smode=1)
    probe_dds_switchmode(smode=1)
    set_probe_freq(w)
    mot_dds_switchmode(smode=1)
    time.sleep(2)

def preparation_sp(w):
    #should switch back to smode=1 for main exp later
    #prepartion for sideprobe
    quadcoil_switchmode(smode=1)
    sideprobe_dds_switchmode(smode=1)
    set_probe_freq(w)
    mot_dds_switchmode(smode=1)
    time.sleep(2)

def check(c=0,w=0,w810=0):
    '''
    Perform hygiene check on experiment
    c=0: check both EXT and Transmission
    c=1: check only Transmission
    c=2: check only EXT

    Return result
    for c=1: result_lock_Ext===1(always)
        result  =1: Lock T and Succeed
                =2: Do not need to lock T
                =3: Exceed maximum number of steps
    '''
    print('#'*40)
    print('\t'+'\x1b[0;30;43m'+'Checking Stage'+'\x1b[0m')
    print('Target T780: %1.3f \t Tolerance %1.2f ~ %1.3f' %(Tref,tolerance,tolerance*Tref))
    print('Target T810: %1.3f \t Tolerance %1.2f ~ %1.3f' %(Tref_810,tolerance_810,tolerance_810*Tref_810))
    print('#'*40)
    print

    if c==0:
        result_lock_trans=lock_trans(f=w,w810=w810)
        result_lock_Ext=lock_Ext()
    elif c==1:
        result_lock_trans=lock_trans(f=w,w810=w810)
        result_lock_Ext=1
    elif c==2:
        result_lock_trans=1
        result_lock_Ext=lock_Ext()

    result=result_lock_trans*result_lock_Ext
    if (result_lock_trans*result_lock_Ext)==0:
        printstyle_warning('Fail locking')
        raise Errors.ExperimentalError()
    else:
        print('Succeed checking and locking')

    return result

def main_exp(w):
    global master_path
    #setprobe freq here
    print('#'*40)
    printstyle_stage1('Main Experiment in Progress')
    print('#'*40)
    preparation_Ext(w)


    t_exp.append(int(time.time()))
    t1=int(time.time())

    savefolder=trace_saving_folder_gen(w,master_path)

    result=get_Ext(tn,savepath=savefolder,sp=1)

    t2=int(time.time())

    time_take.append(t2-t1)

    trig_num.append(result[0])
    Ext.append(result[1])
    std_Ext.append(result[2])

    (Vx,Vy)=get_initV()
    Vx_exp.append(Vx)
    Vy_exp.append(Vy)
    time.sleep(0.5)
    #print("Experiment Results: ",result)
    print("Number of Triggering cases:")
    print(trig_num)
    print("Extinction result: ")
    print(Ext)
    print("Extinction std: ")
    print(std_Ext)

def emptycav(f):
    print('#'*40)
    printstyle_stage2('Empty Cav Spec Stage')
    print('#'*40)
    quadcoil_switchmode()
    probe_dds_switchmode()
    mot_dds_switchmode()
    dds_mot.off()
    dds_mot2.off()
    time.sleep(2)
    freq.append(f)
    tcount,stdt=miniusb.get_countstat(average=100,c=1,d=0)
    Rcount,stdR=miniusb.get_countstat(average=100,c=1,channel=2,d=0)
    print('Tranmission detected: %d' %tcount)
    print('Reflection detected: %d' %Rcount)
    Tnoatom.append(tcount)
    std_Tnoatom.append(stdt)
    Rnoatom.append(Rcount)
    std_Rnoatom.append(stdR)

def party_cleanup():
    print('#'*40)
    print('\t'+'\x1b[0;30;43m'+'Post-Party Cleaning'+'\x1b[0m')
    print('#'*40)
    probe_dds_switchmode()
    mot_dds_switchmode()
    w_probe.slow_set_freq(w_ref,5)
    print('Ending Experiment')
    #return_initial()

def return_initial():

    print('Revert Cavity Piezo to initial conditions')
    print(Vx_checkpoint,Vy_checkpoint)
    setV(Vx_checkpoint,Vy_checkpoint)
    print('Revert DDS to initial conditions')
    probe_dds_switchmode(smode=1)
    mot_dds_switchmode(smode=1)
    quadcoil_switchmode()
    w_probe.slow_set_freq(w_ref,5)
    w_810.slow_set_freq(w810eom,5)

def saving():
    #date_folder="{:%Y_%m_%d}".format(datetime.datetime.now())

    printstyle_stage1('Gathering and Saving useful data')
    #locksave=np.column_stack((atlockfreq,T780lbf,T780laft,T810lbf,T810laft,Vxbfl,Vxafl,Vybfl,Vyafl,ls780,ls810,tsl,lockdu))
    lock_stat_filename=master_path+'/'+'lockstat.dat'
    resave=np.column_stack((freq,Tnoatom,std_Tnoatom,Rnoatom,std_Rnoatom))
    try:
        resave=np.column_stack((freq,Tnoatom,std_Tnoatom,Rnoatom,std_Rnoatom))
    except ValueError as e:

        s_data=[]
        for i in resave:
            s_data.append(np.size(i))
        min_size=np.min(s_data)
        for i in resave:
            while np.size(i)>min_size:
                i.pop()
    finally:
        np.savetxt(master_path+'/'+'emptycavspec.dat',resave,fmt='%1.3f %1.3f %1.3f %1.3f %1.3f')
        with open(lock_stat_filename,'w') as f:
            #f.write("atlockfreq,T780lbf,T780laft,T810lbf,T810laft,Vxbfl,Vxafl,Vybfl,Vyafl,ls780,ls810,tsl,lockdu")

            f.write('{:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^15} {:^10}\n'.format('freq','T780lbf','T780laft','T810lbf','T810laft','Vxbfl','Vxafl','Vybfl','Vyafl','ls780','ls810','w810sb','tsl','lockdu'))
            for i in range(len(tl.T780lbf)):
                f.write('{:^10} {:^10.2f} {:^10.2f} {:^10.2f} {:^10.2f} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10} {:^15s} {:^10}\n'.format(tl.atlockfreq[i],tl.T780lbf[i],tl.T780laft[i],tl.T810lbf[i],tl.T810laft[i],tl.Vxbfl[i],tl.Vxafl[i],tl.Vybfl[i],tl.Vyafl[i],tl.ls780[i],tl.ls810[i],tl.w810sb[i],tl.tsl[i],tl.lockdu[i]))


def trace_saving_folder_gen(f,master_path):

    mypath = master_path+'/'+str(int(f))+'/'
    if not os.path.isdir(mypath):
        os.makedirs(mypath)
    return mypath

def saving_useful_data():
    '''
    Saving what has been recorded before Error raised
    '''
    printstyle_stage1('Gathering and Saving useful data')
    data_to_save=((freq,Tnoatom,std_Tnoatom))
    try:
        c=np.column_stack(data_to_save)
    except ValueError as e:

        s_data=[]
        for i in data_to_save:
            s_data.append(np.size(i))
        min_size=np.min(s_data)
        for i in data_to_save:
            while np.size(i)>min_size:
                i.pop()
    finally:
        saving()

def spectrum_scan(savemode=0):
    global master_path
    preparation_check()

    f_check_range=w_ref_res+np.linspace(-24,24,7)
    tcount=[]
    stdcount=[]
    freqs=[]
    for f in f_check_range:
        set_probe_freq(f)
        time.sleep(1)
        (t,s)=miniusb.get_countstat(average=50,c=1)
        freqs.append(f)
        tcount.append(t)
        stdcount.append(s)
        print(t)

    timesave="{:%H_%M}".format(datetime.datetime.now())
    mypath=master_path+'/'+'emptycav'
    if not os.path.isdir(mypath):
        os.makedirs(mypath)
    fname=mypath+'/'+timesave+'.dat'
    datsave=np.column_stack((freqs,tcount,stdcount))
    print(datsave)
    if savemode==1:
        np.savetxt(fname,datsave)

    datafit=np.column_stack((freqs,tcount,stdcount))
    return datafit

def checkspectrum():
    '''
    Checking if cavity is resonant with a chosen probe freq
    by scanning the probe freq and locate the freq of probe that has
    the maximum transmission

    '''
    print('#'*40)
    printstyle_stage2('Check Cavity Spectrum')
    print('#'*40)

    print('Scanning now...')
    datafit=spectrum_scan()
    init_fitpara=np.array([500, 100, 400])


    result_fit=lorentz_fitting(datafit,init_fitpara)
    fmax=result_fit[4]
    fit_width=result_fit[2]
    fit_maxt=result_fit[0]
    fit_chi=result_fit[-1]
    delf=w_ref_res-fmax
    print('Maximum Transmission: %d' %fit_maxt)
    print('Linewidth: %d' %fit_width)
    print('Chi Square: %1.3f' %fit_chi)
    print('Offset found %d' %delf)
    checkfmax=0 if abs(delf)>3 else 1
    result=0
    if checkfmax==0:
        if abs(delf)>30:
            printstyle_warning('Cavity Length is offset too far')
            raise Errors.FailLocking()
        print('Adjusting Cavity length...')
        currentf=int(w_810.get_freq())/1000
        print(currentf)
        print('To Cavity length: %d' %(currentf-delf))
        #currentf - delf if locked to the -1 sd. eom freq increase->decrease in 810 freq
        w_810.slow_set_freq(currentf-delf,5)
    else:
        print('Cavity Length is as expected')
        result=2
    return result
(Vx_checkpoint,Vy_checkpoint)=get_initV()
def start():
    global master_path
    master_path=master_saving_folder_gen()
    global Vx_checkpoint
    global Vy_checkpoint
    global tstart
    global tend
    global tstart_f
    global tend_f
    global tlock
    global freq
    global Tnoatom
    global std_Tnoatom
    freq=[]
    Tnoatom=[]
    std_Tnoatom=[]
    print('#'*40)
    printstyle_stage1('Starting Experiment')
    quadcoil_switchmode()
    tstart=time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    tstart_f=time.time()
    print(tstart)
    print('#'*40)
    num_pass=0

    for i,f in enumerate(probe_freq_range):
        if i%5==0:
            result_checkspectrum=0
            re=0
            tl1=time.time()
            while re*result_checkspectrum!=4:
                result_checkspectrum=checkspectrum()
                #result_checkspectrum=2
                w810=int(w_810.get_freq())
                re=check(c=1,w=f,w810=w810)



            #check(c=2,w=f)#ext check
            tl2=time.time()
            tlock.append(tl1-tl2)
    # if the flow of the program reach this point, it means that exp passes the
    # checks.

        (Vx_checkpoint,Vy_checkpoint)=get_initV()
        '''
        if i%5==1:
            #chosen such that the sepctrum scan conducted after 1 turn of no locking
            spectrum_scan(savemode=1)
        '''
        main_exp(f)
        emptycav(f)
    saving()
    tend=time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    tend_f=time.time()
if __name__=='__main__':
    try:
        for i in range(1):
            start()

    except Errors.ExperimentalError:
        printstyle_warning('Experimental Error')
        #saving_useful_data()
        saving()
        return_initial()
    except KeyboardInterrupt:
        #saving_useful_data()
        return_initial()
    except Exception as e:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        print ("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print ("*** print_exception:")
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
        print ("*** print_exc:")
        traceback.print_exc()
        print ("*** format_exc, first and last line:")
        formatted_lines = traceback.format_exc().splitlines()
        print (formatted_lines[0])
        print (formatted_lines[-1])
        print ("*** format_exception:")
        print (repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback)))
        print ("*** extract_tb:")
        print (repr(traceback.extract_tb(exc_traceback)))
        print ("*** format_tb:")
        print (repr(traceback.format_tb(exc_traceback)))
        print ("*** tb_lineno:", exc_traceback.tb_lineno)
        saving()
        return_initial()

    finally:
        party_cleanup()
