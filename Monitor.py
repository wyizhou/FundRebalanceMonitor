import requests
import json
import random
import time
from string import Template

class Monitor():
    def __init__(self, headers, url_Template, rebalanceRate, fundsList = []):

        # 获取获取数据的请求头和URL
        self.headers = headers
        self.url_Template = url_Template
    
        self.fundsList = fundsList
        self.totalCaptital = 0.0
        self.last_work_FSRQ = None
        self.rebalanceRate = rebalanceRate

        self.willSellFunds = []
        self.willPurchaseFunds = []
   


    def getFundData(self):



        for fund in self.fundsList:

            code = fund['code']

            url_Template = Template(self.url_Template)

            url = url_Template.substitute(code=code)
    
            response = requests.get(url, headers=self.headers)

            data = json.loads(response.text[response.text.find("(") + 1 : response.text.rfind(")")])["Data"]["LSJZList"]

            # 只获取上一个工作日的净值数据，因为当天的净值数据还没有出来
            last_work_data = data[0]

            # 存下来，用于检查所有基金是不是在当前日期有数据
            self.last_work_FSRQ = last_work_data['FSRQ']


            last_work_DWJZ = float(last_work_data['DWJZ'])

            fund['DWJZ'] = last_work_DWJZ
            fund['FSRQ'] = last_work_data['FSRQ']

            
            # 计算出给定的资金有多少份额
            initCaptital = fund['initCaptital']
            fund['initShare'] = round(initCaptital / last_work_DWJZ, 2)



            # 计算出总体资金用于后面的平衡
            self.totalCaptital += initCaptital

            # 随机休眠0-9秒
            sleep_time = random.uniform(0,5)   #随机一个大于0小于9的小数
            time.sleep(sleep_time)

    def rebalance(self):

        totalSelledCaptital = 0.0
        totalPurchaseCaptital = 0.0

        for fund in self.fundsList:

            currentRate = fund['initCaptital'] / self.totalCaptital
            
            adjustRate = currentRate - fund['rate']

            adjustCaptital = adjustRate * self.totalCaptital

            fund['currentRate'] = round(currentRate, 2)

            fund['adjustRate'] = round(adjustRate, 2)

            fund['adjustCaptital'] = round(adjustCaptital, 2)

            fund['adjustShare'] = round(fund['adjustCaptital'] / fund['DWJZ'], 2)

            fund['adjustScheme'] = []

            if adjustRate >= self.rebalanceRate:

                self.willSellFunds.append(fund)

                # 统计需要卖出的资金
                totalSelledCaptital += fund['adjustCaptital']

            if adjustRate < 0:
                self.willPurchaseFunds.append(fund)

                # 统计需要买入的资金
                totalPurchaseCaptital += fund['adjustCaptital']


        # 需要买入的基金排序，又小到大
        
        self.willSellFunds = sorted(self.willSellFunds, key=lambda fund: fund['adjustCaptital'], reverse=True)
        self.willPurchaseFunds = sorted(self.willPurchaseFunds, key=lambda fund: fund['adjustCaptital'], reverse=False)
        

        
        print('""""""""""""""""""""当前日期：{}""""""""""'.format(self.last_work_FSRQ))

        print('需要卖出资金：{}, 需要买入资金：{}'.format(totalSelledCaptital, totalPurchaseCaptital))

        print('""""""""""""""""""""需要平衡的基金开始打印""""""""""""""""""""')
        for fund in self.willSellFunds:
            
            print('''
                基金当前日期: {}, 基金名称: {}, 基金代码: {}, 基金比例: {}, 基金现有资金: {}, 基金现有份额: {}
                基金净值: {}, 当前资金占比: {}, 需要调整的比例: {}, 需要调整的资金: {}, 需要调整的份额: {}
            '''.format(
                fund['FSRQ'],
                fund['name'],
                fund['code'],
                fund['rate'],
                fund['initCaptital'],
                fund['initShare'],
                fund['DWJZ'],
                fund['currentRate'],
                fund['adjustRate'],
                fund['adjustCaptital'],
                fund['adjustShare']
            ))

        print('""""""""""""""""""""需要平衡的基金结束打印""""""""""""""""""""')


        print('""""""""""""""""""""需要买入的基金开始打印""""""""""""""""""""')

        # 复制一份指针数据，用于存放待平衡列表
        willSellFunds = self.willSellFunds

        for fund in self.willPurchaseFunds:

            willPurchaseCaptital = fund['adjustCaptital'] 

            for index, sellFund in enumerate(willSellFunds):

                # 因为sellFund['adjustCaptital']是需要卖掉的基金，所以一定是正数，而fund['adjustCaptital'] 是需要买入的基金，一定是负数
                # 所以这里采用的是相加
                willPurchaseCaptital = sellFund['adjustCaptital'] + willPurchaseCaptital


                # 结果1:相加后，值为-10到10之间，说明两个基金需要平衡的资金相差不大，所以算作平衡完成
                if willPurchaseCaptital <= 10 and willPurchaseCaptital >= -10:
                    
                    fund['adjustScheme'].append('需要卖掉的基金：{}, 需要卖掉的基金代码: {}，需要卖掉的资金: {}，需要卖掉的份额: {}'.format(
                        sellFund['name'], 
                        sellFund['code'],
                        round(sellFund['adjustCaptital'] , 2),
                        round(sellFund['adjustCaptital'] / sellFund['DWJZ'], 2)
                    ))

                    sellFund['adjustCaptital'] = 0
                    sellFund['adjustShare'] = 0

                    # 因为当前需要平衡的基金中所有资金经平衡给当前需要买入的基金，所以从再平衡列表中弹出。
                    willSellFunds.pop(index)

                    # 如果买了后，被平衡基金还剩余资金说明当前循环中的基金需要买入的资金已完成，则跳过本次需要购买的基金循环
                    break 

                # 结果2: 相加后，值大于10，说明再平衡的基金资金超过待买入基金的资金量，则需要对再平衡基金的资金做记录，资金需要删除再平衡资金量
                elif willPurchaseCaptital > 10:

                    fund['adjustScheme'].append('需要卖掉的基金：{}, 需要卖掉的基金代码: {}，需要卖掉的资金: {}，需要卖掉的份额: {}'.format(
                        sellFund['name'], 
                        sellFund['code'],
                        round(sellFund['adjustCaptital'] - willPurchaseCaptital, 2),
                        round((sellFund['adjustCaptital'] - willPurchaseCaptital ) / sellFund['DWJZ'], 2)
                    ))

                    sellFund['adjustCaptital'] = willPurchaseCaptital
                    sellFund['adjustShare'] = willPurchaseCaptital / sellFund['DWJZ']

                    # 当前需要买入的资金已经完成，所以跳过其他再平衡基金
                    break 
                    
                # 结果3: 相加后，值小于-10，说明再平衡的基金资金少于待买入基金的资金量，则需要买入基金做记录，还剩余多少资金需要在下次买入。
                elif willPurchaseCaptital < -10:

                    fund['adjustScheme'].append('需要卖掉的基金：{}, 需要卖掉的基金代码: {}，需要卖掉的资金: {}，需要卖掉的份额: {}'.format(
                        sellFund['name'], 
                        sellFund['code'],
                        round(sellFund['adjustCaptital'], 2),
                        round(sellFund['adjustCaptital'] / sellFund['DWJZ'], 2)
                    ))

                    sellFund['adjustCaptital'] = 0 
                    sellFund['adjustShare'] = 0 

                    # 因为当前需要平衡的基金中所有资金经平衡给当前需要买入的基金，所以从再平衡列表中弹出。
                    willSellFunds.pop(index)



            
            print('''
                基金当前日期: {}, 基金名称: {}, 基金代码: {}, 基金比例: {}, 基金现有资金: {}, 基金现有份额: {}
                基金净值: {}, 当前资金占比: {}, 需要调整的比例: {}, 需要调整的资金: {}, 需要调整的份额: {}
                平衡方案: {}
            '''.format(
                fund['FSRQ'],
                fund['name'],
                fund['code'],
                fund['rate'],
                fund['initCaptital'],
                fund['initShare'],
                fund['DWJZ'],
                fund['currentRate'],
                fund['adjustRate'],
                fund['adjustCaptital'],
                fund['adjustShare'],
                fund['adjustScheme']
            ))

        print('""""""""""""""""""""需要买入的基金结束打印""""""""""""""""""""')

        # print(self.fundsList)
