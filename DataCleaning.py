import os
import re
import demjson

rawFilePath = "/home/ziwen/MyProjects/StockDB/logs/zcfzb/"

print("Start to check format of these raw files")
standardDictKeys = []
for fileName in os.listdir(rawFilePath):
    print("Checking %s" % fileName)
    oneRawFile = rawFilePath + fileName
    with open(oneRawFile, "r") as f:
        for eachLine in f:
            if standardDictKeys:
                if standardDictKeys != (demjson.decode(eachLine.strip()).keys()):
                    print(eachLine)
                    print("line dict format is different")
                    os._exit(1)
            else:
                standardDictKeys = demjson.decode(eachLine.strip()).keys()
                print(
                    "standard dict keys is %s"
                    % str(demjson.decode(eachLine.strip()).keys())
                )
        print("All rows have same format and name")
        f.close()
print("Finish format check.")

print("Parse data type...")
myReg = {
    "oneGroupData": re.compile("('.*?':.*?(\}|\,))"),
    "separateKeyValue": re.compile("(^'(.*?)':(.*))"),
    "dateTimeType":re.compile("'\d+\-\d+\-\d+T\d+\:\d+\:\d+'"),
    "stringType":re.compile("'.*'"),
    "separateIntDecimal":re.compile("^\s*(.*?)\.(.*)")
}
dataType = {}
maxStringLen=0
maxIntegerLen=0
maxDecimalLen=0
# default is VARCHAR
for tmpKey in standardDictKeys:
    dataType[tmpKey] = "VARCHAR"

for fileName in os.listdir(rawFilePath):
    print("Parse data type of  %s" % fileName)
    oneRawFile = rawFilePath + fileName
    with open(oneRawFile, "r") as f:
        for eachLine in f:
            pairsInOneLine = myReg["oneGroupData"].findall(eachLine.strip())
            for tmpPair in pairsInOneLine:
                tmpStr = tmpPair[0][:-1]  # remove comma for each pair
                myKey = myReg["separateKeyValue"].search(tmpStr).group(2)
                myValue = myReg["separateKeyValue"].search(tmpStr).group(3)
                #print (myValue)
                if myReg["dateTimeType"].search(myValue):
                    dataType[myKey]="DATETIME"
                elif myReg["stringType"].search(myValue):
                    if len(myValue)>maxStringLen:
                        maxStringLen=len(myValue)
                else:
                    dataType[myKey]="DECIMAL"
                    intPart=myReg["separateIntDecimal"].search(myValue).group(1)
                    #print (len(str(intPart)))
                    decPart=myReg["separateIntDecimal"].search(myValue).group(2)
                    #print (len(str(decPart)))
                    if len(str(intPart))>maxIntegerLen:
                        maxIntegerLen=len(str(intPart))
                    if len(str(decPart))>maxDecimalLen:
                        maxDecimalLen=len(str(decPart))
        f.close()

for tmpKey in standardDictKeys:
    print ("%s : %s"%(tmpKey,dataType[tmpKey]))
print ("max string length is : %s"%maxStringLen)
print ("max int part length is : %s"%maxIntegerLen)
print ("max dec part length is : %s"%maxDecimalLen)

