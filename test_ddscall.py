import subprocess
bashCommand="cat ../apps2/Q19_2.script | ./dds_encode -d /dev/ioboards/dds_QO0019"
print(bashCommand.split())
process=subprocess.Popen(bashCommand,cwd='/home/qitlab/programs/usbdds/apps',stdout=subprocess.PIPE,shell=True)
(output,error)=process.communicate()
print(output,error)
