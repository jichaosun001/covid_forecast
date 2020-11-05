

def enhance_range(start,end,step):
    if isinstance(step,int):
        return range(start,end,step)
    else:
        digit=len(str(step).split(".")[1])
    ress_list=[]
    t=start
    while t<=end:
        ress_list.append(t)
        t=t+step
    return [round(i,digit) for i in ress_list]



if __name__=='__main__':
    print(enhance_range(0.05,0.3,0.05))