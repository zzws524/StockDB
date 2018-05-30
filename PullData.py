# -*- coding: utf-8 -*-
import logging
import os
import io
import sys
import time
import re
import requests
import json
import random
import string


class Log:
    def __init__(self):
        self.resultFolder = None
        self.resultFile = None
        self.name = "StockDB"
        self._createResultFolder()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s",
            datefmt="%a, %d %b %Y %H:%M:%S",
            filename=self.resultFile,
            filemode="w",
        )
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def _createResultFolder(self):
        self.resultFolder = r"./logs/" + str(
            time.strftime("%Y%m%d%H%M%S", time.localtime())
        )
        if not os.path.exists(self.resultFolder):
            os.makedirs(self.resultFolder)
        self.resultFile = self.resultFolder + r"/" + self.name + ".log"


class Headers:
    firstHeader = {
        "Host": "data.eastmoney.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "http://data.eastmoney.com/bbsj/201803/yjbb.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }


class UrlAddress:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.year = None
        self.month = None
        self.date = None
        self.tableType = None

    def _parseQuarter(self, yearQuarter):
        myQuarter = str(yearQuarter)[-2:]
        self.year = str(yearQuarter)[0:4]
        if myQuarter == "Q1":
            self.month = "03"
            self.date = "31"
        elif myQuarter == "Q2":
            self.month = "06"
            self.date = "30"
        elif myQuarter == "Q3":
            self.month = "09"
            self.date = "30"
        elif myQuarter == "Q4":
            self.month = "12"
            self.date = "31"
        else:
            self.logger.error("Wrong YearQuarter Format")
            os._exit(1)

    def _parseTableType(self, tableType):
        tmpArr = {
            "业绩报表": [
                "/yjbb.html",
                "YJBB20_YJBB",
                "(securitytypecode%20in%20(%27058001001%27))",
            ],
            "资产负债表": ["/zcfz.html", "CWBB_ZCFZB", ""],
            "利润表": ["/lrb.html", "CWBB_LRB", ""],
            "现金流量表": ["/xjll.html", "CWBB_XJLLB", ""],
        }
        self.tableType = tmpArr[tableType]

    def getInitPage(self, tableType, yearQuarter):
        self._parseQuarter(yearQuarter)
        self._parseTableType(tableType)
        yearMonth = str(yearQuarter)[:4] + self.month
        initPageAddress = (
            "http://data.eastmoney.com/bbsj/" + yearMonth + self.tableType[0]
        )
        self.logger.debug("init page address is : %s" % initPageAddress)
        return initPageAddress

    def dataTableUrl(self, token, sortType, sortRule, currentPageNum):
        random8Chars = "".join(random.sample(string.ascii_letters, 8))
        tmpCurrentTime = int(int(time.time() / 30))
        # TBD, sercuritytpycode is different.
        hostPage = (
            "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type="
            + self.tableType[1]
            + "&token="
            + token
            + "&st="
            + sortType
            + "&sr="
            + sortRule
            + "&p="
            + currentPageNum
            + "&ps=50&js=var%20"
            + random8Chars
            + "={pages:(tp),data:%20(x)}&filter=(reportdate=^"
            + self.year
            + "-"
            + self.month
            + "-"
            + self.date
            + "^)"
            + self.tableType[2]
            + "&rt="
            + str(tmpCurrentTime)
        )
        self.logger.debug(hostPage)
        return hostPage


class PullDataFromWeb:
    def __init__(self, tableType, timeWanted):  # e.g.  '业绩报表','2017Q4'
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.tableType = tableType
        self.timeWanted = timeWanted
        self.myCookie = None
        self.totalRecords = []
        self.totalPageNum = 1
        self.tmpUrlGenerator = UrlAddress()

    def pullData(self):
        firstPageUrl = self.tmpUrlGenerator.getInitPage(self.tableType, self.timeWanted)
        response = self.session.get(
            firstPageUrl, verify=False, headers=Headers.firstHeader
        )
        self.myCookie = response.cookies
        # self.logger.debug(response.text)

        reg = {
            "onePageInfo": re.compile("var\s\S{8}=(.*)"),
            "token": re.compile("token=(.*)\&st="),
            "sortType": re.compile('id\:\s"(.*?)"\,\sdesc'),
            "sortRule": re.compile("\,\sdesc\:\s(\w+?)\s\}\,"),
        }
        # tokens for urls used by following pages
        tmpToken = reg["token"].findall(response.text)[0]
        tmpSort = reg["sortType"].findall(response.text)[0]
        parsedRule = {"true": "-1", "false": "1"}
        tmpRule = parsedRule[reg["sortRule"].findall(response.text)[0]]
        self.logger.debug("sort type is %s" % tmpSort)
        self.logger.debug("token is %s" % tmpToken)
        self.logger.debug("sort type is %s" % tmpSort)
        self.logger.debug("sort rule is %s" % tmpRule)

        # parse first page of the table, get total page number
        tmpUrl = self.tmpUrlGenerator.dataTableUrl(tmpToken, tmpSort, tmpRule, "1")
        self.logger.info("I am working on page 1 of the table")
        response = self.session.get(tmpUrl, verify=False, headers=Headers.firstHeader)
        tmpStr = (
            (reg["onePageInfo"].findall(response.text)[0])
            .replace("pages:", '"pages":')
            .replace("data:", '"data":')
        )
        self.totalPageNum = json.loads(tmpStr)["pages"]
        self.logger.info("Totally %s pages will be pulled" % (self.totalPageNum))
        self.totalRecords = json.loads(tmpStr)["data"]

        # parse remaining pages of the table
        # for currentPageNum in range(2,self.totalPageNum+1):
        for currentPageNum in range(2, 3):
            tmpUrl = self.tmpUrlGenerator.dataTableUrl(
                tmpToken, tmpSort, tmpRule, str(currentPageNum)
            )
            self.logger.info(
                "I am working on page %s of the table" % str(currentPageNum)
            )
            response = self.session.get(
                tmpUrl, verify=False, headers=Headers.firstHeader
            )
            tmpStr = (
                (reg["onePageInfo"].findall(response.text)[0])
                .replace("pages:", '"pages":')
                .replace("data:", '"data":')
            )
            for tmpEachRecord in json.loads(tmpStr)["data"]:
                self.totalRecords.append(tmpEachRecord)
            time.sleep(1)

    def saveResult(self, path):
        myFile = path + r"/" + self.tableType + self.timeWanted + r".txt"
        with open(myFile, "a") as f:
            for eachRecord in self.totalRecords:
                f.write(str(eachRecord))
                f.write("\n")
            f.close()
        self.logger.info("Totally %s records"%str(len(self.totalRecords)))
        self.logger.info("Done!!!!!!!!!!")


if __name__ == "__main__":
    log = Log()
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    log.logger.info("---------------------------------------------------")
    log.logger.info("----------Pull Stock Data From Web-----------------")
    log.logger.info("----------Developed By Zhang Zi We-----------------")
    log.logger.info("---------------------------------------------------")

    myData = PullDataFromWeb("资产负债表", "2017Q4")
    myData.pullData()
    myData.saveResult(log.resultFolder)
