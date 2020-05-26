#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2020/02/28 10:21:56
@作者    :jichaosun
'''

# plot R0 curve
import numpy as np
from datetime import datetime, timedelta
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.pyplot as plt

def func(x, a, b, c):
    return a * np.exp(-b * x)+c



start_date=datetime(2020,1,20)
end_date=datetime(2020,3,10)

label_font = {'weight' : 'normal','size':13}
def all_plot_Rt_curve(title='R(t) decrease curve'):
    all_dates=[]
    current_date=start_date
    while current_date<=end_date:
        all_dates.append(current_date.strftime('%m-%d'))
        current_date=current_date+timedelta(1)
    
    Rt_wuhan=[]
    R0=4.5
    decrease_ratio=0.1
    final_R=0.125
    for i,date in enumerate(all_dates):
        R=func(i,R0,decrease_ratio,final_R)
        Rt_wuhan.append(R)

    Rt_china=[]
    R0=6
    decrease_ratio=0.2
    final_R=0.3
    for i,date in enumerate(all_dates):
        R=func(i,R0,decrease_ratio,final_R)
        Rt_china.append(R)

    
    Rt_hubei=[]
    R0=6
    decrease_ratio=0.15
    final_R=0.2
    for i,date in enumerate(all_dates):
        R=func(i,R0,decrease_ratio,final_R)
        Rt_hubei.append(R)

    ###画全量图
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.plot(all_dates,Rt_wuhan,'b-',label='Wuhan')
    plt.plot(all_dates,Rt_china,'r-',label='China excluding hubei')
    plt.plot(all_dates,Rt_hubei,'y-',label='Hubei excluding wuhan')
    plt.legend(loc=1)
    plt.xlabel('Date',label_font)
    plt.ylabel('R(t)',label_font)
    # plt.title(title,label_font)
    #修改主刻度
    xmajorLocator = MultipleLocator(7) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    plt.savefig('{}.png'.format(title),dpi=500,bbox_inches = 'tight')
    plt.show()
    print(Rt_china[-1],Rt_hubei[-1],Rt_wuhan[-1])

all_plot_Rt_curve(title='R(t) decrease curve')