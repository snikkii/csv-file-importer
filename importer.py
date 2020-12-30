import csv
import re
import pandas as pd
import numpy as np
from lxml import etree
from pathlib import Path
from chardet import detect
from io import StringIO
from guessDialectAndHeader import fileDialect

#Zeile 60: regex !!
#mehrere dateien
#fehlerbehandlung

class file_importer():
    
    def __init__(self):
        self.__file = pd.DataFrame()

    def xmlImport(self, xmlFile:str, xslFile:str, encoding:str = None):
        if xmlFile.endswith(".xml"):
            if xslFile.endswith(".xsl"):
                xmldoc = etree.parse(xmlFile)
                transformer = etree.XSLT(etree.parse(xslFile))
                # + Fehlerbehandlung: Datei-, Parsing-, Transformationsfehler
                transformedString = str(transformer(xmldoc, sep=u"','")) 

                dialect = fileDialect()
                dialect.guess(transformedString)

                if encoding == None:
                    encoding = self.whichEncoding(xmlFile)

                xmlToCsv = StringIO(transformedString)

                self.csvImport(xmlToCsv, dialect, encoding)

    def csvImport(self, csvFile:str, dialect:fileDialect(), encoding:str = None):
        if dialect.header:
            header = 'infer'
        else:
            header = None

        if encoding == None:
            encoding = self.whichEncoding(csvFile)

        self.__file = pd.read_csv(
                        csvFile,
                        sep = dialect.sepChar,
                        quotechar = dialect.quoteChar,
                        encoding = encoding,
                        header = header)

        if dialect.header is False:
            self.createHeaders(self.__file)
        return self

    def whichEncoding(self, file:str):
        enc = detect(Path(file).read_bytes()) # von leo
        encoding = enc["encoding"]
        return encoding

    def newHeaderNames(self, string):
        """Checks if columns are specific data types and gives the header the name of it.\n
        returns string"""
        dataTypes = {
            "integer": re.compile(r"^[-+]?[1-9]\d*\.?[0]*$"), 
            "float": re.compile(r"^[+-]?([0-9]*[.])?[0-9]+$"), 
            "boolean": re.compile(r"^(?:tru|fals)e|(?:wahr|falsch)|(?:TRU|FALS)E|(?:WAHR|FALSCH)|(?:Tru|Fals)e|(?:Wahr|Falsch)$"), 
            "e-mail": re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"), 
            "web-url": re.compile(r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"), 
            "time": re.compile(r"^((([0]?[1-9]|1[0-2])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?))$"), 
            "date": re.compile(r"^(((0?[1-9]|1[012])/(0?[1-9]|1\d|2[0-8])|(0?[13456789]|1[012])/(29|30)|(0?[13578]|1[02])/31)/(19|[2-9]\d)\d{2}|0?2/29/((19|[2-9]\d)(0[48]|[2468][048]|[13579][26])|(([2468][048]|[3579][26])00)))$"),  
            "time-and-date": re.compile(r"^((((31\/(0?[13578]|1[02]))|((29|30)\/(0?[1,3-9]|1[0-2])))\/(1[6-9]|[2-9]\d)?\d{2})|(29\/0?2\/(((1[6-9]|[2-9]\d)?(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00))))|(0?[1-9]|1\d|2[0-8])\/((0?[1-9])|(1[0-2]))\/((1[6-9]|[2-9]\d)?\d{2})) (20|21|22|23|[0-1]?\d):[0-5]?\d:[0-5]?\d$"), 
             "coordinates": re.compile(r"^([SNsn][\s]*)?((?:[\+-]?[0-9]*[\.,][0-9]+)|(?:[\+-]?[0-9]+))(?:(?:[^ms'′″,\.\dNEWnew]?)|(?:[^ms'′″,\.\dNEWnew]+((?:[\+-]?[0-9]*[\.,][0-9]+)|(?:[\+-]?[0-9]+))(?:(?:[^ds°″,\.\dNEWnew]?)|(?:[^ds°″,\.\dNEWnew]+((?:[\+-]?[0-9]*[\.,][0-9]+)|(?:[\+-]?[0-9]+))[^dm°'′,\.\dNEWnew]*))))([SNsn]?)[^\dSNsnEWew\+-]+([EWew][\s]*)?((?:[\+-]?[0-9]*[\.,][0-9]+)|(?:[\+-]?[0-9]+))(?:(?:[^ms'′″,\.\dNEWnew]?)|(?:[^ms'′″,\.\dNEWnew]+((?:[\+-]?[0-9]*[\.,][0-9]+)|(?:[\+-]?[0-9]+))(?:(?:[^ds°″,\.\dNEWnew]?)|(?:[^ds°″,\.\dNEWnew]+((?:[\+-]?[0-9]*[\.,][0-9]+)|(?:[\+-]?[0-9]+))[^dm°'′,\.\dNEWnew]*))))([EWew]?)$")
        }
        
        for elem in dataTypes:
            if dataTypes[elem].match(string):
                return elem
        return ("text")
    
    def createHeaders(self, df:pd.DataFrame):
        headerNames = []
        ctr = 0

        for column in df.columns:
            data = df[column]
            headerName = self.newHeaderNames(str(data.iloc[0]))
            headerNames.append(headerName + "_" + str(ctr))
            ctr += 1

        df.columns = headerNames
        
        return headerNames
    
    def getDataFrame(self):
        return self.__file
    
    def getDictionary(self):
        return self.__file.to_dict(orient = 'list')

    def getNumPyArray(self):
        return self.__file.to_numpy()

    def getListOfLists(self): 
        listOfLists = self.__file.values.tolist()
        header = list(self.__file.columns)
        listOfLists.insert(0, header)
        return listOfLists     
    
    def resetIt(self):
        self.__file = pd.DataFrame()
        return self
    
    #def getJson() wenn ich noch zeit hab