import pandas as pd
import numpy as np
from importer import file_importer
from exporter import file_exporter
from guessDialectAndHeader import fileDialect 
from tkinter import Tk, Menu, Label, Button, Frame, Entry, StringVar, Checkbutton, BooleanVar, OptionMenu, DISABLED
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo, showwarning, showerror
from pandastable import Table

#fehlerbehandlung  
  
class gui(): 
    """Graphical Userinterface to import and export xml- or csv-files.\n
    Dialect, encoding and the existence of headers can also be changed.""" 
    def __init__(self):
        """Constructor of class 'gui'.
        Builds the graphical userinterface without data.\n 
        Data can be added with several other functions that will be activated with buttons."""
        self.importer = file_importer()
        self.exporter = file_exporter()
        self.guessDialectAndHeader = fileDialect()
        self.root = Tk()

        self.data = pd.DataFrame()
        self.encoding = str
        self.encodingList = ["ISO-8859-15", "CP1252", "UTF-8", "UTF-16BE", "UTF-16LE", "ASCII", "UTF-16", "ISO-8859-1"]
        self.filePath = str
        self.sepCharBuffer = str
        self.quoteCharBuffer = str
        self.encodingBuffer = str

        self.root.title("file_importer_and_exporter")
        self.root.minsize(width = 1200, height = 400)
        self.root.configure(bg = "#FAEBD7")

        self.menubar = Menu(self.root)
        self.menubar.add_cascade(label="clear table", command = self.resetTable)
        self.menubar.add_cascade(label = "about", command = self.about)
        self.menubar.add_cascade(label = "exit", command = lambda: self.root.destroy())

        self.root.configure(menu = self.menubar)

        self.frame = Frame(self.root)
        self.frame.grid(row = 0, column = 0)
        self.dataTable = Table(self.frame)
        self.dataTable.show()

        self.settingsFrame = Frame(self.root)
        self.settingsFrame.configure(bg = "#FFFFFF")
        self.settingsFrame.grid(row = 0, column = 1, padx = 10, pady = 10)

        self.addButton = Button(self.settingsFrame, command = self.addData, text= "add file", bg = "#F9E9CF")
        self.addButton.grid(row = 0, column = 2, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.explanationLabel = Label(self.settingsFrame, text= "select your options:")
        self.explanationLabel.grid(row = 1, column = 2, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.quoteCharLabel = Label(self.settingsFrame, text = "quote character:")
        self.quoteCharLabel.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')
        self.sepCharLabel = Label(self.settingsFrame, text = "delimiter:")
        self.sepCharLabel.grid(row = 2, column = 2, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')
        self.encodingLabel = Label(self.settingsFrame, text = "encoding:")
        self.encodingLabel.grid(row = 2, column = 3, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')
       
        self.qouteCharVariable = StringVar()
        self.qouteCharField = Entry(self.settingsFrame, textvariable = self.qouteCharVariable)
        self.qouteCharField.grid(row = 3, column = 1, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.sepCharVariable = StringVar()
        self.sepCharField = Entry(self.settingsFrame, textvariable = self.sepCharVariable)
        self.sepCharField.grid(row = 3, column = 2, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.encodingVariable = StringVar()
        self.encodingField = OptionMenu(self.settingsFrame, self.encodingVariable, *self.encodingList)
        self.encodingField.grid(row = 3, column = 3, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.hasHeaderVariable = BooleanVar()
        self.hasHeaderButton = Checkbutton(self.settingsFrame, command = self.updateHeaders, text = "header?", variable = self.hasHeaderVariable)
        self.hasHeaderButton.grid(row = 4, column = 1, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.exportFrame = Frame(self.root)
        self.exportFrame.configure(bg = "#FFFFFF")
        self.exportFrame.grid(row = 1, column = 2, padx = 10, pady = 10)

        self.csvButton = Button(self.exportFrame, state = DISABLED, command = self.exportCSV, text= "export as CSV", bg = "#F9E9CF")
        self.csvButton.grid(row = 6, column = 0, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.xmlButton = Button(self.exportFrame, state = DISABLED, command = self.exportXML, text= "export as XML", bg = "#F9E9CF")
        self.xmlButton.grid(row = 6, column = 1, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.root.mainloop()

    def addData(self):
        """Data will be transformed from file into a dataframe.\n
        The table with the given data will also be updated and shows the given data."""
        try:
            self.readFilePath = askopenfilename(title = "open csv or xml file!")
            if self.readFilePath.endswith(".csv"):
                self.data = self.importer.csvImport(self.readFilePath, dialect = self.guessDialectAndHeader)
                self.guessDialectAndHeader.guess(self.readFilePath)
                self.encoding = self.guessDialectAndHeader.whichEncoding(self.readFilePath)
            
            elif self.readFilePath.endswith(".xml"):
                xslStyleSheet = askopenfilename(title = "open stylesheet!")
                if xslStyleSheet.endswith(".xsl"):
                    self.data = self.importer.xmlImport(self.readFilePath, xslStyleSheet)

                    self.qouteCharField.config(state = 'disabled')
                    self.sepCharField.config(state = 'disabled')
                   
                else:
                    showwarning("WARNING!", 
                                "There need to be a xsl-stylesheet.")
                    raise ValueError("There must be a xsl-stylesheet")                    
            
            else:
                showwarning("WARNING!", 
                                "Only csv- or xml-files are allowed.")
                raise ValueError("Only csv- or xml-files are allowed.")
            
            self.dataTable = Table(self.frame, dataframe = self.data)
            self.dataTable.show()

            self.updateEntrys()

            self.addButton.config(state = 'disabled')
            self.csvButton.config(state = 'normal')
            self.xmlButton.config(state = 'normal')
        
        except:
            showerror("ERROR!",
                        "File couldn't be opened.")

    def updateEntrys(self):
        """Entry-fields will be filled with guessed dialect to show user what dialect the file now has."""
        self.sepCharField.insert(0, self.guessDialectAndHeader.sepChar)
        self.qouteCharField.insert(0, self.guessDialectAndHeader.quoteChar)
        self.encodingVariable.set(self.guessDialectAndHeader.encoding.upper())
        
        if self.guessDialectAndHeader.hasHeader is False:
            self.hasHeaderButton.deselect()
        else:
            self.hasHeaderButton.select()

    def resetTable(self):
        """Table and dataframe will be cleared. The user can now add a new file."""
        self.data = self.importer.resetIt()
        self.qouteCharField.delete(0, 'end')
        self.sepCharField.delete(0, 'end')
        self.updateDialect()

        self.dataTable = Table(self.frame)
        self.dataTable.show()

        self.qouteCharField.config(state = 'normal')
        self.sepCharField.config(state = 'normal')

        self.addButton.config(state = 'normal')

        self.csvButton.config(state = 'disabled')
        self.xmlButton.config(state = 'disabled')
        
    def updateDialect(self):
        """Updates the dialect if the user changes anything.
        
        Returns void"""
        self.quoteCharBuffer = self.qouteCharVariable.get()
        self.sepCharBuffer =  self.sepCharVariable.get()
        self.encodingBuffer = self.encodingVariable.get()

        self.qouteCharField.delete(0, 'end')
        self.sepCharField.delete(0, 'end')

        self.qouteCharField.insert(0, self.quoteCharBuffer)
        self.sepCharField.insert(0, self.sepCharBuffer)
        self.encodingVariable.set(self.encodingVariable.get().upper())

        return self

    def updateHeaders(self):
        """Headers will be updated if the user wants some or not.
        
        Returns void"""
        if self.readFilePath.endswith(".xml"):
            self.hasHeader = self.hasHeaderVariable.get()
            self.hasHeader = not self.hasHeader
        elif self.readFilePath.endswith(".csv"):
            self.hasHeader = self.hasHeaderVariable.get()

        if self.hasHeader is True:
            newFirstLine = list(self.data.columns.values)
            self.data = self.data.append(pd.Series(newFirstLine, index = self.data.columns), ignore_index = True)
            self.data = self.data.iloc[np.arange(-1, len(self.data)-1)]
            self.data = self.data.reset_index(drop = True)

            self.importer.createHeaders(self.data)
            
        elif self.hasHeader is False:
            newHeader = self.data.iloc[0]
            self.data = self.data[1:]
            self.data.columns = newHeader

        self.updateTable()
        return self

    def updateTable(self):
        """Table will be updated. It now contains the new information like changed headers."""
        self.dataTable = Table(self.frame, dataframe = self.data)
        self.dataTable.show()

    def exportCSV(self):
        """Exports dataframe to csv. The user can choose where the file will be saved."""
        self.updateDialect()
    
        try: 
            self.filePath = asksaveasfilename(
                                        defaultextension = ".csv",
                                        filetypes = [("CSV file", "*.csv")],
                                        initialfile = "output.csv")
            self.exporter.exportAsCSV(self.filePath, 
                                    self.data,
                                    self.sepCharBuffer, 
                                    self.quoteCharBuffer, 
                                    self.encodingBuffer)
            showinfo("success!",
                    "Your CSV file is sucessfully saved!")
        except TypeError:
            showerror("ERROR!",
                            "Delimiter and quotechar must be a 1-character string.")

    def exportXML(self):
        """Exports dataframe to xml. The user can choose where the file will be saved."""
        encoding:str = self.encodingVariable.get()

        try:
            self.filePath:str = asksaveasfilename(
                                            defaultextension = ".xml",
                                            filetypes = [("XML file", "*.xml")],
                                            initialfile = "output.xml")
            self.exporter.exportAsXML(self.filePath, self.data, encoding)
            showinfo("success!",
                    "Your XML file is sucessfully saved!")
        except ValueError as valErr:
            showerror("ERROR!",
                            valErr)
        except TypeError:
            showerror("ERROR!",
                    "Invalid tagname \'nan\'")
      
    def about(self):
        """Shows what version it is an who has developed this program.
        
        Returns nothing"""
        showinfo("ABOUT", 
            "Version: 1.0\n Author: Annika Stadelmann")
        return

if __name__ == "__main__":
    app = gui()