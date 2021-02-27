import csv
from pathlib import Path
from chardet import detect

class fileDialect():
    """This class guesses the dialect of a file and if there are headers.
    The following attributes contain the default-values:
            sepChar: a string; if no delimiter was found it will be ','
            quoteChar: a string; if no quotecharacter was found it will be '\'
            encoding: a string; if no encoding will be detected, it will be 'utf-8'
            header: a boolean; will be changed to 'True' if there are headers"""
    sepChar:str = "," 
    quoteChar:str = "\""
    encoding:str = "utf-8"
    header:bool = False               

    def guess(self, strng:str):
        """changes default parameters
        
        Parameters: 
                strng: a string; it will be tested if the string has headers and what dialect is has
                
        Returns self"""
        self.header = self.hasHeader(strng)

        dialect = self.whatDialect(strng)
        if dialect != None:
            self.sepChar = dialect.delimiter
            self.quoteChar = dialect.quotechar 
        
        return self
    
    def whatDialect(self, strng:str):
        """Returns dialect of given string"""
        return csv.Sniffer().sniff(strng)
    
    def hasHeader(self, strng:str):
        """Returns 'True' if given string has headers.\n
        Returns 'False' if given string has no headers."""
        return csv.Sniffer().has_header(strng)

    def whichEncoding(self, file:str):
        """Guesses encoding from given file.
        
        Parameters:
                file: a string; contains the filepath of the given file
                
        Returns encoding"""
        enc = detect(Path(file).read_bytes())
        encoding = enc["encoding"]
        return encoding