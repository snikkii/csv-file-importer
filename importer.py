import csv
import re
import lxml.etree
import pandas as pd
import numpy as np
from lxml import etree
from pathlib import Path
from chardet import detect
from io import StringIO
from guessDialectAndHeader import fileDialect

class file_importer():
    """This class imports csv- or xml-files. It also checks if the files have a header or the dialect and encoding.\n
    The file can be transformed into a pandas dataframe, a numpy array, a list of lists or a dictionary."""
    
    def __init__(self):
        """Constructor of class 'file_importer'.\n
        The following attribute '__file' is a dataframe which contains the data given from the csv- or xml-file"""
        self.__file = pd.DataFrame()
        self.guesser = fileDialect()

    def xmlImport(self, xmlFile:str, xslFile:str, encoding:str = None):
        """Takes a xml-file and a xsl-stylesheet and transforms it into a dataframe.\n
        Dialect will be guessed by fileDialect-class.\n
        If no encoding is given, it will also be guessed.
        
        Parameters: 
                xmlFile: a string; contains filepath of the xml-file  
                xslFile: a string; contains filepath of the xsl-stylesheet
                encoding: a string; contains the given encoding (optional)
                
        Returns self"""
        if xmlFile.endswith(".xml"):
            if xslFile.endswith(".xsl"):
                try:
                    xmldoc = etree.parse(xmlFile)
                except lxml.etree.ParseError as parErr:
                    raise lxml.etree.ParseError(parErr)

                try:
                    transformer = etree.XSLT(etree.parse(xslFile))
                except lxml.etree.XSLTParseError as xslParErr:
                    raise lxml.etree.XSLTParseError(xslParErr)
                
                try:
                    transformedString = str(transformer(xmldoc, sep=u"','")) 
                except etree.XSLTApplyError as appErr:
                    raise etree.XSLTApplyError(appErr)

                dialect = fileDialect()
                dialect.guess(transformedString)

                if encoding == None:
                    encoding = self.guesser.whichEncoding(xmlFile)

                xmlToCsv = StringIO(transformedString)

                self.__file = self.csvImport(xmlToCsv, dialect, encoding)
               
                return self.__file
            
            else:
                raise ValueError("choose xsl file!")
        else:
            raise ValueError("choose xml file!")

    def csvImport(self, csvFile:str, dialect:fileDialect(), encoding:str = None):
        """Takes a csv-file and transforms it into a dataframe.\n
        Dialect will be guessed by fileDialect-class.\n
        If no encoding is given, it will also be guessed.
        
        Parameters:
                csvFile: a string; contains filepath of csv file or a string which will be converted into the dataframe
                dialect: object of the class fileDialect; contains information about delimiter or quotecharacter
                 encoding: a string; contains the given encoding (optional)
        
        Returns the dataframe '__file'"""
        header = 'infer' if dialect.header else None

        if encoding == None:
            encoding = self.guesser.whichEncoding(csvFile)

        self.__file = pd.read_csv(
                        csvFile,
                        sep = dialect.sepChar,
                        quotechar = dialect.quoteChar,
                        encoding = encoding,
                        header = header)

        if dialect.header is False:
            self.createHeaders(self.__file)
        return self.__file

    def newHeaderNames(self, string):
        """Checks if columns are specific data types and creates list of new headernames.
        
        Parameters: 
                string: a string which will be tested
                
        Returns the datatype of the given string"""
        dataTypes = {
            "integer": re.compile(r"^[-+]?[1-9]\d*\.?[0]*$"), 
            "float": re.compile(r"^[+-]?([0-9]*[.])?[0-9]+$"),
            "boolean": re.compile(r"^(?:tru|fals)e|(?:wahr|falsch)|(?:TRU|FALS)E|(?:WAHR|FALSCH)|(?:Tru|Fals)e|(?:Wahr|Falsch)$"),
            "coordinate": re.compile(r"^(N|S)?0*\d{1,3}°0*\d{1,3}(′|')0*\d{1,3}\.\d*(″|\")(?(1)|(N|S)) (E|W)?0*\d{1,3}°0*\d{1,3}(′|')0*\d{1,3}\.\d*(″|\")(?(5)|(E|W))$"), 
            "e-mail": re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"), 
            "time": re.compile(r"(^([0-1]?\d|2[0-3]):([0-5]?\d):([0-5]?\d)$)|(^([0-5]?\d):([0-5]?\d)$)|(^[0-5]?\d$)"), 
            "date": re.compile(r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$"),  
            "time-and-date": re.compile(r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2}).([0-1]\d|2[0-3]):[0-5]\d(:[0-5]\d)*$"),
            "web-url": re.compile(r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$") 
        }
        
        for elem in dataTypes:
            if dataTypes[elem].match(string):
                return elem
        return ("text")
    
    def createHeaders(self, df:pd.DataFrame):
        """Changes headernames of dataframe with list from function newHeaderNames.
        
        Parameters:
                df: a pandas dataframe with or without headers
                
        Returns the new headernames"""
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
        """Returns data as a pandas dataframe."""
        return self.__file
    
    def getDictionary(self):
        """Returns data as dictionary."""
        return self.__file.to_dict(orient = 'list')

    def getNumPyArray(self):
        """Returns data as numPy-array."""
        return self.__file.to_numpy()

    def getListOfLists(self): 
        """Returns data as list of lists.\n
        The first list contains the headers."""
        listOfLists = self.__file.values.tolist()
        header = list(self.__file.columns)
        listOfLists.insert(0, header)
        return listOfLists     
    
    def resetIt(self):
        """Clears the dataframe.

        Returns void"""
        self.__file = pd.DataFrame()
        return self