# -*- coding: utf-8 -*-
##################################################
#
#          virtual coin  trade alarm
#
##################################################

##################################################
# import
from vctinfo import vctinfo

#################################################
# main
if __name__ == '__main__':
    # vctinfo.VctInfo().vcRace(targetMarket=['KRW'])
    print(vctinfo.VctInfo().getCandlesMinutes(1,'KRW-ZRX','2023-02-20T09:00:00',200))