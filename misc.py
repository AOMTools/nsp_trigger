import numpy as np
def freq_range_gen():
    a1=np.linspace(-120,-40,5)
    a2=np.linspace(40,120,5)
    #a3=np.linspace(-40,40,17)
    a3=np.linspace(-40,-20,3)
    a4=np.linspace(20,40,3)
    a5=np.linspace(-20,-10,3)
    a6=np.linspace(10,20,3)
    a7=np.linspace(-10,-6,2)
    a8=np.linspace(6,10,2)
    a9=np.linspace(-6,6,7)
    b=np.concatenate((a1,a3,a2,a4,a5,a6,a7,a8,a9))
    b=list(set(b))
    b.sort()
    return b
