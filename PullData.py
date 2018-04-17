#-*- coding: utf-8 -*-
import logging
import os
import io
import sys
import time
import re
import requests
import json


class Log:
    def __init__(self):
        self.resultFolder=None
        self.resultFile=None
        self.name='StockDB'
        self._createResultFolder()
        self.logger=logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=self.resultFile,
                filemode='w')
        console=logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        formatter =logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def _createResultFolder(self):
        self.resultFolder=r'./logs/'+str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
        if not os.path.exists(self.resultFolder):
            os.makedirs(self.resultFolder)
        self.resultFile=self.resultFolder+r'/'+self.name+'.log'

class Headers:
    firstHeader={'Host':'data.eastmoney.com',
                 'Connection':'keep-alive',
                 'Upgrade-Insecure-Requests':'1',
                 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                 'Referer':'http://data.eastmoney.com/bbsj/201803/yjbb.html',
                 'Accept-Encoding':'gzip, deflate',
                 'Accept-Language':'zh-CN,zh;q=0.9'}


class UrlAddress:
    def __init__(self):
        self.logger=logging.getLogger(__name__)
        self.month=None

    def _parseQuarter(self,yearQuarter):
        myQuarter=str(yearQuarter)[-2:]
        if myQuarter=='Q1':
            self.month='03'
        elif myQuarter=='Q2':
            self.month='06'
        elif myQuarter=='Q3':
            self.month='09'
        elif myQuarter=='Q4':
            self.month='12'
        else:
            self.logger.error('Wrong YearQuarter Format')
            os._exit(1)

    def getInitPage(self,yearQuarter):
        self._parseQuarter(yearQuarter)
        yearMonth=str(yearQuarter)[:4]+self.month
        initPageAddress='http://data.eastmoney.com/bbsj/'+yearMonth+'/yjbb.html'
        self.logger.info(initPageAddress)
        return initPageAddress

    def urlFormatForMorePages(self):
        hostPage='http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=YJBB20_YJBB&token='

class PullDataFromWeb:
    def __init__(self,timeWanted):    #e.g.  2017Q4
        self.logger=logging.getLogger(__name__)
        self.session=requests.Session()
        self.timeWanted=timeWanted
        self.myCookie=None
        self.totalRecords=[]
        self.totalPageNum=1
        self.tmpUrlGenerator=UrlAddress()

    def _pullFirstPage(self):
        firstPageUrl=self.tmpUrlGenerator.getInitPage(self.timeWanted)
        response=self.session.get(firstPageUrl,verify=False,headers=Headers.firstHeader)
        self.myCookie=response.cookies
        self.logger.debug(response.text)

        reg={'pageNum':re.compile('defjson\: \{pages\:(\d*),data\:'),'stockInfo':re.compile('defjson\: \{pages\:\d*,data\:(.*)\}\,\s*beforeupdate'),'token':re.compile('token=(.*)\&st='),'sortType':re.compile('id\:\s\"(.*?)\"\,\sdesc'),'sortRule':re.compile('\,\sdesc\:\s(\w+?)\s\}\,')}
        #get total page number
        totalPageQty=reg['pageNum'].findall(response.text)[0]
        self.logger.info('total page numer is %s'%totalPageQty)
        self.totalPageNum=totalPageQty
        #get stock info on first page
        stockInfoOn1stPage=reg['stockInfo'].findall(response.text)[0]
        parsedStockInfoOn1stPage=json.loads(stockInfoOn1stPage)
        self.logger.debug('stock info of first page is:')
        self.logger.debug(parsedStockInfoOn1stPage)
        self.totalRecords.append(parsedStockInfoOn1stPage)
        #prepare url for following pages
        tmpToken=reg['token'].findall(response.text)[0]
        tmpSort=reg['sortType'].findall(response.text)[0]
        parsedRule={'true':'-1','false':'1'}
        tmpRule=parsedRule[reg['sortRule'].findall(response.text)[0]]
        self.logger.info('sort type is %s'%tmpSort)
        self.logger.debug('token is %s'%tmpToken)
        self.logger.debug('sort type is %s'%tmpSort)
        self.logger.info('sort rule is %s'%tmpRule)
        #self.tmpUrlGenerator.urlFormatForMorePages(tmpToken,tmpSort,tmpRule)

    def _pullMorePages(self):
        if int(self.totalPageNum)>1:
            for currentPageNum in range(2,int(self.totalPageNum)+1):
                self._pullCurrentPage(currentPageNum)
        else:
            self.logger.info('Only one page stock informations')

    def _pullCurrentPage(self,pageNum):
        return


    def run(self):
        self._pullFirstPage()
        self._pullMorePages()
        self.logger.info('Done!!!!!!!!!!')





if __name__=='__main__':
    log=Log()
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

    log.logger.info('---------------------------------------------------')
    log.logger.info('----------Pull Stock Data From Web-----------------')
    log.logger.info('----------Developed By Zhang Zi We-----------------')
    log.logger.info('---------------------------------------------------')

    myData=PullDataFromWeb('2018Q1')
    myData.run()
