# -*- coding: utf-8 -*-
import logging
import os
import time
import requests



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
        console=logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter =logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def _createResultFolder(self):
        self.resultFolder=r'./logs/'+str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
        if not os.path.exists(self.resultFolder):
            os.makedirs(self.resultFolder)
        self.resultFile=self.resultFolder+r'/'+self.name+'.log'


class PullDataFromWeb:
    def __init__(self,quarterWanted):
        self.logger=logging.getLogger(__name__)
        self.quarterWanted=quarterWanted









if __name__=='__main__':
    log=Log()

    log.logger.info('---------------------------------------------------')
    log.logger.info('----------Pull Stock Data From Web-----------------')
    log.logger.info('----------Developed By Zhang Zi We-----------------')
    log.logger.info('---------------------------------------------------')
