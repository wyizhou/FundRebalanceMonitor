# FundRebalanceMonitor
通过设定指定的再平衡阈值、基金数据，自动从天天基金网获取最后一个工作日的单位净值，计算列表中的基金是否需要再平衡，并给出具体卖出金额、份额。

基金再平衡计算本身依赖于最后一个工作日的净值，但再平衡后，基金买入是看交易日的净值，所以有偏差属于正常情况，但这类偏差不会影响太大。

关于手续费，本来设定有，但后面做个另外一个回测后，发现手续费对于再平衡影响非常小。

如果在下午3点后进行再平衡，建议先检查每个基金的净值日期，如果有存在不同的日期建议等到当天所有基金公布净值后再进行再平衡，当然如果有些基金的影响不大，比如国债、准国债等。



### 使用说明

1. 安装依赖`pip install -r requirements.txt`
2. 将`env`文件更名为`.env`，并修改里面的`rebalanceRate`再平衡阈值和`headers`天天基金网请求头。
3. 修改`funds.json`里面的基金数据，不同的字段含义为如下：

```json
{
  "code": "002656",  # 基金编码，以字符串形式存放
  "name": "南方创业板ETF联接A",  # 基金名称，可以简写，对计算无影响
  "rate": 0.03, # 组合策略中该基金的资金配比
  "initCaptital": 324.65 # 该基金现有资金量
}
```

4. `python main.py`





### 输出结果

输出结果中包含了再平衡方案，计算出需要的卖掉的基金和份额，但有一定的误差，大概在10元左右。

