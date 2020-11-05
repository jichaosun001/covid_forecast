
import os 
current_dir=os.path.abspath(os.path.dirname(__file__))
upper_dir=os.path.join(current_dir,'../')
# os.sys.path.append(upper_dir)
import pandas as pd 
from datetime import datetime
import pandas as pd
from .R0_decrease_select import SEIR_exp
from datetime import datetime,timedelta
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.pyplot as plt
SEIR_exp_=SEIR_exp(mode='country')


def plot_number_incre(number_list,start_date,extend_day=7):
    incre_list=SEIR_exp_.get_incre_number(number_list)
    pred_result=SEIR_exp_.predict_extend(number_list,extend_day=extend_day)
    pred_number=pred_result['pred'][0]
    pred_incre=pred_result['pred'][1]
    parameters=pred_result['parameters']
    len_number=len(number_list)

    all_dates=[]
    all_dates=[]
    for date in range(len_number+extend_day):
        x=start_date+timedelta(date)
        all_dates.append(x.strftime('%m-%d'))
    ###画全量图
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.plot(all_dates[0:len_number],number_list,'b-',label='Real cumulative')
    plt.plot(all_dates,pred_number,'r--',label='Pred cumulative')
    print('final number cumula:',pred_number[-1])
    plt.legend(loc=2)  #指定legend的位置,读者可以自己help它的用法
    plt.xlabel('date')
    plt.ylabel('number')
    #修改主刻度
    xmajorLocator = MultipleLocator(6) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    # plt.savefig('output/china_cumula_{}_{}.png'.format(the_date,start_number),dpi=500,bbox_inches = 'tight')
    plt.show()

    ###plot increase
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.plot(all_dates[0:len_number],incre_list,'b-',label='Real increase')
    plt.plot(all_dates,pred_incre,'r--',label='Pred increase')
    plt.legend(loc=1)  #指定legend的位置,读者可以自己help它的用法
    plt.xlabel('date')
    plt.ylabel('number')
    #修改主刻度
    xmajorLocator = MultipleLocator(6) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    # plt.savefig('output/china_increase_{}_{}.png'.format(the_date,start_number),dpi=500,bbox_inches = 'tight')
    plt.show()
    print(parameters)
