#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2020/02/27 06:40:30
@作者    :jichaosun
'''
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from .enhance_range import enhance_range
import numpy as np

def incre_list_to_numbers(incre_list):
    """
    由incre_list，生成number_list
    """
    number_list=[]
    for i in range(len(incre_list)):
        number_list.append(sum(incre_list[0:i+1]))
    return number_list


###将前几个非单调上升趋势的数据进行转换
def process_first_batch(number_list,incre_list,first_batch=4):
    ###对湖北非武汉前四天数据做简单处理，维持incre_list单调上升趋势
    first_four=incre_list[0:first_batch] ##前四个不是单调上升，改变一下
    sum_four=sum(first_four)
    adjust_p=range(1,first_batch+1)
    adjust_sum=sum(adjust_p)
    adjust_number=[round(p*sum_four/adjust_sum) for p in adjust_p]
    incre_list[0:first_batch]=adjust_number
    number_list[0:first_batch]=incre_list_to_numbers(adjust_number)
    return number_list,incre_list


def plot_list(pred_list,true_list,numType='',title='',save_path=None,start_date=datetime(2020,1,20)):
    len_pred=len(pred_list)
    all_dates=[]
    for date in range(len_pred):
        x=start_date+timedelta(date)
        all_dates.append(x.strftime('%m-%d'))
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.plot(all_dates,pred_list,'r--',label='Pred {}'.format(numType))
    plt.plot(all_dates,true_list,'b-',label='Real {}'.format(numType))
    plt.xlabel('date')
    plt.ylabel('number')
    plt.legend(loc=2)  #指定legend的位置,读者可以自己help它的用法
    #修改主刻度
    xmajorLocator = MultipleLocator(4) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    if title:
        plt.title(title)
    if save_path:
        plt.savefig(save_path,dpi=500,bbox_inches = 'tight')
    plt.show()


##计算两个列表的相对误差

def error_cal(list_true,list_pred):
    len_list=len(list_true)
    zip_list=zip(list_true,list_pred)
    error_list=[abs((i[0]-i[1])/i[0]) for i in zip_list]
    return sum(error_list)/len_list


##plot value with interval

##输入真实值，预测值，预测值上限，预测值下限, start_date, 输出图片, ##加入enhance_pred_list，假设防控措施加强后，预计的曲线

def plot_with_conf_inter(list_true,list_pred_mean,list_pred_min,list_pred_max,enhance_pred_list=[],numType='',title='',save_path=None,start_date=datetime(2020,1,20),label_size=15):
    scale=1000
    list_true=[i/scale for i in list_true]
    list_pred_mean=[i/scale for i in list_pred_mean]
    list_pred_min=[i/scale for i in list_pred_min]
    list_pred_max=[i/scale for i in list_pred_max]
    len_pred=len(list_pred_mean)
    len_true=len(list_true)
    all_dates=[]
    for date in range(len_pred):
        x=start_date+timedelta(date)
        all_dates.append(x.strftime('%m-%d'))
    label_font = {'weight' : 'normal','size':label_size}
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.plot(all_dates,list_pred_mean,'r--',label='Pred {}'.format(numType),linewidth=2)
    plt.plot(all_dates[:len_true],list_true,'b-',label='Real {}'.format(numType),linewidth=2)
    plt.axvline(x=all_dates[len_true],ls="--",c="green")#添加垂直直线
    ax.fill_between(all_dates, list_pred_min, list_pred_max, color='C1', alpha=0.4) ##画置信区间
    if enhance_pred_list:
        enhance_pred_list_=[i/scale for i in enhance_pred_list]
        plt.plot(all_dates[len_true:],enhance_pred_list_,'y--',label='Pred (S) {}'.format(numType),linewidth=2)
    plt.xlabel('Date',label_font)
    plt.ylabel('Number (k)',label_font)
    plt.legend(loc=2)  #指定legend的位置,读者可以自己help它的用法
    #修改主刻度
    xmajorLocator = MultipleLocator(10) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    if title:
        plt.title(title,label_font)
    if save_path:
        plt.savefig(save_path,dpi=500,bbox_inches = 'tight')
    plt.show()


##寻找R0和decrease ratio的约束
##要求R降到1以下的时间大于7，小于60天
def func(x, a, b, c):
    return a * np.exp(-b * x)+c

def R_function_condition(r0,decrease_ratio,final_r,min_day=7,max_day=70):
    r_min_day=func(min_day,r0,decrease_ratio,final_r)
    r_max_day=func(max_day,r0,decrease_ratio,final_r)
    if r_min_day>1 and r_max_day<1:
        return True
    else:
        return False

from ..parameter_config import R0_config,decrease_ratio_config,final_R0_config
def get_non_valid_r_parameters(R0_config=R0_config,decrease_ratio_config=decrease_ratio_config,final_R0_config=final_R0_config):
    R0_list=enhance_range(R0_config['min'],R0_config['max'],round(R0_config['step']/2,2))
    decrease_ratio_list=enhance_range(decrease_ratio_config['min'],decrease_ratio_config['max'],round(decrease_ratio_config['step']/2,2))
    final_R0_list=enhance_range(final_R0_config['min'],final_R0_config['max'],round(final_R0_config['step']/2,2))

    not_valid_list=[]
    count=0
    not_valid_count=0
    for R0 in R0_list:
        for decrease_ratio in decrease_ratio_list:
            for final_R0 in final_R0_list:
                count+=1
                if not R_function_condition(R0,decrease_ratio,final_R0):
                    not_valid_count+=1
                    not_valid_list.append((R0,decrease_ratio,final_R0))
    print('total r combination counts:{}; not_valid_r combination counts:{}'.format(count,not_valid_count))
    return not_valid_list

