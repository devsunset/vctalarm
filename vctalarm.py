# -*- coding: utf-8 -*-
##################################################
#
#          virtual coin vcinfo system
#
##################################################

##################################################
# import

import logging.config
from os import path

from vcinfo import vctinfo

##################################################
# constant

# logging config
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'common/logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vctalarm')

# vctalarm_trade,VctAlarmTrade
vctalarmtrade = vctinfo.VctAlarmTrade()

##################################################
# biz function

#################################################
# main
if __name__ == '__main__':
    # moinitor markets info
    # vctalarmtrade.monitorMarkets(loop=False, looptime=5, sort='signed_change_rate', targetMarket=['KRW'])

    # get candles chart data &  save to db
    # vctalarmtrade.loadMarketsCandlesMwdData()

    # scheduler = BlockingScheduler()
    # scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    # try:
    #    scheduler.start()
    # except Exception as err:
    #    logger.error(' main Exception : %s' % e) 

    # automatic vcinfo one
    vctalarmtrade.vcTradeInfoAlarm(targetMarket=['KRW'])
