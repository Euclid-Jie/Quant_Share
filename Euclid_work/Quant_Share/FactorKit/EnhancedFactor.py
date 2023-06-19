
from .BarraCNE6 import BARRA
from datetime import date
from ..Utils import lazyproperty
import numpy as np

class EnhancingDividend(BARRA):

    '''
    增强红利因子的设计
    正如前文所述，考虑到股息率与市值、盈利性指标的高相关性。我们认为股息率选股的成功之处在于选择大市值中盈利稳健、收入较高的公司，
    因此我们对股息率施以更加严格的市值、盈利能力和分红约束：1）市值和交易活跃度；2）盈利能力和盈利持续性；3）分红能力和持续性。
    为了进一步发挥红利策略的优势，个股权重按照个股分红占全部成份股股票总分红的比例设计（Smart beta的处理方式）。其次，为了
    避免权重向某一些股息率较高或流通市值较高的股票过度倾斜，我们认为还必须对个股和行业的权重进行限制，让组合尽量分散，已达到
    降低组合风险的目的。最后，由于红利策略是一个适合中长期的价值投资策略，我们将调仓期由月频修改至半年调仓，降低因子换手率，避免较高的交易成本。
    通过以上三步增强，我们完成了增强红利因子的构建。我们在股息率因子的基础上引入一个代表其他成份股筛选条件的哑变量D_t，在调仓期t（每半年），
    当股票i满足如下条件时，D_t=1：
    (1)流通市值大于10亿元； negMarketValue
    (2)最近6个月日均成交额大于1,000万元；turnoverValue
    (3)最近两个调整期内至少有一期近三年年均EPS增长率为正；EPS
    (4)最近三年股息年均增长率不低于5%。 perCashDiv
    不满足上述条件时，D_t=0。
    因此，增强红利因子的计算方法为：增强红利因子=D_t×股息率。
    '''

    def __init__(self, beginDate: str = None, endDate: str = None):
        endDate = endDate if endDate else date.today().strftime("%Y%m%d")
        super().__init__(beginDate, endDate)

    @lazyproperty
    def bool_negMarketValue(self):
        df = self.negMarketValue
        df = df.apply(lambda x:x>1e10)
        return df

    @lazyproperty
    def bool_turnoverValue(self):
        df = self.turnoverValue
        df = self.pandas_parallelcal(df, myfunc=lambda x:np.nanmean(x) > 1e7, window=6*21)
        return df


    @lazyproperty
    def EnhancingDividend(self):
        DTOP = self.DTOP
        EPS = self.EPS
        perCashDiv = self.perCashDiv
        turnoverValue = self.turnoverValue
        pass





