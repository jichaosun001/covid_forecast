#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2020/02/18 07:09:59
@作者    :jichaosun
'''

###短期预测，采用过去几天的数字预测下5天

import numpy as np
import pandas as pd
def exponential_decay(t, init,m,finish):
    alpha = np.log(init / finish) / m
    l = - np.log(init) / alpha
    decay = np.exp(-alpha * (t + l))
    return decay

def pred_nex_elements(in_list,step_add=0,number_predict=5):
    """
    输入为三个元素的列表，输出为接下来5个数值
    step_add默认为0，越大表示速率变化越慢
    number_predict，表示，预测接下来几个数字
    """
    in_list=in_list[-3:]
    init=in_list[0]
    finish=in_list[-1]
    step=2+step_add
    pred_value_1=[]
    for i in range(step+1,step+1+number_predict):
        pred=exponential_decay(i,init,step,finish)
        pred_value_1.append(pred)


    init=in_list[1]
    finish=in_list[-1]
    step=1+step_add
    pred_value_2=[]
    for i in range(step+1,step+1+number_predict):
        pred=exponential_decay(i,init,step,finish)
        pred_value_2.append(pred)

    pred_avg=[(pred_value_1[i]+pred_value_2[i])/2 for i in range(number_predict)]
    pred_round=[round(i) for i in pred_avg]
    pred_round=[0 if pd.isnull(x) else x for x in pred_round]
    return pred_round


if __name__=='__main__':
    test_list=[8,9,12]
    print('step=0',pred_nex_elements(test_list))
    print('step=1',pred_nex_elements(test_list,step_add=1))