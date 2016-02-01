#
# This is the class that takes care of opening an existing case
#
import sys
import os
import datetime
import wx

#---------------------------------------------------------------------------

class OpenCase(wx.Dialog):

    def __init__(self,parent,DBconn):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title='Open Case')

        self.OCPanel = wx.Panel(self, wx.ID_ANY)
        self.MakeModal(True)
	self.DBconn = DBconn
#
#	Read list of existing cases from the GIVECASES table and populate lists for each field
#
	Investigators = []
	CaseNames = []
	CaseNums = []
	ImageFiles = []
	ImageProfiles = []
	CreateDates = []
	cursor = self.DBconn.cursor()
        cursor.execute("SELECT * FROM GIVECASES")
	for row in cursor:
	    #print row[0]," ",row[1]," ",row[2]," ",row[3]," ",row[4]," ",row[5]
	    CaseNums.append(str(row[0]))
	    CaseNames.append(str(row[1]))
	    Investigators.append(str(row[2]))
	    ImageFiles.append(str(row[3]))
	    ImageProfiles.append(str(row[4]))
	    CreateDates.append(str(row[5]))
#
#       Labels
#
        InvLbl = wx.StaticText(self.OCPanel, -1, "Investigator:")
        CaseNameLbl = wx.StaticText(self.OCPanel, -1, "Case Name:")
        CaseNumLbl = wx.StaticText(self.OCPanel, -1, "Case Number:")
        ImgFileLbl = wx.StaticText(self.OCPanel, -1, "Image File:")
        ProLbl = wx.StaticText(self.OCPanel, -1, "Image Profile:")
	DateLbl = wx.StaticText(self.OCPanel, -1, "Case Creation Date:")
#
#	Create unique constants for identifying the combo boxes.  These values
#	are lower than the wx.ID_LOWEST which is 4999
#
	self.GID_Investigator=735
	self.GID_CaseName=736
	self.GID_CaseNum=737
	self.GID_ImgFile=738
	self.GID_ImgProfile=739
	self.GID_CreateDate=740
#
#       Input Controls
#
        self.Investigator = wx.ComboBox(self.OCPanel, self.GID_Investigator, "", (0,0),
		(160, -1), Investigators,wx.CB_DROPDOWN|wx.CB_READONLY)
        self.CaseName = wx.ComboBox(self.OCPanel, self.GID_CaseName, "", (0,0),
		(160, -1), CaseNames,wx.CB_DROPDOWN|wx.CB_READONLY)
	self.CaseNum = wx.ComboBox(self.OCPanel, self.GID_CaseNum, "", (0,0),
		(160, -1), CaseNums,wx.CB_DROPDOWN|wx.CB_READONLY)
        self.ImageFile = wx.ComboBox(self.OCPanel, self.GID_ImgFile, "", (0,0),
		(160, -1), ImageFiles,wx.CB_DROPDOWN|wx.CB_READONLY)
        self.Profile = wx.ComboBox(self.OCPanel, self.GID_ImgProfile, "", (0,0), 
                (160, -1), ImageProfiles,wx.CB_DROPDOWN|wx.CB_READONLY)
        self.CreateDate = wx.ComboBox(self.OCPanel, self.GID_CreateDate, "", (0,0), 
                (160, -1), CreateDates,wx.CB_DROPDOWN|wx.CB_READONLY)
#
#	Bind events to a single event handler
#
	self.Bind(wx.EVT_COMBOBOX, self.GetComboChoice, self.Investigator)
	self.Bind(wx.EVT_COMBOBOX, self.GetComboChoice, self.CaseName)
	self.Bind(wx.EVT_COMBOBOX, self.GetComboChoice, self.CaseNum)
	self.Bind(wx.EVT_COMBOBOX, self.GetComboChoice, self.ImageFile)
	self.Bind(wx.EVT_COMBOBOX, self.GetComboChoice, self.Profile)
	self.Bind(wx.EVT_COMBOBOX, self.GetComboChoice, self.CreateDate)
#
#	Open & Cancel buttons, add them to a sizer
#
	OpenButton = wx.Button(self.OCPanel, -1, "Open")
        CancelButton = wx.Button(self.OCPanel, -1, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OpenACase, OpenButton)
        self.Bind(wx.EVT_BUTTON, self.CancelOpen, CancelButton)
        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonSizer.Add(OpenButton,0, wx.ALL, 5)
        ButtonSizer.Add(CancelButton,0,wx.ALL,5)

	topSizer = wx.BoxSizer(wx.VERTICAL)

# add dummy widget to force placement: (wx.StaticText(self, -1, ''), 0, wx.EXPAND)

     	gridSizer = wx.GridSizer(rows=6, cols=3, hgap=2, vgap=2)
        gridSizer.Add(InvLbl, 0, wx.EXPAND)
        gridSizer.Add(self.Investigator, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.OCPanel, -1, ''), 0, wx.EXPAND)
#
	gridSizer.Add(CaseNameLbl, 0, wx.EXPAND)
	gridSizer.Add(self.CaseName, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.OCPanel, -1, ''), 0, wx.EXPAND)
#
	gridSizer.Add(CaseNumLbl, 0, wx.EXPAND)
	gridSizer.Add(self.CaseNum, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.OCPanel, -1, ''), 0, wx.EXPAND)
#
	gridSizer.Add(ImgFileLbl, 0, wx.EXPAND)
	gridSizer.Add(self.ImageFile, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.OCPanel, -1, ''), 0, wx.EXPAND)
#
	gridSizer.Add(ProLbl, 0, wx.EXPAND)
	gridSizer.Add(self.Profile, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.OCPanel, -1, ''), 0, wx.EXPAND)
#
	gridSizer.Add(DateLbl, 0, wx.EXPAND)
	gridSizer.Add(self.CreateDate, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.OCPanel, -1, ''), 0, wx.EXPAND)

	topSizer.Add(gridSizer, 2, wx.ALL|wx.EXPAND, 2)
        topSizer.Add(ButtonSizer,1, wx.ALL|wx.EXPAND, 2)

        self.OCPanel.SetSizer(topSizer)
        topSizer.Fit(self)
 
        self.Show()

    def GetComboChoice(self,event):
	UserChoice = event.GetId()
	if UserChoice == self.GID_Investigator:
	    cmd = "SELECT * FROM GIVECASES WHERE INVESTIGATOR='%s'" % event.GetString()
	elif UserChoice == self.GID_CaseName:
	    cmd = "SELECT * FROM GIVECASES WHERE CASENAME='%s'" % event.GetString()
	elif UserChoice == self.GID_CaseNum:
	    cmd = "SELECT * FROM GIVECASES WHERE CASENUM=%s" % event.GetString()
	elif UserChoice == self.GID_ImgFile:
	    cmd = "SELECT * FROM GIVECASES WHERE IMAGEFILE='%s'" % event.GetString()
	elif UserChoice == self.GID_ImgProfile:
	    cmd = "SELECT * FROM GIVECASES WHERE PROFILE='%s'" % event.GetString()
	elif UserChoice == self.GID_CreateDate:
	    cmd = "SELECT * FROM GIVECASES WHERE CREATEDATE='%s'" % event.GetString()
        print "SELECT command: ",cmd
	cursor = self.DBconn.execute(cmd)
	row = cursor.fetchone()
#
#	Fill in all the combo boxes with what has just been returned
#
	self.Investigator.ChangeValue(str(row[2]))
        self.CaseName.ChangeValue(str(row[1]))
	self.CaseNum.ChangeValue(str(row[0]))
        self.ImageFile.ChangeValue(str(row[3]))
        self.Profile.ChangeValue(str(row[4]))
        self.CreateDate.ChangeValue(str(row[5]))

    def OpenACase(self,event):
	print "In OpenACase"
#
#	check one combo box to make sure it's not empty, if it is display an error dialog
#	if it's not, the user has selected a case, need to figure out what to do next!
#
	if len(self.Investigator.GetValue()) == 0:
	    self.DisplayErrorDialog("Select an existing case or click CANCEL to exit!")
	else:
	    self.GetParent().CaseNum = self.CaseNum.GetValue()
            self.MakeModal(False)
	    self.OCPanel.Destroy()
	    self.Close(True)

    def DisplayErrorDialog(self,Msg):
        errdlg = wx.MessageDialog(self,Msg, "ERROR", wx.OK|wx.ICON_EXCLAMATION)
        errdlg.ShowModal() # Show it
        errdlg.Destroy()

    def CancelOpen(self,event):
        print 'In CancelOpen'
        self.MakeModal(False)
	self.OCPanel.Destroy()
        self.Close(True)
