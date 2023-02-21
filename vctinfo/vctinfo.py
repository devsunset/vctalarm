# -*- coding: utf-8 -*-
##################################################
#
#         vctinfo.py
#
##################################################

##################################################
# import

import logging
import logging.config
import sqlite3
import os
from os import path,makedirs

import pandas as pd
from tabulate import tabulate
import time
from datetime import datetime
import matplotlib.pyplot as plt

from common import common
from common import config
from upbitapi import upbitapi

##################################################
# constant

# target db
TARGET_DB = config.TARGET_DB

# logging config
log_file_path = path.join(path.abspath(path.dirname(path.abspath(path.dirname(__file__)))), 'common/logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
logger = logging.getLogger('vctalarm')

comm = common.Common()
upbitapi = upbitapi.UpbitApi(config.ACCESS_KEY, config.SECRET)

MARKETS  = {}

##################################################
# biz function

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 250)

class VctInfo():
    def __init__(self):
        self.loadMarketSaveToDb()

    ##########################################################
    def createFolder(self,directory):
        try:
            if not path.exists(directory):
                makedirs(directory)
        except OSError:
            print ('Error: Creating directory. ' +  directory)

    # load market info save to db (vc_meta table).
    def loadMarketSaveToDb(self):
        self.createFolder(os.getcwd()+"/db")

        logger.info('loadMarketSaveToDb start')
        data_json = upbitapi.getQuotationMarketAll()
        try:
            conn = sqlite3.connect(TARGET_DB)
            try:
                sqlText = 'drop table vc_meta'
                comm.executeTxDB(conn, sqlText)
            except Exception as e:
                logging.error(' Exception : %s' % e)

            sqlText = 'create table vc_meta (id integer primary key autoincrement, market text , korean_name text, english_name text, market_warning text)'
            comm.executeTxDB(conn, sqlText)

            sqlText = 'insert into vc_meta  (market,korean_name,english_name,market_warning)'
            sqlText += ' values (?, ?, ?, ?)'

            sqlParam = []
            for data in data_json:       
                data.setdefault('market_warning', '')         
                sqlParam.append((data.get('market'),data.get('korean_name'),data.get('english_name'),data.get('market_warning')))
                MARKETS[data['market']] = data['korean_name']

            comm.executeTxDB(conn, sqlText, sqlParam)
            conn.commit()
            logger.info('loadMarketSaveToDb end')
        except Exception as e:
            logging.error(' Exception : %s' % e)
        finally:
            if conn is not None:
                conn.close()

    # get market name  info
    def getMarketName(self,market):        
        return MARKETS[market]

    # get markets info
    def getMarkets(self):        
        markets = comm.searchDB("select market,korean_name,english_name,market_warning,substr(market,0,instr(market,'-')) as market_type from vc_meta")
        return markets

    # getVcInfoData
    def getVcInfoData(self, selectVirtualConins, sort='market'):
        selectMarkets = []
        markets = selectVirtualConins
        for i in markets.index:
                selectMarkets.append(markets['market'][i])

        ###########################################################################################
        # get ticker market data
        df = pd.DataFrame(upbitapi.getQuotationTicker(selectMarkets)).sort_values(by=sort, ascending=False)

        # merge market info & ticker market data
        df = pd.merge(df, markets, on='market')

        # ------------------------------------------------------------------------
        # unused filed delete
        # ticker market data
        # del df['market']                      # 종목 구분 코드
        # del df['trade_date']                  # 최근 거래 일자(UTC)
        # del df['trade_time']                  # 최근 거래 시각(UTC)
        # del df['trade_date_kst']              # 최근 거래 일자(KST)
        # del df['trade_time_kst']              # 최근 거래 시각(KST)
        # del df['trade_timestamp']             # 최근 거래  타임스탬프
        # del df['opening_price'] 	            # 시가
        # del df['high_price'] 	                # 고가
        # del df['low_price'] 	                # 저가
        # del df['trade_price'] 	            # 종가
        # del df['prev_closing_price'] 	        # 전일 종가
        # del df['change'] 	                    # EVEN : 보합 RISE : 상승 FALL : 하락
        # del df['change_price']                # 변화액의 절대값
        # del df['change_rate']                 # 변화율의 절대값
        # del df['signed_change_price'] 	    # 부호가 있는 변화액
        # del df['signed_change_rate'] 	        # 부호가 있는 변화율
        # del df['trade_volume'] 	            # 가장 최근 거래량
        # del df['acc_trade_price']             # 누적 거래대금(UTC 0시 기준)
        # del df['acc_trade_price_14h'] 	    # 24시간 누적 거래대금
        # del df['acc_trade_volume']            # 누적 거래량(UTC 0시 기준)
        # del df['acc_trade_volume_14h'] 	    # 24시간 누적 거래량
        # del df['highest_52_week_price']       # 52주 신고가
        # del df['highest_52_week_date']        # 52주 신고가 달성일
        # del df['lowest_52_week_price']        # 52주 신저가
        # del df['lowest_52_week_date']         # 52주 신저가 달성일
        # del df['timestamp']                   # 타임스탬프
        # market info
        # del df['korean_name']
        # del df['english_name']
        # del df['market_warning']
        # del df['market_type']
        # ------------------------------------------------------------------------

        # # uncomment - data console print
        # # column align
        # columns = df.columns.tolist()
        # colalignList = []
        # for colname in columns:
        #     if 'change' == colname or 'market_type' == colname or 'market_warning' == colname or colname.find(
        #             '_date') > -1 or colname.find('_time') > -1 or colname.find('_timestamp') > -1:
        #         colalignList.append("center")
        #     elif 'korean_name' == colname or 'english_name' == colname:
        #         colalignList.append("left")
        #     else:
        #         colalignList.append("right")

        # #  tabulate Below are all the styles that you can use :
        # # “plain” “simple” “github” “grid” “fancy_grid” “pipe” “orgtbl” “jira” “presto” “pretty” “psql” “rst” “mediawiki” “moinmoin” “youtrack” “html” “latex” “latex_raw” “latex_booktabs”  “textile”
        # print(tabulate(df, headers='keys', tablefmt='psql', showindex=False, colalign=colalignList))

        return df

    def vcData(self, vc):
        count = 200
        # QUOTATION API
        ###############################################################
        # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 분(Minute) 캔들 
        df = pd.DataFrame(upbitapi.getQuotationCandlesMinutes(1,vc, None, count))

        # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 일(Day) 캔들 
        # df = pd.DataFrame((upbitapi.getQuotationCandlesDays(vc,None,count,'KRW')))

        # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 주(Week) 캔들
        # df = pd.DataFrame(upbitapi.getQuotationCandlesWeeks(vc,None,count))

        # print('■■■■■■■■■■ - QUOTATION API - 시세 캔들 조회 - 월(Month) 캔들
        # df = pd.DataFrame(upbitapi.getQuotationCandlesMonths(vc,None,count))

        # print('■■■■■■■■■■ - QUOTATION API - 시세 체결 조회 - 최근 체결 내역
        # df = pd.DataFrame(upbitapi.getQuotationTradesTicks(vc,None,count))

        # print('■■■■■■■■■■ - QUOTATION API - 시세 Ticker 조회 - 현재가 정보
        # df = pd.DataFrame(upbitapi.getQuotationTicker([vc]))

        # print('■■■■■■■■■■ - QUOTATION API - 시세 호가 정보(Orderbook) 조회 - 호가 정보 조회
        # df = pd.DataFrame(upbitapi.getQuotationOrderbook([vc]))

        print(tabulate(df, headers='keys', tablefmt='psql'))

    def vcChart(self, vc):
        df = comm.searchDB("select * from vc_race_data where market='KRW-TON' and save_time < 2023022109000000")
        # print(tabulate(df, headers='keys', tablefmt='psql'))
        df.plot(kind='bar',x='save_time',y='trade_volume')
        # plt.show()
        plt.savefig("test.png")

    ##########################################################

    def vcRace(self, targetMarket=['KRW', 'BTC', 'USDT']):
        while True:
            now_time = (datetime.now().strftime('%H%M%S'))

            race_status = 0
            if int(now_time) >= int(config.VC_RACE_CHECK_TIME_START) and int(now_time) <= int(config.VC_RACE_CHECK_TIME_END):
                logger.info("Race ...")

                if race_status == 0:
                    # 1. 대상 마켓 코인 정보 조회
                    targetMakert_condition = ','.join("'" + item + "'" for item in targetMarket)
                    selectVirtualConins = self.getMarkets().query("market_type in ("+targetMakert_condition+")")

                # 2. 코인 상세 조회
                vc_race_info = self.getVcInfoData(selectVirtualConins=selectVirtualConins, sort='market')

                # 3. 코인 정보 저장
                # date_s = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                date_s = (datetime.now().strftime('%Y%m%d%H%M%S'))
                vc_race_info["save_time"] = date_s

                comm.dataframeSaveToSqlite(df=vc_race_info, tablename='vc_race_data')

                race_status = race_status+1
            else:
                if race_status > 0:
                    race_status = 0
                    self.vcRaceSummary(selectVirtualConins)

            time.sleep(config.VC_RACE_LOOPTIME)

    def vcRaceSummary(selectVirtualConins):
        logger.info("vcRaceSummary ...")






