##第一周，第二周，第三周，第四周，绘制湖北非武汉的图示

##预测，真实，调整后数据

import os
current_dir=os.path.abspath(os.path.dirname(__file__))
root_dir=os.path.join(current_dir,'../')
os.sys.path.append(root_dir)
output_dir=os.path.join(current_dir,'output')
import json

from ..R0_decrease_select import SEIR_exp
import pandas as pd
from datetime import datetime,timedelta
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import copy
from ..utils.utils import incre_list_to_numbers,process_first_batch
from ..utils.utils import get_all_data,get_single_district
all_dict=get_all_data()
district='hubei_except_wuhan'
start_date,raw_number_list=get_single_district(all_dict,district)
raw_incre_list=SEIR_exp().get_incre_number(raw_number_list)
raw_number_list,raw_incre_list=process_first_batch(raw_number_list,raw_incre_list,first_batch=4)
para_config={
    "R0_config":{'min':2,'max':7,'step':1},
    "TI_config":{'min':1,'max':5,'step':1},
    "TE_config":{'min':3,'max':11,'step':2},
    "decrease_ratio_config":{'min':0.05,'max':0.45,'step':0.05},
    "final_R0_config":{'min':0.05,'max':0.35,'step':0.05},
    "E_config":{'min':5,'max':81,'step':16},
    "I_config":{'min':5,'max':51,'step':16},
}

def reform_list(clinical_case,all_case,incre_list,start=23,date=0):
    """
    将临床诊断病例摊分到过去7天，包括当天
    date=0,1,2分别代表23，24，25，无需修改start
    对于12-14号，输入number,13,14输入的是调整后的number，输入当天的临床病例新增数，总新增数，得到从当天到过去七天调整后的数字
    """
    incre_list_new=[]
    suspect=[2622, 2073, 2067, 2272, 1814, 1685, 1400, 1225, 1135]
    suspect_sub=suspect[date:date+7] ##疑似病例
    suspect_sum=sum(suspect_sub) 
    percent_7=[i/suspect_sum for i in suspect_sub]
    current_rna_case=all_case-clinical_case ###当前日期的核酸检测值
    add_case=[round(clinical_case*percent) for percent in percent_7]
    counter=0
    for i,number in enumerate(incre_list):
        if i>=start+date-6 and i<=start+date:
            if i<start+date:
                current_number=incre_list[i]+add_case[counter]
            else:
                current_number=current_rna_case+add_case[counter]
            counter=counter+1
        else:
            current_number=number
        incre_list_new.append(current_number)
    return incre_list_new



##构建函数，输入一个时间点，输出一个number_list，可能原始，也可能调整过
def adjust_number_list(number_list,clinical_case_list=[968,385,216],all_case_list=[1404,783,497],clinical_date_list=[23,24,25]):
    """
    para start_number为截止该天 其中确诊病例出现12号对应23
    para number_list，原始的number_list,输出调整后的天数和当天对应的number_list字典
    12号，用的是1-12天数据，即i=23
    """
    SEIR_exp_=SEIR_exp(parameter_config=para_config)
    new_number_list=copy.deepcopy(number_list)
    incre_list=SEIR_exp().get_incre_number(number_list)
    new_number_dict={}
    seir_pred_incre=[]
    for i in range(0,len(number_list)):
        if i in clinical_date_list: ### 有临床病例的日期开始预测，对number list 和incre_list重写
            date=i-clinical_date_list[0] ## 0,1,2
            clinical_case=clinical_case_list[date]
            all_case=all_case_list[date]
            incre_list=reform_list(clinical_case,all_case,incre_list,date=date)
            new_number_list=incre_list_to_numbers(incre_list)
            # print('i:',i,incre_list[10:])
        if incre_list[i]<0:###负数 ##对number_list和incre_list重写
            # print('i:',i,incre_list)
            incre_list[i]=pred_incre[-1] ##
            new_number_list=incre_list_to_numbers(incre_list)
        if i in [29,30,33,34,35]:
            number_list_sub=new_number_list[0:i] ##截止当天前一天预测当于，用于负数的替换
            pred_result=SEIR_exp_.predict_extend(number_list_sub,extend_day=1)
            pred_incre=pred_result['pred'][1]
            seir_pred_incre.append(pred_incre[-1])
        # print('\n\ni:',i,incre_list[10:],'\n\n')
        new_number_dict[i]={'number_list':copy.deepcopy(new_number_list),'incre_list':copy.deepcopy(incre_list)}
    return new_number_dict


# number_dict=adjust_number_list(raw_number_list)
# number_dict_str=json.dumps(number_dict,ensure_ascii=False,indent=5)
# with open(os.path.join(output_dir,'hubei/adjust_number.json'),'w',encoding='utf-8') as w:
#     w.write(number_dict_str)


##22应该是一样的
##23过去七天变了的
##24又变了
##25又变了
##26与25一样
##29没变，30修正了-266 

##start_number代表使用前n天的数据
##如果使用12号及以前数据，start_number=24, 12号 index为23，数量为24

# start_number=24,为12号及以前数据

def plot_certain_date(plot_date,raw_number_list=raw_number_list):
    the_date = datetime.strptime(plot_date, '%Y-%m-%d').strftime('%m-%d')
    tick_size=14
    label_size=17
    len_number=len(number_dict[1]['number_list'])
    all_dates=[]
    start_date=datetime(2020,1,20)
    for date in range(len_number):
        x=start_date+timedelta(date)
        all_dates.append(x.strftime('%m-%d'))
    start_number=all_dates.index(the_date)

    SEIR_exp_=SEIR_exp(parameter_config=para_config)
    number_list=number_dict[start_number]['number_list']

    the_date=all_dates[start_number] ##13号开始，使用的是12号及以前数据
    number_list_sub=number_list[0:start_number]
    raw_number_list_sub=raw_number_list[0:start_number]
    raw_incre_list=SEIR_exp_.get_incre_number(raw_number_list)
    extend_day=len_number-start_number
    incre_list=SEIR_exp_.get_incre_number(number_list)
    # incre_list_sub=incre_list[0:start_number]
    raw_incre_list_sub=raw_incre_list[0:start_number]
    pred_result=SEIR_exp_.predict_extend(number_list_sub,extend_day=extend_day)
    pred_number=pred_result['pred'][0]
    pred_incre=pred_result['pred'][1]
    parameters=pred_result['parameters']
    parameters_str=json.dumps(parameters,ensure_ascii=False,indent=5)

    ###画全量图
    label_font = {'weight' : 'normal','size':label_size}
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.tick_params(labelsize=tick_size) ##坐标值字体
    if start_number in [7,25]:
        plt.ylabel('Number',label_font)
    plt.plot(all_dates[0:start_number],raw_number_list_sub,'b-',label='Real cumulative',linewidth=3)
    plt.plot(all_dates[start_number::],raw_number_list[start_number::],'y-',label='Posterior real cumulative',linewidth=3)
    plt.plot(all_dates,pred_number,'r--',label='Pred cumulative',linewidth=3)
    plt.axvline(x=all_dates[start_number],ls="--",c="green",linewidth=3)#添加垂直直线

    print('pred_number_final:',pred_number[-1])
    if start_number>=24:
        plt.plot(all_dates[0:start_number],number_list[0:start_number],color='grey',linestyle=':',label='Adjust cumulative',linewidth=2)
    # plt.legend(loc=2)  #指定legend的位置,读者可以自己help它的用法
    plt.legend(loc=2, numpoints=1)
    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize='small')

    plt.xlabel('Date',label_font)

    #修改主刻度
    xmajorLocator = MultipleLocator(7) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    plt.title('Predict date: '+all_dates[start_number],label_font)
    plt.savefig(os.path.join(output_dir,'hubei/hubei_cumula_{}.png'.format(the_date)),dpi=500,bbox_inches = 'tight')
    plt.show()

    ###plot increase
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
    plt.tick_params(labelsize=tick_size) ##坐标值字体
    plt.plot(all_dates[0:start_number],raw_incre_list_sub,'b-',label='Real increase',linewidth=3)
    plt.plot(all_dates[start_number::],raw_incre_list[start_number::],'y-',label='Posterior real increase',linewidth=3)
    plt.plot(all_dates,pred_incre,'r--',label='Pred increase',linewidth=3)
    if start_number>=24:
        plt.plot(all_dates[0:start_number],incre_list[0:start_number],color='grey',linestyle=':',label='Adjust increase',linewidth=3)
    plt.axvline(x=all_dates[start_number],ls="--",c="green",linewidth=3)#添加垂直直线
    plt.legend(loc=1,numpoints=1)  #指定legend的位置,读者可以自己help它的用法    plt.legend(loc=2, numpoints=1)
    leg = plt.gca().get_legend()
    ltext = leg.get_texts()
    plt.setp(ltext, fontsize='small')
    # plt.xlabel('Date',label_font)
    if start_number in [7,25]:
        plt.ylabel('Number',label_font)
    #修改主刻度
    xmajorLocator = MultipleLocator(7) #将x主刻度标签设置为20的倍数
    #设置主刻度标签的位置,标签文本的格式
    ax.xaxis.set_major_locator(xmajorLocator)
    #打开网格
    ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
    plt.title('Predict date: '+all_dates[start_number],label_font)
    plt.savefig(os.path.join(output_dir,'hubei/hubei_increase_{}.png'.format(the_date)),dpi=500,bbox_inches = 'tight')
    plt.show()

    with open(os.path.join(output_dir,'hubei/hubei_pred_{}.csv'.format(all_dates[start_number])),'w',encoding='utf-8') as w:
        for i,number in enumerate(pred_number):
            if i==0:
                write_Str='date,real_cumulative,real_increase,pred_cumulative,pred_increase\n'
                w.write(write_Str)
            write_str='{},{},{},{},{}\n'.format(all_dates[i],number_list[i],incre_list[i],pred_number[i],pred_incre[i])
            w.write(write_str)

    with open(os.path.join(output_dir,'hubei/hubei_parameter_{}.csv'.format(all_dates[start_number])),'w',encoding='utf-8') as w:
        w.write(parameters_str)



if __name__=='__main__':
    with open(os.path.join(current_dir,'data/hubei_adjust_numbers.json'),'r',encoding='utf-8') as f:
        number_dict_str=f.read()
    number_dict_=json.loads(number_dict_str)
    number_dict={}
    for k,v in number_dict_.items():
        number_dict[int(k)]=v
    
    date_list_for_plot=['2020-01-27','2020-02-04','2020-02-11','2020-02-14','2020-02-18','2020-02-25']
    plot_date=date_list_for_plot[-1]
    plot_certain_date(plot_date)
    # for plot_date in date_list_for_plot:
    #     plot_certain_date(plot_date)