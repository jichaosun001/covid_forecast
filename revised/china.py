#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2020/02/26 08:01:02
@作者    :jichaosun
'''

##对中国非湖北的趋势进行做图
##早期27号
##中期2号
##后期8号，9号
##晚期20号，22号
import os
current_dir=os.path.abspath(os.path.dirname(__file__))
root_dir=os.path.join(current_dir,'../')
os.sys.path.append(root_dir)
from ..R0_decrease_select import SEIR_exp
import pandas as pd
import json
from datetime import datetime,timedelta
from ..utils.utils import get_all_data,get_single_district
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.pyplot as plt



para_config={
    "R0_config":{'min':2,'max':7,'step':1},
    "TI_config":{'min':1,'max':5,'step':1},
    "TE_config":{'min':3,'max':11,'step':2},
    "decrease_ratio_config":{'min':0.05,'max':0.45,'step':0.05},
    "final_R0_config":{'min':0.05,'max':0.35,'step':0.05},
    "E_config":{'min':5,'max':81,'step':10},
    "I_config":{'min':5,'max':51,'step':10},
}


SEIR_exp_=SEIR_exp(parameter_config=para_config)
output_dir=os.path.join(current_dir,'output')


def get_all_data():
    file_name='data/china_cumulative_data.json'
    with open(os.path.join(current_dir,file_name),'r') as f:
        all_str=f.read()
    all_dict=json.loads(all_str)
    return all_dict

def plot_certain_date(plot_date,number_list):
    the_date = datetime.strptime(plot_date, '%Y-%m-%d').strftime('%m-%d')
    tick_size=14
    label_size=17
    start_date=datetime(2020,1,20)
    len_number=len(number_list)
    all_dates=[]
    all_dates=[]
    for date in range(len_number):
        x=start_date+timedelta(date)
        all_dates.append(x.strftime('%m-%d'))
    start_number=all_dates.index(the_date)
    plot_point=[start_number]
    the_date=all_dates[start_number]
    i=0
    number_list_sub=number_list[0:plot_point[i]]
    extend_day=len_number-plot_point[i]
    incre_list=SEIR_exp_.get_incre_number(number_list)
    incre_list_sub=incre_list[0:plot_point[i]]
    pred_result=SEIR_exp_.predict_extend(number_list_sub,extend_day=extend_day)
    pred_number=pred_result['pred'][0]
    pred_incre=pred_result['pred'][1]
    parameters=pred_result['parameters']
    parameters_str=json.dumps(parameters,ensure_ascii=False,indent=5)

    label_font = {'weight' : 'normal','size':label_size}
    ###画全量图
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.tick_params(labelsize=tick_size) ##坐标值字体

    plt.plot(all_dates[0:plot_point[i]],number_list_sub,'b-',label='Real cumulative',linewidth=3)
    plt.plot(all_dates[plot_point[i]::],number_list[plot_point[i]::],'y-',label='Posterior real cumulative',linewidth=3)
    plt.plot(all_dates,pred_number,'r--',label='Pred cumulative',linewidth=3)
    plt.axvline(x=all_dates[plot_point[i]],ls="--",c="green",linewidth=3)#添加垂直直线
    print('final number cumula:',pred_number[-1])
    plt.legend(loc=2)  #指定legend的位置,读者可以自己help它的用法
    plt.xlabel('Date',label_font)
    if start_number in [6,22]:
        plt.ylabel('Number',label_font)
    #修改主刻度
    xmajorLocator = MultipleLocator(21) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    plt.title('Predict date: '+all_dates[plot_point[i]],label_font)
    plt.savefig(os.path.join(output_dir,'china/china_cumula_{}.png'.format(the_date)),dpi=500,bbox_inches = 'tight')
    plt.show()

    ###plot increase
    # plt.figure(figsize=(8, 6))
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.tick_params(labelsize=tick_size) ##坐标值字体
    plt.plot(all_dates[0:plot_point[i]],incre_list_sub,'b-',label='Real increase',linewidth=3)
    plt.plot(all_dates[plot_point[i]::],incre_list[plot_point[i]::],'y-',label='Posterior real increase',linewidth=3)
    plt.plot(all_dates,pred_incre,'r--',label='Pred increase',linewidth=3)
    plt.axvline(x=all_dates[plot_point[i]],ls="--",c="green",linewidth=3)#添加垂直直线
    plt.legend(loc=1)  #指定legend的位置,读者可以自己help它的用法
    # plt.xlabel('Date',label_font)
    if start_number in [6,22]:
        plt.ylabel('Number',label_font)
    #修改主刻度
    xmajorLocator = MultipleLocator(21) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    plt.title('Predict date: '+all_dates[plot_point[i]],label_font)
    plt.savefig(os.path.join(output_dir,'china/china_increase_{}.png'.format(the_date)),dpi=500,bbox_inches = 'tight')
    plt.show()

    with open(os.path.join(output_dir,'china/china_no_hubei_pred_{}.csv'.format(all_dates[start_number])),'w',encoding='utf-8') as w:
        for i,number in enumerate(pred_number):
            if i==0:
                write_Str='date,real_cumulative,real_increase,pred_cumulative,pred_increase\n'
                w.write(write_Str)
            write_str='{},{},{},{},{}\n'.format(all_dates[i],number_list[i],incre_list[i],pred_number[i],pred_incre[i])
            w.write(write_str)

    with open(os.path.join(output_dir,'china/china_no_hubei_parameter_{}.csv'.format(all_dates[start_number])),'w',encoding='utf-8') as w:
        w.write(parameters_str)




if __name__=='__main__':
    all_dict=get_all_data()
    district='china_except_hubei'
    start_date,number_list=get_single_district(all_dict,district)
    date_list_for_plot=['2020-01-26','2020-01-27','2020-02-04','2020-02-11','2020-02-18','2020-02-25']
    plot_date=date_list_for_plot[-1]
    plot_certain_date(plot_date,number_list)
    # for plot_date in date_list_for_plot:
    #     plot_certain_date(plot_date,number_list)