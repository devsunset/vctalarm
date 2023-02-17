# -*- coding: utf-8 -*-
##################################################
#
#          virtual coin  trade alarm
#
##################################################

##################################################
# import
from vcinfo import vctinfo

##################################################
# vctinfo VctAlarm
vctalarm = vctinfo.VctAlarm()

#################################################
# main
if __name__ == '__main__':
    # moinitor markets info
    # vctalarm.monitorMarkets(loop=False, looptime=5, sort='signed_change_rate', targetMarket=['KRW'])

    # get candles chart data &  save to db
    # vctalarm.loadMarketsCandlesMwdData()

    # scheduler = BlockingScheduler()
    # scheduler.add_job(daemon_process, 'interval', seconds=config.INTERVAL_SECONDS)
    # try:
    #    scheduler.start()
    # except Exception as err:
    #    logger.error(' main Exception : %s' % e) 

    vctalarm.vcTradeInfoAlarm(targetMarket=['KRW'])
