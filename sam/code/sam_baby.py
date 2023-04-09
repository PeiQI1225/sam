# 显示设置
import pandas as pd

import pyecharts.charts as pyc
import pyecharts.options as opts
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的乱码问题
# 设置value的显示长度为200，默认为50
pd.set_option('max_colwidth', 200)
# 显示所有列，把行显示设置成最大
pd.set_option('display.max_columns', None)
# 显示所有行，把列显示设置成最大
pd.set_option('display.max_rows', None)

baby = pd.read_csv('D:\study\data\sam\sam_tianchi_mum_baby.csv')
trade = pd.read_csv('D:\study\data\sam\sam_tianchi_mum_baby_trade_history.csv')

# print(baby.head())
# print(trade.head())
# print(baby.info())
# print(trade.info())
# print(trade.buy_mount.describe())

quantity = trade.buy_mount.value_counts().sort_index()
sns.scatterplot(x = quantity.index, y = quantity.values, alpha = 0.3)
plt.title("单个订单购买量分布")
plt.ylabel("订单数")
plt.xlabel("购买量")
# plt.show()
# 保留buy_mount[0, 1000]以内的记录
trade = trade[(trade.buy_mount >= 1) & (trade.buy_mount <= 1000)]
# 列重命名
trade.rename({'auction_id': 'item_id'}, axis = 1, inplace = True)
# 先将property暂且取出
property = trade.property
trade.drop('property', axis = 1, inplace = True)
# 日期类型转换
baby['birthday'] = pd.to_datetime(baby.birthday.astype('str'))
trade['day'] = pd.to_datetime(trade.day.astype('str'))

# print(baby.head())
# print(trade.head())

# print(baby['gender'].value_counts())

baby = baby.loc[~(baby['gender'] == 2)]
# print(baby['gender'].value_counts())

trade = pd.merge(trade, baby, on = 'user_id', how = 'outer')
# print(trade.head())
# 根据年月查看销量趋势
# 根据年分组
year_item = trade[['item_id', 'buy_mount', 'day']].groupby(by = trade.day.dt.year)['buy_mount'].sum()
# 各年季度销量情况
year_quarter_item = trade[['item_id', 'buy_mount', 'day']].groupby(by = [trade.day.dt.year, trade.day.dt.quarter])[
    'buy_mount'].sum()
# 根据年月分组
year_month_item = trade[['item_id', 'buy_mount', 'day']].groupby(by = [trade.day.dt.year, trade.day.dt.month])[
    'buy_mount'].sum()

# 作图的字体默认设置
fontdict = {'fontsize': 15, 'horizontalalignment': 'center'}
# 各年销量情况
plt.figure(figsize = (10, 5))
sns.barplot(x = year_item.index, y = year_item.values)
plt.title("年销量趋势", fontdict = fontdict)
plt.xlabel("年份", fontdict = fontdict)
plt.ylabel("销量", fontdict = fontdict)
# plt.show()
# 各季度销售情况
plt.figure(figsize = (10, 5))
sns.barplot(x = year_quarter_item.index.values, y = year_quarter_item.values)
plt.title("季度销量趋势", fontdict = fontdict)
plt.xlabel("(年,季度)", fontdict = fontdict)
plt.ylabel("销量", fontdict = fontdict)
# plt.show()
# 各月份销量情况
x = [str(x[0]) + "/" + str(x[1]) for x in year_month_item.index.values]
y = [int(x) for x in year_month_item.values]
pyc.Bar().add_xaxis(xaxis_data = x).add_yaxis(series_name = "销量", y_axis = y, markpoint_opts = opts.MarkPointOpts(
    data = [opts.MarkPointItem(coord = [x[4], y[4]], value = y[4]),
            opts.MarkPointItem(coord = [x[10], y[10]], value = y[10]),
            opts.MarkPointItem(coord = [x[16], y[16]], value = y[16]),
            opts.MarkPointItem(coord = [x[22], y[22]], value = y[22]),
            opts.MarkPointItem(coord = [x[28], y[28]], value = y[28])]
)).set_series_opts(label_opts = opts.LabelOpts(is_show = False)).set_global_opts(
    title_opts = opts.TitleOpts(title = "月销量趋势", subtitle = "2012/7-2015/2的销量趋势图"),
    toolbox_opts = opts.ToolboxOpts()).render('month.html')
trade['month'] = trade['day'].astype('datetime64[M]')
trade['day_num'] = trade['day'].dt.day
# 5月
# 2012年没有5月的数据
sales13_05_series = trade.query('month == "2013-05-01"')
sales14_05_series = trade.query('month == "2014-05-01"')
sales13_05_sum_series = sales13_05_series.groupby(by = 'day_num')['buy_mount'].sum()
sales14_05_sum_series = sales14_05_series.groupby(by = 'day_num')['buy_mount'].sum()
plt.plot(sales13_05_sum_series, label = '2013-05')
plt.plot(sales14_05_sum_series, label = '2014-05')
plt.legend()
plt.xlabel('Day')
plt.ylabel('Sales')
plt.title('Sales per day')
# plt.show()
# 11月
sales12_11_series = trade.query('month == "2012-11-01"')
sales13_11_series = trade.query('month == "2013-11-01"')
sales14_11_series = trade.query('month == "2014-11-01"')
sales12_11_sum_series = sales12_11_series.groupby(by = 'day_num')['buy_mount'].sum()
sales13_11_sum_series = sales13_11_series.groupby(by = 'day_num')['buy_mount'].sum()
sales14_11_sum_series = sales14_11_series.groupby(by = 'day_num')['buy_mount'].sum()
plt.plot(sales12_11_sum_series, label = '2012-11')
plt.plot(sales13_11_sum_series, label = '2013-11')
plt.plot(sales14_11_sum_series, label = '2014-11')
plt.legend()
plt.xlabel('Day')
plt.ylabel('Sales')
plt.title('Sales per day')
# plt.show()
# 产品大类复购率
# 根据产品大类分组，然后循环大类进行索引求出每个大类的复购率
t = trade.groupby(by = ['cat1', 'user_id']).size()
purchase_dict = {}
for i in trade.cat1.unique():
    c = t.loc[i].value_counts()
    purchase_dict[i] = ((c.sum() - c[:1]) / c[:1]).values[0].round(4)
plt.figure(figsize = (10, 6))
sns.barplot(x = list(purchase_dict.keys()), y = list(purchase_dict.values()))
plt.title("各大类复购率", fontdict = fontdict)
# plt.show()
# 商品大类销售情况
cat = trade.groupby("cat1")['buy_mount'].sum()
sns.barplot(x = cat.index, y = cat.values)
plt.title("商品大类销售情况")
plt.xlabel("商品大类")
# plt.show()
# 人均大类购买情况
cat_aver_user = (trade.groupby("cat1")['buy_mount'].sum() / trade.groupby("cat1")['user_id'].count()).sort_values(
    ascending = False)
sns.barplot(x = cat_aver_user.index, y = cat_aver_user.values)
plt.title("商品大类人均购买情况")
plt.xlabel("商品大类")
# plt.show()
# 大类下子类别数量
cat_count = trade.groupby("cat1")['cat_id'].count()
sns.barplot(x = cat_count.index, y = cat_count.values)
plt.title("商品大类的子类数量")
plt.xlabel("商品大类"),
# plt.show()
