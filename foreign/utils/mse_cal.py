##计算mean square error
def mse_cal(list1,list2):
    len_list=len(list1)
    zip_list=zip(list1,list2)
    square_list=[(i[0]-i[1])**2 for i in zip_list]
    sum_1=sum(square_list)
    mse=(sum_1/len_list)**0.5
    return round(mse,1)
    # for i,j in zip(list1,list2):
    #     sum=sum+(i-j)**2
    # mse=(sum/len_list)**0.5
    # return mse

def mae_cal(list1,list2):
    len_list=len(list1)
    zip_list=zip(list1,list2)
    abs_diff_list=[abs(i[0]-i[1]) for i in zip_list]
    sum_1=sum(abs_diff_list)
    mae=(sum_1/len_list)
    return round(mae,1)


##计算mean square error percent
def mse_cal_percent(list1,list2):
    """
    list2为真实值
    """
    sum_1=0
    len_list=len(list1)
    for i,j in zip(list1,list2):
        sum_1=sum_1+((i-j)/j)**2
    mse=(sum_1/len_list)**0.5
    return mse


if __name__=='__main__':
    list1=[1,2,3]
    list2=[4,5,6]
    print(mse_cal(list1,list2))