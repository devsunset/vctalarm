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
    # vctinfo.VctInfo().vcRace(targetMarket=['KRW'])
    # vctinfo.VctInfo().vcData('KRW-TON')
    # vctinfo.VctInfo().vcChart('KRW-TON')
    vctinfo.VctInfo().vcAnalyze('20230221', targetMarket=['KRW'])

