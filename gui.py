import pandas as pd
import numpy as np
from importer import file_importer
from exporter import file_exporter
from guessDialectAndHeader import fileDialect 
from tkinter import Tk, Menu, Label, Button, Frame, Entry, StringVar, Checkbutton, BooleanVar, OptionMenu
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter.messagebox import showinfo
from pandastable import Table

#ab line 139 export funktionen
#mehrere dateien
#fehlerbehandlung  
  
class gui():
    def __init__(self):
        self.importer = file_importer()
        self.exporter = file_exporter(self.importer)
        self.guessDialectAndHeader = fileDialect()
        self.root = Tk()

        self.data = pd.DataFrame()
        self.encoding = str
        self.encodingList = ["ISO-8859-15", "CP1252", "UTF-8", "UTF-16BE", "UTF-16LE", "ASCII"]
        self.filePath = str
        self.sepCharBuffer = str
        self.quoteCharBuffer = str
        self.encodingBuffer = str

        self.root.title("file_importer_and_exporter")
        self.root.minsize(width = 1200, height = 400)
        self.root.configure(bg = "#FAEBD7")
        # self.root.option_add("*Font", "Arial 12")

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
        self.sepCharLabel = Label(self.settingsFrame, text = "seperation character:")
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

        self.csvButton = Button(self.exportFrame, command = self.exportCSV, text= "export as CSV", bg = "#F9E9CF")
        self.csvButton.grid(row = 6, column = 0, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.xmlButton = Button(self.exportFrame, command = self.exportXML, text= "export as XML", bg = "#F9E9CF")
        self.xmlButton.grid(row = 6, column = 1, padx = 10, pady = 10, sticky = 'w'+'e'+'n'+'s')

        self.root.mainloop()

    def addData(self):
        file = askopenfilename(title = "open csv or xml file!")
        if file.endswith(".csv"):
            self.importer.csvImport(file, dialect = self.guessDialectAndHeader)
        
        if file.endswith(".xml"):
            xslStyleSheet = askopenfilename(title = "open stylesheet!")
            if file.endswith(".xsl"):
                self.importer.xmlImport(file, xslStyleSheet)

        self.encoding = self.importer.whichEncoding(file)
        
        self.data = self.importer.getDataFrame()

        self.dataTable = Table(self.frame, dataframe = self.data)
        self.dataTable.show()

        self.updateEntrys()

    def updateEntrys(self):
        self.sepCharField.insert(0, self.guessDialectAndHeader.sepChar)
        self.qouteCharField.insert(0, self.guessDialectAndHeader.quoteChar)
        self.encodingVariable.set(self.guessDialectAndHeader.encoding.upper())
        if self.guessDialectAndHeader.hasHeader is False:
            self.hasHeaderButton.deselect()
        else:
            self.hasHeaderButton.select()

    def resetTable(self):
        self.data = self.importer.resetIt()
        self.qouteCharField.delete(0, 'end')
        self.sepCharField.delete(0, 'end')
        self.updateDialect()

        self.dataTable = Table(self.frame)
        self.dataTable.show()
        
    def updateDialect(self):
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
        if self.hasHeaderVariable.get() is True:
            newFirstLine = list(self.data.columns.values)
            self.data = self.data.append(pd.Series(newFirstLine, index = self.data.columns), ignore_index = True)
            self.data = self.data.iloc[np.arange(-1, len(self.data)-1)]
            self.data = self.data.reset_index(drop = True)

            self.importer.createHeaders(self.data)

        elif self.hasHeaderVariable.get() is False:
            newHeader = self.data.iloc[0]
            self.data = self.data[1:]
            self.data.columns = newHeader

        self.updateTable()
        return self

    def updateTable(self):
        self.dataTable = Table(self.frame, dataframe = self.data)
        self.dataTable.show()

    def exportCSV(self):
        self.updateDialect()
        self.filePath = asksaveasfile(mode = "w",
                                    defaultextension = ".csv",
                                    filetypes = [("CSV file", "*.csv")],
                                    initialfile = "output.csv")
    
        self.exporter.exportAsCSV(
                            self.filePath, 
                            self.sepCharBuffer, 
                            self.quoteCharBuffer, 
                            self.encodingBuffer)
        showinfo("success!",
                    "Your CSV file is sucessfully saved!")

    def exportXML(self):
        self.filePath:str = asksaveasfile(defaultextension = ".xml")
        encoding:str = self.encodingVariable.get()
        print(encoding)
        self.exporter.exportAsXML(self.filePath, encoding)
        showinfo("success!",
                    "Your XML file is sucessfully saved!")
      
    def about(self):
        showinfo("about", 
            "Version: 1.0\nAuthor: Annika Stadelmann\nE-mail: a.stadelmann@oth-aw.de\n\n\u00A9 Annika Stadelmann")
        return

if __name__ == "__main__":
    App = gui()