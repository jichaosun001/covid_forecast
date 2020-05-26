

##设想R0指数衰减，计算各种参数
from .utils.mse_cal import mse_cal,mse_cal_percent
from datetime import datetime,timedelta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from .utils.enhance_range import enhance_range

def func(x, a, b, c):
    return a * np.exp(-b * x)+c

def cln_incre(incre_list):
    if incre_list[0]>incre_list[1]:
        incre_list[0]=round(incre_list[1]*2/3)
        if incre_list[0]<=0:
            incre_list[0]=1
    return incre_list

class SEIR_exp(object):
    def __init__(self,mode=None,parameter_config=None):
        """
        ##输入一个list of cumulative，输出曲线的R0,final_R0,decrease_ratio,E,I,TE,TI
        """
        # self.number_list=number_list
        if mode=='country':
            self.mode=mode ###国外各国家预测，incre_list不乘10
        else:
            self.mode=''
        self.para_config=parameter_config
        pass

    def generate_pred(self,R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list,printf=False):
        """
        根据预设的R0,decrese_ratio,final_R0 (分别为指数衰减的a,b,c)
        TI,TE，计算预测的increase_num_list,cumulative_number_list
        """
        r1=1/TE
        r2=1/TI
        pred_incre=[]
        pred_cumulative=[]
        cumulative_num=R ##初始的增长值
        for date in range(0,len_list):
            Rt=func(date,R0,decrease_ratio,final_R0) ## 0时刻的R0=R0+c 
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
            cumulative_num=round(cumulative_num,0)
            if printf==True:
                print('Date:{}; E:{}; I:{}; R0:{};cumulative:{},increase:{}'.format(date,E,I,round(Rt,2),cumulative_num,increase_num))   
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
        if I>=E: ##不满足逻辑
            return False
        elif TI>TE: ##不满足逻辑
            return False
        elif decrease_ratio<0.05:
            return False
        # elif len_list<=6 and decrease_ratio<0.075:
        #     return False
        else:
            return True
    
    def get_para_list(self,number_list):
        R0_config=self.para_config['R0_config']
        TI_config=self.para_config['TI_config']
        TE_config=self.para_config['TE_config']
        decrease_ratio_config=self.para_config['decrease_ratio_config']
        final_R0_config=self.para_config['final_R0_config']
        E_config=self.para_config['E_config']
        I_config=self.para_config['I_config']
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
                                        pred_cumula,pred_incre=self.generate_pred(R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list,printf=False)
                                        mse_total=mse_cal(pred_cumula,number_list)
                                        mse_incre=mse_cal(pred_incre,incre_list)
                                        if self.mode=='country':
                                            error_list.append((counter,mse_total+mse_incre,{'R0':R0,'TI':TI,'TE':TE,'decrease_ratio':decrease_ratio,'final_R0':final_R0,'E':E,'I':I}))
                                        else:
                                            error_list.append((counter,mse_total+mse_incre*10,{'R0':R0,'TI':TI,'TE':TE,'decrease_ratio':decrease_ratio,'final_R0':final_R0,'E':E,'I':I}))

        error_list.sort(key=lambda x:x[1])
        print(error_list[0][1])
        return error_list[0]

    def refine_parameter(self,R0,TI,TE,decrease_ratio,final_R0,E,I):
        R0_config=self.para_config['R0_config']
        TI_config=self.para_config['TI_config']
        TE_config=self.para_config['TE_config']
        decrease_ratio_config=self.para_config['decrease_ratio_config']
        final_R0_config=self.para_config['final_R0_config']
        E_config=self.para_config['E_config']
        I_config=self.para_config['I_config']
        R0_step=R0_config['step']/2
        TI_step=TI_config['step']/2
        TE_step=TE_config['step']/2
        decrease_ratio_step=decrease_ratio_config['step']/2
        final_R0_step=final_R0_config['step']/2
        E_step=E_config['step']/2
        I_step=I_config['step']/2
        R0_list=enhance_range(R0-R0_step,R0+R0_step,R0_step)
        TI_list=enhance_range(TI-TI_step,TI+TI_step,TI_step)
        TE_list=enhance_range(TE-TE_step,TE+TE_step,TE_step)
        decrease_ratio_list=enhance_range(decrease_ratio-decrease_ratio_step,decrease_ratio+decrease_ratio_step,decrease_ratio_step)
        final_R0_list=enhance_range(final_R0-final_R0_step,final_R0+final_R0_step,final_R0_step)
        E_list=enhance_range(E-E_step,E+E_step,E_step)
        I_list=enhance_range(I-I_step,I+I_step,I_step)
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
        error=self.select_parameter_list(R0_list,TI_list,TE_list,decrease_ratio_list,final_R0_list,E_list,I_list,number_list,incre_list)
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
        error_new=self.select_parameter_list(R0_list,TI_list,TE_list,decrease_ratio_list,final_R0_list,E_list,I_list,number_list,incre_list)
        return error_new

    def predict_extend(self,number_list,extend_day=30):
        """
        输入一个number_list，输出seir曲线的当前预测值和未来30天预测值，包括累计与新增
        """
        ###默认增加30天预测
        R=number_list[0]
        error=self.select_parameter(number_list)
        R0=error[2]['R0']
        TI=error[2]['TI']
        TE=error[2]['TE']
        decrease_ratio=error[2]['decrease_ratio']
        final_R0=error[2]['final_R0']
        E=error[2]['E']
        I=error[2]['I']
        len_list=len(number_list)
        ## return pred_cumulative,pred_incre
        return {
            'pred':self.generate_pred(R0,TI,TE,decrease_ratio,final_R0,E,I,R,len_list+extend_day,printf=False),
            'parameters':{'R0':R0,'TI':TI,'TE':TE,'decrease_ratio':decrease_ratio,'final_R0':final_R0,'E':E,'I':I,'error':error[1]}
        }


def plot_list(pred_list,true_list):
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

if __name__=='__main__':
    number_list_all=[21, 65, 127, 281, 558, 923, 1321, 1801, 2410, 3125, 3886, 4638, \
        5306, 6059, 6949, 7685, 8395, 9099, 9645, 10151, 10604, 10980, 11364, \
            11676,11946,12170,12335,12453]
    number_list=[5, 16, 32, 54, 157, 434]
    number_list=[38, 145, 321, 566, 880, 1080, 1345, 1591, 1906, 2262, 2640, 3216, 4110, 5143]
    # number_list=number_dict[34]['number_list']
    number_list=[21,65,127,281,558,923,1321]
    # ,1801
    SEIR_exp_=SEIR_exp()
    incre_list=SEIR_exp_.get_incre_number(number_list)
    pred_result=SEIR_exp_.predict_extend(number_list,extend_day=20)
    pred_number=pred_result['pred'][0]
    pred_incre=pred_result['pred'][1]
    parameters=pred_result['parameters']
    plot_list(pred_number,number_list)
    plot_list(pred_incre,incre_list)
    print(parameters)