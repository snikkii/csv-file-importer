import pandas as pd
from lxml import etree
from importer import file_importer
from guessDialectAndHeader import fileDialect

#fehlerbehandlung

class file_exporter():
    __file = pd.DataFrame()
    def __init__(self, importer:file_importer()):
        self.__file = importer.getDataFrame()
    
    def exportAsCSV(self, filePath:str, sepChar:str, quoteChar:str, encoding:str):
        self.__file.to_csv(filePath, sep = sepChar, quotechar = quoteChar, encoding = encoding, index = False)
    
    def exportAsXML(self, filePath:str, encoding:str):
        root = etree.Element("items")

        for _, row in self.__file.iterrows():
            child = etree.SubElement(root, "item")
            for field in row.index:
                elem = etree.SubElement(child, field)
                elem.text = str(row[field])

        doc = etree.ElementTree(root)
        doc.write(filePath, xml_declaration = True, pretty_print = True, encoding = encoding)
    
