#!/usr/bin/env python

import os
import sys
import wx
import sqlite3
import matplotlib.pyplot as plt
import networkx as nx
import proctree as GPT  # GIVE Process Tree
import plist as GPL	# GIVE Process List
import connscan as GCS  # GIVE ConnScan List
import newcase as GNC   # GIVE New Case Class
import opencase as GOC  # GIVE Open Case Class
import svcscan as GSS	# GIVE Service Scan

class GIVEFrame(wx.Frame):
#
#   Class variables
#
    DBconn = None # Connection to the SQLite database
#    DBname = "" # Name of the database file
    DBfilename = ""
    CaseNum = 0
    DG=nx.DiGraph() # directed graph for process hierarchy
#
#   Class constructor
#
    def __init__(self, parent, title):
        #wx.Frame.__init__(self, parent, title=title, style=wx.MAXIMIZE)
        #wx.Frame.__init__(self, parent, title=title, size=wx.DefaultSize)
        wx.Frame.__init__(self, parent, title=title, size=(600,400))

        myStatusBar = self.CreateStatusBar() # A Statusbar in the bottom of the window
        myStatusBar.SetStatusText("No database open",0)

        # Setting up the File menu.
        filemenu= wx.Menu()
        menuOpenDB = filemenu.Append(wx.ID_OPEN,"&Open Database"," Open database")
	menuNew = filemenu.Append(wx.ID_ADD,"&New Case"," Create new case")
	menuOpenCase = filemenu.Append(wx.ID_FIND,"&Open Case"," Open existing case")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

	# Setting up the View menu which determines what is in the right pane.  Default is process list
	viewmenu = wx.Menu()
        menuViewPSList = viewmenu.AppendRadioItem(0,"Process List","Show Process List")
        menuViewNetConnect = viewmenu.AppendRadioItem(1,"Net Connections","Show Network Connections")
        menuViewServices = viewmenu.AppendRadioItem(2,"Services","Show Service Scan")

        # Setting up the Visualize menu.
        visualmenu= wx.Menu()
        #menuVisualizeList = viewmenu.AppendCheckItem(0,"&List"," List Visualize")
        menuVisualizeTree = visualmenu.AppendRadioItem(3,"&Process Tree"," Process Hierarchy")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(viewmenu,"&View")  # Adding the View menu to the MenuBar
        menuBar.Append(visualmenu,"Visuali&ze") # Adding the Visualize menu to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Bind events to menu choices
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnOpenDB, menuOpenDB)
	self.Bind(wx.EVT_MENU, self.OnOpenCase, menuOpenCase)
	self.Bind(wx.EVT_MENU, self.OnNewCase, menuNew)
        self.Bind(wx.EVT_MENU, self.OnPSLIST, menuViewPSList)  
        self.Bind(wx.EVT_MENU, self.OnNetConnect, menuViewNetConnect)
	self.Bind(wx.EVT_MENU, self.OnServices, menuViewServices)
        self.Bind(wx.EVT_MENU, self.OnVisualize, menuVisualizeTree)
#
#	Create panels for each view window
#
        self.PListPanel = GPL.PList(self)
	self.ConnScanPanel = GCS.ConnScan(self)
	self.ServicesPanel = GSS.SvcScan(self)
#
#	Create a master sizer for the frame.  Add two sizers which can be shown/hidde
#	depending on what View the user chooses
#
	self.GiveSizer = wx.BoxSizer(wx.HORIZONTAL)
	self.PlistSizer = wx.BoxSizer(wx.HORIZONTAL)
	self.PlistSizer.Add(self.PListPanel,1,wx.EXPAND|wx.ALL)
	self.ConnSizer = wx.BoxSizer(wx.HORIZONTAL)
	self.ConnSizer.Add(self.ConnScanPanel,1,wx.EXPAND|wx.ALL)
	self.SvcSizer = wx.BoxSizer(wx.HORIZONTAL)
	self.SvcSizer.Add(self.ServicesPanel,1,wx.EXPAND|wx.ALL)
	self.GiveSizer.Add(self.PlistSizer,1,wx.EXPAND|wx.ALL)
	self.GiveSizer.Add(self.ConnSizer,1,wx.EXPAND|wx.ALL)
	self.GiveSizer.Add(self.SvcSizer,1,wx.EXPAND|wx.ALL)
	self.GiveSizer.Hide(self.ConnSizer,True)
	self.GiveSizer.Hide(self.SvcSizer,True)
	self.GiveSizer.Layout()
	self.SetSizer(self.GiveSizer)
	self.Layout()
#
#	Display the frame
#
        self.Show(True)

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Graphical Interface to the Volatility Environment", "About GIVE", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        if self.DBconn != None: 
	    self.DBconn.close()  
        else:
	    print "No database open"
        self.Close(True)  # Close the frame.
	self.DestroyChildren()
	self.Destroy()

    def OnNewCase(self,e):
	if self.DBconn == None:
	    dlg = wx.MessageDialog(self, "No Database Open", "Error", wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal() # Show it
            dlg.Destroy() # finally destroy it when finished.
	else:
  	    NewCaseDlg = GNC.NewCase(self,self.DBconn,self.DBfilename)
	    NewCaseDlg.ShowModal()
	    NewCaseDlg.Destroy()
     	    if self.CaseNum != 0:
	        self.PListPanel.OnOpenDB(self.DBconn,self.CaseNum)
		self.GiveSizer.Hide(self.ConnSizer,True)
		self.GiveSizer.Hide(self.SvcSizer,True)

    def OnOpenCase(self,e):
	if self.DBconn == None:
	    dlg = wx.MessageDialog(self, "No Database Open", "Error", wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal() # Show it
            dlg.Destroy() # finally destroy it when finished.
	else:
  	    OpenCaseDlg = GOC.OpenCase(self,self.DBconn)
	    OpenCaseDlg.ShowModal()
	    OpenCaseDlg.Destroy()
     	    if self.CaseNum != 0:
	        self.PListPanel.OnOpenDB(self.DBconn,self.CaseNum)
		self.GiveSizer.Hide(self.ConnSizer,True)
		self.GiveSizer.Hide(self.SvcSizer,True)

    def OnOpenDB(self,e):
        """ Open a file"""
        dirname = os.getenv('GIVEDB')
        dlg = wx.FileDialog(self, "Choose a database", dirname, "", "*.db", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.DBfilename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            DBname = os.path.join(dirname, self.DBfilename)
            self.DBconn = sqlite3.connect(DBname) 
            statusBar = self.GetStatusBar()
            statusBar.SetStatusText(DBname,0)
	    #self.PListPanel.OnOpenDB(self.DBconn)
        else:
	    print "CANCEL THE WHOLE THING!"
	    e = wx.CloseEvent()
	    self.OnExit(e)

    def OnSize(self, event):
        #print "In OnSize"
        w,h = self.GetClientSizeTuple()
        self.GIVEProcTree.SetDimensions(0, 0, w, h)

#
#   If the user chooses to visualize the process hieararchy, build the graph here and display it
#
    def OnVisualize(self,event):
	if self.CaseNum == 0:
	    dlg = wx.MessageDialog(self, "No Case Open", "Error", wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal() # Show it
            dlg.Destroy() # finally destroy it when finished.

	else:
            ParentList = []  # create an empty list that will hold all the top-leve PIDs
	    cmd = "SELECT PID, PPID FROM PSLIST_%s" % self.CaseNum
            cursor = self.DBconn.execute(cmd)
            for row in cursor:
                PID = row[0]
                PPID = row[1]
                if PPID != 0:
                    ExistingParent = False
                    idx = 0
                    while (idx < len(ParentList) and not(ExistingParent)): # search existing trees for this parent ID
                        ExistingParent = ParentList[idx].SearchTree(PPID)
                        idx+=1

                    if not(ExistingParent):  # start a new tree & add the child
                        ParentList.append(GPT.PTree(PPID))
                        ParentList[len(ParentList)-1].AddChild(PID,PPID)

                    else:  # the process was found in the tree at idx-1, add the child
                        idx-=1
                        ParentList[idx].AddChild(PID,PPID)

                else:   # any process with a parent of 0 is a new tree
                    ParentList.append(GPT.PTree(PID))

            for idx in range(len(ParentList)):
                PD = {ParentList[idx].PID:(50,60)}  # position dictionary
                ParentList[idx].DrawTree(self.DG,PD)
                nx.draw(self.DG,PD,node_color=(.1,.8,.1,.1),node_size=1500)
                figure=plt.figure(1)
                figure.suptitle("Process Hierarchy")
                plt.show()
                self.DG.clear()  # reset for next

    def OnPSLIST(self,e):
	print "Show Process list in left pane!"
	self.GiveSizer.Hide(self.ConnSizer,True)
	self.GiveSizer.Hide(self.SvcSizer,True)
	self.GiveSizer.Show(self.PlistSizer,True)
	self.GiveSizer.Layout()
	self.Layout()

    def OnNetConnect(self,e):
	print "Show network connections"
	self.ConnScanPanel.ShowConnections(self.DBconn)
	self.GiveSizer.Show(self.ConnSizer,True)
	self.GiveSizer.Hide(self.PlistSizer,True)
	self.GiveSizer.Hide(self.SvcSizer,True)
	self.GiveSizer.Layout()
	self.Layout()

    def OnServices(self,e):
	print "Show Service Scan results"
	self.ServicesPanel.ShowServices(self.DBconn)
	self.GiveSizer.Show(self.SvcSizer,True)
	self.GiveSizer.Hide(self.PlistSizer,True)
	self.GiveSizer.Hide(self.ConnSizer,True)
	self.GiveSizer.Layout()
	self.Layout()

app = wx.App(False)
frame = GIVEFrame(None, 'GIVE')
app.MainLoop()
