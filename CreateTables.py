import io
import pymysql
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')



db=pymysql.connect(host='45.78.44.15',port=3306,user='remoteuser',password='1983524',db='MYSTOCK',charset='utf8')

cursor=db.cursor()

tmpResult=cursor.execute("CREATE TABLE StockNames(stockId char(10) NOT NULL unique DEFAULT '',stockName varchar(20) NOT NULL DEFAULT '_',PRIMARY KEY (stockId));")

print (tmpResult)

tmpResult=cursor.execute("create table StockProfit (recordId int not null auto_increment,stockId char(10) not null,earningPerShare decimal(20,4),businessIncome decimal(20,0),incomeIncByYear decimal(10,2),incomeIncByQuarter decimal(10,2),profit decimal(20,0),profitIncByYear decimal(10,2),profitIncByQuarter decimal(10,2),netAssetPerShare decimal(20,4),netAssetProfitRation decimal(10,2),cashPerShare decimal(20,4),grossMargin decimal(20,2),profitDistro varchar(40),publishDate DateTime not null,updateDate DateTime not null,reportQuarter int(6) not null,uploadTime timestamp not null default CURRENT_TIMESTAMP,Primary key (recordId),constraint FK_stock_id foreign key (stockId) references StockNames(stockId));")


print (tmpResult)

db.close()
