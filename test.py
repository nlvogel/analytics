import datetime
# import datetime as dt

# date = dt.datetime.now()
# print(date.strftime('%Y-%m-%d'))

# date_to_number = date.toordinal()
# print(date_to_number)

# jan_1 = dt.datetime.toordinal(dt.datetime(year=2022, month=1, day=1))
# print(jan_1)

# for days in range(0,50):
#     new_date = dt.datetime.fromordinal(738156 + days).strftime('%Y-%m-%d')
#     print(new_date)


# data_list = []
# with open('analytics_test.csv') as f:
#     data = f.readlines()
#     for _ in data:
#         data_list.append(_.strip('\n').split(','))
#         print(_.strip('\n'))
#
# print(data_list)

yesterday = datetime.datetime.now().toordinal()
date = datetime.datetime(year=2022, month=1, day=1)
start_date = date.toordinal()
range_ = yesterday - start_date

for _ in range(0, range_):
    print(datetime.datetime.fromordinal(start_date + _).strftime('%Y-%m-%d'))


