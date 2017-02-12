import numpy as np
def freq_range_gen():
    a1=np.linspace(-100,-40,4)
    a2=np.linspace(40,100,4)
    a3=np.linspace(-40,40,17)
    b=np.concatenate((a1,a3,a2))
    b=list(set(b))
    b.sort()
    return b
