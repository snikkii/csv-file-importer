import pandas as pd
from lxml import etree
from importer import file_importer

#fehlerbehandlung

class file_exporter():
    """This class exports a dataframe to a csv-file or a xml-file."""
    def __init__(self):
        """Constructor of class 'file_exporter'
        The attributes of this class are the 'file_imprter'-object of 'file_importer'-class 
        and a dataframe ('__file') which contains the data."""
        self.file_importer = file_importer()
        self.__file = pd.DataFrame()
    
    def exportAsCSV(self, filePath:str, dataframe:pd.DataFrame(), sepChar:str=",", quoteChar:str="\"", encoding:str="UTF-8"):
        """Turns dataframe into a csv-file.
        
        Parameters:
                filePath: a string; contains the path where file will be saved and what name it has
                dataframe: a pandas dataframe; this is the data which will be turned into a csv-file
                sepChar: a string; sepereates the cells, by default it is ','
                quoteChar: a string; quotation of the cells, by default it is '"'
                encoding: a string; the encoding which the file will be encoded with, by default it is 'utf-8'
        
        Returns nothing"""
        self.__file = dataframe.to_csv(filePath, sep = sepChar, quotechar = quoteChar, encoding = encoding, index = False)
    
    def exportAsXML(self, filePath:str, dataframe:pd.DataFrame(), encoding:str):
        """Turns a given dataframe into a xml-file.
        
        Parameters:
                filePath: a string; contains the path where file will be saved and what name it has
                dataframe: a pandas dataframe; this is the data which will be turned into a csv-file
                encoding: a string; the encoding which the file will be encoded with, by default it is 'utf-8'
                
        Returns nothing"""

        root = etree.Element("items")

        for _, row in dataframe.iterrows():
            item = etree.SubElement(root, "item")
            for field in row.index:
                testField = str(field)

                hasSpecialChar = map(testField.startswith, ("xml", "=", ":", ",", ".", "<", ">", "\""))
                hasDigit = testField[0].isdigit()

                if any(hasSpecialChar) or hasDigit:
                    raise ValueError("Header can't be converted into tag because it starts with an invalid Character or a number.")

                try:
                    replaceIt = testField.replace(" ", "_")
                    elem = etree.SubElement(item, testField)
                except ValueError:
                    raise ValueError(elem + "isn't a valid tag-name.")
                
                elem.text = str(row[field])

        doc = etree.ElementTree(root)
        doc.write(filePath, xml_declaration = True, pretty_print = True, encoding = encoding)