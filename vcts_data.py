# -*- coding: utf-8 -*-
##################################################
#
#          virtual coin  trade system data
#
##################################################

##################################################
# import
from vctinfo import vctinfo

#################################################
# main
if __name__ == '__main__':
    vctinfo.VctInfo().vcMonitoring(targetMarket=['KRW'])
    vctinfo.VctInfo().vcUpbitApiCall('KRW-BTC')
    vctinfo.VctInfo().vcChart('KRW-BTC')
    vctinfo.VctInfo().vcData('20230221', targetMarket=['KRW'])

