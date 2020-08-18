## calculate 25*7 data
from datetime import datetime,timedelta

start_date=datetime(2020,1,20)
all_dates=[]
for date in range(25*7):
    x=start_date+timedelta(date)
    all_dates.append(x.strftime('%m-%d'))

print(x)
## 2020-7-12