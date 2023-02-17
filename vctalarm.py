# -*- coding: utf-8 -*-
##################################################
#
#          virtual coin  trade alarm
#
##################################################

##################################################
# import
from vctinfo import vctinfo

vctalarm = vctinfo.VctInfo()

#################################################
# main
if __name__ == '__main__':
    # moinitor markets info
    # vctalarm.monitorMarkets(loop=False, looptime=5, sort='signed_change_rate', targetMarket=['KRW'])

    # get candles chart data &  save to db
    # vctalarm.loadMarketsCandlesMwdData()

    vctalarm.vctAlarm(targetMarket=['KRW'])
