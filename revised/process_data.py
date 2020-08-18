#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2020/08/16 21:08:52
@作者    :jichaosun
'''

##对于中国，读取原始文件，添加数据，写回文件到本目录下

import os
from datetime import datetime,timedelta
current_dir=os.path.abspath(os.path.dirname(__file__))
root_dir=os.path.join(current_dir,'../')
os.sys.path.append(root_dir)
import json
root_data_dir=os.path.join(root_dir,'data')
current_data_dir=os.path.join(current_dir,'data')

def get_extra_data(region_file='china.txt'):
    with open(os.path.join(current_data_dir,region_file),encoding='utf-8') as f:
        all_lines=f.readlines()
        extra_numbers=[int(i.strip('\n')) for i in all_lines]
        print(extra_numbers)
        return extra_numbers

def get_all_data():
    file_name='china_cumulative_data.json'
    with open(os.path.join(root_data_dir,file_name),'r') as f:
        all_str=f.read()
    all_dict=json.loads(all_str)
    return all_dict



def get_single_district(all_dict,district):
    """
    得到某个地区的number_list和start_date
    """
    sing_dict=all_dict[district]
    sing_list=[]
    for k,v in sing_dict.items():
        sing_list.append((datetime.strptime(k,'%Y/%m/%d'),v))
    sing_list.sort(key=lambda x:x[0])
    start_date=sing_list[0][0]
    number_list=[i[1] for i in sing_list]
    return start_date,number_list


def add_numbers_date():
    ##
    all_dict=get_all_data()
    start_date=datetime(2020,3,11)
    extra_numbers=get_extra_data()
    len_extra=len(extra_numbers)
    all_dates=[]
    for no in range(len_extra):
        date=start_date+timedelta(no)
        all_dates.append(date.strftime('%Y/%m/%d'))
    
    for date,number in zip(all_dates,extra_numbers):
        all_dict['china_except_hubei'][date]=number
    return all_dict

if __name__=='__main__':
    new_dict=add_numbers_date()
    new_dict_str=json.dumps(new_dict,ensure_ascii=False,indent=5)
    with open(os.path.join(current_data_dir,'china_cumulative_data.json'),'w', encoding='utf-8') as w:
        w.write(new_dict_str)

##对于武汉和湖北，直接在每日数据添加

def get_adjust_data(region):
    extra_numbers=get_extra_data(region_file='{}.txt'.format(region))
    adjust_file=os.path.join(root_dir,'output/{}/adjust_number.json'.format(region))
    with open(adjust_file,encoding='utf-8') as f:
        data_str=f.read()
        data_dict=json.loads(data_str)
    return extra_numbers,data_dict

def add_numbers_4_dict(data_dict,extra_numbers,region):
    ##对每天结果添加数据，累计数据与新增数据,并写出到json
    for _,v in data_dict.items():
        number_list=v['number_list']
        incre_list=v['incre_list']
        last_number=number_list[-1]
        new_incre_list=[]
        for n,extra_number in enumerate(extra_numbers):
            if n==0:
                incre=extra_number-last_number
            else:
                incre=extra_number-extra_numbers[n-1]
            new_incre_list.append(incre)
        number_list=number_list+extra_numbers
        incre_list=incre_list+new_incre_list
        data_dict[_]['number_list']=number_list
        data_dict[_]['incre_list']=incre_list
    with open(os.path.join(current_data_dir,'{}_adjust_numbers.json'.format(region)),'w',encoding='utf-8') as w:
        data_Str=json.dumps(data_dict,ensure_ascii=False,indent=6)
        w.write(data_Str)
    return data_dict

if __name__=='__main__':
    region='wuhan'
    extra_numbers, data_dict=get_adjust_data(region)
    add_numbers_4_dict(data_dict,extra_numbers,region)




        



