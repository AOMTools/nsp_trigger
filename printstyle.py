def printstyle_warning(s):
    mess='\x1b[7;31;43m'+s+'\x1b[0m'
    print(mess)
def printstyle_stage1(s):
    print('\t'+'\x1b[0;30;43m'+s+'\x1b[0m')
def printstyle_stage2(s):
    print('\x1b[0;33;40m'+s+'\x1b[0m')
    
