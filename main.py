import json
from dotenv import dotenv_values

from Monitor import Monitor


env_vars = dotenv_values('.env')

# 读取基金列表
with open('./funds.json', 'r') as f:

    fundsList = json.load(f)


url_Template = env_vars['url_Template']
headers = json.loads(env_vars['headers'])
rebalanceRate = float(env_vars['rebalanceRate'])


monitor = Monitor(headers= headers, url_Template= url_Template, fundsList= fundsList, rebalanceRate= rebalanceRate)

monitor.getFundData()
monitor.rebalance()



 