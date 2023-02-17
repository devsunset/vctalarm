# -*- coding: utf-8 -*-
##################################################
#
#         vctinfo.py
#
##################################################

##################################################
# import

import datetime
import logging
import logging.config
import sqlite3
import time
from os import path

import pandas as pd
from tabulate import tabulate

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

##################################################
# biz function

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 250)

class VctInfo():
    def __init__(self):
        self.loadMarketSaveToDb()

    ##########################################################

    # load market info save to db (vctalarm_meta table).
    def loadMarketSaveToDb(self):
        logger.info('loadMarketSaveToDb start')
        data_json = upbitapi.getQuotationMarketAll()
        try:
            conn = sqlite3.connect(TARGET_DB)
            try:
                sqlText = 'drop table vctalarm_meta'
                comm.executeTxDB(conn, sqlText)
            except Exception as e:
                logging.error(' Exception : %s' % e)

            sqlText = 'create table vctalarm_meta (id integer primary key autoincrement, market text , korean_name text, english_name text, market_warning text)'
            comm.executeTxDB(conn, sqlText)

            sqlText = 'insert into vctalarm_meta  (market,korean_name,english_name,market_warning)'
            sqlText += ' values (?, ?, ?, ?)'

            sqlParam = []
            for data in data_json:       
                data.setdefault('market_warning', '')         
                sqlParam.append((data.get('market'),data.get('korean_name'),data.get('english_name'),data.get('market_warning')))
                MARKETS[data['market']] =  data['korean_name']

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
        markets = comm.searchDB("select market,korean_name,english_name,market_warning,substr(market,0,instr(market,'-')) as market_type from vctalarm_meta")
        return markets

    # get ticker markets
    def getTickerMarkets(self,markets):
        return pd.DataFrame(upbitapi.getQuotationTicker(markets))

    # get vctinfo ticks markets
    def getTradesTicksMarket(self,market,count):
        return pd.DataFrame(upbitapi.getQuotationTradesTicks(market=market,count=count))

    # get orderbook
    def getOrderbook(self,markets):
        return pd.DataFrame(upbitapi.getQuotationOrderbook(markets=markets))

    # get candles minutes
    def getCandlesMinutes(self, unit, market, count):
        return pd.DataFrame(upbitapi.getQuotationCandlesMinutes(unit=unit, market=market, count=count))

    ##########################################################

    # market monitor
    def monitorMarkets(self, loop=False, looptime=3, sort='signed_change_rate', targetMarket=['KRW','BTC','USDT']):
        selectMarkets = []

        ### TYPE ONE
        markets = self.getMarkets()
        for i in markets.index:
            if markets['market_type'][i] in targetMarket:
                selectMarkets.append(markets['market'][i])

        ### TYPE TWO
        # get continue grows coins
        # columns = ['opening_price','high_price','low_price','trade_price','candle_acc_trade_price','candle_acc_trade_volume']
        # columns = ['opening_price','trade_price']
        # selectMarkets = self.getChoiceGrowsMarkets(columns,3,3,3,3)

        ### TYPE THREE 
        # selectMarkets.append('KRW-DOGE')

        ###########################################################################################
        while True:
            # get ticker market data
            df = self.getTickerMarkets(selectMarkets).sort_values(by=sort, ascending=False)

            # merge market info & ticker market data
            df = pd.merge(df, markets, on = 'market')

            # ------------------------------------------------------------------------
            # unused filed delete
            # ticker market data
            # del df['market'] #종목 구분 코드	
            del df['trade_date'] 	#최근 거래 일자(UTC)	
            del df['trade_time'] 	#최근 거래 시각(UTC)	
            del df['trade_date_kst'] 	#최근 거래 일자(KST)	
            del df['trade_time_kst'] 	#최근 거래 시각(KST)	
            del df['trade_timestamp'] 	#최근 거래  타임스탬프	
            # del df['opening_price'] 	#시가	
            # del df['high_price'] 	#고가	
            # del df['low_price'] 	#저가	
            # del df['trade_price'] 	#종가	
            # del df['prev_closing_price'] 	#전일 종가	
            # del df['change'] 	#EVEN : 보합 RISE : 상승 FALL : 하락	
            del df['change_price'] 	#변화액의 절대값	
            del df['change_rate'] 	#변화율의 절대값	
            # del df['signed_change_price'] 	#부호가 있는 변화액	
            # del df['signed_change_rate'] 	#부호가 있는 변화율	
            # del df['trade_volume'] 	#가장 최근 거래량	
            del df['acc_trade_price'] 	#누적 거래대금(UTC 0시 기준)	
            # del df['acc_trade_price_14h'] 	#24시간 누적 거래대금	
            del df['acc_trade_volume'] 	#누적 거래량(UTC 0시 기준)	
            # del df['acc_trade_volume_14h'] 	#24시간 누적 거래량	
            del df['highest_52_week_price'] 	#52주 신고가	
            del df['highest_52_week_date'] 	#52주 신고가 달성일	
            del df['lowest_52_week_price'] 	#52주 신저가	
            del df['lowest_52_week_date'] 	#52주 신저가 달성일	
            del df['timestamp'] 	#타임스탬프	
            # market info
            # del df['korean_name']
            del df['english_name']
            del df['market_warning']
            del df ['market_type']
            # ------------------------------------------------------------------------

            # column align
            columns = df.columns.tolist()
            colalignList = []
            for colname in columns:
                if 'change' == colname or 'market_type' == colname or  'market_warning' == colname or colname.find('_date') > -1 or colname.find('_time') > -1 or colname.find('_timestamp') > -1:
                    colalignList.append("center")
                elif 'korean_name' == colname or 'english_name' == colname :        
                    colalignList.append("left")
                else:
                    colalignList.append("right")

            #  tabulate Below are all the styles that you can use :
            # “plain” “simple” “github” “grid” “fancy_grid” “pipe” “orgtbl” “jira” “presto” “pretty” “psql” “rst” “mediawiki” “moinmoin” “youtrack” “html” “latex” “latex_raw” “latex_booktabs”  “textile”
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False, colalign=colalignList))

            if(loop == True):
                time.sleep(looptime)
            else:
                break

    # automatic vctinfo
    def vctAlarm(self, targetMarket=['KRW', 'BTC', 'USDT']):
            selectCoins = []

            # get market info data
            markets = self.getMarkets()
            for i in markets.index:
                if markets['market_type'][i] in targetMarket:
                    selectCoins.append(markets['market'][i])

            conins_df = pd.DataFrame(selectCoins, columns=['market'])

            print(conins_df)


