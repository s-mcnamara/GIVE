#
# This is the class that takes care of creating a new case
#
import sys
import subprocess
import os
import datetime
import wx

#---------------------------------------------------------------------------

class NewCase(wx.Dialog):

    def __init__(self,parent,DBconn,DBfile):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title='New Case')

        self.NCPanel = wx.Panel(self, wx.ID_ANY)
        self.MakeModal(True)
	self.DBconn = DBconn
	self.DBfile = DBfile
#
#       Labels
#
        InvLbl = wx.StaticText(self.NCPanel, -1, "Investigator:")
        CaseNameLbl = wx.StaticText(self.NCPanel, -1, "Case Name:")
        CaseNumLbl = wx.StaticText(self.NCPanel, -1, "Case Number:")
        ImgFileLbl = wx.StaticText(self.NCPanel, -1, "Image File:")
        ProLbl = wx.StaticText(self.NCPanel, -1, "Image Profile:")
#
#       Input Controls
#
        self.Investigator = wx.TextCtrl(self.NCPanel, -1, size=(125, -1))
        self.CaseName = wx.TextCtrl(self.NCPanel, -1, size=(125, -1))
	self.CaseNum = wx.TextCtrl(self.NCPanel, -1, size=(125, -1))
        self.ImageFile = wx.TextCtrl(self.NCPanel, -1, style=wx.TE_READONLY)  # fill in file name after browse
        self.ImageFile.SetBackgroundColour(wx.LIGHT_GREY)
        ProfileChoices = ['WinXPSP2x86']
        self.Profile = wx.ComboBox(self.NCPanel, -1, "", (0,0), 
                     (160, -1), ProfileChoices,wx.CB_DROPDOWN|wx.CB_READONLY)
#
#	Button to browse for image file
#
        BrowseButton = wx.Button(self.NCPanel, -1, "Browse")
        self.Bind(wx.EVT_BUTTON, self.GetImageFile, BrowseButton)
#
#	OK & Cancel buttons, add them to a sizer
#
	OKButton = wx.Button(self.NCPanel, -1, "OK")
        CancelButton = wx.Button(self.NCPanel, -1, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.SaveCase, OKButton)
        self.Bind(wx.EVT_BUTTON, self.CancelSave, CancelButton)
        self.Bind(wx.EVT_BUTTON, self.GetImageFile, BrowseButton)
        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonSizer.Add(OKButton,0, wx.ALL, 5)
        ButtonSizer.Add(CancelButton,0,wx.ALL,5)

	topSizer = wx.BoxSizer(wx.VERTICAL)

# add dummy widget to force placement: (wx.StaticText(self, -1, ''), 0, wx.EXPAND)

     	gridSizer = wx.GridSizer(rows=5, cols=3, hgap=2, vgap=2)
        gridSizer.Add(InvLbl, 0, wx.EXPAND)
        gridSizer.Add(self.Investigator, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.NCPanel, -1, ''), 0, wx.EXPAND)
#
	gridSizer.Add(CaseNameLbl, 0, wx.EXPAND)
	gridSizer.Add(self.CaseName, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.NCPanel, -1, ''), 0, wx.EXPAND)
#
	gridSizer.Add(CaseNumLbl, 0, wx.EXPAND)
	gridSizer.Add(self.CaseNum, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.NCPanel, -1, ''), 0, wx.EXPAND)
#
	gridSizer.Add(ImgFileLbl, 0, wx.EXPAND)
	gridSizer.Add(self.ImageFile, 0, wx.EXPAND)
	gridSizer.Add(BrowseButton, 0, wx.EXPAND)
#
	gridSizer.Add(ProLbl, 0, wx.EXPAND)
	gridSizer.Add(self.Profile, 0, wx.EXPAND)
	gridSizer.Add(wx.StaticText(self.NCPanel, -1, ''), 0, wx.EXPAND)

	topSizer.Add(gridSizer, 2, wx.ALL|wx.EXPAND, 2)
        topSizer.Add(ButtonSizer,1, wx.ALL|wx.EXPAND, 2)

        self.NCPanel.SetSizer(topSizer)
        topSizer.Fit(self)
 
        self.Show()

    def GetImageFile(self,event):
        print 'In GetImageFile'
        StartDir = os.getcwd()  # start in current directory
        dlg = wx.FileDialog(self, "Choose a memory image", StartDir, "","",wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            IFN = dlg.GetFilename()
            IDN = dlg.GetDirectory()
	    ImageFileName = os.path.join(IDN, IFN)
            print "The image file is ",ImageFileName
	dlg.Destroy()
        self.ImageFile.SetValue(ImageFileName)

    def SaveCase(self,event):
        if len(self.Investigator.GetValue()) == 0:
	    self.DisplayErrorDialog("Investigator field cannot be blank!")
        elif len(self.CaseName.GetValue()) == 0:
            self.DisplayErrorDialog("Case Name field cannot be blank!")
        elif len(self.CaseNum.GetValue()) == 0:
            self.DisplayErrorDialog("Case Number field cannot be blank!")
        elif len(self.ImageFile.GetValue()) == 0:
            self.DisplayErrorDialog("You must specify a memory image!")
        elif len(self.Profile.GetValue()) == 0:
            self.DisplayErrorDialog("You must specify a memory profile!")
        else:
#
#	    Check if the case num already exists in the db and print an error
#
	    cursor = self.DBconn.cursor()
	    cursor.execute("SELECT * from GIVECASES WHERE CASENUM=?",(int(self.CaseNum.GetValue()),))
	    row = cursor.fetchone()
	    if row is not None: 
		self.DisplayErrorDialog("Duplicate Case Number!")
		self.GetParent().CaseNum = 0
	    else:   # all is good save to DB and exit
                #print "Investigator: ",self.Investigator.GetValue()
                #print "Case Name: ",self.CaseName.GetValue()
                #print "Case Number: ",self.CaseNum.GetValue()
                #print "Image File: ",self.ImageFile.GetValue()
                #print "Memory Profile: ",self.Profile.GetValue()
                #print "Save to database and goodnight!"
#
#	        Add to GIVECASES table
#
                cursor.execute("INSERT INTO GIVECASES VALUES (?,?,?,?,?,?)",
	  	    (int(self.CaseNum.GetValue()),str(self.CaseName.GetValue()),
		     str(self.Investigator.GetValue()),str(self.ImageFile.GetValue()),
		     str(self.Profile.GetValue()),datetime.date.today()))
                self.DBconn.commit()
#
#		Call function to execute Volatility plug-ins
#
		self.CallVolatility(self.DBfile,self.CaseNum.GetValue(),
		    self.ImageFile.GetValue(),self.Profile.GetValue())
	        self.GetParent().CaseNum = self.CaseNum.GetValue()
                self.MakeModal(False)
	        self.NCPanel.Destroy()
                self.Close(True)
#
#   Call Volatility invokes the various GIVE plug-ins by spawning a sub-process to run
#   the Volatility commands
#
    def CallVolatility(self,dbf,cn,ifl,pro):
	volcmd = "python $VOLDIR/vol.py -f '%s' --profile=%s give_pslist --cn=%s --df='%s'" % (ifl,pro,cn,dbf)
	print "Volatility command: ",volcmd
        VolProc = subprocess.Popen(volcmd,stdin=None,stdout=subprocess.PIPE,shell=True,
	    universal_newlines=True,bufsize=-1)
	for line in iter(VolProc.stdout.readline, ""):
	    sys.stdout.write(line)  # print without \n
#
	volcmd = "python $VOLDIR/vol.py -f '%s' --profile=%s give_dlllist --cn=%s --df='%s'" % (ifl,pro,cn,dbf)
	print "Volatility command: ",volcmd
        VolProc = subprocess.Popen(volcmd,stdin=None,stdout=subprocess.PIPE,shell=True,
	    universal_newlines=True,bufsize=-1)
	for line in iter(VolProc.stdout.readline, ""):
	    sys.stdout.write(line)  # print without \n
#
	volcmd = "python $VOLDIR/vol.py -f '%s' --profile=%s give_handles --cn=%s --df='%s'" % (ifl,pro,cn,dbf)
	print "Volatility command: ",volcmd
        VolProc = subprocess.Popen(volcmd,stdin=None,stdout=subprocess.PIPE,shell=True,
	    universal_newlines=True,bufsize=-1)
	for line in iter(VolProc.stdout.readline, ""):
	    sys.stdout.write(line)  # print without \n
#
	volcmd = "python $VOLDIR/vol.py -f '%s' --profile=%s give_sockets --cn=%s --df='%s'" % (ifl,pro,cn,dbf)
	print "Volatility command: ",volcmd
        VolProc = subprocess.Popen(volcmd,stdin=None,stdout=subprocess.PIPE,shell=True,
	    universal_newlines=True,bufsize=-1)
	for line in iter(VolProc.stdout.readline, ""):
	    sys.stdout.write(line)  # print without \n
#
	volcmd = "python $VOLDIR/vol.py -f '%s' --profile=%s give_connscan --cn=%s --df='%s'" % (ifl,pro,cn,dbf)
	print "Volatility command: ",volcmd
        VolProc = subprocess.Popen(volcmd,stdin=None,stdout=subprocess.PIPE,shell=True,
	    universal_newlines=True,bufsize=-1)
	for line in iter(VolProc.stdout.readline, ""):
	    sys.stdout.write(line)  # print without \n
#
	volcmd = "python $VOLDIR/vol.py -f '%s' --profile=%s give_svcscan --cn=%s --df='%s'" % (ifl,pro,cn,dbf)
	print "Volatility command: ",volcmd
        VolProc = subprocess.Popen(volcmd,stdin=None,stdout=subprocess.PIPE,shell=True,
	    universal_newlines=True,bufsize=-1)
	for line in iter(VolProc.stdout.readline, ""):
	    sys.stdout.write(line)  # print without \n

    def DisplayErrorDialog(self,Msg):
        errdlg = wx.MessageDialog(self,Msg, "ERROR", wx.OK|wx.ICON_EXCLAMATION)
        errdlg.ShowModal() # Show it
        errdlg.Destroy()

    def CancelSave(self,event):
        print 'In CancelSave'
        self.MakeModal(False)
	self.NCPanel.Destroy()
        self.Close(True)
