import csv
from pathlib import Path
from chardet import detect

class fileDialect():
    sepChar:str = ","
    quoteChar:str = "\""
    encoding:str = "utf-8"
    header:bool = False                 

    def guess(self, strng:str):
        self.header = self.hasHeader(strng)

        dialect = self.whatDialect(strng)
        if dialect != None:
            self.sepChar = dialect.delimiter
            self.quoteChar = dialect.quotechar 
        
        return self
    
    def whatDialect(self, strng:str):
        return csv.Sniffer().sniff(strng)
    
    def hasHeader(self, strng:str):
        return csv.Sniffer().has_header(strng)