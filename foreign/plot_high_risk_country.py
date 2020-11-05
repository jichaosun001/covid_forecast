#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2020/03/04 20:10:18
@作者    :jichaosun
'''

##对高危国家进行预测
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
SEIR_exp_=SEIR_exp(mode='country',output_E=True)
from .plot_number_incre import plot_number_incre
from .utils.fill_null_date import fill_date_df
from .utils.utils import plot_with_conf_inter


# count_number=cov19_data['国家或地区'].value_counts().reset_index()
# count_number[count_number['国家或地区']>7]
# country_names_15=open('data/15_country.txt').readlines()
# country_names_15=[i.strip('\n') for i in country_names_15]



def str_to_date(x_Str):
    return datetime.strptime(x_Str, '%Y%m%d')

class prepare_data_func(object):
    def __init__(self,raw_file,end_date):
        self.raw_file=raw_file
        self.end_date=end_date
        self.cov19_data=pd.read_excel(raw_file)


    def get_country_df(self,country_name):
        cov19_data=self.cov19_data
        cov19_data.drop_duplicates(keep='first',inplace=True)
        country_df=cov19_data[['日期','累计确诊','国家或地区']][cov19_data['国家或地区']==country_name]
        country_df['date']=country_df['日期'].astype(str).map(str_to_date)
        country_df.sort_values(by=['date'],inplace=True)
        print(country_df)
        new_country_df=fill_date_df(country_df)
        return new_country_df

    def return_numbers(self,start_date,country_df):
        keep_df=country_df[(country_df['date']>=start_date) & (country_df['date']<=self.end_date)]
        number_list=keep_df['累计确诊'].tolist()
        return number_list

    def return_posterior_numbers(self,start_date,country_df):
        keep_df=country_df[(country_df['date']>=start_date) & (country_df['date']<=datetime(2020,5,26))]
        number_list=keep_df['累计确诊'].tolist()
        return number_list

    country_start_date={
    '新加坡':datetime(2020,2,1),
    '美国':datetime(2020,3,1),
    '泰国':datetime(2020,1,29),
    '韩国':datetime(2020,2,18),
    '加拿大':datetime(2020,1,29),
    '阿联酋':datetime(2020,1,29),
    '澳大利亚':datetime(2020,1,28),
    '马来西亚':datetime(2020,1,29),
    '越南':datetime(2020,1,28),
    '日本本土':datetime(2020,2,11),
    '英国':datetime(2020,2,27),
    '法国':datetime(2020,2,25),
    '德国':datetime(2020,2,24),
    '伊朗':datetime(2020,2,19),
    '意大利':datetime(2020,2,21),
    '西班牙':datetime(2020,2,25)
    }


###计算每个国家未来一月预测的发病人数

class plot_and_pred(object):
    """
    取过去三天或5天的预测结果中间值，生成三个list，作为最终结果confidence interval输出
    取过去三天的中间值，然后三天结果汇总，会出现三天结果完全一致。
    因此选择取一天的最小10个error的第一个值，中间值，最后一个值的参数作为range
    取三组参数形成的曲线的最小值，最大值，平均值作为预测结果
    """
    def __init__(self,country,country_eng,output_dir,enhance_decrease_ratio=0.10,extend_day=29):
        self.enhance_decrease_ratio=enhance_decrease_ratio ##加强防控后的下降速率
        self.country=country
        self.country_eng=country_eng
        self.output_dir=output_dir
        self.extend_day=extend_day
        self.start_date=country_start_date[country]
        country_df=get_country_df(country)
        self.number_list=return_numbers(self.start_date,country_df)
        self.posterior_number_list=return_posterior_numbers(self.start_date,country_df)
        print('self.number_list:',self.number_list)
        self.incre_list=SEIR_exp_.get_incre_number(self.number_list)
        self.posterior_incre_list=SEIR_exp_.get_incre_number(self.posterior_number_list)
        self.len_num=len(self.number_list)
        # print(self.incre_list)

    def get_pred_result(self,number_list):
        diff=self.len_num-len(number_list)
        extend_day=self.extend_day
        # print(number_list)
        incre_list=SEIR_exp_.get_incre_number(number_list)
        pred_result=SEIR_exp_.predict_extend(number_list,extend_day=extend_day+diff) ## is a list of dict
        return number_list,incre_list,pred_result
    
    def get_mean_pred(self,number_list_):
        number_list,incre_list,pred_result=self.get_pred_result(number_list_)
        interval_results=SEIR_exp_.get_confidence_interval(pred_result)
        number_mean=interval_results['number_range']['mean']
        incre_mean=interval_results['incre_range']['mean']
        E_mean=interval_results['E_range']['mean']
        # parameter_mean=interval_results['parameter_range']['mean']
        len_number=len(number_list)

        return {
            'pred_number':number_mean,
            'pred_incre':incre_mean,
            'pred_E':E_mean,
            # 'pred_parameter':parameter_mean,
            'number_list':number_list,
            'incre_list':incre_list,
            'len_number':len_number
            }

    def get_past_n_pred(self,past_days=3):
        """
        使用过去三天的数据，生成三套pred_mean
        """
        number_list=self.number_list
        past_n_result=[]
        for past_day in range(past_days):
            if past_day==0:
                number_list_sub=number_list
            else:
                number_list_sub=number_list[0:0-past_day]
            mean_pred=self.get_mean_pred(number_list_sub)
            mean_pred['past_day']=past_day
            past_n_result.append(mean_pred)
        return past_n_result ## list of dict
    
    def get_past_n_intervals(self,past_days=3):
        past_n_result=self.get_past_n_pred(past_days=past_days)
        past_n_result.sort(key=lambda x: x['pred_number'][-1]) ##从小到大
        middle_index=int((len(past_n_result)-1)/2)

        number_min=past_n_result[0]['pred_number']
        number_mean=past_n_result[middle_index]['pred_number']
        number_max=past_n_result[-1]['pred_number']

        incre_min=past_n_result[0]['pred_incre']
        incre_mean=past_n_result[middle_index]['pred_incre']
        incre_max=past_n_result[-1]['pred_incre']

        parameter_min=past_n_result[0]['pred_parameter']
        parameter_mean=past_n_result[middle_index]['pred_parameter']
        parameter_max=past_n_result[-1]['pred_parameter']
     
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
                'mean':parameter_mean,
                'max':parameter_max,
                'min':parameter_min
            },

        }
        print('return_ress:',return_ress)
        return return_ress


    def plot_and_write_v2(self):
        """
        plot with no confidential intervals and write out
        """

        number_list=self.number_list
        # incre_list=self.incre_list
        len_train=len(number_list)

        # interval_results=self.get_past_n_intervals()
        number_list,incre_list,pred_result=self.get_pred_result(self.number_list)
        interval_results=SEIR_exp_.get_confidence_interval(pred_result)
        number_mean=interval_results['number_range']['mean']
        number_min=interval_results['number_range']['min']
        number_max=interval_results['number_range']['max']
        incre_mean=interval_results['incre_range']['mean']
        incre_min=interval_results['incre_range']['min']
        incre_max=interval_results['incre_range']['max']
        parameters=interval_results['parameter_range']


        number_pred=number_max
        incre_pred=incre_max
        scale=1000

        number_pred=[i/scale for i in number_pred]
        incre_pred=[i/scale for i in incre_pred]

        tick_size=14
        label_size=17
        label_font = {'weight' : 'normal','size':label_size}
        all_number_list=self.posterior_number_list
        all_number_list=[i/scale for i in all_number_list]
        all_incre_list=self.posterior_incre_list
        all_incre_list=[i/scale for i in all_incre_list]
        len_number=len(all_number_list)
        start_date=self.start_date
        all_dates=[]
        for date in range(len_number):
            x=start_date+timedelta(date)
            all_dates.append(x.strftime('%m-%d'))
        
        ###画全量图
        plt.figure(figsize=(8, 6))
        ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
        plt.tick_params(labelsize=tick_size) ##坐标值字体

        plt.plot(all_dates[0:len_train],all_number_list[0:len_train],'b-',label='Real cumulative',linewidth=3)
        plt.plot(all_dates[len_train::],all_number_list[len_train::],'y-',label='Posterior real cumulative',linewidth=3)
        plt.plot(all_dates,number_pred,'r--',label='Pred cumulative',linewidth=3)
        plt.axvline(x=all_dates[len_train],ls="--",c="green",linewidth=3)#添加垂直直线
        print('final number cumula:',number_pred[-1])
        ## difference
        diff=(number_pred[-1]-all_number_list[-1])/all_number_list[-1]
        with open(os.path.join(output_dir,self.country_eng),'w') as w:
            w.write('pred: {},real: {},diff: {}\n'.format(number_pred[-1],all_number_list[-1],diff))
        plt.legend(loc=2)  #指定legend的位置,读者可以自己help它的用法
        plt.xlabel('Date',label_font)
        plt.ylabel('Number (K)',label_font)
        #修改主刻度
        xmajorLocator = MultipleLocator(14) #将x主刻度标签设置为20的倍数
        #设置主刻度标签的位置,标签文本的格式
        ax.xaxis.set_major_locator(xmajorLocator)
        #打开网格
        ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
        plt.title('{}, Predict date: {}'.format(self.country_eng,all_dates[len_train-1]),label_font)
        plt.savefig(os.path.join(output_dir,'{}_cumula.png'.format(self.country_eng)),dpi=500,bbox_inches = 'tight')
        plt.show()

        ###plot increase
        # plt.figure(figsize=(8, 6))
        plt.figure(figsize=(8, 6))
        ax = plt.subplot(111) #注意:一般都在ax中设置,不再plot中设置
        plt.tick_params(labelsize=tick_size) ##坐标值字体
        plt.plot(all_dates[0:len_train],all_incre_list[0:len_train],'b-',label='Real increase',linewidth=3)
        plt.plot(all_dates[len_train::],all_incre_list[len_train::],'y-',label='Posterior real increase',linewidth=3)
        plt.plot(all_dates,incre_pred,'r--',label='Pred increase',linewidth=3)
        plt.axvline(x=all_dates[len_train],ls="--",c="green",linewidth=3)#添加垂直直线
        plt.legend(loc=2)  #指定legend的位置,读者可以自己help它的用法
        plt.xlabel('Date',label_font)
        plt.ylabel('Number (K)',label_font)
        #修改主刻度
        xmajorLocator = MultipleLocator(14) #将x主刻度标签设置为20的倍数
        #设置主刻度标签的位置,标签文本的格式
        ax.xaxis.set_major_locator(xmajorLocator)
        #打开网格
        ax.xaxis.grid(True, which='major') #x坐标轴的网格使用主刻度
        plt.title('{}, Predict date: {}'.format(self.country_eng,all_dates[len_train-1]),label_font)
        plt.savefig(os.path.join(output_dir,'{}_incre.png'.format(self.country_eng)),dpi=500,bbox_inches = 'tight')
        plt.show()



    def plot_and_write(self):

        """
        plot confidential intervals and write out
        """
        number_list=self.number_list
        incre_list=self.incre_list
        len_number=len(number_list)

        # interval_results=self.get_past_n_intervals()
        number_list,incre_list,pred_result=self.get_pred_result(self.number_list)
        interval_results=SEIR_exp_.get_confidence_interval(pred_result)
        number_mean=interval_results['number_range']['mean']
        number_min=interval_results['number_range']['min']
        number_max=interval_results['number_range']['max']
        incre_mean=interval_results['incre_range']['mean']
        incre_min=interval_results['incre_range']['min']
        incre_max=interval_results['incre_range']['max']
        parameters=interval_results['parameter_range']

        len_pred=len(number_mean)

        if self.enhance_decrease_ratio: ##是否有假设截止训练日期后加强管控
            ##加入一条线，为修改了decrease_ratio 至 0.08后的曲线数值，长度为【number_list:len_pred】
            min_para=parameters['min']
            R0=min_para['R0']
            TI=min_para['TI']
            TE=min_para['TE']
            R=min_para['R']
            decrease_ratio=min_para['decrease_ratio']
            final_R0=min_para['final_R0']
            E=min_para['E']
            I=min_para['I']
            enhance_decrease_ratio=self.enhance_decrease_ratio
            enhance_date=len(number_list)
            en_pred_cumulative,en_pred_incre,_E=SEIR_exp_.generate_pred(R0, TI, TE, decrease_ratio, final_R0, E, I, R, len_pred, decrease_ratio_enhance=enhance_decrease_ratio, enhance_date=enhance_date,printf=False)
            en_pred_cumulative_=en_pred_cumulative[enhance_date:]
            print('enhance_pred_cumula:',en_pred_cumulative)
            en_pred_incre_=en_pred_incre[enhance_date:]
        else:
            en_pred_cumulative_=[]
            en_pred_incre_=[]


        title_=self.country_eng
        incre_save_path='{}/{}_incre.png'.format(self.output_dir,self.country_eng)
        number_save_path='{}/{}_cumula.png'.format(self.output_dir,self.country_eng)


        plot_with_conf_inter(number_list,number_mean,number_min,number_max,enhance_pred_list=en_pred_cumulative_,numType='cumulative',\
            title=title_,save_path=number_save_path,start_date=self.start_date)     
        plot_with_conf_inter(incre_list,incre_mean,incre_min,incre_max,enhance_pred_list=en_pred_incre_,numType='increase',\
            title=title_,save_path=incre_save_path,start_date=self.start_date)
        
        all_dates=[]
        for date in range(len_pred):
            x=self.start_date+timedelta(date)
            all_dates.append(x.strftime('%m-%d'))

        with open('{}/{}_pred.csv'.format(self.output_dir,self.country_eng),'w',encoding='utf-8') as w:
            for i,number in enumerate(number_mean):
                if i<len_number:
                    real_num=number_list[i]
                    real_incre=incre_list[i]
                else:
                    real_num=0
                    real_incre=0
                if not self.enhance_decrease_ratio: ##没有enhance
                    if i==0:
                        write_Str='date,累计确诊,新增确诊,预测累计_min,预测新增_min,预测累计_mean,预测新增_mean,预测累计_max,预测新增_max\n'
                        w.write(write_Str)
                    write_str='{},{},{},{},{},{},{},{},{}\n'.format(all_dates[i],real_num,real_incre,number_min[i],incre_min[i],\
                        number_mean[i],incre_mean[i],number_max[i],incre_max[i])
                    w.write(write_str)
                else:
                    if i==0:
                        write_Str='date,累计确诊,新增确诊,预测累计_min,预测新增_min,预测累计_mean,预测新增_mean,预测累计_max,预测新增_max,加强管控_累计,加强管控_新增\n'
                        w.write(write_Str)
                    write_str='{},{},{},{},{},{},{},{},{},{},{}\n'.format(all_dates[i],real_num,real_incre,number_min[i],incre_min[i],\
                        number_mean[i],incre_mean[i],number_max[i],incre_max[i],en_pred_cumulative[i],en_pred_incre[i])
                    w.write(write_str)      
        with open('{}/{}_parameter.txt'.format(self.output_dir,self.country_eng),'w',encoding='utf-8') as w:
            w.write(str(parameters))


country_names={
    # '伊朗':'Iran',
    '意大利':'Italy',
    # '韩国':'Korea',
    # '英国':'Britain',
    '德国':'Germany',
    '西班牙':'Spain',
    '法国':'France',
    '美国':'US'
}

##运行前，修改paramete config, decrease_ratio 0.07
if __name__=='__main__':
    raw_file=os.path.join(current_dir,'data/0527data_cut.xls')
    end_date=datetime(2020,4,27)
    prepare_data_func_=prepare_data_func(raw_file,end_date)

    get_country_df=prepare_data_func_.get_country_df
    country_start_date=prepare_data_func_.country_start_date
    return_numbers=prepare_data_func_.return_numbers

    return_posterior_numbers=prepare_data_func_.return_posterior_numbers

    # country='意大利'
    # country_eng='Italy'

    # country='西班牙'
    # country_eng='Spain'

    # country='法国'
    # country_eng='France'

    country='美国'
    country_eng='US'

    output_dir=os.path.join(current_dir,'output')

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    plot_and_pred_=plot_and_pred(country,country_eng,output_dir,enhance_decrease_ratio=None,extend_day=29)
    plot_and_pred_.plot_and_write_v2()

    # for country,country_eng in country_names.items():
    #     plot_and_pred_=plot_and_pred(country,country_eng,output_dir,extend_day=30)
    #     plot_and_pred_.plot_and_write()




