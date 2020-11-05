
#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2020/03/30 15:41:45
@作者    :jichaosun
'''

## 0330,每个日期，得到三个结果最小的参数组合，输出置信区间，处于中间的值作为当前最优。
## 过去三个日期的最优值，作为预测的range。

##设想R0指数衰减，计算各种参数
import os
from .utils.mse_cal import mse_cal,mse_cal_percent,mae_cal
from datetime import datetime,timedelta
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from .utils.enhance_range import enhance_range
from .utils.utils import plot_with_conf_inter,get_non_valid_r_parameters
from .parameter_config import *
current_dir=os.path.abspath(os.path.dirname(__file__))
import sympy
from sympy import *

##增加限制条件，拐点出现日期大于8天，小于2个月

def func(x, a, b, c):
    return a * np.exp(-b * x)+c

def cln_incre(incre_list):
    if incre_list[0]>incre_list[1]:
        incre_list[0]=round(incre_list[1]*2/3)
        if incre_list[0]<=0:
            incre_list[0]=1
    return incre_list


class seir_config(object):
    error_function=mse_cal # mse
    incre_weight=5


class SEIR_exp(object):
    def __init__(self,mode=None,output_E=False,config=seir_config()):
        """
        ##输入一个list of cumulative，输出曲线的R0,final_R0,decrease_ratio,E,I,TE,TI
        ##默认的pred不会输出潜伏期人数
        """
        # self.number_list=number_list
        if mode=='country':
            self.mode=mode ###国外各国家预测，incre_list不乘10
        else:
            self.mode=''
        self.output_E=output_E
        self.error_function=mse_cal ##修改error_function
        self.config=config
        self.non_valid_R_combination_list=get_non_valid_r_parameters() ##非合理范围的R0 decrease curve
        pass

    def generate_pred(self,R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list,decrease_ratio_enhance=None,enhance_date=None,printf=False):
        """
        根据预设的R0,decrese_ratio,final_R0 (分别为指数衰减的a,b,c)
        TI,TE，计算预测的increase_num_list,cumulative_number_list
        """
        r1=1/TE
        r2=1/TI
        pred_incre=[]
        pred_cumulative=[]
        E_current_list=[]
        cumulative_num=R ##初始的增长值
        for date in range(0,len_list):
            Rt=func(date,R0,decrease_ratio,final_R0) ## 0时刻的R0=R0+c 
            if decrease_ratio_enhance and enhance_date:
                if date==enhance_date:
                    R_cutoff=Rt
                    ##解方程，找到初始R0
                    x=Symbol('x')
                    solve_r=sympy.solve(x * exp( - decrease_ratio_enhance * enhance_date) + final_R0 - R_cutoff,x)
                    R0_reform=solve_r[0]
                if date>enhance_date: ##逐渐减少
                    Rt=func(date,R0_reform,decrease_ratio_enhance,final_R0) ##enhance date之后的Rt
                    Rt=round(Rt,2)
            if date==0:
                increase_num=cumulative_num
            else:
                b=Rt/TI ##传播系数
                E_current=E+b*I-r1*E
                I_current=I+r1*E-r2*I
                cumulative_num=r2*I+cumulative_num
                increase_num=r2*I ##报告数字即收治数字
                R=R+r2*I
                E=E_current
                I=I_current
            increase_num=round(increase_num,0)
            cumulative_num=round(cumulative_num,0)
            pred_incre.append(increase_num)
            pred_cumulative.append(cumulative_num)
            ## round
            E=round(E,0)
            I=round(I,0)
            R=round(R,0)
            E_current_list.append(E)
            if printf==True:
                print('Date:{}; E:{}; I:{}; R0:{};cumulative:{},increase:{}'.format(date,E,I,round(Rt,2),cumulative_num,increase_num))
        if self.output_E:
            return pred_cumulative,pred_incre,E_current_list
        else:   
            return pred_cumulative,pred_incre

    def get_incre_number(self,number_list):
        incre_list=[]
        for i,number in enumerate(number_list):
            if i==0:
                incre_list.append(number_list[0])
            elif i<=len(number_list)-1:
                incre_list.append(number-number_list[i-1])
        incre_list_new=cln_incre(incre_list)
        return incre_list_new

    def conditions(self,R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list):
        if R0<3:
            return False
        elif (R0,decrease_ratio,final_R0) in self.non_valid_R_combination_list:
            return False
        # elif I>=E: ##不满足逻辑
        #     return False
        elif TI>=TE: ##不满足逻辑
            return False
        elif decrease_ratio<0.03:
            return False
        # elif len_list<=6 and decrease_ratio<0.075: 
        #     return False
        else:
            return True
    
    def get_para_list(self,number_list):
        R=number_list[0]
        R0_list=enhance_range(R0_config['min'],R0_config['max'],R0_config['step'])
        TI_list=enhance_range(TI_config['min'],TI_config['max'],TI_config['step']) ##传染期
        TE_list=enhance_range(TE_config['min'],TE_config['max'],TE_config['step']) ##潜伏期
        decrease_ratio_list=enhance_range(decrease_ratio_config['min'],decrease_ratio_config['max'],decrease_ratio_config['step'])
        final_R0_list=enhance_range(final_R0_config['min'],final_R0_config['max'],final_R0_config['step']) ## 取值0.05到0.3
        ##设置最初潜伏期E个，传染期I个，收治人数R个
        E_list=[i*R for i in enhance_range(E_config['min'],E_config['max'],E_config['step'])]
        I_list=[i*R for i in enhance_range(I_config['min'],I_config['max'],I_config['step'])]
        return {
        'R0_list':R0_list,
        'TI_list':TI_list,
        'TE_list':TE_list,
        'decrease_ratio_list':decrease_ratio_list,
        'final_R0_list':final_R0_list,
        'E_list':E_list,
        'I_list':I_list
        }
       
    def select_parameter_list(self,R0_list,TI_list,TE_list,decrease_ratio_list,final_R0_list,E_list,I_list,number_list,incre_list):
        len_list=len(number_list)
        R=number_list[0]
        counter=0
        error_list=[]
        for R0 in R0_list:
            for TI in TI_list:
                for TE in TE_list:
                    for decrease_ratio in decrease_ratio_list:
                        for final_R0 in final_R0_list:
                            for E in E_list:
                                for I in I_list:
                                    counter=counter+1
                                    if counter%50000==0:
                                        print(counter)
                                    if self.conditions(R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list):
                                        if self.output_E:
                                            pred_cumula,pred_incre,_e=self.generate_pred(R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list,printf=False)
                                        else:
                                            pred_cumula,pred_incre=self.generate_pred(R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list,printf=False)
                                        # help(self.config.error_function)
                                        # print('pred_cumula:',pred_cumula)
                                        error_total=self.error_function(pred_cumula,number_list)
                                        error_incre=self.error_function(pred_incre,incre_list)
                                        if self.mode=='country':
                                            error_list.append((counter,error_total+error_incre*self.config.incre_weight,{'R0':R0,'TI':TI,'TE':TE,'decrease_ratio':decrease_ratio,'final_R0':final_R0,'E':E,'I':I}))
                                        else:
                                            error_list.append((counter,error_total+error_incre*self.config.incre_weight,{'R0':R0,'TI':TI,'TE':TE,'decrease_ratio':decrease_ratio,'final_R0':final_R0,'E':E,'I':I}))

        error_list.sort(key=lambda x:x[1])
        # print(error_list[0][1])
        select_index=[0,16,32,64,128]
        error_list_10=error_list[0:129]
        return [error_list_10[i] for i in select_index] ## return 三个最小的error对应的参数, 三个error再次refine后容易变成两个，因此设置成10个

    def refine_parameter(self,R0,TI,TE,decrease_ratio,final_R0,E,I):
        R0_step=R0_config['step']/2
        TI_step=TI_config['step']/2
        TE_step=TE_config['step']/2
        decrease_ratio_step=decrease_ratio_config['step']/4 ##细化 decrease_ratio_step
        final_R0_step=final_R0_config['step']/2
        E_step=E_config['step']/4
        I_step=I_config['step']/4
        R0_list=enhance_range(R0-R0_step,R0+R0_step,R0_step)
        TI_list=enhance_range(TI-TI_step,TI+TI_step,TI_step)
        TE_list=enhance_range(TE-TE_step,TE+TE_step,TE_step)
        decrease_ratio_list=enhance_range(decrease_ratio-2*decrease_ratio_step,decrease_ratio+2*decrease_ratio_step,decrease_ratio_step) ## 细化到0.025
        final_R0_list=enhance_range(final_R0-final_R0_step,final_R0+final_R0_step,final_R0_step)
        E_list=enhance_range(E-2*E_step,E+2*E_step,E_step)
        I_list=enhance_range(I-2*I_step,I+2*I_step,I_step)
        return {
            'R0_list':R0_list,
            'TI_list':TI_list,
            'TE_list':TE_list,
            'decrease_ratio_list':decrease_ratio_list,
            'final_R0_list':final_R0_list,
            'E_list':E_list,
            'I_list':I_list
            }
    

    def select_parameter(self,number_list):
        incre_list=self.get_incre_number(number_list)
        R=incre_list[0]
        len_list=len(number_list)
        para_list=self.get_para_list(number_list)
        R0_list=para_list['R0_list']
        TI_list=para_list['TI_list']
        TE_list=para_list['TE_list']
        decrease_ratio_list=para_list['decrease_ratio_list']
        final_R0_list=para_list['final_R0_list']
        E_list=para_list['E_list']
        I_list=para_list['I_list']
        ##变成三个区间
        error_list=self.select_parameter_list(R0_list,TI_list,TE_list,decrease_ratio_list,final_R0_list,E_list,I_list,number_list,incre_list)
        print('error_list:{}\n'.format(error_list))
        error_refine_list=[]
        for error in error_list:
            # return error
            R0=error[2]['R0']
            TI=error[2]['TI']
            TE=error[2]['TE']
            decrease_ratio=error[2]['decrease_ratio']
            final_R0=error[2]['final_R0']
            E=error[2]['E']
            I=error[2]['I']
            ###微调参数
            new_list=self.refine_parameter(R0,TI,TE,decrease_ratio,final_R0,E,I)
            R0_list=new_list['R0_list']
            TI_list=new_list['TI_list']
            TE_list=new_list['TE_list']
            decrease_ratio_list=new_list['decrease_ratio_list']
            final_R0_list=new_list['final_R0_list']
            E_list=new_list['E_list']
            I_list=new_list['I_list']
            error_new_list=self.select_parameter_list(R0_list,TI_list,TE_list,decrease_ratio_list,final_R0_list,E_list,I_list,number_list,incre_list)
            error_new_min=error_new_list[0]
            if error_new_min[2] not in [i[2] for i in error_refine_list]: ##非重复参数
                error_refine_list.append(error_new_min)
        
        len_error=len(error_refine_list)
        if len_error%2==0:
            middle_index=int(len_error/2)
        else:
            middle_index=int((len_error-1)/2)
        
        error_refine_list=[error_refine_list[0]]+[error_refine_list[middle_index]]+[error_refine_list[-1]] ##取10个error中的首，中，尾三个参数，不一定预测值最小
        assert len(error_refine_list)==3
        print('error_refine_list:',error_refine_list)
        return error_refine_list ##三个refine后最小的error,counter, parameter

    def predict_extend(self,number_list,extend_day=30,write_out=False):
        """
        输入一个number_list，输出seir曲线的当前预测值和未来30天预测值，包括累计与新增, 输出一个3 elements list of dict，包含了参数最小的三套数据
        dict key为counter+str(error), value为{'pred':(pred_cumula,pred_incre),'parameters':{}}
        """
        ###默认增加30天预测
        R=number_list[0]
        error_list=self.select_parameter(number_list)
        results=[]
        for error in error_list:
            R0=error[2]['R0']
            TI=error[2]['TI']
            TE=error[2]['TE']
            decrease_ratio=error[2]['decrease_ratio']
            final_R0=error[2]['final_R0']
            E=error[2]['E']
            I=error[2]['I']
            len_list=len(number_list)
            ## 计算当前的Rt
            current_r=func(len_list-1,R0,decrease_ratio,final_R0)
            key=str(error[0])+'_'+str(error[1])
            ## counter+error as key
            one_result={
            'pred':self.generate_pred(R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list+extend_day,printf=False),
            'parameters':{'R0':R0,'TI':TI,'TE':TE,'decrease_ratio':decrease_ratio,'final_R0':final_R0,'current_R':current_r,
            'E':E,'I':I,'error':error[1],'R':R}
            }
            one_result_dic={key:one_result}
            results.append(one_result_dic) ## 3 key:value
        if write_out:
            self.write_ress(results)
        return results 

    def write_ress(self,input_dict,out_path='tmp_result'):
        file_name=datetime.now().strftime('%m-%d %H:%M') ##以分钟命名输出文件
        out_path_file=os.path.join(current_dir,out_path,file_name)
        input_dict_str=json.dumps(input_dict,indent=6,ensure_ascii=False)
        with open(out_path_file,'w',encoding='utf-8') as w:
            w.write(input_dict_str)



    def plot_list(self,pred_list,true_list):
        len_pred=len(pred_list)
        len_true=len(true_list)
        ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
        plt.plot(range(len_pred),pred_list,'r--',label='prediction')
        plt.plot(range(len_true),true_list,'b-',label='real')
        plt.legend(loc=2)  #指定legend的位置,读者可以自己help它的用法
        #修改主刻度
        xmajorLocator = MultipleLocator(4) #将x主刻度标签设置为20的倍数
        #设置主刻度标签的位置,标签文本的格式
        ax.xaxis.set_major_locator(xmajorLocator)
        #打开网格
        ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
        plt.show()

    def get_confidence_interval(self,pred_result,use_mean=True):
        """
        param pred_result为predict_extend的输出，输出number_list和incre_list的confidence interval
        """
        cumula_incre_list=[]
        for element in pred_result:
            for k,v in element.items():
                cumula_incre_list.append(v['pred']+(v['parameters'],)) #(pred_number,pred_incre,[pred_e],parameters)
        cumula_incre_list.sort(key=lambda x: x[0][-1]) ##根据cumula的最后一个从小到大排序
        middle_index=int((len(cumula_incre_list)-1)/2)

        number_min=cumula_incre_list[0][0]
        number_max=cumula_incre_list[-1][0]
        if use_mean: ###使用最小和最大值的中间值作为预测结果
            number_mean=[(number_min[i]+number_max[i])/2 for i in range(len(number_max))]
        else:
            number_mean=cumula_incre_list[middle_index][0]

        incre_min=cumula_incre_list[0][1]
        incre_max=cumula_incre_list[-1][1]
        if use_mean: ###使用最小和最大值的中间值作为预测结果
            incre_mean=[(incre_min[i]+incre_max[i])/2 for i in range(len(incre_max))]
        else:
            incre_mean=cumula_incre_list[middle_index][1]

        parameter_min=cumula_incre_list[0][-1]
        # parameter_mean=cumula_incre_list[middle_index][-1]
        parameter_max=cumula_incre_list[-1][-1]

        
        return_ress= {
            'number_range':{
                'mean':number_mean,
                'max':number_max,
                'min':number_min
            },
            'incre_range':{
                'mean':incre_mean,
                'max':incre_max,
                'min':incre_min
            },
            'parameter_range':{
                # 'mean':parameter_mean,
                'max':parameter_max,
                'min':parameter_min
            },

        }

        if self.output_E:
            E_min=cumula_incre_list[0][2]
            E_mean=cumula_incre_list[middle_index][2]
            E_max=cumula_incre_list[-1][2] ##第一个key=-1，代表是最大的预测值，第二个2代表是pred的第三位潜伏期人数
            return_ress['E_range']={'mean':E_mean,'min':E_min,'max':E_max}
        return return_ress




if __name__=='__main_':
    number_list=[21, 65, 127, 281, 558, 923, 1321, 1801, 2410, 3125, 3886, 4638, \
        5306, 6059, 6949, 7685, 8395, 9099, 9645, 10151, 10604, 10980, 11364, \
            11676,11946,12170,12335,12453]
    number_list=[5, 16, 32, 54, 157, 434]
    number_list=[38, 145, 321, 566, 880, 1080, 1345, 1591, 1906, 2262, 2640, 3216, 4110, 5143]
    # number_list=number_dict[34]['number_list']
    number_list=[3.0, 9.0, 13.0, 25.0, 41.0, 74.0, 112.0, 150.0, 179.0, 248.0, 345.0, 441.0, 613.0, 1046.0]
    # ,1801
    start_date=datetime(2020,2,20)
    SEIR_exp_=SEIR_exp()
    incre_list=SEIR_exp_.get_incre_number(number_list)
    pred_result=SEIR_exp_.predict_extend(number_list,extend_day=30,write_out=True)
    interval_results=SEIR_exp_.get_confidence_interval(pred_result)
    number_mean=interval_results['number_range']['mean']
    number_min=interval_results['number_range']['min']
    number_max=interval_results['number_range']['max']

    incre_mean=interval_results['incre_range']['mean']
    incre_min=interval_results['incre_range']['min']
    incre_max=interval_results['incre_range']['max']
    plot_with_conf_inter(number_list,number_mean,number_min,number_max,numType='cumulative',title='',start_date=start_date)     
    plot_with_conf_inter(incre_list,incre_mean,incre_min,incre_max,numType='increase',title='',start_date=start_date)


