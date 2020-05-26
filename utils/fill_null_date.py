#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2020/03/11 14:18:12
@作者    :jichaosun
'''
from datetime import datetime,timedelta
import pandas as pd 
##输入一个df,里面日期不连续，输出连续日期的df 

##输入两个date,num的tuples，输出改成后的tumples

def fill_blank_num(start_tuple,end_tuple):
    """
    start_tuple:(date,num)格式
    """
    start_num=start_tuple[1]
    end_num=end_tuple[1]
    start=start_tuple[0]
    end=end_tuple[0]
    diff=(end-start).days-1
    if diff==0:
        return [start_tuple,end_tuple]
    else:
        step=round((end_num-start_num)/(diff+1),1)
        fill_tuple=[]
        for i in range(diff):
            current_date=start+timedelta(i+1)
            current_num=start_num+(i+1)*step
            fill_tuple.append((current_date,current_num))
        final_tuple=fill_tuple+[end_tuple]
        return final_tuple

# start_tuple=(datetime(2020,2,24),11)
# end_tuple=(datetime(2020,2,27),15)
# fill_blank_num(start_tuple,end_tuple)


def fill_date_tuple(date_num_tuple_lst):
    """
    :输入一个[(date(2019,3,1),123),(date(2019,3,3),156),(date(2019,3,4),178)]
    :填充中间的空缺日期，输出结果
    """
    new_tuple_list=[]
    for i,cur_tuple in enumerate(date_num_tuple_lst):
        if i==0:
            new_tuple_list.append(cur_tuple)
        elif (cur_tuple[0]-date_num_tuple_lst[i-1][0]).days==1:
            new_tuple_list.append(cur_tuple)
        else:
            new_tuple=fill_blank_num(date_num_tuple_lst[i-1],cur_tuple)
            new_tuple_list+=new_tuple
    return new_tuple_list





def fill_date_df(df):
    britain_tuple=list(zip(df['date'].tolist(),df['累计确诊'].tolist()))
    new_britain_tuple=[]
    for i,cur_tuple in enumerate(britain_tuple):
        if i==0:
            new_britain_tuple.append(cur_tuple)
        elif (cur_tuple[0]-britain_tuple[i-1][0]).days==1:
            new_britain_tuple.append(cur_tuple)
        else:
            new_tuple=fill_blank_num(britain_tuple[i-1],cur_tuple)
            new_britain_tuple+=new_tuple

    new_date_list=[i[0] for i in new_britain_tuple]
    new_number_list=[i[1] for i in new_britain_tuple]
    new_df=pd.DataFrame({'date':new_date_list,'累计确诊':new_number_list})
    return new_df


if __name__=='__main__':
    test_date_number_tuple=[
        (datetime(2020, 3, 24, 0, 0),123),
        (datetime(2020, 3, 25, 0, 0),345),
        (datetime(2020, 3, 29, 0, 0),689)
    ]
    print(fill_date_tuple(test_date_number_tuple))